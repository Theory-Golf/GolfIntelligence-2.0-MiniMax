"""
Scoring Performance Page
Comprehensive analysis of scoring issues by categorizing performance problems
into three distinct sections based on root cause analysis.

Usage: Streamlit will automatically discover this page when placed in pages/ directory
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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


def render_scoring_performance(df: pd.DataFrame, engines: dict):
    """
    Render Scoring Performance page.
    
    Args:
        df: Shot-level DataFrame
        engines: Dictionary of analytics engines
    """
    st.header("📊 Scoring Performance")
    st.markdown("Comprehensive analysis of scoring issues by root cause")
    
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
    summary = scoring_engine.calculate_scoring_summary(
        hole_metrics, double_bogey, bogey, underperformance
    )
    
    # Calculate hero cards
    hero_cards = scoring_engine.calculate_hero_cards(double_bogey, bogey, underperformance)
    
    # Calculate trend analysis
    trend_data = scoring_engine.calculate_trend_analysis(double_bogey, bogey, underperformance)
    
    # Calculate penalty metrics
    penalty_metrics = scoring_engine.calculate_penalty_metrics(double_bogey, bogey, df)
    
    # Get root cause detail
    root_cause_detail = scoring_engine.get_root_cause_detail(double_bogey, bogey, underperformance)
    
    # Render sections
    render_overview_section(summary, double_bogey, bogey, underperformance)
    st.divider()
    render_hero_cards_section(hero_cards)
    st.divider()
    render_trend_analysis(trend_data)
    st.divider()
    render_penalty_metrics(penalty_metrics)
    st.divider()
    render_detail_sections(double_bogey, bogey, underperformance)
    st.divider()
    render_root_cause_detail_section(root_cause_detail)


def render_overview_section(summary: dict, double_bogey: dict, bogey: dict, underperformance: dict):
    """Render the overview section with fail counts."""
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
    
    # Score distribution mini-chart
    score_dist = pd.DataFrame({
        'Category': ['Eagle', 'Birdie', 'Par', 'Bogey', 'Double+'],
        'Count': [
            summary.get('eagles', 0),
            summary.get('birdies', 0),
            summary.get('pars', 0),
            summary.get('bogeys', 0),
            summary.get('doubles_or_worse', 0)
        ]
    })
    
    if score_dist['Count'].sum() > 0:
        fig = px.bar(
            score_dist, 
            x='Category', 
            y='Count',
            color='Category',
            color_discrete_map={
                'Eagle': '#27AE60',
                'Birdie': '#2ECC71',
                'Par': '#3498DB',
                'Bogey': '#F39C12',
                'Double+': '#E74C3C'
            }
        )
        fig.update_layout(
            title="Score Distribution",
            showlegend=False,
            height=200
        )
        st.plotly_chart(fig, use_container_width=True)


def render_hero_cards_section(hero_cards: dict):
    """Render the hero cards section showing aggregated root cause counts."""
    st.subheader("🎯 Root Cause Hero Cards")
    
    # Organize cards in a 4-3 grid
    categories = list(hero_cards.keys())
    first_row = categories[:4]
    second_row = categories[4:]
    
    # First row
    cols1 = st.columns(4)
    for idx, cat in enumerate(first_row):
        with cols1[idx]:
            render_hero_card(cat, hero_cards[cat])
    
    # Second row
    cols2 = st.columns(4) if len(second_row) >= 1 else st.columns(len(second_row))
    for idx, cat in enumerate(second_row):
        with cols2[idx]:
            render_hero_card(cat, hero_cards[cat])


def render_hero_card(category: str, data: dict):
    """Render a single hero card."""
    icon = HERO_ICONS.get(category, '⛳')
    count = data.get('count', 0)
    total_sg = data.get('total_sg', 0)
    
    # Color based on SG value
    if total_sg < -1:
        sg_color = '#E74C3C'
    elif total_sg < 0:
        sg_color = '#F39C12'
    else:
        sg_color = '#27AE60'
    
    st.markdown(f"""
    <div class="hero-card" style="border-left: 4px solid {sg_color};">
        <div style="font-size: 1.8em; margin-bottom: 0.25rem;">{icon}</div>
        <div class="hero-value">{count}</div>
        <div class="hero-label">{category}</div>
        <div class="hero-sg" style="color: {sg_color};">SG: {total_sg:+.2f}</div>
    </div>
    """, unsafe_allow_html=True)


def render_trend_analysis(trend_data: dict):
    """Render the collapsible trend analysis section."""
    with st.expander("📈 Root Cause Trend Analysis", expanded=False):
        st.markdown("#### Root Cause Distribution by Round")
        
        data = trend_data.get('data', [])
        categories = trend_data.get('categories', [])
        
        if len(data) == 0:
            st.info("Not enough data to display trend analysis")
            return
        
        # Convert to DataFrame for plotting
        trend_df = pd.DataFrame(data)
        
        # Create dual-axis chart
        fig = go.Figure()
        
        # Primary axis: Stacked bar for root causes
        colors = px.colors.qualitative.Set2
        color_idx = 0
        
        for category in categories:
            if category in trend_df.columns:
                fig.add_trace(go.Bar(
                    x=trend_df['round'],
                    y=trend_df[category],
                    name=category,
                    marker_color=colors[color_idx % len(colors)],
                    yaxis='y'
                ))
                color_idx += 1
        
        # Secondary axis: Line for total fails
        fig.add_trace(go.Scatter(
            x=trend_df['round'],
            y=trend_df['total_fails'],
            name='Total Fails',
            mode='lines+markers',
            line=dict(color='#2C3E50', width=3),
            yaxis='y2'
        ))
        
        # Update layout for dual axis
        fig.update_layout(
            yaxis=dict(
                title='Root Cause Count',
                overlaying='y2',
                side='left'
            ),
            yaxis2=dict(
                title='Total Fails',
                side='right'
            ),
            xaxis_title='Round',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            ),
            height=400,
            barmode='stack'
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_penalty_metrics(penalty_metrics: dict):
    """Render the penalty and severe shot analysis section."""
    st.subheader("⚠️ Penalty & Severe Shot Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        bogey_pct = penalty_metrics.get('bogey_with_penalty_pct', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #F39C12;">{bogey_pct:.1f}%</div>
            <div class="metric-label">Bogey Holes w/ Penalty</div>
            <div style="font-size: 0.8em; color: #666; margin-top: 0.5rem;">
                of {penalty_metrics.get('bogey_total', 0)} total bogey holes
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        double_pct = penalty_metrics.get('double_bogey_with_penalty_pct', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #E74C3C;">{double_pct:.1f}%</div>
            <div class="metric-label">Double Bogey+ w/ Penalty</div>
            <div style="font-size: 0.8em; color: #666; margin-top: 0.5rem;">
                of {penalty_metrics.get('double_bogey_total', 0)} total double+ holes
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        severe_pct = penalty_metrics.get('double_bogey_multiple_severe_pct', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #E74C3C;">{severe_pct:.1f}%</div>
            <div class="metric-label">Double Bogey 2+ Severe Shots</div>
            <div style="font-size: 0.8em; color: #666; margin-top: 0.5rem;">
                Multiple SG ≤ -0.5 shots
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_detail_sections(double_bogey: dict, bogey: dict, underperformance: dict):
    """Render the three detail sections."""
    
    # Section 1: Double Bogey+
    render_section_detail(
        "🔴 Section 1: Double Bogey+ Root Cause",
        double_bogey,
        "Double Bogey+ holes (score ≥ +2) with root cause analysis"
    )
    st.divider()
    
    # Section 2: Bogey
    render_section_detail(
        "🟡 Section 2: Bogey Root Cause",
        bogey,
        "Bogey holes (score = +1) with root cause analysis"
    )
    st.divider()
    
    # Section 3: Underperformance
    render_section_detail(
        "🔵 Section 3: Underperformance Root Cause",
        underperformance,
        "Underperformance holes (par/better with scoring issues)"
    )


def render_section_detail(header: str, data: dict, description: str):
    """Render a single section detail."""
    st.markdown(f"#### {header}")
    st.markdown(f"*{description}*")
    
    total_holes = data.get('total_holes', 0)
    
    if total_holes == 0:
        st.info("No holes in this category")
        return
    
    st.markdown(f"**Total Holes: {total_holes}**")
    
    # Category breakdown
    category_counts = data.get('category_counts', {})
    category_sg = data.get('category_sg', {})
    
    if category_counts:
        breakdown_data = []
        for cat in ScoringPerformanceEngine.ROOT_CAUSE_CATEGORIES:
            count = category_counts.get(cat, 0)
            sg = category_sg.get(cat, 0)
            if count > 0:
                breakdown_data.append({
                    'Category': cat,
                    'Count': count,
                    'Total SG': sg
                })
        
        if breakdown_data:
            breakdown_df = pd.DataFrame(breakdown_data)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                fig = px.bar(
                    breakdown_df,
                    x='Category',
                    y='Count',
                    color='Count',
                    color_continuous_scale='Reds'
                )
                fig.update_layout(showlegend=False, height=250)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.dataframe(
                    breakdown_df,
                    hide_index=True,
                    column_config={
                        'Count': st.column_config.NumberColumn('Count', format='%d'),
                        'Total SG': st.column_config.NumberColumn('Total SG', format='%.2f')
                    }
                )
    
    # Show individual hole details
    root_causes = data.get('root_causes', [])
    if root_causes:
        with st.expander(f"View All {total_holes} Hole Details", expanded=False):
            detail_df = pd.DataFrame(root_causes)
            
            # Select columns to display
            display_cols = ['round_id', 'hole', 'hole_score', 'score_vs_par', 
                           'shot_number', 'shot_type', 'distance', 'sg_value', 
                           'root_cause', 'penalty']
            
            available_cols = [c for c in display_cols if c in detail_df.columns]
            
            if available_cols:
                st.dataframe(
                    detail_df[available_cols],
                    hide_index=True,
                    column_config={
                        'hole_score': st.column_config.NumberColumn('Score', format='%d'),
                        'sg_value': st.column_config.NumberColumn('SG', format='%.2f'),
                        'distance': st.column_config.NumberColumn('Distance (yd)', format='%.0f')
                    }
                )


def render_root_cause_detail_section(detail_df: pd.DataFrame):
    """Render the collapsible root cause detail section."""
    with st.expander("📋 Root Cause Detail Data", expanded=False):
        st.markdown("#### Shot-Level Detail by Root Cause Category")
        
        if len(detail_df) == 0:
            st.info("No root cause detail data available")
            return
        
        # Filtering options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_section = st.multiselect(
                "Filter by Section",
                options=['Double Bogey+', 'Bogey', 'Underperformance'],
                default=['Double Bogey+', 'Bogey', 'Underperformance']
            )
        
        with col2:
            selected_category = st.multiselect(
                "Filter by Root Cause",
                options=ScoringPerformanceEngine.ROOT_CAUSE_CATEGORIES,
                default=ScoringPerformanceEngine.ROOT_CAUSE_CATEGORIES
            )
        
        with col3:
            min_sg = st.number_input(
                "Min SG Value",
                value=float(detail_df['sg_value'].min()) if 'sg_value' in detail_df.columns else -5.0,
                step=0.5
            )
        
        # Apply filters
        filtered_df = detail_df.copy()
        
        if 'section' in filtered_df.columns and selected_section:
            filtered_df = filtered_df[filtered_df['section'].isin(selected_section)]
        
        if 'root_cause' in filtered_df.columns and selected_category:
            filtered_df = filtered_df[filtered_df['root_cause'].isin(selected_category)]
        
        if 'sg_value' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['sg_value'] <= min_sg]
        
        # Sorting options
        sort_col, sort_dir = st.columns(2)
        
        with sort_col:
            sort_by = st.selectbox(
                "Sort by",
                options=['sg_value', 'round_id', 'hole', 'root_cause', 'section'],
                index=0
            )
        
        with sort_dir:
            ascending = st.toggle("Ascending", value=False)
        
        # Sort the dataframe
        if sort_by in filtered_df.columns:
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
        
        # Display filtered data
        st.markdown(f"Showing {len(filtered_df)} of {len(detail_df)} records")
        
        # Format columns for display
        if len(filtered_df) > 0:
            display_cols = [
                'round_id', 'hole', 'section', 'hole_score',
                'shot_number', 'shot_type', 'distance', 
                'sg_value', 'root_cause', 'ending_location', 'penalty'
            ]
            
            available_cols = [c for c in display_cols if c in filtered_df.columns]
            
            st.dataframe(
                filtered_df[available_cols],
                hide_index=True,
                use_container_width=True,
                column_config={
                    'hole_score': st.column_config.NumberColumn('Score', format='%d'),
                    'shot_number': st.column_config.NumberColumn('Shot #', format='%d'),
                    'sg_value': st.column_config.NumberColumn('SG', format='%.2f'),
                    'distance': st.column_config.NumberColumn('Dist (yd)', format='%.0f')
                }
            )
        
        # Summary by filtered data
        if len(filtered_df) > 0:
            st.markdown("#### Summary by Root Cause (Filtered)")
            
            if 'root_cause' in filtered_df.columns:
                summary = filtered_df.groupby('root_cause').agg({
                    'sg_value': ['count', 'sum', 'mean']
                }).round(2)
                summary.columns = ['Count', 'Total SG', 'Avg SG']
                summary = summary.sort_values('Total SG')
                st.dataframe(summary, use_container_width=True)


# For standalone page execution
if __name__ == "__main__":
    st.info("This page should be run from app.py")
