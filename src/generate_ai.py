from claude import call_claude, parse_json

LEVEL_SPECS = {
    "A1": {"words": "60-90", "grammar": "極短句、現在式為主 (Presente)",
           "topics": "日常：家庭、食物、天氣"},
    "A2": {"words": "100-150", "grammar": "簡單連接詞、加入 Pretérito 與 Futuro próximo",
           "topics": "旅行、購物、興趣"},
    "B1": {"words": "180-250", "grammar": "從屬子句、各種過去式與條件式",
           "topics": "工作、社會議題、表達意見"},
}


def generate_ai_article(level: str, date: str, caller=call_claude) -> dict:
    spec = LEVEL_SPECS[level]
    prompt = f"""你是西班牙語教材編寫者。請為 CEFR {level} 程度的學習者寫一篇西班牙語短文。

要求：
- 長度 {spec['words']} 字
- 文法：{spec['grammar']}
- 主題：{spec['topics']}
- 全文使用西班牙語（含標點與重音符號）

同時提供：
- translation（整篇短文的繁體中文全文翻譯，通順自然）
- 8 到 10 個文中重點單字，每個含：word（單字）、pos（詞性縮寫）、zh（繁體中文釋義）、example（西語例句）
- 5 題西語四選一理解測驗，每題含：q（西語題目）、options（4 個西語選項）、answer（正解索引 0-3）、explain（繁體中文簡短解析）

只回傳 JSON 物件，格式：
{{"title": "...", "text": "...", "translation": "...", "words": [...], "quiz": [...]}}"""
    data = parse_json(caller(prompt, max_tokens=2500), {})
    return {
        "id": f"{date}-{level}-1",
        "source": "ai",
        "level_label": level,
        "title": data.get("title", ""),
        "text": data.get("text", ""),
        "translation": data.get("translation", ""),
        "words": data.get("words", []),
        "quiz": data.get("quiz", []),
    }
