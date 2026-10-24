#!/usr/bin/env python3
"""Family 172: exact rotated-base moments and all product-rule jet coefficients.

Alexander Richard Towell, with substantial OpenAI Codex assistance.
Source: pinned 07-consequences.tex, cons:derivation-moments/obstruction.
This checks algebra over Q(sqrt(3))(t), not the Ramsey classification theorem.
"""
import argparse
import json

import sympy as sp

T = sp.Symbol("t")
ROOT = sp.sqrt(3)


def normal(value):
    """Exact rational-function normalization, with an algebraic coefficient field."""
    return sp.cancel(value, extension=ROOT)


def require_zero(value):
    reduced = normal(value)
    if reduced != 0:
        raise ValueError(f"nonzero rational-function residual: {reduced}")


def base_square():
    return [(sp.Integer(x), sp.Integer(y)) for x, y in [(1, 0), (0, 1), (-1, 0), (0, -1)]]


def base_triangle():
    return [(sp.Integer(1), sp.Integer(0)),
            (-sp.Rational(1, 2), ROOT / 2), (-sp.Rational(1, 2), -ROOT / 2)]


def configuration(base, fault=None):
    denominator = 1 + T*T
    u, v = (1 - T*T)/denominator, 2*T/denominator
    plus = sp.Matrix([[u, -v], [v, u]])
    minus = sp.Matrix([[u, v], [-v, u]])
    rotations = [plus, plus if fault == "same_rotation" else minus, sp.eye(2)]
    group_weights = [1, 1, -1 if fault == "central_weight" else -2]
    factor = 1 if fault == "plain_derivative" else denominator / 2
    points, velocities, weights = [], [], []
    for rotation, weight in zip(rotations, group_weights, strict=True):
        for point in base:
            spatial = rotation * sp.Matrix(point)
            augmented = sp.Matrix([1, *spatial])
            points.append(augmented)
            velocities.append(augmented.applyfunc(lambda x: normal(factor * sp.diff(x, T))))
            weights.append(weight)
    return points, velocities, weights


def certificate(base, fault=None):
    vectors = [sp.Matrix(p) for p in base]
    centroid = sum(vectors, sp.zeros(2, 1))
    covariance = sum((v * v.T for v in vectors), sp.zeros(2))
    for entry in centroid:
        require_zero(entry)
    c = normal(covariance[0, 0])
    if c == 0:
        raise ValueError("zero second moment cannot give an obstruction")
    for entry in covariance - c * sp.eye(2):
        require_zero(entry)
    for vector in vectors:
        require_zero((vector.T * vector)[0] - 1)

    points, derivatives, weights = configuration(base, fault)
    target = sp.diag(0, 2*c, 2*c)
    moments = []
    for left, right in [(points, points), (derivatives, points), (derivatives, derivatives)]:
        moments.append(sum((w * a * b.T for w, a, b in zip(weights, left, right, strict=True)),
                           sp.zeros(3)).applyfunc(normal))
    for matrix, expected in zip(moments, [sp.zeros(3), sp.zeros(3), target], strict=True):
        for entry in matrix - expected:
            require_zero(entry)

    # Directly expand arbitrary coefficient values and their first derivatives.
    # Coefficients of a*b, a*db, da*b, da*db cover all product-rule terms.
    a, da, b, db = sp.symbols("a da b db")
    count = 0
    for alpha in range(3):
        for beta in range(3):
            expression = sum(w * (dp[alpha]*a + p[alpha]*da)
                             * (dp[beta]*b + p[beta]*db)
                             for w, p, dp in zip(weights, points, derivatives, strict=True))
            expression -= target[alpha, beta]*a*b
            polynomial = sp.Poly(sp.expand(expression), a, da, b, db)
            for monomial in (a*b, a*db, da*b, da*db):
                require_zero(polynomial.coeff_monomial(monomial))
                count += 1
    return {"points": len(points), "base_size": len(base),
            "base_second_moment": str(c), "spatial_coefficient": int(2*c),
            "moment_entries_checked": 27, "jet_coefficients_checked": count,
            "multiplied_identity_block_contradiction": str(4*c)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--negative-control", choices=["central_weight", "same_rotation", "plain_derivative"])
    args = parser.parse_args()
    try:
        if args.negative_control:
            result = certificate(base_triangle(), fault=args.negative_control)
            print(json.dumps(result, sort_keys=True))
            print("RESULT: accepted (a negative-control harness must flag this as failure)")
            return 0
        result = {"field": "Q(sqrt(3))(t)", "method": "exact symbolic rational-function identities",
                  "square": certificate(base_square()), "triangle": certificate(base_triangle()),
                  "scope": "moment and tensor product-rule identities; Ramsey classification inherited"}
        print(json.dumps(result, indent=2, sort_keys=True))
        print("RESULT: square and triangular-base moments and all 72 jet coefficients verified")
        return 0
    except ValueError as error:
        print(f"RESULT: rejected: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
