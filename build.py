#!/usr/bin/env python3
"""Rebuild the scoreboard and row table in README.md from rows.tsv and census.tsv. No number is typed by hand."""
import collections, re
rows = [l.split("\t") for l in open("rows.tsv", encoding="utf-8").read().splitlines()[1:] if l.strip()]
census = [l.split("\t") for l in open("census.tsv", encoding="utf-8").read().splitlines()[1:] if l.strip()]
c = collections.Counter(r[4] for r in rows)
fams = sorted(set(r[0] for r in rows))
board = (f"**{len(fams)} of {len(census)} counterexample families checked** · "
         f"holds {c['holds']} · fails {c['fails']} · not-explicit {c['not-explicit']} · not-finite {c['not-finite']}")
table = ["| family | what the script checks | result | agent | output sha256 |", "|---|---|---|---|---|"]
for r in rows:
    table.append(f"| [{r[0]}](rows/{r[0]}/) | {r[1]} | **{r[4]}** | {r[6]} | `{r[7]}` |")
src = open("README.md", encoding="utf-8").read()
src = re.sub(r"<!-- board -->.*?<!-- /board -->", "<!-- board -->\n" + board + "\n<!-- /board -->", src, flags=re.S)
src = re.sub(r"<!-- rows -->.*?<!-- /rows -->", "<!-- rows -->\n" + "\n".join(table) + "\n<!-- /rows -->", src, flags=re.S)
open("README.md", "w", encoding="utf-8").write(src)
print(board)
