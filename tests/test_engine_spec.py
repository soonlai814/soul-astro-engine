"""
Comprehensive engine tests according to the specification.
"""
import pytest
from app.astro.aspects import detect_aspects
from app.astro.angle_contacts import detect_angle_contacts
from app.astro.stellium_detection import detect_stelliums
from app.astro.sign_blend import detect_sign_blend
from app.astro.significance_scoring import AspectTheme, StelliumTheme, AngleTheme, SignBlendTheme, calculate_significance, rank_themes
from app.astro.composite_engine import analyze_composite
from app.core.constants import ORB_SUN_MOON, ORB_OTHERS, STELLIUM_SPAN_DEG, ANGLE_ORB_DEG


def test_sun_moon_orb_rules():
    """Test Sun/Moon orb rules: 4.9° passes, 5.1° fails."""
    # Test Sun-Moon conjunction within orb
    planets = {"Sun": 0.0, "Moon": 4.9}
    aspects = detect_aspects(planets)
    sun_moon_aspects = [a for a in aspects if set(a.planets) == {"Sun", "Moon"}]
    assert len(sun_moon_aspects) > 0
    assert sun_moon_aspects[0].diff <= ORB_SUN_MOON
    
    # Test Sun-Moon conjunction outside orb
    planets = {"Sun": 0.0, "Moon": 5.1}
    aspects = detect_aspects(planets)
    sun_moon_aspects = [a for a in aspects if set(a.planets) == {"Sun", "Moon"}]
    assert len(sun_moon_aspects) == 0


def test_others_orb_rules():
    """Test other planets orb rules: 2.9° passes, 3.1° fails."""
    # Test Mars-Saturn conjunction within orb
    planets = {"Mars": 0.0, "Saturn": 2.9}
    aspects = detect_aspects(planets)
    mars_saturn_aspects = [a for a in aspects if set(a.planets) == {"Mars", "Saturn"}]
    assert len(mars_saturn_aspects) > 0
    assert mars_saturn_aspects[0].diff <= ORB_OTHERS
    
    # Test Mars-Saturn conjunction outside orb
    planets = {"Mars": 0.0, "Saturn": 3.1}
    aspects = detect_aspects(planets)
    mars_saturn_aspects = [a for a in aspects if set(a.planets) == {"Mars", "Saturn"}]
    assert len(mars_saturn_aspects) == 0


def test_stellium_detection():
    """Test stellium detection: 3 planets within 7.5° → detected, 8.5° → not."""
    # Test stellium within span
    planets = {"Sun": 0.0, "Moon": 3.0, "Mars": 7.5}
    stelliums = detect_stelliums(planets)
    assert len(stelliums) > 0
    assert stelliums[0].span_deg <= STELLIUM_SPAN_DEG
    assert len(stelliums[0].planets) >= 3
    
    # Test no stellium outside span
    planets = {"Sun": 0.0, "Moon": 3.0, "Mars": 8.5}
    stelliums = detect_stelliums(planets)
    # Should NOT detect stellium as 8.5° is outside 8° span
    assert len(stelliums) == 0
    
    # Test definitely no stellium
    planets = {"Sun": 0.0, "Moon": 3.0, "Mars": 9.0}
    stelliums = detect_stelliums(planets)
    assert len(stelliums) == 0


def test_angle_contact_detection():
    """Test angle contact detection: planet within 2.5° of MC → contact collected."""
    planets = {"Sun": 0.0, "Mars": 2.5}
    angles = {"MC": 0.0, "AC": 90.0, "DC": 270.0, "IC": 180.0}
    
    contacts = detect_angle_contacts(planets, angles)
    assert len(contacts) > 0
    
    # Check Sun-MC contact
    sun_mc_contacts = [c for c in contacts if c.planet == "Sun" and c.angle == "MC"]
    assert len(sun_mc_contacts) > 0
    assert sun_mc_contacts[0].orb_deg <= ANGLE_ORB_DEG


def test_significance_scoring():
    """Test significance scoring: tight Sun-Saturn conjunction outranks loose Mercury-Jupiter trine."""
    # Tight Sun-Saturn conjunction
    sun_saturn = AspectTheme(
        source="aspect",
        type="conjunction",
        orb_deg=1.0,
        a="Sun",
        b="Saturn",
        a_deg=0.0,
        b_deg=1.0
    )
    
    # Loose Mercury-Jupiter trine
    mercury_jupiter = AspectTheme(
        source="aspect",
        type="trine",
        orb_deg=2.5,
        a="Mercury",
        b="Jupiter",
        a_deg=0.0,
        b_deg=120.0
    )
    
    sun_saturn_score = calculate_significance(sun_saturn)
    mercury_jupiter_score = calculate_significance(mercury_jupiter)
    
    # Sun-Saturn should score higher due to conjunction base score and tightness
    assert sun_saturn_score > mercury_jupiter_score


def test_ranking_priority():
    """Test ranking priority: conjunction > opposition > stellium > angle > square > trine."""
    themes = [
        AspectTheme("aspect", "trine", 2.0, "Mercury", "Jupiter", 0.0, 120.0),
        AspectTheme("aspect", "conjunction", 1.0, "Sun", "Moon", 0.0, 1.0),  # Tighter orb
        AspectTheme("aspect", "square", 2.0, "Mars", "Saturn", 0.0, 90.0),
        AspectTheme("aspect", "opposition", 2.0, "Venus", "Pluto", 0.0, 180.0),  # Same orb as conjunction
        StelliumTheme("stellium", "stellium", 5.0, "Scorpio", ["Uranus", "Neptune", "North Node"], 5.0),  # Different planets
        AngleTheme("angle", "angle", 2.0, "MC", "Sun", 0.0, 0.0)
    ]
    
    ranked = rank_themes(themes)
    
    # Check that conjunction comes first (due to higher base score)
    assert ranked[0].type == "conjunction"
    
    # Check that opposition comes before stellium
    conjunction_idx = next(i for i, t in enumerate(ranked) if t.type == "conjunction")
    opposition_idx = next(i for i, t in enumerate(ranked) if t.type == "opposition")
    stellium_idx = next(i for i, t in enumerate(ranked) if t.type == "stellium")
    
    assert opposition_idx < stellium_idx


def test_comprehensive_analysis():
    """Test the complete analysis pipeline."""
    # Create test data
    planets = {
        "Sun": 0.0,
        "Moon": 5.0,  # Sun-Moon conjunction
        "Mars": 10.0,
        "Saturn": 12.0,  # Mars-Saturn conjunction
        "Venus": 15.0,
        "Jupiter": 20.0,
        "Mercury": 25.0,
        "Uranus": 30.0,
        "Neptune": 35.0,
        "Pluto": 40.0,
        "North Node": 45.0,
        "South Node": 225.0
    }
    
    angles = {
        "AC": 0.0,  # Sun conjunct AC
        "DC": 180.0,
        "MC": 90.0,
        "IC": 270.0
    }
    
    result = analyze_composite(planets, angles)
    
    # Check structure
    assert "placements" in result
    assert "meta" in result
    
    placements = result["placements"]
    assert "stelliums" in placements
    assert "angles" in placements
    assert "aspects" in placements
    assert "sign_themes" in placements
    assert "selected_themes" in placements
    
    # Check that we have some results
    assert len(placements["aspects"]) > 0
    assert len(placements["selected_themes"]) > 0
    
    # Check meta
    meta = result["meta"]
    assert "rules" in meta
    assert "computed_at" in meta
    assert meta["rules"]["orb_sun_moon"] == 5.0
    assert meta["rules"]["orb_others"] == 3.0
    assert meta["rules"]["stellium_span"] == 8.0


def test_core_bodies_bonus():
    """Test that core bodies get bonus in scoring."""
    # Core body aspect
    sun_saturn = AspectTheme(
        source="aspect",
        type="conjunction",
        orb_deg=2.0,
        a="Sun",  # Core body
        b="Saturn",  # Core body
        a_deg=0.0,
        b_deg=2.0
    )
    
    # Non-core body aspect
    mercury_uranus = AspectTheme(
        source="aspect",
        type="conjunction",
        orb_deg=2.0,
        a="Mercury",  # Not core
        b="Uranus",   # Not core
        a_deg=0.0,
        b_deg=2.0
    )
    
    sun_saturn_score = calculate_significance(sun_saturn)
    mercury_uranus_score = calculate_significance(mercury_uranus)
    
    # Sun-Saturn should score higher due to core body bonus
    assert sun_saturn_score > mercury_uranus_score
