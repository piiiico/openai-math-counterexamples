"""Independent exponent-vector/SymPy GF(7) replay of Family 095.
Shared input: certificate.json; no import of the main checker.
Run: python independent_check.py /path/to/certificate.json
Alexander Richard Towell, with substantial OpenAI Codex assistance. MIT.
Finite modular calculation only; no characteristic-zero/real lifting claim.
"""
import json
import hashlib
from pathlib import Path
import sys
from sympy import GF
from sympy.polys.matrices import DomainMatrix

F = GF(7)
cert = json.loads(Path(sys.argv[1]).read_text())
weights = [0, 5, 1, 9, 2, 8, 4, 6]
point = [1, 6, 6, 0, 3, 0, 2, 5]
pivots = [[0, 2] if i in (0, 8) else [0, 1] for i in range(10)]
velocity = [2,0,0,0,3,6,1,4,1,6,0,3,0,5,2,2,0,0,4,0,6] + [0]*14


def demand(condition, message):
    if not condition:
        raise ValueError(message)


demand(cert['field'] == 7 and cert['weights'] == weights, 'source field/weights')
demand(cert['point'] == point, 'source point')
demand(cert['pivot_columns'] == [[j+1 for j in s] for s in pivots], 'source pivots')
demand(cert['tangent_moments'] == velocity, 'source tangent moments')


def matrix(rows):
    return DomainMatrix.from_list(rows, F)


def integer_rows(a):
    return [[int(x) for x in row] for row in a.to_list()]


def fingerprint(a):
    payload={'rows':a.shape[0],'columns':a.shape[1],'entries':integer_rows(a)}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def zero(a):
    return not any(x for row in a.to_list() for x in row)


def compositions(total, slots):
    if slots == 1:
        yield (total,)
    else:
        for first in range(total+1):
            for tail in compositions(total-first, slots-1):
                yield (first,) + tail


def indices(e):
    return tuple(i for i, n in enumerate(e) for _ in range(n))


def monomials(degree):
    return sorted(compositions(degree, 8), key=indices)


def wt(e):
    return sum(a*b for a,b in zip(e, weights)) % 10


def add_exp(a, b):
    return tuple(x+y for x,y in zip(a,b))


def evaluate(e):
    answer = 1
    for x, n in zip(point, e):
        answer = answer * pow(x, n, 7) % 7
    return answer


Q, V = monomials(2), monomials(4)
qb = [[e for e in Q if wt(e) == i] for i in range(10)]
vb = [[e for e in V if wt(e) == i] for i in range(10)]
tangent = dict(zip(vb[0], velocity))
at = {e:i for i,e in enumerate(Q)}


def mom(e):
    return (1 + evaluate(e)) % 7 if wt(e) == 0 else 0


T = matrix([[mom(add_exp(e,f)) for f in Q] for e in Q])
T1 = matrix([[tangent.get(add_exp(e,f), 0) for f in Q] for e in Q])
L = [i for i,e in enumerate(Q) if e[0]]
demand(T.rank() == 20, 'rank T')
demand(int(T.extract(L,L).det()) == 6, 'det T|L')


def frame(row_matrix, chosen):
    """Canonical null frame from arbitrary invertible selected column block."""
    n = row_matrix.shape[1]
    free = [i for i in range(n) if i not in chosen]
    solved = -(row_matrix.extract(range(row_matrix.shape[0]), chosen).inv()
               * row_matrix.extract(range(row_matrix.shape[0]), free))
    sr = integer_rows(solved)
    rows = [[0]*len(free) for _ in range(n)]
    for j,k in enumerate(free):
        rows[k][j] = 1
    for j,k in enumerate(chosen):
        rows[k] = sr[j]
    return matrix(rows)


def derivative(local, opposite, basis, chosen, equations):
    selected = T.extract(equations, [local[k] for k in chosen])
    rhs = T1.extract(equations, local) * basis
    sr = integer_rows(-(selected.inv() * rhs))
    rows = [[0]*basis.shape[1] for _ in local]
    for j,k in enumerate(chosen):
        rows[k] = sr[j]
    return matrix(rows)


J, Jdot, N, Ndot = [], [], [], []
for i, mon in enumerate(qb):
    c = matrix([[1]*len(mon), [evaluate(e) for e in mon]])
    b = frame(c, pivots[i])
    demand(integer_rows(b.transpose()) == cert['basis_columns'][i], 'displayed J basis '+str(i))
    J.append(b)
for i, mon in enumerate(qb):
    local = [at[e] for e in mon]
    opp = (-i) % 10
    eq = [at[qb[opp][k]] for k in pivots[opp]]
    Jdot.append(derivative(local, opp, J[i], pivots[i], eq))
    lrows = [at[e] for e in qb[opp] if e[0]]
    if lrows:
        chosen = [next(j for j,e in enumerate(mon) if e[0])]
        N.append(frame(T.extract(lrows, local), chosen))
        Ndot.append(derivative(local, opp, N[i], chosen, lrows))
    else:
        N.append(DomainMatrix.eye(len(mon), F).to_dense())
        Ndot.append(DomainMatrix.zeros((len(mon), len(mon)), F).to_dense())


def global_frame(blocks):
    cols = sum(b.shape[1] for b in blocks)
    rows = [[0]*cols for _ in Q]
    offset = 0
    for mon,b in zip(qb, blocks):
        for e,row in zip(mon, integer_rows(b)):
            rows[at[e]][offset:offset+b.shape[1]] = row
        offset += b.shape[1]
    return matrix(rows)


j, jd, n, nd = map(global_frame, (J,Jdot,N,Ndot))
demand(zero(T*j), 'kernel')
demand(zero(j.transpose()*T1*j), 'tangency')
demand(zero(T*jd + T1*j), 'differentiated kernel')
demand(zero(T.extract(L, range(36))*n), 'H0')
demand(zero(T.extract(L, range(36))*nd + T1.extract(L, range(36))*n), 'differentiated H0')


def polynomials(b, mon):
    return [{e:x for e,x in zip(mon,col) if x} for col in integer_rows(b.transpose())]


JP, JDP, NP, NDP = [[polynomials(b,mon) for b,mon in zip(bs,qb)] for bs in (J,Jdot,N,Ndot)]


def multiply(a,b):
    result = {}
    for e,x in a.items():
        for f,y in b.items():
            ef = add_exp(e,f)
            result[ef] = (result.get(ef,0) + x*y) % 7
    return result


def plus(a,b):
    keys = set(a).union(b)
    return {e:(a.get(e,0)+b.get(e,0)) % 7 for e in keys}


def polynomial_matrix(cols, rows):
    return matrix([[c.get(e,0) for c in cols] for e in rows])


def retain(count, excluded):
    return [i for i in range(count) if i+1 not in excluded]


answer = []
for w in range(10):
    g1, g2, d, dd = [], [], [], []
    for i in range(10):
        k = (w-i) % 10
        for a,u in enumerate(JP[i]):
            for b,v in enumerate(JP[k]):
                if (i,a) <= (k,b):g1.append(multiply(u,v))
            for coordinate in range(1,8):
                e = tuple(int(t == 0)+int(t == coordinate) for t in range(8))
                if wt(e) == k:g2.append(multiply(u,{e:1}))
            for b,v in enumerate(NP[k]):
                d.append(multiply(u,v))
                dd.append(plus(multiply(JDP[i][a],v),multiply(u,NDP[k][b])))
    g1 = polynomial_matrix(g1,[e for e in vb[w] if e[0] == 0])
    g2 = polynomial_matrix(g2,[e for e in vb[w] if e[0] == 1])
    d, dd = polynomial_matrix(d,vb[w]), polynomial_matrix(dd,vb[w])
    blank = DomainMatrix.zeros(d.shape,F).to_dense()
    border = d.hstack(blank).vstack(dd.hstack(d))
    ranks = [b.rank() for b in (g1,g2,d,border)]
    record = {'weight':w, 'ranks':ranks, 'matrix_hashes':{name:fingerprint(b) for name,b in [('G1',g1),('G2',g2),('D',d),('D1',dd)]}}
    if w <= 5:
        for name,b in (('G1',g1),('G2',g2),('D',d)):
            spec = cert[name][w]
            rr = retain(b.shape[0], spec.get('omit_rows',[]))
            cc = retain(b.shape[1], spec.get('omit_columns',[]))
            demand(len(rr) == len(cc) == spec['size'], name+' size')
            demand(int(b.extract(rr,cc).det()) == spec['det'], name+' determinant')
        spec = cert['D'][w]
        r = retain(d.shape[0], spec['omit_rows'])
        s = retain(d.shape[1], spec['omit_columns'])
        rp, sp = [[x-1 for x in spec[k]] for k in ('extra_rows','extra_columns')]
        einv = d.extract(r,s).inv()
        left = DomainMatrix.eye(len(rp),F).to_dense()
        right = DomainMatrix.eye(len(sp),F).to_dense()
        z = (dd.extract(rp,sp)-dd.extract(rp,s)*einv*d.extract(r,sp)
             -d.extract(rp,s)*einv*dd.extract(r,sp)
             +d.extract(rp,s)*einv*dd.extract(r,s)*einv*d.extract(r,sp))
        demand(integer_rows(z) == spec['corner'], 'corner entries')
        demand(int(z.det()) == spec['corner_det'], 'corner determinant')
        br = r + [d.shape[0]+x for x in r+rp]
        bc = s + sp + [d.shape[1]+x for x in s]
        direct_det = int(border.extract(br,bc).det())
        predicted = ((-1)**(len(r)*len(rp))*spec['det']**2*spec['corner_det']) % 7
        demand(direct_det == predicted != 0, 'direct bordered determinant')
        record.update(corner=integer_rows(z),direct_bordered_det=direct_det)
    answer.append(record)
totals = [sum(x['ranks'][j] for x in answer) for j in range(4)]
demand(totals == [136,84,302,623], 'rank totals')
print(json.dumps({'method':'exponent vectors; SymPy DomainMatrix GF(7)', 'seed_rank':T.rank(),
                  'L_det':int(T.extract(L,L).det()),'seed_matrix_hashes':{'T':fingerprint(T),'T1':fingerprint(T1)},'weights':answer,'rank_totals':totals},indent=2))
