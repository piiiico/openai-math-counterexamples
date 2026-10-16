# Contributing a check

This repo re-runs the counterexamples in [openai/math](https://github.com/openai/math). Its scope is the 63 counterexample families in [`census.tsv`](census.tsv), plus counterexamples OpenAI adds in corrections (row 342). Checks of other results belong elsewhere: family 109 in [CrocSwap/integer-mult-bounds](https://github.com/CrocSwap/integer-mult-bounds), Lean statement fidelity in [mathvet](https://github.com/mathvet/mathvet).

People, agents and people working with agents are all welcome. Say which in the PR.

## One family, one script, one result

A check is a pull request that adds or changes one directory `rows/NNN/` and one line of `rows.tsv`.

1. **One script.** `rows/NNN/check.py` (or a package with a single entry command). It prints a line starting `RESULT:` and exits non-zero unless the computation agrees with the paper.
2. **Cite the claim.** The docstring or README quotes the claim it checks, with the file and line in openai/math, at a pinned commit (full 40-character sha in `rows.tsv`) and the sha256 of each source file read.
3. **Pinned dependencies.** Standard library if you can. Otherwise a `requirements.txt` with exact versions, and the Python version you ran.
4. **A negative control that must fail.** Change one input (an entry of the matrix, one edge, the precision) and show the script then exits non-zero. A check that cannot fail checks nothing.
5. **State the scope.** Say what the script computes and what it does not: which step of the paper is a proof it did not compute. A row never says a theorem is true or false.
6. **Output.** Commit `output.txt`. Its sha256 goes in `rows.tsv`.

Then run `python3 build.py`, which rebuilds the board in the README and on the page from `rows.tsv` and `census.tsv`. No number is typed by hand.

## What counts

Not only a new **holds**. These are contributions too, and are credited the same way:

- a second, independent implementation of a row that already holds (rows 272 and 361 have one);
- an audit that says a **not-finite** or **not-explicit** call is wrong, with the object or the finite step that makes it checkable;
- a check that does not go through, written up with what was tried;
- a **fails**: our computation disagreeing with the paper at a cited line. Before a fails row is published, it is re-implemented independently here.

## What happens to your PR

- It is re-run on a clean checkout, with your pinned dependencies and your negative control.
- You are credited by name, in `rows.tsv` and the README, in the form you choose. If an AI system helped, say how; the disclosure is kept.
- You get an answer within a day.

Nobody here judges a proof by reading it. If your check needs a referee rather than a computer, it belongs somewhere else.

## Before you start

Claim the family in an issue ([Check request](.github/ISSUE_TEMPLATE/check-request.md)) so two people do not do the same work. Search open issues and PRs for the family number first.
