import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from process_real import process_real_article
from schema import validate_article

_FAKE = json.dumps({
    "level_label": "約 B2–C1",
    "title": "La economía",
    "text": "Un párrafo real de nivel avanzado sobre economía y sociedad.",
    "words": [{"word": "economía", "pos": "n.f.", "zh": "經濟", "example": "La economía crece."}],
    "quiz": [{"q": "¿De qué trata?", "options": ["economía", "deporte", "clima", "arte"],
              "answer": 0, "explain": "主題是經濟。"}],
})

_CAND = {"title": "orig", "link": "https://elpais.com/x",
         "text": "texto largo " * 60, "origin_name": "El País"}


def test_process_returns_valid_real_article():
    art = process_real_article(_CAND, "2026-07-18", 1,
                               caller=lambda p, max_tokens=2000: _FAKE)
    assert validate_article(art) == []
    assert art["source"] == "real"
    assert art["origin_url"] == "https://elpais.com/x"
    assert art["origin_name"] == "El País"
    assert "B2" in art["level_label"]
