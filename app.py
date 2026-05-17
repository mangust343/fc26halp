import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    df = pd.read_csv("FC26_20250921.csv", low_memory=False)
    return df

df = load_data()

st.title("⚽ Твій Персональний Скаут FC 26")
st.markdown("Ця прога допоможе тобі підібрати ідеальні трансфери для кар'єри!")

teams = df['club_name'].dropna().unique().tolist()
teams.sort()
selected_team = st.selectbox("Обери свій клуб:", teams)

if selected_team:
    team_players = df[df['club_name'] == selected_team].sort_values(by='overall', ascending=False)
    st.subheader(f"🏟 Склад команди: {selected_team}")
    st.dataframe(team_players[['short_name', 'player_positions', 'overall', 'potential', 'age', 'value_eur', 'wage_eur']])

    st.subheader("🔎 Пошук підсилення")
    col1, col2 = st.columns(2)
    with col1:
        position = st.selectbox("На яку позицію шукаємо гравця?", ["ST", "LW", "RW", "CAM", "CM", "CDM", "LB", "CB", "RB", "GK", "LM", "RM"])
    with col2:
        max_budget = st.number_input("Твій максимальний бюджет (в євро):", min_value=0, value=20000000,

