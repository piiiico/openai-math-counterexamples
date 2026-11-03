# Family 132: an explicit edge labelling (candidate)

**Status.** Finite computation done; written proof drafted (AI-reviewed, not
human-reviewed). Claimed in
[#45](https://github.com/piiiico/openai-math-counterexamples/issues/45).

## Background

Family 132 in `piiiico/openai-math-counterexamples` is OpenAI's preprint *A
superquadratic separation between sensitivity and block sensitivity*
(25 September 2026; openai/math commit
`fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`, directory
`preprints/A-superquadratic-separation-between-sensitivity-and-block-sensitivity-September-25-2026/build/sections`).
Its census status is "not-explicit". The construction is deterministic
except for Lemma `lem:labelling` (`source/01-construction.tex:27-47`): edges
of a regular tournament on `[k]`, `k = 2M^2 + 1`, get labels in `[r]`,
`r = ceil(sqrt M)`, chosen at random, so that no set of `t = 16` vertices is
"bad" (has choices `m_j` with `a(i,j) = m_j` on every edge `i -> j` inside
the set).

## Finding

1. **How `t` is used (checked against the text).** The labelling property
   is used once, at `02-recurrences.tex:70-80`, to bound the list `T` by
   `|T| < t`. After that `t` is only a coefficient
   (`02-recurrences.tex:13-16`) and, after normalisation, enters only
   `epsilon = max(r,t)/M` (`03-separation.tex:27`). The only property of
   `r` and `t` used is `max(r,t) <= 2 sqrt M`
   (`03-separation.tex:55-60`); the remaining proof
   (`03-separation.tex:63-102`) uses only `epsilon <= 2/3^(d+1)`, so even
   `max(r,t) <= 2M/3^(d+1)` would do. `r >= sqrt M` is needed only by the
   probabilistic proof. See `PROOF.md`
   section 1.
2. **An explicit labelling.** `a(i,j) = bit_length((i-1) XOR (j-1))`, the
   most significant bit in which `i-1` and `j-1` differ, with values in
   `[h]`, `h = ceil(log2 k)`. Lemma A (`PROOF.md` section 2): for **every**
   tournament on `[k]`, every bad set has at most `h + 1` elements, and this
   is attained. So `t = h + 2` works.
3. **Fitting it into the manuscript.** Replace `t = 16` by `t = h + 2` and
   either keep `r = ceil(sqrt M)` and take `M >= 290` (automatic for
   `M >= 9^(d+1)`, `d >= 2`; for `d = 1` choose such an `M`) or set
   `r = max(ceil(sqrt M), h)`. Then `max(r,t) <= 2 sqrt M` for all
   `M >= 81`, so `03-separation.tex:55-60` and everything after are
   unchanged. With `M = 9^(d+1)`, `d >= 2`, and the cyclic tournament, the
   function `f` is then written down explicitly. `PROOF.md` section 3.

The manuscript's statement with the constant `t = 16` is **not** made
explicit; the explicit route needs `t` to grow like `2 log2 M`, which the
proof tolerates.

## Evidence, separated

| Kind | What | Status |
| --- | --- | --- |
| Finite computation | `check.py`: exact maximum bad sets for the cyclic tournaments `M = 2..5`, transitive and pseudorandom tournaments up to `k = 40`; all bounded by `h + 1`; tightness examples; parameter inequalities for `81 <= M <= 20000` | passes |
| Finite computation | `test_check.py`: Lemma A on every labelled tournament with `k <= 6`; backtracking search equals exhaustive subset enumeration on several tournaments and labellings; all `2^19` subsets for `M = 3` | 18 tests pass, also under `python -O` |
| Written proof | `PROOF.md`: Lemma A, the trace of `t` and `r`, the parameter inequalities | Claude-written, unreviewed by a human |
| AI review | `REVIEW.md`: separate Claude agent, not a human | confirmed the trace, Lemma A and the inequalities; found wrong `03` line numbers, now fixed |
| Human review, upstream acceptance, archival | none | not done |

## Reproduce

Python 3.13.15, standard library only. From this directory:

```sh
bash reproduce.sh
```

It verifies `source/SHA256SUMS`, runs the tests under normal and optimised
Python, compares `check.py` output with `output.txt`, and asserts that each
negative control (`bound-too-small`, `constant-label`, `epsilon-below-57`,
`parity-label`) exits 1 with `RESULT: fails`, under both. The run takes
about ten seconds. Branch coverage of `check.py` is 99% (`logs/coverage.txt`;
the only missed line is the `sys.exit` guard).

## Outside scope

- The rest of the manuscript (Proposition `prop:recurrences`,
  Lemma `lem:blocks`, the final estimates) is taken as given and was read
  only where `t`, `r` and the labelling enter.
- An explicit labelling with a constant `t` (such as the manuscript's 16)
  and `r = ceil(sqrt M)` labels. Not needed for explicitness, not attempted.
- The introduction's prose "Random labels exclude..." (`00-introduction.tex:74`)
  would need rewording in an upstream edit; not drafted here.
- Novelty. The colouring is classical (Erdos-Hajnal stepping-up delta;
  Conlon-Fox-Lee-Sudakov binary colouring); no prior statement of Lemma A
  was found, and it may be folklore. Chen's bound-132 family is explicit
  only via a terminating search. See `LITERATURE.md` and `PROOF.md`
  section 4.
- Any upstream action. Nothing was posted or pushed.

## Attribution and AI disclosure

Prepared by Alexander Richard Towell with Anthropic Claude (Claude Code,
Opus 5.5). The trace of the manuscript, the labelling, Lemma A, the checker
and the tests were produced by Claude; Alexander Richard Towell set the task
and questions. The manuscript is OpenAI's (credited by the commit above);
its tournament architecture adapts Meiburg (2026), as the manuscript states
at `01-construction.tex:22-23`.
