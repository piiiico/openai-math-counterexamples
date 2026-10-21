#!/usr/bin/env python3
"""Family190: exact fixed-anchor repair model and solver-free RUP replay.

OpenAI source 1581d4cbdd69a0faf34b2089614fe2a814316a6a, Polynomial-removal-fails-
for-ordered-binary-matrices-September-25-2026, sections 02,03,03b. See PROOF.md
for the model/full-host bridge. This is finite computation, not a kernel proof.
Alexander Richard Towell, substantial OpenAI Codex assistance. MIT.
"""

from dataclasses import dataclass
from enum import Enum
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json


class Sign(Enum):
    PLUS = "+"
    MINUS = "-"


class PositionKind(Enum):
    INTERNAL = "internal"
    LEAF = "leaf"
    DUMMY = "dummy"


class Kind(Enum):
    V = "V"
    W = "W"


@dataclass(frozen=True)
class Position:
    kind: PositionKind
    depth: int
    node: int
    offset: int
    sign: Sign | None = None


@dataclass(frozen=True)
class Mode:
    kind: Kind
    depth: int
    sign: Sign
    parity: int | None = None


@dataclass(frozen=True)
class Body:
    mode: Mode
    cells: tuple[int, int, int, int]


class Model:
    """The source's non-anchor axes and ALL admissible mode bodies."""

    def __init__(self, h):
        if not isinstance(h, int) or h < 1:
            raise ValueError("positive integer depth required")
        self.h = h
        self.m = 2**h
        self.rows = self.axis(row=True)
        self.columns = self.axis(row=False)
        self.width = len(self.columns)
        self.original = tuple(self.entry(r, c) for r in self.rows for c in self.columns)
        self.modes = tuple(
            mode
            for i in range(1, h + 1)
            for mode in (
                Mode(Kind.V, i, Sign.PLUS),
                Mode(Kind.V, i, Sign.MINUS),
                Mode(Kind.W, i, Sign.PLUS, 0),
                Mode(Kind.W, i, Sign.PLUS, 1),
                Mode(Kind.W, i, Sign.MINUS, 0),
                Mode(Kind.W, i, Sign.MINUS, 1),
            )
        )
        self.bodies = tuple(self.all_bodies())

    def axis(self, row):
        before = Sign.MINUS if row else Sign.PLUS
        after = Sign.PLUS if row else Sign.MINUS

        def subtree(i, p):
            if i == self.h:
                return [Position(PositionKind.LEAF, i, p, 0)]
            block = self.m // 2**i
            return (
                [Position(PositionKind.INTERNAL, i, p, x, before) for x in range(block)]
                + subtree(i + 1, 2 * p)
                + subtree(i + 1, 2 * p + 1)
                + [
                    Position(PositionKind.INTERNAL, i, p, x, after)
                    for x in range(block)
                ]
            )

        variable = subtree(0, 0)
        dummy = [Position(PositionKind.DUMMY, -1, -1, x) for x in range(self.m)]
        return tuple(variable + dummy if row else dummy + variable)

    @staticmethod
    def in_level(p, depth, sign, parity=None):
        return (
            p.depth == depth
            and p.kind is not PositionKind.DUMMY
            and (p.kind is PositionKind.LEAF or p.sign is sign)
            and (parity is None or p.node % 2 == parity)
        )

    def entry(self, r, c):
        if PositionKind.DUMMY in (r.kind, c.kind):
            return True
        # The leaves carry both signs; same-level minus excludes them.
        same = r.depth == c.depth
        if (
            same
            and self.in_level(r, r.depth, Sign.PLUS)
            and self.in_level(c, c.depth, Sign.PLUS)
        ):
            return r.node <= c.node
        if same and r.depth < self.h and r.sign is Sign.MINUS and c.sign is Sign.MINUS:
            return r.node < c.node
        if r.depth == c.depth + 1:
            if self.in_level(r, r.depth, Sign.PLUS) and self.in_level(
                c, c.depth, Sign.PLUS
            ):
                return r.node // 2 <= c.node
            if self.in_level(r, r.depth, Sign.MINUS) and self.in_level(
                c, c.depth, Sign.MINUS
            ):
                return r.node // 2 < c.node
        return False

    def role(self, p, mode, row, role):
        i, sign = mode.depth, mode.sign
        if mode.kind is Kind.V:
            if not row:
                return (
                    p.kind is PositionKind.DUMMY
                    if role == 0
                    else self.in_level(p, i - 1, sign)
                )
            depth = (
                (i if role == 0 else i - 1)
                if sign is Sign.PLUS
                else (i - 1 if role == 0 else i)
            )
            return self.in_level(p, depth, sign)
        if row:
            return (
                self.in_level(p, i, sign, mode.parity)
                if role == 0
                else p.kind is PositionKind.DUMMY
            )
        child = (role == 1) if sign is Sign.PLUS else (role == 0)
        return (
            self.in_level(p, i, sign, mode.parity)
            if child
            else self.in_level(p, i - 1, sign)
        )

    def all_bodies(self):
        for mode in self.modes:
            rs = [
                [i for i, p in enumerate(self.rows) if self.role(p, mode, True, j)]
                for j in (0, 1)
            ]
            cs = [
                [i for i, p in enumerate(self.columns) if self.role(p, mode, False, j)]
                for j in (0, 1)
            ]
            for r1, r2, c1, c2 in product(*rs, *cs):
                if r1 < r2 and c1 < c2:
                    yield Body(
                        mode,
                        (
                            r1 * self.width + c1,
                            r1 * self.width + c2,
                            r2 * self.width + c1,
                            r2 * self.width + c2,
                        ),
                    )

    def check_bits(self, bits):
        if len(bits) != len(self.original) or any(type(b) is not bool for b in bits):
            raise ValueError("complete Boolean matrix required")

    def cost(self, bits):
        self.check_bits(bits)
        return sum(a != b for a, b in zip(bits, self.original))

    def violations(self, bits):
        self.check_bits(bits)
        return [
            body
            for body in self.bodies
            if tuple(bits[c] for c in body.cells) == (True, False, True, True)
        ]

    def dummy_leaf_repair(self):
        return tuple(
            False
            if r.kind is PositionKind.DUMMY and c.kind is PositionKind.LEAF
            else self.entry(r, c)
            for r in self.rows
            for c in self.columns
        )

    def leaf_hitting_set(self):
        return tuple(
            False
            if r.kind is c.kind is PositionKind.LEAF and r.node == c.node
            else self.entry(r, c)
            for r in self.rows
            for c in self.columns
        )

    def body_clauses(self):
        return [
            (-(a + 1), b + 1, -(c + 1), -(d + 1))
            for a, b, c, d in (body.cells for body in self.bodies)
        ]

    def cnf(self, bound):
        edits = [-(i + 1) if bit else i + 1 for i, bit in enumerate(self.original)]
        counter, highest, _ = at_most(edits, bound, len(edits))
        return self.body_clauses() + counter, highest


def neg(lit):
    return not lit if type(lit) is bool else -lit


def at_most(literals, bound, highest):
    """Exact prefix-count circuit. s[i,j] <-> at least j of first i literals.

    Each gate z <-> a OR (b AND c) uses all four implications.
    The final output s[n,bound+1] is forced false. See PROOF.md.
    """
    if bound < 0:
        raise ValueError("nonnegative bound required")
    clauses, counter = [], {}

    def s(i, j):
        return True if j == 0 else counter.get((i, j), False)

    def emit(*lits):
        if any(lit is True for lit in lits):
            return
        clause = tuple(dict.fromkeys(lit for lit in lits if lit is not False))
        clauses.append(clause)

    for i, c in enumerate(literals, 1):
        for j in range(1, min(i, bound + 1) + 1):
            highest += 1
            z = highest
            counter[i, j] = z
            a, b = s(i - 1, j), s(i - 1, j - 1)
            emit(neg(a), z)
            emit(neg(b), neg(c), z)
            emit(-z, a, b)
            emit(-z, a, c)
    emit(neg(s(len(literals), bound + 1)))
    return clauses, highest, counter


def is_rup(clauses, candidate):
    """Reverse unit propagation, with fresh assignments for every addition."""
    if any(type(lit) is not int or lit == 0 for lit in candidate):
        raise ValueError("nonzero integer literals required")
    assignment = {}
    for lit in candidate:
        variable, value = abs(lit), lit < 0
        if variable in assignment and assignment[variable] != value:
            return True
        assignment[variable] = value
    changed = True
    while changed:
        changed = False
        for clause in clauses:
            unknown = []
            satisfied = False
            for lit in clause:
                value = assignment.get(abs(lit))
                if value is None:
                    unknown.append(lit)
                elif value == (lit > 0):
                    satisfied = True
                    break
            if satisfied:
                continue
            if not unknown:
                return True
            if len(unknown) == 1:
                lit = unknown[0]
                assignment[abs(lit)] = lit > 0
                changed = True
    return False


def replay(clauses, proof):
    if not proof or proof[-1] != ():
        raise ValueError("proof must end in the empty clause")
    database = list(clauses)
    for i, clause in enumerate(proof):
        if not is_rup(database, clause):
            raise ValueError(f"addition {i} is not RUP")
        database.append(clause)
    return len(proof)


def canonical_hash(clauses):
    return hashlib.sha256(
        json.dumps(clauses, separators=(",", ":")).encode()
    ).hexdigest()


def verify(packet_dir, negative_control=None):
    model = Model(1)
    certificate = json.loads((packet_dir / "certificate.json").read_text())
    if certificate["depth"] != 1 or certificate["excluded_budget"] != 3:
        raise ValueError("wrong finite domain or budget")
    clauses, highest = model.cnf(3)
    if certificate["cnf_sha256"] != canonical_hash(clauses):
        raise ValueError("input binding mismatch")
    proof = [tuple(c) for c in certificate["rup_additions"]]
    if negative_control == "truncate":
        proof = proof[:-1]
    if negative_control == "weaken":
        clauses = [
            c
            for c, b in zip(model.body_clauses(), model.bodies)
            if not (
                b.mode.kind is Kind.W
                and b.mode.sign is Sign.MINUS
                and b.mode.parity == 0
            )
        ] + clauses[len(model.bodies) :]
    count = replay(clauses, proof)
    witness = certificate["repaired_bits"]
    if negative_control == "witness":
        witness = list(witness)
        cell = next(
            i for i, (a, b) in enumerate(zip(model.original, witness)) if a != b
        )
        witness[cell] = model.original[cell]
    if model.cost(witness) != 4 or model.violations(witness):
        raise ValueError("upper-bound witness invalid")
    if tuple(witness) != model.dummy_leaf_repair():
        raise ValueError("witness does not equal the specified repair")
    print(
        f"h=1 non-anchor region: {len(model.rows)}x{len(model.columns)}; {len(model.bodies)} bodies"
    )
    print(f"CNF: {highest} variables, {len(clauses)} clauses; {count} RUP additions")
    print("original bodies:", len(model.violations(model.original)))
    print(
        "leaf-hitting-set edits/new bodies:",
        model.cost(model.leaf_hitting_set()),
        len(model.violations(model.leaf_hitting_set())),
    )
    print("optimal fixed-anchor repair edits:", model.cost(witness))
    print("RESULT: certified fixed-anchor repair optimum 4 at h=1")
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet-dir", type=Path, default=Path(__file__).parent)
    parser.add_argument("--negative-control", choices=["truncate", "weaken", "witness"])
    args = parser.parse_args()
    try:
        verify(args.packet_dir, args.negative_control)
    except (ValueError, KeyError, TypeError) as error:
        print("RESULT: rejected:", error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
