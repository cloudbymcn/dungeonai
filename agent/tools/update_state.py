import json
from datetime import datetime, timezone
import boto3
from strands import tool

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("dungeonai-game-sessions")


def _default_state() -> dict:
    """Return a fresh game state for new sessions."""
    return {
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


@tool
def update_game_state(session_id: str, state_changes: dict = None) -> dict:
    """Load, update, and persist the game state in DynamoDB.

    If no state_changes are provided, returns the current state (or creates a new one).

    Args:
        session_id: Unique game session identifier
        state_changes: Changes to apply (hp_delta, gold_delta, xp_delta, new_items, removed_items, new_location)

    Returns:
        The updated game state dict
    """
    try:
        response = table.get_item(Key={"session_id": session_id})
        state = response.get("Item", {}).get("game_state")
        if state:
            state = json.loads(state) if isinstance(state, str) else state
        else:
            state = _default_state()
    except Exception:
        state = _default_state()

    if state_changes:
        state["hp"] = max(0, min(100, state["hp"] + state_changes.get("hp_delta", 0)))
        state["gold"] = max(0, state["gold"] + state_changes.get("gold_delta", 0))
        state["xp"] += state_changes.get("xp_delta", 0)

        new_level = 1 + state["xp"] // 100
        if new_level > state["level"]:
            state["level"] = new_level

        for item in state_changes.get("new_items", []):
            if item and item not in state["inventory"]:
                state["inventory"].append(item)

        for item in state_changes.get("removed_items", []):
            if item in state["inventory"]:
                state["inventory"].remove(item)

        if state_changes.get("new_location"):
            state["location"] = state_changes["new_location"]

        state["turn"] += 1

        if state["hp"] <= 0:
            state["status"] = "dead"

    table.put_item(
        Item={
            "session_id": session_id,
            "game_state": json.dumps(state, ensure_ascii=False),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    return state
