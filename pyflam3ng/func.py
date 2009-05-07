from math import *

def polar(x, y):
    len = sqrt(x**2 + y**2)
    ang = atan2(y, x) * (180.0/pi)
    return len, ang

def rect(len, ang):
    x = len * cos(ang*pi/180.0)
    y = len * sin(ang*pi/180.0)
    return x, y

def clip(n, mini=None, maxi=None, rotates=False):
    if rotates and mini!=None and maxi!=None:
        while n < mini or n > maxi:
            if n < mini: n += (maxi - mini)
            elif n > maxi: n -= (maxi - mini)
    else:
        if mini:
            if n < mini: n = mini
        if maxi:
            if n > maxi: n = maxi
    return n

