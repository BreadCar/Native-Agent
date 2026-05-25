import os
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv

if load_dotenv(find_dotenv()):
    print("Environment variables loaded successfully.")

def call_api(prompt: str):
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_API_BASE_URL")
    model = os.getenv("MODEL")
    sys_prompt = os.getenv("SYS_PROMPT", "You are a helpful assistant.")

    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    if not base_url:
        raise ValueError("OPENAI_API_BASE_URL environment variable not set.")
    if not model:
        raise ValueError("MODEL environment variable not set.")

    client = OpenAI(api_key = api_key, base_url = base_url)
    response = client.chat.completions.create(
        model = model,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()

    