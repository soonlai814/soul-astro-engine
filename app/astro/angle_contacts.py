"""
Angle contact detection for planets near AC/DC/MC/IC.
"""
from typing import Dict, List
from dataclasses import dataclass
from app.core.constants import ANGLE_ORB_DEG
from app.core.angles import normalize_deg


@dataclass
class AngleContact:
    angle: str  # AC, DC, MC, IC
    contact: str  # e.g., "Pluto conjunct MC"
    orb_deg: float
    planet: str
    planet_deg: float
    angle_deg: float


def _sep_deg(a: float, b: float) -> float:
    """Separation in degrees, folded to 0..180."""
    d = abs(a - b) % 360.0
    return d if d <= 180.0 else 360.0 - d


def detect_angle_contacts(planets: Dict[str, float], 
                         composite_angles: Dict[str, float]) -> List[AngleContact]:
    """
    Detect planet contacts with composite angles.
    
    Args:
        planets: Dict of planet names to longitudes
        composite_angles: Dict of angle names (AC, DC, MC, IC) to longitudes
        
    Returns:
        List of AngleContact objects for planets within ANGLE_ORB_DEG of any angle
    """
    contacts = []
    
    if not composite_angles:
        return contacts
    
    for planet, planet_lon in planets.items():
        for angle_name, angle_lon in composite_angles.items():
            if angle_lon is None:
                continue
                
            separation = _sep_deg(planet_lon, angle_lon)
            
            if separation <= ANGLE_ORB_DEG:
                contact_label = f"{planet} conjunct {angle_name}"
                contacts.append(AngleContact(
                    angle=angle_name,
                    contact=contact_label,
                    orb_deg=round(separation, 2),
                    planet=planet,
                    planet_deg=round(planet_lon, 2),
                    angle_deg=round(angle_lon, 2)
                ))
    
    # Sort by orb (tighter first)
    contacts.sort(key=lambda c: c.orb_deg)
    return contacts
