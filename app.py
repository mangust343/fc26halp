import streamlit as st
import pandas as pd

# 1. Завантаження бази даних
@st.cache_data
def load_data():
    df = pd.read_csv("FC26_20250921.csv", low_memory=False)
    # Залишаємо тільки потрібні колонки для швидкості
    cols = ['short_name', 'club_name', 'overall', 'potential', 'age', 'value_eur', 'wage_eur', 'player_positions', 'pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']
    return df[cols]

df = load_data()

st.title("⚽ Супер-Скаут & Менеджер Кар'єри FC 26")
st.markdown("Твій персональний інтерактивний штаб для керування командою!")

# 2. Ініціалізація збереження стану (пам'ять для трансферів)
if 'current_team' not in st.session_state:
    st.session_state.current_team = None
if 'custom_players' not in st.session_state:
    st.session_state.custom_players = {}

# Вибір клубу
teams = df['club_name'].dropna().unique().tolist()
teams.sort()
selected_team = st.selectbox("Обери свій клуб, щоб підтягнути склад:", ["-- Оберіть клуб --"] + teams)

if selected_team != "-- Оберіть клуб --":
    # Якщо змінили клуб — скидаємо кастомні трансфери для чистоти
    if st.session_state.current_team != selected_team:
        st.session_state.current_team = selected_team
        # Завантажуємо дефолтних гравців клубу
        base_players = df[df['club_name'] == selected_team].to_dict(orient='records')
        st.session_state.custom_players = {p['short_name']: p for p in base_players}

    # Працюємо з поточним складом
    my_players = list(st.session_state.custom_players.values())
    team_df = pd.DataFrame(my_players)

    if not team_df.empty:
        team_df = team_df.sort_values(by='overall', ascending=False).reset_index(drop=True)
        
        # Розділяємо на Основу (перші 11) та Заміну
        starters = team_df.head(11)
        bench = team_df.iloc[11:]

        # --- БЛОК 4: ШІ АНАЛІЗ ТА ПІДБІР СХЕМИ ---
        st.header("🧠 ШІ-Аналітик: Оптимальна тактика")
        
        # Рахуємо позиції серед найкращих гравців
        all_positions = ",".join(starters['player_positions'].astype(str)).upper()
        
        strikers = all_positions.count("ST") + all_positions.count("CF")
        wingers = all_positions.count("LW") + all_positions.count("RW") + all_positions.count("LM") + all_positions.count("RM")
        defenders = all_positions.count("CB") + all_positions.count("LB") + all_positions.count("RB")
        
        if strikers >= 2 and wingers >= 2:
            best_formation = "4-2-4 (Атакувальна з 2 форвардами та вінгерами)"
            tactical_tip = "🔥 У тебе потужний атакувальний потенціал! Використовуй швидкі фланги для прострілів на двох форвардів."
        elif wingers >= 2 and strikers == 1:
            best_formation = "4-3-3 (Класична флангова)"
            tactical_tip = "🚀 Твої вінгери мають розганяти атаки по флангах і зміщуватися в центр під удар форварду."
        elif strikers >= 2 and wingers < 2:
            best_formation = "4-4-2 (Рівновага або Ромб)"
            tactical_tip = "⚖️ Надійний баланс. Контролюй центр поля і шукай пасами двох нападників попереду."
        else:
            best_formation = "4-2-3-1 (Сучасна тактична)"
            tactical_tip = "🛡 Стабільна схема з насиченим центром. Роби ставку на розіграш м'яча через атакувального півзахисника (CAM)."

        st.success(f"📋 **Рекомендована схема:** {best_formation}")
        st.info(tactical_tip)

        # --- БЛОК 2: ВІДОБРАЖЕННЯ СКЛАДУ ---
        st.header("🏟 Твій актуальний ростер")
        
        st.subheader("⭐ Стартовий склад (ТОП-11)")
        st.dataframe(starters[['short_name', 'player_positions', 'overall', 'potential', 'age', 'value_eur', 'wage_eur']])
        
        if not bench.empty:
            st.subheader("🪑 Лава запасних та резерв")
            st.dataframe(bench[['short_name', 'player_positions', 'overall', 'potential', 'age', 'value_eur', 'wage_eur']])

        # --- БЛОК 1 та 3: УПРАВЛІННЯ ТРАНСФЕРАМИ ТА ЦІНИ ---
        st.header("🔄 Трансферний ринок клубу")
        
        tab1, tab2 = st.tabs(["❌ Продати гравця", "🛍 Купити підсилення"])
        
        with tab1:
            player_to_sell = st.selectbox("Обери кого продати:", ["-- Виберіть гравця --"] + list(st.session_state.custom_players.keys()))
            if player_to_sell != "-- Виберіть гравця --":
                p_data = st.session_state.custom_players[player_to_sell]
                st.warning(f"💵 Ринкова вартість: {p_data['value_eur']:,} € | Поточна зарплата: {p_data['wage_eur']:,} €/тиж")
                st.write(f"💡 *Порада скаута: Цього гравця можна спробувати відпустити за {int(p_data['value_eur']*1.2):,} €, якщо торгуватися з іншими клубами.*")
                if st.button(f"Підтвердити продаж {player_to_sell}"):
                    del st.session_state.custom_players[player_to_sell]
                    st.success(f"Гравець {player_to_sell} успішно проданий!")
                    st.rerun()

        with tab2:
            st.subheader("🔎 Пошук на ринку")
            search_name = st.text_input("Введи прізвище гравця для покупки:")
            
            if search_name:
                search_results = df[df['short_name'].str.contains(search_name, case=False, na=False)].head(5)
                if not search_results.empty:
                    for idx, row in search_results.iterrows():
                        # Розрахунок реалістичних цін кар'єри
                        rec_buy_price = int(row['value_eur'] * 1.25) # Націнка клубу (~25%)
                        rec_wage = int(row['wage_eur'] * 1.15) if row['wage_eur'] > 0 else 5000 # Запит гравця
                        
                        st.write(f"🏃‍♂️ **{row['short_name']}** ({row['player_positions']}) | Клуб: {row['club_name']}")
                        st.write(f"📊 Рейтинг: {row['overall']} / Потенціал: {row['potential']} | Вік: {row['age']}")
                        st.markdown(f"💰 **Чиста вартість:** {row['value_eur']:,} €")
                        st.markdown(f"🎯 **Рекомендована ціна покупки (на ринку):** ~`{rec_buy_price:,} €`")
                        st.markdown(f"💵 **Рекомендована зарплата:** ~`{rec_wage:,} € / тиждень`")
                        
                        if row['short_name'] in st.session_state.custom_players:
                            st.text("✅ Вже у твоїй команді")
                        else:
                            if st.button(f"Підписати контрак з {row['short_name']}", key=f"buy_{idx}"):
                                # Додаємо гравця у наш клуб
                                new_player = row.to_dict()
                                new_player['club_name'] = selected_team
                                st.session_state.custom_players[row['short_name']] = new_player
                                st.success(f"📝 {row['short_name']} підписаний! Він доданий на лаву запасних.")
                                st.rerun()
                        st.write("---")
                else:
                    st.error("Гравця з таким іменем не знайдено 😢")
