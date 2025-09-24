# Soul Astro Engine - Algorithm Documentation

## Overview

This document provides detailed explanations of the core algorithms used in the Soul Astro Engine, including mathematical formulas, edge cases, and implementation details.

## 1. Aspect Detection Algorithm

### Mathematical Foundation

The aspect detection algorithm identifies planetary aspects based on angular separation and orb tolerances.

```python
def detect_aspects(longitudes: Dict[str, float]) -> List[AspectHit]:
    """
    Core Algorithm:
    1. For each planet pair (A, B):
       - Calculate angular separation: min(|A-B|, 360-|A-B|)
       - Find nearest aspect angle (0°, 90°, 120°, 180°)
       - Check if within orb limit
       - Create AspectHit if valid
    2. Sort by orb tightness and aspect priority
    """
```

### Angular Separation Calculation

```python
def _sep_deg(a: float, b: float) -> float:
    """
    Calculate separation in degrees, folded to 0..180.
    
    Formula: min(|a-b|, 360-|a-b|)
    
    Examples:
    - 10° and 20° → |10-20| = 10°
    - 10° and 350° → min(|10-350|, |350-10|) = min(340, 20) = 20°
    - 180° and 0° → min(|180-0|, |0-180|) = min(180, 180) = 180°
    """
    d = abs(a - b) % 360.0
    return d if d <= 180.0 else 360.0 - d
```

### Orb Rules

```python
def _orb_for_pair(p1: str, p2: str) -> float:
    """
    Orb limits based on planet types:
    - Sun/Moon pairs: 5.0°
    - All other pairs: 3.0°
    
    Rationale: Sun and Moon are considered more influential
    and can form valid aspects at wider orbs.
    """
    if "Sun" in (p1, p2) or "Moon" in (p1, p2):
        return ORB_SUN_MOON  # 5.0°
    return ORB_OTHERS  # 3.0°
```

### Aspect Types and Priorities

```python
ASPECTS = {
    0: 'conjunction',    # 0° - strongest aspect
    90: 'square',        # 90° - challenging aspect
    120: 'trine',        # 120° - harmonious aspect
    180: 'opposition'    # 180° - intense aspect
}

# Sorting priority (lower number = higher priority)
priority = {"opposition": 0, "square": 1, "conjunction": 2, "trine": 3}
```

### Edge Cases Handled

1. **0-360° Wraparound**: Properly handles cases like 10° and 350°
2. **Exact Aspects**: Handles exact 0°, 90°, 120°, 180° separations
3. **Orb Boundaries**: Correctly applies 4.9° vs 5.1° rules
4. **Duplicate Prevention**: Prevents duplicate aspects for same planet pair

## 2. Stellium Detection Algorithm

### Sliding Window Approach

```python
def detect_stelliums(planets: Dict[str, float]) -> List[Stellium]:
    """
    Algorithm:
    1. Sort planets by longitude (ascending)
    2. For each starting planet i:
       - Create sliding window starting at i
       - Add planets j, j+1, ... until 3+ planets
       - Calculate span: max(degrees) - min(degrees)
       - Handle 0-360° wraparound if span > 180°
       - If span <= 8°, found stellium
    3. Determine modal sign for stellium
    4. Deduplicate overlapping stelliums
    """
```

### Span Calculation with Wraparound

```python
def calculate_span(degrees: List[float]) -> float:
    """
    Calculate span with proper 0-360° wraparound handling.
    
    Algorithm:
    1. Calculate basic span: max(degrees) - min(degrees)
    2. If span > 180°, check wraparound:
       - Add 360° to degrees < 180°
       - Recalculate span with wrapped degrees
    3. Return minimum of both calculations
    """
    basic_span = max(degrees) - min(degrees)
    
    if basic_span > 180:
        # Handle wraparound
        wrapped_degrees = []
        for deg in degrees:
            if deg < 180:
                wrapped_degrees.append(deg + 360)
            else:
                wrapped_degrees.append(deg)
        wrapped_span = max(wrapped_degrees) - min(wrapped_degrees)
        return min(basic_span, wrapped_span)
    
    return basic_span
```

### Modal Sign Detection

```python
def _get_modal_sign(degrees: List[float]) -> str:
    """
    Find the most common zodiac sign among the degrees.
    
    Algorithm:
    1. Convert each degree to zodiac sign (0-30° = Aries, etc.)
    2. Count occurrences of each sign
    3. Return the most frequent sign
    """
    sign_counts = {}
    for deg in degrees:
        sign = _get_sign(deg)
        sign_counts[sign] = sign_counts.get(sign, 0) + 1
    
    return max(sign_counts.items(), key=lambda x: x[1])[0]
```

### Deduplication Logic

```python
def deduplicate_stelliums(stelliums: List[Stellium]) -> List[Stellium]:
    """
    Remove overlapping stelliums to avoid double-counting.
    
    Rules:
    1. If stellium A is subset of stellium B → keep B
    2. If stellium A equals stellium B → keep one
    3. If stelliums overlap but neither is subset → keep both
    """
    deduplicated = []
    for stellium in stelliums:
        is_duplicate = False
        for existing in deduplicated:
            if (set(existing.planets) == set(stellium.planets) or
                set(existing.planets).issubset(set(stellium.planets))):
                is_duplicate = True
                break
        if not is_duplicate:
            deduplicated.append(stellium)
    return deduplicated
```

## 3. Angle Contact Detection Algorithm

### Contact Detection

```python
def detect_angle_contacts(planets: Dict[str, float], 
                         composite_angles: Dict[str, float]) -> List[AngleContact]:
    """
    Algorithm:
    1. For each planet P and angle X (AC/DC/MC/IC):
       - Calculate separation: min(|P-X|, 360-|P-X|)
       - If separation <= 3°, create AngleContact
    2. Sort by orb tightness (tighter first)
    """
```

### Angle Types

```python
ANGLES = {
    'AC': 'Ascendant',    # Rising sign
    'DC': 'Descendant',   # Setting sign (AC + 180°)
    'MC': 'Midheaven',    # Highest point
    'IC': 'Imum Coeli'    # Lowest point (MC + 180°)
}
```

### Contact Labeling

```python
def create_contact_label(planet: str, angle: str) -> str:
    """
    Create descriptive contact label.
    
    Examples:
    - "Pluto conjunct MC"
    - "Sun conjunct AC"
    - "Moon conjunct IC"
    """
    return f"{planet} conjunct {angle}"
```

## 4. Sign Blend Synthesis Algorithm

### Weighted Sign Analysis

```python
def detect_sign_blend(planets: Dict[str, float]) -> List[SignTheme]:
    """
    Algorithm:
    1. Weight planets (core bodies = 2.0, others = 1.0)
    2. Count weighted signs
    3. Find two most dominant signs
    4. Apply thresholds:
       - Each sign >= 15% of total weight
       - Combined >= 40% of total weight
    5. Return both signs as themes
    """
```

### Planet Weighting

```python
def _get_planet_weight(planet: str) -> float:
    """
    Weight planets based on astrological importance.
    
    Core bodies (2.0x weight):
    - Sun, Moon, Venus, Mars, Saturn, Pluto
    - North Node, South Node
    
    Other bodies (1.0x weight):
    - Mercury, Jupiter, Uranus, Neptune
    """
    if planet in CORE_BODIES:
        return 2.0
    return 1.0
```

### Threshold Calculations

```python
def calculate_thresholds(total_weight: float) -> Tuple[float, float]:
    """
    Calculate minimum thresholds for sign blend detection.
    
    Individual threshold: 15% of total weight
    Combined threshold: 40% of total weight
    
    Rationale: Ensures meaningful dominance without being too restrictive
    """
    individual_threshold = total_weight * 0.15
    combined_threshold = total_weight * 0.40
    return individual_threshold, combined_threshold
```

## 5. Significance Scoring Algorithm

### Base Score Calculation

```python
def _get_base_score(theme_type: str) -> float:
    """
    Base scores by theme type:
    
    Conjunction: 2.0    # Strongest aspect
    Opposition: 2.0     # Strongest aspect
    Square: 1.4         # Challenging aspect
    Trine: 1.2          # Harmonious aspect
    Stellium: 1.8       # Cluster power
    Angle: 1.6          # Angular strength
    Sign Blend: 1.0     # Thematic influence
    """
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
```

### Tightness Score Calculation

```python
def _get_tightness_score(orb_deg: float, orb_limit: float) -> float:
    """
    Calculate tightness multiplier: 1.0 + max(0, (orb_limit - orb) / orb_limit)
    
    Examples:
    - orb_deg = 0°, orb_limit = 5° → 1.0 + (5-0)/5 = 2.0
    - orb_deg = 2.5°, orb_limit = 5° → 1.0 + (5-2.5)/5 = 1.5
    - orb_deg = 5°, orb_limit = 5° → 1.0 + (5-5)/5 = 1.0
    - orb_deg = 6°, orb_limit = 5° → 1.0 + max(0, (5-6)/5) = 1.0
    """
    if orb_limit <= 0:
        return 1.0
    
    tightness_factor = max(0, (orb_limit - orb_deg) / orb_limit)
    return 1.0 + tightness_factor
```

### Bonus Calculations

```python
def _get_core_bonus(planets: List[str]) -> float:
    """+0.3 if any planet is in CORE_BODIES"""
    return 0.3 if any(p in CORE_BODIES for p in planets) else 0.0

def _get_angle_bonus(theme: ThemeUnit, angle_contacts: List) -> float:
    """+0.2 if theme is also near an angle"""
    if theme.source == 'angle':
        return 0.2  # Already an angle contact
    
    # Check if aspect involves planets near angles
    if theme.source == 'aspect' and isinstance(theme, AspectTheme):
        for contact in angle_contacts:
            if contact.planet in [theme.a, theme.b]:
                return 0.2
    
    return 0.0

def _get_stellium_bonus(theme: ThemeUnit, stelliums: List) -> float:
    """+0.2 if theme members are in a detected stellium"""
    if theme.source == 'stellium':
        return 0.2  # Already a stellium
    
    # Check if aspect involves planets in stelliums
    if theme.source == 'aspect' and isinstance(theme, AspectTheme):
        for stellium in stelliums:
            if theme.a in stellium.planets and theme.b in stellium.planets:
                return 0.2
    
    return 0.0
```

### Final Score Formula

```python
def calculate_significance(theme: ThemeUnit) -> float:
    """
    Final significance score:
    
    score = base * tightness + core_bonus + angle_bonus + stellium_bonus
    
    Where:
    - base: Theme type base score (1.0 - 2.0)
    - tightness: Orb tightness multiplier (1.0 - 2.0)
    - core_bonus: +0.3 for core body involvement
    - angle_bonus: +0.2 for angular contact
    - stellium_bonus: +0.2 for stellium involvement
    """
    base = _get_base_score(theme.type)
    tightness = _get_tightness_score(theme.orb_deg, orb_limit)
    core_bonus = _get_core_bonus(planets)
    angle_bonus = _get_angle_bonus(theme, angle_contacts)
    stellium_bonus = _get_stellium_bonus(theme, stelliums)
    
    return base * tightness + core_bonus + angle_bonus + stellium_bonus
```

## 6. Theme Ranking and Deduplication

### Ranking Algorithm

```python
def rank_themes(themes: List[ThemeUnit]) -> List[ThemeUnit]:
    """
    Algorithm:
    1. Calculate significance score for each theme
    2. Sort by significance (descending)
    3. Deduplicate overlaps:
       - If aspect planets already used in stellium → skip aspect
       - If stellium planets already used → skip stellium
       - Angle contacts and sign blends don't conflict
    4. Return top 5 themes
    """
```

### Deduplication Rules

```python
def deduplicate_themes(scored_themes: List[ThemeUnit]) -> List[ThemeUnit]:
    """
    Deduplication rules:
    
    1. Aspect vs Stellium:
       - If both planets of aspect are in stellium → keep stellium, skip aspect
       - If only one planet in stellium → keep both
    
    2. Stellium vs Stellium:
       - If any planets overlap → keep higher scoring stellium
    
    3. Angle Contacts:
       - No conflicts with other theme types
       - Keep all valid angle contacts
    
    4. Sign Blends:
       - No conflicts with other theme types
       - Keep all valid sign blends
    """
    deduplicated = []
    used_planets = set()
    
    for theme in scored_themes:
        if theme.source == 'aspect' and isinstance(theme, AspectTheme):
            # Check if both planets are already used in a stellium
            if theme.a in used_planets and theme.b in used_planets:
                continue  # Skip this aspect
            used_planets.update([theme.a, theme.b])
            deduplicated.append(theme)
        elif theme.source == 'stellium' and isinstance(theme, StelliumTheme):
            # Check if any planets are already used
            if any(p in used_planets for p in theme.planets):
                continue  # Skip this stellium
            used_planets.update(theme.planets)
            deduplicated.append(theme)
        else:
            # Angle contacts and sign blends don't conflict
            deduplicated.append(theme)
    
    return deduplicated[:5]  # Return top 5
```

## 7. Mathematical Constants and Precision

### Degree Precision
- All calculations use 3 decimal places for degrees
- Swiss Ephemeris provides high precision (typically 6+ decimal places)
- Final results rounded to 2 decimal places for readability

### Orb Tolerance
- Sun/Moon aspects: 5.0° ± 0.1° (tested with 4.9° pass, 5.1° fail)
- Other aspects: 3.0° ± 0.1° (tested with 2.9° pass, 3.1° fail)
- Angle contacts: 3.0° ± 0.1°

### Stellium Detection
- Minimum planets: 3
- Maximum span: 8.0° ± 0.1°
- Wraparound handling: Proper 0-360° boundary crossing

### Sign Calculation
- 30° per sign (360° / 12 signs)
- Sign boundaries: 0-30° = Aries, 30-60° = Taurus, etc.
- Degree within sign: `degree % 30.0`

## 8. Performance Characteristics

### Time Complexity
- Aspect detection: O(n²) where n = number of planets
- Stellium detection: O(n²) with sliding window optimization
- Angle contacts: O(n×m) where m = number of angles (4)
- Sign blend: O(n)
- Overall: O(n²) due to aspect detection

### Space Complexity
- Planet storage: O(n)
- Aspect storage: O(n²) worst case
- Stellium storage: O(n) average case
- Overall: O(n²) worst case

### Optimization Strategies
1. **Sliding Window**: Efficient stellium detection
2. **Early Returns**: Skip invalid calculations
3. **Sorted Processing**: Process tighter orbs first
4. **Minimal Object Creation**: Reuse objects where possible

---

This algorithm documentation provides the mathematical foundation and implementation details for all core calculations in the Soul Astro Engine, ensuring accuracy and maintainability.
