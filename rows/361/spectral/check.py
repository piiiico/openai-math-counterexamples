"""Exact finite selection for OpenAI math family 361 (standard library only).

The fast generator uses polynomial prefix sums. The replay checker instead
adds literal binomial-difference multiplicities. No metric theorem is checked.
"""

from __future__ import annotations
import argparse
from dataclasses import asdict, dataclass
from functools import lru_cache
import hashlib
import json
from math import comb
from pathlib import Path
import time


@dataclass(frozen=True)
class Parameters:
    s: int = 8
    k: int = 50000
    q_num: int = 101
    q_den: int = 100
    alpha_num: int = 99853
    alpha_den: int = 100000

    @property
    def m(self):
        return 2 * self.s - 1

    @property
    def h(self):
        return self.m - 1

    @property
    def target(self):
        return self.q_num * self.alpha_num * self.k * (self.k + self.h)


def require(condition, message):
    """Failure detection remains enabled under python -O."""
    if not condition:
        raise ValueError(message)


def multiplicity(p, l, b):
    """Unpaired h(l,b), using the factored polynomial identity."""
    require(0 <= b <= l, "bidegree out of range")
    numerator = (l + p.s - 1) * comb(b + p.s - 2, p.s - 2) * comb(l - b + p.s - 2, p.s - 2)
    require(numerator % (p.s - 1) == 0, "nonintegral multiplicity")
    return numerator // (p.s - 1)


def sphere_dimension(p, l):
    return comb(l + p.m, p.m) - comb(l + p.m - 2, p.m)


def euclidean_dimension(p, k):
    return comb(k + p.m, p.m) + comb(k + p.m - 1, p.m)


def forward_coefficients(values):
    result = []
    while values:
        result.append(values[0])
        values = [b - a for a, b in zip(values, values[1:])]
    return tuple(result)


@lru_cache(maxsize=512)
def moment_coefficients(p, l):
    # All samples must satisfy b <= l so ordinary combinatorial values
    # equal the relevant polynomials; no negative-top binomials are used.
    require(l >= 2 * p.s - 2, "degree too small for the polynomial sampler")
    values = [multiplicity(p, l, b) for b in range(2 * p.s - 1)]
    charge_values = [value * (l - 2 * b)**2 for b, value in enumerate(values)]
    return forward_coefficients(values[:2 * p.s - 3]), forward_coefficients(charge_values)


def prefix_moments(p, l, groups):
    """Count and squared-charge sum of the first paired b-groups."""
    require(0 <= groups <= l // 2 + 1, "prefix out of range")
    coefficients, charge_coefficients = moment_coefficients(p, l)
    count = 2 * sum(c * comb(groups, j + 1) for j, c in enumerate(coefficients))
    charge = 2 * sum(c * comb(groups, j + 1) for j, c in enumerate(charge_coefficients))
    if l % 2 == 0 and groups == l // 2 + 1:
        count -= multiplicity(p, l, l // 2)
    return count, charge


def eigenvalue_numerator(p, l, b):
    return p.alpha_den * (p.q_num * l * (l + p.h) - (p.q_num - p.q_den) * (l - 2 * b)**2)


def prefix_weight(p, l, groups):
    count, charge = prefix_moments(p, l, groups)
    total = p.alpha_den * (p.q_num * l * (l + p.h) * count - (p.q_num - p.q_den) * charge)
    return count, total


def select_degree(p, l):
    """Maximal ordered prefix for the sufficient mean-eigenvalue criterion."""
    lo, hi = 0, l // 2 + 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        count, total = prefix_weight(p, l, mid)
        if total < p.target * count:
            lo = mid
        else:
            hi = mid - 1
    count, total = prefix_weight(p, l, lo)
    take = 0
    if count and lo < l // 2 + 1:
        numerator = eigenvalue_numerator(p, l, lo)
        excess = numerator - p.target
        require(excess > 0, "partial group has nonpositive excess")
        group_size = multiplicity(p, l, lo) * (1 if 2 * lo == l else 2)
        take = min(group_size, (p.target * count - total - 1) // excess)
        count += take
        total += take * numerator
    return {"degree": l, "full_groups": lo, "partial_take": take,
            "count": count, "weighted_num": total, "slack": p.target * count - total}


def cutoffs(p):
    full = p.k
    while p.alpha_den * full * (full + p.h) >= p.alpha_num * p.k * (p.k + p.h):
        full -= 1
    last = p.k
    while eigenvalue_numerator(p, last, 0) < p.target:
        last += 1
    return full, last - 1


def generate():
    p = Parameters()
    full, last = cutoffs(p)
    rows = [select_degree(p, l) for l in range(full + 1, last + 1)]
    low_count = euclidean_dimension(p, full) - (2 * p.s + 1)
    selected = low_count + sum(row["count"] for row in rows)
    comparator = euclidean_dimension(p, p.k)
    return {"schema": "family361-spectral-selection-v1", "parameters": asdict(p),
            "full_cutoff": full, "last_degree": last, "low_count": low_count,
            "degrees": rows, "selected": selected, "comparator": comparator,
            "surplus": selected - comparator}


def parameter_checks(p):
    require(p == Parameters(), "parameters differ from the pinned problem")
    require(p.q_num > p.q_den > 0 and 0 < p.alpha_num < p.alpha_den,
            "parameter sign conditions")
    curvature_num = p.q_den * p.h * (p.alpha_den - p.alpha_num) - 2 * (p.q_num - p.q_den) * p.alpha_den
    require(curvature_num > 0, "endpoint curvature margin")
    require(p.q_num * p.alpha_num**p.m < p.q_den * p.alpha_den**p.m,
            "a < 1 condition")
    require(1000 * (p.alpha_den - p.alpha_num) < 2 * p.alpha_num,
            "logarithmic upper-bound witness")


def replay(certificate):
    """Replay literal binomial differences, without any prefix-sum machinery.

    Deliberately does not call select_degree, prefix_moments, cutoffs,
    multiplicity, sphere_dimension, or euclidean_dimension.
    """
    p = Parameters()
    parameter_checks(p)
    require(certificate.get("schema") == "family361-spectral-selection-v1", "schema mismatch")
    require(certificate.get("parameters") == asdict(p), "parameters mismatch")
    full, last = certificate["full_cutoff"], certificate["last_degree"]
    require(type(full) is int and type(last) is int and 2 <= full < last, "invalid cutoffs")
    bound = p.alpha_num * p.k * (p.k + p.h)
    require(p.alpha_den * full * (full + p.h) < bound <= p.alpha_den * (full + 1) * (full + 1 + p.h),
            "full cutoff boundary")
    def minimum_num(l):
        return p.alpha_den * (p.q_den * l * l + p.q_num * p.h * l)
    require(minimum_num(last) < p.target <= minimum_num(last + 1), "last cutoff boundary")
    low_count = comb(full + p.m, p.m) + comb(full + p.m - 1, p.m) - (2 * p.s + 1)
    require(certificate["low_count"] == low_count, "low-degree count (degrees 0 and 1 excluded)")
    rows = certificate["degrees"]
    require([row["degree"] for row in rows] == list(range(full + 1, last + 1)), "degree coverage")
    selected, full_degrees, partial_degrees, groups_checked = low_count, 0, 0, 0
    minimum_slack = None
    for row in rows:
        require(set(row) == {"degree", "full_groups", "partial_take", "count", "weighted_num", "slack"}, "degree fields")
        require(all(type(value) is int for value in row.values()), "degree fields must be integers")
        l, groups, take = row["degree"], row["full_groups"], row["partial_take"]
        require(0 <= groups <= l // 2 + 1 and take >= 0, "invalid prefix")
        count = total = next_num = next_mult = 0
        for b in range(groups + (1 if groups <= l // 2 else 0)):
            # Independent unfactored formula from the source statement.
            h = comb(b + p.s - 1, p.s - 1) * comb(l - b + p.s - 1, p.s - 1) - comb(b + p.s - 2, p.s - 1) * comb(l - b + p.s - 2, p.s - 1)
            mult = h * (1 if 2 * b == l else 2)
            numerator = p.alpha_den * (p.q_num * l * (l + p.h) + (p.q_den - p.q_num) * (2 * b - l)**2)
            groups_checked += 1
            if b == groups:
                next_mult, next_num = mult, numerator
            else:
                count += mult
                total += mult * numerator
        if groups == l // 2 + 1:
            require(take == 0, "partial selection after full degree")
            require(count == comb(l + p.m, p.m) - comb(l + p.m - 2, p.m), "full-degree dimension")
            full_degrees += 1
        else:
            require(take < next_mult, "partial group is not partial")
            count += take
            total += take * next_num
            require(total + next_num >= p.target * (count + 1), "next vector still passes sufficient criterion")
            partial_degrees += 1
        slack = p.target * count - total
        require(count > 0 and slack > 0, "mean-eigenvalue inequality is not strict")
        require((row["count"], row["weighted_num"], row["slack"]) == (count, total, slack), "degree arithmetic mismatch")
        minimum_slack = slack if minimum_slack is None else min(minimum_slack, slack)
        selected += count
    comparator = comb(p.k + p.m, p.m) + comb(p.k + p.m - 1, p.m)
    require(certificate["selected"] == selected, "selected total mismatch")
    require(certificate["comparator"] == comparator, "comparator mismatch")
    require(certificate["surplus"] == selected - comparator > 0, "strict surplus mismatch")
    return {"status": "verified", "checked_degrees": len(rows), "full_degrees": full_degrees,
            "partial_degrees": partial_degrees, "groups_checked": groups_checked,
            "minimum_strict_slack": minimum_slack,
            "selected": selected, "comparator": comparator, "surplus": selected - comparator}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="generate and verify before writing")
    parser.add_argument("--certificate", type=Path, default=Path(__file__).with_name("certificate.json"))
    args = parser.parse_args()
    started = time.monotonic()
    certificate = generate() if args.write else json.loads(args.certificate.read_text())
    result = replay(certificate)
    data = (json.dumps(certificate, sort_keys=True, indent=2) + "\n").encode()
    if args.write:
        args.certificate.write_bytes(data)
    result["certificate_sha256"] = hashlib.sha256(data).hexdigest()
    result["elapsed_seconds"] = round(time.monotonic() - started, 6)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
