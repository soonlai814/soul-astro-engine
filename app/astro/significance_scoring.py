"""
New significance scoring system for theme units.
"""
from typing import Dict, List, Union, Optional
from dataclasses import dataclass
from app.core.constants import CORE_BODIES, ORB_SUN_MOON, ORB_OTHERS


@dataclass
class AspectTheme:
    """Aspect theme unit."""
    source: str  # 'aspect'
    type: str
    orb_deg: float
    a: str
    b: str
    a_deg: float
    b_deg: float
    significance: float = 0.0


@dataclass
class StelliumTheme:
    """Stellium theme unit."""
    source: str  # 'stellium'
    type: str
    orb_deg: float
    sign: str
    planets: List[str]
    span_deg: float
    significance: float = 0.0


@dataclass
class AngleTheme:
    """Angle contact theme unit."""
    source: str  # 'angle'
    type: str
    orb_deg: float
    angle: str
    planet: str
    planet_deg: float
    angle_deg: float
    significance: float = 0.0


@dataclass
class SignBlendTheme:
    """Sign blend theme unit."""
    source: str  # 'sign_blend'
    type: str
    orb_deg: float
    sign: str
    keywords: List[str]
    significance: float = 0.0


# Union type for all theme units
ThemeUnit = Union[AspectTheme, StelliumTheme, AngleTheme, SignBlendTheme]


def _get_base_score(theme_type: str) -> float:
    """Get base score for theme type."""
    base_scores = {
        'conjunction': 2.0,
        'opposition': 2.0,
        'square': 1.4,
        'trine': 1.2,
        'stellium': 1.8,
        'angle': 1.6,
        'sign_blend': 1.0
    }
    return base_scores.get(theme_type, 1.0)


def _get_tightness_score(orb_deg: float, orb_limit: float) -> float:
    """Calculate tightness score: 1.0 + max(0, (orb_limit - orb)/orb_limit)"""
    if orb_limit <= 0:
        return 1.0
    tightness_factor = max(0, (orb_limit - orb_deg) / orb_limit)
    return 1.0 + tightness_factor


def _get_core_bonus(planets: List[str]) -> float:
    """+0.3 if any planet is in CORE_BODIES."""
    return 0.3 if any(p in CORE_BODIES for p in planets) else 0.0


def _get_angle_bonus(theme: ThemeUnit, angle_contacts: List) -> float:
    """+0.2 if theme is also near an angle."""
    if theme.source == 'angle':
        return 0.2  # Already an angle contact
    
    # Check if aspect involves planets near angles
    if theme.source == 'aspect' and isinstance(theme, AspectTheme):
        for contact in angle_contacts:
            if contact.planet in [theme.a, theme.b]:
                return 0.2
    
    return 0.0


def _get_stellium_bonus(theme: ThemeUnit, stelliums: List) -> float:
    """+0.2 if theme members are in a detected stellium."""
    if theme.source == 'stellium':
        return 0.2  # Already a stellium
    
    # Check if aspect involves planets in stelliums
    if theme.source == 'aspect' and isinstance(theme, AspectTheme):
        for stellium in stelliums:
            if theme.a in stellium.planets and theme.b in stellium.planets:
                return 0.2
    
    return 0.0


def calculate_significance(theme: ThemeUnit, 
                          angle_contacts: List = None, 
                          stelliums: List = None) -> float:
    """
    Calculate significance score for a theme unit.
    
    Formula:
    score = base * tightness + core_bonus + angle_bonus + stellium_bonus
    
    Args:
        theme: ThemeUnit to score
        angle_contacts: List of angle contacts for bonus calculation
        stelliums: List of stelliums for bonus calculation
        
    Returns:
        Significance score
    """
    if angle_contacts is None:
        angle_contacts = []
    if stelliums is None:
        stelliums = []
    
    # Base score
    base = _get_base_score(theme.type)
    
    # Tightness score
    orb_limit = ORB_SUN_MOON if theme.source == 'aspect' and isinstance(theme, AspectTheme) and any(p in ['Sun', 'Moon'] for p in [theme.a, theme.b]) else ORB_OTHERS
    tightness = _get_tightness_score(theme.orb_deg, orb_limit)
    
    # Bonuses
    planets = []
    if isinstance(theme, AspectTheme):
        planets = [theme.a, theme.b]
    elif isinstance(theme, StelliumTheme):
        planets = theme.planets
    elif isinstance(theme, AngleTheme):
        planets = [theme.planet]
    elif isinstance(theme, SignBlendTheme):
        planets = []  # Sign blend doesn't have specific planets
    
    core_bonus = _get_core_bonus(planets)
    angle_bonus = _get_angle_bonus(theme, angle_contacts)
    stellium_bonus = _get_stellium_bonus(theme, stelliums)
    
    # Calculate final score
    score = base * tightness + core_bonus + angle_bonus + stellium_bonus
    
    return round(score, 3)


def rank_themes(themes: List[ThemeUnit], 
                angle_contacts: List = None, 
                stelliums: List = None) -> List[ThemeUnit]:
    """
    Rank themes by significance score and deduplicate overlaps.
    
    Args:
        themes: List of theme units to rank
        angle_contacts: List of angle contacts for bonus calculation
        stelliums: List of stelliums for bonus calculation
        
    Returns:
        Top 5 themes sorted by significance (descending)
    """
    if angle_contacts is None:
        angle_contacts = []
    if stelliums is None:
        stelliums = []
    
    # Calculate scores
    scored_themes = []
    for theme in themes:
        theme.significance = calculate_significance(theme, angle_contacts, stelliums)
        scored_themes.append(theme)
    
    # Sort by significance (descending)
    scored_themes.sort(key=lambda t: t.significance, reverse=True)
    
    # Deduplicate overlaps (prefer aspects over stelliums when both exist)
    deduplicated = []
    used_planets = set()
    
    for theme in scored_themes:
        if theme.source == 'aspect' and isinstance(theme, AspectTheme):
            # Check if both planets are already used in a stellium
            if theme.a in used_planets and theme.b in used_planets:
                continue  # Skip this aspect as both planets are in stellium
            used_planets.update([theme.a, theme.b])
            deduplicated.append(theme)
        elif theme.source == 'stellium' and isinstance(theme, StelliumTheme):
            # Check if any planets are already used
            if any(p in used_planets for p in theme.planets):
                continue  # Skip this stellium as planets are already used
            used_planets.update(theme.planets)
            deduplicated.append(theme)
        else:
            # Angle contacts and sign blends don't conflict
            deduplicated.append(theme)
    
    # Return top 5
    return deduplicated[:5]