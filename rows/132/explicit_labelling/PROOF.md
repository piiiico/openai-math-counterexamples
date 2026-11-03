# An explicit labelling for family 132 (candidate proof, unreviewed)

Status: written proof by Anthropic Claude (Claude Code), not yet reviewed by
a human or by a separate AI reviewer. It is a candidate, not an established
result. Only the parts of the manuscript where the labelling parameters
enter were read; the rest of the manuscript's argument is taken as given.

Source: openai/math commit `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`,
section files pinned in `source/SHA256SUMS`. Line numbers below refer to
those files.

## 1. What the manuscript needs from the labelling

Notation of `01-construction.tex:9-20`: `k = 2M^2 + 1`, `r = ceil(sqrt M)`,
`t = 16`, a tournament on `[k]` with every outdegree `M^2`.

Call a set `I` of vertices **bad** for a labelling `a` if there are choices
`m_j` (`j` in `I`) with `a(i,j) = m_j` for every edge `i -> j` with both ends
in `I`. Equivalently: for every `j` in `I`, all labels `a(i,j)` on edges
coming into `j` from `I` are equal. Lemma `lem:labelling`
(`01-construction.tex:27-34`) asserts a labelling with values in `[r]` and no
bad set of size `t`. Subsets of bad sets are bad (keep the same `m_j`), so
this is the same as "every bad set has fewer than `t` elements".

Uses of the lemma and of `t`:

- `02-recurrences.tex:70-80`. The clauses in `T` (exactly one failed target,
  no failed gate) form a bad set, so `|T| < t`, and their repairs contribute
  at most `t S'_0` flips. This is the only use of the lemma.
- `02-recurrences.tex:13-16`. Hence `t` appears as a coefficient in
  `S_{l,0} <= t S'_0 + S'_1 + 3 J'_1` and `J_{l,0} <= t S'_0 + 3 J'_1`.
- `03-separation.tex:27`. After normalisation `t` survives only in
  `epsilon = max(r,t)/M` (`03-separation.tex:34-52`).
- `03-separation.tex:55-60`. The only property of `r` and `t` used is
  `r <= 2 sqrt M` and `t = 16 <= 2 sqrt M` (for `M >= 81`), giving
  `epsilon <= 2/sqrt(M) <= 2/3^(d+1)`. The rest of the proof of
  Lemma `lem:quantitative-profiles` (`03-separation.tex:63-102`) uses only
  `epsilon <= 2/3^(d+1)`.
- The theorem and the corollary (`03-separation.tex:105-155`, `231-274`)
  use the labelling only through Lemma `lem:quantitative-profiles` and
  Lemma `lem:blocks`, apart from sentences saying that a labelling is fixed
  or supplied (`01-construction.tex:49`, `03-separation.tex:107`, `152`,
  `232-233`); `lem:blocks` (`01-construction.tex:168-193`) does not
  use the labels at all. The value of `r` enters elsewhere only as the row
  width (input lengths `N_l = LM(kr)^l`, block sizes `L r^l`, and the
  coefficient `r S'_1`), none of which needs `r >= sqrt M`.

So `t` and `r` may be any positive integers with
`max(r, t) <= 2 sqrt M`; in fact `max(r, t) <= 2M/3^(d+1)` suffices,
because only `epsilon <= 2/3^(d+1)` is used later. The bound `r >= sqrt M`
is needed only by the probabilistic proof at `01-construction.tex:35-46`.

## 2. The explicit labelling

Identify vertex `v` in `[k]` with the binary expansion of `v - 1`, a string
of `h = ceil(log2 k)` bits (bits numbered `0, ..., h-1` from least
significant). For distinct `i, j` put

    a(i, j) = 1 + (index of the most significant bit in which i-1 and j-1 differ)
            = bit_length((i - 1) XOR (j - 1)).

So `a(i,j)` is in `[h]` and `a(i,j) = a(j,i)`. It does not depend on the
tournament.

**Lemma A.** For every tournament on `[k]`, every bad set for this labelling
has at most `h + 1` elements.

*Proof.* For `0 <= p <= h`, a *level-p block* is a set of vertices whose
expansions agree in all bits of index at least `p`. It has at most `2^p`
elements. We prove by induction on `p` that every bad set `I` contained in a
level-`p` block has `|I| <= p + 1`. All of `[k]` is a level-`h` block,
which gives the lemma.

For `p = 0` the block has one element. Let `p >= 1` and let `I` be a bad set
in a level-`p` block. Split `I` by bit `p - 1` into `I_0` and `I_1`. Each is
contained in a level-`(p-1)` block and is bad, so `|I_0|, |I_1| <= p` by
induction. Members of `I` agree in all bits of index at least `p`. Hence an
edge between `I_0` and `I_1` has label exactly `p`, and an edge inside `I_0`
or inside `I_1` has label at most `p - 1`.

Suppose `|I_0| >= 2` and `|I_1| >= 2`. Take any edge inside `I_0` and let `u`
be its head; `u` has an in-neighbour in `I_0`, with label at most `p - 1`.
Because `I` is bad, all edges into `u` from `I` have the same label, so `u`
has no in-neighbour in `I_1`. Since the tournament orients every pair,
`u -> w` for every `w` in `I_1`. In the same way some `v` in `I_1` has
`v -> w` for every `w` in `I_0`. Then both `u -> v` and `v -> u`, which is
impossible. So one of the parts, say `I_1`, has at most one element, and
`|I| <= |I_0| + 1 <= p + 1`. QED.

The bound is attained: in the transitive tournament (`i -> j` iff `i < j`)
the vertices with `v - 1` in `{0, 1, 3, 7, ..., 2^(h-1) - 1, k - 1}` form a
bad set of size `h + 1` (`check.py`, check 4).

## 3. Plugging it into the manuscript

Put `h = ceil(log2 k)` with `k = 2M^2 + 1`, and replace `t = 16` by
`t = h + 2`. Lemma A gives Lemma `lem:labelling` for this `t`, provided the
labels lie in `[r]`, i.e. `h <= r`. Two ways to arrange that:

1. Keep `r = ceil(sqrt M)` and require `M >= 290`. Then `h <= ceil(sqrt M)`
   (finite check for `290 <= M <= 20000` in `check.py`; for larger `M`,
   `h <= 2 log2 M + 2 <= sqrt M` since `x - 4 log2 x - 2` is increasing for
   `x >= 6` and positive at `x = sqrt 20000`). It fails at `M = 289`
   (`h = 20 > 17`). Every `M >= 9^(d+1)` with `d >= 2` qualifies; for `d = 1`
   choose `M >= 290`, which the theorem allows (it only needs `M >= 9^(d+1)`).
2. For all `M >= 81`, set `r = max(ceil(sqrt M), h)` instead. This changes
   only the row width, hence the dimension `n = LM^2(kr)^d` and the
   coefficient of `S'_1`; the ratio bound (`03-separation.tex:144-147`)
   depends on `k/M^2` only.

In either case `t = h + 2 <= 2 sqrt M` for all `M >= 81`:
`h = bit_length(2M^2)`, so `2^(h-1) <= 2M^2` and `h <= 2 + 2 log2 M`. With
`x = sqrt M >= 9`, it suffices that `2 log2 x + 2 <= x`; this holds at
`x = 9` (`2 log2 9 + 2 < 8.34`), and `x - 2 log2 x - 2` is increasing for
`x > 2/ln 2`. Also `r <= 2 sqrt M` (`ceil(sqrt M) <= 2 sqrt M`, and
`h <= t <= 2 sqrt M`). This is exactly the inequality used at
`03-separation.tex:55-60`, so `epsilon <= 2/sqrt M <= 2/3^(d+1)` and the
remainder of the manuscript applies unchanged. (`check.py` check 5 confirms
`max(ceil(sqrt M), h + 2)^2 <= 4M` for `81 <= M <= 20000`; it fails for
`M <= 56`.)

With `M = 9^(d+1)` (for `d >= 2`), the cyclic tournament of
`01-construction.tex:18-20`, `r = ceil(sqrt M)` and the labels above, every
ingredient of the function `f` (OR of `M` copies of `P_{d,1}`,
`03-separation.tex:108-110`) is defined deterministically, so `f` is written
down. Its claimed bound `bs(f) >= 2^d/(4(d+2)^2) s(f)^2` then rests on the
manuscript's remaining argument with `t = h + 2`.

## 4. What this does not show

- The rest of the manuscript (Proposition `prop:recurrences`, the blocks,
  the final count) is not re-verified here. Only the claim "`t` enters only
  through `|T| < t` and `epsilon`" was checked against the text.
- The manuscript's statement with the fixed value `t = 16` is not made
  explicit: the explicit labelling needs `t = h + 2`, which grows like
  `2 log2 M`. Whether an explicit labelling with `r = ceil(sqrt M)` labels
  and a constant `t` exists is not addressed.
- No novelty is claimed for the colouring. Labelling an edge by the top
  differing bit is the classical delta function of the Erdos-Hajnal
  stepping-up lemma; Conlon, Fox, Lee and Sudakov (arXiv:1405.6587, Section 2)
  call the least-differing-bit variant the binary colouring. Those uses are
  undirected Ramsey properties. A search (`LITERATURE.md`, 2026-11-03) found
  no prior statement of Lemma A (bad sets in an arbitrary orientation), but
  an elementary argument like this may be folklore.
- Qiuyu Chen's bound-132 family (canghaimeng/openai-math-improvement,
  `problems/bound-132/paper.pdf`, commit b3c7abea0d5e) is called explicit in
  a weaker sense: labels in {1,2,3,4} chosen as the first lexicographic
  vector passing a finite test, whose termination rests on the random-label
  count. The labelling here is a closed formula with a direct proof. It
  needs about log2 k labels, so it does not apply to constant-r variants
  such as Chen's r = 4.
