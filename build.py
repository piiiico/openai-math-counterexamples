#!/usr/bin/env python3
"""Rebuild the scoreboard and row table in README.md from rows.tsv and census.tsv. No number is typed by hand."""
import collections, re
rows = [l.split("\t") for l in open("rows.tsv", encoding="utf-8").read().splitlines()[1:] if l.strip()]
census = [l.split("\t") for l in open("census.tsv", encoding="utf-8").read().splitlines()[1:] if l.strip()]
in_census = {r[0] for r in census}
fams = sorted(set(r[0] for r in rows) & in_census)
extra = sorted(set(r[0] for r in rows) - in_census)
c = collections.Counter(r[4] for r in rows if r[0] in in_census)
board = (f"**{len(fams)} of {len(census)} counterexample families classified** · open {len(census) - len(fams)} · "
         f"holds {c['holds']} · fails {c['fails']} · not-explicit {c['not-explicit']} · not-finite {c['not-finite']}"
         + (f"<br>plus {len(extra)} outside the census, a counterexample OpenAI added in a correction: " + ", ".join(f"{r[0]} {r[4]}" for r in rows if r[0] in extra) if extra else ""))
status = {r[0]: r[4] for r in rows}  # census.tsv status column follows rows.tsv, never typed by hand
with open("census.tsv", encoding="utf-8") as fh: chdr = fh.readline()
open("census.tsv", "w", encoding="utf-8").write(chdr + "".join("\t".join(r[:-1] + [status.get(r[0], "open")]) + "\n" for r in census))
table = ["| family | what the script checks | result | agent | output sha256 | checked against (openai/math commit · source sha256) |", "|---|---|---|---|---|---|"]
for r in rows:
    assert len(r) == 10 and len(r[8]) == 40, f"row {r[0]}: needs source_commit (full 40-char sha) and source_sha256"
    src_h = "; ".join(f"`{x[:12]}`" for x in r[9].split(";"))
    table.append(f"| [{r[0]}](rows/{r[0]}/) | {r[1]} | **{r[4]}** | {r[6]} | `{r[7]}` | [`{r[8][:7]}`](https://github.com/openai/math/tree/{r[8]}) · {src_h} |")
src = open("README.md", encoding="utf-8").read()
src = re.sub(r"<!-- board -->.*?<!-- /board -->", "<!-- board -->\n" + board + "\n<!-- /board -->", src, flags=re.S)
src = re.sub(r"<!-- rows -->.*?<!-- /rows -->", "<!-- rows -->\n" + "\n".join(table) + "\n<!-- /rows -->", src, flags=re.S)
open("README.md", "w", encoding="utf-8").write(src)
print(board)
# The human page (docs/index.html) gets the same board and the holds rows, from the same files.
import datetime, html
titles = {r[0]: r[1] for r in census}
titles.setdefault("342", "Taming implies compatibility on four-manifolds (the example OpenAI added on 7 Oct)")
page_board = (f'<p class="board"><strong>{len(census)}</strong> counterexample families · <strong>{c["holds"]}</strong> hold · '
              f'<strong>{c["fails"]}</strong> fail · <strong>{c["not-explicit"]}</strong> not written down · '
              f'<strong>{c["not-finite"]}</strong> no finite check · <strong>{len(census) - len(fams)}</strong> unclassified</p>'
              f'<p class="meta">From census.tsv and rows.tsv, rebuilt {datetime.date.today().isoformat()}. '
              + ("Plus " + ", ".join(f"{r[0]} ({r[4]})" for r in rows if r[0] in extra) + ", a counterexample OpenAI added in a correction." if extra else "") + "</p>")
holds = [f'<tr><td><a href="https://github.com/piiiico/openai-math-counterexamples/tree/main/rows/{r[0]}">{r[0]}</a></td>'
         f'<td>{html.escape(titles.get(r[0], ""))}</td><td>{html.escape(r[6].replace("pico_amdal", "Pico"))}</td></tr>'
         for r in sorted(rows, key=lambda r: r[0]) if r[4] == "holds"]
pg = open("docs/index.html", encoding="utf-8").read()
pg = re.sub(r"<!-- board -->.*?<!-- /board -->", "<!-- board -->\n" + page_board + "\n<!-- /board -->", pg, flags=re.S)
pg = re.sub(r"<!-- holds -->.*?<!-- /holds -->", "<!-- holds -->\n" + "\n".join(holds) + "\n<!-- /holds -->", pg, flags=re.S)
open("docs/index.html", "w", encoding="utf-8").write(pg)
