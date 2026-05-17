import streamlit as st
import pandas as pd

# 1. Завантаження бази даних
@st.cache_data
def load_data():
    df = pd.read_csv("FC26_20250921.csv", low_memory=False)
    cols = ['short_name', 'club_name', 'overall', 'potential', 'age', 'value_eur', 'wage_eur', 'player_positions']
    return df[cols]

df = load_data()

st.title("⚽ Професійний Менеджер Кар'єри FC 26")

# 2. Ініціалізація пам'яті (Бюджет, Клуб, Гравці, Схема)
if 'budget' not in st.session_state:
    st.session_state.budget = 50000000  # Дефолтний бюджет 50 млн
if 'current_team' not in st.session_state:
    st.session_state.current_team = None
if 'custom_players' not in st.session_state:
    st.session_state.custom_players = []
if 'chosen_formation' not in st.session_state:
    st.session_state.chosen_formation = "Авто-вибір ШІ"

# --- БЛОК 1: КЕРУВАННЯ БУДЖЕТОМ ---
st.header("💰 Фінансовий департамент")
st.session_state.budget = st.number_input("Твій поточний бюджет трансферів (€):", min_value=0, value=st.session_state.budget, step=1000000)
st.metric(label="💵 Доступний баланс клубу", value=f"{st.session_state.budget:,} €")

# Вибір клубу
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

    # --- БЛОК 2: ВИБІР ТА АНАЛІЗ СХЕМИ ВІД ШІ ---
    st.header("🧠 Тактичний аналіз & Вибір схеми")
    
    # Вибір схеми користувачем
    formation_options = ["Авто-вибір ШІ", "4-2-4", "4-3-3", "4-4-2", "4-2-3-1"]
    st.session_state.chosen_formation = st.selectbox("Яку тактичну схему ти хочеш використовувати?", formation_options, index=formation_options.index(st.session_state.chosen_formation))

    # Рахуємо позиції в основі для аналізу ШІ
    all_pos = ",".join([p['player_positions'] for p in starters]).upper()
    strikers = all_pos.count("ST") + all_pos.count("CF")
    wingers = all_pos.count("LW") + all_pos.count("RW") + all_pos.count("LM") + all_pos.count("RM")
    midfielders = all_pos.count("CM") + all_pos.count("CDM") + all_pos.count("CAM")

    # Визначаємо, яка схема найкраща за складом
    if strikers >= 2 and wingers >= 2:
        ai_recommended = "4-2-4"
    elif wingers >= 2:
        ai_recommended = "4-3-3"
    elif strikers >= 2:
        ai_recommended = "4-4-2"
    else:
        ai_recommended = "4-2-3-1"

    # Сценарій 1: Користувач довірився ШІ
    if st.session_state.chosen_formation == "Авто-вибір ШІ":
        st.success(f"📋 **ШІ автоматично обрав схему:** {ai_recommended}")
        st.info("💡 *Порада тренера: Ця схема ідеально підходить під твоїх поточних ТОП-11 гравців.*")
    
    # Сценарій 2: Користувач сам вибрав тактику
    else:
        user_form = st.session_state.chosen_formation
        st.info(f"📋 **Твоя збережена схема:** {user_form}")
        
        if user_form == ai_recommended:
            st.success("✅ **Вердикт ШІ:** Чудова схема! Вона ідеально збалансована під гравців у твоїй основі.")
        else:
            st.warning(f"⚠️ **Вердикт ШІ:** Схема не зовсім оптимальна для цих гравців.")
            if user_form == "4-2-4" and (strikers < 2 or wingers < 2):
                st.write("❌ *Причина: Для схеми 4-2-4 тобі не вистачає чистих форвардів або вінгерів у стартовому складі. Рекомендується докупити їх або змінити схему.*")
            elif user_form == "4-3-3" and wingers < 2:
                st.write("❌ *Причина: У тебе мало флангових атакувальних гравців (вінгеров) для якісної гри в 4-3-3.*")
            elif user_form == "4-4-2" and strikers < 2:
                st.write("❌ *Причина: Схема 4-4-2 вимагає двох сильних нападників попереду, а у тебе зараз один або взагалі немає.*")
            else:
                st.write(f"💡 *Порада: Спробуй перевести в основу гравців потрібних позицій або ШІ радить увімкнути тактику `{ai_recommended}`.*")

    # --- БЛОК 3: ТАБЛИЦІ СКЛАДУ (ОСНОВА ТА ЗАМІНА) ---
    st.header("🏟️ Управління складом команди")
    
    # Перетворюємо в датафрейми для чистого табличного виводу
    starters_df = pd.DataFrame(starters)
    bench_df = pd.DataFrame(bench)

    st.subheader("⭐ Стартовий склад (ТОП-11)")
    if not starters_df.empty:
        st.dataframe(starters_df[['short_name', 'player_positions', 'overall', 'potential', 'age']])
        
        # Кнопки дій для основи
        for idx, p in enumerate(starters):
            if st.button(f"⬇️ Відправити на банку: {p['short_name']}", key=f"b_starters_{idx}"):
                for op in st.session_state.custom_players:
                    if op['short_name'] == p['short_name']: op['is_starter'] = False
                st.rerun()
    
    st.write("---")
    st.subheader("🪑 Лава запасних та Резерв")
    if not bench_df.empty:
        st.dataframe(bench_df[['short_name', 'player_positions', 'overall', 'potential', 'age']])
        
        # Кнопки дій для заміни
        for idx, p in enumerate(bench):
            if st.button(f"⬆️ Поставити в основу: {p['short_name']}", key=f"b_bench_{idx}"):
                for op in st.session_state.custom_players:
                    if op['short_name'] == p['short_name']: op['is_starter'] = True
                st.rerun()
    else:
        st.info("На заміні немає нікого.")

    # --- БЛОК 4: ТРАНСФЕРИ З АВТО-РАХУНКОМ БУДЖЕТУ ---
    st.header("🔄 Трансферне вікно клубу")
    t1, t2 = st.tabs(["🛍️ Купити підсилення", "❌ Продати гравця"])
    
    with t1:
        s_name = st.text_input("Пошук гравця на ринку (прізвище):")
        if s_name:
            res = df[df['short_name'].str.contains(s_name, case=False, na=False)].head(3)
            for idx, row in res.iterrows():
                p_price = int(row['value_eur'] * 1.25)
                p_wage = int(row['wage_eur'] * 1.15) if row['wage_eur'] > 0 else 4500
                st.write(f"**{row['short_name']}** ({row['player_positions']}) | OVR: {row['overall']} | Клуб: {row['club_name']}")
                st.markdown(f"💰 Рекомендована ціна покупки: `{p_price:,} €` | Зарплата: `{p_wage:,} €/тиж`")
                
                owned = any(cp['short_name'] == row['short_name'] for cp in st.session_state.custom_players)
                if owned:
                    st.text("✅ Вже є у твоїй коменді")
                else:
                    if st.button(f"🤝 Підписати за {p_price:,} €", key=f"buy_btn_{idx}"):
                        if st.session_state.budget >= p_price:
                            # Віднімаємо від бюджету
                            st.session_state.budget -= p_price
                            np = row.to_dict()
                            np['is_starter'] = False  # Новачок іде на заміну
                            st.session_state.custom_players.append(np)
                            st.success(f"📝 {row['short_name']} підписаний! {p_price:,} € знято з бюджету.")
                            st.rerun()
                        else:
                            st.error("❌ Недостатньо бюджету для цієї покупки! Продай когось спочатку.")
                st.write("---")

    with t2:
        all_names = [p['short_name'] for p in st.session_state.custom_players]
        to_sell = st.selectbox("Обери кого продати:", ["-- Виберіть гравця --"] + all_names)
        if to_sell != "-- Виберіть гравця --":
            # Знаходимо дані гравця для продажу
            p_to_sell_data = next(p for p in st.session_state.custom_players if p['short_name'] == to_sell)
            sell_price = int(p_to_sell_data['value_eur'] * 1.20)  # Продаємо з націнкою 20%
            
            st.warning(f"💡 Ти можеш продати його приблизно за: {sell_price:,} €")
            if st.button(f"💰 Підтвердити продаж і отримати {sell_price:,} €"):
                # Додаємо гроші в бюджет
                st.session_state.budget += sell_price
                st.session_state.custom_players = [p for p in st.session_state.custom_players if p['short_name'] != to_sell]
                st.success(f"📈 {to_sell} проданий! Гроші додані на твій баланс.")
                st.rerun()
