"""Exhaust the finite six-label domain used on tetrahedron complements.

Copyright (c) 2026 Alexander Richard Towell. MIT license.
Substantial OpenAI Codex assistance. This checks only finite combinatorics.
"""
from itertools import combinations, permutations, product
from rup import InvalidProof


def valid_system(labels, triangles):
    triples = [frozenset(t) for t in combinations(sorted(labels), 3)]
    return (all((t in triangles) != (labels - t in triangles) for t in triples)
            and all(sum(frozenset(p) <= t for t in triangles) == 2
                    for p in combinations(sorted(labels), 2)))


def six_system_controls(corrupt=False):
    labels = frozenset(range(6))
    triples = [frozenset(t) for t in combinations(range(6), 3)]
    pairs = [(t, labels - t) for t in triples
             if tuple(sorted(t)) < tuple(sorted(labels - t))]
    systems = []
    for choices in product((0, 1), repeat=len(pairs)):
        triangles = frozenset(pair[bit] for pair, bit in zip(pairs, choices))
        if valid_system(labels, triangles):
            systems.append(triangles)
    if not systems:
        raise InvalidProof('six-system domain unexpectedly empty')
    if corrupt:
        triangle = min(systems[0], key=lambda t: tuple(sorted(t)))
        systems[0] = (systems[0] - {triangle}) | {labels - triangle}
    four_checks = link_checks = restricted_checks = 0
    projections = [set() for _ in labels]
    for system in systems:
        if not valid_system(labels, system):
            raise InvalidProof('corrupted six-label system violates pair/complement axioms')
        links = {a: {t - {a} for t in system if a in t} for a in labels}
        for a, edges in links.items():
            remaining = labels - {a}
            if any(sum(v in e for e in edges) != 2 for v in remaining):
                raise InvalidProof('link is not 2-regular')
            reached = {min(remaining)}
            while True:
                enlarged = reached | set().union(*(e for e in edges if e & reached))
                if enlarged == reached:
                    break
                reached = enlarged
            if reached != remaining:
                raise InvalidProof('link is not connected')
            link_checks += 1
        for four in combinations(range(6), 4):
            count = sum(t <= frozenset(four) for t in system)
            if count != 2:
                raise InvalidProof('four-subset does not have exactly two triangles')
            four_checks += 1
        for a, b in combinations(range(6), 2):
            for three in combinations(sorted(labels - {a, b}), 3):
                r = frozenset(three)
                if {e for e in links[a] if e <= r} == {e for e in links[b] if e <= r}:
                    raise InvalidProof('restricted links coincide')
                restricted_checks += 1
        for omitted in labels:
            restriction = frozenset(t for t in system if omitted not in t)
            if restriction in projections[omitted]:
                raise InvalidProof('five-label restriction does not determine the system')
            projections[omitted].add(restriction)
    orbit = set()
    stabilizers = 0
    for permutation in permutations(range(6)):
        image = frozenset(frozenset(permutation[v] for v in t) for t in systems[0])
        orbit.add(image)
        stabilizers += image == systems[0]
    if orbit != set(systems):
        raise InvalidProof('six-system orbit does not cover the enumerated domain')
    return {'complementary_pair_choices': 2 ** len(pairs), 'six_systems': len(systems),
            'five_cycle_links': link_checks, 'four_subset_checks': four_checks,
            'restricted_link_comparisons': restricted_checks,
            'five_label_unique_restrictions': sum(map(len, projections)),
            'permutations': 720, 'automorphisms': stabilizers,
            'orbits': 1}
