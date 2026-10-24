# Pico independent check for PR #28: exact Q(sqrt3) dual numbers at rational t, no sympy, no J identity.
from fractions import Fraction as Fr
import random, math
class K:  # a + b*sqrt3
    def __init__(s,a,b=0): s.a,s.b=Fr(a),Fr(b)
    def __add__(s,o): o=o if isinstance(o,K) else K(o); return K(s.a+o.a,s.b+o.b)
    __radd__=__add__
    def __neg__(s): return K(-s.a,-s.b)
    def __sub__(s,o): return s+(-(o if isinstance(o,K) else K(o)))
    def __mul__(s,o): o=o if isinstance(o,K) else K(o); return K(s.a*o.a+3*s.b*o.b,s.a*o.b+s.b*o.a)
    __rmul__=__mul__
    def inv(s): n=s.a*s.a-3*s.b*s.b; return K(s.a/n,-s.b/n)
    def z(s): return s.a==0 and s.b==0
class D:  # dual over K
    def __init__(s,x,e=K(0)): s.x,s.e=(x if isinstance(x,K) else K(x)),(e if isinstance(e,K) else K(e))
    def __add__(s,o): o=o if isinstance(o,D) else D(o); return D(s.x+o.x,s.e+o.e)
    __radd__=__add__
    def __neg__(s): return D(-s.x,-s.e)
    def __sub__(s,o): return s+(-(o if isinstance(o,D) else D(o)))
    def __mul__(s,o): o=o if isinstance(o,D) else D(o); return D(s.x*o.x,s.x*o.e+s.e*o.x)
    __rmul__=__mul__
    def inv(s): i=s.x.inv(); return D(i,-(s.e*i*i))
S3=K(0,1)
def run(base,t0,wc=-2,flip=True):
    t=D(K(t0),K(1)); den=(1+t*t).inv(); u=(D(1)-t*t)*den; v=2*t*den
    fac=(1+K(t0)*K(t0))*K(Fr(1,2))
    rots=[(u,v),(u,-v) if flip else (u,v),(D(1),D(0))]; ws=[1,1,wc]
    P=[];dP=[];W=[]
    for (c,s),w in zip(rots,ws):
        for (qx,qy) in base:
            x=c*D(qx)-s*D(qy); y=s*D(qx)+c*D(qy)
            P.append([K(1),x.x,y.x]); dP.append([K(0),x.e*fac,y.e*fac]); W.append(w)
    M=lambda A,B:[[sum((K(w)*a[i]*b[j] for w,a,b in zip(W,A,B)),K(0)) for j in range(3)] for i in range(3)]
    return M(P,P),M(dP,P),M(dP,dP),P
tri=[(K(1),K(0)),(K(Fr(-1,2)),S3*K(Fr(1,2))),(K(Fr(-1,2)),-(S3*K(Fr(1,2))))]
sq=[(K(1),K(0)),(K(0),K(1)),(K(-1),K(0)),(K(0),K(-1))]
def ok(base,c,**kw):
    bad=0
    for _ in range(20):
        t0=Fr(random.randint(1,999),random.randint(1000,5000))
        M0,M1,M2,_=run(base,t0,**kw); tgt=[[0,0,0],[0,2*c,0],[0,0,2*c]]
        bad+=sum(not M0[i][j].z() or not M1[i][j].z() or not (M2[i][j]-K(tgt[i][j])).z() for i in range(3) for j in range(3))
    return bad
random.seed(172)
print("triangle c=3/2 bad entries:",ok(tri,Fr(3,2)))
print("square c=2 bad entries:",ok(sq,2))
print("NEG central weight -1:",ok(tri,Fr(3,2),wc=-1))
print("NEG same rotation:",ok(tri,Fr(3,2),flip=False))
iso=[(K(1),K(0)),(K(-1),K(1)),(K(0),K(-1))]  # centered, not isotropic
print("NEG non-isotropic base:",ok(iso,Fr(3,2)))
# distinctness at Liouville t = sum 10^-m!
tL=sum(10.0**-math.factorial(m) for m in range(1,5)); th=2*math.atan(tL)
pts=[(math.cos(a+b),math.sin(a+b)) for a in (th,-th,0) for b in (0,2*math.pi/3,4*math.pi/3)]
dmin=min(math.dist(p,q) for i,p in enumerate(pts) for q in pts[i+1:])
print(f"Liouville t={tL:.6f} theta={th:.4f} < pi/3: {th<math.pi/3}; min pairwise dist over 36 pairs = {dmin:.4f}")
