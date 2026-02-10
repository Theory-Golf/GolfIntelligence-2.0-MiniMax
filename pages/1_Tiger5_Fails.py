"""
Tiger 5 Fails Overview Page
Analysis of blowup hole prevention

Usage: Streamlit will automatically discover this page when placed in pages/ directory
"""

import streamlit as st
import pandas as pd
import plotly.express as px


def render_tiger5_overview(df: pd.DataFrame, engines: dict, tiger5_config: dict):
    """Render Tiger 5 Overview page."""
    st.header("🏆 Tiger 5 Overview")
    st.markdown("Analysis of blowup hole prevention")
    
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
    
    # Fail scenarios table
    st.subheader("📋 Fail Scenarios")
    scenarios = tiger5_engine.get_tiger5_scenarios(hole_metrics)
    
    if len(scenarios) > 0:
        st.dataframe(
            scenarios,
            column_config={
                'round_id': 'Round',
                'hole': 'Hole',
                'score': 'Score',
                'score_vs_par': 'vs Par',
                'fails': 'Tiger 5 Fails'
            }
        )


# For standalone page execution
if __name__ == "__main__":
    st.info("This page should be run from app.py")
