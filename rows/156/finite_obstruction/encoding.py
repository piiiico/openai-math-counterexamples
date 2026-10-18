"""Direct CNF for the six fields of OpenAI's ten-label TenSystem.

Copyright (c) 2026 Alexander Richard Towell. MIT license.
Substantial OpenAI Codex assistance. No solver or source proof is imported.
"""
from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class Constraint:
    family: str
    clause: tuple[int, ...]


@dataclass
class Encoding:
    triples: dict[frozenset[int], int]
    tetrahedra: dict[frozenset[int], int]
    constraints: list[Constraint]

    @property
    def variables(self):
        return len(self.triples) + len(self.tetrahedra)

    def clauses(self, omitted=frozenset()):
        return [c.clause for c in self.constraints if c.family not in omitted]


def build():
    labels = frozenset(range(10))
    triples = {frozenset(t): i + 1 for i, t in enumerate(combinations(range(10), 3))}
    tetrahedra = {frozenset(t): len(triples) + i + 1
                  for i, t in enumerate(combinations(range(10), 4))}
    constraints = []

    def add(family, *clause):
        constraints.append(Constraint(family, tuple(clause)))

    for triangle, tv in triples.items():
        extensions = [qv for s, qv in tetrahedra.items() if triangle <= s]
        add('pure', -tv, *extensions)
        for qv in extensions:
            add('down', -qv, tv)
            add('no_boundary', -qv, *(other for other in extensions if other != qv))
    for facet, qv in tetrahedra.items():
        complement = labels - facet
        for triangle in combinations(sorted(complement), 3):
            t = frozenset(triangle)
            a, b = triples[t], triples[complement - t]
            if a < b:  # Each complementary pair is encoded once.
                add('complementary', -qv, a, b)
                add('complementary', -qv, -a, -b)
        for pair in combinations(sorted(complement), 2):
            p = frozenset(pair)
            choices = [triples[p | {w}] for w in sorted(complement - p)]
            for three in combinations(choices, 3):
                # Exactly two of four: neither three false nor three true.
                add('pair_count', -qv, *three)
                add('pair_count', -qv, *(-v for v in three))
    add('nonempty', tetrahedra[frozenset(range(4))])
    return Encoding(triples, tetrahedra, constraints)


def assignment_for_facets(encoding, facets):
    facets = {frozenset(f) for f in facets}
    triangles = {frozenset(t) for f in facets for t in combinations(sorted(f), 3)}
    return {**{v: t in triangles for t, v in encoding.triples.items()},
            **{v: f in facets for f, v in encoding.tetrahedra.items()}}


def satisfies(clauses, assignment):
    return all(any(assignment[abs(lit)] == (lit > 0) for lit in clause)
               for clause in clauses)


def dimacs(encoding, omitted=frozenset()):
    clauses = encoding.clauses(omitted)
    return f'p cnf {encoding.variables} {len(clauses)}\n' + ''.join(
        ' '.join(map(str, clause)) + ' 0\n' for clause in clauses)
