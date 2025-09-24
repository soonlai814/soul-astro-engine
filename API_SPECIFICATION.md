# Soul Astro Engine - API Specification

## Overview

The Soul Astro Engine provides a RESTful API for comprehensive astrological composite analysis. This document details all endpoints, request/response formats, and error handling.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required. All endpoints are publicly accessible.

## Content Type

All requests and responses use `application/json`.

## Endpoints

### 1. Health Check

#### GET `/health`

Check if the service is running.

**Response:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200 OK`: Service is healthy

---

### 2. Service Information

#### GET `/about`

Get service metadata and configuration.

**Response:**
```json
{
  "name": "Soul Astro Engine",
  "version": "0.1.0",
  "license": "AGPL-3.0",
  "swe_path": "/path/to/swiss/ephemeris"
}
```

**Status Codes:**
- `200 OK`: Service information retrieved

---

### 3. Basic Composite Calculation

#### POST `/composite`

Calculate composite midpoints for two charts.

**Request Body:**
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

**Request Schema:**
- `parent.datetime_utc` (string, required): UTC timestamp in ISO format
- `parent.lat` (number, optional): Latitude in decimal degrees (+N, -S)
- `parent.lon` (number, optional): Longitude in decimal degrees (+E, -W)
- `child.datetime_utc` (string, required): UTC timestamp in ISO format
- `child.lat` (number, optional): Latitude in decimal degrees (+N, -S)
- `child.lon` (number, optional): Longitude in decimal degrees (+E, -W)

**Response:**
```json
{
  "longitudes": {
    "parent": {
      "Sun": 280.123,
      "Moon": 45.678,
      "Mercury": 275.456,
      "Venus": 290.789,
      "Mars": 15.234,
      "Jupiter": 120.567,
      "Saturn": 200.890,
      "Uranus": 310.123,
      "Neptune": 330.456,
      "Pluto": 250.789,
      "North Node": 180.123,
      "South Node": 0.123
    },
    "child": {
      "Sun": 90.456,
      "Moon": 120.789,
      "Mercury": 85.123,
      "Venus": 95.456,
      "Mars": 75.789,
      "Jupiter": 200.123,
      "Saturn": 150.456,
      "Uranus": 280.789,
      "Neptune": 300.123,
      "Pluto": 220.456,
      "North Node": 45.789,
      "South Node": 225.789
    }
  },
  "composite": {
    "Sun": 185.290,
    "Moon": 83.234,
    "Mercury": 180.290,
    "Venus": 193.123,
    "Mars": 45.512,
    "Jupiter": 160.345,
    "Saturn": 175.673,
    "Uranus": 295.456,
    "Neptune": 315.290,
    "Pluto": 235.623,
    "North Node": 112.956,
    "South Node": 292.956
  },
  "meta": {
    "src": "Swiss Ephemeris"
  }
}
```

**Status Codes:**
- `200 OK`: Composite calculation successful
- `400 Bad Request`: Invalid datetime format or missing required fields

---

### 4. Aspect Analysis

#### POST `/aspects`

Analyze aspects for given planet longitudes.

**Request Body:**
```json
{
  "longitudes": {
    "Sun": 185.290,
    "Moon": 83.234,
    "Mercury": 180.290,
    "Venus": 193.123,
    "Mars": 45.512,
    "Jupiter": 160.345,
    "Saturn": 175.673,
    "Uranus": 295.456,
    "Neptune": 315.290,
    "Pluto": 235.623,
    "North Node": 112.956,
    "South Node": 292.956
  },
  "composite_angles": {
    "AC": 185.123,
    "DC": 5.123,
    "MC": 275.456,
    "IC": 95.456
  }
}
```

**Request Schema:**
- `longitudes` (object, required): Planet names to longitude degrees
- `composite_angles` (object, optional): Angle names to longitude degrees

**Response:**
```json
{
  "count": 7,
  "aspects": [
    {
      "type": "conjunction",
      "planets": ["Sun", "Mercury"],
      "anchor": "Sun",
      "angle": 0.0,
      "orb": 4.99,
      "separation": 4.99,
      "score": 2.998,
      "strength": 0.749,
      "hardness_weight": 2.0,
      "emotional_bonus": 0.2,
      "angularity_boost": 0.0
    },
    {
      "type": "opposition",
      "planets": ["North Node", "South Node"],
      "anchor": "North Node",
      "angle": 180.0,
      "orb": 0.0,
      "separation": 180.0,
      "score": 2.0,
      "strength": 0.909,
      "hardness_weight": 1.8,
      "emotional_bonus": 0.0,
      "angularity_boost": 0.0
    }
  ]
}
```

**Response Schema:**
- `count` (integer): Number of aspects found
- `aspects` (array): List of aspect objects
  - `type` (string): Aspect type (conjunction, square, trine, opposition)
  - `planets` (array): Array of two planet names
  - `anchor` (string): Primary planet for labeling
  - `angle` (number): Target aspect angle (0°, 90°, 120°, 180°)
  - `orb` (number): Actual orb in degrees
  - `separation` (number): Actual angular separation
  - `score` (number): Calculated significance score
  - `strength` (number): Normalized strength (0.0-1.0)
  - `hardness_weight` (number): Base weight for aspect type
  - `emotional_bonus` (number): Bonus for emotional planets
  - `angularity_boost` (number): Bonus for angular contact

**Status Codes:**
- `200 OK`: Aspect analysis successful
- `400 Bad Request`: Invalid input data

---

### 5. Top Aspects (Legacy)

#### POST `/top-aspects`

Get ranked and grouped aspects (legacy endpoint).

**Request Body:** Same as `/aspects`

**Response:**
```json
{
  "count": 5,
  "items": [
    {
      "aspect_label": "Sun conjunction Mercury",
      "type": "conjunction",
      "anchor": "Sun",
      "planets": ["Sun", "Mercury"],
      "group_id": "sun_conjunction_group_1",
      "cluster_tag": "fusion_sun_group",
      "stellium": false,
      "bucket": "conjunction",
      "orb_min": 4.99,
      "orb_avg": 4.99,
      "score_max": 2.998,
      "score_merged": 2.998,
      "weights": {
        "hardness_weight": 2.0,
        "emotional_bonus": 0.2,
        "angularity_boost": 0.0,
        "group_bonus": 0.0
      }
    }
  ]
}
```

---

### 6. Comprehensive Composite Analysis

#### POST `/top-aspects/composite`

**Main endpoint for complete composite analysis according to specification.**

**Request Body:**
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
      },
      {
        "a": "North Node",
        "b": "South Node",
        "type": "opposition",
        "orb_deg": 0.0,
        "a_deg": 112.956,
        "b_deg": 292.956
      }
    ],
    "sign_themes": [
      {
        "sign": "Scorpio",
        "keywords": ["depth", "loyalty", "intensity"]
      },
      {
        "sign": "Sagittarius",
        "keywords": ["freedom", "truth", "adventure"]
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
      },
      {
        "source": "angle",
        "label": "Pluto conjunct MC",
        "degrees": "25° Scorpio",
        "type": "angle",
        "orb_deg": 1.8,
        "significance": 3.545,
        "payload_ref": {
          "planet": "Pluto",
          "angle": "MC"
        }
      },
      {
        "source": "stellium",
        "label": "Stellium in Scorpio",
        "degrees": "7.5° span",
        "type": "stellium",
        "orb_deg": 7.5,
        "significance": 2.8,
        "payload_ref": {
          "planets": ["Sun", "Mercury", "Venus"],
          "sign": "Scorpio"
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

**Response Schema:**

#### Placements Object
- `stelliums` (array): Detected stelliums
  - `sign` (string): Modal zodiac sign
  - `planets` (array): List of planet names in stellium
  - `span_deg` (number): Span in degrees
- `angles` (array): Angle contacts
  - `angle` (string): Angle name (AC, DC, MC, IC)
  - `contact` (string): Descriptive contact label
  - `orb_deg` (number): Orb in degrees
  - `planet` (string): Planet name
  - `planet_deg` (number): Planet longitude
  - `angle_deg` (number): Angle longitude
- `aspects` (array): All detected aspects
  - `a` (string): First planet
  - `b` (string): Second planet
  - `type` (string): Aspect type
  - `orb_deg` (number): Orb in degrees
  - `a_deg` (number): First planet longitude
  - `b_deg` (number): Second planet longitude
- `sign_themes` (array): Sign blend themes
  - `sign` (string): Zodiac sign
  - `keywords` (array): Associated keywords
- `selected_themes` (array): Top 5 ranked themes
  - `source` (string): Theme source (aspect, stellium, angle, sign_blend)
  - `label` (string): Human-readable label
  - `degrees` (string): Position information
  - `type` (string): Theme type
  - `orb_deg` (number): Orb in degrees
  - `significance` (number): Calculated significance score
  - `payload_ref` (object): Reference data for theme

#### Meta Object
- `rules` (object): Analysis rules used
  - `orb_sun_moon` (number): Orb limit for Sun/Moon aspects
  - `orb_others` (number): Orb limit for other aspects
  - `stellium_span` (number): Stellium detection span
- `computed_at` (string): ISO timestamp of computation
- `src` (string): Data source (Swiss Ephemeris)
- `version` (string): Engine version

**Status Codes:**
- `200 OK`: Analysis completed successfully
- `400 Bad Request`: Invalid input data or calculation error

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Scenarios

#### 1. Invalid DateTime Format
```json
{
  "detail": "Invalid datetime format: Invalid isoformat string: '1990-01-01'"
}
```

#### 2. Missing Required Fields
```json
{
  "detail": "Field required: parent.datetime_utc"
}
```

#### 3. Swiss Ephemeris Calculation Error
```json
{
  "detail": "Error processing request: swe.calc_ut failed for Sun (retflag=-1)"
}
```

#### 4. Invalid Coordinates
```json
{
  "detail": "Error processing request: Invalid latitude: 91.0 (must be -90 to 90)"
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request data
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

---

## Data Types and Validation

### DateTime Format
- **Format**: ISO 8601 with timezone
- **Examples**: 
  - `"1990-01-01T12:00:00Z"` (UTC)
  - `"1990-01-01T12:00:00+00:00"` (UTC with explicit timezone)
  - `"1990-01-01T12:00:00-05:00"` (EST)

### Coordinates
- **Latitude**: -90.0 to 90.0 (decimal degrees)
- **Longitude**: -180.0 to 180.0 (decimal degrees)
- **Positive**: North/East
- **Negative**: South/West

### Planet Names
Valid planet names:
- `"Sun"`, `"Moon"`, `"Mercury"`, `"Venus"`, `"Mars"`
- `"Jupiter"`, `"Saturn"`, `"Uranus"`, `"Neptune"`, `"Pluto"`
- `"North Node"`, `"South Node"`

### Angle Names
Valid angle names:
- `"AC"` (Ascendant)
- `"DC"` (Descendant)
- `"MC"` (Midheaven)
- `"IC"` (Imum Coeli)

---

## Rate Limiting

Currently no rate limiting implemented. Consider implementing for production use.

## Caching

No caching implemented. Consider implementing for frequently requested calculations.

## Versioning

API versioning not currently implemented. Version information available in `/about` endpoint.

---

This API specification provides complete documentation for integrating with the Soul Astro Engine.
