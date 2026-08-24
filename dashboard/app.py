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

st.set_page_config(page_title="EPL Analytics Dashboard", page_icon="⚽", layout="wide")
st.title("⚽ Premier League (EPL) Data Analytics Dashboard")
st.markdown("---")

seasons = load_seasons()
if not seasons:
    st.error("Chưa kết nối được CSDL PostgreSQL!")
    st.stop()

col_left, col_right = st.columns([1, 2], gap="large")

# --- LEFT COLUMN: Pie Chart ---
with col_left:
    st.subheader("📊 Tỷ Lệ Thắng/Hòa/Thua")
    selected_season_left = st.selectbox("Mùa giải (Trái):", seasons, key="s_left")
    df_current = load_current_standings(selected_season_left)
    selected_team = st.selectbox("Chọn đội bóng:", df_current['team_name'].tolist(), key="t_left")
    
    team_info = df_current[df_current['team_name'] == selected_team].iloc[0]
    
    c1, c2 = st.columns([1, 3])
    with c1:
        if pd.notnull(team_info['crest']) and str(team_info['crest']).startswith("http"):
            st.image(team_info['crest'], width=56)
    with c2:
        st.markdown(f"### {team_info['team_name']} ({team_info['tla']})")
        st.caption(f"Hạng: #{team_info['rank']} | Điểm: {team_info['points']} | Hiệu số: {team_info['goals_difference']}")

    pie_df = pd.DataFrame({
        'Kết quả': ['Thắng (Win)', 'Hòa (Draw)', 'Thua (Loss)'],
        'Số trận': [int(team_info['win']), int(team_info['draw']), int(team_info['lose'])]
    })
    fig_pie = px.pie(
        pie_df, values='Số trận', names='Kết quả', color='Kết quả',
        color_discrete_map={'Thắng (Win)': '#2ca02c', 'Hòa (Draw)': '#ff7f0e', 'Thua (Loss)': '#d62728'},
        hole=0.45, title=f"Kết quả {team_info['team_name']} (Mùa {selected_season_left})"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# --- RIGHT COLUMN: Line Chart ---
with col_right:
    st.subheader("📈 So Sánh Phong Độ Các Đội Bóng")
    c1, c2, c3 = st.columns(3)
    with c1:
        selected_season_right = st.selectbox("Mùa giải (Phải):", seasons, key="s_right")
    with c2:
        mode = st.radio("Chế độ:", ["Theo Vòng Đấu (Matchday)", "Theo Số Trận Đã Đá (Played)"], key="m_right")
    with c3:
        metric = st.selectbox("Chỉ số:", ["points", "rank", "goals_scored", "goals_conceded", "goals_difference"], key="met_right")

    df_line = load_matchday_standings(selected_season_right) if mode == "Theo Vòng Đấu (Matchday)" else load_history_standings(selected_season_right)
    x_col = "matchday" if mode == "Theo Vòng Đấu (Matchday)" else "played"
    
    available_teams = sorted(df_line['team_name'].unique())
    color_map = get_team_color_map(available_teams)
    
    select_all = st.checkbox("Chọn tất cả các đội bóng", value=True, key="sel_all")
    selected_teams = available_teams if select_all else st.multiselect("Chọn đội bóng:", available_teams, default=available_teams[:5], key="sel_teams")

    if selected_teams:
        df_sub = df_line[df_line['team_name'].isin(selected_teams)].copy()
        latest_data = pd.merge(df_sub.groupby('team_name')[x_col].max().reset_index(), df_sub, on=['team_name', x_col])
        sorted_teams = latest_data.sort_values(by=metric, ascending=(metric == "rank"))['team_name'].tolist()

        fig_line = px.line(
            df_sub, x=x_col, y=metric, color='team_name', color_discrete_map=color_map,
            category_orders={'team_name': sorted_teams}, markers=True,
            title=f"Biến động {metric.upper()} - Mùa {selected_season_right}"
        )
        if metric == "rank":
            fig_line.update_yaxes(autorange="reversed", dtick=1, title="Thứ hạng (Hạng 1 ở trên)")
        
        st.plotly_chart(fig_line, use_container_width=True)
