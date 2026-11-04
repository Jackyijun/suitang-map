# 与页面一致的 Albers 等积圆锥投影
import math
import numpy as np
RAD = math.pi / 180
L0, P0 = 102.0, 36.0
p1, p2 = 25 * RAD, 47 * RAD
nn = (math.sin(p1) + math.sin(p2)) / 2
CC = math.cos(p1) ** 2 + 2 * nn * math.sin(p1)
rho0 = math.sqrt(CC - 2 * nn * math.sin(P0 * RAD)) / nn
SCL = 1000.0

def proj(lon, lat):
    lon = np.asarray(lon, dtype=float); lat = np.asarray(lat, dtype=float)
    r = np.sqrt(np.maximum(CC - 2 * nn * np.sin(lat * RAD), 1e-9)) / nn
    th = nn * (lon * RAD - L0 * RAD)
    return r * np.sin(th) * SCL, -(rho0 - r * np.cos(th)) * SCL

def inv(x, y):
    X = np.asarray(x, dtype=float) / SCL; Y = -np.asarray(y, dtype=float) / SCL
    r = np.sqrt(X * X + (rho0 - Y) ** 2)
    th = np.arctan2(X, rho0 - Y)
    lon = (L0 * RAD + th / nn) / RAD
    lat = np.arcsin(np.clip((CC - r * r * nn * nn) / (2 * nn), -1, 1)) / RAD
    return lon, lat
