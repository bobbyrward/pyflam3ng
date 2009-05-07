from math import *

def polar(x, y):
    len = sqrt(x**2 + y**2)
    ang = atan2(y, x) * (180.0/pi)
    return len, ang

def rect(len, ang):
    x = len * cos(ang*pi/180.0)
    y = len * sin(ang*pi/180.0)
    return x, y

