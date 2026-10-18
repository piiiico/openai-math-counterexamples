"""Small solver-independent reverse-unit-propagation checker.

Copyright (c) 2026 Alexander Richard Towell. MIT license.
Substantial OpenAI Codex assistance. All failures remain active under python -O.
"""
from collections import defaultdict


class InvalidProof(ValueError):
    pass


class Database:
    def __init__(self, variables, clauses):
        self.variables = variables
        self.clauses = []
        self.watches = defaultdict(list)
        self.units = []
        self.inconsistent = False
        for clause in clauses:
            self.add(clause)

    def validate(self, clause):
        if not isinstance(clause, (list, tuple)):
            raise InvalidProof('clause must be an integer list')
        if any(type(lit) is not int or lit == 0 or abs(lit) > self.variables
               for lit in clause):
            raise InvalidProof('literal outside the declared variable domain')
        if len(set(clause)) != len(clause):
            raise InvalidProof('duplicate literal')

    def add(self, clause):
        self.validate(clause)
        clause = list(clause)
        index = len(self.clauses)
        self.clauses.append(clause)
        if not clause:
            self.inconsistent = True
        elif len(clause) == 1:
            self.units.append(clause[0])
        else:
            self.watches[clause[0]].append(index)
            self.watches[clause[1]].append(index)

    def conflict(self, assumptions=()):
        if self.inconsistent:
            return True
        values = [0] * (self.variables + 1)
        queue = []

        def value(lit):
            return values[abs(lit)] * (1 if lit > 0 else -1)

        def enqueue(lit):
            status = value(lit)
            if status < 0:
                return False
            if status == 0:
                values[abs(lit)] = 1 if lit > 0 else -1
                queue.append(lit)
            return True

        for lit in (*self.units, *assumptions):
            if not enqueue(lit):
                return True
        position = 0
        while position < len(queue):
            false_lit = -queue[position]
            position += 1
            watching = self.watches[false_lit]
            i = 0
            while i < len(watching):
                index = watching[i]
                clause = self.clauses[index]
                if clause[0] == false_lit:
                    clause[0], clause[1] = clause[1], clause[0]
                if clause[1] != false_lit:
                    raise InvalidProof('internal watch invariant')
                other = clause[0]
                if value(other) > 0:
                    i += 1
                    continue
                replacement = next((j for j in range(2, len(clause))
                                    if value(clause[j]) >= 0), None)
                if replacement is not None:
                    clause[1], clause[replacement] = clause[replacement], clause[1]
                    watching[i] = watching[-1]
                    watching.pop()
                    self.watches[clause[1]].append(index)
                    continue
                if not enqueue(other):
                    return True
                i += 1
        return False


def verify(variables, original, proof):
    if not isinstance(proof, list) or not proof or proof[-1] != []:
        raise InvalidProof('refutation must end in the empty clause')
    database = Database(variables, original)
    for index, clause in enumerate(proof):
        database.validate(clause)
        if not clause and index != len(proof) - 1:
            raise InvalidProof('empty clause before end of refutation')
        if not database.conflict(tuple(-lit for lit in clause)):
            raise InvalidProof(f'clause {index + 1} is not reverse-unit-propagation implied')
        database.add(clause)
    return len(proof)
