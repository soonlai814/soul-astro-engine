# Soul Astro Engine

A sophisticated astrological calculation engine built with FastAPI that provides planetary calculations, aspect detection, composite chart generation, and advanced aspect grouping with intelligent scoring algorithms.

## Features

### 🌟 Core Capabilities
- **Swiss Ephemeris Integration**: High-precision planetary calculations using the Swiss Ephemeris library
- **Aspect Detection**: Identifies major astrological aspects (conjunction, square, trine, opposition) with configurable orbs
- **Composite Charts**: Generates composite charts from two birth charts using midpoint calculations
- **Advanced Grouping**: Groups and ranks aspects with sophisticated scoring algorithms
- **Angular Analysis**: Calculates and analyzes angular houses (AC, DC, MC, IC) and their composite midpoints
- **REST API**: FastAPI-based web service with comprehensive endpoints

### 🎯 Intelligent Scoring System
- **Hardness Weights**: Different weights for aspect types (conjunction: 2.0, opposition: 1.8, square: 1.6, trine: 1.2)
- **Orb Scoring**: Dynamic orb calculations based on planetary pairs (5° for Sun/Moon, 3° for others)
- **Emotional Bonuses**: Additional scoring for Sun, Moon, and Mars aspects
- **Angularity Boost**: Enhanced scoring for planets near angular houses (±5°)
- **Group Bonuses**: Clustering bonuses for stelliums and grouped aspects
- **Stellium Detection**: Identifies when 3+ planets cluster in the same aspect pattern

### 📊 Advanced Grouping
- **Band Clustering**: Groups aspects within ±3° separation bands
- **Theme Classification**: Categorizes clusters by astrological themes (fusion, intensity, friction, ease)
- **Priority Ranking**: Sophisticated ranking system considering hardness, orbs, and emotional significance
- **Anchor Selection**: Intelligent planet prioritization for cluster labeling

## API Endpoints

### Health & Info
- `GET /health` - Service health check
- `GET /about` - Service information and configuration

### Core Calculations
- `POST /composite` - Generate composite chart from two birth charts
- `POST /aspects` - Detect aspects from planetary longitudes
- `POST /top-aspects` - Get grouped and ranked aspects with advanced scoring
- `POST /top-aspects/composite` - Composite chart with top aspects analysis

## Installation and Setup

### Prerequisites
- Python 3.11+
- Swiss Ephemeris data files (included in `ephe/` directory)

### Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd soul-astro-engine

# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env to set SWE_EPHE_PATH to the ephe directory path
```

### Running the Service
```bash
# Start the API server
python -m uvicorn app.main:app --reload --port 8000

# Or using the virtual environment's uvicorn
.venv/bin/uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## Usage Examples

### Basic Composite Chart
```python
import requests

# Create a composite chart
response = requests.post("http://localhost:8000/composite", json={
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
})
```

### Aspect Analysis
```python
# Analyze aspects from planetary positions
response = requests.post("http://localhost:8000/aspects", json={
    "longitudes": {
        "Sun": 120.5,
        "Moon": 45.2,
        "Mars": 300.8,
        "Venus": 90.1
    },
    "composite_angles": {
        "AC": 15.0,
        "DC": 195.0,
        "MC": 285.0,
        "IC": 105.0
    }
})
```

### Top Aspects with Grouping
```python
# Get ranked and grouped aspects
response = requests.post("http://localhost:8000/top-aspects", json={
    "longitudes": {
        "Sun": 120.5,
        "Moon": 45.2,
        "Mars": 300.8,
        "Venus": 90.1,
        "Saturn": 180.3
    }
})
```

## Project Structure

```
soul-astro-engine/
├── app/
│   ├── astro/           # Astrological calculation modules
│   │   ├── aspects.py   # Aspect detection and analysis
│   │   ├── composite.py # Composite chart calculations
│   │   ├── rank_group.py # Advanced grouping and ranking
│   │   └── swe_wrap.py  # Swiss Ephemeris wrapper
│   ├── core/            # Core utility functions
│   │   └── angles.py    # Angular calculations and utilities
│   └── main.py          # FastAPI application and endpoints
├── ephe/                # Swiss Ephemeris data files
├── tests/               # Test suite
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Pydantic**: Data validation and settings management
- **Swiss Ephemeris**: High-precision astronomical calculations
- **Uvicorn**: ASGI server for FastAPI
- **Python-dotenv**: Environment variable management
- **Pytest**: Testing framework

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_aspects.py
```

## Configuration

The service requires the following environment variables:

- `SWE_EPHE_PATH`: Path to Swiss Ephemeris data files (defaults to `./ephe`)
- `APP_VERSION`: Application version (defaults to "0.1.0")

## License

AGPL-3.0

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Support

For issues and questions, please open an issue on the repository.