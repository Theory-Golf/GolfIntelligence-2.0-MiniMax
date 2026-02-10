# Golf Intelligence Dashboard 2.0 - Build Plan

## Executive Summary

A premium, interactive golf analytics dashboard built with Streamlit that provides Strokes Gained analysis, Tiger 5 decomposition, and AI-powered coaching insights. Optimized for small sample sizes (3-20 rounds) with robust uncertainty quantification.

## Project Architecture

```
GolfIntelligence-2.0/
├── app.py                          # Main Streamlit application entry point
├── requirements.txt                # Dependencies
├── README.md                       # Documentation
├── config/
│   ├── project_config.json        # Project configuration (accessible in code mode)
│   ├── field_mapping.yaml         # Field mapping configuration
│   └── tiger5_definitions.yaml     # Tiger 5 category definitions
├── core/
│   ├── __init__.py
│   ├── data_ingestion.py           # Data loading from Google Sheets/CSV
│   ├── field_mapper.py             # Config-driven field mapping
│   ├── metric_engine.py            # Core metrics calculations
│   ├── benchmark_engine.py         # SG benchmark switching logic
│   ├── small_sample_analytics.py   # Uncertainty, confidence intervals
│   ├── caching_layer.py            # DuckDB/Parquet caching
│   └── helpers.py                  # Utility functions
├── engines/
│   ├── __init__.py
│   ├── strokes_gained.py           # SG calculations
│   ├── hole_summary.py             # Hole-level aggregations
│   ├── tiger5.py                   # Tiger 5 analysis
│   ├── driving.py                  # Driving metrics
│   ├── approach.py                 # Approach metrics
│   ├── short_game.py               # Short game metrics
│   ├── putting.py                 # Putting metrics
│   ├── overview.py                 # Overview/SG summary
│   ├── coach_corner.py             # Mental metrics, strengths/weaknesses
│   └── comparison.py              # Comparison engine
├── pages/
│   ├── 1_Tiger5_Fails.py          # Tiger 5 overview
│   ├── 2_Root_Cause_Explorer.py   # Tiger 5 root cause analysis
│   ├── 3_Game_Pillars.py           # Driving/Approach/Short Game/Putting
│   ├── 4_SG_Skill_Profile.py       # SG skill card
│   └── 5_Coach_Magic.py            # Strengths/weaknesses, drivers
├── data/
│   ├── benchmarks/                 # Expected strokes lookup tables
│   │   ├── pga_tour.csv
│   │   ├── elite_college.csv
│   │   └── competitive_scratch.csv
│   └── sample_data.csv             # Sample data extract
└── tests/
    ├── __init__.py
    ├── test_metric_engine.py
    └── test_tiger5_engine.py
```

## Data Model

### Primary Data Schema (Shot-Level)

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| Player | string | Player name/identifier | Yes |
| Round ID | string | Unique round identifier | Yes |
| Date | date | Round date | Yes |
| Course | string | Course name | Yes |
| Weather Difficulty | enum | Weather conditions | No |
| Course Difficulty | enum | Course setup difficulty | No |
| Tournament | string | Tournament name | No |
| Benchmark | string | SG benchmark used for pre-computed SG | No |
| Shot | int | Shot number on hole | Yes |
| Hole | int | Hole number (1-18) | Yes |
| Score | int | Cumulative score through shot | Yes |
| Starting Distance | float | Distance before shot (yards/feet) | Yes |
| Starting Location | enum | Tee, Fairway, Rough, Sand, Recovery, Green | Yes |
| Ending Distance | float | Distance after shot | Yes |
| Ending Location | enum | Same as Starting Location | Yes |
| Penalty | enum | Yes/No | Yes |
| Starting SG | float | Expected strokes remaining at start | No (pre-computed) |
| Ending SG | float | Expected strokes remaining at end | No (pre-computed) |
| Strokes Gained | float | SG value for this shot | No (calculated if not provided) |

**Note:** If `Starting SG`, `Ending SG`, or `Strokes Gained` are provided in the data, they will be used as-is (convenient for quick input). If not provided, or if a different benchmark is selected, these values will be calculated from the selected benchmark lookup tables.

### Computed Fields

| Field | Calculation | Engine |
|-------|-------------|--------|
| Hole Score | `max(Score)` per hole | Hole Summary |
| Hole SG | `sum(Strokes Gained)` per hole | Hole Summary |
| Par | Lookup by (Course, Hole) | Data Ingestion |
| Shot Category | Classification logic | Shot Categorization |
| Tiger 5 Fail | Category-specific logic | Tiger 5 Engine |
| Grit Score | Formula from Tiger 5 Engine | Tiger 5 Engine |

## Page Layout & Flow

### Page 1: Tiger 5 Fails Overview

**KPI Tiles:**
- Grit Score (overall)
- Tiger 5 Fail Rate (%)
- Count by category
- Trend across rounds

**Visuals:**
- Round-by-round bar chart of fails
- Category breakdown donut chart
- Hole map showing Tiger 5 locations
- Trend line with confidence bands

**Data Table:**
- Filterable table of all Tiger 5 fails
- Sortable by round, hole, category
- Expandable details per fail

### Page 2: Tiger 5 Root Cause Explorer

**Analysis Methods:**
- Conditional breakdown tables (fairway vs rough, distance buckets)
- Simple correlation analysis
- Delta analysis (best vs worst rounds)
- Bootstrap confidence intervals

**Output:**
- Ranked root causes with evidence
- Example holes/rounds for each cause
- n counts and uncertainty indicators

### Page 3: Game Pillars (Driving, Approach, Short Game, Putting)

**For Each Pillar:**
- Hero metrics (key KPIs)
- Tournament vs Season comparison
- Distance bucket splits
- Lie splits (where applicable)
- Trend charts (3 rounds)
- Consistency metrics (IQR, dispersion)
- Small multiple charts
- Player profile card

### Page 4: SG Skill Profile

**Player Card:**
- SG Total + components (Driving, Approach, Short Game, Putting)
- Current form vs baseline
- Consistency badges
- Signature strength + primary leak

**Visuals:**
- Radar chart for skill profile
- Trend lines with confidence bands
- Distribution charts

### Page 5: Coach Magic Engine

**Strengths & Weaknesses:**
- Delta vs baseline calculation
- Ranked list with confidence labels
- Evidence from multiple rounds/holes

**Performance Drivers:**
- Best vs worst round comparison
- Correlation analysis
- Impact categorization (High/Moderate/Low)
- Bootstrap stability indicators

**Magic Output UX:**
- One-screen summary
- Top 2 actionable recommendations
- Measurable targets with ranges
- Evidence drawer with expandable details

## Small Sample Analytics Strategy

### Uncertainty Quantification

```python
# Bootstrap confidence intervals
def bootstrap_ci(data, metric, n_samples=100, confidence=0.95):
    """Calculate bootstrap confidence interval for a metric."""
    # Implementation using resampling with replacement
    # Returns (lower_bound, upper_bound, stability_score)

# Stability indicator
def stability_score(n, ci_width, threshold=0.5):
    """Categorize stability based on sample size and CI width."""
    if n >= threshold_n and ci_width < tight_threshold:
        return "HIGH"
    elif n >= moderate_n or ci_width < moderate_threshold:
        return "MEDIUM"
    else:
        return "LOW"
```

### Consistency Metrics

| Metric | Calculation | Use Case |
|--------|-------------|----------|
| IQR | Q3 - Q1 | Dispersion, outlier-robust |
| Std Dev | Standard deviation | Overall dispersion |
| Range | Max - Min | Total spread |
| CV | Std Dev / Mean | Relative variability |
| Truncated Mean | Mean excluding extremes | Less sensitive to outliers |
| Median | Middle value | Central tendency, robust |

### Comparison Framework

```python
# Tournament vs Season
tournament_metrics = calculate_metrics(recent_3_rounds)
season_metrics = calculate_metrics(all_rounds)
delta = tournament_metrics - season_metrics

# Confidence labeling
def confidence_label(n, effect_size):
    if n >= 15 and abs(effect_size) >= 0.5:
        return "HIGH"
    elif n >= 10 or abs(effect_size) >= 0.3:
        return "MEDIUM"
    else:
        return "LOW"
```

## Benchmark Engine

### Supported Benchmarks

1. **Pre-computed SG** (default) - Use SG values already in the data (convenient for quick input)
2. **Scratch Golfer** - Competitive amateur baseline
3. **PGA Tour** - Professional baseline
4. **Elite College (+3)** - High-level amateur
5. **Custom Benchmark** - User-uploaded lookup tables

### Benchmark Switching Logic

```python
def compute_shot_sg(shot, benchmark, use_precomputed=True):
    """
    Compute SG for a single shot.
    
    Args:
        shot: Shot data with Starting/Ending Distance and Location
        benchmark: Benchmark to use ('precomputed', 'scratch', 'pga_tour', 'college', 'custom')
        use_precomputed: If True and SG exists in data, use it; otherwise calculate
    
    Returns:
        strokes_gained: SG value for the shot
    """
    # Option 1: Use pre-computed SG (user-friendly input)
    if use_precomputed and shot.get('Strokes Gained') is not None:
        return shot['Strokes Gained']
    
    # Option 2: Calculate from benchmark lookup tables
    lookup_table = load_benchmark(benchmark)
    
    expected_start = lookup_table.lookup(
        shot['Starting Location'],
        bucket_distance(shot['Starting Distance'])
    )
    expected_end = lookup_table.lookup(
        shot['Ending Location'],
        bucket_distance(shot['Ending Distance'])
    )
    
    penalty_factor = 2 if shot.get('Penalty') == 'Yes' else 1
    strokes_gained = expected_start - expected_end - penalty_factor
    
    return strokes_gained
```

## Caching Strategy

### DuckDB + Parquet

```python
# Cache computed metrics by filter state
@st.cache_data(ttl=3600)  # 1 hour cache
def compute_tournament_metrics(filters):
    """Compute tournament metrics with caching."""
    # Load filtered data from Parquet
    # Compute all metrics
    # Return structured results

# Persistent cache for benchmark lookups
@st.cache_resource
def load_benchmark_cache():
    """Load all benchmarks into memory cache."""
    return DuckDBConnection("cache/benchmarks.duckdb")
```

## Three-Benchmark Support

### Overview
The dashboard supports selecting between THREE benchmarks (A, B, C) that you provide. Users choose which benchmark to use for SG calculations via a dropdown selector.

### Benchmark Files to Provide

Place these CSV files in `data/benchmarks/`:

| File | Your Benchmark Name |
|------|---------------------|
| `benchmark_a.csv` | Configure in `config/project_config.json` (e.g., "Scratch Golfer") |
| `benchmark_b.csv` | Configure in `config/project_config.json` (e.g., "PGA Tour") |
| `benchmark_c.csv` | Configure in `config/project_config.json` (e.g., "Elite College") |

### Benchmark CSV Format

```csv
Location,Distance_Bucket,Expected_Strokes
Tee,200-250,3.2
Tee,250-300,2.9
Tee,300+,2.7
Fairway,50-100,2.1
Fairway,100-150,2.4
Rough,50-100,2.3
Rough,100-150,2.8
Sand,20-30,2.6
Green,0-3,0.95
```

### Configuration

In `config/project_config.json`:
```json
{
  "benchmarks": {
    "a": {
      "filename": "benchmark_a.csv",
      "display_name": "Scratch Golfer",
      "description": "Competitive amateur baseline"
    },
    "b": {
      "filename": "benchmark_b.csv",
      "display_name": "PGA Tour",
      "description": "Professional baseline"
    },
    "c": {
      "filename": "benchmark_c.csv",
      "display_name": "Elite College",
      "description": "High-level amateur baseline"
    }
  }
}
```

### UI Components

```python
# In sidebar - benchmark selector
benchmark_options = [
    config['benchmarks']['a']['display_name'],
    config['benchmarks']['b']['display_name'],
    config['benchmarks']['c']['display_name']
]
selected_benchmark_key = st.selectbox(
    'SG Benchmark',
    options=['a', 'b', 'c'],
    format_func=lambda x: config['benchmarks'][x]['display_name']
)

# Show benchmark info
st.info(f"📊 Using: {config['benchmarks'][selected_benchmark_key]['description']}")
```

### Benchmark Engine

```python
class BenchmarkEngine:
    def __init__(self, config):
        self.benchmarks = {}
        for key, cfg in config['benchmarks'].items():
            filepath = f"data/benchmarks/{cfg['filename']}"
            self.benchmarks[key] = self._load_benchmark_csv(filepath)
    
    def lookup(self, benchmark_key, location, distance_bucket):
        """Look up expected strokes for a given state."""
        return self.benchmarks[benchmark_key].get(
            (location, distance_bucket), 
            2.0  # default fallback
        )
    
    def compute_sg(self, benchmark_key, shot):
        """Compute SG for a shot using selected benchmark."""
        start_bucket = bucket_distance(shot['Starting Distance'])
        end_bucket = bucket_distance(shot['Ending Distance'])
        
        expected_start = self.lookup(benchmark_key, shot['Starting Location'], start_bucket)
        expected_end = self.lookup(benchmark_key, shot['Ending Location'], end_bucket)
        
        penalty_factor = 2 if shot.get('Penalty') == 'Yes' else 1
        return expected_start - expected_end - penalty_factor
```

### Overview
The dashboard supports user-uploaded custom benchmarks for calculating Strokes Gained. Users can upload their own expected strokes lookup tables in CSV format.

### Custom Benchmark CSV Format

| Column | Type | Description |
|--------|------|-------------|
| Location | string | Tee, Fairway, Rough, Sand, Recovery, Green |
| Distance_Bucket | string | e.g., "50-100", "100-150", "150-200", "200+" |
| Expected_Strokes | float | Expected strokes to hole out from this state |

### Upload Flow

```python
def handle_custom_benchmark_upload(uploaded_file):
    """
    Handle custom benchmark CSV upload from Streamlit file uploader.
    
    Returns:
        benchmark_data: DataFrame with custom benchmark values
        validation_results: Dict with validation status and errors
    """
    # Read CSV
    benchmark_data = pd.read_csv(uploaded_file)
    
    # Validate required columns
    required_cols = ['Location', 'Distance_Bucket', 'Expected_Strokes']
    missing_cols = [c for c in required_cols if c not in benchmark_data.columns]
    
    if missing_cols:
        return None, {'valid': False, 'errors': f"Missing columns: {missing_cols}"}
    
    # Validate data integrity
    valid_locations = ['Tee', 'Fairway', 'Rough', 'Sand', 'Recovery', 'Green']
    invalid_locations = benchmark_data[~benchmark_data['Location'].isin(valid_locations)]
    
    if len(invalid_locations) > 0:
        return None, {'valid': False, 'errors': f"Invalid locations: {invalid_locations['Location'].unique()}"}
    
    # Validate numeric values
    if not pd.api.types.is_numeric_dtype(benchmark_data['Expected_Strokes']):
        return None, {'valid': False, 'errors': "Expected_Strokes must be numeric"}
    
    # Validate ranges
    if (benchmark_data['Expected_Strokes'] < 0).any():
        return None, {'valid': False, 'errors': "Expected_Strokes cannot be negative"}
    
    # Create lookup dictionary
    lookup_dict = {}
    for _, row in benchmark_data.iterrows():
        key = (row['Location'], row['Distance_Bucket'])
        lookup_dict[key] = row['Expected_Strokes']
    
    return lookup_dict, {'valid': True, 'errors': None}
```

### UI Components for Custom Benchmarks

```python
def custom_benchmark_uploader():
    """Streamlit component for custom benchmark upload."""
    with st.expander("Upload Custom Benchmark"):
        uploaded_file = st.file_uploader(
            "Upload expected strokes CSV",
            type=['csv'],
            help="CSV must have columns: Location, Distance_Bucket, Expected_Strokes"
        )
        
        if uploaded_file:
            lookup_dict, validation = handle_custom_benchmark_upload(uploaded_file)
            
            if validation['valid']:
                st.success("✅ Custom benchmark uploaded successfully!")
                return lookup_dict
            else:
                st.error(f"❌ Validation failed: {validation['errors']}")
                return None
        
        return None
```

### Usage in Dashboard

```python
# In sidebar - benchmark selector
benchmark_options = [
    'Pre-computed SG',
    'Scratch Golfer',
    'PGA Tour',
    'Elite College (+3)',
    'Custom Upload'
]
selected_benchmark = st.selectbox('SG Benchmark', benchmark_options)

# Handle custom upload if selected
if selected_benchmark == 'Custom Upload':
    custom_lookup = custom_benchmark_uploader()
    if custom_lookup is None:
        st.warning("Using Scratch Golfer benchmark instead")
        selected_benchmark = 'Scratch Golfer'
```

## Metric Catalog Integration

### Metrics with Tags

Each metric includes:
- `name`: Unique identifier
- `formula`: Calculation formula
- `description`: What it measures
- `tags`: [category, pillar, skill_level]
- `dependencies`: Other metrics required
- `sample_size_requirement`: Minimum n for reliable results

### Example Entry

```yaml
fairway_percentage:
  name: "Fairway Percentage"
  formula: "(fairway_ends + green_ends) / total_drives * 100"
  description: "Percentage of drives ending in play"
  tags: [driving, tee_game, foundational]
  dependencies: []
  sample_size_requirement: 10
```

## Tiger 5 Categories

### Category Definitions

| Category | Definition | Attempts | Fails |
|----------|-----------|----------|-------|
| 3 Putts | Any hole with ≥3 putts | Holes with ≥1 putt | Holes with ≥3 putts |
| Double Bogey | Score ≥ par + 2 | All holes | Score ≥ par + 2 |
| Par 5 Bogey | Par 5 holes with score ≥ 6 | Par 5 holes only | Score ≥ 6 on Par 5 |
| Missed Green | Short game shot not ending on green | Holes with short game shot | Any short game shot not on green |
| 125yd Bogey | Scoring shot inside 125yd resulting in bogey+ | Shot on par 3 hole (Shot 1), par 4 (Shot 2), par 5 (Shot 3) from ≤125yd | Hole score > par |

### Root Cause Mapping

| Tiger 5 Category | Likely Root Causes |
|------------------|---------------------|
| 3 Putts | Putting (lag distance control, green reading) |
| Double Bogey | Driving (penalty/OB), Approach (missed GIR), Short Game |
| Par 5 Bogey | Driving (position), Approach (GIR), Putting |
| Missed Green | Short Game (technique, distance control) |
| 125yd Bogey | Approach (proximity, green detection) |

## UI/UX Design System

### Color Palette

| Purpose | Primary | Secondary | Accent |
|---------|---------|-----------|--------|
| KPIs | #1E3A5F | #2E86AB | #48A9A6 |
| Positive | #4CAF50 | #81C784 | #A5D6A7 |
| Negative | #F44336 | #E57373 | #EF9A9A |
| Neutral | #607D8B | #90A4AE | #B0BEC5 |
| Background (Dark) | #0D1B2A | | |
| Background (Light) | #F8F9FA | | |

### Component Library

1. **KPI Cards** - Big numbers with trend indicators
2. **Trend Charts** - Line charts with confidence bands
3. **Distribution Plots** - Box plots, violin plots
4. **Comparison Tables** - Side-by-side metric comparisons
5. **Evidence Expanders** - Collapsible detail sections
6. **Confidence Badges** - HIGH/MEDIUM/LOW indicators

### Layout Structure

```
[Sidebar]
├── Player Filter
├── Course Filter
├── Tournament Filter
├── Date Range
├── Benchmark Selector
└── View Toggle (Tournament/Season)

[Main Content]
├── Page Tabs
│   ├── Tiger 5 Overview
│   ├── Root Cause Explorer
│   ├── Game Pillars
│   ├── SG Skill Profile
│   └── Coach Magic
└── [Page-Specific Content]
```

## Implementation Priorities

### Phase 1: Core Foundation
- [ ] Data ingestion and field mapping
- [ ] Basic metric calculations
- [ ] Tiger 5 analysis
- [ ] Overview page with KPIs

### Phase 2: Game Pillars
- [ ] Driving metrics
- [ ] Approach metrics
- [ ] Short game metrics
- [ ] Putting metrics
- [ ] All pillar pages

### Phase 3: Advanced Analytics
- [ ] SG skill profile page
- [ ] Coach magic engine
- [ ] Root cause explorer
- [ ] Small sample analytics

### Phase 4: Polish & Performance
- [ ] Caching layer
- [ ] Premium UI components
- [ ] Benchmark switching
- [ ] Performance optimization

## Testing Strategy

### Unit Tests
- Metric calculations (known inputs → known outputs)
- Tiger 5 categorization
- Field mapping
- Distance bucketing

### Integration Tests
- End-to-end pipeline (raw data → dashboard)
- Benchmark switching
- Filter combinations

### Sample Size Tests
- 3-round tournament view
- 10-round season view
- Edge cases (single round, no data)

## Setup Checklist for User

1. **Copy project files** to local directory
2. **Configure field mapping** in `config/field_mapping.yaml`
3. **Add benchmark CSVs** to `data/benchmarks/`
4. **Update sample data** in `data/sample_data.csv`
5. **Install dependencies** (`pip install -r requirements.txt`)
6. **Run app** (`streamlit run app.py`)
7. **Connect to Google Sheets** using provided credentials

## Next Steps

1. **Switch to Code mode** to implement all modules
2. **Create core engine modules** (metric engine, SG engine, Tiger 5 engine)
3. **Build Streamlit pages** with premium UI components
4. **Test with provided sample data**
5. **Deliver complete runnable project**

---

**Plan Version:** 1.0  
**Created:** February 2025  
**Status:** Ready for Implementation
