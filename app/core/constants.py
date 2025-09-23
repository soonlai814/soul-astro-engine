"""
Shared constants for the Soul Astro Engine.
Keep rules consistent across the system.
"""

# Orb tolerances
ORB_SUN_MOON = 5.0
ORB_OTHERS = 3.0

# Aspect definitions
ASPECTS = {0: 'conjunction', 90: 'square', 120: 'trine', 180: 'opposition'}

# Stellium detection
STELLIUM_SPAN_DEG = 8.0  # 3+ planets within this span

# Angle contact tolerance
ANGLE_ORB_DEG = 3.0  # configurable: planet–AC/DC/MC/IC contact

# Core bodies for significance scoring
CORE_BODIES = {'Sun', 'Moon', 'Venus', 'Mars', 'Saturn', 'Pluto', 'North Node', 'South Node'}

# Priority order for theme selection (engine-side pre-rank to match selection order)
PRIORITY = ['conjunction', 'opposition', 'stellium', 'angle', 'square', 'trine']

# Sign keywords for theme synthesis
SIGN_KEYWORDS = {
    'Aries': ['initiative', 'courage', 'leadership'],
    'Taurus': ['stability', 'sensuality', 'persistence'],
    'Gemini': ['communication', 'curiosity', 'adaptability'],
    'Cancer': ['nurturing', 'intuition', 'emotional depth'],
    'Leo': ['creativity', 'confidence', 'generosity'],
    'Virgo': ['precision', 'service', 'analysis'],
    'Libra': ['harmony', 'partnership', 'balance'],
    'Scorpio': ['depth', 'loyalty', 'intensity'],
    'Sagittarius': ['freedom', 'truth', 'adventure'],
    'Capricorn': ['ambition', 'discipline', 'structure'],
    'Aquarius': ['innovation', 'independence', 'humanitarianism'],
    'Pisces': ['compassion', 'intuition', 'spirituality']
}
