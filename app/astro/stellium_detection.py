"""
Stellium detection: 3+ planets within STELLIUM_SPAN_DEG.
"""
from typing import Dict, List, Tuple
from dataclasses import dataclass
from app.core.constants import STELLIUM_SPAN_DEG, SIGN_KEYWORDS
from app.core.angles import normalize_deg


@dataclass
class Stellium:
    sign: str
    planets: List[str]
    span_deg: float
    keywords: List[str]


def _get_sign(degree: float) -> str:
    """Convert degree to zodiac sign."""
    signs = [
        'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]
    sign_index = int(degree / 30.0) % 12
    return signs[sign_index]


def _get_modal_sign(degrees: List[float]) -> str:
    """Get the most common sign among the given degrees."""
    sign_counts = {}
    for deg in degrees:
        sign = _get_sign(deg)
        sign_counts[sign] = sign_counts.get(sign, 0) + 1
    
    # Return the most common sign
    return max(sign_counts.items(), key=lambda x: x[1])[0]


def detect_stelliums(planets: Dict[str, float]) -> List[Stellium]:
    """
    Detect stelliums: 3+ planets within STELLIUM_SPAN_DEG.
    
    Uses a sliding window approach:
    1. Sort planets by longitude
    2. Maintain a sliding window capturing 3+ planets within the span
    3. For each cluster, compute span + list of planets + modal sign
    
    Args:
        planets: Dict of planet names to longitudes
        
    Returns:
        List of Stellium objects
    """
    if len(planets) < 3:
        return []
    
    # Sort planets by longitude
    sorted_planets = sorted(planets.items(), key=lambda x: x[1])
    stelliums = []
    
    # Use sliding window approach
    for i in range(len(sorted_planets)):
        window_planets = []
        window_degrees = []
        
        # Start window at planet i
        for j in range(i, len(sorted_planets)):
            planet_name, planet_deg = sorted_planets[j]
            window_planets.append(planet_name)
            window_degrees.append(planet_deg)
            
            # Check if we have 3+ planets and they're within the span
            if len(window_planets) >= 3:
                span = max(window_degrees) - min(window_degrees)
                
                # Handle 0-360° wraparound
                if span > 180:
                    # Check if we need to wrap around
                    wrapped_degrees = []
                    for deg in window_degrees:
                        if deg < 180:
                            wrapped_degrees.append(deg + 360)
                        else:
                            wrapped_degrees.append(deg)
                    span = max(wrapped_degrees) - min(wrapped_degrees)
                
                if span <= STELLIUM_SPAN_DEG:
                    # Found a stellium
                    modal_sign = _get_modal_sign(window_degrees)
                    keywords = SIGN_KEYWORDS.get(modal_sign, [])
                    
                    stellium = Stellium(
                        sign=modal_sign,
                        planets=window_planets.copy(),
                        span_deg=round(span, 2),
                        keywords=keywords
                    )
                    
                    # Avoid duplicates by checking if this stellium is already found
                    is_duplicate = False
                    for existing in stelliums:
                        if (set(existing.planets) == set(window_planets) or
                            set(existing.planets).issubset(set(window_planets))):
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        stelliums.append(stellium)
    
    # Sort by span (tighter first), then by number of planets (more first)
    stelliums.sort(key=lambda s: (s.span_deg, -len(s.planets)))
    
    return stelliums
