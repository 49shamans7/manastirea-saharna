import re, json, urllib.request, urllib.parse, html, time
from collections import Counter
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
pages=json.load(open("_pages.json"))
def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40) as r: return r.read().decode("utf-8","ignore")
    except Exception: return ""
found=set()
for u in pages:
    s=get(u)
    # any uploads path anywhere in the document, attribute or not
    for m in re.findall(r'(?:https?:)?//manastirea-saharna\.md/wp-content/uploads/[^\s"\'\\<>()]+?\.(?:jpg|jpeg|png|webp|gif|svg)', s, re.I):
        found.add("https:"+m if m.startswith("//") else m)
    for m in re.findall(r'/wp-content/uploads/[^\s"\'\\<>()]+?\.(?:jpg|jpeg|png|webp|gif|svg)', s, re.I):
        found.add("https://manastirea-saharna.md"+m)
    for m in re.findall(r'/wp-content/(?:themes|plugins)/[^\s"\'\\<>()]+?\.(?:png|svg|gif|jpg)', s, re.I):
        found.add("https://manastirea-saharna.md"+m)
    time.sleep(0.15)
found={html.unescape(x).replace("\\/","/") for x in found}
print("raw urls:", len(found))
# collapse wordpress size variants  name-1024x768.jpg -> name.jpg
def original(u):
    return re.sub(r'-\d{2,4}x\d{2,4}(?=\.(jpg|jpeg|png|webp|gif)$)', '', u, flags=re.I)
originals=sorted({original(u) for u in found})
print("after collapsing size variants:", len(originals))
print("by extension:", Counter(u.rsplit('.',1)[-1].lower() for u in originals))
json.dump(originals, open("_originals.json","w"), indent=1)
