# Literature search: explicit labelling for family 132

Date: 2026-11-03. Performed by Anthropic Claude (Claude Code) as a separate
AI literature search for Alexander Richard Towell. This is a search report,
not a review of the proof. "Found and read" means the quoted text was
retrieved from the named source in this session. "Inferred" means a
conclusion drawn by the searcher that the source does not state.

Subject: the manuscript "A superquadratic separation between sensitivity and
block sensitivity" (openai/math, commit
fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb, `preprints/`), Lemma
`lem:labelling` (random labels with no bad set of size t = 16), and our
explicit labelling a(i,j) = bit_length((i-1) XOR (j-1)) with the bound
|I| <= ceil(log2 k) + 1 for every bad set in every tournament.

## Summary of conclusions

1. No source found states the explicit-labelling lemma (top-differing-bit
   labels, any orientation, bad sets where all in-edges inside the set at
   each vertex carry one label). The colouring itself is classical; the
   lemma about it was not found.
2. Meiburg (2026) uses random labels and the Lovasz local lemma; its main
   construction is nonconstructive. It proposes one explicit rule
   (a cyclotomic / discrete-log gate assignment on Paley tournaments) only
   for empirical estimates, not in a proof. No XOR or bit labelling.
3. Classical explicit separations (Rubinstein, Virza, Ambainis and Sun,
   Chaubal and Gal) give only bs = c s^2 with c <= 2/3. None gives an
   unbounded ratio bs/s^2, so none makes an explicit version of the
   manuscript's separation redundant.
4. The registry row 132 is labelled **not-explicit** because of the random
   labelling. One follow-up (Qiuyu Chen, "bound-132") calls its family
   "explicit" in the computable sense: it fixes labels by a terminating
   lexicographic-first search justified by the same union bound. This is
   the nearest prior "explicit" claim and should be cited; it is not a
   closed-form labelling.

## Q1. Is the explicit-labelling lemma already known?

### Found and read

- **Conlon, Fox, Lee, Sudakov, "On the grid Ramsey problem and related
  questions", arXiv:1405.6587v2 (2014), Section 2.**
  https://arxiv.org/abs/1405.6587
  Exact text (pdftotext extraction): "We denote the (3, 2)-coloring by cB,
  where 'B' stands for 'binary'. ... we consider the vertex set [n] as a
  subset of {0, 1}^t by identifying x with (x1, ..., xt), where
  sum_{i=1}^t x_i 2^{i-1} is the binary expansion of x - 1. Then, for two
  vertices x = (x1, ..., xt) and y = (y1, ..., yt), cB(x, y) is the minimum
  i for which xi != yi. This coloring uses at most ceil(log n) colors and is
  a (3, 2)-coloring since three vertices cannot all differ in the i-th
  coordinate. In fact, it is a chromatic-(2d + 1, d + 1)-coloring for all
  integers d >= 1, since it gives an edge partition E = E1 u ... u Et of Kn
  for t = ceil(log n) such that, for all J subset [t], the graph consisting
  of the edges of the union of E_j, j in J, has chromatic number at most
  2^|J|."
  Relevance: this is the same colouring family (minimum differing bit; the
  top-differing-bit version is the same up to reversing bit order, and the
  dyadic structure is identical). The paper uses it for (p,q) and chromatic
  Ramsey properties of undirected K_n. It states nothing about tournaments,
  orientations, or head-determined (in-star monochromatic) sets.

- **Erdos-Hajnal stepping-up lemma, as stated by Conlon, Fox, Sudakov, "An
  improved bound for the stepping-up lemma", arXiv:0907.0283.**
  https://arxiv.org/abs/0907.0283
  Search snippets for this and arXiv:2507.05641 and arXiv:2504.05647
  describe the classical function delta(x, y) = the largest index where
  binary strings x and y differ, with the property delta(a, b) !=
  delta(b, c) for a < b < c. The stated lemma (from the search result):
  "If k >= 3 and N -/-> (n)^k_l, then 2^N -/-> (2n + k - 4)^{k+1}_l."
  Relevance: delta is exactly our label a(i,j) (top differing bit). It is
  used for hypergraph Ramsey lower bounds, not for the oriented
  in-star property. I read search-result text for these, not the full
  papers.

### Searched, nothing found

Queries (standard and extended WebSearch): XOR colouring / binary colouring /
highest differing bit colouring of K_n with log n colours; stepping-up delta
colouring; edge-coloured tournaments with monochromatic in-neighbourhoods,
"in-monochromatic", "locally monochromatic" subtournaments; ultrametric or
binary-tree-level colourings of tournaments. Results were the colourings
above and unrelated work on monochromatic paths and trees in 2-edge-coloured
tournaments (Bucic, Heberle, Letzter, Sudakov, arXiv:1703.10424 and
arXiv:1809.07089; Sands, Sauer, Woodrow absorbing vertices; Yuster on
path-monochromatic arborescences). None treats sets where the label of each
arc inside the set is a function of its head.

### Inferred

- The colouring is classical (binary / delta colouring), so the write-up
  should cite it (e.g. Conlon, Fox, Lee, Sudakov, Section 2, and the
  Erdos-Hajnal stepping-up delta function) rather than present the
  colouring as new. The bound "every head-determined set in any orientation
  has at most ceil(log2 k) + 1 vertices" was not found and appears new as
  far as this search reaches; a short dyadic induction like ours is the
  kind of argument that could exist unrecorded in folklore, so claim it
  with that caveat.
- The tightness example (transitive tournament) echoes the Erdos-Moser
  log-size transitive subtournament phenomenon, but no source found makes
  this connection for labelled tournaments.

## Q2. Meiburg (2026)

### Found and read

- **Alexander Meiburg, "Block Sensitivity can exceed Spectral Sensitivity
  Squared", arXiv:2608.00851 [cs.CC], submitted 1 August 2026.**
  https://arxiv.org/abs/2608.00851 (HTML: https://arxiv.org/html/2608.00851)
  Section titles: 3.1 "Certificates as Subcubes"; 5.2 "Internal
  obstructions"; 5.3 "Radius one"; 5.4 "Radius two"; 5.5 "The local lemma".
  Exact statements retrieved:
  - Section 3.1: "we do not make any statements about the moment about how
    to select the m(i,j)".
  - Section 5 introduction: "Instead we draw each m(i,j) independently and
    uniformly from B_j and show that with positive probability no violation
    occurs." and "The tournament is not random: it is fixed in advance, and
    it must be chosen so that the violations can be counted."
  - Section 5.5 (local lemma): "then with positive probability no bad
    event occurs."
  - Introduction: "While the headline construction is nonconstructive, we
    do give one concrete total Boolean function on n=30 variables."
  - Section 5.1: Paley tournaments give "a classic construction of doubly
    regular tourament" (sic).
  - Section 6.1: an explicit "cyclotomic gate assignment",
    g(i,j) = dlog(j - i) on a Paley tournament, used for numerical
    estimates; "this exponent is not proved."
  - Abstract: leftover freedom is "resolved by the Lovasz local lemma"; the
    main result is formally verified in Lean.
  Relevance: Meiburg's labels m(i,j) take values in a per-head block B_j
  and must avoid radius-one and radius-two obstructions, a different
  forbidden configuration from the manuscript's (the manuscript itself says
  it uses "a different forbidden-label condition and a direct union bound").
  Meiburg gives no XOR, bit, or other proved explicit labelling and no
  derandomization. The 30-variable example has r = 2 and is a single finite
  witness, not a family.

- MathWorld, "Block Sensitivity" (https://mathworld.wolfram.com/BlockSensitivity.html):
  "Meiburg (2026) constructed a total Boolean function on 2,017,584
  variables with bs(f)>=14011 and lambda(f)<=89.0162"; "an independent
  rebuild and independent mathematical review had not been reported as of
  Oct. 8, 2026".

## Q3. Prior explicit bs versus s^2 separations

### Found and read

- Rubinstein (1995): bs(f) = (1/2) s(f)^2; Virza (arXiv:1008.0521):
  bs(f) = (1/2) s(f)^2 + s(f) per MathWorld and the search summary (the
  manuscript cites Virza as (1/2)s^2 + (1/2)s; this report did not
  reconcile the two forms); Ambainis and Sun, "New separation between s(f)
  and bs(f)", arXiv:1108.3494: bs(f) = (2/3) s(f)^2 - (1/3) s(f) (abstract
  read, paraphrased by the fetch tool; the manuscript cites Theorem 1).
- Chaubal and Gal, "New Constructions with Quadratic Separation between
  Sensitivity and Block Sensitivity", ECCC TR18-205
  (https://eccc.weizmann.ac.il/report/2018/205/): "Some of our
  constructions match the current largest separation between sensitivity
  and block sensitivity ... by Ambainis and Sun." and "we give the first
  direct constructions of families of Boolean functions ... that have both
  0-block sensitivity and 1-block sensitivity quadratically larger than
  sensitivity."
- Robin Kothari, bigospeedrun/site issue 2 (https://github.com/bigospeedrun/site/issues/2,
  opened 2026-10-15): classical exponent 2 (Rubinstein); OpenAI's problem
  132 seed gives exponents about 2.000252 (d=9, M=9^10) and 2.00647
  (d=20, M=9^21). No mention of labels or explicitness.

### Inferred

All classical constructions are explicit but have bounded ratio
bs/s^2 <= 2/3 + o(1). None achieves bs >= 2^d/(4(d+2)^2) s^2 for growing d,
so they do not pre-empt an explicit version of the manuscript's theorem.

## Q4. Registry row 132 and openai/math

### Found and read

- **piiiico/openai-math-counterexamples README, row 132**
  (https://github.com/piiiico/openai-math-counterexamples): "claim:
  bs(f) >= 2^d/(4(d+2)^2) s(f)^2 for the recursive predicates; the
  tournament is explicit but the edge labelling a(i,j) is chosen at random
  and only shown to exist (01-construction.tex:36-46), so no f is written
  down", status "**not-explicit**", agent pico_amdal. The link `rows/132/`
  does not exist in the repository tree (checked via the GitHub API,
  2026-11-03). No registry issue or PR mentions row 132 or sensitivity.
- **openai/math**: issues are disabled; no PR title mentions sensitivity
  or 132. The Lean development at commit adc7f1241b42 contains
  `Labeling*.lean` files including `LabelingProbability.lean` and
  `LabelingEstimate.lean` (file listing only, not read), consistent with a
  probabilistic labelling proof.
- **Hub page** (https://mathcommunity.github.io/oai-math-revised/papers/A-superquadratic-separation-between-sensitivity-and-block-sensitivity-September-25-2026/):
  lists follow-ups; none described as giving a closed-form labelling.
  Orply's exposition is described as "explicitly leaving the
  label-existence calculation and full recurrence algebra undeveloped."
- **Qiuyu Chen, "An exact certificate above 2.032083 for sensitivity
  versus block sensitivity"**, canghaimeng/openai-math-improvement,
  `problems/bound-132/paper.pdf` (commit b3c7abea0d5e, read in full text
  via pdftotext). Abstract: "gives an explicit infinite family of total
  Boolean functions"; "The proof includes the finite deterministic label
  search". Section 2.1: tournament i -> j when (j - i) mod k in
  {1, ..., h}, h = 2^e, k = 2h + 1, labels a(i,j) in {1, 2, 3, 4},
  tau = e + 6; "Such labels exist: independent uniform labels satisfy the
  conditions for fixed I, (m_j) with probability 4^{-binom(tau,2)}"; "Order
  the directed edges lexicographically by (i, j) and choose the first
  lexicographic label vector passing the finite exclusion test. Existence
  proves that this deterministic search terminates." Also: "The
  specification is computable by terminating finite searches." Builds on
  "ProveIt Part I" ("An explicit exponent above 65/32 ...", revision
  5476940edc3a), which this search could not locate.
- **Prove2Me** "Reach 2.13981" mission
  (https://beta.prove2.me/missions/Block_Sensitivity_vs._Sensitivity%3A_Reach_%242.13981%24):
  "A labeling existence theorem simultaneously enforces the marked, arc,
  and three-vertex exclusions used in the repair bounds." and "The
  recursive family fixes one such labeling and uses it at every depth."
  The campaign page (https://prove2.me/campaigns/block-sensitivity-vs-sensitivity)
  lists 23 missions (exponent 2 up to an open 2.15) and does not describe
  any labelling method.

### Inferred

- "Explicit" is already claimed for row 132 in a weaker sense (Chen:
  computable by brute-force search over an astronomically large label
  space, existence via union bound). Our labelling is explicit in the
  strong sense (a closed formula, polynomial-time evaluable, with a direct
  combinatorial proof, no union bound). The write-up should cite Chen and
  state this distinction, not claim to be the first "explicit" family.
- Parameter caution (not from any source): our labels use about
  ceil(log2 k) values, while Chen uses r = 4 and the manuscript r =
  ceil(sqrt M). The XOR labelling therefore fits the manuscript's
  parameters (log2(2M^2+1) is far below sqrt M for M >= 9^{d+1}) but not
  constant-r variants such as Chen's. Replacing t = 16 by
  t = ceil(log2 k) + 2 must be checked against every downstream use of t
  in the manuscript's recurrences; this search did not check that.

## Search log

WebSearch queries: Meiburg 2026 sensitivity block sensitivity; binary /
XOR / highest-differing-bit colouring of K_n with log n colours (standard
and extended); stepping-up delta colouring; edge-coloured tournament
monochromatic in-neighbourhood (two variants); ProveIt "explicit exponent
above 65/32"; explicit labelling superquadratic separation family 132
(extended). WebFetch: arXiv 2608.00851 (abs and HTML), MathWorld Block
Sensitivity, registry README, hub page (twice), Chen bound-132 README,
Prove2Me mission and campaign pages, bigospeedrun issue 2, ECCC TR18-205,
arXiv 1108.3494, arXiv 1405.6587 (PDF, extracted locally). GitHub API (gh):
registry tree, issues and PRs; openai/math PRs; mathcommunity issues;
openai/math Lean directory listing; Chen paper.pdf.
