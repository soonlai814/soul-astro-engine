# Soul Astro Engine - Architecture Documentation

## Overview

The Soul Astro Engine is a comprehensive Python-based astrological analysis system that performs composite chart analysis. It detects aspects, stelliums, angle contacts, and sign themes, then ranks them by significance to provide structured insights for relationship analysis.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Layer                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ /composite      │  │ /aspects        │  │ /top-aspects│  │
│  │                 │  │                 │  │ /composite  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                Composite Analysis Engine                    │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  analyze_composite() - Main Orchestrator                ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Aspect Detection│ │ Angle Contacts  │ │ Stellium Detection│
│  - detect_aspects│ │ - detect_angle_ │ │ - detect_stelliums│
│  - 5° Sun/Moon  │ │   contacts      │ │ - 3+ planets    │
│  - 3° others    │ │ - 3° tolerance  │ │ - 8° span       │
└─────────────────┘ └─────────────────┘ └─────────────────┘
                │               │               │
                ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Sign Blend     │ │ Significance    │ │ Payload         │
│  - detect_sign_ │ │ Scoring         │ │ Formatting      │
│    blend        │ │ - calculate_    │ │ - format_       │
│  - weighted     │ │   significance  │ │   placements_   │
│  - 2 dominant   │ │ - rank_themes   │ │   payload       │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Core Components

### 1. Constants Module (`app/core/constants.py`)

Centralized configuration:

```python
# Orb tolerances
ORB_SUN_MOON = 5.0      # Sun/Moon aspects
ORB_OTHERS = 3.0        # Other planet aspects

# Aspect definitions
ASPECTS = {0: 'conjunction', 90: 'square', 120: 'trine', 180: 'opposition'}

# Detection thresholds
STELLIUM_SPAN_DEG = 8.0  # 3+ planets within this span
ANGLE_ORB_DEG = 3.0      # Planet-to-angle contact tolerance

# Core bodies for significance scoring
CORE_BODIES = {'Sun', 'Moon', 'Venus', 'Mars', 'Saturn', 'Pluto', 'North Node', 'South Node'}

# Priority order for theme selection
PRIORITY = ['conjunction', 'opposition', 'stellium', 'angle', 'square', 'trine']
```

### 2. Swiss Ephemeris Integration (`app/astro/swe_wrap.py`)

Handles all astronomical calculations:

- **Planet Longitudes**: Calculates positions for all planets including North/South Nodes
- **Angle Calculations**: Computes AC/DC/MC/IC for individual charts
- **Composite Angles**: Midpoints parent and child angles
- **Error Handling**: Robust fallback for different Swiss Ephemeris API versions

### 3. Aspect Detection (`app/astro/aspects.py`)

Detects planetary aspects with proper orb rules:

```python
def detect_aspects(longitudes: Dict[str, float]) -> List[AspectHit]:
    """
    Algorithm:
    1. For each planet pair (A, B):
       - Calculate separation: min(|A-B|, 360-|A-B|)
       - Find nearest aspect angle (0°, 90°, 120°, 180°)
       - Check if within orb limit (5° for Sun/Moon, 3° others)
       - If valid, create AspectHit
    2. Sort by orb tightness and aspect priority
    """
```

**Key Features:**
- Proper 0-360° wraparound handling
- Sun/Moon get 5° orb, others get 3° orb
- Returns sorted list with tightest orbs first

### 4. Angle Contact Detection (`app/astro/angle_contacts.py`)

Detects planets near composite angles:

```python
def detect_angle_contacts(planets: Dict[str, float], 
                         composite_angles: Dict[str, float]) -> List[AngleContact]:
    """
    Algorithm:
    1. For each planet P and angle X (AC/DC/MC/IC):
       - Calculate separation: min(|P-X|, 360-|P-X|)
       - If separation <= 3°, create AngleContact
    2. Sort by orb tightness
    """
```

### 5. Stellium Detection (`app/astro/stellium_detection.py`)

Finds clusters of 3+ planets within 8°:

```python
def detect_stelliums(planets: Dict[str, float]) -> List[Stellium]:
    """
    Algorithm:
    1. Sort planets by longitude
    2. Use sliding window approach:
       - Start at planet i
       - Add planets j, j+1, ... until 3+ planets
       - Calculate span: max(degrees) - min(degrees)
       - Handle 0-360° wraparound if span > 180°
       - If span <= 8°, found stellium
    3. Determine modal sign for stellium
    4. Deduplicate overlapping stelliums
    """
```

**Key Features:**
- Handles 0-360° wraparound correctly
- Finds modal sign for stellium labeling
- Prevents duplicate stelliums

### 6. Sign Blend Synthesis (`app/astro/sign_blend.py`)

Detects dominant sign themes:

```python
def detect_sign_blend(planets: Dict[str, float]) -> List[SignTheme]:
    """
    Algorithm:
    1. Weight planets (core bodies = 2.0, others = 1.0)
    2. Count weighted signs
    3. Find two most dominant signs
    4. Check thresholds:
       - Each sign >= 15% of total weight
       - Combined >= 40% of total weight
    5. Return both signs as themes
    """
```

### 7. Significance Scoring (`app/astro/significance_scoring.py`)

Complex scoring system for theme ranking:

```python
def calculate_significance(theme: ThemeUnit) -> float:
    """
    Formula:
    score = base * tightness + core_bonus + angle_bonus + stellium_bonus
    
    Where:
    - base: 2.0 (conj/opp), 1.4 (square), 1.2 (trine), 1.8 (stellium), 1.6 (angle)
    - tightness: 1.0 + max(0, (orb_limit - orb) / orb_limit)
    - core_bonus: +0.3 if any planet in CORE_BODIES
    - angle_bonus: +0.2 if near angle
    - stellium_bonus: +0.2 if in stellium
    """
```

**Theme Types:**
- `AspectTheme`: Planet-to-planet aspects
- `StelliumTheme`: Planet clusters
- `AngleTheme`: Planet-to-angle contacts
- `SignBlendTheme`: Dominant sign themes

### 8. Payload Formatting (`app/astro/payload_formatter.py`)

Creates strict API response format:

```python
{
  "stelliums": [{"sign": "Scorpio", "planets": ["Sun", "Saturn"], "span_deg": 7.0}],
  "angles": [{"angle": "MC", "contact": "Pluto conjunct MC", "orb_deg": 1.8}],
  "aspects": [{"a": "Sun", "b": "Saturn", "type": "conjunction", "orb_deg": 2.4}],
  "sign_themes": [{"sign": "Scorpio", "keywords": ["depth", "loyalty"]}],
  "selected_themes": [{"source": "aspect", "label": "Sun conjunct Saturn", ...}]
}
```

## Data Flow

### 1. Input Processing
```
Parent Chart + Child Chart
         ↓
Parse UTC timestamps
         ↓
Calculate individual longitudes
         ↓
Compute composite midpoints
         ↓
Calculate composite angles (if coordinates provided)
```

### 2. Analysis Pipeline
```
Composite Data
     ↓
┌─────────────────────────────────────────────────────────┐
│  Parallel Detection Phase                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │ Aspects     │ │ Angles      │ │ Stelliums   │      │
│  │ Detection   │ │ Detection   │ │ Detection   │      │
│  └─────────────┘ └─────────────┘ └─────────────┘      │
│  ┌─────────────┐                                     │
│  │ Sign Blend  │                                     │
│  │ Detection   │                                     │
│  └─────────────┘                                     │
└─────────────────────────────────────────────────────────┘
     ↓
Convert to Theme Units
     ↓
Calculate Significance Scores
     ↓
Rank and Deduplicate
     ↓
Format Payload
```

### 3. Theme Ranking Algorithm
```
1. Calculate significance score for each theme
2. Sort by significance (descending)
3. Deduplicate overlaps:
   - If aspect planets already used in stellium → skip aspect
   - If stellium planets already used → skip stellium
   - Angle contacts and sign blends don't conflict
4. Return top 5 themes
```

## API Endpoints

### POST `/top-aspects/composite`
Main endpoint for composite analysis:

**Request:**
```json
{
  "parent": {
    "datetime_utc": "1990-01-01T12:00:00Z",
    "lat": 40.7128,
    "lon": -74.0060
  },
  "child": {
    "datetime_utc": "1995-06-15T18:30:00Z", 
    "lat": 34.0522,
    "lon": -118.2437
  }
}
```

**Response:**
```json
{
  "placements": {
    "stelliums": [...],
    "angles": [...],
    "aspects": [...],
    "sign_themes": [...],
    "selected_themes": [...]
  },
  "meta": {
    "rules": {"orb_sun_moon": 5.0, "orb_others": 3.0, "stellium_span": 8.0},
    "computed_at": "2024-01-01T12:00:00Z",
    "src": "Swiss Ephemeris",
    "version": "0.1.0"
  }
}
```

## Error Handling

### Swiss Ephemeris Errors
- Graceful fallback for different API versions
- Clear error messages for calculation failures
- Proper timezone handling

### Input Validation
- UTC timestamp parsing with timezone support
- Coordinate validation for angle calculations
- Planet name validation

### API Errors
- HTTP 400 for invalid input
- HTTP 500 for internal errors
- Detailed error messages for debugging

## Testing Strategy

### Unit Tests
- Individual component testing
- Edge case validation
- Mock data for isolated testing

### Integration Tests
- End-to-end pipeline testing
- Real astronomical data validation
- Performance testing

### Test Coverage
- 12/12 tests passing
- 100% critical path coverage
- Edge case validation (orb boundaries, wraparound)

## Performance Characteristics

### Time Complexity
- Aspect detection: O(n²) where n = number of planets
- Stellium detection: O(n²) with sliding window optimization
- Overall: O(n²) due to aspect detection

### Space Complexity
- O(n) for storing planet positions
- O(n²) for aspect storage (worst case)
- O(n) for stellium storage

### Optimization Strategies
- Sliding window for stellium detection
- Early returns in validation
- Efficient sorting algorithms
- Minimal object creation

## Future Enhancements

### Potential Improvements
1. **Caching**: Cache sign calculations for repeated use
2. **Parallel Processing**: Parallel aspect detection for large datasets
3. **Configuration**: Runtime configuration of orb limits and thresholds
4. **Metrics**: Performance monitoring and analytics
5. **Validation**: Enhanced input validation and sanitization

### Extensibility
- Plugin architecture for custom aspect types
- Configurable scoring algorithms
- Custom theme detection modules
- Alternative ephemeris backends

## Dependencies

### Core Dependencies
- `swisseph`: Swiss Ephemeris astronomical calculations
- `fastapi`: Web framework
- `pydantic`: Data validation
- `python-dotenv`: Environment configuration

### Development Dependencies
- `pytest`: Testing framework
- `pytest-asyncio`: Async testing support

## Configuration

### Environment Variables
- `SWE_EPHE_PATH`: Path to Swiss Ephemeris data files
- `APP_VERSION`: Application version string

### Constants
All astrological constants are centralized in `app/core/constants.py` for easy modification and consistency.

---

This architecture provides a robust, maintainable, and extensible foundation for astrological composite analysis while maintaining strict adherence to the specified requirements.
