"""
DungeonAI — Streamlit Frontend
RPG text adventure with AI-generated scene images.
Dark fantasy themed UI.
"""

import base64
import streamlit as st
from agent.dungeon_master import create_agent, play_turn, new_session

# --- Page config ---
st.set_page_config(
    page_title="DungeonAI",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Dark Fantasy Theme ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=MedievalSharp&family=Inter:wght@400;500;600&display=swap');

    /* Global dark theme */
    .stApp {
        background: linear-gradient(170deg, #0a0a0f 0%, #12101a 40%, #0d0b14 100%);
        color: #c9c2d4;
    }

    /* Hide default Streamlit header/footer */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    footer { display: none !important; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0e0c16 0%, #161222 100%) !important;
        border-right: 1px solid #2a2340;
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #b8b0c8;
    }

    /* Title */
    .game-title {
        font-family: 'MedievalSharp', cursive;
        text-align: center;
        font-size: 2.8rem;
        background: linear-gradient(135deg, #d4a44c 0%, #f0d68a 50%, #d4a44c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: none;
        margin-bottom: 0;
        letter-spacing: 3px;
    }
    .game-subtitle {
        text-align: center;
        color: #6b6280;
        font-size: 0.85rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-top: -8px;
        margin-bottom: 24px;
    }

    /* Scene image container */
    .scene-frame {
        position: relative;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #2a2340;
        box-shadow: 0 0 40px rgba(100, 60, 180, 0.15), 0 8px 32px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    .scene-frame img {
        border-radius: 12px;
        width: 100%;
        display: block;
    }
    .scene-placeholder {
        background: linear-gradient(135deg, #1a1525 0%, #0f0d18 100%);
        border-radius: 12px;
        height: 280px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #3d3555;
        font-size: 1rem;
        border: 1px dashed #2a2340;
    }

    /* Narrative text */
    .narrative-box {
        background: linear-gradient(135deg, #15122000, #1a1530aa);
        border-left: 3px solid #7c5cbf;
        padding: 20px 24px;
        border-radius: 0 10px 10px 0;
        font-size: 1.05rem;
        line-height: 1.9;
        color: #d4cee0;
        margin: 16px 0;
        font-family: 'Inter', sans-serif;
    }

    /* Action buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1e1a2e 0%, #252040 100%) !important;
        color: #c9b8e8 !important;
        border: 1px solid #3d3260 !important;
        border-radius: 8px !important;
        padding: 12px 20px !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        text-align: left !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2a2445 0%, #352d55 100%) !important;
        border-color: #7c5cbf !important;
        color: #e8dff5 !important;
        box-shadow: 0 0 15px rgba(124, 92, 191, 0.2) !important;
        transform: translateX(4px);
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #5c3d8f 0%, #7c5cbf 100%) !important;
        color: #fff !important;
        border: 1px solid #9070d0 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #7c5cbf 0%, #9070d0 100%) !important;
        box-shadow: 0 0 20px rgba(124, 92, 191, 0.4) !important;
    }

    /* Form input */
    .stTextInput > div > div > input {
        background: #15122080 !important;
        color: #d4cee0 !important;
        border: 1px solid #2a2340 !important;
        border-radius: 8px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #7c5cbf !important;
        box-shadow: 0 0 10px rgba(124, 92, 191, 0.2) !important;
    }

    /* Stat bars */
    .stat-bar-container {
        margin: 8px 0;
    }
    .stat-bar-label {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        margin-bottom: 4px;
        color: #8a8098;
    }
    .stat-bar-track {
        background: #1a1530;
        border-radius: 6px;
        height: 10px;
        overflow: hidden;
        border: 1px solid #2a234080;
    }
    .stat-bar-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.5s ease;
    }
    .hp-bar { background: linear-gradient(90deg, #8b2020, #d44040); }
    .hp-bar-low { background: linear-gradient(90deg, #8b2020, #ff4040); animation: pulse-red 1.5s infinite; }
    .xp-bar { background: linear-gradient(90deg, #2050a0, #4080e0); }
    .gold-bar { background: linear-gradient(90deg, #8a6d20, #d4a44c); }

    @keyframes pulse-red {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }

    /* Inventory panel */
    .inventory-panel {
        background: #12101a;
        border: 1px solid #2a2340;
        border-radius: 8px;
        padding: 12px 16px;
    }
    .inventory-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 0;
        border-bottom: 1px solid #1a1530;
        font-size: 0.9rem;
        color: #b8b0c8;
    }
    .inventory-item:last-child { border-bottom: none; }

    /* Section headers */
    .section-header {
        font-family: 'MedievalSharp', cursive;
        color: #d4a44c;
        font-size: 1.1rem;
        letter-spacing: 1px;
        margin: 16px 0 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Location badge */
    .location-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #1a153080;
        border: 1px solid #2a2340;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.8rem;
        color: #8a8098;
    }

    /* Turn log */
    .turn-log-entry {
        font-size: 0.78rem;
        color: #5a5270;
        padding: 4px 0;
        border-bottom: 1px solid #1a153040;
    }
    .turn-log-entry strong {
        color: #7c6b9f;
    }

    /* Stats inline */
    .stats-row {
        display: flex;
        gap: 16px;
        justify-content: center;
        margin: 12px 0;
    }
    .stat-chip {
        display: flex;
        align-items: center;
        gap: 6px;
        background: #15122080;
        border: 1px solid #2a234060;
        border-radius: 8px;
        padding: 6px 14px;
        font-size: 0.85rem;
    }
    .stat-chip .val {
        font-weight: 600;
        color: #e8dff5;
    }

    /* Action prompt */
    .action-prompt {
        font-family: 'MedievalSharp', cursive;
        color: #9080b0;
        font-size: 1.1rem;
        margin: 16px 0 10px;
    }

    /* Game over overlay */
    .game-over-box {
        background: linear-gradient(135deg, #2a0a0a, #1a0505);
        border: 1px solid #5a2020;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        margin: 20px 0;
    }
    .game-over-box h2 {
        font-family: 'MedievalSharp', cursive;
        color: #d44040;
        font-size: 2rem;
    }

    /* Welcome screen */
    .welcome-box {
        text-align: center;
        max-width: 600px;
        margin: 60px auto;
        padding: 40px;
    }
    .welcome-lore {
        color: #6b6280;
        font-size: 0.95rem;
        line-height: 1.8;
        margin: 20px 0 30px;
        font-style: italic;
    }

    /* Divider */
    hr {
        border: none;
        border-top: 1px solid #2a234060;
        margin: 16px 0;
    }

    /* Metric override */
    [data-testid="stMetric"] {
        background: transparent !important;
    }
    [data-testid="stMetricLabel"] {
        color: #6b6280 !important;
    }
    [data-testid="stMetricValue"] {
        color: #d4cee0 !important;
    }

    /* Progress bar override */
    .stProgress > div > div > div {
        background: #1a1530 !important;
    }

    /* Loading overlay */
    .loading-overlay {
        background: linear-gradient(135deg, #1a153090, #0a0a0f90);
        border: 1px solid #3d3260;
        border-radius: 12px;
        padding: 40px 24px;
        text-align: center;
        margin: 20px 0;
    }
    .loading-text {
        font-family: 'MedievalSharp', cursive;
        color: #d4a44c;
        font-size: 1.3rem;
        margin-bottom: 12px;
    }
    .loading-sub {
        color: #6b6280;
        font-size: 0.85rem;
        font-style: italic;
    }
    .loading-dots::after {
        content: '';
        animation: dots 1.5s steps(4, end) infinite;
    }
    @keyframes dots {
        0% { content: ''; }
        25% { content: '.'; }
        50% { content: '..'; }
        75% { content: '...'; }
    }
    .loading-spinner {
        display: inline-block;
        width: 32px;
        height: 32px;
        border: 3px solid #2a2340;
        border-top: 3px solid #7c5cbf;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 16px;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* Disabled action area */
    .actions-disabled {
        opacity: 0.3;
        pointer-events: none;
    }

    /* Hide streamlit default elements */
    .stDeployButton { display: none !important; }
    #MainMenu { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- Session state init ---
def init_session():
    if "initialized" not in st.session_state:
        st.session_state.initialized = False
        st.session_state.session_id = None
        st.session_state.agent = None
        st.session_state.game_state = None
        st.session_state.narrative = (
            "As Cavernas de Eldrath se erguem diante de você. "
            "A entrada escura exala um ar frio e úmido. "
            "Cristais fracos pulsam nas paredes de pedra, "
            "como se a própria montanha respirasse.\n\n"
            "Você segura sua tocha com firmeza e dá o primeiro passo."
        )
        st.session_state.image_b64 = None
        st.session_state.suggested_actions = [
            "Entrar na caverna com a tocha erguida",
            "Examinar os cristais na entrada",
            "Procurar pegadas no chão",
        ]
        st.session_state.turn_log = []
        st.session_state.processing = False
        st.session_state.pending_action = None


init_session()


# --- Helper: render stat bar ---
def render_stat_bar(label, current, maximum, bar_class, icon=""):
    pct = max(0, min(100, (current / maximum) * 100))
    css_class = bar_class
    if bar_class == "hp-bar" and pct <= 25:
        css_class = "hp-bar-low"
    st.markdown(
        f"""
        <div class="stat-bar-container">
            <div class="stat-bar-label">
                <span>{icon} {label}</span>
                <span>{current}/{maximum}</span>
            </div>
            <div class="stat-bar-track">
                <div class="stat-bar-fill {css_class}" style="width:{pct}%"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --- Start game ---
def start_game():
    with st.spinner("⚔️ Preparando a aventura..."):
        st.session_state.agent = create_agent()
        st.session_state.session_id = new_session()
        st.session_state.game_state = {
            "hp": 100,
            "gold": 10,
            "xp": 0,
            "level": 1,
            "inventory": ["Espada de ferro", "Tocha"],
            "location": "Entrada das Cavernas de Eldrath",
            "turn": 0,
            "scene_history": [],
            "status": "active",
        }
        st.session_state.initialized = True


# --- Queue an action (instant — just sets state and reruns) ---
def queue_action(action: str):
    st.session_state.pending_action = action
    st.session_state.processing = True


# --- Process pending action (runs at top of rerun with visible feedback) ---
if st.session_state.pending_action and st.session_state.processing:
    action = st.session_state.pending_action

    # Show loading screen immediately
    st.markdown(
        f"""
        <div class="loading-overlay">
            <div class="loading-spinner"></div>
            <div class="loading-text">O Dungeon Master narra<span class="loading-dots"></span></div>
            <div class="loading-sub">"{action[:80]}"</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        result = play_turn(
            agent=st.session_state.agent,
            session_id=st.session_state.session_id,
            player_action=action,
        )
        st.session_state.narrative = result["narrative"]
        st.session_state.image_b64 = result["image_base64"]
        st.session_state.game_state = result["game_state"]
        st.session_state.suggested_actions = result["suggested_actions"]
        turn_num = result["game_state"].get("turn", 0)
        st.session_state.turn_log.insert(
            0, f"<strong>Turno {turn_num}</strong> — {action[:60]}"
        )
    except Exception as e:
        st.session_state._last_error = str(e)

    st.session_state.pending_action = None
    st.session_state.processing = False
    st.rerun()

# Show error from previous turn if any
if hasattr(st.session_state, "_last_error") and st.session_state._last_error:
    st.error(f"Erro no turno anterior: {st.session_state._last_error}")
    st.session_state._last_error = None


# ============================
# WELCOME SCREEN
# ============================
if not st.session_state.initialized:
    st.markdown(
        """
        <div class="welcome-box">
            <div class="game-title">DungeonAI</div>
            <div class="game-subtitle">As Cavernas de Eldrath</div>
            <div class="welcome-lore">
                Nas profundezas da montanha de Eldrath, um reino esquecido aguarda.
                Cristais antigos guardam o poder de uma civilização perdida,
                e criaturas das sombras protegem tesouros inimagináveis.
                Sua jornada começa agora.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "⚔️  Iniciar Aventura", type="primary", use_container_width=True
        ):
            start_game()
            st.rerun()
    st.stop()

# ============================
# GAME HEADER
# ============================
st.markdown('<div class="game-title">DungeonAI</div>', unsafe_allow_html=True)

gs = st.session_state.game_state
if gs:
    st.markdown(
        f'<div style="text-align:center;margin-bottom:16px">'
        f'<span class="location-badge">📍 {gs.get("location", "???")}</span>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # Inline stats
    st.markdown(
        f"""
        <div class="stats-row">
            <div class="stat-chip">❤️ <span class="val">{gs['hp']}</span></div>
            <div class="stat-chip">💰 <span class="val">{gs['gold']}</span></div>
            <div class="stat-chip">⭐ <span class="val">{gs['xp']}</span></div>
            <div class="stat-chip">🗡️ Nv <span class="val">{gs['level']}</span></div>
            <div class="stat-chip">📜 Turno <span class="val">{gs.get('turn', 0)}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<hr>", unsafe_allow_html=True)

# ============================
# MAIN LAYOUT
# ============================
col_main, col_side = st.columns([3, 1], gap="large")

with col_main:
    # --- Scene image ---
    if st.session_state.image_b64:
        st.markdown('<div class="scene-frame">', unsafe_allow_html=True)
        image_bytes = base64.b64decode(st.session_state.image_b64)
        st.image(image_bytes, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="scene-placeholder">'
            "🎨 A cena será revelada após sua primeira ação..."
            "</div>",
            unsafe_allow_html=True,
        )

    # --- Narrative ---
    narrative_html = st.session_state.narrative.replace("\n", "<br>")
    st.markdown(
        f'<div class="narrative-box">{narrative_html}</div>',
        unsafe_allow_html=True,
    )

    # --- Game Over ---
    if gs and gs.get("status") == "dead":
        st.markdown(
            """
            <div class="game-over-box">
                <h2>☠️ Você Pereceu</h2>
                <p style="color:#8a5050">As sombras de Eldrath consomem sua memória...</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_r1, col_r2, col_r3 = st.columns([1, 2, 1])
        with col_r2:
            if st.button(
                "⚔️ Tentar Novamente", type="primary", use_container_width=True
            ):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        st.stop()

    # --- Action choices ---
    if st.session_state.suggested_actions and not st.session_state.processing:
        st.markdown(
            '<div class="action-prompt">O que você faz?</div>',
            unsafe_allow_html=True,
        )
        for i, action in enumerate(st.session_state.suggested_actions):
            letter = chr(65 + i)
            if st.button(
                f"  {letter}.  {action}",
                key=f"choice_{i}",
                use_container_width=True,
            ):
                queue_action(action)
                st.rerun()

    # --- Custom action ---
    st.markdown("<hr>", unsafe_allow_html=True)
    with st.form("action_form", clear_on_submit=True):
        custom_action = st.text_input(
            "✍️ Ou descreva sua própria ação:",
            placeholder="Ex: Investigo os cristais púrpura com cuidado...",
        )
        submitted = st.form_submit_button(
            "⚔️ Agir",
            type="primary",
            use_container_width=True,
        )
        if submitted and custom_action:
            queue_action(custom_action)
            st.rerun()


# ============================
# SIDEBAR — Character Panel
# ============================
with col_side:
    if gs:
        # Character stats
        st.markdown(
            '<div class="section-header">⚔️ Personagem</div>',
            unsafe_allow_html=True,
        )

        render_stat_bar("HP", gs["hp"], 100, "hp-bar", "❤️")
        xp_in_level = gs["xp"] % 100
        render_stat_bar("XP", xp_in_level, 100, "xp-bar", "⭐")
        render_stat_bar("Gold", min(gs["gold"], 100), 100, "gold-bar", "💰")

        st.markdown("<hr>", unsafe_allow_html=True)

        # Inventory
        st.markdown(
            '<div class="section-header">🎒 Inventário</div>',
            unsafe_allow_html=True,
        )

        if gs.get("inventory"):
            items_html = ""
            item_icons = {
                "Espada": "⚔️",
                "Tocha": "🔥",
                "Poção": "🧪",
                "Escudo": "🛡️",
                "Arco": "🏹",
                "Chave": "🔑",
                "Mapa": "🗺️",
                "Anel": "💍",
                "Amuleto": "📿",
                "Ouro": "💰",
            }
            for item in gs["inventory"]:
                icon = "📦"
                for keyword, emoji in item_icons.items():
                    if keyword.lower() in item.lower():
                        icon = emoji
                        break
                items_html += (
                    f'<div class="inventory-item">{icon} {item}</div>'
                )
            st.markdown(
                f'<div class="inventory-panel">{items_html}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="inventory-panel">'
                '<div class="inventory-item" style="color:#3d3555">'
                "Inventário vazio</div></div>",
                unsafe_allow_html=True,
            )

        st.markdown("<hr>", unsafe_allow_html=True)

        # Turn log
        st.markdown(
            '<div class="section-header">📜 Histórico</div>',
            unsafe_allow_html=True,
        )

        if st.session_state.turn_log:
            for entry in st.session_state.turn_log[:10]:
                st.markdown(
                    f'<div class="turn-log-entry">{entry}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="turn-log-entry" style="color:#3d3555">'
                "Nenhuma ação registrada</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<hr>", unsafe_allow_html=True)

        # Reset
        if st.button("🔄 Reiniciar Jogo", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
