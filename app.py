import streamlit as st
import pandas as pd

# 1. Завантаження бази даних
@st.cache_data
def load_data():
    df = pd.read_csv("FC26_20250921.csv", low_memory=False)
    cols = ['short_name', 'club_name', 'overall', 'potential', 'age', 'value_eur', 'wage_eur', 'player_positions']
    return df[cols]

df = load_data()

st.title("⚽ Тактичний Скаут FC 26")

# 2. Пам'ять програми
if 'current_team' not in st.session_state:
    st.session_state.current_team = None
if 'custom_players' not in st.session_state:
    st.session_state.custom_players = []

teams = df['club_name'].dropna().unique().tolist()
teams.sort()
selected_team = st.selectbox("Обери свій клуб:", ["-- Оберіть клуб --"] + teams)

if selected_team != "-- Оберіть клуб --":
    if st.session_state.current_team != selected_team:
        st.session_state.current_team = selected_team
        base_players = df[df['club_name'] == selected_team].sort_values(by='overall', ascending=False).to_dict(orient='records')
        for idx, p in enumerate(base_players):
            p['is_starter'] = True if idx < 11 else False
        st.session_state.custom_players = base_players

    players_list = list(st.session_state.custom_players)
    starters = [p for p in players_list if p['is_starter']]
    bench = [p for p in players_list if not p['is_starter']]

    # 3. ШІ Авто-схема
    all_pos = ",".join([p['player_positions'] for p in starters]).upper()
    strikers = all_pos.count("ST") + all_pos.count("CF")
    wingers = all_pos.count("LW") + all_pos.count("RW") + all_pos.count("LM") + all_pos.count("RM")
    
    if strikers >= 2 and wingers >= 2:
        formation = "4-2-4 (Атака з 2 форвардами та вінгерами)"
    elif wingers >= 2:
        formation = "4-3-3 (Класична флангова)"
    elif strikers >= 2:
        formation = "4-4-2 (Баланс з 2 форвардами)"
    else:
        formation = "4-2-3-1 (Сучасна з CAM)"

    st.success(f"🧠 **Оптимальна тактика від ШІ:** {formation}")

    # 4. Візуальне поле (Воротар знизу, напад зверху)
    st.header("📋 Розстановка на полі")
    starters_sorted = sorted(starters, key=lambda x: x['overall'], reverse=True)
    
    # Ділимо склад на позиційні лінії (якщо гравців менше 11, код не зламається)
    line_att = starters_sorted[0:3]
    line_mid = starters_sorted[3:7]
    line_def = starters_sorted[7:10]
    line_gk = starters_sorted[10:]

    field_style = "background:#2e7d32; border:3px solid white; border-radius:10px; padding:15px; text-align:center; color:white; box-shadow: inset 0 0 20px #1b5e20;"
    box_style = "background:#1e3c72; padding:5px; border-radius:5px; font-size:11px; min-width:70px; border:1px solid gold;"
    gk_style = "background:#d84315; padding:5px; border-radius:5px; font-size:11px; min-width:70px; border:1px solid white;"

    field_html = f'<div style="{field_style}">'
    
    # 🔝 НАПАД (ВГОРІ)
    if line_att:
        field_html += '<span style="font-size:11px;font-weight:bold;color:#ffeb3b;">🔥 НАПАД</span>'
        field_html += '<div style="display:flex;justify-content:space-around;margin:10px 0 20px 0;">'
        for p in line_att:
            field_html += f'<div style="{box_style}">{p["short_name"]}<br><b>OVR: {p["overall"]}</b></div>'
        field_html += '</div>'
    
    # ⚡ ПІВЗАХИСТ (ПО СЕРЕДИНІ)
    if line_mid:
        field_html += '<span style="font-size:11px;font-weight:bold;color:#b3e5fc;">⚡ ПІВЗАХИСТ</span>'
        field_html += '<div style="display:flex;justify-content:space-around;margin:10px 0 20px 0;">'
        for p in line_mid:
            field_html += f'<div style="{box_style}">{p["short_name"]}<br><b>OVR: {p["overall"]}</b></div>'
        field_html += '</div>'
    
    # 🛡️ ЗАХИСТ (ПЕРЕД ВОРОТАРЕМ)
    if line_def:
        field_html += '<span style="font-size:11px;font-weight:bold;color:#e0e0e0;">🛡️ ЗАХИСТ</span>'
        field_html += '<div style="display:flex;justify-content:space-around;margin:10px 0 20px 0;">'
        for p in line_def:
            field_html += f'<div style="{box_style}">{p["short_name"]}<br><b>OVR: {p["overall"]}</b></div>'
        field_html += '</div>'
    
    # 🧤 ВОРОТАР (ЗНИЗУ)
    if line_gk:
        field_html += '<span style="font-size:11px;font-weight:bold;color:#ffccbc;">🧤 ВОРОТАР</span>'
        field_html += '<div style="display:flex;justify-content:center;margin-top:10px;">'
        for p in line_gk:
            field_html += f'<div style="{gk_style}">{p["short_name"]}<br><b>OVR: {p["overall"]}</b></div>'
        field_html += '</div>'
        
    field_html += '</div>'
    
    st.markdown(field_html, unsafe_allow_html=True)

    # 5. Керування основою та заміною
    st.header("🏟️ Керування складом")
    
    st.subheader("⭐ Стартові 11")
    for idx, p in enumerate(starters):
        col1, col2 = st.columns([4, 1])
        col1.write(f"🏃‍♂️ **{p['short_name']}** ({p['player_positions']}) | OVR: **{p['overall']}**")
        if col2.button("⬇️ Банка", key=f"bench_{p['short_name']}_{idx}"):
            for op in st.session_state.custom_players:
                if op['short_name'] == p['short_name']: op['is_starter'] = False
            st.rerun()

    st.subheader("🪑 Лава запасних")
    if not bench:
        st.info("Запас порожній.")
    else:
        for idx, p in enumerate(bench):
            col1, col2 = st.columns([4, 1])
            col1.write(f"🪵 **{p['short_name']}** ({p['player_positions']}) | OVR: **{p['overall']}**")
            if col2.button("⬆️ В основу", key=f"start_{p['short_name']}_{idx}"):
                for op in st.session_state.custom_players:
                    if op['short_name'] == p['short_name']: op['is_starter'] = True
                st.rerun()

    # 6. Трансфери та Підказки цін
    st.header("🔄 Трак трансферів")
    t1, t2 = st.tabs(["🛍️ Купити", "❌ Продати"])
    
    with t1:
        s_name = st.text_input("Пошук за прізвищем:")
        if s_name:
            res = df[df['short_name'].str.contains(s_name, case=False, na=False)].head(3)
            for idx, row in res.iterrows():
                p_price = int(row['value_eur'] * 1.25)
                p_wage = int(row['wage_eur'] * 1.15) if row['wage_eur'] > 0 else 4500
                st.write(f"**{row['short_name']}** | OVR: {row['overall']} | {row['club_name']}")
                st.markdown(f"💰 Ціна ринку: `{p_price:,} €` | Зарплата: `{p_wage:,} €/тиж`")
                
                owned = any(cp['short_name'] == row['short_name'] for cp in st.session_state.custom_players)
                if owned:
                    st.text("✅ Вже є у складі")
                else:
                    if st.button(f"Підписати {row['short_name']}", key=f"b_{idx}"):
                        np = row.to_dict()
                        np['is_starter'] = False
                        st.session_state.custom_players.append(np)
                        st.rerun()
                st.write("---")

    with t2:
        all_names = [p['short_name'] for p in st.session_state.custom_players]
        to_sell = st.selectbox("Видалити з команди:", ["-- Обери кого вигнати --"] + all_names)
        if to_sell != "-- Обери кого вигнати --":
            if st.button("Підтвердити продаж"):
                st.session_state.custom_players = [p for p in st.session_state.custom_players if p['short_name'] != to_sell]
                st.rerun()
