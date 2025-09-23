"""
Format placements payload according to the strict API specification.
"""
from typing import Dict, List, Any
from datetime import datetime
from app.astro.aspects import AspectHit
from app.astro.angle_contacts import AngleContact
from app.astro.stellium_detection import Stellium
from app.astro.sign_blend import SignTheme
from app.astro.significance_scoring import ThemeUnit, AspectTheme, StelliumTheme, AngleTheme, SignBlendTheme
from app.core.constants import PRIORITY


def _get_sign_and_degree(degree: float) -> str:
    """Convert degree to sign and degree format (e.g., '27° Scorpio')."""
    signs = [
        'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]
    sign_index = int(degree / 30.0) % 12
    sign = signs[sign_index]
    degree_in_sign = degree % 30.0
    return f"{int(degree_in_sign)}° {sign}"


def format_placements_payload(aspects: List[AspectHit],
                             angle_contacts: List[AngleContact],
                             stelliums: List[Stellium],
                             sign_themes: List[SignTheme],
                             selected_themes: List[ThemeUnit],
                             planet_degrees: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Format the strict placements payload structure.
    
    Args:
        aspects: List of detected aspects
        angle_contacts: List of angle contacts
        stelliums: List of detected stelliums
        sign_themes: List of sign blend themes
        selected_themes: List of top-ranked theme units
        
    Returns:
        Formatted placements payload
    """
    # Format stelliums
    formatted_stelliums = []
    for stellium in stelliums:
        formatted_stelliums.append({
            "sign": stellium.sign,
            "planets": stellium.planets,
            "span_deg": stellium.span_deg
        })
    
    # Format angle contacts
    formatted_angles = []
    for contact in angle_contacts:
        formatted_angles.append({
            "angle": contact.angle,
            "contact": contact.contact,
            "orb_deg": contact.orb_deg,
            "planet": contact.planet,
            "planet_deg": contact.planet_deg,
            "angle_deg": contact.angle_deg
        })
    
    # Format aspects
    formatted_aspects = []
    for aspect in aspects:
        a_deg = planet_degrees.get(aspect.planets[0], 0.0) if planet_degrees else 0.0
        b_deg = planet_degrees.get(aspect.planets[1], 0.0) if planet_degrees else 0.0
        formatted_aspects.append({
            "a": aspect.planets[0],
            "b": aspect.planets[1],
            "type": aspect.type,
            "orb_deg": aspect.diff,
            "a_deg": a_deg,
            "b_deg": b_deg
        })
    
    # Format sign themes
    formatted_sign_themes = []
    for theme in sign_themes:
        formatted_sign_themes.append({
            "sign": theme.sign,
            "keywords": theme.keywords
        })
    
    # Format selected themes
    formatted_selected_themes = []
    for theme in selected_themes:
        if isinstance(theme, AspectTheme):
            label = f"{theme.a} {theme.type} {theme.b}"
            degrees = f"{_get_sign_and_degree(theme.a_deg)} / {_get_sign_and_degree(theme.b_deg)}"
            payload_ref = {"a": theme.a, "b": theme.b}
        elif isinstance(theme, StelliumTheme):
            label = f"Stellium in {theme.sign}"
            degrees = f"{theme.span_deg}° span"
            payload_ref = {"planets": theme.planets, "sign": theme.sign}
        elif isinstance(theme, AngleTheme):
            label = f"{theme.planet} conjunct {theme.angle}"
            degrees = _get_sign_and_degree(theme.planet_deg)
            payload_ref = {"planet": theme.planet, "angle": theme.angle}
        elif isinstance(theme, SignBlendTheme):
            label = f"{theme.sign} blend"
            degrees = theme.sign
            payload_ref = {"sign": theme.sign, "keywords": theme.keywords}
        else:
            label = f"{theme.source} {theme.type}"
            degrees = ""
            payload_ref = {}
        
        formatted_selected_themes.append({
            "source": theme.source,
            "label": label,
            "degrees": degrees,
            "type": theme.type,
            "orb_deg": theme.orb_deg,
            "significance": theme.significance,
            "payload_ref": payload_ref
        })
    
    return {
        "stelliums": formatted_stelliums,
        "angles": formatted_angles,
        "aspects": formatted_aspects,
        "sign_themes": formatted_sign_themes,
        "selected_themes": formatted_selected_themes
    }


def format_meta_payload() -> Dict[str, Any]:
    """Format the meta information payload."""
    return {
        "rules": {
            "orb_sun_moon": 5.0,
            "orb_others": 3.0,
            "stellium_span": 8.0
        },
        "computed_at": datetime.utcnow().isoformat() + "Z"
    }
