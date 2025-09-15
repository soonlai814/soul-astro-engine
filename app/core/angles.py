import math

def normalize_deg(d: float) -> float:
    x = d % 360.0
    return x if x >= 0 else x + 360.0

def circ_midpoint(a_deg: float, b_deg: float) -> float:
    # robust vector average on the circle
    a = math.radians(a_deg)
    b = math.radians(b_deg)
    x = (math.cos(a) + math.cos(b)) / 2.0
    y = (math.sin(a) + math.sin(b)) / 2.0
    ang = math.degrees(math.atan2(y, x))
    return normalize_deg(ang)
