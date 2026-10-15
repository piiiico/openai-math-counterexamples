"""Pico cross-check for PR #4 (run from rows/272: python pico_channel_crosscheck.py channel/certificate.json). Uses only the saved certificate + numpy; imports nothing from channel/."""
import json, sys, numpy as np
c=json.load(open(sys.argv[1])); n=c['dimension']; D=c['denominator']
def mat(key):
    M=[[0]*(n*n) for _ in range(n*n)]
    for r,s,v in c[key]['entries']: M[r][s]=v
    return M
J=mat('channel_choi'); S=mat('square_choi')
def blocks(M):  # input-first: B[i][j] = n x n output block
    return [[[[M[i*n+k][j*n+l] for l in range(n)] for k in range(n)] for j in range(n)] for i in range(n)]
for name,order in (('input-first',0),('output-first',1)):
    ok=True
    for i in range(n):
        for j in range(n):
            t=sum(J[(i*n+k) if order==0 else (k*n+i)][(j*n+k) if order==0 else (k*n+j)] for k in range(n))
            if t!=(D if i==j else 0): ok=False
    print(name,'Tr_out J = D*I exactly:',ok)
B=blocks(J)
# square: Phi^2(E_ij) = sum_kl Phi(E_ij)[k,l] Phi(E_kl), exact ints (scale D^2)
S2=[[0]*(n*n) for _ in range(n*n)]
for i in range(n):
  for j in range(n):
    Bij=B[i][j]
    acc=[[0]*n for _ in range(n)]
    for k in range(n):
      for l in range(n):
        v=Bij[k][l]
        if v:
          Bkl=B[k][l]
          for a in range(n):
            ra=acc[a]; rb=Bkl[a]
            for b in range(n): ra[b]+=v*rb[b]
    for a in range(n):
      for b in range(n): S2[i*n+a][j*n+b]=acc[a][b]
print('square Choi rebuilt by composition == saved square_choi (exact ints):', S2==S)
def pt(M):  # transpose the output factor
    return [[M[(r//n)*n+(s%n)][(s//n)*n+(r%n)] for s in range(n*n)] for r in range(n*n)]
for nm,M,sc in (('channel',J,D),('square',S,D*D)):
    A=np.array(M,dtype=float)/sc
    for lab,X in (('Choi',A),('PT',np.array(pt(M),dtype=float)/sc)):
        w=np.linalg.eigvalsh(X); print(nm,lab,'min eig %.2e max %.2e rank(>1e-9 max) %d'%(w.min(),w.max(),(w>1e-9*w.max()).sum()))
