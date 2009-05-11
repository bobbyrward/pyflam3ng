"""
Interpolation utility functions for generating vectors between control points.

This module includes functions for generating curved vectors between points,
periodic vectors that start and end at the same point, and smoothed TCB splines
for animation and interpolation.
"""

import numpy, math

valid_curves = ['lin', 'par', 'npar', 'sin', 'cos', 'hcos', 'sinh', 'tanh'
               ,'exp', 'plin', 'ppar']


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
        if isinstance(val, numpy.ndarray):
            self.val = val
        else:
            self.val = numpy.array(val, numpy.float32)
        self.time = time #placeholder - irregular grid not ready
        self.t = t
        self.c = c
        self.b = b

    def get_pad(self, target):
        """Returns a CP for padding interp with <4 points.

        Arguments:
            target  - CP's closest neighbor
        """
        dt = target.time - self.time
        dv = target.val - self.val
        return CP(self.val-dv, self.time-dt)

    def _get_spline(self):
        return self.t, self.c, self.b

    def _set_spline(self, params):
        self.t, self.c, self.b = params

    spline = property(_get_spline, _set_spline, doc="Spline parameters in a list")
#---end CP

class Vect(object):
    def __init__(self, cp0, cp1, curve='lin', p1=1, p2=0.5, p3=1):
        self.cps = [cp0, cp1]
        self._length = cp1.time - cp0.time
        self._curve = curve
        self.p1, self.p2, self.p3 = p1, p2, p3

    def update(self):
        self._length = self.cps[1].time - self.cps[0].time

    def _get_curve(self):
        return {'curve': self._curve, 'p1': self.p1, 'p2': self.p2, 'p3': self.p3}

    def _set_curve(self, curve, **kwargs):
        p1 = kwargs.get('p1', 1)
        p2 = kwargs.get('p2', 0.5)
        p3 = kwargs.get('p3', 1)
        if curve not in valid_curves:
            raise ValueError('Bad curve value')
        else:
            if curve in ['plin', 'ppar'] and (p2 <= 0 or p2 >= 1):
                raise ValueError('peak val must be between 0 and 1')
            elif curve=='ppar' and mode not in [0, 1, 2, 3]:
                raise ValueError('mode must be 0, 1, 2, or 3')
            elif curve in ['sin', 'cos'] and (p3 <= 0 or type(p3)<>int):
                raise ValueError('freq must be positive integer')
            self._curve = curve
            self.p1 = p1
            self.p2 = p2
            self.p3 = p3

    curve = property(_get_curve, _set_curve)

    def _get_length(self):
        return self._length

    length = property(_get_length)

    def _get_start(self):
        return self.cps[0]

    def _set_start(self, cp):
        self.cps[0] = cp
        self.update()

    start = property(_get_start, _set_start)

    def _get_end(self):
        return self.cps[1]

    def _set_end(self, cp):
        self.cps[1] = cp
        self.update()

    end = property(_get_end, _set_end)

class Spline():
    def __init__(self, cps=None, loop=False, time=50):
        if cps==None:
            self._cps = []
            self._vects = []
            self._length = 0
            self._count = 0
            self._looping = loop
        else:
            if isinstance(cps[0], CP):
                self._cps = cps
            else:
                self._cps = get_cps_from_list(cps, time)
            self._looping = loop
            if len(self._cps)>1:
                self._vects = self.setup_vects()
                if self._looping:
                    self._length = self._cps[-1].time
                else:
                    self._length = self._cps[-1].time
            self._count = self._cps[0].val.size

    def set_all_splines(self, t, c, b):
        for cp in self._cps:
            cp.spline = t, c, b

    def set_spline(self, index, t, c, b):
        if index < len(self._cps):
            cp[index].spline = t, c, b
        else:
            raise ValueError('index oob')

    def set_all_curves(self, curve, p1=1, p2=0.5, p3=1):
        if curve in valid_curves:
            for v in self._vects[1:-1]:
                v.curve = curve, p1, p2, p3
        else:
            raise ValueError('invalid curve type')

    def set_curve(self, curve, p1=1, p2=0.5, p3=1):
        if 0 < index < len(self._vects)-1:
            if curve in valid_curves:
                v[index].curve = curve, p1, p2, p3
            else:
                raise ValueError('invalid curve type')
        elif index==0 or index==len(self._vects)-1:
            raise ValueError('Edge vectors curves not used')
        else:
            raise ValueError('index oob')

    def add_cp(self, cp, index, dt=50):
        #make sure index is valid
        if not 0 <= index <= len(self._cps):
            raise ValueError('index oob')
        #make sure time is higher than prior time
        if isinstance(cp, CP):
            dt = cp.time - self._cps[index-1].time
            if not dt > 1:
                raise ValueError('CP time must be > time of previous CP')
        else:
            cp = CP(cp, self._cps[index-1].time+dt)
        #insert cp update cps that come after's times
        self._cps.insert(index, cp)
        for cp in self._cps[index+1:]:
            cp.time += dt
        self._length = self._cps[-1].time
        #check 5 different possibles
        if self._looping and index==0:
            #if it's a loop and first position, last segment loops to new 0
            self._vects.insert(index, Vect(self._cps[-1], self._cps[index]))
            self._vects[1].start = self._cps[index]
            self._vects[-1].end = self._cps[index]
        elif self._looping and index==len(self._cps):
            #if it's the last position and a loop, last segment start = new
            self._vects.append(Vect(self._cps[-1], self._cps[0]))
            self._vects[0].start = self._cps[-1]
            self._vects[-2].end = self._cps[-1]
        elif index==0:
            #if it's first in a flat, needs new pad
            pad = self._cps[0].get_pad(self._cps[1])
            self._vects.insert(index, Vect(pad, self._cps[0]))
            self._vects[1].start = self._cps[0]
        elif index==len(self._cps):
            #if it's end in a flat, needs new pad
            pad = self._cps[-1].get_pad(self._cps[-2])
            self._vects.append(Vect(self._cps[-1], pad))
            self._vects[-2].end = self._cps[-1]
        else:
            #middle
            self._vects.insert(index, Vect(self._cps[index], self._cps[index+1]))
            self._vects[index-1].end = self._cps[index]
            self._vects[index+1].start = self._cps[index]
    #---end

    def del_cp(self, index):
        #make sure index is valid
        if not 0 <= index < len(self._cps):
            raise ValueError('index oob')
        #remove cp at index and update times
        if index==0: dt = self._cps[index+1].time - self._cps[index].time
        else:        dt = self._cps[index].time - self._cps[index-1].time
        self._cps.pop(index)
        for cp in self._cps[index+1:]:
            cp.time -= dt
        self._length = self._cps[-1].time
        #check 5 possibles
        if self._looping and index==0:
            #if loop and 0, last ends at new 0
            self._vects.pop(0)
            self._vects[0].start = self._cps[-1]
            self._vects[-1].end = self._cps[0]
        elif self._looping and index==len(self._cps):
            #if loop and last, front starts at new last
            self._vects = self._vects[:-1]
            self._vects[0].start = self._cps[-1]
            self._vects[-1].end = self._cps[0]
        elif index==0:
            #if flat and 0, need new pad for start
            self._vects.pop(0)
            pad = self._cps[0].get_pad(self._cps[1])
            self._vects[0].start = pad
        elif index==len(self._cps):
            #if flat and last, last needs new pad for end
            self._vects = self.vects[:-1]
            pad = self._cps[-1].get_pad(self._cps[-2])
            self._vects[-1].end = pad
        else:
            #middle
            self._vects.pop(index)
            self._vects[index-1].end = self._cps[index]
            self._vects[index].start = self._cps[index]
    #---end

    def calculate(self):
        if len(self._cps) < 2:
            raise ValueError('need more cps first')
        tmp = numpy.zeros((self._count, self._length), numpy.float32)
        for i in xrange(1, len(self._vects)-1):
            i0 = self._vects[i].start.time
            i1 = self._vects[i].end.time
            tcps = [self._vects[i-1].start, self._vects[i].start
                   ,self._vects[i].end, self._vects[i+1].end]
            vals = numpy.zeros((4, self._count), numpy.float32)
            for j in xrange(4):
                vals[j] = tcps[j].val
            for j in xrange(self._count):
                tmp[j][i0:i1] = spline(vals[:,j], self._vects[i].length
                                      ,self._vects[i].start.spline
                                      ,self._vects[i].end.spline
                                      ,**self._vects[i].curve)
        return tmp        

    def setup_vects(self):
        if len(self._cps) < 2:
            raise ValueError('need more cps first')
        cps = list(self._cps[:])
        if self._looping:
            seg = len(cps)
            cps.insert(0, cps[-1])
            cps.append(cps[1])
            cps.append(cps[2])
        else:
            seg = len(cps)-1
            cps.insert(0, cps[0].get_pad(cps[1]))
            cps.append(cps[-1].get_pad(cps[-2]))
        tmp = []
        for i in xrange(seg+2):
            tmp.append(Vect(cps[i], cps[i+1]))
        return tmp

    def _get_vects(self):
        return self._vects

    vects = property(_get_vects)

    def _get_cps(self):
        return self._cps

    def _set_cps(self, cps):
        if isinstance(cps[0], CP):
            self._cps = cps
        else:
            self._cps = get_cps_from_list(cps)
        self.update()

    cps = property(_get_cps, _set_cps)

    def _get_length(self):
        return self._length

    length = property(_get_length)
        

def get_cps_from_list(lst, time=50):
    tmp = []
    for i in xrange(len(lst)):
        tmp.append(CP(lst[i], i*time))
    return tmp

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

    if type(my_cps[0].val)==int or type(my_cps[0])==float:
        count = 1
    else:
        count = my_cps[0].val.size

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
        my_cps.insert(0, my_cps[-1])
        my_cps.append(my_cps[1])
        my_cps.append(my_cps[2])
    else:
        pad1 = my_cps[0].get_pad(my_cps[1])
        pad2 = my_cps[-1].get_pad(my_cps[-2])
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
            tvals = vals[i:i+4, j]
            sp_tmp = spline(tvals, n, tcps[1].spline, tcps[2].spline,
                            curve=curve, p1=p1, p2=p2, p3=p3)
            tmp[j][i0:i1] = sp_tmp
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
    MxC = numpy.dot(M,cps)
    S = numpy.zeros((len(t),4), numpy.float32)
    for i in xrange(len(t)):
        S[i] = [t[i]**3, t[i]**2, t[i], 1]
    result = numpy.dot(S, MxC)
    return result + curve_mod
#---end spline
