"""
NVIDIA NIM Provider — 136 free models, one API key
Get key: https://build.nvidia.com/settings/api-keys
"""

from openai import OpenAI

NVIDIA_BASE = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODELS = {
    "fast_code": "qwen/qwen3-coder-480b-a35b-instruct",
    "reasoning": "moonshotai/kimi-k2-instruct", 
    "heavy": "meta/llama-3.1-405b-instruct",
    "creative": "mistralai/magistral-small-2506"
}

def nvidia_chat(prompt: str, model_key: str = "fast_code") -> str:
    """Call NVIDIA NIM with automatic model selection"""
    client = OpenAI(
        base_url=NVIDIA_BASE,
        api_key=os.getenv("NVIDIA_API_KEY")  # Get from build.nvidia.com
    )
    response = client.chat.completions.create(
        model=NVIDIA_MODELS[model_key],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    return response.choices[0].message.content