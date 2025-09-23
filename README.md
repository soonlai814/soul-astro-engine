# Soul Astro Engine

A comprehensive Python-based astrological analysis engine that performs composite chart analysis. The engine detects aspects, stelliums, angle contacts, and sign themes, then ranks them by significance to provide structured insights for relationship analysis.

## Features

- **Comprehensive Aspect Detection**: Identifies planetary aspects with proper orb rules (5° for Sun/Moon, 3° for others)
- **Stellium Detection**: Finds clusters of 3+ planets within 8° span
- **Angle Contact Analysis**: Detects planets near composite angles (AC/DC/MC/IC)
- **Sign Blend Synthesis**: Identifies dominant sign themes with weighted analysis
- **Significance Scoring**: Complex scoring system with tightness multipliers and bonuses
- **RESTful API**: FastAPI-based web service with comprehensive endpoints
- **Swiss Ephemeris Integration**: High-precision astronomical calculations
- **Comprehensive Testing**: Full test coverage with edge case validation

## Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd soul-astro-engine
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment:**
```bash
echo "SWE_EPHE_PATH=/path/to/swiss/ephemeris/data" > .env
echo "APP_VERSION=0.1.0" >> .env
```

5. **Download Swiss Ephemeris data:**
   - Download from [Swiss Ephemeris website](https://www.astro.com/swisseph/)
   - Extract to a directory and update `SWE_EPHE_PATH` in `.env`

### Running the Application

```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### API Usage

#### Basic Composite Analysis

```bash
curl -X POST "http://localhost:8000/top-aspects/composite" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

#### Response Format

```json
{
  "placements": {
    "stelliums": [
      {
        "sign": "Scorpio",
        "planets": ["Sun", "Mercury", "Venus"],
        "span_deg": 7.5
      }
    ],
    "angles": [
      {
        "angle": "MC",
        "contact": "Pluto conjunct MC",
        "orb_deg": 1.8,
        "planet": "Pluto",
        "planet_deg": 235.623,
        "angle_deg": 237.423
      }
    ],
    "aspects": [
      {
        "a": "Sun",
        "b": "Mercury",
        "type": "conjunction",
        "orb_deg": 4.99,
        "a_deg": 185.290,
        "b_deg": 180.290
      }
    ],
    "sign_themes": [
      {
        "sign": "Scorpio",
        "keywords": ["depth", "loyalty", "intensity"]
      }
    ],
    "selected_themes": [
      {
        "source": "aspect",
        "label": "Sun conjunction Mercury",
        "degrees": "5° Scorpio / 0° Scorpio",
        "type": "conjunction",
        "orb_deg": 4.99,
        "significance": 4.388,
        "payload_ref": {
          "a": "Sun",
          "b": "Mercury"
        }
      }
    ]
  },
  "meta": {
    "rules": {
      "orb_sun_moon": 5.0,
      "orb_others": 3.0,
      "stellium_span": 8.0
    },
    "computed_at": "2024-01-01T12:00:00Z",
    "src": "Swiss Ephemeris",
    "version": "0.1.0"
  }
}
```

## Testing

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_engine_spec.py

# Run with coverage
python -m pytest --cov=app --cov-report=html
```

## Documentation

- **[Architecture Guide](ARCHITECTURE.md)** - System architecture and component overview
- **[Algorithm Documentation](ALGORITHMS.md)** - Detailed algorithm explanations and formulas
- **[API Specification](API_SPECIFICATION.md)** - Complete API reference
- **[Development Guide](DEVELOPMENT_GUIDE.md)** - Development setup and guidelines

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/about` | GET | Service information |
| `/composite` | POST | Basic composite calculation |
| `/aspects` | POST | Aspect analysis |
| `/top-aspects` | POST | Legacy grouped aspects |
| `/top-aspects/composite` | POST | **Main endpoint** - Comprehensive analysis |

## Algorithm Overview

### 1. Aspect Detection
- Calculates angular separation between all planet pairs
- Applies orb rules: 5° for Sun/Moon, 3° for others
- Detects conjunction, square, trine, and opposition aspects
- Handles 0-360° wraparound correctly

### 2. Stellium Detection
- Uses sliding window approach to find 3+ planets within 8°
- Handles 0-360° wraparound for accurate span calculation
- Determines modal sign for stellium labeling
- Prevents duplicate stellium detection

### 3. Angle Contact Detection
- Detects planets within 3° of composite angles (AC/DC/MC/IC)
- Creates descriptive contact labels
- Sorts by orb tightness

### 4. Sign Blend Synthesis
- Weights planets (core bodies = 2.0x, others = 1.0x)
- Identifies two most dominant signs
- Applies thresholds for meaningful dominance
- Returns sign themes with keywords

### 5. Significance Scoring
- Complex formula: `base × tightness + core_bonus + angle_bonus + stellium_bonus`
- Base scores: 2.0 (conj/opp), 1.4 (square), 1.2 (trine), 1.8 (stellium), 1.6 (angle)
- Tightness multiplier: 1.0 + max(0, (orb_limit - orb) / orb_limit)
- Bonuses: +0.3 (core bodies), +0.2 (angular), +0.2 (stellium)

### 6. Theme Ranking
- Ranks by significance score (descending)
- Deduplicates overlapping themes
- Returns top 5 themes
- Priority: conjunction > opposition > stellium > angle > square > trine

## Configuration

### Environment Variables

- `SWE_EPHE_PATH`: Path to Swiss Ephemeris data files
- `APP_VERSION`: Application version string

### Constants

All astrological constants are centralized in `app/core/constants.py`:

```python
ORB_SUN_MOON = 5.0          # Sun/Moon aspect orb
ORB_OTHERS = 3.0            # Other aspect orb
STELLIUM_SPAN_DEG = 8.0     # Stellium detection span
ANGLE_ORB_DEG = 3.0         # Angle contact tolerance
CORE_BODIES = {...}         # Core bodies for scoring
PRIORITY = [...]            # Theme priority order
```

## Dependencies

### Core Dependencies
- `swisseph`: Swiss Ephemeris astronomical calculations
- `fastapi`: Web framework
- `pydantic`: Data validation
- `python-dotenv`: Environment configuration

### Development Dependencies
- `pytest`: Testing framework
- `pytest-asyncio`: Async testing support

## Performance

### Time Complexity
- Aspect detection: O(n²) where n = number of planets
- Stellium detection: O(n²) with sliding window optimization
- Overall: O(n²) due to aspect detection

### Space Complexity
- O(n²) worst case for aspect storage
- O(n) average case for other components

### Optimization Strategies
- Sliding window for stellium detection
- Early returns in validation
- Efficient sorting algorithms
- Minimal object creation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

AGPL-3.0 - See [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or contributions, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information
4. Contact the development team

---

**Soul Astro Engine** - Comprehensive astrological analysis for relationship insights.