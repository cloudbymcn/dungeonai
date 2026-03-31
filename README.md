# 🎮 DungeonAI

**RPG text adventure powered by AI that narrates the story and generates scene images in real-time.**

You describe your actions. The AI Dungeon Master decides what happens, writes the narrative, and draws each scene — all in real-time, running 100% on AWS serverless.

> Built with [Strands Agents SDK](https://strandsagents.com/) + Amazon Bedrock + Nova Canvas — the stack that's defining agentic AI in 2026.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Player (Streamlit)                                     │
│  Text input + scene image + narrative + game state      │
└──────────────────────┬──────────────────────────────────┘
                       │
              ┌────────▼────────┐
              │  Lambda + APIGW │
              └────────┬────────┘
                       │
         ┌─────────────▼──────────────┐
         │  Strands Agent             │
         │  "Dungeon Master"          │
         │  Claude Haiku 4.5          │
         │                            │
         │  Tools:                    │
         │  ├── narrate_story         │
         │  ├── generate_scene        │
         │  └── update_game_state     │
         └──┬──────────┬──────────┬───┘
            │          │          │
     ┌──────▼──┐  ┌────▼────┐  ┌─▼──────────┐
     │ Bedrock │  │  Nova   │  │ DynamoDB   │
     │ Haiku   │  │ Canvas  │  │ Game State │
     └─────────┘  └────┬────┘  └────────────┘
                       │
                  ┌────▼────┐
                  │   S3    │
                  │ Images  │
                  └─────────┘
```

## Stack

| Service | Role | Cost (per session) |
|---|---|---|
| **Strands Agents SDK** | Multi-agent orchestration | Free (open-source) |
| **Claude Haiku 4.5** (Bedrock) | Narrative generation + reasoning | ~$0.002 |
| **Nova Canvas** (Bedrock) | Scene image generation | ~$0.04/image |
| **DynamoDB** | Game state persistence | ~$0.001 |
| **S3** | Generated images storage | ~$0.001 |
| **Lambda + API Gateway** | Serverless backend | Free Tier |
| **Streamlit** | Frontend UI | Free |

**Estimated cost: ~$0.05 per turn, ~$2 for a full 30-turn game session.**

## Project Structure

```
dungeonai/
├── agent/
│   ├── dungeon_master.py      # Strands Agent definition
│   ├── tools/
│   │   ├── narrate_story.py   # Claude Haiku narrative generation
│   │   ├── generate_scene.py  # Nova Canvas image generation
│   │   └── update_state.py    # DynamoDB game state management
│   └── prompts/
│       └── system_prompt.txt  # Dungeon Master personality & rules
├── frontend/
│   └── app.py                 # Streamlit UI
├── infra/
│   └── template.yaml          # SAM/CloudFormation template
├── tests/
│   └── test_agent.py          # Agent integration tests
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Quick Start

```bash
# 1. Clone
git clone https://github.com/cloudbymcn/dungeonai.git
cd dungeonai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure AWS credentials
cp .env.example .env
# Edit .env with your AWS credentials/region

# 4. Run locally
python -m streamlit run frontend/app.py
```

## Prerequisites

- AWS Account with Bedrock model access (Claude Haiku 4.5 + Nova Canvas)
- Python 3.11+
- AWS CLI configured

## Blog Series

This project is documented as a technical series on [Cloud by MCN](https://cloudbymcn.github.io/blog):

1. **"Construí um RPG com IA na AWS por $5"** — Architecture overview and cost breakdown
2. **Strands Agents SDK na prática** — Building the Dungeon Master agent
3. **Nova Canvas para geração de cenas** — Real-time image generation pipeline
4. **Serverless deployment** — Lambda + API Gateway + DynamoDB

## License

MIT

---

**Cloud by MCN** — Building real cloud architectures, one project at a time.
