from typing import Dict, List, Tuple
from dataclasses import dataclass
from app.core.angles import normalize_deg

ASPECTS = [
    ("conjunction", 0.0),
    ("square", 90.0),
    ("trine", 120.0),
    ("opposition", 180.0),
]

SUN_MOON_ORB = 5.0
OTHER_ORB = 3.0

@dataclass
class AspectHit:
    type: str
    planets: Tuple[str, str]
    angle: float          # target angle (0/90/120/180)
    diff: float           # absolute delta to angle (orb)
    exact_angle: float    # actual separation (0..180)

def _sep_deg(a: float, b: float) -> float:
    """Separation in degrees, folded to 0..180."""
    d = abs(a - b) % 360.0
    return d if d <= 180.0 else 360.0 - d

def _orb_for_pair(p1: str, p2: str) -> float:
    if "Sun" in (p1, p2) or "Moon" in (p1, p2):
        return SUN_MOON_ORB
    return OTHER_ORB

def detect_aspects(longitudes: Dict[str, float]) -> List[AspectHit]:
    keys = list(longitudes.keys())
    hits: List[AspectHit] = []
    for i in range(len(keys)):
        for j in range(i+1, len(keys)):
            p1, p2 = keys[i], keys[j]
            a1, a2 = longitudes[p1], longitudes[p2]
            sep = _sep_deg(a1, a2)     # 0..180
            orb_max = _orb_for_pair(p1, p2)
            for name, target in ASPECTS:
                diff = abs(sep - target)
                if diff <= orb_max:
                    hits.append(AspectHit(
                        type=name,
                        planets=(p1, p2),
                        angle=target,
                        diff=round(diff, 2),
                        exact_angle=round(sep, 2),
                    ))
    # sort: tighter orb first; prefer hard aspects a bit
    priority = {"opposition":0, "square":1, "conjunction":2, "trine":3}
    hits.sort(key=lambda h: (round(h.diff,3), priority[h.type], h.planets))
    return hits
