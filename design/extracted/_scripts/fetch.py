import re, json, os, urllib.request, html, time, hashlib
from collections import defaultdict
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
pages=json.load(open("_pages.json"))
def get(u,b=False):
    try:
        with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60) as r:
            d=r.read(); return d if b else d.decode("utf-8","ignore")
    except Exception: return None

def original(u): return re.sub(r'-\d{2,4}x\d{2,4}(?=\.(jpg|jpeg|png|webp|gif)$)','',u,flags=re.I)

# map image -> source pages
byimg=defaultdict(set)
for u in pages:
    s=get(u)
    if not s: continue
    hits=set()
    for m in re.findall(r'/wp-content/uploads/[^\s"\'\\<>()]+?\.(?:jpg|jpeg|png|webp|gif|svg)', s, re.I):
        hits.add("https://manastirea-saharna.md"+html.unescape(m).replace("\\/","/"))
    slug=u.rstrip("/").split("/")[-1] or "home"
    for h in hits: byimg[original(h)].add(slug)
    time.sleep(0.12)

# folder rules from page slug
RULES=[("biserica-sfanta-treime","church-sfanta-treime"),
       ("biserica-nasterea","church-nasterea-maicii"),
       ("rupestra","cave-chapel-bunavestirea"),
       ("casa-de-oaspeti","guesthouse-sf-avraam"),
       ("imagini-de-ansamblu","complex-overview"),
       ("moastele","relics-macarie"),("macarie","st-macarie"),
       ("istoria","history"),("cronica","chronicle"),
       ("obstea","brotherhood"),("staretul","abbot"),("mitropolitul","metropolitan"),
       ("biblioteca","library"),("pomelnic","pomelnic"),("home","home")]
def folder(slugs):
    for key,dest in RULES:
        if any(key in s for s in slugs): return dest
    return "misc"

os.makedirs("images",exist_ok=True)
manifest=[]; counts=defaultdict(int)
for i,(img,slugs) in enumerate(sorted(byimg.items())):
    d=get(img,b=True)
    if not d or len(d)<8000: continue          # skip icons/spacers
    dest=folder(slugs); os.makedirs(f"images/{dest}",exist_ok=True)
    name=img.split("/")[-1]
    p=f"images/{dest}/{name}"
    if os.path.exists(p):
        name=hashlib.md5(img.encode()).hexdigest()[:6]+"_"+name; p=f"images/{dest}/{name}"
    open(p,"wb").write(d)
    counts[dest]+=1
    manifest.append({"file":p,"url":img,"pages":sorted(slugs),"bytes":len(d)})
    time.sleep(0.08)

json.dump(manifest,open("_manifest.json","w"),indent=1)
print("downloaded:",len(manifest))
for k,v in sorted(counts.items(),key=lambda x:-x[1]): print(f"  {v:4d}  {k}")
