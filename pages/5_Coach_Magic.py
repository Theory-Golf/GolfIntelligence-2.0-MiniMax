"""
Coach Magic Page
AI-powered coaching insights and recommendations

Usage: Streamlit will automatically discover this page when placed in pages/ directory
"""

import streamlit as st
import pandas as pd


def render_coach_magic(df: pd.DataFrame, engines: dict):
    """Render Coach Magic page."""
    st.header("🧠 Coach Magic Engine")
    st.markdown("AI-powered coaching insights and recommendations")
    
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
    
    # Streak analysis
    streak = coach_engine.calculate_streakiness(df)
    
    with col2:
        st.markdown("#### 📈 Streakiness")
        st.write(f"Best streak: {streak['best_streak']} birdies+")
        st.write(f"Longest bogey streak: {streak['worst_streak']} bogeys+")
    
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
    
    # Key performance indicators summary
    st.divider()
    st.subheader("📊 KPI Summary")
    
    kpi_data = []
    
    for pillar_name, pillar_metrics in pillars.items():
        if 'message' not in pillar_metrics:
            kpi_data.append({
                'Pillar': pillar_name.title(),
                'SG Total': pillar_metrics.get('sg_total', 0),
                'Key Metric': list(pillar_metrics.keys())[1] if len(pillar_metrics) > 1 else 'N/A',
                'Key Value': list(pillar_metrics.values())[1] if len(pillar_metrics) > 1 else 'N/A'
            })
    
    if kpi_data:
        kpi_df = pd.DataFrame(kpi_data)
        st.dataframe(kpi_df)


# For standalone page execution
if __name__ == "__main__":
    st.info("This page should be run from app.py")
