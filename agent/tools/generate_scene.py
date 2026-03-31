import json
import base64
import uuid
import boto3
from strands import tool

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
s3 = boto3.client("s3", region_name="us-east-1")

IMAGE_MODEL_ID = "amazon.titan-image-generator-v2:0"
S3_BUCKET = "dungeonai-scenes"


@tool
def generate_scene(image_prompt: str, session_id: str) -> dict:
    """Generate a scene image based on the narrative description.

    Args:
        image_prompt: English description of the scene to generate (from narrate_story)
        session_id: Current game session ID for organizing images in S3

    Returns:
        dict with s3_key and image_bytes (base64) of the generated scene
    """
    styled_prompt = (
        f"{image_prompt}, "
        "dark fantasy art style, "
        "detailed environment, "
        "dramatic lighting, "
        "painterly illustration, "
        "no text, no UI elements, no people"
    )

    body = json.dumps(
        {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {"text": styled_prompt},
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": "standard",
                "cfgScale": 7.0,
                "height": 768,
                "width": 1280,
                "seed": 0,
            },
        }
    )

    response = bedrock.invoke_model(
        modelId=IMAGE_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=body,
    )

    result = json.loads(response["body"].read())
    image_b64 = result["images"][0]

    image_key = f"sessions/{session_id}/{uuid.uuid4().hex[:8]}.png"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=image_key,
        Body=base64.b64decode(image_b64),
        ContentType="image/png",
    )

    return {
        "s3_key": image_key,
        "image_base64": image_b64,
    }
