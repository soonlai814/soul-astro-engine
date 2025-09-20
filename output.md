# Soul Astro Engine API Documentation

## Conventions

The following conventions are used throughout all API endpoints:

- **Degrees**: All positions and angles are in ecliptic degrees
- **Separation** (0–180°): Smallest angle between two points (e.g., 170° and 350° → separation = 180°)
- **Orb**: How far the separation is from an exact aspect angle (0°, 90°, 120°, 180°)
- **Max orb**: Sun/Moon pairs = 5°; all other pairs = 3°
- **Anchor planet**: For labeling/grouping, we pick an "emotional-first" anchor by priority:
  - Moon > Sun > Mars > Pluto > Venus > Saturn > Jupiter > Mercury > Uranus > Neptune

---

## API Endpoints

### `/composite` Response
```
{
  "longitudes": {
    "parent":   { "Sun": 123.45, "Moon": 210.78, ... },
    "child":    { "Sun":  87.65, "Moon":  35.42, ... }
  },
  "composite":   { "Sun": 105.55, "Moon": 123.10, ... },
  "meta": { "src": "Swiss Ephemeris" }
}
```

#### Response Fields

| Field | Description |
|-------|-------------|
| `longitudes.parent` / `longitudes.child` | Raw ecliptic longitudes for each body at the given datetimes |
| `composite` | Midpoint positions body-by-body (circular midpoint, so it wraps correctly across 0°/360°) |
| `meta.src` | Data source note |

---

### `/aspects` Response (Pair-by-Pair Hits)
```
{
  "longitudes": { "Sun": 105.55, "Moon": 123.10, ... },
  "composite_angles": { "AC": 15.2, "DC": 195.2, "MC": 280.9, "IC": 100.9 } // optional
}
```

#### Response Shape

```json
{
  "count": 7,
  "aspects": [
    {
      "type": "opposition",         // one of: conjunction|square|trine|opposition
      "planets": ["Moon","Pluto"],  // the pair
      "anchor": "Moon",             // chosen by priority for grouping/labels
      "angle": 180,                 // target angle for this aspect type
      "orb": 1.2,                   // |separation - angle|  (°)
      "separation": 178.8,          // actual separation (0..180°)
      "score": 3.64,                // additive score (see below)
      "strength": 0.88,             // score normalized to 0..1 for this pair
      "hardness_weight": 1.8,       // per type: conj=2.0, opp=1.8, sq=1.6, trine=1.2
      "emotional_bonus": 0.2,       // +0.2 if Sun/Moon/Mars involved
      "angularity_boost": 0.2       // +0.2 if either planet within ±5° of AC/DC/IC/MC (if provided)
    }
  ]
}
```

#### Score Computation (Additive)

The scoring system uses the following formula:

- **orb_score** = `1 - (orb / max_orb)` (clamped 0..1; tighter = larger)
- **hardness_weight** = `2.0` (conj), `1.8` (opp), `1.6` (square), `1.2` (trine)
- **emotional_bonus** = `+0.2` if Sun or Moon or Mars is in the pair
- **angularity_boost** = `+0.2` if either planet is within ±5° of AC/DC/IC/MC (only if you sent composite_angles)
- **score** = `hardness_weight + orb_score + emotional_bonus + angularity_boost`
- **strength** = `score / (hardness_weight + 1.0 + emotional_bonus + angularity_boost)` → 0..1

#### Sorting Order

- **Hardness order**: Conjunction > Opposition > Square > (Angle/Stellium) > Trine
- *Note*: At the raw `/aspects` level we don't form clusters yet, so sort is: type, tighter orb, then strength.

---

### `/top-aspects` Response (Clustered "Insights")

Request body is the same as `/aspects`. We detect aspects, then group and rank them.

```json
{
  "count": 5,
  "items": [
    {
      "aspect_label": "Moon opposition Mars/Pluto/Venus",
      "type": "opposition",            // cluster's primary aspect type
      "anchor": "Moon",                // anchor planet for the cluster
      "planets": ["Moon","Mars","Pluto","Venus"], // anchor + grouped members
      "group_id": "moon_opposition_group_1",
      "cluster_tag": "intensity_moon_group",
      "stellium": true,                // true if anchor + ≥2 members
      "bucket": "stellium_angle",      // one of: conjunction|opposition|square|stellium_angle|trine
      "orb_min": 0.9,                  // tightest orb among members
      "orb_avg": 1.3,                  // average orb across members
      "score_max": 3.92,               // highest member score (no group bonus)
      "score_merged": 3.78,            // avg(member scores) + group_bonus
      "weights": {
        "hardness_weight": 1.8,        // from cluster's primary type
        "emotional_bonus": 0.2,        // +0.2 if Sun/Moon/Mars appears in the cluster
        "angularity_boost": 0.2,       // +0.2 if any member is within ±5° of AC/DC/IC/MC
        "group_bonus": 0.2             // applied because it's a grouped insight
      }
    }
  ]
}
```

#### Clustering Logic ("Stellium" Logic)

1. **Initial Scoring**: We first score each pair (as described above)
2. **Grouping**: We group hits that share the same anchor and same aspect type, and whose separations are within ±3° of a cluster band center
   - *Example*: Mars opp Moon, Venus opp Moon, Pluto opp Moon → one cluster anchored on Moon
3. **Group Bonus**: +0.2 added to the cluster's merged score if there's at least 1 member (anchor + ≥1)
4. **Stellium**: `true` if there are ≥2 members (anchor + at least 2 others)

#### Cluster Metrics

| Metric | Description |
|--------|-------------|
| `orb_min` / `orb_avg` | Min and average of member orbs inside the cluster |
| `score_max` | The best (highest) single-member score in that cluster |
| `score_merged` | `mean(member_scores) + group_bonus` (what we rank on primarily) |

#### Bucket Classification (for UI ordering)

- `"conjunction"`, `"opposition"`, `"square"` as-is
- `"stellium_angle"` if the cluster is a stellium or any member is angle-related
- `"trine"` otherwise

**Display/sort priority**: Conjunction > Opposition > Square > Stellium/Angle > Trine

#### Labels & Tags

| Field | Description |
|-------|-------------|
| `aspect_label` | Human-friendly "Anchor TYPE Member1/Member2/..." |
| `group_id` | Deterministic identifier like "moon_opposition_group_1" |
| `cluster_tag` | Themed tag by type (e.g., fusion_, intensity_, friction_, ease_, angle_) + anchor |

---

### `/top-aspects/composite` Response

Exactly like `/top-aspects`, plus the source geometry:

```json
{
  "count": 5,
  "items": [ /* same cluster objects as above */ ],
  "composite": {
    "Sun": 105.55, "Moon": 123.10, ...
  },
  "composite_angles": {
    "AC": 15.2, "DC": 195.2, "MC": 280.9, "IC": 100.9
  },
  "meta": { "src": "Swiss Ephemeris", "version": "0.1.0" }
}
```

#### Use Cases

| Field | Purpose |
|-------|---------|
| `composite` | For debugging or UI (e.g., show wheel markers) |
| `composite_angles` | Enables angularity_boost and the Angle/Stellium bucket |
