"""
MADT 7202 Mid-Term - Step 3b: map comments -> car models, count comments that mention >=2 models.
Reads  data/raw/yt_videos.csv, data/raw/yt_comments.jsonl
Writes data/processed/comment_models.csv  (ids + model names ONLY, no comment text)
Run:   python3 count_models.py
Alias table is a first draft. Brand-only words (mg, byd, toyota...) and generic words are NOT nodes.
Thai nicknames are only partly covered -> counts are a LOWER bound.
"""
import csv, json, re, os, itertools
from collections import Counter, defaultdict

RAW = "data/raw"
vtitle = {r["video_id"]: r["title"].lower()
          for r in csv.DictReader(open(f"{RAW}/yt_videos.csv", encoding="utf-8"))}
comments = [json.loads(l) for l in open(f"{RAW}/yt_comments.jsonl", encoding="utf-8")]

# (regex, model). ASCII patterns get word-boundary guards automatically.
IN_SCOPE = [
 (r"ex\s?2", "EX2"), (r"ex\s?5", "EX5"), (r"ut", "UT"),
 (r"yaris(?!\s?(ativ|cross))", "Yaris"), (r"yaris\s?ativ|ativ", "Yaris Ativ"), (r"yaris\s?cross", "Yaris Cross"),
 (r"city", "City"), (r"ซิตี้", "City"), (r"civic", "Civic"), (r"ซีวิค", "Civic"),
 (r"x-?\s?force", "XForce"), (r"kicks", "Kicks"),
 (r"dolphin", "Dolphin"), (r"mg\s?4", "MG4"), (r"atto\s?1", "Atto 1"), (r"atto\s?2", "Atto 2"), (r"atto\s?3", "Atto 3"),
 (r"ora\s?0?5", "ORA 5"), (r"q05|nevo", "Nevo Q05"), (r"jaecoo\s?5?", "Jaecoo 5"),
 (r"mg\s?s5", "MG S5"), (r"v27", "iCAUR V27"), (r"mg\s?urban|urban", "MG Urban"),
 (r"swift", "Swift"), (r"fronx", "Fronx"), (r"hr-?v", "HR-V"), (r"cr-?v", "CR-V"),
 (r"camry", "Camry"), (r"แคมรี่", "Camry"), (r"altis", "Altis"), (r"อัลติส", "Altis"),
 (r"model\s?3", "Model 3"),
]
OUT_OF_SCOPE = r"hilux|revo|travo|fortuner|ranger|pajero|d-?max|triton|navara"
PENDING = [(r"tank\s?300", "Tank 300"), (r"fj", "Land Cruiser FJ"), (r"land\s?cruiser", "Land Cruiser FJ"),
           (r"serena", "Serena"), (r"m6", "BYD M6")]

def comp(pat):
    guard = pat[0].isascii()
    return re.compile((r"(?<![a-z0-9])" + pat + r"(?![a-z0-9])") if guard else pat)
IN_RX   = [(comp(p), m) for p, m in IN_SCOPE]
OUT_RX  = comp(OUT_OF_SCOPE)
PEND_RX = [(comp(p), m) for p, m in PENDING]
XF_RX   = comp(r"xf")

# drop exact-duplicate comment texts (spam / copy-paste)
seen, dup = set(), 0
rows = []
for c in comments:
    key = re.sub(r"\s+", " ", c["text"]).strip().lower()
    if key in seen:
        dup += 1; continue
    seen.add(key); rows.append(c)

res, n_out, n_pend, n_mixed_out = [], 0, 0, 0
for c in rows:
    t = c["text"].lower()
    models = {m for rx, m in IN_RX if rx.search(t)}
    if XF_RX.search(t) and "xforce" in vtitle.get(c["video_id"], ""):
        models.add("XForce")
    has_out  = bool(OUT_RX.search(t))
    has_pend = any(rx.search(t) for rx, _ in PEND_RX)
    n_out += has_out; n_pend += has_pend
    if has_out and models: n_mixed_out += 1
    res.append((c["video_id"], c["comment_id"], sorted(models)))

os.makedirs("data/processed", exist_ok=True)
with open("data/processed/comment_models.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["video_id", "comment_id", "models"])
    for v, cid, ms in res:
        if ms: w.writerow([v, cid, "|".join(ms)])

ge1 = [r for r in res if len(r[2]) >= 1]
ge2 = [r for r in res if len(r[2]) >= 2]
pair_c, pair_v = Counter(), defaultdict(set)
for v, cid, ms in ge2:
    for a, b in itertools.combinations(ms, 2):
        pair_c[(a, b)] += 1; pair_v[(a, b)].add(v)
model_c = Counter(m for _, _, ms in res for m in ms)

print("=== MODEL COUNT SUMMARY (paste this back) ===")
print("comments read:", len(comments), "| exact duplicates removed:", dup, "| kept:", len(rows))
print("comments with >=1 in-scope model:", len(ge1))
print("comments with >=2 distinct models (can make an edge):", len(ge2))
print("distinct models found:", len(model_c))
print("distinct model pairs:", len(pair_c))
for k in (1, 2, 3, 5):
    print(f"pairs seen under >={k} different videos:", sum(1 for p in pair_c if len(pair_v[p]) >= k))
print("comments mentioning pickup/PPV words:", n_out, "| of which also mention an in-scope model:", n_mixed_out)
print("comments mentioning pending-scope models (Tank300/FJ/Serena/M6):", n_pend)
print("\nmodels by number of comments:")
for m, n in model_c.most_common(40):
    print(f"  {m}: {n}")
print("\ntop 15 pairs (comments / videos):")
for (a, b), n in pair_c.most_common(15):
    print(f"  {a} + {b}: {n} / {len(pair_v[(a, b)])}")
