"""
Game Pillars Page
Detailed analysis by skill area (Driving, Approach, Short Game, Putting)

Usage: Streamlit will automatically discover this page when placed in pages/ directory
"""

import streamlit as st
import pandas as pd
import plotly.express as px


def render_game_pillars(df: pd.DataFrame, engines: dict):
    """Render Game Pillars page."""
    st.header("🎯 Game Pillars")
    st.markdown("Detailed analysis by skill area")
    
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
    
    # Additional metrics
    st.subheader("📈 Additional Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Drives", analysis['total_drives'])
    
    with col2:
        st.metric("Fairway Hits", analysis['fairway_hits'])
    
    with col3:
        st.metric("SG/Drives", f"{analysis['sg_per_drive']:.3f}")


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
        st.write(f"**From Fairway**: {fairway.get('count', 0)} shots")
        st.write(f"SG: {fairway.get('sg_total', 0):.2f}")
        st.write(f"GIR: {fairway.get('gir_rate', 0):.1f}%")
    
    with col2:
        rough = fairway_rough.get('rough', {})
        st.write(f"**From Rough**: {rough.get('count', 0)} shots")
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


# For standalone page execution
if __name__ == "__main__":
    st.info("This page should be run from app.py")
