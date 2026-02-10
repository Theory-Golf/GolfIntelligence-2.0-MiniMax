# Golf Intelligence Dashboard 2.0

A premium golf analytics dashboard with Strokes Gained, Tiger 5 analysis, and AI-powered coaching insights.

## Features

- **Tiger 5 Analysis**: Track and prevent blowup holes with 5 key fail categories
- **Strokes Gained**: Comprehensive SG calculations with 3 benchmark support
- **Game Pillars**: Detailed analysis for Driving, Approach, Short Game, and Putting
- **Small Sample Analytics**: Bootstrap confidence intervals for tournament and season analysis
- **Coach Magic Engine**: AI-powered strengths/weaknesses identification and recommendations

## Quick Start

### 1. Install Dependencies

```bash
pip install streamlit pandas plotly numpy pyyaml
```

### 2. Run the Dashboard

```bash
cd /Users/adam/Documents/GitHub/GolfIntelligence-2.0-MiniMax
streamlit run app.py
```

### 3. Access the Dashboard

Open your browser to `http://localhost:8501`

## Project Structure

```
GolfIntelligence-2.0-MiniMax/
├── app.py                    # Main Streamlit application
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── PLAN.md                   # Detailed project plan
├── config/
│   ├── project_config.json   # Project configuration
│   ├── field_mapping.yaml    # Data field mappings
│   └── tiger5_definitions.yaml # Tiger 5 category definitions
├── core/
│   ├── data_ingestion.py     # Data loading and preprocessing
│   ├── field_mapper.py       # Field mapping utilities
│   ├── benchmark_engine.py   # SG benchmark calculations
│   ├── metric_engine.py      # Core metric calculations
│   ├── small_sample_analytics.py # Bootstrap CI analysis
│   ├── caching_layer.py      # Performance caching
│   └── helpers.py            # Utility functions
├── engines/
│   ├── strokes_gained.py     # SG calculations
│   ├── tiger5.py            # Tiger 5 analysis
│   ├── driving.py           # Driving pillar
│   ├── approach.py          # Approach pillar
│   ├── short_game.py        # Short game pillar
│   ├── putting.py           # Putting pillar
│   └── coach_corner.py      # Mental metrics & coaching
└── data/
    ├── sample_data.csv       # Sample shot-level data
    └── benchmarks/           # SG benchmark lookup tables
        ├── benchmark_a_pga_tour.csv
        ├── benchmark_b_college.csv
        └── benchmark_c_scratch.csv
```

## Data Format

### Shot-Level Data

The dashboard expects CSV data with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| Player | Player name | Adam |
| Round ID | Unique round identifier | R1769787317558 |
| Date | Round date | 2026-01-30 |
| Course | Course name | Gaston |
| Tournament | Tournament/event name | Practice |
| Shot | Shot number | 1, 2, 3... |
| Hole | Hole number | 1-18 |
| Score | Cumulative score on hole | 1, 2, 3... |
| Starting Distance | Distance before shot | 500 |
| Starting Location | Where shot started | Tee, Fairway, Rough, Green |
| Ending Distance | Distance after shot | 230 |
| Ending Location | Where shot ended | Fairway, Green, Rough |
| Penalty | Penalty stroke? | Yes, No |
| Strokes Gained | Pre-computed SG value | 0.12 |

### Sample Data

Sample data is included in [`data/sample_data.csv`](data/sample_data.csv). Upload this file or use the built-in sample data option.

## Benchmark Files

Benchmark files are CSV lookup tables with:
- **Rows**: Distance values (0-600 yards in 5-yard increments)
- **Columns**: Lie types (Tee, Fairway, Rough, Sand, Recovery, Green)
- **Values**: Expected strokes to hole out

### Available Benchmarks

| Key | Name | Description |
|-----|------|-------------|
| a | PGA Tour | Professional tour-level expectations |
| b | College (+3) | Division I collegiate expectations |
| c | Scratch Golfer | Low amateur expectations |

### Adding Custom Benchmarks

1. Create a CSV file in [`data/benchmarks/`](data/benchmarks/)
2. Add to [`config/project_config.json`](config/project_config.json):
```json
{
  "benchmarks": {
    "d": {
      "filename": "benchmark_d_custom.csv",
      "display_name": "Custom Benchmark"
    }
  }
}
```

## Tiger 5 Categories

The 5 fail categories tracked:

1. **3 Putts**: Holes with 3+ putts
2. **Double Bogey+**: Scores of par+2 or worse
3. **Par 5 Bogey**: Par 5 holes scored 6 or worse
4. **Missed Green**: Short game shots not ending on green
5. **125yd Bogey**: Scoring approaches resulting in bogey+

### Grit Score

`((total_attempts - total_fails) / total_attempts) * 100`

- **Excellent**: ≥85%
- **Good**: 75-85%
- **Needs Work**: 65-75%
- **Critical**: <65%

## Small Sample Analytics

### Confidence Labels

| Rounds | Sample Size | Confidence |
|--------|-------------|------------|
| <3 | Tournament | Very Low |
| 3-9 | Tournament | Low |
| 10-20 | Season | Medium |
| 20+ | Season | High |

### Bootstrap Confidence Intervals

The dashboard uses bootstrap resampling to calculate confidence intervals for all metrics. Narrower intervals indicate more reliable estimates.

## Mental Metrics

- **Bounce Back Rate**: Par or better after bogey+
- **Gas Pedal Rate**: Birdie+ after birdie+
- **Bogey Train Rate**: Consecutive bogey+ holes

## Configuration

### Field Mapping

Edit [`config/field_mapping.yaml`](config/field_mapping.yaml) to map your column names to the standard format:

```yaml
shot_level:
  player: "Your Player Column"
  round_id: "Your Round ID Column"
  # ... etc
```

### Tiger 5 Definitions

Edit [`config/tiger5_definitions.yaml`](config/tiger5_definitions.yaml) to customize:
- Category conditions
- Root causes
- Metrics tracked

## Troubleshooting

### Missing Dependencies

```bash
pip install -r requirements.txt
```

### Benchmark Not Loading

Ensure benchmark files exist in [`data/benchmarks/`](data/benchmarks/) and are referenced in [`config/project_config.json`](config/project_config.json).

### Data Not Loading

Check that your CSV has all required columns and dates are in YYYY-MM-DD format.

## Support

For questions or issues, check the project repository.

## License

Private project - All rights reserved.
