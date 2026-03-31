import json
import boto3
from strands import tool

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

MODEL_ID = "us.anthropic.claude-3-5-haiku-20241022-v1:0"


@tool
def narrate_story(
    player_action: str,
    game_state: dict,
    scene_history: list[str] = None,
) -> dict:
    """Generate the next narrative beat based on the player's action and current game state.

    Args:
        player_action: What the player wants to do (e.g. "I enter the dark cave with my torch")
        game_state: Current game state with hp, gold, xp, level, inventory, location
        scene_history: List of the last 3 scene summaries for continuity

    Returns:
        dict with narrative text, image prompt, updated game state, and suggested actions
    """
    history_context = ""
    if scene_history:
        history_context = "Cenas anteriores:\n" + "\n".join(
            f"- {s}" for s in scene_history[-3:]
        )

    prompt = f"""Você é o Dungeon Master. Baseado na ação do jogador e no estado atual, narre o próximo acontecimento.

Estado atual do jogo:
- HP: {game_state.get('hp', 100)}/100
- Gold: {game_state.get('gold', 10)}
- XP: {game_state.get('xp', 0)}
- Level: {game_state.get('level', 1)}
- Inventário: {json.dumps(game_state.get('inventory', []), ensure_ascii=False)}
- Localização: {game_state.get('location', 'Entrada das Cavernas de Eldrath')}

{history_context}

Ação do jogador: {player_action}

Responda APENAS com JSON válido (sem markdown, sem ```):
{{
    "narrative": "Narrativa em português, 2-4 parágrafos, segunda pessoa",
    "image_prompt": "One English sentence describing the visual scene, fantasy art style",
    "state_changes": {{
        "hp_delta": 0,
        "gold_delta": 0,
        "xp_delta": 0,
        "new_items": [],
        "removed_items": [],
        "new_location": "nome do local atual ou novo"
    }},
    "suggested_actions": ["ação 1", "ação 2", "ação 3"]
}}"""

    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 1024, "temperature": 0.8},
    )

    raw = response["output"]["message"]["content"][0]["text"]

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "narrative": raw,
            "image_prompt": "A mysterious dark fantasy cave with glowing crystals, atmospheric lighting",
            "state_changes": {
                "hp_delta": 0,
                "gold_delta": 0,
                "xp_delta": 0,
                "new_items": [],
                "removed_items": [],
                "new_location": game_state.get("location", "Desconhecido"),
            },
            "suggested_actions": [
                "Explorar os arredores",
                "Voltar pelo caminho anterior",
                "Descansar por um momento",
            ],
        }

    return result
