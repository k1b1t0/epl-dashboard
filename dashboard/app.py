import streamlit as st
import pandas as pd
import plotly.express as px

import sys
from pathlib import Path

# Ensure dashboard directory and project root are in sys.path
DASHBOARD_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DASHBOARD_DIR.parent
if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.database import (
    load_seasons,
    load_current_standings,
    load_matchday_standings,
    load_history_standings
)
from dashboard.utils import get_team_color_map

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="EPL Dashboard", 
    page_icon="⚽", 
    layout="wide"
)

# Load Seasons
seasons = load_seasons()
if not seasons:
    st.error("Failed to connect to PostgreSQL Database! Please verify containers are running.")
    st.stop()

# ==========================================
# TOP HEADER & GLOBAL SEASON SELECTOR
# ==========================================
title_col, season_col = st.columns([3, 1])

with title_col:
    st.title("⚽ EPL Dashboard")

with season_col:
    selected_season = st.selectbox("Season:", seasons, index=0, key="global_season")

season_display = f"{selected_season}/{selected_season + 1}"
st.markdown("---")

# Fetch Season Current Standings
df_current = load_current_standings(selected_season)
if df_current.empty:
    st.warning(f"No standings data found for season {selected_season}.")
    st.stop()

col_left, col_right = st.columns([1, 2], gap="large")

# ==========================================
# LEFT COLUMN: TEAM PERFORMANCE OVERVIEW
# ==========================================
with col_left:
    st.subheader("📊 Team Performance Overview")
    
    # Team dropdown with formatted label (TLA - Full Name)
    teams_dict = {row['team_name']: f"{row['tla']} - {row['team_name']}" for _, row in df_current.iterrows()}
    available_teams = list(teams_dict.keys())
    
    selected_team = st.selectbox(
        "Select Team:", 
        available_teams, 
        format_func=lambda x: teams_dict[x],
        index=0, 
        key="t_select"
    )
    
    team_info = df_current[df_current['team_name'] == selected_team].iloc[0]
    
    # 100% Perfectly Centered Flexbox Header (Logo + Team Name + Stats)
    crest_url = team_info['crest'] if pd.notnull(team_info['crest']) and str(team_info['crest']).startswith("http") else ""
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 16px; margin-top: 12px; margin-bottom: 20px; background: rgba(255,255,255,0.04); padding: 12px 16px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);">
        <img src="{crest_url}" style="width: 56px; height: 56px; object-fit: contain;" alt="crest" />
        <div>
            <h3 style="margin: 0; padding: 0; font-size: 22px; font-weight: 700; line-height: 1.2;">{team_info['team_name']}</h3>
            <div style="font-size: 13px; opacity: 0.85; margin-top: 4px;">
                <b>Rank:</b> #{team_info['rank']} &nbsp;|&nbsp; <b>Points:</b> {team_info['points']} &nbsp;|&nbsp; <b>GD:</b> {team_info['goals_difference']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    pie_df = pd.DataFrame({
        'Outcome': ['Win', 'Draw', 'Loss'],
        'Matches': [int(team_info['win']), int(team_info['draw']), int(team_info['lose'])]
    })
    
    fig_pie = px.pie(
        pie_df, 
        values='Matches', 
        names='Outcome', 
        color='Outcome',
        color_discrete_map={'Win': '#2ca02c', 'Draw': '#ff7f0e', 'Loss': '#d62728'},
        hole=0.4, 
        title=f"Result Breakdown: {team_info['team_name']}"
    )
    fig_pie.update_traces(textinfo='value+percent')
    st.plotly_chart(fig_pie, use_container_width=True)

# ==========================================
# RIGHT COLUMN: COMPARATIVE TRENDS (LINE CHART)
# ==========================================
with col_right:
    st.subheader("📈 Team Trend Comparisons")
    c1, c2 = st.columns(2)
    with c1:
        trend_mode = st.radio("Timeline:", ["By Matchday", "By Games Played"], key="trend_mode")
    with c2:
        metric = st.selectbox(
            "Metric:", 
            ["points", "rank", "goals_scored", "goals_conceded", "goals_difference"], 
            index=0,
            key="trend_metric"
        )

    df_line = load_matchday_standings(selected_season) if trend_mode == "By Matchday" else load_history_standings(selected_season)
    x_col = "matchday" if trend_mode == "By Matchday" else "played"
    
    all_teams = sorted(df_line['team_name'].unique())
    color_map = get_team_color_map(all_teams)
    
    select_all = st.checkbox("Compare All Teams", value=True, key="sel_all_cb")
    selected_teams = all_teams if select_all else st.multiselect("Select Teams:", all_teams, default=all_teams[:5], key="sel_teams_ms")

    if selected_teams:
        df_sub = df_line[df_line['team_name'].isin(selected_teams)].copy()
        latest_data = pd.merge(df_sub.groupby('team_name')[x_col].max().reset_index(), df_sub, on=['team_name', x_col])
        sorted_teams = latest_data.sort_values(by=metric, ascending=(metric == "rank"))['team_name'].tolist()

        fig_line = px.line(
            df_sub, 
            x=x_col, 
            y=metric, 
            color='team_name', 
            color_discrete_map=color_map,
            category_orders={'team_name': sorted_teams}, 
            markers=True,
            title=f"Season Progression: {metric.replace('_', ' ').title()}"
        )
        if metric == "rank":
            fig_line.update_yaxes(autorange="reversed", dtick=1, title="Rank (Rank #1 at Top)")
        
        st.plotly_chart(fig_line, use_container_width=True)

# ==========================================
# BOTTOM SECTION: STANDINGS TABLE & FILTERS
# ==========================================
st.markdown("---")
st.subheader("🏆 Standings Table")

# Standings Filters Placed Directly Above the Table
f_col1, f_col2, f_col3 = st.columns([1, 1, 2])
with f_col1:
    view_mode = st.radio(
        "View Mode:", 
        ["Current Standings", "By Matchday", "By Games Played"], 
        key="table_viewmode"
    )
with f_col2:
    selected_number = 1
    if view_mode == "By Matchday":
        selected_number = st.slider("Matchday:", 1, 38, 1, key="tb_md_slider")
    elif view_mode == "By Games Played":
        selected_number = st.slider("Games Played:", 1, 38, 1, key="tb_pl_slider")
with f_col3:
    if view_mode == "Current Standings":
        st.caption(f"Showing latest overall standings for Season {season_display}")
    else:
        st.caption(f"Showing standings snapshot at step #{selected_number}")

# Fetch Standings Data
if view_mode == "Current Standings":
    df_standings = df_current.copy()
elif view_mode == "By Matchday":
    df_standings = load_matchday_standings(selected_season, selected_number)
else:
    df_standings = load_history_standings(selected_season, selected_number)

if not df_standings.empty:
    st.dataframe(
        df_standings, 
        use_container_width=True, 
        hide_index=True,
        column_order=[
            "rank", 
            "crest", 
            "team_name", 
            "played", 
            "points", 
            "goals_difference", 
            "goals_scored", 
            "goals_conceded", 
            "win", 
            "draw", 
            "lose"
        ],
        column_config={
            "rank": st.column_config.NumberColumn("Position", format="%d"),
            "crest": st.column_config.ImageColumn("Club"),
            "team_name": st.column_config.TextColumn("Team"),
            "played": st.column_config.NumberColumn("Played", format="%d"),
            "points": st.column_config.NumberColumn("Points 💥", format="%d", help="Total Earned Points"),
            "goals_difference": st.column_config.NumberColumn("GD", format="%+d"),
            "goals_scored": st.column_config.NumberColumn("GF", format="%d"),
            "goals_conceded": st.column_config.NumberColumn("GA", format="%d"),
            "win": st.column_config.NumberColumn("W", format="%d"),
            "draw": st.column_config.NumberColumn("D", format="%d"),
            "lose": st.column_config.NumberColumn("L", format="%d")
        }
    )
else:
    st.warning("No standings data available for the selected filters.")
