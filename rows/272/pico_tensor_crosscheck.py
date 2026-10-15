"""Pico float cross-check of tensor/ (PR #2). Run from rows/272 with numpy installed.

Builds Z from the manuscript definitions (geometry.tex: orthonormal U,V, S, R, Phi2 o Phi1 = R^dagger o S o T),
importing nothing from tensor/, then checks 4(D x D) Z (D x D) against the saved integer Z0, rank, PPT,
and Z(xhat x xhat) at the 20 points in output.txt against 20 random directions.
"""
import json, re, itertools, numpy as np
P=json.load(open('rigorous/pencil.json'))['matrices']; M=[np.array(m,float) for m in P]
cert=json.load(open('tensor/certificate.json')); Z0=np.array(cert['choi'],float)
sym=list(itertools.combinations_with_replacement(range(4),2)); ext=list(itertools.combinations(range(4),2))
e=np.eye(4); r2=np.sqrt(2)
U=np.zeros((16,10)); V=np.zeros((16,6))
for c,(i,j) in enumerate(sym): U[:,c]=np.kron(e[i],e[j]) if i==j else (np.kron(e[i],e[j])+np.kron(e[j],e[i]))/r2
for c,(i,j) in enumerate(ext): V[:,c]=(np.kron(e[i],e[j])-np.kron(e[j],e[i]))/r2
Lu=[[M[i].T@M[j] for j in range(4)] for i in range(4)]
def L(A): return sum(A[i,j]*Lu[i][j] for i in range(4) for j in range(4))
def LL(X):  # (L⊗L) on Mat4⊗Mat4, X index (i*4+k, j*4+l)
    out=np.zeros((16,16))
    for i in range(4):
        for j in range(4):
            for k in range(4):
                for l in range(4):
                    v=X[i*4+k,j*4+l]
                    if v: out+=v*np.kron(Lu[i][j],Lu[k][l])
    return out
K=np.zeros((6,6))
for c,(i,j) in enumerate(ext):
    k,l=[t for t in range(4) if t not in (i,j)]
    perm=(i,j,k,l); s=(-1)**sum(perm[a]>perm[b] for a in range(4) for b in range(a+1,4))
    K[ext.index((k,l)),c]=s
def S(A): return V.T@LL(U@A@U.T)@V
def R(A): return K@S(A).T@K.T
E10=lambda i,j: np.outer(np.eye(10)[i],np.eye(10)[j])
Smat=np.array([S(E10(i,j)).ravel() for i in range(10) for j in range(10)]).T  # 36x100
Rmat=np.array([R(E10(i,j)).ravel() for i in range(10) for j in range(10)]).T
Radj=Rmat.T  # real => Hilbert-Schmidt adjoint
def F(A): return (Radj@(Smat@A.T.ravel())).reshape(10,10)  # R† ∘ S ∘ T
Z=sum(np.kron(E10(i,j),F(E10(i,j))) for i in range(10) for j in range(10))
d=np.array([1 if i==j else r2 for (i,j) in sym]); D=np.diag(d)
Zc=4*np.kron(D,D)@Z@np.kron(D,D)
print('max|4(D⊗D)Z(D⊗D) - Z0| =',np.abs(Zc-Z0).max(),' max|Z0|=',np.abs(Z0).max())
print('source-normalized Z[0,0] =',Z[0,0])
w=np.linalg.eigvalsh(Z); print('Z eig min/max',w.min(),w.max(),' rank(tol 1e-9*max)=',(w>1e-9*w.max()).sum())
PT=Z.reshape(10,10,10,10).transpose(0,3,2,1).reshape(100,100)
print('output partial transpose == Z :',np.abs(PT-Z).max())
pts=[]
for line in open('output.txt'):
    m=re.match(r'\s*t = \((.*)\)',line)
    if m: pts.append([1.0]+[float(re.match(r'([+-][\d.]+)',x.strip()).group(1)) for x in m.group(1).split(',')])
print('points',len(pts))
def xh(x): x=np.array(x); return np.array([x[i]**2 if i==j else r2*x[i]*x[j] for (i,j) in sym])
def rel(x): v=np.kron(xh(x),xh(x)); return np.linalg.norm(Z@v)/(np.linalg.norm(Z,2)*np.linalg.norm(v))
print('max rel |Z(x̂⊗x̂)| at 20 points:',max(rel(p) for p in pts))
rng=np.random.default_rng(0); print('min rel at 20 random x (control):',min(rel([1]+list(rng.normal(size=3))) for _ in range(20)))
print('rank M(x) smallest sv at points:',max(np.linalg.svd(sum(p[k]*M[k] for k in range(4)),compute_uv=False)[-1] for p in pts))
