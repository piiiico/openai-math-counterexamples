"""Reviewer calculation; only path resolution adapted by the coordinating agent.

This prints evidence. reproduce.py checks the exact expected output.
"""
import sympy as s
import hashlib, json
from pathlib import Path

p = Path(__file__).resolve().parents[1]
for entry in json.loads((p / "sources.json").read_text())["files"]:
    b = (p / entry["local"]).read_bytes()
    print(entry["local"], len(b) == entry["bytes"],
          hashlib.sha256(b).hexdigest() == entry["sha256"])

t = s.symbols("t")
h = (1 + t*t) / 2
u = (1 - t*t) / (1 + t*t)
v = 2*t / (1 + t*t)
base = [(1, 0), (-s.Rational(1, 2), s.sqrt(3)/2),
        (-s.Rational(1, 2), -s.sqrt(3)/2)]
points = []
for sign, weight in [(1, 1), (-1, 1), (0, -2)]:
    for x, y in base:
        points.append((s.Matrix([1, u*x-sign*v*y, sign*v*x+u*y])
                       if sign else s.Matrix([1, x, y]), weight))

D = lambda x: h*s.diff(x, t)
lhs = 0
rhs = 0
for i in range(3):
    for j in range(3):
        a = (t**(i+1) + s.sqrt(3)) / (1+t*t)
        b = (t**(j+2) - s.sqrt(3)) / (2+t*t)
        lhs += sum(w*D(p[i]*a)*D(p[j]*b) for p, w in points)
        if i == j and i > 0:
            rhs += 3*a*b

print("actual arbitrary-entry product derivative residual:", s.cancel(lhs-rhs, extension=s.sqrt(3)))
print("pairwise squared distances nonzero as rational functions:", all(
    s.cancel(sum((points[i][0][k]-points[j][0][k])**2 for k in [1, 2]),
             extension=s.sqrt(3)) != 0
    for i in range(9) for j in range(i)))
