"""Exact integer/rational verification of the finite tensor construction.

The two matrix constructions below use respectively Kraus matrices and the
matrix-unit definition of the pencil map. No floating-point arithmetic is used.
"""

from collections import defaultdict
from itertools import combinations, combinations_with_replacement, permutations
import hashlib
import json

from flint import fmpq_mat, fmpz_mat


class TensorCertificateError(ValueError):
    """An exact finite proof obligation failed."""


def require(condition, message):
    """Keep verification active even when Python assertions are disabled."""
    if not condition:
        raise TensorCertificateError(message)


def matrix_rows(matrix):
    """Serialize an integer matrix without rounding or fixed-width conversion."""
    return [[int(matrix[i, j]) for j in range(matrix.ncols())]
            for i in range(matrix.nrows())]


def digest(value):
    """Hash canonical structured evidence, independent of presentation spacing."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def sign(permutation):
    """Sign from inversions, also used for exterior complements."""
    return (-1) ** sum(permutation[i] > permutation[j]
                      for i in range(len(permutation)) for j in range(i + 1, len(permutation)))


def complementary_pairs(pairs):
    """Exterior Hodge signed permutation in the real coordinate basis."""
    result = fmpz_mat(len(pairs), len(pairs))
    for column, pair in enumerate(pairs):
        other = tuple(i for i in range(4) if i not in pair)
        result[pairs.index(other), column] = sign(pair + other)
    return result


def exponent(indices):
    return tuple(indices.count(i) for i in range(4))


def homogeneous_minors(matrices, monomials):
    """Division-free determinant expansion over Python integer polynomials.

    This adapts the permutation-expansion method of our earlier geometry
    checker to homogeneous degree four; it does not import that checker.
    """
    linear = [exponent((i,)) for i in range(4)]
    answer = []
    for rows in combinations(range(6), 4):
        result = defaultdict(int)
        for permutation in permutations(range(4)):
            product = {(0, 0, 0, 0): sign(permutation)}
            for i, column in enumerate(permutation):
                expanded = defaultdict(int)
                for left, coefficient in product.items():
                    for variable, right in enumerate(linear):
                        scalar = matrices[variable][rows[i]][column]
                        if scalar:
                            expanded[tuple(a + b for a, b in zip(left, right))] += coefficient * scalar
                product = expanded
            for monomial, coefficient in product.items():
                result[monomial] += coefficient
        answer.append([result[m] for m in monomials])
    return fmpz_mat(answer)


def kraus_construction(matrices, symmetric, exterior):
    """Build V0^T (Q_r tensor Q_s) U0 and the resulting Choi Gram matrix."""
    q = [fmpz_mat([[matrices[i][r][a] for i in range(4)] for a in range(4)])
         for r in range(6)]
    kraus = []
    for left in q:
        for right in q:
            h = fmpz_mat(6, 10)
            for out, (a, b) in enumerate(exterior):
                for inp, (c, d) in enumerate(symmetric):
                    h[out, inp] = left[a, c] * right[b, d] - left[b, c] * right[a, d]
                    if c != d:
                        h[out, inp] += left[a, d] * right[b, c] - left[b, d] * right[a, c]
            kraus.append(h)
    vectors = fmpz_mat([[h[a, i] for h in kraus] for i in range(10) for a in range(6)])
    return kraus, vectors * vectors.transpose()


def matrix_unit_construction(blocks, symmetric, exterior):
    """Compute S0 on every matrix unit directly from L(E_ij)=M_i^T M_j."""
    result = fmpz_mat(60, 60)
    for i, (c, d) in enumerate(symmetric):
        left_terms = [(c, d)] if c == d else [(c, d), (d, c)]
        for j, (e, f) in enumerate(symmetric):
            right_terms = [(e, f)] if e == f else [(e, f), (f, e)]
            for a, (u, v) in enumerate(exterior):
                for b, (w, x) in enumerate(exterior):
                    entry = 0
                    for p, q in left_terms:
                        for r, s in right_terms:
                            first, second = blocks[p][r], blocks[q][s]
                            entry += (first[u, w] * second[v, x] - first[u, x] * second[v, w]
                                      - first[v, w] * second[u, x] + first[v, x] * second[u, w])
                    result[6 * i + a, 6 * j + b] = entry
    return result


def transpose_fixed(choi, input_dim, output_dim, *, output):
    """Check every entry of one specified Choi partial transpose."""
    for i in range(input_dim):
        for j in range(input_dim):
            for a in range(output_dim):
                for b in range(output_dim):
                    row, col = ((i * output_dim + b, j * output_dim + a) if output
                                else (j * output_dim + a, i * output_dim + b))
                    if choi[i * output_dim + a, j * output_dim + b] != choi[row, col]:
                        return False
    return True


def verify(matrices, *, complement=None):
    """Return a report and exact evidence, or raise on any failed obligation.

    The optional complement allows a different orthogonal exterior operation
    to be audited; positive maps alone do not guarantee the kernel identities.
    """
    require(len(matrices) == 4 and all(len(m) == 6 for m in matrices)
            and all(len(row) == 4 for m in matrices for row in m)
            and all(type(x) is int for m in matrices for row in m for x in row),
            "expected four exact integer 6 by 4 matrices")
    m = [fmpz_mat(a) for a in matrices]
    blocks = [[a.transpose() * b for b in m] for a in m]
    require(all(blocks[i][j] == blocks[j][i] for i in range(4) for j in range(4)),
            "pencil block symmetry failed")
    symmetric = list(combinations_with_replacement(range(4), 2))
    exterior = list(combinations(range(4), 2))
    k = complementary_pairs(exterior) if complement is None else fmpz_mat(complement)
    require(k.nrows() == k.ncols() == 6 and k.transpose() * k == fmpz_mat(
        [[int(i == j) for j in range(6)] for i in range(6)]), "complement must be orthogonal")
    kraus, s_choi = kraus_construction(matrices, symmetric, exterior)
    require(s_choi == matrix_unit_construction(blocks, symmetric, exterior),
            "Kraus and matrix-unit constructions disagree")
    require(transpose_fixed(s_choi, 10, 6, output=True), "S output transpose identity failed")
    require(transpose_fixed(s_choi, 10, 6, output=False), "S input transpose identity failed")

    # Superoperator coordinates are output row/column followed by input row/column.
    s = fmpz_mat([[s_choi[6 * i + a, 6 * j + b] for i in range(10) for j in range(10)]
                 for a in range(6) for b in range(6)])
    r = fmpz_mat(36, 100)
    for col in range(100):
        block = fmpz_mat(6, 6, [s[row, col] for row in range(36)])
        transformed = k * block.transpose() * k.transpose()
        for a in range(6):
            for b in range(6):
                r[6 * a + b, col] = transformed[a, b]
    s_input_transpose = fmpz_mat([[s[row, 10 * j + i] for i in range(10) for j in range(10)]
                                 for row in range(36)])
    composite = r.transpose() * s_input_transpose
    z = fmpz_mat([[composite[10 * a + b, 10 * i + j] for j in range(10) for b in range(10)]
                 for i in range(10) for a in range(10)])

    # Independently compose Kraus operators. The verified transpose identities
    # justify S0 o T = S0 and R0 = Ad_K o S0 for this specific pencil.
    composed = [left.transpose() * k.transpose() * right for left in kraus for right in kraus]
    vectors = fmpz_mat([[b[a, i] for b in composed] for i in range(10) for a in range(10)])
    require(z == vectors * vectors.transpose(), "composite Choi Gram identity failed")
    require(transpose_fixed(z, 10, 10, output=True), "composite PPT identity failed")
    require(z[0, 0] > 0, "nonzero composite witness failed")

    # Every coordinate of Z(v(x) tensor v(x)) is a homogeneous quartic.
    monomials = [exponent(t) for t in combinations_with_replacement(range(4), 4)]
    positions = {m: i for i, m in enumerate(monomials)}
    evaluation = fmpz_mat(100, 35)
    for i, left in enumerate(symmetric):
        for j, right in enumerate(symmetric):
            evaluation[10 * i + j, positions[exponent(left + right)]] = 1
    kernel_coefficients = z * evaluation
    minors = homogeneous_minors(matrices, monomials)
    high = [i for i, monomial in enumerate(monomials) if monomial[0] == 0]
    high_minors = fmpq_mat([[minors[i, j] for j in high] for i in range(15)])
    require(high_minors.det() != 0, "kernel certificate has singular leading-minor matrix")
    coefficients = fmpq_mat([[kernel_coefficients[i, j] for j in high] for i in range(100)]) * high_minors.inv()
    require(coefficients * fmpq_mat(minors) == fmpq_mat(kernel_coefficients),
            "kernel polynomial identity failed")
    evidence = {
        "schema_version": 1,
        "pencil": matrices,
        "s_kraus": [matrix_rows(h) for h in kraus],
        "complement": matrix_rows(k),
        "choi": matrix_rows(z),
        "quartic_monomials": monomials,
        "maximal_minor_coefficients": matrix_rows(minors),
        "kernel_multipliers": [[[int(coefficients[i, j].numerator), int(coefficients[i, j].denominator)]
                                for j in range(15)] for i in range(100)],
    }
    return {
        "status": "certified", "scope": "finite_PPT_composition_and_polynomial_kernel_identities",
        "arithmetic": "exact integers and rationals", "s_kraus_count": len(kraus),
        "composite_kraus_count": len(composed), "choi_shape": [100, 100],
        "choi_rank": int(z.rank()), "choi_trace": int(sum(z[i, i] for i in range(100))),
        "nonzero_product_value": int(z[0, 0]), "kernel_polynomial_identities": 100,
        "maximal_minors": 15, "homogeneous_quartic_monomials": 35,
        "choi_sha256": digest(evidence["choi"]), "evidence_sha256": digest(evidence),
        "geometry_prerequisite": "twenty singular directions; every ten quadratic evaluation rows independent",
        "geometry_replayed_by_this_function": False,
        "secret_key_claim_checked": False, "evidence": evidence,
    }


def verify_saved(matrices, certificate):
    """Check a saved certificate against an independently supplied pencil."""
    require(isinstance(certificate, dict) and certificate.get("schema_version") == 1,
            "unsupported certificate schema")
    require(certificate.get("pencil") == matrices, "certificate and supplied pencil differ")
    report = verify(matrices)
    expected = report.pop("evidence")
    require(certificate == json.loads(json.dumps(expected)), "saved certificate differs from exact reconstruction")
    return report
