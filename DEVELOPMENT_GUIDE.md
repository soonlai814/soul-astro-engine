# Soul Astro Engine - Development Guide

## Overview

This guide provides comprehensive information for developers working with the Soul Astro Engine, including setup, testing, debugging, and extending the system.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Running the Application](#running-the-application)
4. [Testing](#testing)
5. [Debugging](#debugging)
6. [Adding New Features](#adding-new-features)
7. [Performance Optimization](#performance-optimization)
8. [Troubleshooting](#troubleshooting)

## Development Environment Setup

### Prerequisites

- Python 3.11+
- pip (Python package manager)
- Git
- Swiss Ephemeris data files

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

4. **Set up environment variables:**
```bash
# Create .env file
echo "SWE_EPHE_PATH=/path/to/swiss/ephemeris/data" > .env
echo "APP_VERSION=0.1.0" >> .env
```

5. **Download Swiss Ephemeris data:**
   - Download from [Swiss Ephemeris website](https://www.astro.com/swisseph/)
   - Extract to a directory (e.g., `/usr/local/share/swisseph/`)
   - Update `SWE_EPHE_PATH` in `.env`

### IDE Setup

#### VS Code
1. Install Python extension
2. Select Python interpreter from virtual environment
3. Install recommended extensions:
   - Python
   - Pylance
   - Python Test Explorer

#### PyCharm
1. Open project directory
2. Configure Python interpreter to use virtual environment
3. Set up run configurations for FastAPI

## Project Structure

```
soul-astro-engine/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── core/
│   │   ├── __init__.py
│   │   ├── constants.py        # Shared constants
│   │   └── angles.py          # Angle calculation utilities
│   └── astro/
│       ├── __init__.py
│       ├── aspects.py          # Aspect detection
│       ├── angle_contacts.py   # Angle contact detection
│       ├── stellium_detection.py # Stellium detection
│       ├── sign_blend.py       # Sign blend synthesis
│       ├── significance_scoring.py # Theme scoring
│       ├── payload_formatter.py # Response formatting
│       ├── composite_engine.py # Main analysis engine
│       ├── composite.py        # Composite calculations
│       ├── rank_group.py       # Legacy grouping logic
│       └── swe_wrap.py         # Swiss Ephemeris integration
├── tests/
│   ├── test_aspects.py         # Aspect detection tests
│   ├── test_grouping_spec.py   # Legacy grouping tests
│   └── test_engine_spec.py     # Comprehensive engine tests
├── ephe/                       # Swiss Ephemeris data files
├── requirements.txt
├── .env
├── README.md
├── ARCHITECTURE.md
├── ALGORITHMS.md
├── API_SPECIFICATION.md
└── DEVELOPMENT_GUIDE.md
```

## Running the Application

### Development Server

```bash
# Activate virtual environment
source venv/bin/activate

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server

```bash
# Run with Gunicorn (recommended for production)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker (Optional)

```bash
# Build image
docker build -t soul-astro-engine .

# Run container
docker run -p 8000:8000 -e SWE_EPHE_PATH=/app/ephe soul-astro-engine
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_engine_spec.py

# Run specific test
python -m pytest tests/test_engine_spec.py::test_sun_moon_orb_rules

# Run with coverage
python -m pytest --cov=app --cov-report=html
```

### Test Categories

#### Unit Tests
- Individual function testing
- Edge case validation
- Mock data testing

#### Integration Tests
- End-to-end pipeline testing
- Real astronomical data validation
- API endpoint testing

#### Performance Tests
- Large dataset handling
- Memory usage monitoring
- Response time measurement

### Writing Tests

```python
def test_new_feature():
    """Test description explaining what is being tested."""
    # Arrange
    input_data = {"Sun": 0.0, "Moon": 5.0}
    expected_result = "expected_value"
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_result
    assert len(result) > 0
```

## Debugging

### Logging

```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Use in code
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Debug Mode

```bash
# Run with debug logging
PYTHONPATH=. python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from app.astro.composite_engine import analyze_composite
# Your debug code here
"
```

### Common Debug Scenarios

#### 1. Swiss Ephemeris Errors
```python
# Check ephemeris path
import os
print(f"SWE_EPHE_PATH: {os.getenv('SWE_EPHE_PATH')}")
print(f"Path exists: {os.path.exists(os.getenv('SWE_EPHE_PATH'))}")

# Test calculation
from app.astro.swe_wrap import planet_longitudes
from datetime import datetime
dt = datetime(1990, 1, 1, 12, 0, 0)
try:
    result = planet_longitudes(dt)
    print("Calculation successful")
except Exception as e:
    print(f"Error: {e}")
```

#### 2. Aspect Detection Issues
```python
# Debug aspect detection
from app.astro.aspects import detect_aspects

planets = {"Sun": 0.0, "Moon": 4.9}
aspects = detect_aspects(planets)
print(f"Found {len(aspects)} aspects")
for aspect in aspects:
    print(f"{aspect.type}: {aspect.planets} (orb: {aspect.diff})")
```

#### 3. Stellium Detection Problems
```python
# Debug stellium detection
from app.astro.stellium_detection import detect_stelliums

planets = {"Sun": 0.0, "Moon": 3.0, "Mars": 7.5}
stelliums = detect_stelliums(planets)
print(f"Found {len(stelliums)} stelliums")
for stellium in stelliums:
    print(f"Sign: {stellium.sign}, Planets: {stellium.planets}, Span: {stellium.span_deg}")
```

## Adding New Features

### 1. New Aspect Types

```python
# In app/core/constants.py
ASPECTS = {
    0: 'conjunction',
    30: 'semi-sextile',  # New aspect
    60: 'sextile',       # New aspect
    90: 'square',
    120: 'trine',
    150: 'quincunx',     # New aspect
    180: 'opposition'
}

# In app/astro/aspects.py
# Update orb rules if needed
def _orb_for_pair(p1: str, p2: str) -> float:
    if "Sun" in (p1, p2) or "Moon" in (p1, p2):
        return ORB_SUN_MOON
    elif "sextile" in ASPECTS.values():  # New aspect type
        return 2.0  # Smaller orb for minor aspects
    return ORB_OTHERS
```

### 2. New Theme Types

```python
# In app/astro/significance_scoring.py
@dataclass
class NewThemeType:
    source: str
    type: str
    orb_deg: float
    # Add new fields
    significance: float = 0.0

# Update ThemeUnit union
ThemeUnit = Union[AspectTheme, StelliumTheme, AngleTheme, SignBlendTheme, NewThemeType]

# Add scoring logic
def _get_base_score(theme_type: str) -> float:
    base_scores = {
        # ... existing scores
        'new_theme': 1.5  # New theme base score
    }
    return base_scores.get(theme_type, 1.0)
```

### 3. New Detection Algorithms

```python
# Create new file: app/astro/new_detection.py
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class NewDetection:
    # Define detection result structure
    pass

def detect_new_feature(planets: Dict[str, float]) -> List[NewDetection]:
    """
    Algorithm for new detection feature.
    
    Args:
        planets: Dict of planet names to longitudes
        
    Returns:
        List of NewDetection objects
    """
    # Implementation here
    pass
```

### 4. Update Main Engine

```python
# In app/astro/composite_engine.py
from app.astro.new_detection import detect_new_feature

def analyze_composite(composite_planets: Dict[str, float], 
                     composite_angles: Dict[str, float] = None) -> Dict[str, Any]:
    # ... existing code ...
    
    # Add new detection
    new_detections = detect_new_feature(composite_planets)
    
    # Convert to theme units
    for detection in new_detections:
        theme_units.append(NewThemeType(
            source="new_feature",
            type="new_type",
            orb_deg=detection.orb,
            # ... other fields
        ))
    
    # ... rest of function
```

## Performance Optimization

### 1. Profiling

```python
# Install profiling tools
pip install cProfile memory_profiler

# Profile function
import cProfile
cProfile.run('analyze_composite(planets, angles)')

# Memory profiling
from memory_profiler import profile

@profile
def analyze_composite(composite_planets, composite_angles):
    # Function implementation
    pass
```

### 2. Caching

```python
# Add caching for expensive calculations
from functools import lru_cache

@lru_cache(maxsize=128)
def calculate_sign(degree: float) -> str:
    """Cache sign calculations."""
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    sign_index = int(degree / 30.0) % 12
    return signs[sign_index]
```

### 3. Parallel Processing

```python
# For large datasets
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

def parallel_aspect_detection(planets: Dict[str, float]) -> List[AspectHit]:
    """Parallel aspect detection for large planet sets."""
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        # Split work and process in parallel
        pass
```

## Troubleshooting

### Common Issues

#### 1. Swiss Ephemeris Path Error
```
RuntimeError: SWE_EPHE_PATH missing or invalid directory.
```
**Solution:** Check that `SWE_EPHE_PATH` environment variable is set correctly and points to valid directory.

#### 2. Import Errors
```
ModuleNotFoundError: No module named 'swisseph'
```
**Solution:** Install Swiss Ephemeris Python bindings:
```bash
pip install pyswisseph
```

#### 3. Test Failures
```
AssertionError: assert 0 > 0
```
**Solution:** Check test data and expected results. Use debug mode to inspect intermediate values.

#### 4. Memory Issues
```
MemoryError: Unable to allocate array
```
**Solution:** 
- Reduce dataset size
- Implement data streaming
- Add memory monitoring

### Debug Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Environment variables set
- [ ] Swiss Ephemeris data available
- [ ] Test data valid
- [ ] Logging enabled
- [ ] Error messages clear

### Getting Help

1. **Check logs** for error messages
2. **Run tests** to identify failing components
3. **Use debug mode** to inspect intermediate values
4. **Check documentation** for API usage
5. **Review code** for logical errors

## Code Quality Guidelines

### 1. Style Guidelines

- Follow PEP 8 Python style guide
- Use type hints for all functions
- Write comprehensive docstrings
- Keep functions small and focused
- Use meaningful variable names

### 2. Testing Guidelines

- Write tests for all new features
- Test edge cases and error conditions
- Use descriptive test names
- Mock external dependencies
- Maintain high test coverage

### 3. Documentation Guidelines

- Update documentation for new features
- Include code examples
- Document API changes
- Keep architecture docs current
- Write clear commit messages

---

This development guide provides comprehensive information for working with the Soul Astro Engine codebase effectively.
