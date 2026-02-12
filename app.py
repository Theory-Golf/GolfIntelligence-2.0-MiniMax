"""
Golf Intelligence Dashboard 2.0
Main Streamlit Application

A premium golf analytics dashboard with Strokes Gained, Tiger 5 analysis,
and AI-powered coaching insights.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.data_ingestion import DataIngestion
from core.field_mapper import FieldMapper
from core.benchmark_engine import BenchmarkEngine
from core.metric_engine import MetricEngine
from core.small_sample_analytics import SmallSampleAnalytics
from core.helpers import Helpers
from core.caching_layer import CachingLayer

# Page configuration
st.set_page_config(
    page_title="Golf Intelligence",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Nordic Theme CSS
st.markdown("""
<style>
    /* Nordic Theme - Clean, Minimal, Premium */
    
    /* Main background */
    .stApp {
        background-color: #FAFAFA;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #F5F5F5;
        border-right: 1px solid #E0E0E0;
    }
    
    /* Typography */
    h1, h2, h3, h4 {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 600;
        color: #2C3E50;
        letter-spacing: -0.5px;
    }
    
    h1 {
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        font-size: 1.6rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #E8E8E8;
        padding-bottom: 0.5rem;
    }
    
    h3 {
        font-size: 1.2rem;
        color: #34495E;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
    }
    
    /* Metric cards - Nordic style */
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 24px 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 4px 12px rgba(0, 0, 0, 0.03);
        text-align: center;
        border: 1px solid #EEEEEE;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2C3E50;
        line-height: 1.2;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #404040;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    /* Confidence badges */
    .confidence-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .confidence-high {
        background-color: #E8F5E9;
        color: #2E7D32;
    }
    
    .confidence-medium {
        background-color: #FFF3E0;
        color: #E65100;
    }
    
    .confidence-low {
        background-color: #FFEBEE;
        color: #C62828;
    }
    
    /* Streamlit metric styling */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 16px 20px;
        border: 1px solid #EEEEEE;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.8rem;
        color: #4a4a4a;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: 600;
        color: #2C3E50;
    }
    
    /* Tabs - Nordic style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 500;
        color: #404040;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF;
        border-bottom: 3px solid #3498DB;
        color: #2C3E50;
    }
    
    /* Cards and containers */
    .stMarkdown > div {
        background-color: transparent;
    }
    
    /* Divider */
    hr {
        border: none;
        border-top: 1px solid #E8E8E8;
        margin: 1.5rem 0;
    }
    
    /* Info and warning boxes */
    .stAlert {
        border-radius: 8px;
        padding: 12px 16px;
    }
    
    /* Dataframes */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #E8E8E8;
    }
    
    /* Select boxes and inputs */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
    }
    
    /* Expander */
    .stExpander {
        background-color: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #E8E8E8;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #3498DB;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 500;
        padding: 10px 24px;
    }
    
    .stButton > button:hover {
        background-color: #2980B9;
    }
    
    /* Progress bars */
    .stProgress > div > div {
        background-color: #3498DB;
        border-radius: 4px;
    }
    
    /* Tables */
    table {
        border-collapse: collapse;
        width: 100%;
    }
    
    th {
        background-color: #F8F9FA;
        font-weight: 600;
        color: #2C3E50;
        text-align: left;
        padding: 12px 16px;
        border-bottom: 2px solid #E8E8E8;
    }
    
    td {
        padding: 12px 16px;
        border-bottom: 1px solid #EEEEEE;
        color: #1a1a1a;
    }
    
    /* Subtle color accents */
    .positive {
        color: #27AE60;
    }
    
    .negative {
        color: #E74C3C;
    }
    
    .neutral {
        color: #404040;
    }
    
    /* Hero cards */
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
        line-height: 1.2;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .hero-label {
        font-size: 0.85rem;
        color: #404040;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    .hero-sg {
        font-size: 1rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .hero-sg.negative {
        color: #E74C3C;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {
        visibility: hidden;
    }
    
    footer {
        visibility: hidden;
    }
    
    header {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# Load configuration
@st.cache_resource
def load_config():
    """Load project configuration."""
    config_path = Path("config/project_config.json")
    if config_path.exists():
        import json
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

@st.cache_resource
def load_field_mapping():
    """Load field mapping configuration."""
    mapper = FieldMapper("config/field_mapping.yaml")
    return mapper

@st.cache_resource
def load_tiger5_config():
    """Load Tiger 5 category definitions."""
    import yaml
    tiger5_path = Path("config/tiger5_definitions.yaml")
    if tiger5_path.exists():
        with open(tiger5_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


# Initialize engines
@st.cache_resource
def initialize_engines(config):
    """Initialize all analytics engines."""
    field_mapper = FieldMapper("config/field_mapping.yaml")
    benchmark_engine = BenchmarkEngine(config)
    metric_engine = MetricEngine(field_mapper)
    small_sample = SmallSampleAnalytics()
    cache = CachingLayer()
    
    # Import pillar engines
    from engines.driving import DrivingEngine
    from engines.approach import ApproachEngine
    from engines.short_game import ShortGameEngine
    from engines.putting import PuttingEngine
    from engines.tiger5 import Tiger5Engine
    from engines.coach_corner import CoachCornerEngine
    from engines.strokes_gained import StrokesGainedEngine
    from engines.scoring_performance import ScoringPerformanceEngine
    
    driving = DrivingEngine()
    approach = ApproachEngine()
    short_game = ShortGameEngine()
    putting = PuttingEngine()
    tiger5 = Tiger5Engine()
    coach = CoachCornerEngine()
    strokes_gained = StrokesGainedEngine()
    scoring = ScoringPerformanceEngine()
    
    return {
        'field_mapper': field_mapper,
        'benchmark_engine': benchmark_engine,
        'metric_engine': metric_engine,
        'small_sample': small_sample,
        'helpers': Helpers(),
        'cache': cache,
        'driving': driving,
        'approach': approach,
        'short_game': short_game,
        'putting': putting,
        'tiger5': tiger5,
        'coach': coach,
        'strokes_gained': strokes_gained,
        'scoring': scoring
    }


def main():
    """Main application entry point."""
    config = load_config()
    tiger5_config = load_tiger5_config()
    engines = initialize_engines(config)
    
    # Sidebar - Filters
    st.sidebar.markdown('<h3 style="margin-bottom: 1rem;">Filters</h3>', unsafe_allow_html=True)
    
    # Data loading
    data_source = st.sidebar.selectbox(
        "Data Source",
        ["Sample Data", "Upload CSV", "Google Sheets"]
    )
    
    df = load_data(data_source)
    
    if df is None or len(df) == 0:
        st.warning("No data loaded. Please upload a CSV file.")
        return
    
    # Prepare data
    df = prepare_data(df, engines['field_mapper'])
    
    # Filters
    filters = create_filters(df)
    filtered_df = apply_filters(df, filters)
    
    # View selection
    view_type = st.sidebar.radio(
        "View",
        ["Tournament (Last 3 Rounds)", "Season (Last 20 Rounds)", "All Data"]
    )
    
    filtered_df = apply_view_filter(filtered_df, view_type)
    
    # Benchmark selector
    benchmark_options = engines['benchmark_engine'].get_available_benchmarks()
    selected_benchmark = st.sidebar.selectbox(
        "SG Benchmark",
        options=list(benchmark_options.keys()),
        format_func=lambda x: benchmark_options.get(x, x)
    )
    
    # Small sample warning
    n_rounds = filtered_df['round_id'].nunique()
    if n_rounds < 10:
        st.sidebar.warning(f"⚠️ Small sample: {n_rounds} rounds (confidence limited)")
    
    # Main content - Clean header
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="margin-bottom: 0.25rem;">⛳ Golf Intelligence</h1>
        <p style="color: #404040; font-size: 1rem; margin: 0;">Analytics & insights for better golf</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Overview KPIs
    render_overview_kpis(filtered_df, engines['metric_engine'])
    
    # Page tabs - Clean Nordic style
    tabs = st.tabs([
        "Tiger 5",
        "Root Cause",
        "Game Pillars",
        "SG Profile",
        "Coach Magic",
        "Scoring Performance"
    ])
    
    with tabs[0]:
        render_tiger5_overview(filtered_df, engines, tiger5_config)
    
    with tabs[1]:
        render_tiger5_root_cause(filtered_df, engines, tiger5_config)
    
    with tabs[2]:
        render_game_pillars(filtered_df, engines)
    
    with tabs[3]:
        render_sg_skill_profile(filtered_df, engines)
    
    with tabs[4]:
        render_coach_magic(filtered_df, engines)
    
    with tabs[5]:
        render_scoring_performance(filtered_df, engines)


def load_data(source: str) -> pd.DataFrame:
    """Load data based on source selection."""
    ingestion = DataIngestion()
    
    if source == "Sample Data":
        return ingestion.load_sample_data()
    elif source == "Upload CSV":
        uploaded = st.sidebar.file_uploader("Upload CSV", type=['csv'])
        if uploaded:
            return ingestion.load_csv(uploaded)
    elif source == "Google Sheets":
        # Default sheet ID for user's golf data
        default_sheet_id = "1cLMC4HxovHnvnke24vBXMBRXz6-kvw-x6s9-RbVjS4c"
        
        sheet_id = st.sidebar.text_input(
            "Google Sheet ID",
            value=default_sheet_id,
            help="Enter the Google Sheets spreadsheet ID"
        )
        
        sheet_name = st.sidebar.text_input("Sheet Name (optional)", value="")
        
        if sheet_id:
            with st.spinner("Loading data from Google Sheets..."):
                try:
                    if sheet_name:
                        df = ingestion.load_google_sheet(sheet_id, sheet_name)
                    else:
                        df = ingestion.load_google_sheet(sheet_id)
                    st.success("✅ Data loaded successfully!")
                    return df
                except Exception as e:
                    st.error(f"Error loading Google Sheet: {e}")
    
    return ingestion.load_sample_data()


def prepare_data(df: pd.DataFrame, field_mapper) -> pd.DataFrame:
    """Prepare data with calculated fields."""
    df = df.copy()
    
    # Add distance buckets
    df = Helpers.add_distance_buckets(df)
    
    # Add shot categories
    df = Helpers.add_shot_categories(df)
    
    return df


def create_filters(df: pd.DataFrame) -> dict:
    """Create sidebar filters."""
    filters = {}
    
    # Player filter
    if 'player' in df.columns:
        players = ['All'] + sorted(df['player'].unique().tolist())
        filters['player'] = st.sidebar.selectbox("Player", players)
    
    # Course filter
    if 'course' in df.columns:
        courses = ['All'] + sorted(df['course'].unique().tolist())
        filters['course'] = st.sidebar.selectbox("Course", courses)
    
    # Tournament filter
    if 'tournament' in df.columns:
        tournaments = ['All'] + sorted(df['tournament'].unique().tolist())
        filters['tournament'] = st.sidebar.selectbox("Tournament", tournaments)
    
    # Date range
    if 'date' in df.columns:
        min_date = pd.to_datetime(df['date']).min()
        max_date = pd.to_datetime(df['date']).max()
        
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(min_date, max_date)
        )
        filters['date_range'] = date_range
    
    return filters


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply filters to data."""
    filtered = df.copy()
    
    for key, value in filters.items():
        if key == 'date_range':
            continue
        if value == 'All':
            continue
        if key in filtered.columns:
            filtered = filtered[filtered[key] == value]
    
    # Date filter
    if 'date_range' in filters and len(filters['date_range']) == 2:
        start_date, end_date = filters['date_range']
        if 'date' in filtered.columns:
            dates = pd.to_datetime(filtered['date'])
            filtered = filtered[
                (dates >= pd.to_datetime(start_date)) & 
                (dates <= pd.to_datetime(end_date))
            ]
    
    return filtered


def apply_view_filter(df: pd.DataFrame, view: str) -> pd.DataFrame:
    """Apply view type filter."""
    if view == "Tournament (Last 3 Rounds)":
        return Helpers.get_recent_rounds(df, 3)
    elif view == "Season (Last 20 Rounds)":
        return Helpers.get_recent_rounds(df, 20)
    else:
        return df


def render_overview_kpis(df: pd.DataFrame, metric_engine):
    """Render overview KPI section."""
    if len(df) == 0:
        return
    
    metrics = metric_engine.calculate_all_metrics(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        scoring = metrics.get('scoring', {})
        st.metric(
            "Scoring Average",
            f"{scoring.get('scoring_average', 0):.1f}",
            delta=None
        )
    
    with col2:
        sg = metrics.get('sg_total', {})
        st.metric(
            "SG Total",
            f"{sg.get('total_sg', 0):.1f}",
            delta=f"{sg.get('sg_per_round', 0):.2f}/round"
        )
    
    with col3:
        holes = metrics.get('holes', pd.DataFrame())
        if len(holes) > 0:
            birdies = (holes['score_vs_par'] == -1).sum()
            st.metric("Birdies", birdies)
    
    with col4:
        rounds = df['round_id'].nunique()
        st.metric("Rounds", rounds)


def render_tiger5_overview(df: pd.DataFrame, engines: dict, tiger5_config: dict):
    """Render Tiger 5 Overview page."""
    st.markdown('<h2 style="border-bottom: 2px solid #E8E8E8; padding-bottom: 0.5rem;">Tiger 5 Analysis</h2>', unsafe_allow_html=True)
    st.markdown("<p style='color: #404040; margin-bottom: 1.5rem;'>Track and prevent blowup holes</p>")
    
    if len(df) == 0:
        st.warning("No data available for Tiger 5 analysis")
        return
    
    tiger5_engine = engines['tiger5']
    
    # Calculate hole-level metrics
    hole_metrics = tiger5_engine.calculate_hole_metrics(df)
    
    # Calculate Tiger 5 fails
    tiger5_results = tiger5_engine.calculate_tiger5_fails(hole_metrics)
    
    # Grit Score
    grit_score = tiger5_results['grit_score']
    interpretation = tiger5_engine.get_grit_interpretation(grit_score)
    
    # Grit Score Card
    st.subheader("🎯 Grit Score")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{grit_score:.1f}%</div>
            <div class="metric-label">Grit Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.info(f"**{interpretation['level']}**: {interpretation['message']}")
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{tiger5_results['total_fails']}</div>
            <div class="metric-label">Total Tiger 5 Fails</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Category breakdown
    st.subheader("📊 Tiger 5 Categories")
    
    categories = tiger5_config.get('categories', {})
    
    # Create category cards
    cat_cols = st.columns(5)
    
    for idx, (cat_key, cat_def) in enumerate(categories.items()):
        if idx >= 5:
            break
            
        with cat_cols[idx]:
            cat_name = cat_def.get('name', cat_key)
            icon = cat_def.get('icon', '⛳')
            cat_data = tiger5_results['categories'].get(cat_name, {})
            
            fail_rate = cat_data.get('fail_rate', 0)
            fails = cat_data.get('fails', 0)
            attempts = cat_data.get('attempts', 0)
            
            # Color based on fail rate
            if fail_rate < 5:
                color = "#4CAF50"
            elif fail_rate < 10:
                color = "#FF9800"
            else:
                color = "#F44336"
            
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid {color};">
                <div style="font-size: 1.5em;">{icon}</div>
                <div class="metric-value" style="font-size: 1.2em;">{fail_rate:.1f}%</div>
                <div class="metric-label">{cat_name}</div>
                <div style="font-size: 0.8em; color: #666;">{fails}/{attempts} attempts</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Tiger 5 Fail Trend
    st.subheader("📈 Tiger 5 Fail Trend")
    
    round_ids = df['round_id'].unique()
    if len(round_ids) > 1:
        trend = tiger5_engine.calculate_tiger5_trend(hole_metrics, round_ids)
        
        trend_df = pd.DataFrame([
            {'round': rid, 'fails': trend[rid]['total_fails'], 'grit': trend[rid]['grit_score']}
            for rid in round_ids
        ])
        
        if len(trend_df) > 0:
            fig = px.line(trend_df, x='round', y='fails', markers=True)
            fig.update_layout(
                title="Tiger 5 Fails per Round",
                xaxis_title="Round",
                yaxis_title="Number of Fails"
            )
            st.plotly_chart(fig, use_container_width=True)


def render_tiger5_root_cause(df: pd.DataFrame, engines: dict, tiger5_config: dict):
    """Render Tiger 5 Root Cause page."""
    st.markdown('<h2 style="border-bottom: 2px solid #E8E8E8; padding-bottom: 0.5rem;">Root Cause Analysis</h2>', unsafe_allow_html=True)
    st.markdown("<p style='color: #404040; margin-bottom: 1.5rem;'>Diagnose what causes your blowup holes</p>")
    
    if len(df) == 0:
        st.warning("No data available for root cause analysis")
        return
    
    tiger5_engine = engines['tiger5']
    
    # Get hole metrics
    hole_metrics = tiger5_engine.calculate_hole_metrics(df)
    
    # Calculate root causes
    causes = tiger5_engine.calculate_root_causes(hole_metrics, df)
    
    if isinstance(causes, dict) and 'message' in causes:
        st.info(causes['message'])
        return
    
    st.subheader("🎯 Root Cause Analysis")
    
    # Driving analysis
    st.markdown("### 🚗 Driving")
    driving = causes.get('driving', {})
    st.write(f"Fairway miss rate on fail holes: {driving.get('fairway_miss_rate', 0)*100:.1f}%")
    st.write(f"Penalty rate on fail holes: {driving.get('penalty_rate', 0)*100:.1f}%")
    
    # Putting analysis
    st.markdown("### 🏌️ Putting")
    putting = causes.get('putting', {})
    st.write(f"3-putt rate on fail holes: {putting.get('three_putt_rate', 0)*100:.1f}%")
    
    # Show fail scenarios
    st.subheader("📋 Fail Scenarios")
    scenarios = tiger5_engine.get_tiger5_scenarios(hole_metrics)
    
    if len(scenarios) > 0:
        st.dataframe(
            scenarios,
            column_config={
                'round_id': 'Round',
                'hole': 'Hole',
                'score': 'Score',
                'fails': 'Tiger 5 Fails'
            }
        )


def render_game_pillars(df: pd.DataFrame, engines: dict):
    """Render Game Pillars page."""
    st.markdown('<h2 style="border-bottom: 2px solid #E8E8E8; padding-bottom: 0.5rem;">Game Pillars</h2>', unsafe_allow_html=True)
    st.markdown("<p style='color: #404040; margin-bottom: 1.5rem;'>Detailed breakdown of each skill area</p>")
    
    if len(df) == 0:
        st.warning("No data available for pillar analysis")
        return
    
    # Create sub-tabs for each pillar
    pillar_tabs = st.tabs(["🚗 Driving", "🎯 Approach", "🏌️ Short Game", "⛳ Putting"])
    
    # Driving
    with pillar_tabs[0]:
        render_driving_pillar(df, engines['driving'])
    
    # Approach
    with pillar_tabs[1]:
        render_approach_pillar(df, engines['approach'])
    
    # Short Game
    with pillar_tabs[2]:
        render_short_game_pillar(df, engines['short_game'])
    
    # Putting
    with pillar_tabs[3]:
        render_putting_pillar(df, engines['putting'])


def render_driving_pillar(df: pd.DataFrame, driving_engine):
    """Render driving pillar analysis."""
    st.subheader("🚗 Driving Analysis")
    
    analysis = driving_engine.analyze_driving(df)
    
    if 'message' in analysis:
        st.info(analysis['message'])
        return
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Fairway Hit %", f"{analysis['fairway_percentage']:.1f}%")
    
    with col2:
        st.metric("SG Total", f"{analysis['sg_total']:.2f}")
    
    with col3:
        st.metric("OB/Re-tee Rate", f"{analysis['ob_rate']:.1f}%")
    
    with col4:
        st.metric("Penalty Rate", f"{analysis['penalty_rate']:.1f}%")
    
    # Distance analysis
    st.subheader("📊 Driving by Distance")
    sg_by_dist = driving_engine.analyze_driving_by_distance(df)
    
    if sg_by_dist:
        dist_df = pd.DataFrame([
            {'Distance': k, 'SG': v} for k, v in sg_by_dist.items()
        ])
        
        fig = px.bar(dist_df, x='Distance', y='SG', color='SG', 
                     color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)


def render_approach_pillar(df: pd.DataFrame, approach_engine):
    """Render approach pillar analysis."""
    st.subheader("🎯 Approach Analysis")
    
    analysis = approach_engine.analyze_approach(df)
    
    if 'message' in analysis:
        st.info(analysis['message'])
        return
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("GIR %", f"{analysis['gir_rate']:.1f}%")
    
    with col2:
        st.metric("SG Total", f"{analysis['sg_total']:.2f}")
    
    with col3:
        st.metric("Proximity (ft)", f"{analysis['proximity']:.1f}")
    
    with col4:
        st.metric("Approaches from Fairway", f"{analysis['approaches_from_fairway']}")
    
    # Distance breakdown
    st.subheader("📊 Approach by Distance")
    sg_by_bucket = analysis.get('sg_by_bucket', {})
    
    if sg_by_bucket:
        bucket_df = pd.DataFrame([
            {'Distance': k, 'SG': v} for k, v in sg_by_bucket.items()
        ])
        
        fig = px.bar(bucket_df, x='Distance', y='SG', color='SG',
                     color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    
    # Fairway vs Rough
    st.subheader("📊 Fairway vs Rough")
    fairway_rough = approach_engine.analyze_fairway_rough_split(df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fairway = fairway_rough.get('fairway', {})
        st.write(f"From Fairway: {fairway.get('count', 0)} shots")
        st.write(f"SG: {fairway.get('sg_total', 0):.2f}")
        st.write(f"GIR: {fairway.get('gir_rate', 0):.1f}%")
    
    with col2:
        rough = fairway_rough.get('rough', {})
        st.write(f"From Rough: {rough.get('count', 0)} shots")
        st.write(f"SG: {rough.get('sg_total', 0):.2f}")
        st.write(f"GIR: {rough.get('gir_rate', 0):.1f}%")


def render_short_game_pillar(df: pd.DataFrame, short_game_engine):
    """Render short game pillar analysis."""
    st.subheader("🏌️ Short Game Analysis")
    
    analysis = short_game_engine.analyze_short_game(df)
    
    if 'message' in analysis:
        st.info(analysis['message'])
        return
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Green Hit %", f"{analysis['green_hit_rate']:.1f}%")
    
    with col2:
        st.metric("SG Total", f"{analysis['sg_total']:.2f}")
    
    with col3:
        st.metric("Proximity (ft)", f"{analysis['proximity']:.1f}")
    
    with col4:
        st.metric("Total Shots", f"{analysis['total_shots']}")
    
    # Distance analysis
    st.subheader("📊 Short Game by Distance")
    sg_by_bucket = analysis.get('sg_by_bucket', {})
    
    if sg_by_bucket:
        bucket_df = pd.DataFrame([
            {'Distance': k, 'SG': v} for k, v in sg_by_bucket.items()
        ])
        
        fig = px.bar(bucket_df, x='Distance', y='SG', color='SG',
                     color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    
    # Lie analysis
    st.subheader("📊 Performance by Lie")
    sg_by_lie = analysis.get('sg_by_lie', {})
    
    lie_data = []
    for lie, metrics in sg_by_lie.items():
        lie_data.append({
            'Lie': lie,
            'Shots': metrics.get('shots', 0),
            'SG': metrics.get('sg_total', 0),
            'Green Rate %': metrics.get('green_rate', 0)
        })
    
    if lie_data:
        lie_df = pd.DataFrame(lie_data)
        st.dataframe(lie_df)


def render_putting_pillar(df: pd.DataFrame, putting_engine):
    """Render putting pillar analysis."""
    st.subheader("⛳ Putting Analysis")
    
    analysis = putting_engine.analyze_putting(df)
    
    if 'message' in analysis:
        st.info(analysis['message'])
        return
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Putts/Hole", f"{analysis['avg_putts_per_hole']:.2f}")
    
    with col2:
        st.metric("1-Putt %", f"{analysis['one_putt_rate']:.1f}%")
    
    with col3:
        st.metric("3-Putt %", f"{analysis['three_putt_rate']:.1f}%")
    
    with col4:
        st.metric("SG Total", f"{analysis['sg_total']:.2f}")
    
    # Distance analysis
    st.subheader("📊 Putting by Distance")
    sg_by_bucket = analysis.get('sg_by_bucket', {})
    
    if sg_by_bucket:
        bucket_df = pd.DataFrame([
            {'Distance': k, 'SG': v} for k, v in sg_by_bucket.items()
        ])
        
        fig = px.bar(bucket_df, x='Distance', y='SG', color='SG',
                     color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    
    # 3-putt prevention
    st.subheader("🛡️ 3-Putt Prevention")
    prevention = putting_engine.calculate_3_putt_prevention(df)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("3-Putts", f"{prevention['three_putts']}")
    
    with col2:
        st.metric("3-Putt Rate", f"{prevention['three_putt_rate']:.1f}%")
    
    with col3:
        st.metric("Prevented", f"{prevention['opportunities_prevented']}")


def render_sg_skill_profile(df: pd.DataFrame, engines: dict):
    """Render SG Skill Profile page."""
    st.markdown('<h2 style="border-bottom: 2px solid #E8E8E8; padding-bottom: 0.5rem;">SG Skill Profile</h2>', unsafe_allow_html=True)
    st.markdown("<p style='color: #404040; margin-bottom: 1.5rem;'>Strokes Gained breakdown by category</p>")
    
    if len(df) == 0:
        st.warning("No data available for SG analysis")
        return
    
    sg_engine = engines['strokes_gained']
    
    # Calculate SG by category
    sg_by_category = sg_engine.calculate_sg_by_shot_category(df)
    
    # Create breakdown
    st.subheader("📈 SG by Category")
    
    cat_data = []
    for cat, sg in sg_by_category.items():
        cat_data.append({
            'Category': cat.title(),
            'SG': sg
        })
    
    cat_df = pd.DataFrame(cat_data)
    
    if len(cat_df) > 0:
        fig = px.bar(cat_df, x='Category', y='SG', color='SG',
                     color_continuous_scale='RdYlGn')
        fig.update_layout(
            title="Strokes Gained by Category",
            yaxis_title="Strokes Gained"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # SG separators
    st.subheader("🏆 SG Separators")
    separators = sg_engine.calculate_sg_separators(df)
    
    sep_cols = st.columns(4)
    
    idx = 0
    for metric, value in separators.items():
        with sep_cols[idx % 4]:
            st.metric(metric.replace('_', ' ').title(), f"{value:.2f}")
        idx += 1
    
    # SG trend
    st.subheader("📈 SG Trend")
    trend = sg_engine.calculate_sg_trend(df)
    
    if 'labels' in trend and len(trend['labels']) > 0:
        trend_df = pd.DataFrame(trend)
        fig = px.line(trend_df, x='labels', y='values', markers=True)
        fig.update_layout(
            title="SG Over Time",
            xaxis_title="Date/Round",
            yaxis_title="Strokes Gained"
        )
        st.plotly_chart(fig, use_container_width=True)


def render_coach_magic(df: pd.DataFrame, engines: dict):
    """Render Coach Magic page."""
    st.markdown('<h2 style="border-bottom: 2px solid #E8E8E8; padding-bottom: 0.5rem;">Coach Magic</h2>', unsafe_allow_html=True)
    st.markdown("<p style='color: #404040; margin-bottom: 1.5rem;'>AI-powered insights and recommendations</p>")
    
    if len(df) == 0:
        st.warning("No data available for coaching analysis")
        return
    
    coach_engine = engines['coach']
    
    # Mental metrics
    st.subheader("🧠 Mental Metrics")
    
    # Bounce back rate
    bounce_back = coach_engine.calculate_bounce_back_rate(df)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ↩️ Bounce Back Rate")
        st.metric("Rate", f"{bounce_back['bounce_back_rate']:.1f}%")
        st.write(f"Opportunities: {bounce_back['opportunities']}")
        st.write(f"Successes: {bounce_back['successes']}")
    
    # Gas pedal rate
    gas_pedal = coach_engine.calculate_gas_pedal_rate(df)
    
    with col2:
        st.markdown("#### 🚀 Gas Pedal Rate")
        st.metric("Rate", f"{gas_pedal['gas_pedal_rate']:.1f}%")
        st.write(f"Opportunities: {gas_pedal['opportunities']}")
        st.write(f"Successes: {gas_pedal['successes']}")
    
    # Bogey train
    st.divider()
    bogey_train = coach_engine.calculate_bogey_train_rate(df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🚂 Bogey Train Rate")
        st.metric("Rate", f"{bogey_train['bogey_train_rate']:.1f}%")
        st.write(f"Bogey+ holes: {bogey_train['bogey_plus_holes']}")
        st.write(f"Trains (2+ consecutive): {bogey_train['trains']}")
    
    # Strengths and weaknesses
    st.divider()
    st.subheader("💪 Strengths & Weaknesses")
    
    # Calculate pillar metrics for comparison
    pillars = {
        'driving': engines['driving'].analyze_driving(df),
        'approach': engines['approach'].analyze_approach(df),
        'short_game': engines['short_game'].analyze_short_game(df),
        'putting': engines['putting'].analyze_putting(df)
    }
    
    # Create comparison (using baseline of 0 for simplicity)
    current_metrics = {
        'driving_sg': pillars['driving'].get('sg_total', 0),
        'approach_sg': pillars['approach'].get('sg_total', 0),
        'short_game_sg': pillars['short_game'].get('sg_total', 0),
        'putting_sg': pillars['putting'].get('sg_total', 0),
        'bounce_back': bounce_back['bounce_back_rate'],
        'gas_pedal': gas_pedal['gas_pedal_rate']
    }
    
    baseline_metrics = {k: 0 for k in current_metrics.keys()}
    
    ranked = coach_engine.rank_strengths_weaknesses(current_metrics, baseline_metrics)
    
    # Display strengths
    st.markdown("#### ✅ Top Strengths")
    strengths = ranked.get('strengths', [])
    if strengths:
        for i, strength in enumerate(strengths[:5], 1):
            confidence = strength.get('confidence', 'LOW').lower()
            st.markdown(f"""
            <span class="confidence-badge confidence-{confidence}">{confidence.upper()}</span>
            **{strength['metric']}**: +{strength['delta']:.2f}
            """, unsafe_allow_html=True)
    else:
        st.write("No significant strengths identified yet")
    
    # Display weaknesses
    st.markdown("#### ⚠️ Areas for Improvement")
    weaknesses = ranked.get('weaknesses', [])
    if weaknesses:
        for i, weakness in enumerate(weaknesses[:5], 1):
            confidence = weakness.get('confidence', 'LOW').lower()
            st.markdown(f"""
            <span class="confidence-badge confidence-{confidence}">{confidence.upper()}</span>
            **{weakness['metric']}**: {weakness['delta']:.2f}
            """, unsafe_allow_html=True)
    else:
        st.write("No significant weaknesses identified")
    
    # Recommendations
    st.divider()
    st.subheader("🎯 Action Plan")
    
    recommendations = coach_engine.generate_recommendations(ranked)
    
    if recommendations:
        for i, rec in enumerate(recommendations[:5], 1):
            st.markdown(f"""
            **{i}. {rec['type']} - {rec['area']}**
            - Action: {rec['action']}
            - Evidence: {rec['evidence']}
            - Confidence: <span class="confidence-badge confidence-{rec['confidence'].lower()}">{rec['confidence']}</span>
            """, unsafe_allow_html=True)
    else:
        st.write("Keep practicing to generate recommendations")


def render_scoring_performance(df: pd.DataFrame, engines: dict):
    """Render Scoring Performance page."""
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    
    st.markdown('<h2 style="border-bottom: 2px solid #E8E8E8; padding-bottom: 0.5rem;">📊 Scoring Performance</h2>', unsafe_allow_html=True)
    st.markdown("<p style='color: #404040; margin-bottom: 1.5rem;'>Comprehensive analysis of scoring issues by root cause</p>")
    
    if len(df) == 0:
        st.warning("No data available for scoring performance analysis")
        return
    
    scoring_engine = engines['scoring']
    
    # Calculate hole-level metrics
    hole_metrics = scoring_engine.calculate_hole_metrics(df)
    
    # Run all three analysis sections
    double_bogey = scoring_engine.analyze_double_bogey_plus(hole_metrics, df)
    bogey = scoring_engine.analyze_bogey(hole_metrics, df)
    underperformance = scoring_engine.analyze_underperformance(hole_metrics, df)
    
    # Calculate summary data
    summary = scoring_engine.calculate_scoring_summary(hole_metrics, double_bogey, bogey, underperformance)
    
    # Calculate hero cards
    hero_cards = scoring_engine.calculate_hero_cards(double_bogey, bogey, underperformance)
    
    # Calculate trend analysis
    trend_data = scoring_engine.calculate_trend_analysis(double_bogey, bogey, underperformance)
    
    # Calculate penalty metrics
    penalty_metrics = scoring_engine.calculate_penalty_metrics(double_bogey, bogey, df)
    
    # Get root cause detail
    root_cause_detail = scoring_engine.get_root_cause_detail(double_bogey, bogey, underperformance)
    
    # Hero card icons mapping
    HERO_ICONS = {
        'Short Putts': '⛳',
        'Mid Range': '📏',
        'Lag Putts': '🎯',
        'Driving': '🚗',
        'Approach': '🎯',
        'Short Game': '🏌️',
        'Recovery/Other': '🔧'
    }
    
    # Render overview section
    st.subheader("📋 Scoring Fail Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid #E74C3C;">
            <div class="metric-value">{summary.get('total_fails', 0)}</div>
            <div class="metric-label">Total Fails</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        db_count = double_bogey.get('total_holes', 0)
        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid #E74C3C;">
            <div class="metric-value">{db_count}</div>
            <div class="metric-label">Double Bogey+</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        b_count = bogey.get('total_holes', 0)
        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid #F39C12;">
            <div class="metric-value">{b_count}</div>
            <div class="metric-label">Bogey</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        up_count = underperformance.get('total_holes', 0)
        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid #3498DB;">
            <div class="metric-value">{up_count}</div>
            <div class="metric-label">Underperformance</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Render hero cards
    st.subheader("🎯 Root Cause Hero Cards")
    
    categories = list(hero_cards.keys())
    first_row = categories[:4]
    second_row = categories[4:]
    
    cols1 = st.columns(4)
    for idx, cat in enumerate(first_row):
        with cols1[idx]:
            data = hero_cards[cat]
            icon = HERO_ICONS.get(cat, '⛳')
            count = data.get('count', 0)
            total_sg = data.get('total_sg', 0)
            sg_color = '#E74C3C' if total_sg < 0 else '#27AE60'
            
            st.markdown(f"""
            <div class="hero-card" style="border-left: 4px solid {sg_color};">
                <div style="font-size: 1.8em; margin-bottom: 0.25rem;">{icon}</div>
                <div class="hero-value">{count}</div>
                <div class="hero-label">{cat}</div>
                <div class="hero-sg" style="color: {sg_color};">SG: {total_sg:+.2f}</div>
            </div>
            """, unsafe_allow_html=True)
    
    if second_row:
        cols2 = st.columns(4)
        for idx, cat in enumerate(second_row):
            with cols2[idx]:
                data = hero_cards[cat]
                icon = HERO_ICONS.get(cat, '⛳')
                count = data.get('count', 0)
                total_sg = data.get('total_sg', 0)
                sg_color = '#E74C3C' if total_sg < 0 else '#27AE60'
                
                st.markdown(f"""
                <div class="hero-card" style="border-left: 4px solid {sg_color};">
                    <div style="font-size: 1.8em; margin-bottom: 0.25rem;">{icon}</div>
                    <div class="hero-value">{count}</div>
                    <div class="hero-label">{cat}</div>
                    <div class="hero-sg" style="color: {sg_color};">SG: {total_sg:+.2f}</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()
    
    # Render trend analysis
    with st.expander("📈 Root Cause Trend Analysis", expanded=False):
        data = trend_data.get('data', [])
        categories_rc = trend_data.get('categories', [])
        
        if len(data) == 0:
            st.info("Not enough data to display trend analysis")
        else:
            trend_df = pd.DataFrame(data)
            
            fig = go.Figure()
            colors = px.colors.qualitative.Set2
            color_idx = 0
            
            for category in categories_rc:
                if category in trend_df.columns:
                    fig.add_trace(go.Bar(
                        x=trend_df['round'],
                        y=trend_df[category],
                        name=category,
                        marker_color=colors[color_idx % len(colors)]
                    ))
                    color_idx += 1
            
            fig.add_trace(go.Scatter(
                x=trend_df['round'],
                y=trend_df['total_fails'],
                name='Total Fails',
                mode='lines+markers',
                line=dict(color='#2C3E50', width=3),
                yaxis='y2'
            ))
            
            fig.update_layout(
                yaxis=dict(title='Root Cause Count', overlaying='y2', side='left'),
                yaxis2=dict(title='Total Fails', side='right'),
                xaxis_title='Round',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
                height=400,
                barmode='stack'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Render penalty metrics
    st.subheader("⚠️ Penalty & Severe Shot Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        bogey_pct = penalty_metrics.get('bogey_with_penalty_pct', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #F39C12;">{bogey_pct:.1f}%</div>
            <div class="metric-label">Bogey Holes w/ Penalty</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        double_pct = penalty_metrics.get('double_bogey_with_penalty_pct', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #E74C3C;">{double_pct:.1f}%</div>
            <div class="metric-label">Double Bogey+ w/ Penalty</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        severe_pct = penalty_metrics.get('double_bogey_multiple_severe_pct', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #E74C3C;">{severe_pct:.1f}%</div>
            <div class="metric-label">Double Bogey 2+ Severe Shots</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Render detail sections
    ROOT_CAUSE_CATEGORIES = ['Short Putts', 'Mid Range', 'Lag Putts', 
                            'Driving', 'Approach', 'Short Game', 'Recovery/Other']
    
    # Section 1: Double Bogey+
    st.markdown("#### 🔴 Section 1: Double Bogey+ Root Cause")
    total_db = double_bogey.get('total_holes', 0)
    if total_db > 0:
        db_counts = double_bogey.get('category_counts', {})
        db_sg = double_bogey.get('category_sg', {})
        
        breakdown_data = [{'Category': k, 'Count': db_counts.get(k, 0), 'Total SG': db_sg.get(k, 0)} 
                         for k in ROOT_CAUSE_CATEGORIES if db_counts.get(k, 0) > 0]
        if breakdown_data:
            bd_df = pd.DataFrame(breakdown_data)
            st.dataframe(bd_df, hide_index=True)
    else:
        st.info("No Double Bogey+ holes")
    
    st.divider()
    
    # Section 2: Bogey
    st.markdown("#### 🟡 Section 2: Bogey Root Cause")
    total_b = bogey.get('total_holes', 0)
    if total_b > 0:
        b_counts = bogey.get('category_counts', {})
        b_sg = bogey.get('category_sg', {})
        
        breakdown_data = [{'Category': k, 'Count': b_counts.get(k, 0), 'Total SG': b_sg.get(k, 0)} 
                         for k in ROOT_CAUSE_CATEGORIES if b_counts.get(k, 0) > 0]
        if breakdown_data:
            bd_df = pd.DataFrame(breakdown_data)
            st.dataframe(bd_df, hide_index=True)
    else:
        st.info("No Bogey holes")
    
    st.divider()
    
    # Section 3: Underperformance
    st.markdown("#### 🔵 Section 3: Underperformance Root Cause")
    total_up = underperformance.get('total_holes', 0)
    if total_up > 0:
        up_counts = underperformance.get('category_counts', {})
        up_sg = underperformance.get('category_sg', {})
        
        breakdown_data = [{'Category': k, 'Count': up_counts.get(k, 0), 'Total SG': up_sg.get(k, 0)} 
                         for k in ROOT_CAUSE_CATEGORIES if up_counts.get(k, 0) > 0]
        if breakdown_data:
            bd_df = pd.DataFrame(breakdown_data)
            st.dataframe(bd_df, hide_index=True)
    else:
        st.info("No Underperformance holes")
    
    st.divider()
    
    # Render root cause detail
    with st.expander("📋 Root Cause Detail Data", expanded=False):
        st.markdown("#### Shot-Level Detail by Root Cause Category")
        
        if len(root_cause_detail) == 0:
            st.info("No detail data available")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                selected_section = st.multiselect(
                    "Filter by Section",
                    options=['Double Bogey+', 'Bogey', 'Underperformance'],
                    default=['Double Bogey+', 'Bogey', 'Underperformance']
                )
            
            with col2:
                selected_category = st.multiselect(
                    "Filter by Root Cause",
                    options=ROOT_CAUSE_CATEGORIES,
                    default=ROOT_CAUSE_CATEGORIES
                )
            
            filtered_df = root_cause_detail.copy()
            
            if 'section' in filtered_df.columns and selected_section:
                filtered_df = filtered_df[filtered_df['section'].isin(selected_section)]
            
            if 'root_cause' in filtered_df.columns and selected_category:
                filtered_df = filtered_df[filtered_df['root_cause'].isin(selected_category)]
            
            st.markdown(f"Showing {len(filtered_df)} of {len(root_cause_detail)} records")
            
            display_cols = ['round_id', 'hole', 'section', 'shot_number', 'shot_type', 
                           'distance', 'sg_value', 'root_cause', 'penalty']
            available_cols = [c for c in display_cols if c in filtered_df.columns]
            
            if available_cols:
                st.dataframe(
                    filtered_df[available_cols],
                    hide_index=True,
                    column_config={
                        'sg_value': st.column_config.NumberColumn('SG', format='%.2f'),
                        'distance': st.column_config.NumberColumn('Dist (yd)', format='%.0f')
                    }
                )


if __name__ == "__main__":
    main()
