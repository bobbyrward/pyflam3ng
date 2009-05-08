"""
Interpolation utility functions for generating vectors between control points.

This module includes functions for generating curved vectors between points,
periodic vectors that start and end at the same point, and smoothed TCB splines
for animation and interpolation.
"""

from math import *
import numpy


def crange(x, y, n, curve='lin', a=1.0, b=0.5, c=1.0):
    """Generates a curved range between x and y with n points.

    Arguments:
        x       - Starting value
        y       - Ending value
        n       - Number of steps from x to y
        curve   - Curve of the line
        a, b, c - Curve params

    Curve options are:
        lin     - Linear
        par     - Parabolic
        npar    - Negative Parabolic
        cos     - Half-period Cosine (a = slope)
        sinh    - Hyperbolic Sinusoidal (a = slope)
        tanh    - Hyperbolic Tangent (a = slope)
        exp     - Exponential (a = slope)
        plin    - Periodic Linear (a = amp, b = peak)
        ppar    - Periodic Parabolic (a = amp, b = peak, c = mode)
                    Mode options: 0 = ++, 1 = +-, 2 = --, 3 = -+
        psin    - Periodic Sinusoidal (a = amp (+ and -), b = slope, c = freq)
        pcos    - Periodic Cosine (a = amp (+ only), b = slope c = freq)
    """
    m = float(n)
    tmp = numpy.zeros(n, numpy.float32)

    if curve not in ['plin', 'ppar', 'psin', 'pcos']:
        #Discrete
        if   curve=='exp':
            d = y-x
            for i in xrange(n):
                tmp[i] = d*(1-exp(-a*(i/m)))/(1-exp(-a))
        elif curve=='par':
            d = (y-x)/(m**2)
            for i in xrange(n):
                tmp[i] = x+d*(i**2)
        elif curve=='npar':
            d = (y-x)/(m**2)
            for i in xrange(n):
                tmp[i] = y-d*((n-i)**2)
        elif curve=='cos':
            d = y-x
            for i in xrange(n):
                tmp[i] = (x+d*((cos(pi + (i/m)*pi))+1)/2)**a
        elif curve=='sinh':
            d = y-x
            tmp[0] = x
            for i in xrange(1,n):
                tmp[i] = x+((sinh(a*(2*i-m)/m) - sinh(-a)) / (2*sinh(a*(2*n-m)/m)/d))
        elif curve=='tanh':
            d = y-x
            tmp[0] = x
            for i in xrange(1,n):
                tmp[i] = x+((tanh(a*(2*i-m)/m) - tanh(-a)) / (2*tanh(a*(2*n-m)/m)/d))
        else:
            d = (y-x)/m
            for i in xrange(n):
                tmp[i] = x+d*i
    else:
        #Periodic
        if   curve=='plin':
            n1=int(b*n)
            n2=n-n1
            mod = list(crange(0,a,n1,curve='lin'))
            mod.extend(list(crange(a,0,n2,curve='lin')))
            tmp = crange(x,y,n,curve='lin')
            for i in xrange(n):
                tmp[i] += mod[i]
        elif curve=='ppar':
            n1=int(b*n)
            n2=n-n1
            mod = []
            tmp = crange(x,y,n,curve='lin')
            if c in [0, 1]: #+
                mod.extend(list(crange(0,a,n1,curve='par')))
            else:
                mod.extend(list(crange(0,a,n1,curve='npar')))
            if c in [0, 3]: #+
                mod.extend(list(crange(a,0,n2,curve='par')))
            else:
                mod.extend(list(crange(a,0,n2,curve='npar')))
            for i in xrange(n):
                tmp[i] += mod[i]
        elif curve=='psin':
            tmp = crange(x,y,n,curve='lin')
            for i in xrange(n):
                tmp[i] += (a*sin((i/m)*pi*2*c))#**b
        else:
            d = y-x
            tmp = crange(x,y,n,'lin')
            for i in xrange(n):
                tmp[i] += (a*((cos(pi + (i/m)*pi*2*c))+1)/2)#**b
    return tmp
#---end crange

class CP(object):
    """Helper object for spline interpo."""
    def __init__(self, val, time=0, t=0, c=-1, b=0):
        """Set values.

        Arguments:
            val     - Value of the CP. Can be n-dimensional.
            time    - Time of the CP. Placeholder currently.
            t, c, b - Spline params. Default to linear.
        """
        self.val = val
        self.time = time #placeholder - irregular grid not ready
        self.t = t
        self.c = c
        self.b = b

    def _get_spline(self):
        return self.t, self.c, self.b

    spline = property(_get_spline)
#---end CP

def get_pad(target, neighbor, n):
    """Returns a CP for padding interp with <4 points.

    Arguments:
        target  - CP that's being padded
        neighbor- CP's closest neighbor
        n       - Distance from target to neighbor (- if after, + if before)
    """
    if type(target.val)==int or type(target.val)==float:
        count = 1
    else:
        count = len(target.val)

    if count==1:
        diff = (target.val-neighbor.val)*(n/abs(n))
        return CP(target.val-diff)
    else:
        val = []
        for i in xrange(count):
            diff = (target.val[i]-neighbor.val[i])*(n/abs(n))
            val.append(target.val[i]-diff)
        return CP(val)
#---end get_pad

def get_spline(cps, n=50, loop=False, curve='lin', a=1, b=0.5, c=1):
    """Takes list CPs and returns full spline.

    Arguments:
        cps     - List of CP objects. All vals must have same dimensions.
        loop    - Does the animation loop?
        curve   - Curve shape. This will eventually be done per-segment.
        a, b, c - Curve params.
    """
    vals = []
    if type(cps[0].val)==int or type(cps[0].val)==float:
        #1D data
        for c in cps:
            vals.append(c.val)
        count = 1
    else:
        #nD data
        for i in xrange(len(cps[0].val)):
            tmp = []
            for c in cps:
                tmp.append(c.val[i])
            vals.append(tmp)
        count = len(cps[0].val)

    tmp =[]
    if loop:
        for i in xrange(len(cps)):
            #handle first seg: -1, 0, 1, 2
            if i==0:
                tcps = cps[-1:] + cps[:3]
            #handle last seg: n-1 n 0 1
            elif i==len(cps)-1:
                tcps = cps[-2:] + cps[:2]
            elif i==len(cps)-2:
                tcps = cps[-3:] + cps[:1]
            else:
                tcps = cps[i-1:i+3]

            print tcps

            if count==1:
                tmp.extend(spline([cp.val for cp in tcps], n, tcps[1].spline,
                           tcps[2].spline, curve=curve, a=a, b=b, c=c))
            else:
                #This code is ripe for improvement
                ttmp = []
                for i in xrange(count):
                    ttmp.append(spline([cp.val[i] for cp in tcps], n, tcps[1].spline,
                                tcps[2].spline, curve=curve, a=a, b=b, c=c))
                reord = []
                for i in xrange(len(ttmp[0])):
                    row = []
                    for j in xrange(count):
                        row.append(tmp[j][i])
                    reord.append(row)
                tmp.extend(reord)
                #end improve section
    else:
        for i in xrange(len(cps)-1):
            #handle first seg: pad, 0, 1, 2
            if i==0:
                tcps = [get_pad(cps[0], cps[1], n),] + cps[:3]
            #handle last seg: n-2, n-1, n, pad
            elif i==len(cps)-2:
                tcps = cps[-3:] + [get_pad(cps[-1], cps[-2], -n),]
            else:
                tcps = cps[i-1:i+3]

            print tcps

            if count==1:
                tmp.extend(spline([cp.val for cp in tcps], n, tcps[1].spline,
                           tcps[2].spline, curve=curve, a=a, b=b, c=c))
            else:
                ttmp = []
                for i in xrange(count):
                    ttmp.append(spline([cp.val[i] for cp in tcps], n, tcps[1].spline,
                                tcps[2].spline, curve=curve, a=a, b=b, c=c))
                reord = []
                for i in xrange(len(ttmp[0])):
                    row = []
                    for j in xrange(count):
                        row.append(tmp[j][i])
                    reord.append(row)
                tmp.extend(reord)
    return tmp
#---end get_spline


def spline(cps, n, splinea=(0, -1, 0), splineb=(0, -1, 0), **kwargs):
    """Generates a smoothed spline from a list of 4 control points.

    Arguments:
        cps     - List of 4 points to be smoothed (1D only)
        n       - Number of points to interp
        splinea - TCB spline parameters for first interp point
        splineb - TCB spline parameters for second interp point
        kwargs  - Curve information for timeline curve (curve, a, b, c)
    """
    if len(cps) < 4: raise ValueError('Need 4 cps')

    v = crange(0, 1, n, **kwargs)

    ta, ca, ba = splinea
    tb, cb, bb = splineb
    fa = (1-ta)*(1+ca)*(1+ba)
    fb = (1-ta)*(1-ca)*(1-ba)
    fc = (1-tb)*(1-cb)*(1+bb)
    fd = (1-tb)*(1+cb)*(1-bb)

    M = numpy.array([[-fa,4+fa-fb-fc,-4+fb+fc-fd,fd]
                    ,[2*fa,-6-2*fa+2*fb+fc,6-2*fb-fc+fd,-fd]
                    ,[-fa,fa-fb,fb,0]
                    ,[0,2,0,0]])/2.0
    C = numpy.array(cps)
    MxC = numpy.dot(M,C)
    S = []
    for t in v:
        S.append([t**3, t**2, t, 1])
    return list(numpy.dot(numpy.array(S), MxC))

