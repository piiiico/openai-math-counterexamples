"""Independent matrix-unit review of the 21-dimensional channel completion.

This module intentionally imports no primary channel or tensor checker code.
It instantiates the source's generic construction for the certified integer-
coordinate pair. Entanglement of its square remains conditional on the earlier
tensor/geometry result; this is not a proof-assistant kernel verification.
"""

import argparse
from copy import deepcopy
from dataclasses import dataclass
import hashlib
from itertools import combinations
import json
from pathlib import Path
import time

from flint import fmpz_mat


class ReviewFailure(ValueError):
    """An independent review obligation failed."""


def require(condition, message):
    if not condition:
        raise ReviewFailure(message)


def identity(n):
    return fmpz_mat([[int(i == j) for j in range(n)] for i in range(n)])


def exact_matrix(rows):
    require(isinstance(rows, list) and rows and all(isinstance(row, list) for row in rows)
            and all(len(row) == len(rows[0]) for row in rows)
            and all(type(value) is int for row in rows for value in row),
            "expected an exact rectangular integer matrix")
    return fmpz_mat(rows)


@dataclass
class Model:
    m: int
    n: int
    denominator: int
    first: tuple
    second: tuple
    effects: tuple
    defects: tuple
    tensor_choi: fmpz_mat
    defect_gram_rows: tuple


def build_model(tensor):
    kraus = tuple(exact_matrix(rows) for rows in tensor["s_kraus"])
    require(bool(kraus), "missing tensor Kraus matrices")
    q, m = kraus[0].nrows(), kraus[0].ncols()
    require(q <= m and all(h.nrows() == q and h.ncols() == m for h in kraus),
            "inconsistent tensor Kraus dimensions")
    k = exact_matrix(tensor["complement"])
    require(k.nrows() == k.ncols() == q and k.transpose() * k == identity(q),
            "exterior complement is not orthogonal")
    inclusion = fmpz_mat(m, q)
    for i in range(q):
        inclusion[i, i] = 1
    first = tuple(inclusion * h for h in kraus)
    second = tuple(h.transpose() * k.transpose() * inclusion.transpose() for h in kraus)
    effects = tuple(sum((a.transpose() * a for a in family), fmpz_mat(m, m))
                    for family in (first, second))
    denominators = tuple(1 + int(sum(effect[i, i] for i in range(m))) for effect in effects)
    require(denominators[0] == denominators[1] and denominators[0] > 0,
            "the separately computed channel denominators must agree and be positive")
    denominator = denominators[0]
    defects = tuple(denominator * identity(m) - effect for effect in effects)
    gram_rows = []
    for family, defect in zip((first, second), defects):
        # These are actual integer Gram factors, not an eigenvalue estimate.
        witnesses = [[int(i == j) for j in range(m)] for i in range(m)]
        for a in family:
            for row in range(m):
                for i, j in combinations(range(m), 2):
                    if a[row, i] or a[row, j]:
                        witness = [0] * m
                        witness[i], witness[j] = int(a[row, j]), -int(a[row, i])
                        witnesses.append(witness)
        gram = fmpz_mat(witnesses)
        require(gram.transpose() * gram == defect, "failure-effect Gram identity failed")
        gram_rows.append(len(witnesses))
    tensor_choi = exact_matrix(tensor["choi"])
    require(tensor_choi.nrows() == tensor_choi.ncols() == m * m,
            "tensor Choi dimension mismatch")
    return Model(m, 2 * m + 1, denominator, first, second, effects,
                 defects, tensor_choi, tuple(gram_rows))


def apply_kraus(family, matrix):
    result = fmpz_mat(family[0].nrows(), family[0].nrows())
    if matrix != fmpz_mat(matrix.nrows(), matrix.ncols()):
        for a in family:
            result += a * matrix * a.transpose()
    return result


def channel_numerator(matrix, model):
    """Evaluate D*Theta directly on a matrix, without a Choi reshuffle."""
    m, n = model.m, model.n
    x0 = fmpz_mat([[matrix[i, j] for j in range(m)] for i in range(m)])
    x1 = fmpz_mat([[matrix[m+i, m+j] for j in range(m)] for i in range(m)])
    outputs = (apply_kraus(model.second, x1), apply_kraus(model.first, x0))
    result = fmpz_mat(n, n)
    for block, output in enumerate(outputs):
        for i in range(m):
            for j in range(m):
                result[block*m+i, block*m+j] = output[i, j]
    result[n-1, n-1] = (
        sum(defect[i, j] * x[j, i]
            for defect, x in zip(model.defects, (x0, x1))
            for i in range(m) for j in range(m))
        + model.denominator * matrix[n-1, n-1]
    )
    return result


def construct_channel(model):
    """Evaluate all complex matrix units once and twice, then form Choi matrices."""
    n = model.n
    choi, square = fmpz_mat(n*n, n*n), fmpz_mat(n*n, n*n)
    for i in range(n):
        for j in range(n):
            unit = fmpz_mat(n, n)
            unit[i, j] = 1
            image = channel_numerator(unit, model)
            twice = channel_numerator(image, model)
            for a in range(n):
                for b in range(n):
                    choi[n*i+a, n*j+b] = image[a, b]
                    square[n*i+a, n*j+b] = twice[a, b]
    return choi, square


def verify_trace(choi, n, denominator):
    require(all(sum(choi[n*i+a, n*j+a] for a in range(n))
                == denominator * int(i == j)
                for i in range(n) for j in range(n)),
            "the reconstructed channel must preserve trace")


def verify_transposes(choi, n):
    require(all(choi[n*i+a, n*j+b] == choi[n*i+b, n*j+a]
                == choi[n*j+a, n*i+b]
                for i in range(n) for j in range(n)
                for a in range(n) for b in range(n)),
            "channel Choi partial-transpose identities failed")


def verify_flag(choi, n, denominator):
    last = n*n - 1
    require(all(choi[row, last] == denominator * int(row == last)
                and choi[last, row] == denominator * int(row == last)
                for row in range(n*n)),
            "the flag product vector must be a positive eigenvector")
    require(all(choi[n*(n-1)+a, n*(n-1)+b]
                == denominator * int(a == b == n-1)
                for a in range(n) for b in range(n)),
            "the flag input must be absorbing")


def verify_positive_assembly(choi, model):
    """Match matrix-unit output against a positive Gram-plus-flag decomposition."""
    n, m = model.n, model.m
    vectors = []
    for family, source, target in ((model.first, 0, m), (model.second, m, 0)):
        for a in family:
            vector = [0] * (n*n)
            for i in range(m):
                for j in range(m):
                    vector[n*(source+i)+target+j] = int(a[j, i])
            vectors.append(vector)
    gram = fmpz_mat(vectors)
    positive = gram.transpose() * gram
    for block, defect in enumerate(model.defects):
        for i in range(m):
            for j in range(m):
                positive[n*(block*m+i)+n-1, n*(block*m+j)+n-1] += defect[j, i]
    positive[n*n-1, n*n-1] += model.denominator
    require(positive == choi, "channel matrix-unit and positive Gram assembly disagree")


def canonical_digest(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def decode_sparse(value, size):
    require(set(value) == {"shape", "entries"} and value["shape"] == [size, size],
            "unexpected sparse Choi schema or shape")
    result = fmpz_mat(size, size)
    previous = (-1, -1)
    for entry in value["entries"]:
        require(isinstance(entry, list) and len(entry) == 3
                and all(type(item) is int for item in entry),
                "expected integer sparse entries")
        row, column, number = entry
        require(0 <= row < size and 0 <= column < size and number != 0
                and previous < (row, column),
                "sparse entries must be nonzero, in bounds, unique, and row-major")
        result[row, column] = number
        previous = (row, column)
    return result


def compare_certificate(certificate, tensor, model, choi, square):
    require(set(certificate) == {"schema_version", "source_tensor_sha256", "dimension",
                                "denominator", "effects", "channel_choi", "square_choi"},
            "unexpected channel certificate fields")
    require(type(certificate["schema_version"]) is int and certificate["schema_version"] == 1,
            "unsupported channel certificate schema")
    require(certificate["source_tensor_sha256"] == canonical_digest(tensor),
            "channel source tensor digest mismatch")
    require(type(certificate["dimension"]) is int and certificate["dimension"] == model.n
            and type(certificate["denominator"]) is int
            and certificate["denominator"] == model.denominator,
            "channel dimension or denominator mismatch")
    require(tuple(exact_matrix(rows) for rows in certificate["effects"]) == model.effects,
            "channel effects mismatch")
    require(decode_sparse(certificate["channel_choi"], model.n**2) == choi,
            "saved channel Choi differs from independent matrix-unit construction")
    require(decode_sparse(certificate["square_choi"], model.n**2) == square,
            "saved square Choi differs from independent twice-applied block map")


def must_reject(action):
    try:
        action()
    except ReviewFailure as error:
        return str(error)
    raise ReviewFailure("a deliberately false control was accepted")


def failure_controls(choi, square, model):
    n, denominator = model.n, model.denominator
    controls = {}
    missing = fmpz_mat(choi)
    for i in range(n-1):
        for j in range(n-1):
            missing[n*i+n-1, n*j+n-1] = 0
    controls["missing_failure_branches"] = must_reject(
        lambda: verify_trace(missing, n, denominator))
    lost = fmpz_mat(choi)
    lost[n*n-1, n*n-1] = 0
    controls["lost_flag"] = must_reject(lambda: verify_trace(lost, n, denominator))
    redirected = fmpz_mat(lost)
    redirected[n*(n-1), n*(n-1)] = denominator
    verify_trace(redirected, n, denominator)
    controls["trace_preserving_nonabsorbing_flag"] = must_reject(
        lambda: verify_flag(redirected, n, denominator))
    corrupted = fmpz_mat(choi)
    corrupted[0, 0] += 1
    controls["corrupted_choi_entry"] = must_reject(
        lambda: require(corrupted == choi, "corrupted Choi disagrees with matrix-unit oracle"))
    verify_flag(square, n, denominator**2)
    controls["full_range_product_exclusion"] = (
        "refuted: e_flag tensor e_flag is an eigenvector with positive eigenvalue D^2"
    )
    return controls


def review(tensor, certificate=None):
    start = time.perf_counter()
    model = build_model(tensor)
    choi, square = construct_channel(model)
    for matrix, denominator in ((choi, model.denominator), (square, model.denominator**2)):
        verify_trace(matrix, model.n, denominator)
        verify_transposes(matrix, model.n)
        verify_flag(matrix, model.n, denominator)
    verify_positive_assembly(choi, model)
    corner = fmpz_mat([
        [square[model.n*i+a, model.n*j+b] for j in range(model.m) for b in range(model.m)]
        for i in range(model.m) for a in range(model.m)
    ])
    require(corner == model.tensor_choi, "channel square corner differs from the entire tensor Z0")
    if certificate is not None:
        compare_certificate(certificate, tensor, model, choi, square)
    controls = failure_controls(choi, square, model)
    if certificate is not None:
        for field in ("channel_choi", "square_choi"):
            corrupted = deepcopy(certificate)
            corrupted[field]["entries"][0][2] += 1
            controls["corrupted_saved_" + field] = must_reject(
                lambda: compare_certificate(corrupted, tensor, model, choi, square))
    return {
        "status": "independent_finite_checks_passed",
        "dimension": model.n,
        "denominator": model.denominator,
        "effect_traces": [int(sum(a[i, i] for i in range(model.m))) for a in model.effects],
        "defect_gram_rows": list(model.defect_gram_rows),
        "matrix_units_checked": model.n**2,
        "channel_and_square_trace_preserving": True,
        "both_partial_transposes_fixed": True,
        "positive_gram_assembly_checked": True,
        "square_corner_equals_tensor_Z0": True,
        "normalized_square_corner_multiplier": [1, model.denominator**2],
        "full_square_range_contains_flag_product": True,
        "saved_channel_certificate_compared": certificate is not None,
        "source_tensor_sha256": canonical_digest(tensor),
        "channel_certificate_sha256": (canonical_digest(certificate)
                                       if certificate is not None else None),
        "failure_controls": controls,
        "elapsed_seconds": round(time.perf_counter() - start, 6),
        "formal_proof_kernel_verification": False,
        "secret_key_theorem_checked": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tensor_certificate", type=Path)
    parser.add_argument("--channel-certificate", type=Path)
    args = parser.parse_args()
    tensor = json.loads(args.tensor_certificate.read_text())
    certificate = (json.loads(args.channel_certificate.read_text())
                   if args.channel_certificate is not None else None)
    print(json.dumps(review(tensor, certificate), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
