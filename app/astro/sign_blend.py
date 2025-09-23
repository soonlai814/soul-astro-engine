"""
Sign blend synthesis for theme detection.
Detects if many weighted bodies fall into two dominant signs.
"""
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import Counter
from app.core.constants import SIGN_KEYWORDS, CORE_BODIES


@dataclass
class SignTheme:
    sign: str
    keywords: List[str]


def _get_sign(degree: float) -> str:
    """Convert degree to zodiac sign."""
    signs = [
        'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]
    sign_index = int(degree / 30.0) % 12
    return signs[sign_index]


def _get_planet_weight(planet: str) -> float:
    """Get weight for planet based on importance."""
    if planet in CORE_BODIES:
        return 2.0  # Core bodies get double weight
    return 1.0


def detect_sign_blend(planets: Dict[str, float]) -> List[SignTheme]:
    """
    Detect sign blend themes.
    
    Computes a lightweight "sign blend" to inform one theme (max 1):
    - Detect if many weighted bodies fall into two dominant signs
    - Attach keyword lists for LLM color
    
    Args:
        planets: Dict of planet names to longitudes
        
    Returns:
        List of SignTheme objects (max 1 as per spec)
    """
    if len(planets) < 4:  # Need at least 4 planets for meaningful blend
        return []
    
    # Count weighted signs
    sign_weights = Counter()
    for planet, degree in planets.items():
        sign = _get_sign(degree)
        weight = _get_planet_weight(planet)
        sign_weights[sign] += weight
    
    # Get the two most dominant signs
    most_common = sign_weights.most_common(2)
    
    if len(most_common) < 2:
        return []
    
    sign1, weight1 = most_common[0]
    sign2, weight2 = most_common[1]
    
    # Check if there's a meaningful blend (both signs have significant weight)
    total_weight = sum(sign_weights.values())
    min_threshold = total_weight * 0.15  # Each sign should be at least 15% of total
    
    if weight1 < min_threshold or weight2 < min_threshold:
        return []
    
    # Check if the two dominant signs together represent a significant portion
    dominant_weight = weight1 + weight2
    if dominant_weight < total_weight * 0.4:  # At least 40% of total weight
        return []
    
    # Return both signs as themes
    themes = []
    for sign, weight in [(sign1, weight1), (sign2, weight2)]:
        keywords = SIGN_KEYWORDS.get(sign, [])
        themes.append(SignTheme(sign=sign, keywords=keywords))
    
    return themes
