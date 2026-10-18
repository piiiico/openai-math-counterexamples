# Pico's independent check of the 049 integral packet: plain Python ints, maps typed from PROOF.md statement only.
import random, itertools
def xys(h,u,v,w): return u**3+h*v, -u**2+h*w, 2*u**3*v+3*u**4*w+h*(v*v-3*u*u*w*w)+h*h*w**3
def p(x,y,s): return -2*s*s*x+3*s*y*y-3*s**3*y
def F(h,u,v,w): x,y,s=xys(h,u,v,w); return h-p(x,y,s)-1
def ab(x,y,s): a=1+2*s*s*x+4*s**5; return a,(3*s**3-3*s*y)*(1+2*s*s*x)-4*s**4*y*y
def to3(h,u,v,w): x,y,s=xys(h,u,v,w); a,b=ab(x,y,s); return x+s**3, y-s*s, a*u+b*(v+u*w)
def from3(X,Y,T):
  s=X*X+Y**3; x=X-s**3; y=Y+s*s; h=1+p(x,y,s); a,b=ab(x,y,s)
  u=h*T-b*x; g=y*T+a*x; w=a*(1+b*y)*(y+u*u)+b*b*(s-h*g*g+2*u*y*g); return h,u,g-u*w,w
# (1) A^3 -> fibre -> A^3 over Z at random integer points; image lies on F=0
random.seed(1)
for _ in range(200):
  X,Y,T=(random.randint(-50,50) for _ in range(3)); q=from3(X,Y,T)
  assert F(*q)==0 and to3(*q)==(X,Y,T)
# (2) over F_p: fibre has exactly p^3 points and fibre->A^3->fibre is identity on each
for P in (2,3,5,7):
  pts=[q for q in itertools.product(range(P),repeat=4) if F(*q)%P==0]
  imgs={tuple(c%P for c in to3(*q)) for q in pts}
  ok=all(tuple(c%P for c in from3(*to3(*q)))==q for q in pts)
  print(f"F_{P}: fibre points {len(pts)} (p^3={P**3}), images {len(imgs)}, round-trip identity {ok}")
# (3) integral critical point: F and exact partials via forward differences of polynomial? use symbolic-free central check: integer polynomial -> exact derivative by finite difference with dual numbers
class D:
  def __init__(s,a,b=0): s.a,s.b=a,b
  def __add__(s,o): o=o if isinstance(o,D) else D(o); return D(s.a+o.a,s.b+o.b)
  __radd__=__add__
  def __sub__(s,o): o=o if isinstance(o,D) else D(o); return D(s.a-o.a,s.b-o.b)
  def __rsub__(s,o): return D(o)-s
  def __mul__(s,o): o=o if isinstance(o,D) else D(o); return D(s.a*o.a,s.a*o.b+s.b*o.a)
  __rmul__=__mul__
  def __neg__(s): return D(-s.a,-s.b)
  def __pow__(s,n):
    r=D(1)
    for _ in range(n): r=r*s
    return r
Pt=(2,1,-1,1); grads=[]
for i in range(4):
  args=[D(c,1 if j==i else 0) for j,c in enumerate(Pt)]; r=F(*args); grads.append(r.b); val=r.a
print("F(2,1,-1,1) =",val," grad =",grads)
# negative control: the source's own point (2,0,-1/2,1/2) is not integral; a moved point must not be critical
args=[D(c,1 if j==0 else 0) for j,c in enumerate((2,1,-1,2))]; print("moved point (2,1,-1,2) dF/dh =",F(*args).b)
