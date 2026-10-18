# Requires python-sat (tested python-sat 1.9.dev16: CaDiCaL 1.5.3 and Glucose 4). Usage: python pico_sat_crosscheck.py [down|pure|noboundary|comp|paircount]
# Pico's independent encoding of TenSystem (Labels.lean:13-22), no symmetry breaking, pysat cardinality encodings.
import itertools, sys
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical153, Glucose4
L=range(10); pool=IDPool()
tri=[frozenset(c) for c in itertools.combinations(L,3)]; tet=[frozenset(c) for c in itertools.combinations(L,4)]
T=lambda u: pool.id(('T',tuple(sorted(u)))); Q=lambda s: pool.id(('Q',tuple(sorted(s))))
cnf=CNF(); [T(u) for u in tri]; [Q(s) for s in tet]
drop=sys.argv[1] if len(sys.argv)>1 else ''
cnf.append([Q(s) for s in tet])  # nonempty
for s in tet:
  comp=frozenset(L)-s
  for u in itertools.combinations(s,3):
    u=frozenset(u)
    if drop!='down': cnf.append([-Q(s),T(u)])
    if drop!='noboundary': cnf.append([-Q(s)]+[Q(u|{x}) for x in L if x not in s])
  for u in itertools.combinations(sorted(comp),3):
    u=frozenset(u); v=comp-u
    if drop!='comp':
      cnf.append([-Q(s),T(u),T(v)]); cnf.append([-Q(s),-T(u),-T(v)])
  for p in itertools.combinations(sorted(comp),2):
    p=frozenset(p); lits=[T(p|{w}) for w in comp-p]
    if drop!='paircount':
      for cl in CardEnc.equals(lits=lits,bound=2,vpool=pool,encoding=EncType.seqcounter).clauses: cnf.append([-Q(s)]+cl)
for u in tri:
  if drop!='pure': cnf.append([-T(u)]+[Q(u|{x}) for x in L if x not in u])
for S in (Cadical153,Glucose4):
  with S(bootstrap_with=cnf.clauses) as s: r=s.solve(); print(S.__name__, drop or 'full', 'SAT' if r else 'UNSAT', len(cnf.clauses))
