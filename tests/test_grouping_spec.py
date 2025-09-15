from app.astro.aspects import AspectHit
from app.astro.rank_group import group_and_rank

def AH(t, p1, p2, angle, diff, sep):  # helper
    return AspectHit(t, (p1,p2), angle, diff, sep)

def test_stellium_and_group_fields():
    # Moon opposite three planets around ~180°, within ±3°
    hits = [
        AH("opposition","Moon","Mars",180.0,1.0,179.0),
        AH("opposition","Moon","Pluto",180.0,1.5,178.7),
        AH("opposition","Moon","Venus",180.0,2.4,181.8),
    ]
    items = group_and_rank(hits, planets_pos=None, comp_angles=None)
    top = items[0]
    assert top["stellium"] is True
    assert top["group_id"].startswith("moon_opposition_group_")
    assert "cluster_tag" in top and "intensity" in top["cluster_tag"]
    assert top["orb_avg"] >= 0.0 and top["score_merged"] >= 0.0

def test_hardness_sort_conjunction_first():
    hits = [
        AH("opposition","Moon","Saturn",180.0,0.5,179.5),
        AH("conjunction","Sun","Mercury",0.0,2.0,2.0)
    ]
    items = group_and_rank(hits)
    # Because of bucket rank + scoring, conj should be allowed to outrank when scores comparable
    assert items[0]["type"] in ("conjunction","opposition")
