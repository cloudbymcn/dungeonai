"""
DungeonAI — Streamlit Frontend
RPG text adventure with AI-generated scene images.
"""

import base64
import streamlit as st
from agent.dungeon_master import create_agent, play_turn, new_session

# --- Page config ---
st.set_page_config(
    page_title="DungeonAI",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown(
    """
    <style>
    .narrative-text {
        font-size: 1.1rem;
        line-height: 1.8;
        padding: 1rem 0;
    }
    .scene-image {
        border-radius: 12px;
        width: 100%;
    }
    .stat-label {
        color: #888;
        font-size: 0.85rem;
    }
    .stat-value {
        font-size: 1.1rem;
        font-weight: 600;
    }
    .log-entry {
        font-size: 0.8rem;
        color: #999;
        padding: 2px 0;
    }
    .choice-btn {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- Session state init ---
def init_session():
    """Initialize all session state variables."""
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


init_session()


# --- Start game ---
def start_game():
    """Create agent and start a new game session."""
    with st.spinner("Preparando a aventura..."):
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


# --- Process turn ---
def process_action(action: str):
    """Send player action to the agent and update state."""
    st.session_state.processing = True

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
            0, f"**Turno {turn_num}** — {action[:60]}"
        )

    except Exception as e:
        st.error(f"Erro no turno: {e}")

    st.session_state.processing = False


# --- Header ---
st.markdown("## DungeonAI")

if not st.session_state.initialized:
    st.markdown(
        "Um RPG text adventure com IA que narra a história "
        "e gera as cenas em imagem — tudo rodando na AWS."
    )
    if st.button("Iniciar aventura", type="primary", use_container_width=True):
        start_game()
        st.rerun()
    st.stop()

# --- Status badges ---
gs = st.session_state.game_state
if gs:
    cols = st.columns([1, 1, 1, 1, 3])
    cols[0].metric("HP", f"{gs['hp']}/100")
    cols[1].metric("Gold", gs["gold"])
    cols[2].metric("XP", gs["xp"])
    cols[3].metric("Nivel", gs["level"])
    cols[4].markdown(
        f"<span style='color:#888;font-size:0.85rem'>"
        f"📍 {gs.get('location', '???')}</span>",
        unsafe_allow_html=True,
    )

st.divider()

# --- Main layout ---
col_main, col_side = st.columns([3, 1])

with col_main:
    # Scene image
    if st.session_state.image_b64:
        image_bytes = base64.b64decode(st.session_state.image_b64)
        st.image(image_bytes, use_container_width=True)
    else:
        st.markdown(
            "<div style='background:#f0f0f0;border-radius:12px;"
            "height:200px;display:flex;align-items:center;"
            "justify-content:center;color:#aaa'>"
            "A cena será gerada após sua primeira ação"
            "</div>",
            unsafe_allow_html=True,
        )

    # Narrative
    st.markdown(
        f"<div class='narrative-text'>{st.session_state.narrative}</div>",
        unsafe_allow_html=True,
    )

    # Suggested actions as buttons
    if st.session_state.suggested_actions and not st.session_state.processing:
        st.markdown("**O que você faz?**")
        for i, action in enumerate(st.session_state.suggested_actions):
            label = f"{chr(65 + i)}. {action}"
            if st.button(label, key=f"choice_{i}", use_container_width=True):
                process_action(action)
                st.rerun()

    # Free input
    st.markdown("---")
    with st.form("action_form", clear_on_submit=True):
        custom_action = st.text_input(
            "Ou digite sua própria ação:",
            placeholder="Ex: Investigo os cristais púrpura com cuidado...",
        )
        submitted = st.form_submit_button(
            "Agir", type="primary", use_container_width=True
        )
        if submitted and custom_action:
            process_action(custom_action)
            st.rerun()

# --- Sidebar ---
with col_side:
    if gs:
        # HP bar
        st.markdown("**Status**")
        st.progress(gs["hp"] / 100, text=f"HP {gs['hp']}/100")
        xp_in_level = gs["xp"] % 100
        st.progress(xp_in_level / 100, text=f"XP {xp_in_level}/100")

        # Stats
        st.markdown(
            f"Força **14** · Destreza **12** · Int **10**"
        )

        st.divider()

        # Inventory
        st.markdown("**Inventário**")
        if gs.get("inventory"):
            for item in gs["inventory"]:
                st.markdown(f"- {item}")
        else:
            st.markdown("*Vazio*")

        st.divider()

        # Turn log
        st.markdown("**Log**")
        for entry in st.session_state.turn_log[:8]:
            st.markdown(
                f"<div class='log-entry'>{entry}</div>",
                unsafe_allow_html=True,
            )

        st.divider()

        # Game over check
        if gs.get("status") == "dead":
            st.error("Você morreu! A aventura acabou.")
            if st.button("Nova aventura", type="primary"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        # Reset button
        if st.button("Reiniciar jogo"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
