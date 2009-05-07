
class Var_Linear(Object):
	def __init__(self, value=1.0):
		self.name = 'linear'
		self.value = value


class Var_Sinusoidal(Object):
	def __init__(self, value=1.0):
		self.name = 'sinusoidal'
		self.value = value


class Var_Spherical(Object):
	def __init__(self, value=1.0):
		self.name = 'spherical'
		self.value = value


class Var_Swirl(Object):
	def __init__(self, value=1.0):
		self.name = 'swirl'
		self.value = value


class Var_Horseshoe(Object):
	def __init__(self, value=1.0):
		self.name = 'horseshoe'
		self.value = value


class Var_Polar(Object):
	def __init__(self, value=1.0):
		self.name = 'polar'
		self.value = value


class Var_Handkerchief(Object):
	def __init__(self, value=1.0):
		self.name = 'handkerchief'
		self.value = value


class Var_Heart(Object):
	def __init__(self, value=1.0):
		self.name = 'heart'
		self.value = value


class Var_Disc(Object):
	def __init__(self, value=1.0):
		self.name = 'disc'
		self.value = value


class Var_Spiral(Object):
	def __init__(self, value=1.0):
		self.name = 'spiral'
		self.value = value


class Var_Hyperbolic(Object):
	def __init__(self, value=1.0):
		self.name = 'hyperbolic'
		self.value = value


class Var_Diamond(Object):
	def __init__(self, value=1.0):
		self.name = 'diamond'
		self.value = value


class Var_Ex(Object):
	def __init__(self, value=1.0):
		self.name = 'ex'
		self.value = value


class Var_Julia(Object):
	def __init__(self, value=1.0):
		self.name = 'julia'
		self.value = value


class Var_Bent(Object):
	def __init__(self, value=1.0):
		self.name = 'bent'
		self.value = value


class Var_Waves(Object):
	def __init__(self, value=1.0):
		self.name = 'waves'
		self.value = value


class Var_Fisheye(Object):
	def __init__(self, value=1.0):
		self.name = 'fisheye'
		self.value = value


class Var_Popcorn(Object):
	def __init__(self, value=1.0):
		self.name = 'popcorn'
		self.value = value


class Var_Exponential(Object):
	def __init__(self, value=1.0):
		self.name = 'exponential'
		self.value = value


class Var_Power(Object):
	def __init__(self, value=1.0):
		self.name = 'power'
		self.value = value


class Var_Cosine(Object):
	def __init__(self, value=1.0):
		self.name = 'cosine'
		self.value = value


class Var_Rings(Object):
	def __init__(self, value=1.0):
		self.name = 'rings'
		self.value = value


class Var_Fan(Object):
	def __init__(self, value=1.0):
		self.name = 'fan'
		self.value = value


class Var_Blob(Object):
	def __init__(self, value=1.0, variables={'high':1, 'low':0, 'waves':1, }):
		self.name = 'blob'
		self.value = value
		self.variables = variables


class Var_Pdj(Object):
	def __init__(self, value=1.0, variables={'a':0, 'c':0, 'b':0, 'd':0, }):
		self.name = 'pdj'
		self.value = value
		self.variables = variables


class Var_Fan2(Object):
	def __init__(self, value=1.0, variables={'y':1, 'x':0, }):
		self.name = 'fan2'
		self.value = value
		self.variables = variables


class Var_Rings2(Object):
	def __init__(self, value=1.0, variables={'val':0, }):
		self.name = 'rings2'
		self.value = value
		self.variables = variables


class Var_Eyefish(Object):
	def __init__(self, value=1.0):
		self.name = 'eyefish'
		self.value = value


class Var_Bubble(Object):
	def __init__(self, value=1.0):
		self.name = 'bubble'
		self.value = value


class Var_Cylinder(Object):
	def __init__(self, value=1.0):
		self.name = 'cylinder'
		self.value = value


class Var_Perspective(Object):
	def __init__(self, value=1.0, variables={'dist':0, 'angle':0, }):
		self.name = 'perspective'
		self.value = value
		self.variables = variables


class Var_Noise(Object):
	def __init__(self, value=1.0):
		self.name = 'noise'
		self.value = value


class Var_Julian(Object):
	def __init__(self, value=1.0, variables={'dist':1, 'power':1, }):
		self.name = 'julian'
		self.value = value
		self.variables = variables


class Var_Juliascope(Object):
	def __init__(self, value=1.0, variables={'dist':1, 'power':1, }):
		self.name = 'juliascope'
		self.value = value
		self.variables = variables


class Var_Blur(Object):
	def __init__(self, value=1.0):
		self.name = 'blur'
		self.value = value


class Var_Gaussian_Blur(Object):
	def __init__(self, value=1.0):
		self.name = 'gaussian_blur'
		self.value = value


class Var_Radial_Blur(Object):
	def __init__(self, value=1.0):
		self.name = 'radial_blur'
		self.value = value


class Var_Pie(Object):
	def __init__(self, value=1.0, variables={'rotation':0, 'thickness':0, 'slices':6, }):
		self.name = 'pie'
		self.value = value
		self.variables = variables


class Var_Ngon(Object):
	def __init__(self, value=1.0, variables={'corners':2, 'circle':1, 'sides':5, 'power':3, }):
		self.name = 'ngon'
		self.value = value
		self.variables = variables


class Var_Curl(Object):
	def __init__(self, value=1.0, variables={'c2':0, 'c1':1, }):
		self.name = 'curl'
		self.value = value
		self.variables = variables


class Var_Rectangles(Object):
	def __init__(self, value=1.0, variables={'y':1, 'x':1, }):
		self.name = 'rectangles'
		self.value = value
		self.variables = variables


class Var_Arch(Object):
	def __init__(self, value=1.0):
		self.name = 'arch'
		self.value = value


class Var_Tangent(Object):
	def __init__(self, value=1.0):
		self.name = 'tangent'
		self.value = value


class Var_Square(Object):
	def __init__(self, value=1.0):
		self.name = 'square'
		self.value = value


class Var_Rays(Object):
	def __init__(self, value=1.0):
		self.name = 'rays'
		self.value = value


class Var_Blade(Object):
	def __init__(self, value=1.0):
		self.name = 'blade'
		self.value = value


class Var_Secant2(Object):
	def __init__(self, value=1.0):
		self.name = 'secant2'
		self.value = value


class Var_Twintrian(Object):
	def __init__(self, value=1.0):
		self.name = 'twintrian'
		self.value = value


class Var_Cross(Object):
	def __init__(self, value=1.0):
		self.name = 'cross'
		self.value = value


class Var_Disc2(Object):
	def __init__(self, value=1.0, variables={'twist':0, 'rot':0, }):
		self.name = 'disc2'
		self.value = value
		self.variables = variables


class Var_Super_Shape(Object):
	def __init__(self, value=1.0):
		self.name = 'super_shape'
		self.value = value


class Var_Flower(Object):
	def __init__(self, value=1.0, variables={'petals':0, 'holes':0, }):
		self.name = 'flower'
		self.value = value
		self.variables = variables


class Var_Conic(Object):
	def __init__(self, value=1.0, variables={'eccentricity':1, 'holes':0, }):
		self.name = 'conic'
		self.value = value
		self.variables = variables


class Var_Parabola(Object):
	def __init__(self, value=1.0, variables={'width':0, 'height':0, }):
		self.name = 'parabola'
		self.value = value
		self.variables = variables


class Var_Bent2(Object):
	def __init__(self, value=1.0, variables={'y':0, 'x':0, }):
		self.name = 'bent2'
		self.value = value
		self.variables = variables


class Var_Bipolar(Object):
	def __init__(self, value=1.0, variables={'shift':0, }):
		self.name = 'bipolar'
		self.value = value
		self.variables = variables


class Var_Boarders(Object):
	def __init__(self, value=1.0):
		self.name = 'boarders'
		self.value = value


class Var_Butterfly(Object):
	def __init__(self, value=1.0):
		self.name = 'butterfly'
		self.value = value


class Var_Cell(Object):
	def __init__(self, value=1.0, variables={'size':1, }):
		self.name = 'cell'
		self.value = value
		self.variables = variables


class Var_Cpow(Object):
	def __init__(self, value=1.0, variables={'i':0, 'r':1, 'power':1, }):
		self.name = 'cpow'
		self.value = value
		self.variables = variables


class Var_Curve(Object):
	def __init__(self, value=1.0, variables={'ylength':1, 'xlength':1, 'yamp':1, 'xamp':1, }):
		self.name = 'curve'
		self.value = value
		self.variables = variables


class Var_Edisc(Object):
	def __init__(self, value=1.0):
		self.name = 'edisc'
		self.value = value


class Var_Elliptic(Object):
	def __init__(self, value=1.0):
		self.name = 'elliptic'
		self.value = value


class Var_Escher(Object):
	def __init__(self, value=1.0, variables={'beta':0, }):
		self.name = 'escher'
		self.value = value
		self.variables = variables


class Var_Foci(Object):
	def __init__(self, value=1.0):
		self.name = 'foci'
		self.value = value


class Var_Lazysusan(Object):
	def __init__(self, value=1.0, variables={'twist':0, 'x':1, 'spin':0, 'y':1, 'space':0, }):
		self.name = 'lazysusan'
		self.value = value
		self.variables = variables


class Var_Loonie(Object):
	def __init__(self, value=1.0):
		self.name = 'loonie'
		self.value = value


class Var_Pre_Blur(Object):
	def __init__(self, value=1.0):
		self.name = 'pre_blur'
		self.value = value


class Var_Modulus(Object):
	def __init__(self, value=1.0, variables={'y':1, 'x':1, }):
		self.name = 'modulus'
		self.value = value
		self.variables = variables


class Var_Oscilloscope(Object):
	def __init__(self, value=1.0):
		self.name = 'oscilloscope'
		self.value = value


class Var_Polar2(Object):
	def __init__(self, value=1.0):
		self.name = 'polar2'
		self.value = value


class Var_Popcorn2(Object):
	def __init__(self, value=1.0, variables={'y':0, 'x':0, 'c':0, }):
		self.name = 'popcorn2'
		self.value = value
		self.variables = variables


class Var_Scry(Object):
	def __init__(self, value=1.0):
		self.name = 'scry'
		self.value = value


class Var_Separation(Object):
	def __init__(self, value=1.0, variables={'y':0, 'x':0, 'xinside':0, 'yinside':0, }):
		self.name = 'separation'
		self.value = value
		self.variables = variables


class Var_Split(Object):
	def __init__(self, value=1.0, variables={'ysize':0, 'xsize':0, }):
		self.name = 'split'
		self.value = value
		self.variables = variables


class Var_Splits(Object):
	def __init__(self, value=1.0, variables={'y':1, 'x':1, }):
		self.name = 'splits'
		self.value = value
		self.variables = variables


class Var_Stripes(Object):
	def __init__(self, value=1.0, variables={'warp':0, 'space':1, }):
		self.name = 'stripes'
		self.value = value
		self.variables = variables


class Var_Wedge(Object):
	def __init__(self, value=1.0, variables={'count':0, 'swirl':0, 'hole':0, 'angle':0, }):
		self.name = 'wedge'
		self.value = value
		self.variables = variables


class Var_Wedge_Julia(Object):
	def __init__(self, value=1.0, variables={'count':0, 'dist':1, 'angle':0, 'power':2, }):
		self.name = 'wedge_julia'
		self.value = value
		self.variables = variables


class Var_Wedge_Sph(Object):
	def __init__(self, value=1.0, variables={'count':0, 'swirl':0, 'hole':0, 'angle':0, }):
		self.name = 'wedge_sph'
		self.value = value
		self.variables = variables


class Var_Whorl(Object):
	def __init__(self, value=1.0, variables={'inside':1, 'outside':1, }):
		self.name = 'whorl'
		self.value = value
		self.variables = variables


class Var_Waves2(Object):
	def __init__(self, value=1.0, variables={'scalex':1, 'scaley':1, 'freqy':1, 'freqx':1, }):
		self.name = 'waves2'
		self.value = value
		self.variables = variables

