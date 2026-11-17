"""Assemble the 'Trente secondes' video: Ken Burns clips, transitions, grade, subtitles, audio.

Usage: make_video.py PLANS_JSON IMAGES_DIR AUDIO ASS WORK_DIR OUT_MP4
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

plans_path, img_dir, audio, ass, work, out = sys.argv[1:7]
work = Path(work)
work.mkdir(parents=True, exist_ok=True)
spec = json.load(open(plans_path, encoding="utf-8"))
plans, T = spec["plans"], spec["fin"]
FPS = 30

starts = [p["debut"] for p in plans] + [T]
trans = [p.get("entree", ["fade", 0.0]) for p in plans]  # transition INTO plan i
xd = [t[1] for t in trans] + [0.0]


def zoompan(p, n):
    (z0, z1), (cx0, cy0), (cx1, cy1) = p["z"], p["c0"], p["c1"]
    e = f"(pow(on/{n - 1},2)*(3-2*on/{n - 1}))"
    z = f"{z0}+({z1 - z0})*{e}"
    x = f"clip(({cx0}+({cx1 - cx0})*{e})*iw-iw/zoom/2,0,iw-iw/zoom)"
    y = f"clip(({cy0}+({cy1 - cy0})*{e})*ih-ih/zoom/2,0,ih-ih/zoom)"
    return f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s=1920x1080:fps={FPS}"


def render(i):
    p = plans[i]
    length = (starts[i + 1] - starts[i]) + xd[i] / 2 + xd[i + 1] / 2
    n = round(length * FPS)
    clip = work / f"plan{i:02d}.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(Path(img_dir) / f"{p['img']}.png"),
        "-vf", f"scale=3840:2160:flags=lanczos,{zoompan(p, n)},format=yuv420p",
        "-frames:v", str(n), "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", str(clip)],
        check=True)
    return clip, n / FPS


with ThreadPoolExecutor(max_workers=2) as pool:
    clips = list(pool.map(render, range(len(plans))))

# Chaîne de transitions
inputs, chain = [], []
for clip, _ in clips:
    inputs += ["-i", str(clip)]
for i in range(len(clips)):
    chain.append(f"[{i}:v]settb=AVTB,fps={FPS},format=yuv420p[v{i}]")
prev = "v0"
for i in range(1, len(clips)):
    kind, d = trans[i]
    offset = starts[i] - d / 2
    chain.append(f"[{prev}][v{i}]xfade=transition={kind}:duration={d}:offset={offset:.3f}[x{i}]")
    prev = f"x{i}"
chain.append(
    f"[{prev}]eq=saturation=0.94:contrast=1.04,vignette=angle=PI/5,noise=alls=3:allf=t,"
    f"ass={ass},fade=t=in:st=0:d=1,fade=t=out:st={T - 2.5:.3f}:d=2.5,format=yuv420p[vout]")

audio_idx = len(clips)
subprocess.run(
    ["ffmpeg", "-y", "-v", "error", *inputs, "-i", audio,
     "-filter_complex", ";".join(chain),
     "-map", "[vout]", "-map", f"{audio_idx}:a",
     "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-tune", "film", "-profile:v", "high",
     "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-t", f"{T:.3f}", "-movflags", "+faststart", out],
    check=True)
print("ok", out)
