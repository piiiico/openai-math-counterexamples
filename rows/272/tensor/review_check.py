"""Independent review replay: explicit tensors and SymPy determinants.

Written by the separately tasked OpenAI Codex reviewer; only the certificate
path and an optimized-mode guard were added for portable reproduction.
This imports no code from the primary tensor checker.
"""
import json
from itertools import combinations, combinations_with_replacement
from pathlib import Path

import sympy as sp
from flint import fmpz_mat

if not __debug__:
    raise SystemExit("Run this review script without -O: its checks use assertions.")

c = json.loads(Path(__file__).with_name("certificate.json").read_text())
M = c["pencil"]
sy = list(combinations_with_replacement(range(4), 2))
ex = list(combinations(range(4), 2))
U = fmpz_mat(16, 10)
V = fmpz_mat(16, 6)
for j, (a, b) in enumerate(sy):
    U[4*a+b, j] = U[4*b+a, j] = 1
for j, (a, b) in enumerate(ex):
    V[4*a+b, j], V[4*b+a, j] = 1, -1
Q = [fmpz_mat([[M[i][r][a] for i in range(4)] for a in range(4)]) for r in range(6)]

def kron(A, B):
    return fmpz_mat([
        [A[i//B.nrows(), j//B.ncols()] * B[i%B.nrows(), j%B.ncols()]
         for j in range(A.ncols()*B.ncols())]
        for i in range(A.nrows()*B.nrows())
    ])

H = [V.transpose()*kron(A, B)*U for A in Q for B in Q]
assert H == [fmpz_mat(h) for h in c["s_kraus"]]
K = fmpz_mat(c["complement"])
E = fmpz_mat(10, 6)
for i in range(6):
    E[i, i] = 1
A = [E*h for h in H]
B = [h.transpose()*K.transpose()*E.transpose() for h in H]

def choi(kraus):
    F = fmpz_mat([
        [k[a, i] for k in kraus]
        for i in range(kraus[0].ncols())
        for a in range(kraus[0].nrows())
    ])
    return F*F.transpose()

def output_pt(J, n):
    return fmpz_mat([
        [J[i*n+b, j*n+a] for j in range(n) for b in range(n)]
        for i in range(n) for a in range(n)
    ])

for label, kraus in [("Phi1", A), ("Phi2", B)]:
    J = choi(kraus)
    assert J == output_pt(J, 10)
    print(label, "explicit 10x10 Kraus count", len(kraus),
          "Choi rank", J.rank(), "output-transpose fixed")

Z = choi([b*a for b in B for a in A])
assert Z == fmpz_mat(c["choi"])
print("Independent explicit U0,V0,E Kraus construction matches all 36 H and full Z0")
P = fmpz_mat(10, 10)
P[0, 0] = 1
SP = sum((h*P*h.transpose() for h in H), fmpz_mat(6, 6))
assert SP == fmpz_mat([[2592*int(i == j) for j in range(6)] for i in range(6)])
assert Z[0, 0] == 6*2592**2 == 4*6*36**4
print("S0(Pe00)=2*36^2 I6; positive test=4*6*36^4")
print("U0*U0 diagonal:", [int((U.transpose()*U)[i, i]) for i in range(10)])
print("V0*V0 diagonal:", [int((V.transpose()*V)[i, i]) for i in range(6)])

x = sp.symbols("x0:4")
Mx = sum((x[i]*sp.Matrix(M[i]) for i in range(4)), sp.zeros(6, 4))
minors = [
    sp.Poly(Mx.extract(rows, range(4)).det(method="domain-ge"), *x)
    for rows in combinations(range(6), 4)
]
for actual, coefficients in zip(minors, c["maximal_minor_coefficients"]):
    expected = sp.Poly.from_dict({
        tuple(exponents): value
        for exponents, value in zip(c["quartic_monomials"], coefficients) if value
    }, x)
    assert actual == expected
v = sp.Matrix([x[i]*x[j] for i, j in sy])
C = sp.Matrix([[sp.Rational(*q) for q in row] for row in c["kernel_multipliers"]])
lhs = sp.Matrix(c["choi"])*sp.kronecker_product(v, v)
rhs = C*sp.Matrix([p.as_expr() for p in minors])
assert all(sp.Poly(l-r, *x).is_zero for l, r in zip(lhs, rhs))
print("Independent SymPy determinant engine matches all 15 homogeneous minors; "
      "all 100 saved rational polynomial identities hold")
