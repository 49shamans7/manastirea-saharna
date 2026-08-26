import re, os, json, urllib.request, urllib.parse, html, time
from collections import defaultdict

BASE = "https://manastirea-saharna.md"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"}

def get(url, timeout=40):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read(), r.headers.get("Content-Type","")
    except Exception as e:
        return None, str(e)

seen_pages, queue = set(), [BASE + "/"]
pages = {}
while queue and len(seen_pages) < 60:
    u = queue.pop(0)
    if u in seen_pages: continue
    seen_pages.add(u)
    body, ct = get(u)
    if not body or "html" not in (ct or ""): continue
    s = body.decode("utf-8", "ignore")
    pages[u] = s
    for m in re.findall(r'href="(https://manastirea-saharna\.md/[^"#?]*)"', s):
        if m.endswith((".jpg",".png",".pdf",".zip",".webp",".gif")): continue
        if "/wp-" in m or "/feed" in m or "/comment" in m: continue
        if m not in seen_pages and len(queue) < 80: queue.append(m)
    time.sleep(0.2)

print(f"pages crawled: {len(pages)}")
json.dump(sorted(pages.keys()), open("_pages.json","w"), indent=1)

# ---- harvest asset urls ----
assets = defaultdict(set)
ATTRS = r'(?:src|data-src|data-lazy-src|data-large_image|data-thumb|content|href|data-bg|data-background)'
for u, s in pages.items():
    for m in re.findall(ATTRS + r'="([^"]+\.(?:jpg|jpeg|png|webp|gif|svg))"', s, re.I):
        assets["direct"].add(urllib.parse.urljoin(u, html.unescape(m)))
    for m in re.findall(r'srcset="([^"]+)"', s, re.I):
        for part in m.split(","):
            p = part.strip().split(" ")[0]
            if re.search(r'\.(jpg|jpeg|png|webp|svg)$', p, re.I):
                assets["direct"].add(urllib.parse.urljoin(u, html.unescape(p)))
    for m in re.findall(r'url\((["\']?)([^)"\']+\.(?:jpg|jpeg|png|webp|svg|gif))\1\)', s, re.I):
        assets["css_bg"].add(urllib.parse.urljoin(u, html.unescape(m[1])))
    for m in re.findall(r'<svg[\s\S]{0,6000}?</svg>', s, re.I):
        assets["inline_svg"].add(m)
    for m in re.findall(r'href="([^"]+\.css)"', s, re.I):
        assets["css_files"].add(urllib.parse.urljoin(u, m))

# stylesheets often hold the patterns/textures
for c in list(assets["css_files"])[:40]:
    body, ct = get(c)
    if not body: continue
    t = body.decode("utf-8","ignore")
    for m in re.findall(r'url\((["\']?)([^)"\']+\.(?:jpg|jpeg|png|webp|svg|gif))\1\)', t, re.I):
        assets["css_bg"].add(urllib.parse.urljoin(c, m[1]))

for k in ("direct","css_bg","inline_svg","css_files"):
    print(f"{k}: {len(assets[k])}")
json.dump({k: sorted(v) for k,v in assets.items() if k!="inline_svg"}, open("_assets_found.json","w"), indent=1)
open("_inline_svgs.txt","w").write("\n\n<!-- ---- -->\n\n".join(sorted(assets["inline_svg"])))
