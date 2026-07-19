import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from schema import validate_article


def _valid_article():
    return {
        "id": "2026-07-18-A1-1",
        "source": "ai",
        "level_label": "A1",
        "title": "Mi familia",
        "text": "Yo tengo una familia grande.",
        "words": [{"word": "familia", "pos": "n.f.", "zh": "家庭",
                   "example": "Mi familia es grande."}],
        "quiz": [{"q": "¿Cómo es la familia?",
                  "options": ["grande", "pequeña", "nueva", "vieja"],
                  "answer": 0, "explain": "文中說 grande。"}],
    }


def test_valid_article_passes():
    assert validate_article(_valid_article()) == []


def test_missing_field_reported():
    a = _valid_article(); del a["title"]
    assert any("title" in e for e in validate_article(a))


def test_empty_words_reported():
    a = _valid_article(); a["words"] = []
    assert any("words" in e for e in validate_article(a))


def test_answer_out_of_range_reported():
    a = _valid_article(); a["quiz"][0]["answer"] = 9
    assert any("answer" in e for e in validate_article(a))


def test_real_article_requires_origin():
    a = _valid_article(); a["source"] = "real"
    errs = validate_article(a)
    assert any("origin_url" in e for e in errs)
