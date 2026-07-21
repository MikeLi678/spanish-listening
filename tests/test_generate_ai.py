import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from generate_ai import generate_ai_article, LEVEL_SPECS, _pick_topic
from schema import validate_article

_FAKE = json.dumps({
    "title": "Mi día",
    "text": "Yo como pan por la mañana.",
    "translation": "我早上吃麵包。",
    "words": [{"word": "pan", "pos": "n.m.", "zh": "麵包", "example": "Como pan."}],
    "quiz": [{"q": "¿Qué come?", "options": ["pan", "agua", "sol", "casa"],
              "answer": 0, "explain": "文中 como pan。"}],
})


def test_specs_cover_low_levels():
    assert set(LEVEL_SPECS) == {"A1", "A2", "B1"}


def test_pick_topic_varies_by_date_and_is_deterministic():
    # 連續兩天不同主題
    assert _pick_topic("A1", "2026-07-22") != _pick_topic("A1", "2026-07-23")
    # 同日期穩定
    assert _pick_topic("A1", "2026-07-22") == _pick_topic("A1", "2026-07-22")
    # 一整個池長度內每天都不重複
    seen = [_pick_topic("B1", f"2026-07-{d:02d}") for d in range(1, 21)]
    assert len(set(seen)) == 20


def test_generate_returns_valid_article():
    art = generate_ai_article("A1", "2026-07-18", caller=lambda p, max_tokens=1500: _FAKE)
    assert validate_article(art) == []
    assert art["source"] == "ai"
    assert art["level_label"] == "A1"
    assert art["id"].startswith("2026-07-18-A1")
    assert art["translation"] == "我早上吃麵包。"
