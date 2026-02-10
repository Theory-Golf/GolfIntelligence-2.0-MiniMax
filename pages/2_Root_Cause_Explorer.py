"""
Tiger 5 Root Cause Explorer Page
Diagnose the causes of blowup holes

Usage: Streamlit will automatically discover this page when placed in pages/ directory
"""

import streamlit as st
import pandas as pd
import plotly.express as px


def render_tiger5_root_cause(df: pd.DataFrame, engines: dict, tiger5_config: dict):
    """Render Tiger 5 Root Cause Explorer page."""
    st.header("🔍 Tiger 5 Root Cause Explorer")
    st.markdown("Diagnose the causes of blowup holes")
    
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
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Fairway Miss Rate on Fail Holes",
            f"{driving.get('fairway_miss_rate', 0)*100:.1f}%",
            delta=None
        )
    
    with col2:
        st.metric(
            "Penalty Rate on Fail Holes",
            f"{driving.get('penalty_rate', 0)*100:.1f}%",
            delta=None
        )
    
    st.write(driving.get('evidence', ''))
    
    # Putting analysis
    st.markdown("### 🏌️ Putting")
    putting = causes.get('putting', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "3-Putt Rate on Fail Holes",
            f"{putting.get('three_putt_rate', 0)*100:.1f}%",
            delta=None
        )
    
    with col2:
        st.metric(
            "Evidence",
            putting.get('evidence', 'No data'),
            delta=None
        )
    
    # Additional analysis
    st.markdown("### 📊 Additional Insights")
    
    # Fairway vs Rough breakdown
    fail_holes = hole_metrics[hole_metrics['score_vs_par'] >= 2]['hole'].unique()
    fail_shots = df[df['hole'].isin(fail_holes)]
    
    # Shot location breakdown on fail holes
    if len(fail_shots) > 0:
        location_counts = fail_shots.groupby('starting_location').size()
        location_sg = fail_shots.groupby('starting_location')['strokes_gained'].mean()
        
        loc_df = pd.DataFrame({
            'Location': location_counts.index,
            'Count': location_counts.values,
            'Avg SG': location_sg.values
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(loc_df, x='Location', y='Count', title="Shot Locations on Fail Holes")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(loc_df, x='Location', y='Avg SG', title="Avg SG by Location on Fail Holes")
            st.plotly_chart(fig, use_container_width=True)
    
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
                'score_vs_par': 'vs Par',
                'fails': 'Tiger 5 Fails'
            }
        )
    
    # Recommendations
    st.subheader("💡 Recommendations")
    
    # Generate recommendations based on root causes
    recommendations = []
    
    if driving.get('fairway_miss_rate', 0) > 0.3:
        recommendations.append({
            'area': 'Driving',
            'action': 'Improve driving accuracy to reduce Tiger 5 fails',
            'priority': 'HIGH'
        })
    
    if driving.get('penalty_rate', 0) > 0.1:
        recommendations.append({
            'area': 'Driving',
            'action': 'Reduce penalties and OB strokes',
            'priority': 'HIGH'
        })
    
    if putting.get('three_putt_rate', 0) > 0.15:
        recommendations.append({
            'area': 'Putting',
            'action': 'Focus on 3-putt avoidance and lag putting',
            'priority': 'HIGH'
        })
    
    for rec in recommendations:
        st.markdown(f"""
        **{rec['priority']} Priority - {rec['area']}**
        - {rec['action']}
        """)


# For standalone page execution
if __name__ == "__main__":
    st.info("This page should be run from app.py")
