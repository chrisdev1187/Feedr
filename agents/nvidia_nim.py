"""
NVIDIA NIM Provider — 136 free models, one API key
Get key: https://build.nvidia.com/settings/api-keys
"""

import os
from openai import OpenAI

NVIDIA_BASE = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODELS = {
    "fast_code": "qwen/qwen3-coder-480b-a35b-instruct",
    "reasoning": "moonshotai/kimi-k2-instruct", 
    "heavy": "meta/llama-3.1-405b-instruct",
    "creative": "mistralai/magistral-small-2506"
}

def nvidia_chat(prompt: str, model_key: str = "fast_code") -> str:
    """
    Call NVIDIA NIM with automatic model selection.
    Requires NVIDIA_API_KEY environment variable.
    """
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        return "Error: NVIDIA_API_KEY not found in environment."

    client = OpenAI(
        base_url=NVIDIA_BASE,
        api_key=api_key
    )
    try:
        response = client.chat.completions.create(
            model=NVIDIA_MODELS.get(model_key, NVIDIA_MODELS["fast_code"]),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling NVIDIA NIM: {e}"
