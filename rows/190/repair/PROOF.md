# A sharp repair for the ordered-matrix construction

Alexander Richard Towell, with substantial OpenAI Codex assistance.
OpenAI supplied the pattern, host, distance lower bound and anchor-rigidity
mechanism. Pico / Håkon Åmdal supplied the preceding finite replay. The new
contribution is the explicit repair and the construction-specific upper bound,
with a separate exact finite optimality certificate at depth one.

## Statement and trust boundaries

Let h>=1, m=2^h, n=(386h+2)m, and let H and A_h be exactly the pattern and
ordered binary host of the pinned source. Define B_h from A_h by changing
all entries in R_* × C_h^+ from 1 to 0, with every other entry unchanged.
Here C_h^+=C_h^- is the single shared leaf column class; it is not counted twice.

**Written upper-bound theorem:** B_h is H-free and differs from A_h on
exactly m² entries. All anchor-incident entries remain fixed.

**Corollary inheriting the source's lower-bound proposition:**
The unrestricted minimum edit distance is exactly m², and
normalized distance is exactly 1/(386h+2)². This equality uses the source's
separate all-edits lower bound in 04-distance.tex, not merely the finite SAT
certificate below. No new proof-assistant verification of that lower bound
is asserted. The written upper-bound argument is independent of the source's
general removal theorem and uses only its explicit construction and elementary
counting. It does not claim a new removal counterexample.

**Independently certified finite conclusion:** for h=1 the minimum among
fixed-anchor repairs is four, regardless of the source's all-edits lower bound.
The direct model has 64 editable entries, 48 body-avoidance clauses, and an
exact cardinality circuit. A 25-step RUP refutation excludes budget three;
a four-edit witness provides the upper bound.

## Why rigidity survives the proposed edit

Only the dummy-row × leaf-column entries change. All variable rows, all
anchor-incident entries and every dummy column are unchanged. The dummy
rows remain identical to one another, although they are no longer all ones.

For any five non-anchor columns, a dummy column, if selected, is constant one
on every non-anchor row and prevents shattering. Otherwise they are all
variable columns. Partition them into the source's level/sign classes,
counting the shared leaf class once. Variable rows are unchanged. In each
class their ones are suffixes in node order, and each variable row is
nonzero in at most three classes. If a class contains a selected columns,
there are at most a nonempty suffixes. Thus there are at most five suffix
generators altogether. Each variable-row trace is a union of at most three
of them, so there are at most

    C(5,0)+C(5,1)+C(5,2)+C(5,3) = 26

such traces. This is an upper bound even if several different generator
choices yield the same trace. The identical edited dummy rows contribute
at most one further trace. Therefore there are at most 27<32 words.
Crucially, this argument needs dummy rows to be identical, not to be all ones.
It proves the source's no-five-column-shattering premise for B_h.

The rest of anchor rigidity uses only unchanged facts: distinct anchor
rows/columns and anchor-group twins; sparse variable-to-anchor incidence;
zero cross-mode incidences; dense initial32×32 restrictions of S; and the
unit or zero signatures of dummy positions against anchors. Dummy rows are
still twins, so at most one can occur in an S-copy. Consequently the source's
argument in 03-pinning.tex applies verbatim after replacing its trace lemma
by the preceding argument: every ordered S-copy uses one representative of
each anchor group of one mode, in order. All H-copy body roles are then
forced by the unchanged signatures.

For the finite h=1 model there is a simpler **arbitrary-edit** bridge that
avoids any assumption that edited dummy rows remain twins. A 64-row S-copy
selects at most eight non-anchor rows, so its first 32 rows are anchors.
At most one representative of any anchor group can occur, since those
anchor positions remain global twins under every permitted edit. Against
such selected anchors, each variable column has at most four ones; a dummy
column has at most two, from the two V modes at h=1. Each S-column has at
least31 ones among its first 32 rows, so no selected column can be non-anchor.
All 64 selected columns are anchors. Any two share a one among the first 32
selected rows, hence are in one common mode t. A row in another anchor mode
is then all zero; a non-anchor row has at most one one against these distinct
anchor groups of t. Both contradict the at least 58 ones in every S-row.
Thus every selected row also lies in mode t. Exactly one position from every
anchor group is used, and order fixes the group labels. The unchanged unit
signatures then force the body roles. Conversely, each role-compatible P
body completes with that mode's anchors to an H-copy. Hence avoidance of
all 48 bodies is equivalent to H-freeness for **every** permitted h=1 repair.

The arbitrary-edit bridge is not asserted for larger depths. The all-depth
upper bound uses only the specified repair, whose dummy rows do remain twins.

## Eliminating every possible body

By preserved rigidity, any H-copy must have a body P=[[1,0],[1,1]] in one
of the source's prescribed modes.

- V_i^+ and V_i^- use dummy columns. These columns and all their variable
  entries are unchanged. The source's parent-order contradictions continue
  to exclude P in every such mode.
- W_{i,d}^+ and W_{i,d}^- with i<h use only non-leaf columns. Their bodies
  are unchanged, and the same parent/parity contradictions exclude P.
- W_{h,d}^+ has its bottom-right entry in R_* × C_h^+, now zero. P requires
  it to be one.
- W_{h,d}^- has its bottom-left entry in the same edited block, now zero.
  Again P requires it to be one.

Thus no mode contains a body and B_h is H-free. There are m dummy rows and
m shared leaf columns, all their original entries are one, and they are
all distinct cells. The edit count is m².

## Finite model and lower-bound certificate

The 8×8 model uses the exact recursive row and column orders at h=1.
For each of the six modes, enumerate every ordered role-compatible
quadruple (r1<r2,c1<c2). The 48 resulting constraints exclude the body P:

    not x11 OR x12 OR not x21 OR not x22.

Every original Boolean cell is a variable. An edit literal is x for an
original zero and not x for an original one. The cardinality circuit uses
s[i,j] meaning at least j edit literals among the first i. Its recurrence is

    s[i,j] <-> s[i-1,j] OR (s[i-1,j-1] AND edit_i),

with s[i,0]=true and s[i,j]=false for j>i. Each gate z<->a OR(b AND c)
has clauses (not a OR z), (not b OR not c OR z),
(not z OR a OR b), (not z OR a OR c). All four implications are retained.
Force not s[64,4]. Induction gives an extension exactly when at most three
bits differ. The resulting CNF has 314 variables and 981 clauses.

The certificate contains only RUP additions and ends with the empty clause.
For each addition C, the checker assumes the negation of every literal of C
and runs unit propagation from scratch. A contradiction certifies that the
current formula entails C. Sequential soundness then proves unsatisfiability.
The optional solver is not used during verification, and ignored solver
proof deletions only leave extra already-proved clauses available.

The four-edit witness is checked against all 48 body constraints. Deleting
only the two leaf-diagonal cells instead produces eight new bodies at h=1,
illustrating the source's hitting-set warning. Certificate truncation,
a satisfiable constraint weakening and damaged witness controls must reject.
