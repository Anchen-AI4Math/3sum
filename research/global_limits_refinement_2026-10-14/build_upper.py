"""Generate a new rational upper certificate; floats choose tangents only."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.append(str(ROOT.parent/'heterogeneous_limits_2026-10-14'))
from explore_profiles import Profile
from verify_upper import F,floor_dec,ceil_dec,dual,weights,verify

if __name__=='__main__':
    src=json.loads((ROOT/'integer_profile.json').read_text())
    cs=[round(c) for c in src['cs']]
    ws=[F(format(w,'.12f')) for w in src['ws'][:-1]];ws.append(1-sum(ws))
    p={k:format(src[k],'.12f') for k in ('epsilon','beta','saving','tau')}
    p.update(principal='1.9585615',target='1.958562')
    tau=F(p['tau']);v=F(p['saving'])-2*F(p['beta'])
    profile=Profile(cs,[float(w) for w in ws])
    ends=[];end=F(0)
    for w in ws:end+=w;ends.append(end)
    grid=sorted(set([F(0),tau]+[a for a in ends if a<tau]+[F(i,1000) for i in range(1,1000) if F(i,1000)<tau]))
    pieces=[]
    for lo,hi in zip(grid[:-1],grid[1:]):
        lam=F(format(profile.query(float((lo+hi)/2),float(v))[3],'.16f'))
        d,hs=dual(cs,lam);dl=floor_dec(d.lo,21);hl=[floor_dec(h.lo,21) for h in hs]
        qs=[]
        for a in (lo,hi):
            w=weights(ws,a)
            q=ceil_dec((v+a-sum(wi*h for wi,h in zip(w,hl)))/dl+F(1,10**12),12);qs.append(q)
        pieces.append(dict(lo=str(lo),hi=str(hi),**{'lambda':str(lam)},qlo=str(qs[0]),qhi=str(qs[1])))
    data={'schema':2,'expansions':cs,'weights':[str(w) for w in ws],'parameters':p,'schedule':pieces}
    (ROOT/'upper_certificate.json').write_text(json.dumps(data,indent=2)+'\n')
    out=verify(data);(ROOT/'upper_verification.json').write_text(json.dumps(out,indent=2)+'\n')
