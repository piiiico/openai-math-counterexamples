#!/usr/bin/env python3
"""Pico's check of the Towell/Codex GCD packet (PR #21), run from rows/059/gcd/.

1. The packet's vendored relation hashes to the same SHA-256 as the file row 059 already checked.
2. E printed by the packet equals sum(e_b) computed here directly.
3. A mutation outside the packet's five controls: swap the coefficients of two seeded rows.
   This keeps E, sum|e_b| and the support, so only the product identities can catch it.
   The packet's verify_relation must reject it, and so must Pico's sieve route
   (rows/059/check.py's valuation sums, re-implemented inline below, not imported).
"""
import hashlib, json, random, sys
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here))
import check  # the packet's checker

raw = (here / "source/explicit-relation.json").read_bytes()
sha = hashlib.sha256(raw).hexdigest()
assert sha == "e5a3ad0b8901ac358374575dbaf7be9e03bb84063def63749f16618cf2ba1780", sha
print("relation sha256 matches row 059:", sha[:16])
good = json.loads(raw)
rel = [(int(r["b"]), int(r["e"])) for r in good["relation"]]
d = int(good["d"])

res = check.verify_relation(good)
assert res.sum_e == sum(e for _, e in rel) and len(res.reduction.residual) == 0
print("packet accepts; E agrees with direct sum; residual bases 0")

N = 3 * d + 1
spf = list(range(N))
for p in range(2, int(N ** 0.5) + 1):
    if spf[p] == p:
        for k in range(p * p, N, p):
            if spf[k] == k:
                spf[k] = p

def add(v, n, e):
    while n > 1:
        p = spf[n]; n //= p
        v[p] = v.get(p, 0) + e

def sieve_nonzero(rel):
    va, vr = {}, {}
    for b, e in rel:
        add(va, d - b, e); add(va, b, -e)
        add(vr, 2 * d + b, e); add(vr, 2 * d - b, e); add(vr, 3 * d - b, -e); add(vr, d + b, -e)
    return sum(1 for x in va.values() if x), sum(1 for x in vr.values() if x)

assert sieve_nonzero(rel) == (0, 0)
random.seed(59)
i, j = random.sample(range(len(rel)), 2)
bad = json.loads(raw)
bad["relation"][i]["e"], bad["relation"][j]["e"] = good["relation"][j]["e"], good["relation"][i]["e"]
swapped = [(int(r["b"]), int(r["e"])) for r in bad["relation"]]
try:
    check.verify_relation(bad)
    sys.exit("FAIL: packet accepted the swapped relation")
except check.InvalidCertificate as err:
    print(f"swap rows {i},{j}: packet rejects ({err})")
nz = sieve_nonzero(swapped)
assert nz != (0, 0)
print(f"swap rows {i},{j}: Pico sieve rejects (nonzero valuations {list(nz)})")
print("RESULT: packet agrees with Pico's sieve on the real relation and on an E-preserving swap")
