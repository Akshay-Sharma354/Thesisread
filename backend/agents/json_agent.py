"""
Small shared helper: call Claude and force a clean JSON object back.
Every agent in this pipeline is a thin wrapper around this function
with its own system prompt + schema description.
"""
import json
import re
from config import client


def call_json(model: str, system_prompt: str, user_content: str, max_tokens: int = 1024) -> dict:
    """
    Calls the model with a system prompt that demands JSON-only output,
    then defensively parses the response (models occasionally wrap JSON
    in prose or code fences despite instructions).
    """
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt + "\n\nRespond with ONLY a valid JSON object. No preamble, no markdown fences, no explanation outside the JSON.",
        messages=[{"role": "user", "content": user_content}],
    )
    text = "".join(block.text for block in response.content if block.type == "text").strip()

    # Defensive cleanup in case the model wraps the JSON anyway.
    text = re.sub(r"^```json\s*|\s*```$", "", text.strip())
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"Agent did not return parseable JSON. Raw output:\n{text}")
    return json.loads(match.group(0))
