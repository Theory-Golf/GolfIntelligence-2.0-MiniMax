# Scoring Performance Tab - Implementation Plan

## Overview
Create a new tab "Scoring Performance" that provides comprehensive analysis of scoring issues by categorizing performance problems into three distinct sections based on root cause analysis.

## Architecture

### 1. New Engine: `engines/scoring_performance.py`

```python
class ScoringPerformanceEngine:
    """
    Engine for analyzing scoring performance and root causes.
    
    Calculates:
    - Root cause categories for scoring issues
    - Section analysis (Double Bogey+, Bogey, Underperformance)
    - Hero cards data
    - Trend analysis
    - Penalty and severe shot metrics
    """
```

#### Key Methods

| Method | Description |
|--------|-------------|
| `classify_shot_category(shot)` | Classify shot into 7 root cause categories |
| `identify_root_cause(hole_shots)` | Find lowest SG shot to determine root cause |
| `analyze_double_bogey_plus(hole_df, shot_df)` | Section 1: Double Bogey+ analysis |
| `analyze_bogey(hole_df, shot_df)` | Section 2: Bogey analysis |
| `analyze_underperformance(hole_df, shot_df)` | Section 3: Underperformance analysis |
| `calculate_hero_cards(double_bogey, bogey, underperformance)` | Aggregate root cause counts |
| `calculate_trend_analysis(double_bogey, bogey, underperformance)` | Dual-axis trend chart data |
| `calculate_penalty_metrics(double_bogey, bogey, shot_df)` | Penalty and severe shot metrics |
| `get_root_cause_detail(double_bogey, bogey, underperformance)` | Shot-level detail data |

### 2. Root Cause Categories

| Category | Definition | Icon |
|----------|-----------|------|
| **Short Putts** | Shots from 6 feet and in | ⛳ |
| **Mid Range** | Shots from 7-15 feet | 📏 |
| **Lag Putts** | Shots from 16 feet and further | 🎯 |
| **Driving** | Shot type = "Drive" | 🚗 |
| **Approach** | Shot type = "Approach" | 🎯 |
| **Short Game** | Shot type = "Short Game" | 🏌️ |
| **Recovery/Other** | Shot type = "Recovery" or "Other" | 🔧 |

### 3. New Page: `pages/6_Scoring_Performance.py`

#### Section Structure

```markdown
## Scoring Performance

### Overview Cards
┌─────────────────────────────────────────────┐
│  Total Fails: XX                           │
│  ├── Double Bogey+: XX                      │
│  ├── Bogey: XX                             │
│  └── Underperformance: XX                   │
└─────────────────────────────────────────────┘

### Hero Cards (7 cards in grid)
┌─────────┬─────────┬─────────┬─────────┐
│ Short   │ Mid     │ Lag     │ Driving │
│ Putts   │ Range   │ Putts   │         │
│   XX    │   XX    │   XX    │   XX    │
│ -X.XX   │ -X.XX   │ -X.XX   │ -X.XX   │
│   SG    │   SG    │   SG    │   SG    │
├─────────┼─────────┼─────────┼─────────┤
│Approach │Short    │Recovery │         │
│         │ Game    │/Other   │         │
│   XX    │   XX    │   XX    │         │
│ -X.XX   │ -X.XX   │ -X.XX   │         │
│   SG    │   SG    │   SG    │         │
└─────────┴─────────┴─────────┴─────────┘

### Root Cause Trend Analysis (Collapsible)
[▼] Root Cause Trend Analysis
┌────────────────────────────────────────────┐
│  Dual-Axis Chart:                          │
│  Y1: Stacked Bar (Root Causes by Round)    │
│  Y2: Line (Total Fails per Round)          │
└────────────────────────────────────────────┘

### Penalty & Severe Shot Analysis
┌───────────────┬───────────────┬───────────────┐
│ Bogey w/      │ Double+ w/    │ Double Bogey  │
│ Penalty       │ Penalty       │ 2+ Severe     │
│   XX%         │   XX%         │   XX%         │
└───────────────┴───────────────┴───────────────┘

### Section 1: Double Bogey+ Root Cause
### Section 2: Bogey Root Cause  
### Section 3: Underperformance Root Cause

### Root Cause Detail (Collapsible)
[▼] Root Cause Detail Data
┌────────────────────────────────────────────┐
│  Filterable/Sortable DataTable             │
│  (Mirror Tiger 5 Details section)          │
└────────────────────────────────────────────┘
```

### 4. Implementation Details

#### Engine Functions

##### `classify_shot_category(shot: dict) -> str`
```python
def classify_shot_category(self, shot: pd.Series) -> str:
    """Classify shot into root cause category based on distance and type."""
    distance = shot.get('starting_distance', 0)
    shot_type = shot.get('shot_category', '').lower()
    
    # Putting categories by distance
    if shot_type == 'putting':
        if distance <= 6:
            return 'Short Putts'
        elif distance <= 15:
            return 'Mid Range'
        else:
            return 'Lag Putts'
    
    # Shot type categories
    if 'drive' in shot_type:
        return 'Driving'
    elif 'approach' in shot_type:
        return 'Approach'
    elif 'short game' in shot_type:
        return 'Short Game'
    else:
        return 'Recovery/Other'
```

##### `identify_root_cause(hole_shots: pd.DataFrame) -> dict`
```python
def identify_root_cause(self, hole_shots: pd.DataFrame) -> dict:
    """Identify root cause by finding shot with lowest SG."""
    if len(hole_shots) == 0:
        return None
    
    lowest_shot = hole_shots.loc[hole_shots['strokes_gained'].idxmin()]
    
    return {
        'hole': lowest_shot['hole'],
        'round_id': lowest_shot['round_id'],
        'shot_number': lowest_shot['shot'],
        'shot_type': lowest_shot['shot_category'],
        'distance': lowest_shot['starting_distance'],
        'sg_value': lowest_shot['strokes_gained'],
        'root_cause': self.classify_shot_category(lowest_shot)
    }
```

##### Section Analysis Functions

Each section follows the same pattern:
1. Filter holes by score condition
2. For each hole, find the root cause shot
3. Aggregate counts by root cause category
4. Return structured data

```python
def analyze_double_bogey_plus(self, hole_df: pd.DataFrame, shot_df: pd.DataFrame) -> dict:
    """Analyze holes where score >= +2 over par."""
    # Filter holes
    double_bogey_holes = hole_df[hole_df['score_vs_par'] >= 2]
    
    # Find root cause for each hole
    root_causes = []
    for _, hole in double_bogey_holes.iterrows():
        hole_shots = shot_df[
            (shot_df['round_id'] == hole['round_id']) & 
            (shot_df['hole'] == hole['hole'])
        ]
        root_cause = self.identify_root_cause(hole_shots)
        if root_cause:
            root_cause['hole_score'] = hole['hole_score']
            root_cause['score_vs_par'] = hole['score_vs_par']
            root_causes.append(root_cause)
    
    # Aggregate by category
    category_counts = {}
    category_sg = {}
    for rc in root_causes:
        cat = rc['root_cause']
        category_counts[cat] = category_counts.get(cat, 0) + 1
        category_sg[cat] = category_sg.get(cat, 0) + rc['sg_value']
    
    return {
        'total_holes': len(double_bogey_holes),
        'root_causes': root_causes,
        'category_counts': category_counts,
        'category_sg': category_sg
    }
```

### 5. Chart Implementation

#### Dual-Axis Trend Chart

```python
def calculate_trend_analysis(self, double_bogey: dict, bogey: dict, underperformance: dict) -> dict:
    """Create data for dual-axis trend chart."""
    rounds = sorted(set([
        *self._get_rounds(double_bogey),
        *self._get_rounds(bogey),
        *self._get_rounds(underperformance)
    ]))
    
    trend_data = []
    for round_id in rounds:
        round_entry = {'round': round_id}
        
        # Get counts by category for this round
        for category in ['Short Putts', 'Mid Range', 'Lag Putts', 
                        'Driving', 'Approach', 'Short Game', 'Recovery/Other']:
            round_entry[category] = self._get_round_count(
                round_id, category, double_bogey, bogey, underperformance
            )
        
        # Total fails for secondary axis
        round_entry['total_fails'] = sum([
            self._get_round_total(round_id, double_bogey),
            self._get_round_total(round_id, bogey),
            self._get_round_total(round_id, underperformance)
        ])
        
        trend_data.append(round_entry)
    
    return {'data': trend_data, 'categories': ['Short Putts', 'Mid Range', 'Lag Putts', 
                                                'Driving', 'Approach', 'Short Game', 'Recovery/Other']}
```

### 6. CSS Updates

Add hero card styles to `app.py`:

```css
.hero-card {
    background-color: #FFFFFF;
    border-radius: 16px;
    padding: 24px 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    text-align: center;
    border: 2px solid #EEEEEE;
    transition: all 0.3s ease;
}

.hero-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.hero-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #2C3E50;
}

.hero-label {
    font-size: 0.9rem;
    color: #404040;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.hero-sg {
    font-size: 1rem;
    font-weight: 600;
    margin-top: 0.5rem;
}

.hero-sg.negative {
    color: #E74C3C;
}
```

## File Changes Summary

| File | Change |
|------|--------|
| `engines/scoring_performance.py` | **NEW** - Scoring performance engine |
| `pages/6_Scoring_Performance.py` | **NEW** - Scoring performance page |
| `app.py` | **MODIFIED** - Add tab, imports, render function |
| `config/tiger5_definitions.yaml` | **OPTIONAL** - Add category definitions |

## Data Flow

```
sample_data.csv
    ↓
DataIngestion.load_csv()
    ↓
DataFrame with columns:
  - round_id, hole, shot, score
  - starting_distance, starting_location
  - strokes_gained, shot_category
    ↓
ScoringPerformanceEngine.calculate_*()
    ↓
Page rendering functions
    ↓
Streamlit UI Components
```

## Dependencies

- `pandas` - Data manipulation
- `plotly` - Charts (dual-axis)
- `streamlit` - UI components
- Existing `Tiger5Engine` for hole metrics

## Next Steps

1. Create `engines/scoring_performance.py` with all engine methods
2. Create `pages/6_Scoring_Performance.py` with UI components
3. Update `app.py` to register the new tab
4. Test with sample data
