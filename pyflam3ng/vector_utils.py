"""
Interpolation utility functions for generating vectors between control points.

This module includes functions for generating curved vectors between points,
periodic vectors that start and end at the same point, and smoothed TCB splines
for animation and interpolation.
"""

import numpy, math


def crange(x, y, n, curve='lin', p1=1.0, p2=0.5, p3=1.0):
    """Generates a curved range between x and y with n points.

    Arguments:
        x       - Starting value
        y       - Ending value
        n       - Number of steps from x to y
        curve   - Curve of the line
        p1, 2, 3- Curve params

    Curve options are:
        lin     - Linear
        par     - Parabolic
        npar    - Negative Parabolic
        sin     - Sinusoidal (p1 = amp (+ and -), p2 = slope, p3 = freq)
        cos     - Periodic Cosine (p1 = amp (+ only), p2 = slope p3 = freq)
        hcos    - Half-period Cosine (p1 = slope)
        sinh    - Hyperbolic Sinusoidal (p1 = slope)
        tanh    - Hyperbolic Tangent (p1 = slope)
        exp     - Exponential (p1 = slope)
        plin    - Periodic Linear (p1 = amp, p2 = peak)
        ppar    - Periodic Parabolic (p1 = amp, p2 = peak, p3 = mode)
                    Mode options: 0 = ++, 1 = +-, 2 = --, 3 = -+
    """
    if curve in ['plin', 'pcos']:
        if p2 <= 0 or p2 >= 1:
            raise ValueError('peak setting out of bounds (must be')

    m = float(n)
    tmp = numpy.zeros(n, numpy.float32)

    if   curve=='lin':
        d = (y-x)/m
        for i in xrange(n):
            tmp[i] = x+d*i
    elif curve=='par':
        d = (y-x)/(m**2)
        for i in xrange(n):
            tmp[i] = x+d*(i**2)
    elif curve=='npar':
        d = (y-x)/(m**2)
        for i in xrange(n):
            tmp[i] = y-d*((n-i)**2)
    elif curve=='sin':
        for i in xrange(n):
            tmp[i] = p1*math.sin((i/m)*math.pi*2*p3)#**b
        tmp += crange(x,y,n,curve='lin')
    elif curve=='cos':
        d = y-x
        for i in xrange(n):
            tmp[i] = (p1*((math.cos(math.pi + (i/m)*math.pi*2*p3))+1)/2)**p2
        tmp += crange(x,y,n,'lin')
    elif curve=='hcos':
        d = y-x
        for i in xrange(n):
            tmp[i] = (x+d*((math.cos(math.pi + (i/m)*math.pi))+1)/2)**p1
    elif curve=='sinh':
        d = y-x
        tmp[0] = x
        for i in xrange(1,n):
            tmp[i] = x+((math.sinh(p1*(2*i-m)/m)-math.sinh(-p1))/
                        (2*math.sinh(p1*(2*n-m)/m)/d))
    elif curve=='tanh':
        d = y-x
        tmp[0] = x
        for i in xrange(1,n):
            tmp[i] = x+((math.tanh(p1*(2*i-m)/m)-math.tanh(-p1))/
                        (2*math.tanh(p1*(2*n-m)/m)/d))
    elif curve=='exp':
        d = y-x
        for i in xrange(n):
            tmp[i] = d*(1-math.exp(-p1*(i/m)))/(1-math.exp(-p1))
    elif curve=='plin':
        np=int(p2*n)
        tmp[:np] = crange(0,p1,np,curve='lin')
        tmp[np:] = crange(p1,0,n-np,curve='lin')
        tmp += crange(x,y,n,curve='lin')
    elif curve=='ppar':
        np=int(p2*n)
        if p3 in [0, 1]: #+
            tmp[:np] = crange(0,p1,np,curve='par')
        else:
            tmp[:np] = crange(0,p1,np,curve='npar')
        if p3 in [0, 3]: #+
            tmp[np:] = crange(p1,0,n-np,curve='par')
        else:
            tmp[np:] = crange(p1,0,n-np,curve='npar')
        tmp += crange(x,y,n,curve='lin')
    else:
        return ValueError('Bad curve type')
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

    def _set_spline(self, params):
        self.t, self.c, self.b = params

    spline = property(_get_spline, _set_spline, doc="Spline parameters in a list")
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
        return CP(target.val+diff)
    else:
        val = []
        for i in xrange(count):
            diff = (target.val[i]-neighbor.val[i])*(n/abs(n))
            val.append(target.val[i]-diff)
        return CP(val)
#---end get_pad

def get_spline(my_cps, n=50, loop=False, curve='lin', p1=1, p2=0.5, p3=1):
    """Takes list CPs and returns full spline.

    Arguments:
        my_cps  - List of CP objects. All vals must have same dimensions.
        loop    - Does the animation loop?
        curve   - Curve shape. This will eventually be done per-segment.
        a, b, c - Curve params.
    """
    if len(my_cps)<2:
        raise ValueError('Need 2 or more CPs')

    #Segments is the number of interps to do, 1 less than #cps when not looping
    if loop: seg = len(my_cps)
    else:    seg = len(my_cps)-1
    nf = seg * n

    if type(my_cps[0].val)==int or type(cps[0])==float:
        count = 1
    else:
        count = len(cps[0].val)

    vals = numpy.zeros((seg+3, count), numpy.float32)

    #examples with [0, 1, 2, 3] - remember n-1, n, n+1, n+2 for spline
    #  looping - (3,) 0, 1, 2, 3, 0, (1) (not interped, just used for spline)
    #  not - (pad0,) 0, 1, 2, 3, (pad3) (not interped)
    if loop:
        vals[0] = my_cps[-1].val
        for i in xrange(len(my_cps)):
            vals[i+1] = my_cps[i].val
        vals[-2] = my_cps[0].val
        vals[-1] = my_cps[1].val
        my_cps.append(my_cps[1])
        my_cps.append(my_cps[2])
        my_cps.insert(0, my_cps[-1])
    else:
        pad1 = get_pad(my_cps[0], my_cps[1], n)
        pad2 = get_pad(my_cps[-2], my_cps[-1], -n)
        vals[0] = pad1.val
        for i in xrange(len(my_cps)):
            vals[i+1] = my_cps[i].val
        vals[-1] = pad2.val
        my_cps.insert(0, pad1)
        my_cps.append(pad2)

    tmp = numpy.zeros((count, nf), numpy.float32)
    #do segments
    for i in xrange(seg):
        tcps = my_cps[i:i+4]
        i0, i1 = i*n, (i+1)*n
        for j in xrange(count):
            sp_tmp = spline(vals[i:i+4], n, tcps[1].spline, tcps[2].spline,
                            curve=curve, p1=p1, p2=p2, p3=p3)
            sp_tmp = sp_tmp.transpose()
            tmp[j][i0:i1] = sp_tmp[j]
    #---end segments
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

    t = crange(0, 1, n)
    curve_mod = crange(0, cps[2]-cps[1], n, **kwargs) - crange(0, cps[2]-cps[1], n)
    curve_mod.resize(len(curve_mod),1)
    
    ta, ca, ba = splinea
    tb, cb, bb = splineb
    fa = (1-ta)*(1+ca)*(1+ba)
    fb = (1-ta)*(1-ca)*(1-ba)
    fc = (1-tb)*(1-cb)*(1+bb)
    fd = (1-tb)*(1+cb)*(1-bb)

    M = numpy.array([[-fa,4+fa-fb-fc,-4+fb+fc-fd,fd]
                    ,[2*fa,-6-2*fa+2*fb+fc,6-2*fb-fc+fd,-fd]
                    ,[-fa,fa-fb,fb,0]
                    ,[0,2,0,0]], numpy.float32)/2.0
    C = numpy.array(cps, numpy.float32)
    MxC = numpy.dot(M,C)
    S = numpy.zeros((len(t),4), numpy.float32)
    for i in xrange(len(t)):
        S[i] = [t[i]**3, t[i]**2, t[i], 1]
    result = numpy.dot(S, MxC)
    return result + curve_mod
#---end spline
