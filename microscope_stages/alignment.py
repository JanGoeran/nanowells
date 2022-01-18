import numpy as np
import math

def rot(point, angle):
    """Takes (x,y) and applies rotation around origin by angle (degrees)"""
    rad = angle * math.pi/180
    v1 = np.array(point)
    rotmat = np.array([[math.cos(rad), math.sin(rad)], [-math.sin(rad), math.cos(rad)]])
    v2 = np.matmul(rotmat, v1).astype(float)
    return v2

def trans(point, offset):
    """Takes (x,y) and adds offset."""
    v2 = np.array(point) + np.array(offset)
    return v2.astype(float)

def scale(point, zoom):
    """Takes (x,y) and applies scaling factor (zoom) relative to origin."""
    v1 = np.array(point)
    z = np.array([[zoom,0],[0,zoom]])
    v2 = np.matmul(z, v1).astype(float)
    return v2

def uv2xy(point, tran, angle, zoom):
    """Takes (u,v) converts to (x,y) coordinates performing coordinate transformation."""
    puv = np.array(point)
    puv = scale(puv, zoom)
    puv = rot(puv, -angle)
    pxy = trans(puv, tran)
    return pxy

def uv2z(v, z0, slope):
    """Takes v-coordinate and calculates z (stage height)."""
    z = z0+(v*slope)
    return z

def xy2uv(point, tran, angle, zoom):
    """Takes (x,y) converts to (u,v) coordinates performing coordinate transformation."""
    pxy = np.array(point)
    pxy = trans(pxy, -tran)
    pxy = scale(pxy, 1/zoom)
    puv = rot(pxy, angle)
    return puv

def get_trans(pxy,puv = (0,0)):
    """Takes (x,y) and desired (u,v) coordinates to calculate translation."""
    pxy = np.array(pxy)
    puv = np.array(puv)
    t = pxy - puv
    return t

def get_angle(pxy1, pxy2):
    """Takes two (x,y) points and calculates the angle between them."""
    pxy1 = np.array(pxy1)
    pxy2 = np.array(pxy2)

    if (pxy2[1]-pxy1[1]) == 0:
        a = 0
    else:
        a = math.atan((pxy2[0]-pxy1[0])/(pxy2[1]-pxy1[1]))
    a = - a * 180 / math.pi
    return a

def get_zoom(pxy1, pxy2, uvdist, stage_inverted=True):
    """Takes two (x,y) points and the known (u,v) distance between them to calculate zoom."""
    pxy1 = np.array(pxy1)
    pxy2 = np.array(pxy2)
    xydist = np.linalg.norm(pxy1 - pxy2)
    z = xydist/uvdist
    if stage_inverted:
        return -z
    else:
        return z