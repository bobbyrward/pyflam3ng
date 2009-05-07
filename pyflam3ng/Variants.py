

variation_registry = {}

def define_variation(class_name, xml_name, variables=None):
    class Var(object):
        def __init__(self, value=1.0, **kwargs):
            self.value = value

            if variables is not None:
                for var_name, default in variables.iteritems():
                    setattr(self, var_name, kwargs.get(var_name, default))

        def name(self):
            return xml_name

    c = Var
    c.__name__ = class_name

    variation_registry[xml_name] = c

    return c

Linear = define_variation('Linear', 'linear')
Sinusoidal = define_variation('Sinusoidal', 'sinusoidal')
Spherical = define_variation('Spherical', 'spherical')
Swirl = define_variation('Swirl', 'swirl')
Horseshoe = define_variation('Horseshoe', 'horseshoe')
Polar = define_variation('Polar', 'polar')
Handkerchief = define_variation('Handkerchief', 'handkerchief')
Heart = define_variation('Heart', 'heart')
Disc = define_variation('Disc', 'disc')
Spiral = define_variation('Spiral', 'spiral')
Hyperbolic = define_variation('Hyperbolic', 'hyperbolic')
Diamond = define_variation('Diamond', 'diamond')
Ex = define_variation('Ex', 'ex')
Julia = define_variation('Julia', 'julia')
Bent = define_variation('Bent', 'bent')
Waves = define_variation('Waves', 'waves')
Fisheye = define_variation('Fisheye', 'fisheye')
Popcorn = define_variation('Popcorn', 'popcorn')
Exponential = define_variation('Exponential', 'exponential')
Power = define_variation('Power', 'power')
Cosine = define_variation('Cosine', 'cosine')
Rings = define_variation('Rings', 'rings')
Fan = define_variation('Fan', 'fan')
Blob = define_variation('Blob', 'blob', {'high':1, 'low':0, 'waves':1, })
Pdj = define_variation('Pdj', 'pdj', {'a':0, 'c':0, 'b':0, 'd':0, })
Fan2 = define_variation('Fan2', 'fan2', {'y':1, 'x':0, })
Rings2 = define_variation('Rings2', 'rings2', {'val':0, })
Eyefish = define_variation('Eyefish', 'eyefish')
Bubble = define_variation('Bubble', 'bubble')
Cylinder = define_variation('Cylinder', 'cylinder')
Perspective = define_variation('Perspective', 'perspective', {'dist':0, 'angle':0, })
Noise = define_variation('Noise', 'noise')
Julian = define_variation('Julian', 'julian', {'dist':1, 'power':1, })
Juliascope = define_variation('Juliascope', 'juliascope', {'dist':1, 'power':1, })
Blur = define_variation('Blur', 'blur')
Gaussian_Blur = define_variation('Gaussian_Blur', 'gaussian_blur')
Radial_Blur = define_variation('Radial_Blur', 'radial_blur')
Pie = define_variation('Pie', 'pie', {'rotation':0, 'thickness':0, 'slices':6, })
Ngon = define_variation('Ngon', 'ngon', {'corners':2, 'circle':1, 'sides':5, 'power':3, })
Curl = define_variation('Curl', 'curl', {'c2':0, 'c1':1, })
Rectangles = define_variation('Rectangles', 'rectangles', {'y':1, 'x':1, })
Arch = define_variation('Arch', 'arch')
Tangent = define_variation('Tangent', 'tangent')
Square = define_variation('Square', 'square')
Rays = define_variation('Rays', 'rays')
Blade = define_variation('Blade', 'blade')
Secant2 = define_variation('Secant2', 'secant2')
Twintrian = define_variation('Twintrian', 'twintrian')
Cross = define_variation('Cross', 'cross')
Disc2 = define_variation('Disc2', 'disc2', {'twist':0, 'rot':0, })
Super_Shape = define_variation('Super_Shape', 'super_shape')
Flower = define_variation('Flower', 'flower', {'petals':0, 'holes':0, })
Conic = define_variation('Conic', 'conic', {'eccentricity':1, 'holes':0, })
Parabola = define_variation('Parabola', 'parabola', {'width':0, 'height':0, })
Bent2 = define_variation('Bent2', 'bent2', {'y':0, 'x':0, })
Bipolar = define_variation('Bipolar', 'bipolar', {'shift':0, })
Boarders = define_variation('Boarders', 'boarders')
Butterfly = define_variation('Butterfly', 'butterfly')
Cell = define_variation('Cell', 'cell', {'size':1, })
Cpow = define_variation('Cpow', 'cpow', {'i':0, 'r':1, 'power':1, })
Curve = define_variation('Curve', 'curve', {'ylength':1, 'xlength':1, 'yamp':1, 'xamp':1, })
Edisc = define_variation('Edisc', 'edisc')
Elliptic = define_variation('Elliptic', 'elliptic')
Escher = define_variation('Escher', 'escher', {'beta':0, })
Foci = define_variation('Foci', 'foci')
Lazysusan = define_variation('Lazysusan', 'lazysusan', {'twist':0, 'x':1, 'spin':0, 'y':1, 'space':0, })
Loonie = define_variation('Loonie', 'loonie')
Pre_Blur = define_variation('Pre_Blur', 'pre_blur')
Modulus = define_variation('Modulus', 'modulus', {'y':1, 'x':1, })
Oscilloscope = define_variation('Oscilloscope', 'oscilloscope')
Polar2 = define_variation('Polar2', 'polar2')
Popcorn2 = define_variation('Popcorn2', 'popcorn2', {'y':0, 'x':0, 'c':0, })
Scry = define_variation('Scry', 'scry')
Separation = define_variation('Separation', 'separation', {'y':0, 'x':0, 'xinside':0, 'yinside':0, })
Split = define_variation('Split', 'split', {'ysize':0, 'xsize':0, })
Splits = define_variation('Splits', 'splits', {'y':1, 'x':1, })
Stripes = define_variation('Stripes', 'stripes', {'warp':0, 'space':1, })
Wedge = define_variation('Wedge', 'wedge', {'count':0, 'swirl':0, 'hole':0, 'angle':0, })
Wedge_Julia = define_variation('Wedge_Julia', 'wedge_julia', {'count':0, 'dist':1, 'angle':0, 'power':2, })
Wedge_Sph = define_variation('Wedge_Sph', 'wedge_sph', {'count':0, 'swirl':0, 'hole':0, 'angle':0, })
Whorl = define_variation('Whorl', 'whorl', {'inside':1, 'outside':1, })
Waves2 = define_variation('Waves2', 'waves2', {'scalex':1, 'scaley':1, 'freqy':1, 'freqx':1, })

