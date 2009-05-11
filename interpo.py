from pyflam3ng import *
from pyflam3ng.vector_utils import Spline, CP
import numpy

defaults = {'nframes': 50
           ,'looping': False
           ,'curve': {'curve': 'lin', 'p1': 1, 'p2': 0.5, 'p3': 1}
           ,'spline': {'t': 0, 'c': -1, 'b': -1}
           ,'p_space': 'polar'}

parametric_vars = [v for v, val in variation_registry.items() if val]

class Interpo(object):
    def __init__(self, genomes=None, loop=False, nframes=50):
        self._looping = loop
        self.nframes = nframes
        self._length = None
        self.brightness = None
        self.contrast = None
        self.gamma = None
        self.vibrancy = None
        self.rotate = None
        self.scale = None
        self.symmetry = None
        self.center = None
        self.xforms = []
        self.times = []
        self.genomes = []
        self._frames = []

        if genomes:
            for i, g in enumerate(genomes):
                if not isinstance(g, Genome):
                    raise TypeError('needs to be genome obj')
                self.genomes.append(g)
                self.times.append(i*self.nframes)
        if self._looping: self.segments = len(self.genomes)
        else:             self.segments = len(self.genomes)-1
        self._length = self.segments * nframes
        if len(self.genomes) > 1: self.update_all()

    def build_frames(self):
        self._frames = []
        for i in xrange(self._length):
            self._frames.append(Genome(False))
        #calculate splines
        tmp_bri = self.brightness.calculate()
        tmp_con = self.contrast.calculate()
        tmp_gam = self.gamma.calculate()
        tmp_vib = self.vibrancy.calculate()
        tmp_sym = self.symmetry.calculate()
        tmp_rot = self.rotate.calculate()
        tmp_sca = self.scale.calculate()
        tmp_cen = self.center.calculate()
        tmp_xfs = []
        for xf in self.xforms:
            xf_buff = {'weight': xf.weight.calculate()
                      ,'color': xf.color.calculate()
                      ,'symmetry': xf.symmetry.calculate()
                      ,'opacity': xf.opacity.calculate()
                      ,'o': xf.o.calculate()
                      ,'x': xf.x.calculate()
                      ,'y': xf.y.calculate()
                      ,'vars': {}}
            for var in xf.vars:
                var_buff = {'weight': var.weight.calculate()}
                if var.name in parametric_vars:
                    for key, value in var.variables.items():
                        var_buff.setdefault(key, value.calculate())
                xf_buff['vars'].setdefault(var.name, var_buff)
            tmp_xfs.append(xf_buff)
        #---end spline calc
        #frame create
        for i, g in enumerate(self._frames):
            g.brightness = tmp_bri[0][i]
            g.contrast = tmp_con[0][i]
            g.gamma = tmp_gam[0][i]
            g.vibrancy = tmp_vib[0][i]
            g.symmetry = tmp_sym[0][i]
            g.rotate = tmp_rot[0][i]
            g.pixels_per_unit = tmp_sca[0][i]
            g.center.fill(tuple(tmp_cen[:,i]))
            for j, xf in enumerate(tmp_xfs):
                if xf['weight'][0][i] > 0.0:
                #if weight not 0, otherwise you can ignore
                    g.xforms.append(Xform())
                    g.xforms[-1].weight = xf['weight'][0][i]
                    g.xforms[-1].color = xf['color'][0][i]
                    g.xforms[-1].symmetry = xf['symmetry'][0][i]
                    g.xforms[-1].opacity = xf['opacity'][0][i]
                    g.xforms[-1].o = xf['o'][:,i]
                    g.xforms[-1].x = xf['x'][:,i]
                    g.xforms[-1].y = xf['y'][:,i]
                    for var, attrs in xf['vars'].items():
                        if attrs['weight'][0][i] > 0.0:
                            g.xforms[-1].vars.set_variation(var, attrs['weight'][0][i])
                            for varib, value in attrs.items():
                                if varib <> 'weight':
                                    g.xforms[-1].vars.set_variable(var, varib, value[0][i])
                    #---end variants
            #---end xforms
        #---end frame create

    def _get_frames(self):
        return self._frames

    frames = property(_get_frames)

    def update_keyframe(self, keyid, key):
        #alter the CPs - splines should update
        pass

    def add_keyframe(self, index, key):
        pass

    def del_keyframe(self, index):
        pass

    def _get_keyframes(self):
        pass

    keyframes = property(_get_keyframes)

    def _get_length(self):
        return self._length

    length = property(_get_length)

    def _get_looping(self):
        return self._looping

    def _set_looping(self, loop):
        if loop: self._looping = True
        else:    self._looping = False
        #self.update_loop()

    looping = property(_get_looping, _set_looping)

    def _get_splines(self):
        #return splines - in a dict?
        pass

    splines = property(_get_splines)

    #update methods
    def update_all(self):
        #update all keyframes
        tmp_bri = []
        tmp_con = []
        tmp_gam = []
        tmp_vib = []
        tmp_rot = []
        tmp_sca = []
        tmp_sym = []
        tmp_cen = []
        #check for pads
        for i in xrange(len(self.genomes)-1):
            self.genomes[i], self.genomes[i+1] = check_for_pad(self.genomes[i], self.genomes[i+1])
        if self._looping:
            self.genomes[-1], self.genomes[0] = check_for_pad(self.genomes[-1], self.genomes[0])

        maxx = max([len(g.xforms) for g in self.genomes])
        for i in xrange(maxx):
            xfvars = []
            for g in self.genomes:
                if i < len(g.xforms):
                    xfvars = set(xfvars).union(g.xforms[i].get_attribs()['vars'].keys())
            int_xf = IntXf()
            for v in xfvars:
                int_xf.add_var(v)
            self.xforms.append(int_xf)

        for t, g in enumerate(self.genomes):
        #go through all genomes and make spline of frame vals
            attrs = g.get_attribs()
            center = numpy.array(list(attrs['center'][0].tolist()))
            tmp_bri.append(CP(attrs['brightness'], self.times[t]))
            tmp_con.append(CP(attrs['contrast'], self.times[t]))
            tmp_gam.append(CP(attrs['gamma'], self.times[t]))
            tmp_vib.append(CP(attrs['vibrancy'], self.times[t]))
            tmp_rot.append(CP(attrs['rotate'], self.times[t]))
            tmp_sca.append(CP(attrs['scale'], self.times[t]))
            tmp_sym.append(CP(attrs['symmetry'], self.times[t]))
            tmp_cen.append(CP(center, self.times[t]))
            #go through all xforms at index and get the variants used
            for i, xf in enumerate(self.xforms):
                xf_attrs = g.xforms[i].get_attribs()
                if i < len(g.xforms):
                    xf.weight_b.append(CP(xf_attrs['weight'], self.times[t]))
                    xf.color_b.append(CP(xf_attrs['color'], self.times[t]))
                    xf.symmetry_b.append(CP(xf_attrs['symmetry'], self.times[t]))
                    xf.opacity_b.append(CP(xf_attrs['opacity'], self.times[t]))
                    xf.o_b.append(CP(xf_attrs['o'], self.times[t]))
                    xf.x_b.append(CP(xf_attrs['x'], self.times[t]))
                    xf.y_b.append(CP(xf_attrs['y'], self.times[t]))
                    for vari in xf.vars:
                        if vari.name in xf_attrs['vars'].keys():
                            vari.weight_b.append(CP(xf_attrs['vars'][vari.name], self.times[t]))
                            v_attrs = xf_attrs['variables']
                            if vari.name in parametric_vars:
                                for key in vari.variables.keys():
                                    vari.variables_b[key].append(CP(v_attrs[vari.name][key], self.times[t]))
                        else:
                            vari.weight_b.append(CP(0, self.times[t]))
                            if vari.name in parametric_vars:
                                for key, value in vari.variables.items():
                                    vari.variables_b[key].append(CP(0, self.times[t]))
                    #---end variants
                else:
                    xf.weight_b.append(CP(0, self.times[t]))
                    xf.color_b.append(CP(0, self.times[t]))
                    xf.symmetry_b.append(CP(0, self.times[t]))
                    xf.opacity_b.append(CP(0, self.times[t]))
                    xf.o_b.append(CP(Point(0.0, 0.0), self.times[t]))
                    xf.x_b.append(CP(Point(0.0, 1.0), self.times[t]))
                    xf.y_b.append(CP(Point(1.0, 0.0), self.times[t]))
                    for vari in xf.vars:
                        vari.weight_b.append(CP(0, self.times[t]))
                        if vari.name in parametric_vars:
                            for key, value in vari.variables.items():
                                vari.variables_b[key].append(CP(0, self.times[t]))
                    #---end variants
        #---end CP create
        #---start spline create
        self.brightness = Spline(tmp_bri, self._looping)
        self.contrast = Spline(tmp_con, self._looping)
        self.gamma = Spline(tmp_gam, self._looping)
        self.vibrancy = Spline(tmp_vib, self._looping)
        self.rotate = Spline(tmp_rot, self._looping)
        self.scale = Spline(tmp_sca, self._looping)
        self.symmetry = Spline(tmp_sym, self._looping)
        self.center = Spline(tmp_cen, self._looping)
        for xf in self.xforms:
            xf.weight = Spline(xf.weight_b, self._looping)
            xf.color = Spline(xf.color_b, self._looping)
            xf.symmetry = Spline(xf.symmetry_b, self._looping)
            xf.opacity = Spline(xf.opacity_b, self._looping)
            xf.o = Spline(xf.o_b, self._looping)
            xf.x = Spline(xf.x_b, self._looping)
            xf.y = Spline(xf.y_b, self._looping)
            for vari in xf.vars:
                vari.weight = Spline(vari.weight_b, self._looping)
                if vari.name in parametric_vars:
                    for key, value in vari.variables_b.items():
                        vari.variables[key] = Spline(value, self._looping)
            #---end variants
        #---end spline create
        self._frames = None

    def update_loop(self):
        #adjust for loop turning on or off
        #if turned on - add segment and change edge vects to point to loops
        #if turned off - remove loopback seg and change edge vects to pads
        pass

    def update_index(self, index):
        #update cp and surrounding area
        pass

class IntXf(object):
    def __init__(self):
        self.weight = None
        self.color = None
        self.symmetry = None
        self.opacity = None
        self.o = None
        self.x = None
        self.y = None
        self.vars = []
        self.weight_b = []
        self.color_b = []
        self.symmetry_b = []
        self.opacity_b = []
        self.o_b = []
        self.x_b = []
        self.y_b = []

    def add_var(self, name):
        if name not in [v.name for v in self.vars]:
            self.vars.append(IntVar(name))
        else:
            pass

    def add_dict_to_buff(self, attrs, time):
        self.weight_b.append(CP(attrs['weight'], time))
        self.color_b.append(CP(attrs['color'], time))
        self.symmetry_b.append(CP(attrs['symmetry'], time))
        self.opacity_b.append(CP(attrs['opacity'], time))
        self.o_b.append(CP(attrs['o'], time))
        self.x_b.append(CP(attrs['x'], time))
        self.y_b.append(CP(attrs['y'], time))
        for v in self.vars:
            if v.name in attrs['vars'].keys():
                v.weight_b.append(CP(attrs['vars'][v.name], time))
                if v.name in parametric_vars:
                    vvaribs = attrs['variables'][v.name]
                    for var, varvalue in vvaribs:
                        v.variables[var].append(CP(varvalue, time))
            else:
                v.weight_b.append(CP(0, time))
                if v.name in parametric_vars:
                    vvaribs = attrs['variables'][v.name]
                    for var, varvalue in vvaribs:
                        v.variables[var].append(CP(0, time))
            #---end branch
        #---end for loop
        pass

class IntVar(object):
    def __init__(self, name):
        if name not in variation_registry.keys():
            raise ValueError('invalid variant name')
        self.name = name
        self.weight = None
        self.variables = {}
        self.weight_b = []
        self.variables_b = {}
        if name in parametric_vars:
            for key in variation_registry[name].keys():
                self.variables.setdefault(key, None)
                self.variables_b.setdefault(key, [])




def check_for_pad(k0, k1):
    k0x, k1x = len(k0.xforms), len(k1.xforms)
    if k0x > k1x: #pad 1
        tmp = k0.clone()
        for i in xrange(k1x, k0x):
            tmp.xforms.append(k1.xforms[i].get_pad())
        k0 = tmp
    else:
        tmp = k1.clone()
        for i in xrange(k0x, k1x):
            tmp.xforms.append(k0.xforms[i].get_pad())
        k1 = tmp
    return k0, k1
