import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import Dict

from app.astro import swe_wrap
from app.astro.composite import composite_longitudes
from app.astro.swe_wrap import planet_longitudes, composite_angles
from app.astro.aspects import detect_aspects
from app.astro.rank_group import group_and_rank

# Load .env file from the project root directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
SWE_EPHE_PATH = os.getenv("SWE_EPHE_PATH")

# Debug information
print(f"Current working directory: {os.getcwd()}")
print(f"SWE_EPHE_PATH: {SWE_EPHE_PATH}")
print(f"Is directory: {os.path.isdir(SWE_EPHE_PATH) if SWE_EPHE_PATH else False}")

app = FastAPI(title="Soul Astro Engine", version=APP_VERSION)

class Person(BaseModel):
    datetime_utc: str
    lat: float | None = None   # decimal degrees (+N, -S)
    lon: float | None = None   # decimal degrees (+E, -W)

class CompositeBody(BaseModel):
    parent: Person
    child: Person

class LongitudesBody(BaseModel):
    longitudes: Dict[str, float]
    composite_angles: Dict[str, float] | None = None  # optional for angularity

PLANET_PRIORITY = ["Moon","Sun","Mars","Pluto","Venus","Saturn","Jupiter","Mercury","Uranus","Neptune"]
def _anchor_pair(p1: str, p2: str) -> str:
    pr = {p:i for i,p in enumerate(PLANET_PRIORITY)}
    return p1 if pr.get(p1,999) <= pr.get(p2,999) else p2

def _parse_utc(s: str) -> datetime:
    # small helper that accepts ...Z or +00:00
    s = s.replace("Z", "+00:00") if s.endswith("Z") else s
    return datetime.fromisoformat(s)

@app.on_event("startup")
def _startup():
    if not SWE_EPHE_PATH or not os.path.isdir(SWE_EPHE_PATH):
        raise RuntimeError("SWE_EPHE_PATH missing or invalid directory.")
    swe_wrap.init(SWE_EPHE_PATH)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/about")
def about():
    return {
        "name": "Soul Astro Engine",
        "version": APP_VERSION,
        "license": "AGPL-3.0",
        "swe_path": SWE_EPHE_PATH,
    }

@app.post("/composite")
def post_composite(body: CompositeBody):
    try:
        a = _parse_utc(body.parent.datetime_utc)
        b = _parse_utc(body.child.datetime_utc)
    except Exception as e:
        raise HTTPException(400, f"Invalid datetime format: {e}")

    comp = composite_longitudes(a, b)
    return {
        "longitudes": {
            "parent": planet_longitudes(a),
            "child": planet_longitudes(b)
        },
        "composite": comp,
        "meta": {"src": "Swiss Ephemeris"}
    }

@app.post("/aspects")
def post_aspects(body: LongitudesBody = Body(...)):
    hits = detect_aspects(body.longitudes)

    # For /aspects, we compute additive pieces WITHOUT group_bonus (clusters happen later).
    items = []
    for h in hits:
        p1, p2 = h.planets
        # emotional + hardness + angularity_boost (if angles provided)
        max_orb = 5.0 if ("Sun" in h.planets or "Moon" in h.planets) else 3.0
        orb_score = max(0.0, 1.0 - (h.diff / max_orb))
        hardness_weight = {"conjunction":2.0, "opposition":1.8, "square":1.6, "trine":1.2}[h.type]
        emotional_bonus = 0.2 if ({"Sun","Moon","Mars"} & set(h.planets)) else 0.0

        angularity_boost = 0.0
        if body.composite_angles:
            # 0.2 if either planet within ±5° of AC/DC/IC/MC
            def near(a,b):
                d = abs((a - b) % 360.0)
                return d if d <= 180.0 else 360.0 - d <= 5.0
            pos1 = body.longitudes.get(p1); pos2 = body.longitudes.get(p2)
            if pos1 is not None:
                for ang in ("AC","DC","IC","MC"):
                    A = body.composite_angles.get(ang)
                    if A is not None:
                        d = abs((pos1 - A) % 360.0); d = d if d <= 180.0 else 360.0 - d
                        if d <= 5.0: angularity_boost = 0.2; break
            if angularity_boost == 0.0 and pos2 is not None:
                for ang in ("AC","DC","IC","MC"):
                    A = body.composite_angles.get(ang)
                    if A is not None:
                        d = abs((pos2 - A) % 360.0); d = d if d <= 180.0 else 360.0 - d
                        if d <= 5.0: angularity_boost = 0.2; break

        score = round(hardness_weight + orb_score + emotional_bonus + angularity_boost, 6)
        theoretical_max = hardness_weight + 1.0 + emotional_bonus + angularity_boost  # no group bonus at /aspects
        strength = round(score / theoretical_max, 3) if theoretical_max > 0 else 0.0

        items.append({
            "type": h.type,
            "planets": list(h.planets),
            "anchor": _anchor_pair(*h.planets),
            "angle": h.angle,
            "orb": round(h.diff, 2),
            "separation": round(h.exact_angle, 2),
            "score": score,
            "strength": strength,
            "hardness_weight": hardness_weight,
            "emotional_bonus": emotional_bonus,
            "angularity_boost": angularity_boost
        })

    # sort: hardness order (Conj > Opp > Sq > Angle/Stellium > Trine), then tighter orb, then strength desc
    order = {"conjunction":0, "opposition":1, "square":2, "trine":4}
    items.sort(key=lambda x: (order[x["type"]], x["orb"], -x["strength"], x["anchor"]))
    return {"count": len(items), "aspects": items}

@app.post("/top-aspects")
def post_top_aspects(body: LongitudesBody):
    hits = detect_aspects(body.longitudes)
    clusters = group_and_rank(hits, planets_pos=body.longitudes, comp_angles=body.composite_angles)
    return {"count": len(clusters), "items": clusters}

@app.post("/top-aspects/composite")
def post_top_aspects_composite(body: CompositeBody):
    print(body)
    try:
        a = _parse_utc(body.parent.datetime_utc)
        b = _parse_utc(body.child.datetime_utc)

        comp = composite_longitudes(a, b)

        comp_ang = None
        if (body.parent.lat is not None and body.parent.lon is not None and
            body.child.lat  is not None and body.child.lon  is not None):
            comp_ang = composite_angles(a, body.parent.lat, body.parent.lon,
                                        b, body.child.lat,  body.child.lon)

        hits = detect_aspects(comp)
        clusters = group_and_rank(hits, planets_pos=comp, comp_angles=comp_ang)

        return {
            "count": len(clusters),
            "items": clusters,
            "composite": comp,
                "composite_angles": comp_ang,
                "meta": {"src": "Swiss Ephemeris", "version": APP_VERSION}
            }
    except Exception as e:
        raise HTTPException(400, f"Error processing request: {e}")