import json
import re
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-6"


def call_claude(prompt: str, max_tokens: int = 1500) -> str:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


def parse_json(text: str, fallback):
    # 優先抓 ```json fenced 區塊，否則抓第一段平衡 JSON
    fenced = re.search(r"```(?:json)?\s*([\[{][\s\S]*?[\]}])\s*```", text)
    candidate = fenced.group(1) if fenced else None
    if candidate is None:
        m = re.search(r"[\[{][\s\S]*[\]}]", text)
        candidate = m.group(0) if m else None
    if candidate is None:
        return fallback
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return fallback
