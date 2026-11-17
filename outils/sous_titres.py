"""Build styled ASS + SRT subtitles from ElevenLabs Scribe word timings.

Usage: make_subs.py WORDS_JSON OFFSET_S OUT_ASS OUT_SRT
"""
import json
import sys

words_path, offset, out_ass, out_srt = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4]
data = json.load(open(words_path, encoding="utf-8"))
words = data["words"] if isinstance(data, dict) else data

# Drop audio-direction tags such as [softly], [long pause], [frustrated sigh]
tokens, in_tag = [], False
for w in words:
    t = w["text"].strip()
    if not t:
        continue
    if t.startswith("[") or in_tag:
        in_tag = not t.endswith("]")
        continue
    tokens.append({"text": t, "start": w["start"] + offset, "end": w["end"] + offset})

HARD_END = (".", "!", "?")
SOFT_END = ("…", ",", ":")
MAX_CHARS = 66


def text_of(ws):
    return " ".join(w["text"] for w in ws)


# 1) Sentences: break after . ! ? (a closing » stays with its sentence)
sentences, cur = [], []
for i, tok in enumerate(tokens):
    cur.append(tok)
    nxt = tokens[i + 1]["text"] if i + 1 < len(tokens) else None
    if nxt == "»":
        continue
    if nxt is None or tok["text"].endswith(HARD_END) or tok["text"] == "»":
        sentences.append(cur)
        cur = []


# 2) Long sentences: split at … , : (balanced), else at the middle word
def split_long(ws):
    if len(text_of(ws)) <= MAX_CHARS or len(ws) < 2:
        return [ws]
    soft = [k for k in range(1, len(ws)) if ws[k - 1]["text"].endswith(SOFT_END) and ws[k]["text"] != "»"]
    fits = [k for k in soft if len(text_of(ws[:k])) <= MAX_CHARS and len(text_of(ws[k:])) <= MAX_CHARS]
    if fits:
        k = min(fits, key=lambda k: max(len(text_of(ws[:k])), len(text_of(ws[k:]))))
    elif soft:
        k = min(soft, key=lambda k: abs(len(text_of(ws[:k])) - len(text_of(ws)) / 2))
    else:
        cands = [k for k in range(1, len(ws)) if ws[k - 1]["text"] != "«" and ws[k]["text"] != "»"]
        k = min(cands, key=lambda k: abs(len(text_of(ws[:k])) - len(text_of(ws)) / 2))
    return split_long(ws[:k]) + split_long(ws[k:])


cues = [part for s in sentences for part in split_long(s)]

# 3) Merge a very short cue into the next one when spoken in the same breath
merged = []
for c in cues:
    if merged:
        prev = merged[-1]
        gap = c[0]["start"] - prev[-1]["end"]
        dur_prev = prev[-1]["end"] - prev[0]["start"]
        if dur_prev < 0.8 and gap < 0.3 and len(text_of(prev + c)) <= MAX_CHARS:
            merged[-1] = prev + c
            continue
    merged.append(c)


def wrap(s, width=40):
    if len(s) <= width:
        return [s]
    mid = len(s) // 2
    spaces = [k for k, ch in enumerate(s) if ch == " "]
    # avoid breaking right after an opening guillemet or before a closing one / colon
    spaces = [k for k in spaces if s[k - 1] != "«" and s[k + 1] not in "»:"]
    k = min(spaces, key=lambda p: abs(p - mid))
    return [s[:k], s[k + 1:]]


events = []
for n, c in enumerate(merged):
    start = c[0]["start"]
    end = max(c[-1]["end"] + 0.35, start + 0.9)
    if n + 1 < len(merged):
        end = min(end, merged[n + 1][0]["start"] - 0.04)
    events.append((start, end, wrap(text_of(c))))


def ass_time(t):
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Monologue,Inter SemiBold,54,&H00FFFFFF,&H00FFFFFF,&H64000000,&H96000000,0,0,0,0,100,100,0.5,0,1,2.6,1.2,2,160,160,84,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
with open(out_ass, "w", encoding="utf-8") as f:
    f.write(header)
    for start, end, lines in events:
        f.write(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Monologue,,0,0,0,,{{\\fad(120,120)}}{'\\N'.join(lines)}\n")

with open(out_srt, "w", encoding="utf-8") as f:
    for n, (start, end, lines) in enumerate(events, 1):
        f.write(f"{n}\n{srt_time(start)} --> {srt_time(end)}\n" + "\n".join(lines) + "\n\n")

print(f"{len(events)} sous-titres")
for start, end, lines in events:
    print(f"{start:7.2f} → {end:7.2f}  {' / '.join(lines)}")
