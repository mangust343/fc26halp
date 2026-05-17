import streamlit as st
import pandas as pd

# 1. Завантаження бази даних
@st.cache_data
def load_data():
    df = pd.read_csv("FC26_20250921.csv", low_memory=False)
    cols = ['short_name', 'club_name', 'overall', 'potential', 'age', 'value_eur', 'wage_eur', 'player_positions', 'pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']
    return df[cols]

df = load_data()

st.title("⚽ Супер-Скаут & Тактичний Менеджер FC 26")

# 2. Ініціалізація пам'яті програми
if 'current_team' not in st.session_state:
    st.session_state.current_team = None
if 'custom_players' not in st.session_state:
    st.session_state.custom_players = []

# Вибір клубу
teams = df['club_name'].dropna().unique().tolist()
teams.sort()
selected_team = st.selectbox("Обери свій клуб:", ["-- Оберіть клуб --"] + teams)

if selected_team != "-- Оберіть клуб --":
    # Завантаження складу при першому виборі
    if st.session_state.current_team != selected_team:
        st.session_state.current_team = selected_team
        base_players = df[df['club_name'] == selected_team].sort_values(by='overall', ascending=False).to_dict(orient='records')
        # Додаємо статус: перші 11 в основу, інші на заміну
        for idx, p in enumerate(base_players):
            p['is_starter'] = True if idx < 11 else False
        st.session_state.custom_players = base_players

    # Обробка дій (переноси з заміни в основу)
    # Створюємо копію для безпечного перебору
    players_list = list(st.session_state.custom_players)
    
    starters = [p for p in players_list if p['is_starter']]
    bench = [p for p in players_list if not p['is_starter']]

    # --- БЛОК 1: ШІ АНАЛІЗ ТА АВТО-СХЕМА ---
    all_positions = ",".join([p['player_positions'] for p in starters]).upper()
    strikers = all_positions.count("ST") + all_positions.count("CF")
    wingers = all_positions.count("LW") + all_positions.count("RW") + all_positions.count("LM") + all_positions.count("RM")
    
    if strikers >= 2 and wingers >= 2:
        formation = "4-2-4"
        positions_layout = ["GK", "LB", "CB", "CB", "RB", "CM", "CM", "LW", "ST", "ST", "RW"]
    elif wingers >= 2:
        formation = "4-3-3"
        positions_layout = ["GK", "LB", "CB", "CB", "RB", "CM", "CDM", "CAM", "LW", "ST", "RW"]
    elif strikers >= 2:
        formation = "4-4-2"
        positions_layout = ["GK", "LB", "CB", "CB", "RB", "LM", "CM", "CM", "RM", "ST", "ST"]
    else:
        formation = "4-2-3-1"
        positions_layout = ["GK", "LB", "CB", "CB", "RB", "CDM", "CDM", "CAM", "LM", "RM", "ST"]

    st.success(f"🧠 **ШІ-Аналітик обрав тактику:** {formation} під твій поточний склад!")

    # --- БЛОК 2: ВІЗУАЛЬНЕ ФОТО РОЗТАШУВАННЯ (ГРАФІЧНЕ ПОЛЕ) ---
    st.header("📋 Тактична розстановка на полі")
    
    # Сортуємо стартовий склад для красивої посадки на позиції
    starters_sorted = sorted(starters, key=lambda x: x['overall'], reverse=True)
    
    # Малюємо поле через HTML/CSS стилі
    field_html = """
    <div style="background-color: #2e7d32; border: 3px solid white; border-radius: 10px; padding: 15px; text-align: center; font-family: Arial, sans-serif; color: white; box-shadow: inset 0 0 20px #1b5e20;">
        <div style="border: 2px dashed rgba(255,255,255,0.4); border-radius: 5px; padding: 10px;">
            <span style="background: rgba(0,0,0,0.6); padding: 3px 10px; border-radius: 10px; font-size: 12px; font-weight: bold;">🔥 АТАКУВАЛЬНА ЗОНА</span>
            <div style="display: flex; justify-content: space-around; margin: 20px 0;">
    """
    
    # Розподіляємо 11 гравців по умовних лініях поля (Атака, Півзахист, Захист, Воротар)
    # Для простоти візуалізації розіб'ємо ТОП-11 на лінії
    line_att = starters_sorted[0:3] if len(starters_sorted) >= 3 else starters_sorted
    line_mid = starters_sorted[3:7] if len(starters_sorted) >= 7 else []
    line_def = starters_sorted[7:10] if len(starters_sorted) >= 10 else []
    line_gk = [starters_sorted[10]] if len(starters_sorted) == 11 else []

    # Атака
    for p in line_att:
        field_html += f'<div style="background: #1e3c72; padding: 8px; border-radius: 5px; min-width: 75px; border: 1px solid gold;"><b style="font-size:11px;">{p["short_name"]}</b><br><span style="font-size:10px; color: #00ffcc;">OVR: {p["overall"]}</span></div>'
    
    field_html += '</div><span style="background: rgba(0,0,0,0.6); padding: 3px 10px; border-radius: 10px; font-size: 12px; font-weight: bold;">⚡ ПІВЗАХИСТ</span><div style="display: flex; justify-content: space-around; margin: 20px 0;">'
    
    # Півзахист
    for p in line_mid:
        field_html += f'<div style="background: #2a5298; padding: 8px; border-radius: 5px; min-width: 75px;"><b style="font-size:11px;">{p["short_name"]}</b><br><span style="font-size:10px; color: #00ffcc;">OVR: {p["overall"]}</span></div>'
        
    field_html += '</div><span style="background: rgba(0,0,0,0.6); padding: 3px 10px; border-radius: 10px; font-size: 12px; font-weight: bold;">🛡 ЗАХИСТ</span><div style="display: flex; justify-content: space-around; margin: 20px 0;">'
    
    # Захист
    for p in line_def:
        field_html += f'<div style="background: #37474f; padding: 8px; border-radius: 5px; min-width: 75px;"><b style="font-size:11px;">{p["short_name"]}</b><br><span style="font-size:10px; color: #
