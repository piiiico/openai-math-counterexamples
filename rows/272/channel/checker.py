"""Exact certificate for the existing Family272 absorbing-flag construction.

All positivity certificates use integer Gram identities. No spectral tolerance,
random sampling, or operational secret-key theorem is used.
"""
from dataclasses import dataclass
from itertools import combinations, combinations_with_replacement
import hashlib
import json

from flint import fmpz_mat


class ChannelCertificateError(ValueError):
    """A required exact finite identity failed."""


def require(condition, message):
    if not condition:
        raise ChannelCertificateError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def rows(matrix):
    return [[int(matrix[i, j]) for j in range(matrix.ncols())] for i in range(matrix.nrows())]


def identity(n):
    return fmpz_mat([[int(i == j) for j in range(n)] for i in range(n)])


def encode(matrix):
    return dict(shape=[matrix.nrows(), matrix.ncols()],
                entries=[[i, j, int(matrix[i, j])] for i in range(matrix.nrows())
                         for j in range(matrix.ncols()) if matrix[i, j]])


def decode(value):
    require(isinstance(value, dict) and set(value) == {"shape", "entries"}, "invalid sparse matrix")
    shape = value["shape"]
    require(isinstance(shape, list) and len(shape) == 2
            and all(type(n) is int and n > 0 for n in shape), "invalid sparse shape")
    matrix = fmpz_mat(*shape)
    previous = (-1, -1)
    for entry in value["entries"]:
        require(isinstance(entry, list) and len(entry) == 3
                and all(type(x) is int for x in entry), "invalid sparse entry")
        i, j, scalar = entry
        require(0 <= i < shape[0] and 0 <= j < shape[1] and scalar != 0
                and (i, j) > previous, "sparse entries must be nonzero, in bounds and ordered uniquely")
        matrix[i, j] = scalar
        previous = (i, j)
    return matrix


def choi(kraus):
    n = kraus[0].ncols()
    out = kraus[0].nrows()
    vectors = fmpz_mat([[k[a, i] for k in kraus] for i in range(n) for a in range(out)])
    return vectors * vectors.transpose()


def effect(kraus):
    n = kraus[0].ncols()
    return sum((k.transpose() * k for k in kraus), fmpz_mat(n, n))


def flag_gram(kraus):
    """Gram for I + sum_w (||w||² I - w wᵀ), without square roots."""
    n = kraus[0].ncols()
    columns = [[int(i == j) for i in range(n)] for j in range(n)]
    for k in kraus:
        for r in range(k.nrows()):
            w = [int(k[r, i]) for i in range(n)]
            for i, j in combinations(range(n), 2):
                if w[i] or w[j]:
                    v = [0] * n
                    v[i], v[j] = w[j], -w[i]
                    columns.append(v)
    vectors = fmpz_mat(columns).transpose()
    return vectors * vectors.transpose(), len(columns)


def pair_from_tensor(tensor):
    """Rebuild the 36 intermediate Kraus matrices from the original pencil."""
    pencil = tensor["pencil"]
    require(len(pencil) == 4 and all(len(m) == 6 for m in pencil)
            and all(len(row) == 4 for m in pencil for row in m)
            and all(type(x) is int for m in pencil for row in m for x in row),
            "expected the exact 4 by 6 by 4 pencil")
    sy, ex = list(combinations_with_replacement(range(4), 2)), list(combinations(range(4), 2))
    q = [fmpz_mat([[pencil[i][r][a] for i in range(4)] for a in range(4)]) for r in range(6)]
    h = []
    for left in q:
        for right in q:
            matrix = fmpz_mat(len(ex), len(sy))
            for a, (u, v) in enumerate(ex):
                for i, (c, d) in enumerate(sy):
                    matrix[a, i] = left[u, c] * right[v, d] - left[v, c] * right[u, d]
                    if c != d:
                        matrix[a, i] += left[u, d] * right[v, c] - left[v, d] * right[u, c]
            h.append(matrix)
    require([rows(k) for k in h] == tensor["s_kraus"], "tensor Kraus matrices disagree with pencil")
    complement = fmpz_mat(len(ex), len(ex))
    for j, pair in enumerate(ex):
        other = tuple(i for i in range(4) if i not in pair)
        permutation = pair + other
        sign = (-1) ** sum(permutation[i] > permutation[j]
                          for i in range(4) for j in range(i + 1, 4))
        complement[ex.index(other), j] = sign
    require(rows(complement) == tensor["complement"], "exterior complement disagrees with pencil convention")
    inclusion = fmpz_mat([[int(i == j) for j in range(len(ex))] for i in range(len(sy))])
    first = [inclusion * k for k in h]
    second = [k.transpose() * complement.transpose() * inclusion.transpose() for k in h]
    return first, second


def assemble(pair_choi, defects, denominator):
    n = defects[0].nrows()
    d, flag = 2 * n + 1, 2 * n
    answer = fmpz_mat(d * d, d * d)
    for block in range(2):
        out = 1 - block
        for i in range(n):
            for j in range(n):
                for a in range(n):
                    for b in range(n):
                        answer[d * (block * n + i) + out * n + a,
                               d * (block * n + j) + out * n + b] = pair_choi[block][n * i + a, n * j + b]
                answer[d * (block * n + i) + flag, d * (block * n + j) + flag] = defects[block][j, i]
    answer[d * flag + flag, d * flag + flag] = denominator
    return answer


def reshuffle(matrix, d):
    """Input-first Choi to row-major superoperator conversion."""
    return fmpz_mat([[matrix[d * i + a, d * j + b] for i in range(d) for j in range(d)]
                     for a in range(d) for b in range(d)])


def unreshuffle(matrix, d):
    """Inverse conversion; it is a different four-index permutation."""
    return fmpz_mat([[matrix[d * a + b, d * i + j] for j in range(d) for b in range(d)]
                     for i in range(d) for a in range(d)])


def partial_transpose_fixed(matrix, d):
    return all(matrix[d * i + a, d * j + b] == matrix[d * i + b, d * j + a]
               for i in range(d) for j in range(d) for a in range(d) for b in range(d))


def partial_trace(matrix, d):
    return fmpz_mat([[sum(matrix[d * i + a, d * j + a] for a in range(d))
                      for j in range(d)] for i in range(d)])


@dataclass(frozen=True)
class ChannelData:
    dimension: int
    denominator: int
    effects: tuple
    pair_choi: tuple
    defects: tuple
    gram_counts: tuple
    channel: fmpz_mat
    square: fmpz_mat
    source_z: fmpz_mat
    source_digest: str


def build(tensor):
    pair = pair_from_tensor(tensor)
    n = pair[0][0].ncols()
    effects = tuple(effect(ks) for ks in pair)
    traces = [int(sum(a[i, i] for i in range(n))) for a in effects]
    require(traces[0] == traces[1], "the two source denominators differ")
    denominator = 1 + traces[0]
    pair_choi = tuple(choi(ks) for ks in pair)
    for j in pair_choi:
        require(partial_transpose_fixed(j, n), "source map output transpose identity failed")
    defects = tuple(denominator * identity(n) - a for a in effects)
    grams = [flag_gram(ks) for ks in pair]
    require(all(g[0] == f for g, f in zip(grams, defects)), "failure-effect Gram identity failed")
    z = choi([second * first for second in pair[1] for first in pair[0]])
    require(rows(z) == tensor["choi"], "source composite Choi identity failed")
    d = 2 * n + 1
    channel = assemble(pair_choi, defects, denominator)
    superoperator = reshuffle(channel, d)
    square = unreshuffle(superoperator * superoperator, d)
    return ChannelData(d, denominator, effects, pair_choi, defects,
                       tuple(g[1] for g in grams), channel, square, z, digest(tensor))


def certify(data):
    d, scale, b, c = data.dimension, data.denominator, data.channel, data.square
    n = (d - 1) // 2
    require(scale > 0 and d == 2 * n + 1, "invalid positive normalization")
    require(partial_trace(b, d) == scale * identity(d), "channel trace preservation failed")
    require(partial_transpose_fixed(b, d), "channel output transpose identity failed")
    require(b == b.transpose(), "channel Hermitian identity failed")
    require(b == assemble(data.pair_choi, data.defects, scale), "channel Gram block assembly failed")
    superoperator = reshuffle(b, d)
    require(c == unreshuffle(superoperator * superoperator, d), "square composition identity failed")
    require(partial_trace(c, d) == scale * scale * identity(d), "square trace preservation failed")
    require(partial_transpose_fixed(c, d), "square output transpose identity failed")
    corner = fmpz_mat([[c[d * i + a, d * j + bb] for j in range(n) for bb in range(n)]
                      for i in range(n) for a in range(n)])
    require(corner == data.source_z, "entangled-corner identity failed")
    flag = d * d - 1
    require(b[flag, flag] == scale and c[flag, flag] == scale * scale
            and all(b[i, flag] == b[flag, i] == c[i, flag] == c[flag, i] == 0
                    for i in range(flag)), "absorbing product flag identity failed")
    certificate = dict(schema_version=1, source_tensor_sha256=data.source_digest,
                       dimension=d, denominator=scale, effects=[rows(a) for a in data.effects],
                       channel_choi=encode(b), square_choi=encode(c))
    report = dict(status="certified", scope="exact_trace_preserving_PPT_channel_and_square_corner",
                  dimension=d, denominator=scale, square_denominator=scale * scale,
                  channel_choi_rank=int(b.rank()), square_choi_rank=int(c.rank()),
                  flag_effect_gram_columns=list(data.gram_counts),
                  square_corner_trace_numerator=int(sum(corner[i, i] for i in range(n * n))),
                  square_corner_rank=int(corner.rank()), square_corner_positive_entry=int(corner[0, 0]),
                  flag_product_vector_in_square_range=True,
                  channel_nonzero_entries=len(certificate["channel_choi"]["entries"]),
                  square_nonzero_entries=len(certificate["square_choi"]["entries"]),
                  source_tensor_sha256=data.source_digest, certificate_sha256=digest(certificate),
                  geometry_replayed=False, secret_key_claim_checked=False,
                  non_entanglement_breaking_consequence="written local-compression argument plus separately certified geometry")
    return report, certificate


def verify_saved(tensor, certificate):
    require(isinstance(certificate, dict) and certificate.get("schema_version") == 1,
            "invalid saved certificate schema")
    # Parse before comparison so duplicate, out-of-range or nonintegral entries fail explicitly.
    decode(certificate["channel_choi"])
    decode(certificate["square_choi"])
    report, expected = certify(build(tensor))
    require(certificate == expected, "saved certificate differs from exact reconstruction")
    return report
