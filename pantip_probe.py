"""
MADT 7202 Mid-Term — Pantip PROBE (not the collector yet)
Checks whether search results / topic content are in plain HTML or loaded by JavaScript,
so the real collector can be written against the actual page structure.
Run:  python pantip_probe.py            (optionally: python pantip_probe.py https://pantip.com/topic/XXXXXXXX)
"""
import re, sys, time
from urllib.parse import quote
import requests

CONTACT = "your.name@university.example"   # <-- put your real NIDA email
H = {"User-Agent": f"MADT7202-NIDA-academic-research/0.1 (contact: {CONTACT})"}

def probe(url, keyword=None):
    print(f"\n--- {url}")
    try:
        r = requests.get(url, headers=H, timeout=30)
    except Exception as e:
        print("ERROR:", e); return None
    html = r.text
    topics = sorted(set(re.findall(r"/topic/(\d{6,})", html)))
    print("status:", r.status_code, "| bytes:", len(html))
    print("has __NEXT_DATA__ (JS-rendered JSON):", "__NEXT_DATA__" in html)
    if keyword:
        print(f"keyword '{keyword}' in HTML:", keyword in html)
    print("unique /topic/ ids in HTML:", len(topics), topics[:5])
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    print("title tag:", (m.group(1).strip()[:100] if m else None))
    for marker in ["display-post-title", "display-post-story", "og:description",
                   "datePublished", "ld+json"]:
        print(f"marker '{marker}':", marker in html)
    return topics

kw = "ลังเลระหว่าง"
found = probe(f"https://pantip.com/search?q={quote(kw)}", keyword=kw)
time.sleep(3)
probe("https://pantip.com/forum/rachada")
time.sleep(3)

topic_url = sys.argv[1] if len(sys.argv) > 1 else (
    f"https://pantip.com/topic/{found[0]}" if found else None)
if topic_url:
    probe(topic_url)
else:
    print("\nNo topic id found automatically. Open any Pantip car thread in your browser,")
    print("copy its URL, and rerun:  python pantip_probe.py <that URL>")
