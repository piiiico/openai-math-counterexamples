# Agent entry point

You were asked to "contribute", "check something" or "use spare inference" here. Read this, then [CONTRIBUTING.md](CONTRIBUTING.md). Aim for one checkable result in one session of about an hour. A PR is not required: a useful negative result posted on an issue also finishes a session.

## What to pick

All 63 families in [`census.tsv`](census.tsv) have a status; none is open. So the work is one of these, in order of value:

1. **Second implementation of a holds row.** Every holds row in `rows.tsv` now has a second check (088 was the last, #34). New holds rows still need one; refresh against merged `rows.tsv` and open claims/PRs before choosing, since a pending submission is not an accepted second implementation. Write your own check from the manuscript, not from our script, and compare. Row 272 shows the pattern: geometry, then tensor, then channel, each checked twice.
2. **Audit a not-finite or not-explicit call.** If a paper does write down an object we said it does not, or has a finite step under an infinite claim (as row 361's counting check and row 199's algebra do), check that step.
3. **Try to write down a not-explicit object.** README, "Trying to write down a not-explicit object", lists what was tried for 192, 162 and 161.

Family 109 is not here: go to [CrocSwap/integer-mult-bounds](https://github.com/CrocSwap/integer-mult-bounds).

## How not to duplicate

1. Fetch main first: `git fetch https://github.com/piiiico/openai-math-counterexamples.git main` and read `rows.tsv` at that commit.
2. Search open issues and PRs for the family number.
3. Claim the family in an issue with the [Check request](.github/ISSUE_TEMPLATE/check-request.md) template before substantial work. A claim with no update in 3 days lapses.

## What gets credited

A new holds, a negative control that catches something, an audit of one of our calls, or a check that does not go through: each is credited by name in `rows.tsv` and the README. Say whether a person, an agent or both did the work, and which AI system helped; that disclosure is kept.

## Rules

- Do not edit `rows/` directories other than the one you are checking, and never change another contributor's row; contest it with a second implementation instead.
- Pin the openai/math commit you read (full sha) and hash each source file.
- Distinguish a finite certificate, a scoped computation, a search failure and a theorem. They are different claims.
- Run `python3 build.py` after editing `rows.tsv`.

Questions go in an issue. The maintainers are Pico, an AI agent operated by Håkon Åmdal, and Alexander Richard Towell (`queelius`), scoped in [MAINTAINERS.md](MAINTAINERS.md).
