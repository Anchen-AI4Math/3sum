#!/usr/bin/env python3
"""Optional FLOATING-POINT exploration; NOT part of any certificate.

Requires scipy. verify_certificate.py needs only the Python standard library.
The checker, not this optimizer, determines whether a witness is accepted.
"""
import math
from scipy.optimize import minimize_scalar, brentq

def H(t):
    if t in (0,1):
        return 0.0
    return (-t*math.log(t)-(1-t)*math.log1p(-t))/math.log(2)

def candidate(c):
    E=c*H(1/c)/2
    k=2*c*H(1/(2*c))-c*H(1/c)-1
    g=lambda t:c*(H(1/c)-H((1-t)/c))
    opt=minimize_scalar(lambda t:-H(t)/(1+g(t)),bounds=(.001,.49),method='bounded',
                        options={'xatol':1e-13})
    rho=-opt.fun
    def at_theta(t):
        h=H(t)
        beta=(h-k-rho*(1.5-h))/(2-rho)
        saving=.5-h+beta
        return beta,saving
    theta=brentq(lambda t:g(t)-(at_theta(t)[1]-2*at_theta(t)[0]),1e-6,.49,xtol=1e-13)
    b,S=at_theta(theta)
    eps=1/(E+.5-H(theta))
    tau_min=.5+b+k+S
    tau_max=(g(.5)-(S-2*b))/(1+g(.5))
    tau=(tau_min+tau_max)/2
    values=[2*eps*E,1+eps*(E-b),2-eps*S,2-eps*(.5+b-H(theta)),
            2-eps*(.5-b-k-rho*(1+S-2*b)),2-eps*(tau-.5-b-k),
            eps*1.6*(E+.5),2+eps*(.8-.4*E-2*b),1+eps*(.5-b),
            2-eps*(E+b),2-2*eps*(E+b),1]
    if not (S>0 and 0<tau_min<tau_max<1 and 0<eps*(E+b)<1):
        raise ValueError('Exploratory candidate is infeasible.')
    return dict(c=c,exponent=max(values),epsilon=eps,beta=b,saving=S,theta=theta,
                rho=rho,tangent=opt.x,tau=tau,costs=values)

if __name__=='__main__':
    print('EXPLORATORY FLOATS ONLY. NO CERTIFICATE OR GLOBAL OPTIMALITY CLAIM.')
    for c in (64,128,192,231,232,233,256,384,512):
        r=candidate(c)
        print(c,format(r['exponent'],'.15f'))
    opt=minimize_scalar(lambda c:candidate(c)['exponent'],bounds=(180,300),method='bounded',
                        options={'xatol':1e-6})
    print('Continuous-c exploratory point:',candidate(opt.x))
    print('All correctness decisions must be made by verify_certificate.py instead.')
