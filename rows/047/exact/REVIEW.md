# Scoped AI review

**Reviewer.** A separate Claude agent (Claude Code `code-reviewer`, Opus 5.5)
ran on 2026-10-21 at about 23:12 UTC. It had read-only access to the packet
and its sources, and could run code. This is an AI review, not human peer
review.

**Scope.**
- whether the derivation in PROOF.md is sound;
- whether `check.py` matches the manuscript formulas;
- whether any check could pass vacuously, and how good the tests are;
- whether README and visit.json claim more than the packet supports;
- whether the independent implementation is really independent.

## Verdict

The reviewer found nothing blocking and no mathematical gap.
- **What it confirmed:** the steps of PROOF.md, (a) through (e); that every
  formula in `build()` matches `02-construction.tex`; and that both
  implementations reproduce the same q.
- **Uniqueness of q:** the divisor H + p³w is linear in w, with leading
  coefficient p³, which is a non-zero-divisor. So q is unique, and the
  matching hashes therefore show the two implementations computed the same
  polynomial.
- **Claims it re-checked:** every count, line range and statement about
  row 047 in README.

## Findings and dispositions

| Severity | Finding | Disposition |
| --- | --- | --- |
| should-fix | PROOF.md called con:h-expansion and con:e-polynomial "unused", although the chain uses their *definitions* of Q, h and e₀. `check.py` labelled the line-203 identity con:e-polynomial. | Fixed. PROOF.md now separates the definitions the chain uses from the identities that are verified but unused. The check is relabelled with its line, 203. |
| should-fix | README and `check.py` claimed "every identity", but `check.py` skipped H mod p and the Laurent identities of con:domain. The con:localized-coordinates check holds by construction. | Fixed. Added an H mod p check. The scope is narrowed to prop:stabilization, con:identity and H mod p. The Laurent identities are recorded as checked only by the independent implementation. The by-construction check is labelled as such. |
| should-fix | "Written from the two manuscript files alone" was inaccurate. The independent agent also received a task specification. | Fixed in README and in the independent implementation's docstring. Its author agent made the docstring change. |
| should-fix | README cited LOG.md and verification.json before they existed. | Fixed. Both files now exist. |
| should-fix | The hash pin for q was not enforced, and `reproduce.sh` never ran the independent implementation. | Fixed. `check.py` check 18 compares q's hash with the independent value. `INDEPENDENT=1 bash reproduce.sh` reruns the SymPy implementation, compares its output and hash, and runs its controls. |
| nit | `exact_quotient_in_w` looped forever when the divisor had w-degree 2 or more. | Fixed. It now requires a divisor linear in w and has a test. |
| nit | `Poly.lift(None)` became the zero polynomial. | Fixed. Any value that is not an int or a Poly raises `TypeError`, with a test. |
| nit | `reproduce.sh` accepted any exit status of 1, including a crash. | Fixed. It now also requires `RESULT: fails`. |
| nit | The `linear-inverse` control mutated M, which nothing downstream uses. | Fixed. It is renamed `linear-coordinates`, and a new `linear-inverse` mutates F(L,M), breaking six checks. The independent implementation was changed the same way by its author agent. |
| nit | The determinant hardcoded L's coefficients. | Fixed. It is now read from `L_of_FJ` and `M_of_FJ`. |
| nit | The independent implementation's `holds` did not require the expected number of results. | Fixed by its author agent (`EXPECTED_RESULTS = 25`). |
| nit | visit.json cited 19-245. | Fixed: 19-256. |
| nit | PROOF.md cited `preamble.tex`, which was not in `source/`. | Fixed. The file is copied and hashed. |
| nit | Tests did not pin which checks each control breaks. | Fixed. A test pins the expected failing checks for every control. |
