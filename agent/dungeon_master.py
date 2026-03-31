"""
DungeonAI — Strands Agent Dungeon Master

Orchestrates narrative generation, scene image creation,
and game state management for a text adventure RPG.
"""

import uuid
from pathlib import Path
from strands import Agent
from strands.models.bedrock import BedrockModel

from agent.tools.narrate_story import narrate_story
from agent.tools.generate_scene import generate_scene
from agent.tools.update_state import update_game_state

SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "system_prompt.txt").read_text()


def create_agent() -> Agent:
    """Create and return the Dungeon Master agent."""
    model = BedrockModel(
        model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
        region_name="us-east-1",
    )

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[narrate_story, generate_scene, update_game_state],
    )

    return agent


def play_turn(agent: Agent, session_id: str, player_action: str) -> dict:
    """Execute a single game turn.

    1. Load current game state from DynamoDB
    2. Generate narrative based on player action
    3. Generate scene image from the narrative
    4. Update and persist game state
    5. Return everything to the frontend

    Args:
        agent: The Strands Agent instance
        session_id: Current game session ID
        player_action: What the player wants to do

    Returns:
        dict with narrative, image, game_state, and suggested_actions
    """
    game_state = update_game_state(
        session_id=session_id,
    )

    story = narrate_story(
        player_action=player_action,
        game_state=game_state,
        scene_history=game_state.get("scene_history", []),
    )

    scene = generate_scene(
        image_prompt=story["image_prompt"],
        session_id=session_id,
    )

    updated_state = update_game_state(
        session_id=session_id,
        state_changes=story["state_changes"],
    )

    scene_summary = story["narrative"][:120]
    history = updated_state.get("scene_history", [])
    history.append(scene_summary)
    if len(history) > 5:
        history = history[-5:]
    updated_state["scene_history"] = history

    update_game_state(
        session_id=session_id,
        state_changes={"hp_delta": 0, "gold_delta": 0, "xp_delta": 0},
    )

    return {
        "narrative": story["narrative"],
        "image_base64": scene["image_base64"],
        "image_s3_key": scene["s3_key"],
        "game_state": updated_state,
        "suggested_actions": story["suggested_actions"],
    }


def new_session() -> str:
    """Start a new game session and return the session ID."""
    session_id = uuid.uuid4().hex[:12]
    update_game_state(session_id=session_id)
    return session_id


if __name__ == "__main__":
    agent = create_agent()
    sid = new_session()
    print(f"Nova sessão: {sid}\n")

    result = play_turn(agent, sid, "Olho ao redor da entrada da caverna")
    print(result["narrative"])
    print(f"\nHP: {result['game_state']['hp']}")
    print(f"Sugestões: {result['suggested_actions']}")
