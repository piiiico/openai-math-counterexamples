#!/usr/bin/env python3
"""Independent exhaustive h=1 checker derived directly from the source tables.

Imports neither the primary model nor its certificate. Every repair with at
most three edits is checked, in lexicographic combination order (no seed).
Written by the separately tasked OpenAI Codex reviewer for Alexander Richard
Towell; substantial AI assistance, not human peer review. MIT.
"""

from itertools import combinations, product
import argparse


def run(negative_control=False):
    # Source order at h=1: each root/dummy block has size two; each shared
    # leaf block has size one. These are the complete eight-position axes.
    r_minus, r_leaf, r_plus, r_dummy = (0, 1), (2, 3), (4, 5), (6, 7)
    c_dummy, c_plus, c_leaf, c_minus = (0, 1), (2, 3), (4, 5), (6, 7)
    original = 0
    for row, col in product(range(8), repeat=2):
        value = (
            row in r_dummy
            or col in c_dummy
            or (row in r_plus and col in c_plus)
            or (row in r_leaf and col in c_plus)
            or (row in r_leaf and col in c_leaf and row - 2 <= col - 4)
        )
        original |= int(value) << (8 * row + col)
    if negative_control:
        original ^= 1 << 52  # Pre-apply one genuine repair edit.

    roles = [(r_leaf, r_plus, c_dummy, c_plus), (r_minus, r_leaf, c_dummy, c_minus)]
    roles += [((2 + parity,), r_dummy, c_plus, (4 + parity,)) for parity in (0, 1)]
    roles += [((2 + parity,), r_dummy, (4 + parity,), c_minus) for parity in (0, 1)]
    bodies = []
    for top_rows, bottom_rows, left_cols, right_cols in roles:
        for r1, r2, c1, c2 in product(top_rows, bottom_rows, left_cols, right_cols):
            if r1 < r2 and c1 < c2:
                cells = (8 * r1 + c1, 8 * r1 + c2, 8 * r2 + c1, 8 * r2 + c2)
                mask = sum(1 << cell for cell in cells)
                wanted = sum(1 << cells[index] for index in (0, 2, 3))
                bodies.append((mask, wanted))
    if len(bodies) != 48:
        raise RuntimeError("wrong ordered role domain")

    def has_body(matrix):
        return any(matrix & mask == wanted for mask, wanted in bodies)

    cases = 0
    for budget in range(4):
        for edits in combinations(range(64), budget):
            matrix = original ^ sum(1 << cell for cell in edits)
            if not has_body(matrix):
                raise RuntimeError(f"repair within budget three: {edits}")
            cases += 1
    repair_cells = tuple(8 * row + col for row in r_dummy for col in c_leaf)
    witness = original ^ sum(1 << cell for cell in repair_cells)
    if len(repair_cells) != 4 or has_body(witness):
        raise RuntimeError("four-edit witness failed")
    print(f"Ordered role bodies: {len(bodies)}")
    print(
        f"Exhausted repairs with zero through three edits: {cases}; all contain a body"
    )
    print(f"Four-edit witness cells: {repair_cells}; contains no body")
    print("RESULT: independent exhaustive optimum 4 at h=1")
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--negative-control", action="store_true")
    args = parser.parse_args()
    try:
        run(args.negative_control)
    except RuntimeError as error:
        print("RESULT: rejected:", error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
