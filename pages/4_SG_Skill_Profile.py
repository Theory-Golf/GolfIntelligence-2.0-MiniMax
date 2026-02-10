"""
SG Skill Profile Page
Strokes Gained skill breakdown

Usage: Streamlit will automatically discover this page when placed in pages/ directory
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render_sg_skill_profile(df: pd.DataFrame, engines: dict):
    """Render SG Skill Profile page."""
    st.header("📊 SG Skill Profile")
    st.markdown("Strokes Gained skill breakdown")
    
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
    
    # Radar chart for skill profile
    st.subheader("🎯 Skill Profile")
    
    # Prepare data for radar chart
    categories_radar = ['Driving', 'Approach', 'Short Game', 'Putting']
    values_radar = [
        sg_by_category.get('driving', 0),
        sg_by_category.get('approach', 0),
        sg_by_category.get('short_game', 0),
        sg_by_category.get('putting', 0)
    ]
    
    # Normalize values for radar chart
    max_val = max(abs(v) for v in values_radar) if max(abs(v) for v in values_radar) > 0 else 1
    normalized_values = [v / max_val * 100 for v in values_radar]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=normalized_values,
        theta=categories_radar,
        fill='toself',
        name='SG Performance'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[-100, 100]
            )),
        showlegend=True,
        title="Skill Profile Radar"
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
    
    # SG by distance buckets
    st.subheader("📊 SG by Distance")
    
    distance_buckets = ['<100', '100-150', '150-200', '200-250', '250-300', '300+']
    sg_by_distance = {}
    
    for bucket in distance_buckets:
        mask = df['distance_bucket'] == bucket
        sg_by_distance[bucket] = df.loc[mask, 'strokes_gained'].sum()
    
    dist_df = pd.DataFrame([
        {'Distance': k, 'SG': v} for k, v in sg_by_distance.items()
    ])
    
    if len(dist_df) > 0:
        fig = px.bar(dist_df, x='Distance', y='SG', color='SG',
                     color_continuous_scale='RdYlGn')
        fig.update_layout(
            title="SG by Distance Bucket",
            xaxis_title="Distance",
            yaxis_title="Strokes Gained"
        )
        st.plotly_chart(fig, use_container_width=True)


# For standalone page execution
if __name__ == "__main__":
    st.info("This page should be run from app.py")
