from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from statistics import mean
from app.astro.aspects import AspectHit

# Hardness weights (spec)
HARDNESS_W = {"conjunction": 2.0, "opposition": 1.8, "square": 1.6, "trine": 1.2}

# Sort priority bucket (lower = stronger)
# Conjunction > Opposition > Square > Stellium/Angle > Trine
BUCKET_RANK = {"conjunction": 0, "opposition": 1, "square": 2, "stellium_angle": 3, "trine": 4}

# Cluster theme tag base
THEME = {"conjunction": "fusion", "opposition": "intensity", "square": "friction", "trine": "ease", "stellium_angle": "angle"}

# Emotional anchor priority (for labels)
PLANET_PRIORITY = ["Moon","Sun","Mars","Pluto","Venus","Saturn","Jupiter","Mercury","Uranus","Neptune"]

def _anchor(p1: str, p2: str) -> Tuple[str, str]:
    pr = {p:i for i,p in enumerate(PLANET_PRIORITY)}
    return (p1, p2) if pr.get(p1,999) <= pr.get(p2,999) else (p2, p1)

def _max_orb(p1: str, p2: str) -> float:
    return 5.0 if ("Sun" in (p1,p2) or "Moon" in (p1,p2)) else 3.0

def _emotional_bonus(p1: str, p2: str) -> float:
    return 0.2 if ({"Sun","Moon","Mars"} & {p1,p2}) else 0.0

def _near(a: float, b: float, tol: float) -> bool:
    d = abs((a - b) % 360.0)
    d = d if d <= 180.0 else 360.0 - d
    return d <= tol

def _angularity_for_pair(p1: str, p2: str,
                         planets_pos: Optional[Dict[str,float]],
                         comp_angles: Optional[Dict[str,float]]) -> float:
    """+0.2 if either planet is within ±5° of AC/DC/IC/MC."""
    if not planets_pos or not comp_angles:
        return 0.0
    for p in (p1, p2):
        pos = planets_pos.get(p)
        if pos is None:
            continue
        for ang_name in ("AC","DC","IC","MC"):
            ang = comp_angles.get(ang_name)
            if ang is not None and _near(pos, ang, 5.0):
                return 0.2
    return 0.0

def _score_additive(h: AspectHit,
                    planets_pos: Optional[Dict[str,float]],
                    comp_angles: Optional[Dict[str,float]]) -> Tuple[float, float, float, float]:
    """Return (score_no_group, hardness_weight, emotional_bonus, angularity_boost)."""
    p1, p2 = h.planets
    max_orb = _max_orb(p1, p2)
    orb_score = max(0.0, 1.0 - (h.diff / max_orb))
    hardness = HARDNESS_W[h.type]
    emot = _emotional_bonus(p1, p2)
    ang_boost = _angularity_for_pair(p1, p2, planets_pos, comp_angles)
    score = round(hardness + orb_score + emot + ang_boost, 6)  # group_bonus added at cluster level
    return score, hardness, emot, ang_boost

@dataclass
class Cluster:
    primary_type: str
    anchor: str
    band_center: float                # central separation for ±3° band
    members: List[str] = field(default_factory=list)     # non-anchor planets
    member_orbs: List[float] = field(default_factory=list)
    member_scores: List[float] = field(default_factory=list)  # per-hit score (no group bonus)
    angle_related: bool = False
    min_orb: float = 999.0
    avg_orb: float = 999.0
    merged_score: float = 0.0         # avg(member_scores) + group_bonus
    max_score: float = 0.0            # best member score
    stellium: bool = False
    group_bonus: float = 0.0
    group_id: str = ""
    cluster_tag: str = ""             # e.g., intensity_moon_group
    bucket: str = ""                  # 'conjunction'|'opposition'|'square'|'stellium_angle'|'trine'

    def label(self) -> str:
        tail = "/".join(sorted(self.members))
        return f"{self.anchor} {self.primary_type} {tail}"

def group_and_rank(hits: List[AspectHit],
                   planets_pos: Optional[Dict[str,float]] = None,
                   comp_angles: Optional[Dict[str,float]] = None) -> List[Dict]:
    # 1) score each hit (without group bonus)
    scored = []
    details = {}  # map hit -> components to emit later if needed
    for h in hits:
        s, hardness, emot, ang = _score_additive(h, planets_pos, comp_angles)
        scored.append((h, s))
        details[id(h)] = (s, hardness, emot, ang)

    # 2) cluster by (type, anchor) & ±3° band around separation
    clusters: List[Cluster] = []
    BAND = 3.0

    def find_or_make_cluster(h: AspectHit, anchor: str) -> Cluster:
        for cl in clusters:
            if cl.primary_type != h.type or cl.anchor != anchor:
                continue
            # same band?
            if abs(h.exact_angle - cl.band_center) <= BAND:
                return cl
        # new cluster (band centered on this hit's separation)
        cl = Cluster(primary_type=h.type, anchor=anchor, band_center=h.exact_angle)
        clusters.append(cl)
        return cl

    for h, s in scored:
        a, b = _anchor(*h.planets)
        cl = find_or_make_cluster(h, a)
        cl.members.append(b)
        cl.member_orbs.append(h.diff)
        cl.member_scores.append(s)
        cl.min_orb = min(cl.min_orb, h.diff)
        cl.max_score = max(cl.max_score, s)
        # mark angle-related if any member contributes ang boost
        _, _, _, ang = details[id(h)]
        if ang > 0:
            cl.angle_related = True

    # 3) finalize clusters (group bonus, stellium, averages, tags, bucket)
    idx_counter: Dict[Tuple[str,str], int] = {}  # (type, anchor) -> seq
    out_clusters = []

    for cl in clusters:
        cl.avg_orb = round(mean(cl.member_orbs), 2) if cl.member_orbs else 999.0
        cl.stellium = len(cl.members) >= 2  # anchor + ≥2 others => stellium
        if len(cl.members) >= 1:
            cl.group_bonus = 0.2  # clustered insight (anchor + ≥1 other)
        cl.merged_score = round(mean(cl.member_scores) + cl.group_bonus, 6)

        # bucket: stellium/angle between square & trine
        # Only classify as stellium_angle if it's purely a stellium (not an aspect cluster)
        if cl.stellium and cl.primary_type not in ['conjunction', 'opposition', 'square', 'trine']:
            cl.bucket = "stellium_angle"
        elif cl.angle_related and not cl.stellium:
            cl.bucket = "stellium_angle"
        else:
            cl.bucket = cl.primary_type

        # group_id + cluster_tag
        key = (cl.primary_type, cl.anchor)
        idx_counter[key] = idx_counter.get(key, 0) + 1
        cl.group_id = f"{cl.anchor.lower()}_{cl.primary_type}_group_{idx_counter[key]}"
        theme = THEME.get(cl.bucket, THEME.get(cl.primary_type, "group"))
        cl.cluster_tag = f"{theme}_{cl.anchor.lower()}_group"

        out_clusters.append(cl)

    # 4) rank clusters
    def sort_key(c: Cluster):
        return (-c.merged_score, BUCKET_RANK.get(c.bucket, 99), c.min_orb, c.label())

    ranked = sorted(out_clusters, key=sort_key)[:5]

    # 5) emit
    results = []
    for c in ranked:
        planets = [c.anchor] + sorted(c.members)
        results.append({
            "aspect_label": c.label(),       # "Moon opposition Mars/Pluto/..."
            "type": c.primary_type,
            "anchor": c.anchor,
            "planets": planets,
            "group_id": c.group_id,
            "cluster_tag": c.cluster_tag,
            "stellium": c.stellium,
            "bucket": c.bucket,              # for UI sorting/sectioning
            "orb_min": round(c.min_orb, 2),
            "orb_avg": round(c.avg_orb, 2),
            "score_max": round(c.max_score, 4),
            "score_merged": round(c.merged_score, 4),
            "weights": {
                "hardness_weight": HARDNESS_W[c.primary_type],
                "emotional_bonus": 0.2 if ({"Sun","Moon","Mars"} & set(planets)) else 0.0,
                "angularity_boost": 0.2 if c.angle_related else 0.0,
                "group_bonus": c.group_bonus
            }
        })
    return results
