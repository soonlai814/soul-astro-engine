"""
Comprehensive composite analysis engine that implements the complete specification.
"""
from typing import Dict, List, Any
from datetime import datetime
from app.astro.aspects import detect_aspects
from app.astro.angle_contacts import detect_angle_contacts
from app.astro.stellium_detection import detect_stelliums
from app.astro.sign_blend import detect_sign_blend
from app.astro.significance_scoring import (
    AspectTheme, StelliumTheme, AngleTheme, SignBlendTheme, 
    rank_themes
)
from app.astro.payload_formatter import format_placements_payload, format_meta_payload
from app.core.constants import ASPECTS


def analyze_composite(composite_planets: Dict[str, float], 
                     composite_angles: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Perform comprehensive composite analysis according to the specification.
    
    Args:
        composite_planets: Dict of planet names to composite longitudes
        composite_angles: Dict of angle names to composite longitudes
        
    Returns:
        Complete analysis result with placements and meta
    """
    # 1. Detect aspects
    aspects = detect_aspects(composite_planets)
    
    # 2. Detect angle contacts
    angle_contacts = detect_angle_contacts(composite_planets, composite_angles) if composite_angles else []
    
    # 3. Detect stelliums
    stelliums = detect_stelliums(composite_planets)
    
    # 4. Detect sign blend themes
    sign_themes = detect_sign_blend(composite_planets)
    
    # 5. Convert to theme units for scoring
    theme_units = []
    
    # Convert aspects to theme units
    for aspect in aspects:
        a_deg = composite_planets.get(aspect.planets[0], 0.0)
        b_deg = composite_planets.get(aspect.planets[1], 0.0)
        theme_units.append(AspectTheme(
            source="aspect",
            type=aspect.type,
            orb_deg=aspect.diff,
            a=aspect.planets[0],
            b=aspect.planets[1],
            a_deg=a_deg,
            b_deg=b_deg
        ))
    
    # Convert stelliums to theme units
    for stellium in stelliums:
        theme_units.append(StelliumTheme(
            source="stellium",
            type="stellium",
            orb_deg=stellium.span_deg,
            sign=stellium.sign,
            planets=stellium.planets,
            span_deg=stellium.span_deg
        ))
    
    # Convert angle contacts to theme units
    for contact in angle_contacts:
        theme_units.append(AngleTheme(
            source="angle",
            type="angle",
            orb_deg=contact.orb_deg,
            angle=contact.angle,
            planet=contact.planet,
            planet_deg=contact.planet_deg,
            angle_deg=contact.angle_deg
        ))
    
    # Convert sign themes to theme units
    for theme in sign_themes:
        theme_units.append(SignBlendTheme(
            source="sign_blend",
            type="sign_blend",
            orb_deg=0.0,  # Sign blends don't have orbs
            sign=theme.sign,
            keywords=theme.keywords
        ))
    
    # 6. Rank themes by significance
    selected_themes = rank_themes(theme_units, angle_contacts, stelliums)
    
    # 7. Format payload
    placements = format_placements_payload(
        aspects, angle_contacts, stelliums, sign_themes, selected_themes, composite_planets
    )
    
    meta = format_meta_payload()
    
    return {
        "placements": placements,
        "meta": meta
    }
