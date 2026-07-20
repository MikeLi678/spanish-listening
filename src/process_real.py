from claude import call_claude, parse_json


def process_real_article(candidate: dict, date: str, index: int, caller=call_claude) -> dict:
    prompt = f"""以下是一篇西班牙語真實新聞文章。請為進階學習者（CEFR B2–C2）處理它。

原文：
\"\"\"{candidate['text'][:3000]}\"\"\"

請完成：
- 節錄或整理出 250-350 字、語言保持地道的西語段落（text）
- translation（該段的繁體中文全文翻譯，通順自然）
- 判定這段的難度，以範圍標注（level_label），例如「約 B2–C1」
- 一個西語標題（title）
- 8 到 10 個重點單字或慣用語，每個含 word、pos（詞性）、zh（繁體中文釋義）、example（西語例句）、example_zh（例句的繁體中文翻譯）
- 5 題西語四選一理解測驗，每題含 q、options（4 選項）、answer（0-3 索引）、explain（繁體中文解析）

只回傳 JSON 物件：
{{"level_label": "...", "title": "...", "text": "...", "translation": "...", "words": [...], "quiz": [...]}}"""
    data = parse_json(caller(prompt, max_tokens=3000), {})
    return {
        "id": f"{date}-real-{index}",
        "source": "real",
        "level_label": data.get("level_label", "約 B2–C1"),
        "origin_url": candidate["link"],
        "origin_name": candidate["origin_name"],
        "title": data.get("title", candidate["title"]),
        "text": data.get("text", ""),
        "translation": data.get("translation", ""),
        "words": data.get("words", []),
        "quiz": data.get("quiz", []),
    }
