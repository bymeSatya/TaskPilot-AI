import os, requests

GROQ_API = "https://api.groq.com/openai/v1/chat/completions"
SYSTEM = (
 "You are TaskPilot AI, a focused assistant for Snowflake and Matillion tasks. "
 "Provide step-by-step guidance, SQL samples, Matillion orchestration tips, and troubleshooting."
)

def groq_chat(messages, model="llama-3.1-70b-versatile", temperature=0.2):
    key = os.getenv("groq_api_key") or os.getenv("GROQ_API_KEY")
    if not key:
        return "Set groq_api_key in Streamlit secrets to enable AI guidance."
    headers = {"Authorization": f"Bearer {key}"}
    payload = {"model": model, "messages": [{"role":"system","content":SYSTEM}] + messages, "temperature": temperature}
    r = requests.post(GROQ_API, json=payload, headers=headers, timeout=60)
    if r.status_code != 200:
        return f"Groq API error: {r.status_code} {r.text[:200]}"
    return r.json()["choices"][0]["message"]["content"].strip()