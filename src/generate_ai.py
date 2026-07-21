from datetime import date as _date
from claude import call_claude, parse_json

# 每個等級一組主題池，依日期輪播一個主題，連續 len(pool) 天不重複才循環
LEVEL_SPECS = {
    "A1": {"words": "60-90", "grammar": "極短句、現在式為主 (Presente)",
           "topics": ["家庭成員", "一日三餐", "今天的天氣", "顏色與衣服", "我的房間",
                      "寵物", "數字與時間", "身體部位", "學校用品", "一週七天",
                      "我住的城市", "交通工具", "水果和蔬菜", "我最好的朋友", "我的興趣",
                      "早上的習慣", "週末做什麼", "我的家", "四季", "常喝的飲料"]},
    "A2": {"words": "100-150", "grammar": "簡單連接詞、加入 Pretérito 與 Futuro próximo",
           "topics": ["一次旅行的回憶", "逛街購物", "在餐廳點餐", "假期計畫", "去看醫生",
                      "問路", "喜歡的電影", "做運動", "過節慶", "買衣服的經驗",
                      "描述一個朋友", "童年回憶", "上個週末", "未來的計畫", "找房子",
                      "在機場", "學西班牙語的理由", "一頓難忘的晚餐", "天氣與戶外活動", "我平常的一天"]},
    "B1": {"words": "180-250", "grammar": "從屬子句、各種過去式與條件式",
           "topics": ["理想的工作", "科技如何改變生活", "環境保護", "教育的重要性", "社群媒體的利弊",
                      "健康的生活方式", "住城市還是鄉村", "遠距工作的趨勢", "旅行帶來的成長", "各國的飲食文化",
                      "世代之間的差異", "當志工的意義", "學語言的好方法", "藝術與創意", "過度消費的問題",
                      "都市交通問題", "心理健康", "傳統與現代的拉扯", "多元文化社會", "未來的城市樣貌"]},
}


def _pick_topic(level: str, date: str) -> str:
    """依日期序號輪播主題：連續日期取相鄰主題，len(pool) 天內不重複。"""
    pool = LEVEL_SPECS[level]["topics"]
    try:
        idx = _date.fromisoformat(date).toordinal()
    except ValueError:
        idx = 0
    return pool[idx % len(pool)]


def generate_ai_article(level: str, date: str, caller=call_claude) -> dict:
    spec = LEVEL_SPECS[level]
    topic = _pick_topic(level, date)
    prompt = f"""你是西班牙語教材編寫者。請為 CEFR {level} 程度的學習者寫一篇西班牙語短文。

要求：
- 長度 {spec['words']} 字
- 文法：{spec['grammar']}
- 主題：{topic}
- 全文使用西班牙語（含標點與重音符號）

同時提供：
- translation（整篇短文的繁體中文全文翻譯，通順自然）
- 8 到 10 個文中重點單字，每個含：word（單字）、pos（詞性縮寫）、zh（繁體中文釋義）、example（西語例句）、example_zh（例句的繁體中文翻譯）
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
