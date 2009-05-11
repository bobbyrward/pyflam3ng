from pyflam3ng import Genome, variation_registry
from vector_utils import Spline, CP
import numpy

defaults = {'nframes': 50
           ,'looping': False
           ,'curve': {'curve': 'lin', 'p1': 1, 'p2': 0.5, 'p3': 1}
           ,'spline': {'t': 0, 'c': -1, 'b': -1}
           ,'p_space': 'polar'}

parametric_vars = [v for v, val in variation_registry.items() if val] 

class Variant(object):
    def __init__(self, frame, name, attrs):
        self.name = name
        self.cps = {}
        for key, value in attrs.items():
            self.cps.setdefault(key, CP(value, frame.time))

class Xform(object):
    def __init__(self, frame, xid, attrs):
        self.id = xid
        self.cps = {}
        self.coefs = {}
        self.vars = {}
        for key, value in attrs.items():
            if key in ['o', 'x', 'y']:
                self.coefs.setdefault(key, CP(value, frame.time))
            elif key=='vars':
                for variant, vweight in value.items():
                    variant_vals = {variant: vweight}
                    if key in attrs['variables']:
                        for varkey, varval in attrs['variables'][variant]:
                            variant_vals.setdefault(varkey, varval)
                    self.vars.setdefault(variant, Variant(frame, variant, variant_vals))
            elif key=='variables':
                pass
            else:
                self.cps.setdefault(key, CP(value, frame.time))
        self.cps.setdefault('vars', self.vars)

class Keyframe(object):
    def __init__(self, genome, time=0):
        self._genome = genome
        self._time = time
        self._xforms = []
        self.update_cps()

    def _get_attribs(self):
        return self._genome.get_attribs()

    attribs = property(_get_attribs)

    def _get_genome(self):
        return self._genome

    def _set_genome(self, genome):
        if not isinstance(genome, Genome):
            raise TypeError('genome must be a valid pyflam3 Genome')
        self._genome = genome
        self.update_cps()

    genome = property(_get_genome, _set_genome)

    def _get_time(self):
        return self._time

    def _set_time(self, time):
        self._time = time
        self.update_cps()
    
    time = property(_get_time, _set_time)

    def _get_cps(self):
        return self._cps

    cps = property(_get_cps)

    def update_cps(self):
        attribs = self.attribs
        tmp_cps = {}
        for key, value in attribs.items():
            if key=='xforms':
                tmp_xcps = {}
                for xid, xattr in value.items():
                    self._xforms.append(Xform(self, xid, xattr))
                tmp_cps.setdefault(key, self._xforms)
            else:
                tmp_cps.setdefault(key, CP(value, self._time))
        self._cps = tmp_cps.copy()

class Interpo(object):
    def __init__(self, keyframes=None, genomes=None, **kwargs):
        self._keyframes = []
        self.splines = {}
        self.nframes = kwargs.get('nframes', defaults['nframes'])
        self.looping = kwargs.get('looping', defaults['looping'])
        self.curve = kwargs.get('curve', defaults['curve'])
        self.spline = kwargs.get('spline', defaults['spline'])
        if keyframes and genomes:
            raise ValueError('can only have keyframes or genomes, not both')
        if keyframes:
            for i in xrange(len(keyframes)):
                if isinstance(keyframes[i], Keyframe):
                    if i <> 0:
                        if keyframes[i].time <= keyframes[i-1].time:
                            raise ValueError('times must be sequential')
                        self._keyframes.append(keyframes[i])
                    else:
                        if keyframes[i].time <> 0:
                            raise ValueError('first keyframe must be t=0')
                        self._keyframes.append(keyframes[i])
                else:
                    raise ValueError('keyframes must be keyframes')
        if genomes:
            for i in xrange(len(genomes)):
                if isinstance(genomes[i], Genome):
                    self._keyframes.append(Keyframe(genomes[i], i*self.nframes))
                else:
                    raise TypeError('genomes must be valid pyflam3ng Genomes')
        #---end branch
        self._length = self._keyframes[-1].time
        if len(self._keyframes) > 1:
            self.update()

    def _get_frames(self):
        if len(self._keyframes) < 2:
            raise ValueError('need more keyframes first')
        return self._frames

    def update(self):
        self.splines = {}
        variants_used = []
        if len(self._keyframes) < 2:
            raise ValueError('need more keyframes first')
        #pad xforms
        for i in xrange(len(self._keyframes)-1):
            check_for_pad(self._keyframes[i], self.keyframes[i+1])
        if self.looping:
            check_for_pad(self._keyframes[-1], self.keyframes[0])
        #figure out max # xforms that need kept track of
        maxx = max([len(k.genome.xforms) for k in self._keyframes])
        #get active variants per xform
        for i in xrange(maxx):
            tmp = []
            for k in self._keyframes:
                if i < len(k._xforms):
                    tmp = set(tmp).union(k._xforms[i].vars.keys())
            variants_used.append(tmp)

        #Get CPs for splines
        #first get frame attribs
        cplist = {}
        for count, frame in enumerate(self._keyframes):
            for key, value in frame.cps.items():
                if key <> 'xforms':
                    if key not in cplist.keys():
                        tmp = numpy.zeros(len(self._keyframes), CP)
                        tmp[count] = value
                        cplist.setdefault(key, tmp)
                    else:
                        cplist[key][count] = value
                else:
                    #go through maxx, if nothing there use 0s for defaults
                    for i in xrange(maxx):
                        if i < len(k._xforms):
                            for var in variants_used:
                                if var in k._xforms[i].vars.keys():
                                    
                                    
                        #go through union of variants, in nothing use 0s for defaults

                    #for xf, cps in value.items():
        return cplist
        #make spline dict
        #for 

        #go through maxx, if nothing there use 0s for defaults
            #go through union of variants, in nothing use 0s for defaults
        pass

    def _get_length(self):
        return self._length

    length = property(_get_length)

    def _get_keyframes(self):
        return self._keyframes

    def _set_keyframes(self, keyframes):
        self._keyframes = []
        for k in keyframes:
            if not isinstance(k, Keyframe):
                raise TypeError('need to be keyframes')
            else:
                self._keyframes.append(k)
        self.update()

    keyframes = property(_get_keyframes, _set_keyframes)


def check_for_pad(k0, k1):
    k0x, k1x = len(k0.genome.xforms), len(k1.genome.xforms)
    if k0x > k1x: #pad 1
        tmp = k0.genome.clone()
        for i in xrange(k1x, k0x):
            tmp.xforms.append(k1.genome.xforms[i].get_pad())
        k0.genome = tmp
    else:
        tmp = k1.genome.clone()
        for i in xrange(k0x, k1x):
            tmp.xforms.append(k0.genome.xforms[i].get_pad())
        k1.genome = tmp   
