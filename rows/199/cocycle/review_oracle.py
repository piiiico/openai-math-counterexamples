"""Independent review oracle; source transcription, bit polynomials, pushed differential.
No imports of the packet checker. Independent exact finite computation, not a formal proof.
Source: OpenAI math@1581d4cbdd69a0faf34b2089614fe2a814316a6a,
03-algebra.tex:12-34,80-95,170-186 and 09-cochain.tex:19-38.
All source data below were transcribed directly from the pinned TeX by the
separately tasked AI reviewer, not imported from data.json or the main checker.
"""
from collections import defaultdict
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--packet', type=Path, default=Path(__file__).resolve().parent)
parser.add_argument('--mutate', choices=['cochain'])
args = parser.parse_args()

PACKET=args.packet
# Typed directly from 09-cochain.tex:19-38, separate from JSON and check.py.
GROUPS={
2: '''EuNT EyZX FNtU JtXZ NtEU NtXV XzJT ZxEY tEun tXuf
 tXvn tXzj tuFn tuNf tvNn uFNT vNNT vtJu xEyz zJtx''',
1: '''EuUE EuVX EvVE ExXE EyYE EzZE FNnF FVvF FVxU FtTF
 FtYU Ftun Ftxj JFtX JNtZ JUyX JVyZ JjEE JjTT JjXX
 NFtU NNtV NUyU NVyV NjJN NjZV NnNN NnVV Ntuf Ntvn
 Ntzj TtEE TtXX UuFF UuUU UvNF UvVU UxXU Uyun Uyxj
 UzZU VvNN VvVV VxEU VxXV Vyuf Vyvn Vyzj VzZV XxEE
 XxXX YuFT YuUY YvNT YvVY YxXY YyEE YyJJ YyTT YyXX
 YyYY YyZZ YzZY ZxXZ ZzEE ZzJJ ZzTT ZzXX jJFF jJUU
 jJjj jJnn jYyj jZvn jZzj nNFF nNUU ntTn tJjt tTNN
 tTVV tTtt tYyt tZzt tzJn uFVX uFty uNFT uNUY uNte
 uUyy uVye ujJu vNUE vNVX vNty vVyy vtTv xEuv xJFT
 xJUY xJjx xJte xTtx xXuu xXvv xXyy xXzz xYyx xZye
 xZzx xuFv xuNu xvNv yxJu yzJv zJNT zJVY zYyz zZuu
 zZvv zZyy zZzz''',
3: 'EyJT JtEY tEyj tyJf',
0: '''JNjX JVzX NNjU NVzU NjYU Njun Njxj Ntxt TNtX TVyX
 Vyxt VzYU Vzun Vzxj YuNJ YuVZ jYun juNn jxJn txTn
 uNNJ uNVZ uNjy uVzy xJNJ xJVZ xTNT xTVY yxTv zYuv
 zuNv zxJv'''
}
P={tuple(w[:3]): (w[3],1<<d) for d, text in GROUPS.items() for w in text.split()}
require(len(P)==179, 'source transcription must contain 179 distinct inputs')
raw=json.loads((PACKET/'data.json').read_text())
require(len(raw['cochain']) == 179 and P == {tuple(r['inputs']):(r['output'],1<<r['q_degree']) for r in raw['cochain']}, 'cochain transcription mismatch')
print('Source cochain transcription: 179/179 exact matches')

# Polynomial coefficients use binary integers (bit i = coefficient of q^i).
def times(a,b):
    v=0
    while b:
        if b&1: v ^= a
        a <<= 1
        b >>= 1
    return v

def put(d,k,c):
    d[k] ^= c

def nonzero(d):
    return {k:v for k,v in d.items() if v}

C='efxyzuvtjn'
B=C+C.upper()
R=B.replace('e','').replace('f','')
corners={**{a:'ee' for a in 'exyz'}, **{a:'ef' for a in 'uv'},
         **{a:'fe' for a in 'tj'}, **{a:'ff' for a in 'fn'}}
degrees={'e':0,'f':0,'u':1,'t':1,'x':2,'y':2,'n':2,'v':3,'j':3,'z':4}
require([{ 'name':a,'left':corners[a][0], 'right':corners[a][1], 'degree':degrees[a]} for a in C] == raw['basis'], 'basis/corners/grading transcription mismatch')
source_products={('x','y'):{'z':2},('y','x'):{'z':1},
('x','u'):{'v':1},('y','u'):{'v':1},('t','x'):{'j':1},('t','y'):{'j':4},
('u','t'):{'y':1,'x':2},('v','t'):{'z':2},('u','j'):{'z':1},
('t','u'):{'n':3},('n','t'):{'j':2},('u','n'):{'v':1}}
require(len(raw['products']) == 12 and source_products == {tuple(r['inputs']):{v:sum(1<<n for n in ns) for v,ns in r['output'].items()} for r in raw['products']}, 'base products transcription mismatch')
require(len(raw['z_support']) == 9 and set(raw['z_support'])==set('uvtEXYZUV'), 'z support transcription mismatch')
print('Source basis, corners, degrees, 12 products and z support: exact matches')
M=defaultdict(int)
for (a,b),v in source_products.items():
    for c,k in v.items(): M[a,b,c]=k
for a in C:
    M[corners[a][0],a,a]=1
    M[a,corners[a][1],a]=1
# Push each C structure coefficient into the two dual-action tables.
for (a,b,c),k in list(M.items()):
    M[b,c.upper(),a.upper()]=k
    M[c.upper(),a,b.upper()]=k
by_pair=defaultdict(list)
by_value=defaultdict(list)
for (a,b,c),k in M.items():
    by_pair[a,b].append((c,k))
    if a in R and b in R: by_value[c].append((a,b,k))

if args.mutate == 'cochain':
    P['t', 'y', 'J'] = ('f', 4)
    print('Applied cochain mutation: p(t,y,J) = q^2 f')

# Push all nonzero p terms into a sparse coefficient table for delta(p).
# No per-quadruple gather routine and no shared arithmetic with check.py.
delta=defaultdict(int)
for (a,b,c),(v,k) in P.items():
    for l in R:
        for out,m in by_pair[l,v]: put(delta,(l,a,b,c,out),times(k,m))
        for out,m in by_pair[v,l]: put(delta,(a,b,c,l,out),times(k,m))
    for l,r,m in by_value[a]: put(delta,(l,r,b,c,v),times(k,m))
    for l,r,m in by_value[b]: put(delta,(a,l,r,c,v),times(k,m))
    for l,r,m in by_value[c]: put(delta,(a,b,l,r,v),times(k,m))
residual = nonzero(delta)
if residual:
    key = min(residual)
    print('RESULT: FAIL: Hochschild differential at', key, 'q-polynomial bits:', residual[key])
    raise SystemExit(1)
print('Independent pushed Hochschild differential: all coefficients zero on 18^4 words')

# Split by exact H power (0 or 1), computing full symbolic boundary.
boundary=defaultdict(int)
support=set('uvtEXYZUV')
for (a,b,w),(v,k) in P.items():
    for out,m in by_pair[v,w.swapcase()]:
        put(boundary,(a,b,out,int(w.isupper())),times(k,m))
for a,b in product(R,repeat=2):
    for out,m in by_pair[a,b]:
        if b in support: put(boundary,(a,b,out,1),times(2,m))
        if out in support: put(boundary,(a,b,out,1),times(2,m))
        if a in support: put(boundary,(a,b,out,1-int(b.isupper())),times(2,m))
residual = nonzero(boundary)
if residual:
    key = min(residual)
    print('RESULT: FAIL: twisted boundary at', key, 'q-polynomial bits:', residual[key])
    raise SystemExit(1)
print('Independent exact H-coefficient boundary oracle: all 324 pairs zero')

# Show a pair where the H^-1 is essential and remains a nonzero constant.
a,b='u','N'
contributions=[]
for (u,v,w),(out,k) in P.items():
    if (u,v)==(a,b):
        for result,m in by_pair[out,w.swapcase()]:
            contributions.append((w,result,times(k,m),int(w.isupper())))
print('(u,N) nonzero LHS summands (w, output, q-polynomial bits, H degree):',contributions)
print('u*N =',by_pair['u','N'])
print('RESULT: holds — independent source transcription and exact finite identity oracle')
print('Oracle sha256',hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
