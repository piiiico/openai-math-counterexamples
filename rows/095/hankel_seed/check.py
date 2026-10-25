"""Reconstruct Appendix A's finite Hankel calculation over F7.

Alexander Richard Towell, with substantial OpenAI Codex assistance. MIT.
Scope: source-pinned modular arithmetic, not the real PSD lifting/nonliftability proof.
"""
import argparse
from dataclasses import dataclass
import hashlib
import copy
from itertools import combinations, combinations_with_replacement
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent

Monomial = tuple[int, ...]
Polynomial = dict[Monomial, int]
Matrix = list[list[int]]


@dataclass(frozen=True)
class Model:
    weights: tuple[int, ...]
    quadratics: list[Monomial]
    quartics: list[Monomial]
    blocks: list[list[Monomial]]
    T: Matrix
    T1: Matrix
    L: list[int]
    J: list[list[Polynomial]]
    Jp: list[list[Polynomial]]
    N: list[list[Polynomial]]
    Np: list[list[Polynomial]]
    field: int

    def wt(self, monomial: Monomial) -> int:
        return sum(self.weights[j] for j in monomial) % 10



def require(ok,message):
    if not ok:raise ValueError(message)


def transpose(a):
    return [list(x) for x in zip(*a)]


def mm(a,b,p):
    require(bool(a) and bool(b) and len(a[0])==len(b),'matrix product shape')
    return [[sum(x*y for x,y in zip(row,col))%p for col in zip(*b)] for row in a]


def combine(a,b,p,sign=1):
    require(len(a)==len(b) and all(len(x)==len(y) for x,y in zip(a,b)),'matrix sum shape')
    return [[(x+sign*y)%p for x,y in zip(r,s)] for r,s in zip(a,b)]


def eliminate(a,p,limit=None,trace=None):
    require(bool(a) and all(len(r)==len(a[0]) for r in a),'rectangular nonempty matrix required')
    out=[[x%p for x in row] for row in a];nr=len(out);nc=len(out[0]);limit=nc if limit is None else limit
    pivots=[];product=1;row=0
    for col in range(limit):
        pick=next((r for r in range(row,nr) if out[r][col]),None)
        if pick is None:continue
        if pick!=row:out[row],out[pick]=out[pick],out[row];product=-product
        pivot=out[row][col]
        if trace is not None:trace.append((pivot if pick==row else -pivot)%p)
        product=product*pivot%p;inv=pow(pivot,-1,p)
        out[row]=[x*inv%p for x in out[row]]
        for r in range(nr):
            if r!=row and out[r][col]:
                t=out[r][col];out[r]=[(x-t*y)%p for x,y in zip(out[r],out[row])]
        pivots.append(col);row+=1
        if row==nr:break
    return out,pivots,product%p


def fingerprint(a):
    payload={'rows':len(a),'columns':len(a[0]),'entries':a}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def rank(a,p):return len(eliminate(a,p)[1])


def determinant(a,p):
    require(bool(a) and all(len(row)==len(a) for row in a),'square matrix required')
    _,pivots,product=eliminate(a,p)
    return product if len(pivots)==len(a) else 0


def inverse(a,p):
    n=len(a);require(n>0 and all(len(row)==n for row in a),'inverse shape')
    out,pivots,_=eliminate([row+[int(i==j) for j in range(n)] for i,row in enumerate(a)],p,n)
    require(len(pivots)==n,'singular inverse')
    return [row[n:] for row in out]


def submatrix(a,rows,columns):return [[a[i][j] for j in columns] for i in rows]


def null_basis(a,pivots,p):
    free=[i for i in range(len(a[0])) if i not in pivots]
    inv=inverse([[row[j] for j in pivots] for row in a],p)
    columns=[]
    for f in free:
        v=[0]*len(a[0]);v[f]=1
        for i,j in enumerate(pivots):v[j]=-sum(inv[i][k]*a[k][f] for k in range(len(a)))%p
        columns.append(v)
    return columns


def poly(v,monomials):return {m:x for m,x in zip(monomials,v) if x}


def poly_product(a,b,p):
    result={}
    for u,x in a.items():
        for v,y in b.items():
            mon=tuple(sorted(u+v));result[mon]=(result.get(mon,0)+x*y)%p
    return result


def poly_sum(a,b,p):
    return {m:(a.get(m,0)+b.get(m,0))%p for m in a.keys()|b.keys()}


def dense(columns,rows):return [[column.get(m,0) for column in columns] for m in rows]


def build_model(cert):
    p=cert['field'];weights=cert['weights'];point=cert['point']
    require(p==7 and len(weights)==len(point)==8,'unexpected field/variable domain')
    require(all(type(x) is int and 0<=x<10 for x in weights) and all(type(x) is int and 0<=x<p for x in point),'noncanonical input coefficients')
    require(len(cert['pivot_columns'])==10 and len(cert['basis_columns'])==10,'basis block domain')
    quadratics=list(combinations_with_replacement(range(8),2));quartics=list(combinations_with_replacement(range(8),4))
    wt=lambda m:sum(weights[j] for j in m)%10
    def evaluate(m):
        value=1
        for j in m:value=value*point[j]%p
        return value
    blocks=[[m for m in quadratics if wt(m)==i] for i in range(10)]
    require([[list(m) for m in block] for block in blocks]==cert['quadratic_blocks'],'displayed quadratic order differs')
    zero=[m for m in quartics if wt(m)==0]
    require([list(m) for m in zero]==cert['zero_quartics'],'displayed zero-quartic order differs')
    require(len(cert['tangent_moments'])==len(zero),'tangent moment domain')
    require(all(type(x) is int and 0<=x<p for x in cert['tangent_moments']),'noncanonical tangent coefficients')
    tangent=dict(zip(zero,cert['tangent_moments']))
    moment=lambda m:(1+evaluate(m))%p if wt(m)==0 else 0
    T=[[moment(tuple(sorted(u+v))) for v in quadratics] for u in quadratics]
    T1=[[tangent.get(tuple(sorted(u+v)),0)%p for v in quadratics] for u in quadratics]
    at={m:i for i,m in enumerate(quadratics)};L=[at[(0,j)] for j in range(8)]
    J=[];Jp=[];N=[];Np=[]
    for i,monomials in enumerate(blocks):
        C=[[1]*len(monomials),[evaluate(m) for m in monomials]]
        pivots=[x-1 for x in cert['pivot_columns'][i]]
        cols=null_basis(C,pivots,p);require(cols==cert['basis_columns'][i],f'J basis differs in weight{i}')
        J.append([poly(v,monomials) for v in cols])
    for i,monomials in enumerate(blocks):
        opposite=(-i)%10;global_cols=[at[m] for m in monomials]
        pivot_cols=[x-1 for x in cert['pivot_columns'][i]]
        pivot_rows=[at[blocks[opposite][x-1]] for x in cert['pivot_columns'][opposite]]
        E=submatrix(T,pivot_rows,[global_cols[j] for j in pivot_cols])
        rhs=mm(submatrix(T1,pivot_rows,global_cols),dense(J[i],monomials),p)
        solved=mm(inverse(E,p),rhs,p);derivative=[[0]*len(J[i]) for _ in monomials]
        for r,slot in enumerate(pivot_cols):derivative[slot]=[-x%p for x in solved[r]]
        Jp.append([poly(v,monomials) for v in transpose(derivative)])
        lrows=[at[m] for m in blocks[opposite] if m[0]==0]
        if not lrows:
            cols=[[int(r==c) for r in range(len(monomials))] for c in range(len(monomials))]
            N.append([poly(v,monomials) for v in cols]);Np.append([{} for _ in cols])
        else:
            require(len(lrows)==1,'L weight multiplicity')
            pivot=next(j for j,m in enumerate(monomials) if m[0]==0)
            row=submatrix(T,lrows,global_cols)[0];cols=null_basis([row],[pivot],p)
            N.append([poly(v,monomials) for v in cols])
            rhs=mm(submatrix(T1,lrows,global_cols),transpose(cols),p)[0]
            derivatives=[[0]*len(monomials) for _ in cols]
            for c,x in enumerate(rhs):derivatives[c][pivot]=-x*pow(row[pivot],-1,p)%p
            Np.append([poly(v,monomials) for v in derivatives])
    j=dense([c for b in J for c in b],quadratics);jp=dense([c for b in Jp for c in b],quadratics)
    n=dense([c for b in N for c in b],quadratics);np=dense([c for b in Np for c in b],quadratics)
    require(len(j[0])==16 and rank(j,p)==16,'kernel basis dimension')
    require(len(n[0])==28 and rank(n,p)==28,'H0 basis dimension')
    require(rank([row for row,m in zip(j,quadratics) if 0 not in m],p)==16,'projected kernel dimension')
    require(all(not x for row in mm(T,j,p) for x in row),'kernel equation')
    require(all(not x for row in mm(transpose(j),mm(T1,j,p),p) for x in row),'tangent equation')
    require(all(not x for row in combine(mm(T,jp,p),mm(T1,j,p),p) for x in row),'differentiated J equation')
    require(all(not x for row in mm([T[r] for r in L],n,p) for x in row),'H0 equation')
    require(all(not x for row in combine(mm([T[r] for r in L],np,p),mm([T1[r] for r in L],n,p),p) for x in row),'differentiated H0 equation')
    return Model(tuple(weights),quadratics,quartics,blocks,T,T1,L,J,Jp,N,Np,p)


def matrices(model,w):
    p=model.field;G1=[];G2=[];D=[];D1=[]
    for i in range(10):
        j=(w-i)%10
        for uidx,u in enumerate(model.J[i]):
            for vidx,v in enumerate(model.J[j]):
                if (i,uidx)<=(j,vidx):G1.append(poly_product(u,v,p))
            for coordinate in range(1,8):
                if model.wt((0,coordinate))==j:G2.append(poly_product(u,{(0,coordinate):1},p))
            for vidx,v in enumerate(model.N[j]):
                D.append(poly_product(u,v,p));D1.append(poly_sum(poly_product(model.Jp[i][uidx],v,p),poly_product(u,model.Np[j][vidx],p),p))
    rows=[m for m in model.quartics if model.wt(m)==w]
    return {'G1':dense(G1,[m for m in rows if 0 not in m]),'G2':dense(G2,[m for m in rows if m.count(0)==1]),'D':dense(D,rows),'D1':dense(D1,rows)}


def retained(size,omitted):
    require(len(omitted)==len(set(omitted)) and all(type(i) is int and 1<=i<=size for i in omitted),'invalid omitted indices')
    return [i for i in range(size) if i+1 not in omitted]


def verify_weight(model,cert,w):
    p=model.field;mat=matrices(model,w);d=mat['D'];d1=mat['D1']
    zeros=[[0]*len(d[0]) for _ in d]
    bordered=[row+z for row,z in zip(d,zeros)]+[row+tail for row,tail in zip(d1,d)]
    result={'weight':w,'dimensions':[len(d),len(d[0])],'ranks':{k:rank(mat[k],p) for k in ['G1','G2','D']}}
    result['ranks']['bordered']=rank(bordered,p)
    result['matrix_hashes']={key:fingerprint(value) for key,value in mat.items()}
    if w<=5:
        for name in ['G1','G2']:
            spec=next(x for x in cert[name] if x['weight']==w);matrix=mat[name]
            rows=retained(len(matrix),spec.get('omit_rows',[]));cols=retained(len(matrix[0]),spec.get('omit_columns',[]))
            require(len(rows)==len(cols)==spec['size'],f'{name} minor size weight{w}')
            det=determinant(submatrix(matrix,rows,cols),p);require(det==spec['det'],f'{name} minor det weight{w}: {det}')
            result[name+'_minor_det']=det
            if w==0 and name=='G2':
                trace=[];eliminate(submatrix(matrix,rows,cols),p,trace=trace)
                require(trace==[x%p for x in cert['elimination_pivots']['G2_weight0']],'G2 signed pivot trace')
                result['G2_signed_pivots']=trace
        spec=next(x for x in cert['D'] if x['weight']==w);R=retained(len(d),spec['omit_rows']);S=retained(len(d[0]),spec['omit_columns'])
        E=submatrix(d,R,S);require(len(R)==len(S)==spec['size'],'D minor size')
        det=determinant(E,p);require(det==spec['det'],f'D minor det weight{w}: {det}');result['D_minor_det']=det
        if w==0:
            trace=[];eliminate(E,p,trace=trace)
            require(trace==[x%p for x in cert['elimination_pivots']['D_weight0']],'D signed pivot trace')
            result['D_signed_pivots']=trace
        Rp=[x-1 for x in spec['extra_rows']];Sp=[x-1 for x in spec['extra_columns']]
        inv=inverse(E,p);A=submatrix(d,R,Sp);B=submatrix(d,Rp,S);BE=mm(B,inv,p);EA=mm(inv,A,p)
        Z=combine(submatrix(d1,Rp,Sp),mm(submatrix(d1,Rp,S),EA,p),p,-1)
        Z=combine(Z,mm(BE,submatrix(d1,R,Sp),p),p,-1)
        Z=combine(Z,mm(mm(BE,submatrix(d1,R,S),p),EA,p),p)
        require(Z==spec['corner'],f'corner differs weight{w}: {Z}')
        require(determinant(Z,p)==spec['corner_det'],f'corner determinant weight{w}')
        result['corner']=Z
        require(len(Rp)==len(Sp)==len(Z) and not set(R)&set(Rp) and not set(S)&set(Sp),'border indices overlap')
        br=R+[len(d)+r for r in R]+[len(d)+r for r in Rp]
        bc=S+[len(d[0])+c for c in S]+Sp
        bdet=determinant(submatrix(bordered,br,bc),p)
        require(bdet==det*det*spec['corner_det']%p and bdet!=0,f'direct bordered determinant weight{w}')
        result['bordered_minor_det']=bdet
    return result


def naive_lift_probe(cert):
    """Boundary control: printed integers in the raw complex-coordinate formula
    do not give a real PSD witness. No positivity notion is imposed on F7.
    """
    weights,point=cert['weights'],cert['point']
    def moment(m):
        if sum(weights[i] for i in m)%10:return 0
        value=1
        for i in m:value*=point[i]
        return 1+value
    quadratics=list(combinations_with_replacement(range(len(point)),2))
    for u,v in combinations(quadratics,2):
        a,b,c=moment(u+u),moment(u+v),moment(v+v)
        det=a*c-b*b
        if det<0:
            return {'quadratics':[list(u),list(v)],'principal_minor':[[a,b],[b,c]],'integer_determinant':det}
    raise ValueError('negative naive-lift principal minor not found')


def verify(cert):
    for name in ['G1','G2','D']:require([x['weight'] for x in cert[name]]==list(range(6)),f'incomplete {name} minor domain')
    require(set(cert['generic_rank_lower_bounds'])=={'G1','G2','D','bordered'} and all(len(v)==10 for v in cert['generic_rank_lower_bounds'].values()),'rank target domain')
    model=build_model(cert);seed=rank(model.T,7);ldet=determinant(submatrix(model.T,model.L,model.L),7)
    require(seed==20 and ldet==6,'seed rank or L determinant differs')
    results=[verify_weight(model,cert,w) for w in range(10)]
    for key,targets in cert['generic_rank_lower_bounds'].items():
        require(all(r['ranks'][key]>=targets[r['weight']] for r in results),f'fixed-specialization rank lower bound {key}')
    require(sum(r['ranks']['D'] for r in results)==302,'fixed-specialization D rank')
    return {'seed_matrix_hashes':{'T':fingerprint(model.T),'T1':fingerprint(model.T1)},'seed_rank':seed,'L_det':ldet,'naive_lift_boundary':naive_lift_probe(cert),'displayed_weights':list(range(6)),'weights':results,'rank_sums':{key:sum(r['ranks'][key] for r in results) for key in ['G1','G2','D','bordered']}}


def mutate(cert,control):
    bad=copy.deepcopy(cert)
    if control=='point':bad['point'][1]=(bad['point'][1]+1)%7
    elif control=='tangent':bad['tangent_moments'][0]=(bad['tangent_moments'][0]+1)%7
    elif control=='zero_tangent':bad['tangent_moments']=[0]*len(bad['tangent_moments'])
    elif control=='minor':bad['G1'][0]['det']=(bad['G1'][0]['det']+1)%7
    elif control=='corner':bad['D'][0]['corner'][0][0]=(bad['D'][0]['corner'][0][0]+1)%7
    else:raise ValueError('unknown control')
    return bad


def check_sources():
    sources=json.loads((ROOT/'sources.json').read_text())
    for f in sources['files']:
        require(hashlib.sha256((ROOT/f['local']).read_bytes()).hexdigest()==f['sha256'],f'source hash differs: {f["local"]}')
    return len(sources['files'])


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--control',choices=['point','tangent','zero_tangent','minor','corner']);args=parser.parse_args()
    cert=json.loads((ROOT/'certificate.json').read_text())
    if args.control:cert=mutate(cert,args.control)
    result=verify(cert);result['source_files_hashed']=check_sources();print(json.dumps(result,sort_keys=True,indent=2));print('RESULT: modular Hankel seed, tangent and displayed minors reconstructed')


if __name__=='__main__':main()
