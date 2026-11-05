"""DEC-021 revision 2: exact error rates of the >=2 heuristic, fixed n and staged design (independent Bernoulli trials; illustrative). Run: python3 dec-021-power.py"""
from math import comb
def b(n,k,p): return comb(n,k)*p**k*(1-p)**(n-k)
def fixed(n,pa,pb,m=2):
    fav=sum(b(n,i,pa)*b(n,j,pb) for i in range(n+1) for j in range(n+1) if j-i>=m)
    harm=sum(b(n,i,pa)*b(n,j,pb) for i in range(n+1) for j in range(n+1) if i-j>=m)
    return fav,harm
def fixed_either(n,pa,pb,pc,m=2):
    s=0;h=0
    for i in range(n+1):
        pi=b(n,i,pa)
        pB=sum(b(n,j,pb) for j in range(n+1) if j-i>=m); pC=sum(b(n,j,pc) for j in range(n+1) if j-i>=m)
        s+=pi*(1-(1-pB)*(1-pC))
        hB=sum(b(n,j,pb) for j in range(n+1) if i-j>=m); hC=sum(b(n,j,pc) for j in range(n+1) if i-j>=m)
        h+=pi*(1-(1-hB)*(1-hC))
    return s,h
def staged(pa,pb,pc):
    # returns P(ceiling), P(B ahead), P(either B or C ahead), P(any harm), expected trials (target only)
    ceil=fav_b=fav_any=harm_any=0; et=0
    for a3 in range(4):
        pa3=b(3,a3,pa)
        if a3>=2: ceil+=pa3; et+=pa3*3; continue
        for x3 in range(4):
          for c3 in range(4):
            w=pa3*b(3,x3,pb)*b(3,c3,pc)
            dB=x3-a3; dC=c3-a3
            undB=abs(dB) in (1,2); undC=abs(dC) in (1,2)
            n4=(1 if (undB or undC) else 0)+(1 if undB else 0)+(1 if undC else 0)
            et+=w*(9+n4)
            # outcomes of 4th trials
            for a4 in ((0,1) if (undB or undC) else (0,)):
              wa=(pa if a4 else 1-pa) if (undB or undC) else 1
              for x4 in ((0,1) if undB else (0,)):
                wb=(pb if x4 else 1-pb) if undB else 1
                for c4 in ((0,1) if undC else (0,)):
                  wc=(pc if c4 else 1-pc) if undC else 1
                  ww=w*wa*wb*wc
                  fB = (dB>=3) or (undB and (x3+x4)-(a3+a4)>=2)
                  fC = (dC>=3) or (undC and (c3+c4)-(a3+a4)>=2)
                  hB = (dB<=-3) or (undB and (a3+a4)-(x3+x4)>=2)
                  hC = (dC<=-3) or (undC and (a3+a4)-(c3+c4)>=2)
                  fav_b+=ww*fB; fav_any+=ww*(fB or fC); harm_any+=ww*(hB or hC)
    return ceil,fav_b,fav_any,harm_any,et
print('fixed n=4 single comparison (fav, harm):')
for pa,pb in [(.5,.5),(.3,.3),(.3,.6),(.3,.7),(.5,.9)]: print(pa,pb,[round(x,3) for x in fixed(4,pa,pb)])
print('fixed n=4 either B or C (fav, harm) at null:')
for p in (.3,.5): print(p,[round(x,3) for x in fixed_either(4,p,p,p)])
print('n=6 m=2', [round(x,3) for x in fixed(6,.3,.3)], [round(x,3) for x in fixed(6,.3,.6)])
print('staged: ceil, B ahead, B-or-C ahead, any harm, E[target trials]')
for s in [(.1,.1,.1),(.3,.3,.3),(.5,.5,.5),(.3,.6,.3),(.3,.7,.3),(.1,.5,.1),(.7,.7,.7)]: print(s,[round(x,3) for x in staged(*s)])
