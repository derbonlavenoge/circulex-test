"""Mix the Brick voice-over with looped rain + wiper ambiance.

Usage: python3 -I mix.py VOICE RAIN WIPERS OUT_DIR
"""
import json
import re
import subprocess
import sys
from pathlib import Path

voice, rain, wipers, out_dir = sys.argv[1:5]
out = Path(out_dir)
out.mkdir(parents=True, exist_ok=True)

PRE = 2.0          # ambiance seule avant la voix (s)
TAIL = 4.0         # ambiance après la dernière phrase (s)
FADE_IN = 1.5
FADE_OUT = 3.5
RAIN_UNDER = 12.0  # dB sous la voix, hors ducking
WIPERS_UNDER = 16.0
TARGET = -16.0     # LUFS final
LIMIT_DB = -2.0    # plafond crête final (dBFS)


def run(args):
    return subprocess.run(args, check=True, capture_output=True, text=True)


def lufs(path):
    err = run(["ffmpeg", "-nostats", "-hide_banner", "-i", str(path),
               "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    summary = err[err.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summary).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summary).group(1))
    return i, tp


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "default=nw=1:nk=1", str(path)]).stdout)


# 1) Voix : passe-haut, compression douce, limiteur, stéréo
voice_proc = out / "voix-traitee.wav"
run(["ffmpeg", "-y", "-v", "error", "-i", voice, "-af",
     "highpass=f=70,"
     "acompressor=threshold=-30dB:ratio=3:attack=10:release=250:makeup=2,"
     "alimiter=limit=-2dB:level=false,"
     "pan=stereo|c0=c0|c1=c0",
     "-ar", "44100", str(voice_proc)])
v_lufs, _ = lufs(voice_proc)
v_dur = duration(voice_proc)
total = PRE + v_dur + TAIL

# 2) Gains des boucles, calés sur la voix traitée
r_lufs, _ = lufs(rain)
w_lufs, _ = lufs(wipers)
g_rain = (v_lufs - RAIN_UNDER) - r_lufs
g_wip = (v_lufs - WIPERS_UNDER) - w_lufs

# 3) Mix : boucles répétées, ducking sous la voix, fondus
graph = (
    f"[1:a]volume={g_rain:.2f}dB[r];"
    f"[2:a]volume={g_wip:.2f}dB[w];"
    f"[r][w]amix=inputs=2:normalize=0:duration=longest,"
    f"atrim=0:{total:.3f},asetpts=N/SR/TB[bed];"
    f"[0:a]adelay={int(PRE * 1000)}:all=1,apad,atrim=0:{total:.3f},asetpts=N/SR/TB,"
    f"asplit=2[v][sc];"
    f"[bed][sc]sidechaincompress=threshold=-30dB:ratio=4:attack=20:release=600[duck];"
    f"[duck]afade=t=in:d={FADE_IN},afade=t=out:st={total - FADE_OUT:.3f}:d={FADE_OUT}[bedf];"
    f"[v][bedf]amix=inputs=2:normalize=0:duration=first[mix]"
)
premix = out / "premix.wav"
run(["ffmpeg", "-y", "-v", "error",
     "-i", str(voice_proc),
     "-stream_loop", "-1", "-i", rain,
     "-stream_loop", "-1", "-i", wipers,
     "-filter_complex", graph, "-map", "[mix]", "-t", f"{total:.3f}",
     "-ar", "44100", str(premix)])

# 4) Niveau final : gain linéaire vers la cible, puis limiteur de sécurité
m_lufs, _ = lufs(premix)
gain = TARGET - m_lufs
final = out / "trente-secondes-mix.mp3"
run(["ffmpeg", "-y", "-v", "error", "-i", str(premix), "-af",
     f"volume={gain:.2f}dB,alimiter=limit={LIMIT_DB}dB:level=false",
     "-c:a", "libmp3lame", "-b:a", "320k", str(final)])

f_lufs, f_peak = lufs(final)
print(json.dumps({
    "voix_traitee_lufs": v_lufs, "pluie_lufs_source": r_lufs, "essuie_glaces_lufs_source": w_lufs,
    "gain_pluie_db": round(g_rain, 2), "gain_essuie_glaces_db": round(g_wip, 2),
    "duree_totale_s": round(total, 2), "premix_lufs": m_lufs, "gain_final_db": round(gain, 2),
    "final_lufs": f_lufs, "final_crete_dbfs": f_peak, "fichier": str(final),
}, indent=2, ensure_ascii=False))
