# Row 132: second check of Lemma A (Pico)

Independent of `../explicit_labelling/` (no shared code; different method). Written by Pico, an AI agent.

Lemma A (`../explicit_labelling/PROOF.md` §2): under `a(i,j) = bit_length((i-1) XOR (j-1))`, every bad set in every tournament on `[k]` has at most `h + 1` elements, `h = ceil(log2 k)`.

Badness of a set depends only on the labelled tournament induced on it. So the lemma holds for all tournaments on `[k]` iff no `(h+2)`-subset of `[k]` is bad under any orientation of that subset. `check.py` enumerates exactly that, with a pruned search over orientations, for every `k <= 24` (1,076,762 subsets, about 95 s), and checks that some `(h+1)`-set is bad for each `k`.

    python3 check.py 24              # RESULT: passes
    python3 check.py 8 --label const # negative control, RESULT: fails, exit 1

Python 3.13.5, standard library. `output.txt` holds both runs.

Scope: a finite case of Lemma A, `k <= 24`. It does not check the general lemma, the reading that `t` may be replaced by `h + 2`, or the manuscript's bound. The row status stays `not-explicit`.
