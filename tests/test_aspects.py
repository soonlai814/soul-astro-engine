from app.astro.aspects import detect_aspects

def test_conj_near_zero():
    longs = {"Sun": 359.0, "Moon": 1.0}
    hits = detect_aspects(longs)
    names = {(h.type, tuple(sorted(h.planets))) for h in hits}
    assert ("conjunction", ("Moon","Sun")) in names

def test_square_detect():
    longs = {"Mars": 10.0, "Saturn": 100.5}
    hits = detect_aspects(longs)
    found = [h for h in hits if h.type=="square" and set(h.planets)=={"Mars","Saturn"}]
    assert found and found[0].orb <= 1.0
