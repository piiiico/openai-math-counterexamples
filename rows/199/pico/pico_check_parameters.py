"""Pico's check for PR #25 (Family 199 parameter specializations, issue #24).

Independent of the packet's check.py, algebra.json and independent_oracle.py:
1. Parses the two multiplication tables displayed in the proof of Lemma
   res:base straight from the vendored 04-resolution.tex (right action
   a*u, a*l_i on Ce; left action l_i*a on eC) plus the stated images of u*
   on fC, (u, y+qx, z, v).
2. Specializes q in every field F2, F4, F8, F16 (the packet's moduli),
   builds the augmented chain complex Cf <- Ce <- Ce <- ... and the Hom
   complex fC -> eC -> eC -> ..., checks d o d = 0, and computes every
   homology dimension by rank over the field.
3. Requires (a) every per-degree dimension to equal the packet's
   evidence.json, all 30 cases, both complexes; (b) the stated
   classification: q=0 exact, q of order d first fails in degree d-1;
   q=0 dual dimension 2 in every degree >= 2.
4. Mutation: replace 1+q^{i+2} by 1+q^{i+1} in the TeX table; the first
   failing degree must move and (a) must fail.
Standard library only. Run from the repo root.
"""
import json, re, sys
from pathlib import Path

PKT = Path(__file__).resolve().parent.parent / 'parameters'
TEX = (PKT / 'sources' / '04-resolution.tex').read_text()
EVID = json.loads((PKT / 'evidence.json').read_text())
MOD = {2: 0b11, 4: 0b111, 8: 0b1011, 16: 0b10011}
DEG = {2: 1, 4: 2, 8: 3, 16: 4}


def mul(a, b, n):
    k, m, r = DEG[n], MOD[n], 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> k & 1:
            a ^= m
    return r


def pw(a, e, n):
    r = 1
    for _ in range(e):
        r = mul(r, a, n)
    return r  # pw(0,0)=1: l_0 = x + y


def inv(a, n):
    return pw(a, n - 2, n)


def rank(M, n):
    M = [row[:] for row in M]
    r = 0
    for c in range(len(M[0]) if M else 0):
        p = next((i for i in range(r, len(M)) if M[i][c]), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        iv = inv(M[r][c], n)
        M[r] = [mul(v, iv, n) for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c]:
                f = M[i][c]
                M[i] = [a ^ mul(f, b, n) for a, b in zip(M[i], M[r])]
        r += 1
    return r


def parse_entry(s):
    """'(1+q^{i+2})j' -> [('1+q', 'i+2', 'j')]; '\\ell_i' -> l_i."""
    s = s.strip().replace(' ', '')
    if s == '0':
        return []
    if s.startswith('\\ell_'):
        return [('', '0', 'x'), ('q', s[5:].strip('{}'), 'y')]
    m = re.fullmatch(r'(\(1\+q(?:\^\{?([^})]*)\}?)?\)|q(?:\^\{?([^}]*?)\}?)?)?([a-z])', s)
    assert m, s
    pre, e1, e2, b = m.groups()
    if not pre:
        return [('', '0', b)]
    if pre.startswith('('):
        return [('1+q', e1 or '1', b)]
    return [('q', e2 or '1', b)]


def tables(tex):
    out = []
    for arr in re.findall(r'\\begin\{array\}\{c\|c+\}(.*?)\\end\{array\}', tex, re.S):
        lines = [l.strip().rstrip('\\').rstrip('.').strip() for l in arr.split('\\\\')]
        head = [h.strip() for h in lines[0].split('&')]
        rows = {}
        for l in lines[1:]:
            l = l.replace('\\hline', '').strip()
            if not l:
                continue
            cells = l.split('&')
            rows[cells[0].replace(' ', '')] = [parse_entry(c) for c in cells[1:]]
        out.append((head[1:], rows))
    return out


def coef(kind, expr, q, i, n):
    e = eval(expr, {'i': i})
    v = pw(q, e, n)
    return 1 ^ v if kind == '1+q' else (v if kind == 'q' else 1)


def matrix(src, dst, entries, q, i, n):
    """columns = images of src basis, rows = dst basis coords."""
    M = [[0] * len(src) for _ in dst]
    for c, ent in enumerate(entries):
        for kind, expr, b in ent:
            M[dst.index(b)][c] ^= coef(kind, expr, q, i, n)
    return M


def matmul(A, B, n):
    return [[0 if not B else
             __import__('functools').reduce(lambda x, y: x ^ y,
                [mul(A[r][k], B[k][c], n) for k in range(len(B))], 0)
             for c in range(len(B[0]))] for r in range(len(A))]


def profiles(tex, n, q, top):
    (rb, rrows), (lb, lrows) = tables(tex)
    Ce, Cf = rb, ['f', 'u', 'v', 'n']
    eC, fC = lb, ['f', 't', 'j', 'n']
    du = matrix(Ce, Cf, rrows['au'], q, 0, n)
    dl = lambda i: matrix(Ce, Ce, rrows['a\\ell_i'], q, i, n)
    # u* on fC: (f,t,j,n) -> (u, y+qx, z, v), stated in the proof text
    assert '$(u,y+qx,z,v)$' in tex
    ustar = matrix(fC, eC, [[('', '0', 'u')], [('', '0', 'y'), ('q', '1', 'x')],
                            [('', '0', 'z')], [('', '0', 'v')]], q, 0, n)
    ll = lambda i: matrix(eC, eC, lrows['\\ell_ia'], q, i, n)
    # chain: d_1 = u, d_{k} = l_{k-2}; dims R_0=4, R_k=6
    d = {1: du, **{k: dl(k - 2) for k in range(2, top + 3)}}
    for k in range(1, top + 2):
        assert not any(any(r) for r in matmul(d[k], d[k + 1], n)), (n, q, k)
    rk = {k: rank(d[k], n) for k in d}
    chain = [4 - rk[1] - 1] + [6 - rk[k] - rk[k + 1] for k in range(1, top + 1)]
    # cochain: delta^0 = u*, delta^k = l_{k-1}*
    de = {0: ustar, **{k: ll(k - 1) for k in range(1, top + 2)}}
    for k in range(0, top + 1):
        assert not any(any(r) for r in matmul(de[k + 1], de[k], n)), (n, q, k)
    dr = {k: rank(de[k], n) for k in de}
    dual = [4 - dr[0]] + [6 - dr[k] - dr[k - 1] for k in range(1, top + 1)]
    return chain, dual


def order(q, n):
    if q == 0:
        return None
    d, v = 1, q
    while v != 1:
        v, d = mul(v, q, n), d + 1
    return d


def run(tex, quiet=False):
    bad = 0
    for case in EVID['cases']:
        n, q, top = case['field_size'], case['q_bits'], case['maximum_degree']
        chain, dual = profiles(tex, n, q, top)
        if chain != case['chain_homology_dimensions'] or dual != case['dual_cohomology_dimensions']:
            bad += 1
            continue
        d = order(q, n)
        assert d == case['order']
        first = next((k for k, h in enumerate(chain) if h), None)
        if d is None:
            ok = first is None and all(h == 2 for h in dual[2:])
        else:
            ok = first == d - 1
        bad += not ok
    return bad


if __name__ == '__main__':
    assert len(EVID['cases']) == 30
    bad = run(TEX)
    print(f'TeX tables vs evidence.json: {30 - bad}/30 cases agree per degree (chain + dual); classification holds' if not bad else f'FAIL {bad}')
    mtex = TEX.replace('(1+q^{i+2})j', '(1+q^{i+1})j', 1)
    assert mtex != TEX
    mbad = run(mtex)
    print(f'mutation 1+q^(i+2) -> 1+q^(i+1): {mbad}/30 cases now disagree (must be > 0)')
    sys.exit(0 if bad == 0 and mbad > 0 else 1)
