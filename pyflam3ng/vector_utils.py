"""
Interpolation utility functions for generating vectors between control points.

This module includes functions for generating curved vectors between points,
periodic vectors that start and end at the same point, and smoothed TCB splines
for animation and interpolation.
"""

import numpy, math, copy
from util import spline

valid_curves = ['lin', 'par', 'npar', 'sin', 'cos', 'hcos', 'sinh', 'tanh',
                'exp', 'plin', 'ppar']

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
        self.ti, self.to = t,t
        self.ci, self.co = c,c
        self.bi, self.bo = b,b

    def get_pad(self, target):
        """Returns a CP for padding interp with <4 points.

        Arguments:
            target  - CP's closest neighbor
        """
        dt = target.time - self.time
        dv = target.val - self.val
        return CP(self.val-dv, self.time-dt)

    def _get_spline(self):
        return self.ti, self.ci, self.bi

    def _set_spline(self, params):
        self.ti, self.ci, self.bi = params
        self.to, self.co, self.bo = params

    spline = property(_get_spline, _set_spline, doc="Spline parameters in a list")

    def _get_spline_in(self):
        return self.ti, self.ci, self.bi

    def _set_spline_in(self, params):
        self.ti, self.ci, self.bi = params

    spline_in = property(_get_spline_in, _set_spline_in)

    def _get_spline_out(self):
        return self.to, self.co, self.bo

    def _set_spline_out(self, params):
        self.to, self.co, self.bo = params

    spline_out = property(_get_spline_out, _set_spline_out)
#---end CP

class Vect(object):
    def __init__(self, cp0, cp1, curve='lin', amp=0, freq=1, slope=1,
                 peak=0.5, mode=0):

        self.cps = [cp0, cp1]
        self._length = cp1.time - cp0.time
        self._curve = curve
        self.amp, self.freq, self.slope = amp, freq, slope
        self.peak, self.mode = peak, mode

    def update(self):
        self._length = self.cps[1].time - self.cps[0].time

    def _get_curve(self):
        return self._curve, self.amp, self.freq, self.slope, self.peak, self.mode

    def _set_curve(self, curve, amp=0, freq=1, slope=1, peak=0.5, mode=0):
        if curve not in valid_curves:
            raise ValueError('Bad curve value')
        else:
            if curve in ['plin', 'ppar'] and (peak <= 0 or peak >= 1):
                raise ValueError('peak val must be between 0 and 1')
            elif curve=='ppar' and mode not in [0, 1, 2, 3]:
                raise ValueError('mode must be 0, 1, 2, or 3')
            elif curve in ['sin', 'cos'] and (freq <= 0 or type(freq)<>int):
                raise ValueError('freq must be positive integer')
            self._curve = curve
            self.amp = amp
            self.freq = freq
            self.slope = slope
            self.peak = peak
            self.mode = mode

    curve = property(_get_curve, _set_curve)

    def __len__(self):
        return self._length

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
            self._nframes = time
        else:
            self._nframes = time
            if isinstance(cps[0], CP):
                self._cps = cps
            else:
                self._cps = get_cps_from_list(cps, time)
            self._looping = loop
            if len(self._cps)>1:
                self._vects = self.setup_vects()
                if self._looping:
                    self._length = self._cps[-1].time + time
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

    def set_all_curves(self, curve, amp=0, freq=1, slope=1, peak=0.5, mode=0):
        if curve in valid_curves:
            for v in self._vects[1:-1]:
                v.curve = curve, amp, freq, slope, peak, mode
        else:
            raise ValueError('invalid curve type')

    def set_curve(self, curve, amp=0, freq=1, slope=1, peak=0.5, mode=0):
        if 0 < index < len(self._vects)-1:
            if curve in valid_curves:
                v[index].curve = curve, amp, freq, slope, peak, mode
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
            times = numpy.zeros(4, numpy.int32)
            ti, ci, bi = self._vects[i].start.spline_out
            to, co, bo = self._vects[i].end.spline_in
            curve, amp, freq, slope, peak, mode = self._vects[i].curve
            if   curve=='lin':  curve=-1
            elif curve=='par':  curve=0
            elif curve=='npar': curve=1
            elif curve=='hcos': curve=2
            elif curve=='sinh': curve=3
            elif curve=='tanh': curve=4
            elif curve=='exp':  curve=5
            elif curve=='cos':  curve=6
            elif curve=='sin':  curve=7
            elif curve=='plin': curve=8
            elif curve=='ppar': curve=9
            else: raise ValueError('no such curve')

            for j in xrange(4):
                vals[j] = tcps[j].val
                times[j] = tcps[j].time
            for j in xrange(self._count):
                tmp[j][i0:i1] = spline(vals[:,j], times, ti, ci, bi, to, co, bo
                                      ,curve, amp, freq, slope, peak, mode)
        return tmp

    def setup_vects(self):
        if len(self._cps) < 2:
            raise ValueError('need more cps first')
        cps = list(self._cps[:])
        if self._looping:
            seg = len(cps)
            cps.insert(0, copy.deepcopy(cps[-1]))
            cps[0].time = cps[1].time - self._nframes
            cps.append(copy.deepcopy(cps[1]))
            cps[-1].time = cps[-2].time + self._nframes
            cps.append(cps[2])
            cps[-1].time = cps[-2].time + self._nframes
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

    def __len__(self):
        return self._length

def get_cps_from_list(lst, time=50):
    tmp = []
    for i in xrange(len(lst)):
        tmp.append(CP(lst[i], i*time))
    return tmp

def get_spline(my_cps, n=50, loop=False, curve='lin', amp=0, freq=1, slope=1,
               peak=0.5, mode=0):
    """Takes list CPs and returns full spline.

    Arguments:
        my_cps  - List of CP objects. All vals must have same dimensions.
        loop    - Does the animation loop?
        curve   - Curve shape. This will eventually be done per-segment.
        amp, freq, mode,  - Curve params.
    """
    if len(my_cps)<2:
        raise ValueError('Need 2 or more CPs')

    #Segments is the number of interps to do, 1 less than #cps when not looping
    if loop: seg = len(my_cps)
    else:    seg = len(my_cps)-1

    if type(my_cps[0].val)==int or type(my_cps[0])==float:
        count = 1
    else:
        count = my_cps[0].val.size

    vals = numpy.zeros((seg+3, count), dtype=numpy.float32)
    times = numpy.zeros(seg+3, dtype=numpy.int32)

    if   curve=='lin':  curve=-1
    elif curve=='par':  curve=0
    elif curve=='npar': curve=1
    elif curve=='hcos': curve=2
    elif curve=='sinh': curve=3
    elif curve=='tanh': curve=4
    elif curve=='exp':  curve=5
    elif curve=='cos':  curve=6
    elif curve=='sin':  curve=7
    elif curve=='plin': curve=8
    elif curve=='ppar': curve=9
    else: raise ValueError('no such curve')

    #examples with [0, 1, 2, 3] - remember n-1, n, n+1, n+2 for spline
    #  looping - (3,) 0, 1, 2, 3, 0, (1) (not interped, just used for spline)
    #  not - (pad0,) 0, 1, 2, 3, (pad3) (not interped)
    if loop:
        vals[0] = my_cps[-1].val
        times[0] = my_cps[0].time-n
        for i in xrange(len(my_cps)):
            vals[i+1] = my_cps[i].val
            times[i+1] = my_cps[i].time
        vals[-2] = my_cps[0].val
        times[-2] = my_cps[-3].time+n
        vals[-1] = my_cps[1].val
        times[-1] = my_cps[-3].time+2*n
        my_cps.insert(0, my_cps[-1])
        my_cps.append(my_cps[1])
        my_cps.append(my_cps[2])
    else:
        pad1 = my_cps[0].get_pad(my_cps[1])
        pad2 = my_cps[-1].get_pad(my_cps[-2])
        vals[0] = pad1.val
        times[0] = pad1.time
        for i in xrange(len(my_cps)):
            vals[i+1] = my_cps[i].val
            times[i+1] = my_cps[i].val
        vals[-1] = pad2.val
        vals[-1] = pad2.time
        my_cps.insert(0, pad1)
        my_cps.append(pad2)
    nf = times[-2]

    tmp = numpy.zeros((count, nf), dtype=numpy.float32)
    #do segments
    for i in xrange(seg):
        tcps = my_cps[i:i+4]
        i0, i1 = i*n, (i+1)*n
        for j in xrange(count):
            ti, ci, bi, to, co, bo = tcps[1].spline_in, tcps[2].spline_out
            sp_tmp = spline(vals[i:i+4,j], times[i:i+4], ti, ci, bi, to, co, bo,
                            curve, amp, freq, slope, peak, mode)
            tmp[j][i0:i1] = sp_tmp
    #---end segments
    return tmp
#---end get_spline
