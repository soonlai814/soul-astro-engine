"""
Special astrological pattern detection for Grand Cross, Grand Trine, T-Square, and Mystic Rectangle.
These patterns are ranked above all other aspects (group_rank = 0, special_feature = true).
"""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from app.core.angles import normalize_deg
from app.core.constants import (
    ORB_SUN_MOON, ORB_OTHERS, GRAND_TRINE_ORB, T_SQUARE_OPPOSITION_ORB, 
    T_SQUARE_SQUARE_ORB, GRAND_CROSS_ORB, MYSTIC_RECTANGLE_ORB
)


@dataclass
class AstrologicalPattern:
    """Represents a detected astrological pattern."""
    pattern_type: str  # 'grand_cross', 'grand_trine', 't_square', 'mystic_rectangle'
    planets: List[str]
    orb_deg: float  # tightest orb in the pattern


def _sep_deg(a: float, b: float) -> float:
    """Separation in degrees, folded to 0..180."""
    d = abs(a - b) % 360.0
    return d if d <= 180.0 else 360.0 - d


def _orb_for_pair(p1: str, p2: str) -> float:
    """Get orb tolerance for planet pair."""
    if "Sun" in (p1, p2) or "Moon" in (p1, p2):
        return ORB_SUN_MOON
    return ORB_OTHERS


def _is_aspect_within_orb(sep: float, target_angle: float, p1: str, p2: str) -> bool:
    """Check if separation forms aspect within orb tolerance."""
    orb_max = _orb_for_pair(p1, p2)
    diff = abs(sep - target_angle)
    return diff <= orb_max


def detect_grand_trine(planets: Dict[str, float]) -> Optional[AstrologicalPattern]:
    """
    Detect Grand Trine: 3 planets ~120° apart each, forming an equilateral triangle.
    Orb: ±5°
    Theme: "Blessed flow — natural harmony, effortless support."
    """
    if len(planets) < 3:
        return None
    
    planet_names = list(planets.keys())
    planet_positions = list(planets.values())
    
    # Check all combinations of 3 planets
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            for k in range(j + 1, len(planet_names)):
                p1, p2, p3 = planet_names[i], planet_names[j], planet_names[k]
                pos1, pos2, pos3 = planet_positions[i], planet_positions[j], planet_positions[k]
                
                # Calculate separations
                sep12 = _sep_deg(pos1, pos2)
                sep23 = _sep_deg(pos2, pos3)
                sep31 = _sep_deg(pos3, pos1)
                
                # Check if all separations are close to 120°
                orb_tolerance = GRAND_TRINE_ORB
                
                if (abs(sep12 - 120.0) <= orb_tolerance and
                    abs(sep23 - 120.0) <= orb_tolerance and
                    abs(sep31 - 120.0) <= orb_tolerance):
                    
                    # Calculate tightest orb
                    orb12 = abs(sep12 - 120.0)
                    orb23 = abs(sep23 - 120.0)
                    orb31 = abs(sep31 - 120.0)
                    tightest_orb = min(orb12, orb23, orb31)
                    
                    return AstrologicalPattern(
                        pattern_type="grand_trine",
                        planets=[p1, p2, p3],
                        orb_deg=round(tightest_orb, 2)
                    )
    
    return None


def detect_t_square(planets: Dict[str, float]) -> Optional[AstrologicalPattern]:
    """
    Detect T-Square: An opposition with a third planet squaring both ends.
    Orb: opposition ±5°, squares ±3°.
    Theme: "Creative stress — growth through challenge and adjustment."
    """
    if len(planets) < 3:
        return None
    
    planet_names = list(planets.keys())
    planet_positions = list(planets.values())
    
    # Find all oppositions first
    oppositions = []
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1, p2 = planet_names[i], planet_names[j]
            pos1, pos2 = planet_positions[i], planet_positions[j]
            sep = _sep_deg(pos1, pos2)
            
            if _is_aspect_within_orb(sep, 180.0, p1, p2):
                oppositions.append((p1, p2, pos1, pos2, abs(sep - 180.0)))
    
    # For each opposition, check if any third planet squares both ends
    for opp_p1, opp_p2, opp_pos1, opp_pos2, opp_orb in oppositions:
        for k, (p3, pos3) in enumerate(zip(planet_names, planet_positions)):
            if p3 in [opp_p1, opp_p2]:
                continue
            
            # Check if p3 squares both ends of the opposition
            sep1_3 = _sep_deg(opp_pos1, pos3)
            sep2_3 = _sep_deg(opp_pos2, pos3)
            
            if (_is_aspect_within_orb(sep1_3, 90.0, opp_p1, p3) and
                _is_aspect_within_orb(sep2_3, 90.0, opp_p2, p3)):
                
                # Calculate tightest orb
                square_orb1 = abs(sep1_3 - 90.0)
                square_orb2 = abs(sep2_3 - 90.0)
                tightest_orb = min(opp_orb, square_orb1, square_orb2)
                
                return AstrologicalPattern(
                    pattern_type="t_square",
                    planets=[opp_p1, opp_p2, p3],
                    orb_deg=round(tightest_orb, 2)
                )
    
    return None


def detect_grand_cross(planets: Dict[str, float]) -> Optional[AstrologicalPattern]:
    """
    Detect Grand Cross: 4 planets forming two oppositions (180°) and four squares (90°).
    Rule: Each planet ~90° apart ± orb tolerance.
    Theme: "Dynamic tension — constant push for balance and growth."
    """
    if len(planets) < 4:
        return None
    
    planet_names = list(planets.keys())
    planet_positions = list(planets.values())
    
    # Check all combinations of 4 planets
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            for k in range(j + 1, len(planet_names)):
                for l in range(k + 1, len(planet_names)):
                    p1, p2, p3, p4 = planet_names[i], planet_names[j], planet_names[k], planet_names[l]
                    pos1, pos2, pos3, pos4 = planet_positions[i], planet_positions[j], planet_positions[k], planet_positions[l]
                    
                    # Check if this forms a Grand Cross
                    # We need two oppositions and four squares
                    positions = [pos1, pos2, pos3, pos4]
                    names = [p1, p2, p3, p4]
                    
                    # Find oppositions
                    oppositions = []
                    for m in range(4):
                        for n in range(m + 1, 4):
                            sep = _sep_deg(positions[m], positions[n])
                            if _is_aspect_within_orb(sep, 180.0, names[m], names[n]):
                                oppositions.append((m, n, abs(sep - 180.0)))
                    
                    # Need exactly 2 oppositions
                    if len(oppositions) != 2:
                        continue
                    
                    # Check if we have 4 squares
                    squares = []
                    for m in range(4):
                        for n in range(m + 1, 4):
                            sep = _sep_deg(positions[m], positions[n])
                            if _is_aspect_within_orb(sep, 90.0, names[m], names[n]):
                                squares.append((m, n, abs(sep - 90.0)))
                    
                    # Need exactly 4 squares
                    if len(squares) != 4:
                        continue
                    
                    # Calculate tightest orb
                    all_orbs = [orb for _, _, orb in oppositions + squares]
                    tightest_orb = min(all_orbs)
                    
                    return AstrologicalPattern(
                        pattern_type="grand_cross",
                        planets=[p1, p2, p3, p4],
                        orb_deg=round(tightest_orb, 2)
                    )
    
    return None


def detect_mystic_rectangle(planets: Dict[str, float]) -> Optional[AstrologicalPattern]:
    """
    Detect Mystic Rectangle: 4 planets forming two oppositions + two trines + two sextiles.
    Rule: Oppositions bridged by trines/sextiles (harmonious release valves).
    Theme: "Complex, creative tension that finds graceful outlets."
    """
    if len(planets) < 4:
        return None
    
    planet_names = list(planets.keys())
    planet_positions = list(planets.values())
    
    # Check all combinations of 4 planets
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            for k in range(j + 1, len(planet_names)):
                for l in range(k + 1, len(planet_names)):
                    p1, p2, p3, p4 = planet_names[i], planet_names[j], planet_names[k], planet_names[l]
                    pos1, pos2, pos3, pos4 = planet_positions[i], planet_positions[j], planet_positions[k], planet_positions[l]
                    
                    positions = [pos1, pos2, pos3, pos4]
                    names = [p1, p2, p3, p4]
                    
                    # Find oppositions
                    oppositions = []
                    for m in range(4):
                        for n in range(m + 1, 4):
                            sep = _sep_deg(positions[m], positions[n])
                            if _is_aspect_within_orb(sep, 180.0, names[m], names[n]):
                                oppositions.append((m, n, abs(sep - 180.0)))
                    
                    # Need exactly 2 oppositions
                    if len(oppositions) != 2:
                        continue
                    
                    # Find trines
                    trines = []
                    for m in range(4):
                        for n in range(m + 1, 4):
                            sep = _sep_deg(positions[m], positions[n])
                            if _is_aspect_within_orb(sep, 120.0, names[m], names[n]):
                                trines.append((m, n, abs(sep - 120.0)))
                    
                    # Find sextiles
                    sextiles = []
                    for m in range(4):
                        for n in range(m + 1, 4):
                            sep = _sep_deg(positions[m], positions[n])
                            if _is_aspect_within_orb(sep, 60.0, names[m], names[n]):
                                sextiles.append((m, n, abs(sep - 60.0)))
                    
                    # Need exactly 2 trines and 2 sextiles
                    if len(trines) != 2 or len(sextiles) != 2:
                        continue
                    
                    # Calculate tightest orb
                    all_orbs = [orb for _, _, orb in oppositions + trines + sextiles]
                    tightest_orb = min(all_orbs)
                    
                    return AstrologicalPattern(
                        pattern_type="mystic_rectangle",
                        planets=[p1, p2, p3, p4],
                        orb_deg=round(tightest_orb, 2)
                    )
    
    return None


def detect_special_patterns(planets: Dict[str, float]) -> List[AstrologicalPattern]:
    """
    Detect all special astrological patterns in order of priority.
    
    Priority order:
    1. Grand Cross (most complex)
    2. Grand Trine
    3. T-Square
    4. Mystic Rectangle
    
    Args:
        planets: Dict of planet names to longitudes
        
    Returns:
        List of detected patterns (empty if none found)
    """
    patterns = []
    
    # Check for patterns in priority order
    # Note: We check Grand Cross first as it's the most complex
    grand_cross = detect_grand_cross(planets)
    if grand_cross:
        patterns.append(grand_cross)
        return patterns  # Grand Cross takes precedence
    
    grand_trine = detect_grand_trine(planets)
    if grand_trine:
        patterns.append(grand_trine)
    
    t_square = detect_t_square(planets)
    if t_square:
        patterns.append(t_square)
    
    mystic_rectangle = detect_mystic_rectangle(planets)
    if mystic_rectangle:
        patterns.append(mystic_rectangle)
    
    return patterns
