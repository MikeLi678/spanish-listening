import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from generate_ai import generate_ai_article, LEVEL_SPECS
from schema import validate_article

_FAKE = json.dumps({
    "title": "Mi día",
    "text": "Yo como pan por la mañana.",
    "words": [{"word": "pan", "pos": "n.m.", "zh": "麵包", "example": "Como pan."}],
    "quiz": [{"q": "¿Qué come?", "options": ["pan", "agua", "sol", "casa"],
              "answer": 0, "explain": "文中 como pan。"}],
})


def test_specs_cover_low_levels():
    assert set(LEVEL_SPECS) == {"A1", "A2", "B1"}


def test_generate_returns_valid_article():
    art = generate_ai_article("A1", "2026-07-18", caller=lambda p, max_tokens=1500: _FAKE)
    assert validate_article(art) == []
    assert art["source"] == "ai"
    assert art["level_label"] == "A1"
    assert art["id"].startswith("2026-07-18-A1")
