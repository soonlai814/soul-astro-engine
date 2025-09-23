import os
from datetime import datetime, timezone
import swisseph as swe
from typing import Dict

from app.core.angles import circ_midpoint, normalize_deg

PLANETS = {
    "Sun":    swe.SUN,
    "Moon":   swe.MOON,
    "Mercury":swe.MERCURY,
    "Venus":  swe.VENUS,
    "Mars":   swe.MARS,
    "Jupiter":swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune":swe.NEPTUNE,
    "Pluto":  swe.PLUTO,
    "North Node": swe.TRUE_NODE,
    "South Node": swe.TRUE_NODE,  # Will be calculated as North Node + 180°
}

_initialised = False

def init(ephe_path: str):
    global _initialised
    if not _initialised:
        swe.set_ephe_path(ephe_path)
        _initialised = True

def _to_jd_ut(dt_utc: datetime) -> float:
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)
    else:
        dt_utc = dt_utc.astimezone(timezone.utc)
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                      dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)

def planet_longitudes(dt_utc: datetime) -> Dict[str, float]:
    jd = _to_jd_ut(dt_utc)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED  # swiss ephemeris, speed if needed
    out: Dict[str, float] = {}

    for name, pid in PLANETS.items():
        if name == "South Node":
            # South Node is North Node + 180°
            if "North Node" in out:
                out[name] = normalize_deg(out["North Node"] + 180.0)
            else:
                # Calculate North Node first
                xx, retflag = swe.calc_ut(jd, swe.TRUE_NODE, flags)
                if retflag < 0 or xx is None or len(xx) < 1:
                    raise RuntimeError(f"swe.calc_ut failed for North Node (retflag={retflag})")
                north_node_lon = float(xx[0])
                out["North Node"] = north_node_lon
                out[name] = normalize_deg(north_node_lon + 180.0)
        else:
            xx, retflag = swe.calc_ut(jd, pid, flags)  # <- returns (xx, retflag)
            if retflag < 0 or xx is None or len(xx) < 1:
                raise RuntimeError(f"swe.calc_ut failed for {name} (retflag={retflag})")
            lon = float(xx[0])  # ecliptic longitude in degrees, already 0..360
            out[name] = lon

    return out

def calc_angles(dt_utc: datetime, lat: float, lon: float, hsys: str = "P") -> Dict[str, float]:
    """Return AC/DC/MC/IC for a single chart. lat/lon in decimal degrees (N+=+, S=-; E+=+, W=-)."""
    jd = _to_jd_ut(dt_utc)
    h = hsys.encode() if isinstance(hsys, str) else hsys

    try:
        # Newer API: (jd_ut, iflag, lat, lon, hsys) -> (cusps, ascmc, retflag)
        cusps, ascmc, _ = swe.houses_ex(jd, swe.FLG_SWIEPH, lat, lon, h)
    except TypeError:
        # Fallback API: (jd_ut, lat, lon, hsys) -> (cusps, ascmc)
        cusps, ascmc = swe.houses(jd, lat, lon, h)

    asc = float(ascmc[0])
    mc  = float(ascmc[1])
    dc  = normalize_deg(asc + 180.0)
    ic  = normalize_deg(mc  + 180.0)
    return {"AC": asc, "DC": dc, "MC": mc, "IC": ic}

def composite_angles(dt_a: datetime, lat_a: float, lon_a: float,
                     dt_b: datetime, lat_b: float, lon_b: float,
                     hsys: str = "P") -> Dict[str, float]:
    """Midpoint the parents' angles to produce composite AC/DC/MC/IC."""
    a1 = calc_angles(dt_a, lat_a, lon_a, hsys)
    a2 = calc_angles(dt_b, lat_b, lon_b, hsys)
    return {k: circ_midpoint(a1[k], a2[k]) for k in ("AC", "DC", "MC", "IC")}