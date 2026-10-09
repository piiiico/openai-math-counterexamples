#!/usr/bin/env python3
"""Family 059: Lemma seed:product of 'Ambiently homeomorphic isolated hypersurfaces of
multiplicities two and three' (seeds.tex:7-19) for the explicit relation the authors ship
(verification/support/explicit-relation.json, certificate.tex:11-14).

  d = 3^11, B = {0<b<d/2, 3 does not divide b}, A_b = (d-b)/b, R_b = (2d+b)(2d-b)/((3d-b)(d+b)).
  Claim: E = sum e_b > 0 and prod A_b^e_b = prod R_b^e_b = 1.

Two routes, neither shared with the authors' validator (which factors by trial division):
  1. smallest-prime-factor sieve to 3d, signed valuation sums per prime, all must be 0;
  2. no factoring at all: the products reduced mod 40 seeded random 61-bit primes must be 1.
     (Route 2 alone is a consistency check, not a proof; route 1 is exact.)
Negative arms: e_b of one row +1, and one sign flipped; both routes must reject each.
Usage: python3 check.py <path to openai/math preprint dir>
"""
import hashlib, json, random, sys, time
from pathlib import Path

t0 = time.time()
DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
raw = (DIR / "verification/support/explicit-relation.json").read_bytes()
data = json.loads(raw)
print("relation file sha256", hashlib.sha256(raw).hexdigest())
d = int(data["d"]); assert d == 3 ** 11
rel = [(int(r["b"]), int(r["e"])) for r in data["relation"]]
assert len({b for b, _ in rel}) == len(rel)
assert all(0 < 2 * b < d and b % 3 and e != 0 for b, e in rel), "support outside B"

N = 3 * d + 1
spf = list(range(N))
for i in range(2, int(N ** 0.5) + 1):
    if spf[i] == i:
        for j in range(i * i, N, i):
            if spf[j] == j: spf[j] = i

def vals(n):
    out = {}
    while n > 1:
        p = spf[n]; out[p] = out.get(p, 0) + 1; n //= p
    return out

def frac_groups(b):
    return ([(d - b, 1), (b, -1)], [(2*d + b, 1), (2*d - b, 1), (3*d - b, -1), (d + b, -1)])

def route1(rel):
    tot = [{}, {}]
    for b, e in rel:
        for g, parts in enumerate(frac_groups(b)):
            for n, s in parts:
                for p, k in vals(n).items():
                    tot[g][p] = tot[g].get(p, 0) + s * k * e
    return [sum(1 for v in t.values() if v) for t in tot]  # count of nonzero prime valuations

def is_prime(n):
    if n < 2: return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0: return n == p
    dd, s = n - 1, 0
    while dd % 2 == 0: dd //= 2; s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, dd, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True

rng = random.Random(59)
primes = []
while len(primes) < 40:
    q = rng.getrandbits(61) | (1 << 60) | 1
    if is_prime(q): primes.append(q)

def route2(rel):
    bad = 0
    for q in primes:
        pa = pr = 1
        for b, e in rel:
            for g, parts in enumerate(frac_groups(b)):
                num = den = 1
                for n, s in parts:
                    if s > 0: num = num * n % q
                    else: den = den * n % q
                x = pow(num * pow(den, -1, q) % q, e % (q - 1), q)
                if g == 0: pa = pa * x % q
                else: pr = pr * x % q
        bad += (pa != 1) + (pr != 1)
    return bad

E = sum(e for _, e in rel)
print("support size", len(rel), "(certificate.tex:12 says 849)")
print("max |e_b| digits", max(len(str(abs(e))) for _, e in rel), "(certificate.tex:13 says at most 140)")
print("E > 0:", E > 0)
r1, r2 = route1(rel), route2(rel)
print("route 1 (sieve valuations): nonzero prime valuations in prod A, prod R =", r1)
print("route 2 (mod 40 random 61-bit primes): residues != 1 =", r2)
ok = len(rel) == 849 and max(len(str(abs(e))) for _, e in rel) <= 140 and E > 0 and r1 == [0, 0] and r2 == 0

neg1 = [(b, e + (1 if i == 0 else 0)) for i, (b, e) in enumerate(rel)]
neg2 = [(b, -e if i == 100 else e) for i, (b, e) in enumerate(rel)]
for name, nr in (("e_b of first row +1", neg1), ("sign of row 100 flipped", neg2)):
    a1, a2 = route1(nr), route2(nr)
    fired = a1 != [0, 0] and a2 > 0
    print(f"negative arm '{name}': route 1 {a1}, route 2 {a2} -> {'rejected' if fired else 'NOT REJECTED'}")
    ok = ok and fired
print("RESULT:", "holds" if ok else "FAILS")
print(f"runtime {time.time()-t0:.1f}s", file=sys.stderr)
