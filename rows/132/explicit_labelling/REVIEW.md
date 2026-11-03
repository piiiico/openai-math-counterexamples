# Review record (AI review, not human review)

**Reviewer.** A separate Anthropic Claude agent (Claude Code, Opus 5.5),
started 2026-11-02 at about 08:22Z. It had read-only access to this directory.
Its brief listed four items to check. It was told to read the `.tex` files
itself rather than trust `PROOF.md`. It had not seen this session's reasoning
beyond the packet files. **This is not a human review**, and the reviewer
shares a model with the author.

## Verdicts

1. **Uses of `t`, the labelling and `r`: confirmed.**
   - `t` appears only at its definition (`01:12`), in the lemma and its
     random proof (`01:29-46`), in the `|T| < t` step (`02:70-77`), and in
     `epsilon` and the `2 sqrt M` bound (`03:27`, `03:56`).
   - The labelling is otherwise used only in the clause definition (`01:82`)
     and in sentences saying a labelling is fixed or supplied.
   - `r >= sqrt M` is used only at `01:45`. Otherwise `r` needs to be at
     least 1 (so blocks are nonempty) and at most `2 sqrt M`.
   - `00-introduction.tex` mentions random labels only in prose (`00:74`).
2. **Lemma A: confirmed.** The reviewer checked the definition of a bad set
   against the manuscript, the base case, empty or singleton parts, the
   head-of-an-edge step, the use of the tournament property (outdegrees are
   not used), and the tightness example. It could not break the proof.
3. **Parameter inequalities: confirmed.** These are `h = bit_length(2M^2)`,
   `h <= 2 + 2 log2 M`, the monotonicity arguments, the thresholds 290 and 57
   (from a separate scan), and the claim that `03:63-102` uses only
   `epsilon <= 2/3^(d+1)`. The theorem chooses `M` itself (`03:106`), so
   requiring `M >= 290` when `d = 1` is legitimate.
4. **Problems found.**
   - **Every `03-separation.tex` line number in `PROOF.md` was off by +149**,
     because the author numbered `02` and `03` as one listing.
   - Two wording gaps: the existence-only citations of the labelling, and
     the fact that option 2 changes the dimension.

## Response

- All `03-separation.tex` citations in `PROOF.md`, `README.md`, `LOG.md`
  and `check.py` were shifted by -149 and spot-checked against the file.
- `PROOF.md` now cites the existence-only sentences and notes what
  option 2 changes.
- No mathematical change was needed.
