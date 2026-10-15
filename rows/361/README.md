# Row 361: independently checked finite spectral selection

Alexander Richard Towell, with substantial OpenAI Codex assistance.

The paper's full metric theorem remains a `not-finite` claim. The new
[spectral packet](spectral/README.md) checks only its explicit finite
selection at dimension 16 and cutoff 50000, using a different integer-only
sufficient criterion. The strict surplus remains positive without computing
square roots or choosing a precision parameter.

Run `python rows/361/check.py` from the repository root. Expected:
`RESULT: holds (finite spectral selection only; metric theorem unchecked)`.
The packet includes the certificate, two independent replay methods, tests,
source pins, attribution and a separate AI review; no human or kernel review
is claimed.
