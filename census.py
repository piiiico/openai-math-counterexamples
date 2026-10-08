import re, json, os, sys
ROOT = sys.argv[1]
txt = open(os.path.join(ROOT, "CONTENTS.md"), encoding="utf-8").read()
# family headers
hdr = re.compile(r"^\*\*(\d{3})\. (.+?)\*\*\s*(.*)$", re.M)
fams = []
ms = list(hdr.finditer(txt))
for i, m in enumerate(ms):
    end = ms[i+1].start() if i+1 < len(ms) else len(txt)
    block = txt[m.end():end]
    dirs = sorted(set(re.findall(r"\(preprints/([^/)]+)/", block)))
    fams.append(dict(family=m.group(1), title=m.group(2).rstrip("."), headline=m.group(3).strip(), dirs=dirs))
KW = re.compile(r"counterexample|disprov|refut|\bfails?\b|\bfalse\b|negative answer|no such|does not hold|cannot be|is not|are not", re.I)
STRONG = re.compile(r"counterexample|disprov|refut|negative (answer|solution|resolution)|\bfails?\b|\bfalse\b", re.I)
ANC = (".py",".json",".txt",".cpp",".hpp",".tsv",".jsonl",".sage",".g",".m",".gp",".mmd")
out = []
for f in fams:
    hl = f["title"] + ". " + f["headline"]
    strong = bool(STRONG.search(hl))
    anc = []
    for d in f["dirs"]:
        p = os.path.join(ROOT, "preprints", d)
        for dp, _, fs in os.walk(p):
            for fn in fs:
                if fn.endswith(ANC):
                    anc.append(os.path.relpath(os.path.join(dp, fn), ROOT))
    f["counterexample_headline"] = strong
    f["ancillary"] = sorted(anc)
    out.append(f)
json.dump(out, open("families.json","w"), indent=1, ensure_ascii=False)
print("families", len(out), "strong", sum(f["counterexample_headline"] for f in out),
      "strong+anc", sum(f["counterexample_headline"] and bool(f["ancillary"]) for f in out))
