"""Float-assisted witness selection; verify_profile is rational-only."""
from explore_profiles import Profile
from verify_profile import *

if __name__=='__main__':
    src=json.loads((ROOT/'integer_profile.json').read_text())
    cs=[round(c) for c in src['cs']]
    ws=[F(format(w,'.12f')) for w in src['ws'][:-1]]
    ws.append(1-sum(ws))
    # Merge adjacent identical expansion factors: ten numerical segments -> nine.
    cc=[];ww=[]
    for c,w in zip(cs,ws):
        if cc and cc[-1]==c:ww[-1]+=w
        else:cc.append(c);ww.append(w)
    cs,ws=cc,ww
    p={k:format(src[k],'.12f') for k in ('epsilon','beta','saving','tau')}
    p.update(principal='1.9586106',target='1.958611')
    tau=F(p['tau']);v=F(p['saving'])-2*F(p['beta'])
    profile=Profile(cs,[float(w) for w in ws])
    cuts=[];end=F(0)
    for w in ws:end+=w;cuts.append(end)
    grid=sorted(set([F(0),tau]+[a for a in cuts if a<tau]+[F(i,1000) for i in range(1,1000) if F(i,1000)<tau]))
    pieces=[]
    for lo,hi in zip(grid[:-1],grid[1:]):
        lam=F(format(profile.query(float((lo+hi)/2),float(v))[3],'.16f'))
        d,hs=dual(cs,lam)
        dl=floor_dec(d.lo,21);hl=[floor_dec(h.lo,21) for h in hs]
        qs=[]
        for a in (lo,hi):
            w=weights(ws,a)
            q=ceil_dec((v+a-sum(wi*h for wi,h in zip(w,hl)))/dl+F(1,10**12),12)
            qs.append(q)
        pieces.append(dict(lo=str(lo),hi=str(hi),**{'lambda':str(lam)},qlo=str(qs[0]),qhi=str(qs[1])))
    data={'schema':2,'expansions':cs,'weights':[str(w) for w in ws],'parameters':p,'schedule':pieces}
    (ROOT/'profile_certificate.json').write_text(json.dumps(data,indent=2)+'\n')
    verify(data)
