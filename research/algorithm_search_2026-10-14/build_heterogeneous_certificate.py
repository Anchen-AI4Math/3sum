"""Generate rational witnesses. Uses floats only to choose dual tangent points."""
from explore_heterogeneous import query
from verify_heterogeneous import *

if __name__=='__main__':
    c1,c2=72,252
    p={'epsilon':'0.215745630','beta':'-0.046171284','saving':'0.189018426',
       'split':'0.340200365','tau':'0.65','principal':'1.959226','target':'1.95923'}
    split=F(p['split']);tau=F(p['tau']);v=F(p['saving'])-2*F(p['beta'])
    grid=sorted(set([F(i,200) for i in range(131)]+[split]))
    pieces=[]
    for lo,hi in zip(grid[:-1],grid[1:]):
        a=(lo+hi)/2
        _,t=query(c1,c2,float(split),float(a),float(v))
        q=t*float(1-a);w1,w2=weights(split,a)
        if w1>0 and q<=float(w1)*(1-c1/c2):
            lam=(float(1-a)-q-float(w2))/(float(w1)*c1)
        else:lam=(float(1-a)-q)/(float(w1)*c1+float(w2)*c2)
        lam=F(format(lam,'.16f'))
        d,hs=dual(c1,c2,lam)
        dl=floor_dec(d.lo,21);hl=[floor_dec(h.lo,21) for h in hs]
        qs=[]
        for a in (lo,hi):
            w=weights(split,a)
            q=ceil_dec((v+a-w[0]*hl[0]-w[1]*hl[1])/dl+F(1,10**12),12)
            qs.append(q)
        pieces.append(dict(lo=str(lo),hi=str(hi),**{'lambda':str(lam)},qlo=str(qs[0]),qhi=str(qs[1])))
    data={'schema':1,'expansions':[c1,c2],'parameters':p,'schedule':pieces}
    (ROOT/'heterogeneous_certificate.json').write_text(json.dumps(data,indent=2)+'\n')
    verify(data)
