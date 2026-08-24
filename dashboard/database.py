import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

POSTGRES_HOST = "localhost"
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "epl")
POSTGRES_USER = os.getenv("POSTGRES_USER", "root")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "root")

DB_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

@st.cache_resource
def get_db_engine():
    return create_engine(DB_URL)

engine = get_db_engine()

@st.cache_data(ttl=60)
def load_seasons() -> list:
    try:
        query = "SELECT DISTINCT season FROM public.fct_current_standings ORDER BY season DESC;"
        df = pd.read_sql(query, engine)
        return df['season'].tolist()
    except Exception:
        return []

@st.cache_data(ttl=60)
def load_current_standings(season: int) -> pd.DataFrame:
    query = f"SELECT * FROM public.fct_current_standings WHERE season = {season} ORDER BY rank ASC;"
    return pd.read_sql(query, engine)

@st.cache_data(ttl=60)
def load_matchday_standings(season: int, matchday: int = None) -> pd.DataFrame:
    if matchday is not None:
        query = f"SELECT * FROM public.fct_matchday_standings WHERE season = {season} AND matchday = {matchday} ORDER BY rank ASC;"
    else:
        query = f"SELECT * FROM public.fct_matchday_standings WHERE season = {season} ORDER BY matchday ASC, rank ASC;"
    return pd.read_sql(query, engine)

@st.cache_data(ttl=60)
def load_history_standings(season: int, played: int = None) -> pd.DataFrame:
    if played is not None:
        query = f"SELECT * FROM public.fct_history_standings WHERE season = {season} AND played = {played} ORDER BY rank ASC;"
    else:
        query = f"SELECT * FROM public.fct_history_standings WHERE season = {season} ORDER BY played ASC, rank ASC;"
    return pd.read_sql(query, engine)