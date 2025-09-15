from datetime import datetime
from typing import Dict
from .swe_wrap import planet_longitudes
from ..core.angles import circ_midpoint

def composite_longitudes(dt_a: datetime, dt_b: datetime) -> Dict[str, float]:
    longs_a = planet_longitudes(dt_a)
    longs_b = planet_longitudes(dt_b)
    keys = longs_a.keys()
    return {k: circ_midpoint(longs_a[k], longs_b[k]) for k in keys}
