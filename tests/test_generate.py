import sys, os, json, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pytest
import generate
from schema import validate_article

_AI = {"id": "d-A1-1", "source": "ai", "level_label": "A1", "title": "t",
       "text": "texto", "words": [{"word": "a", "pos": "n", "zh": "甲", "example": "a."}],
       "quiz": [{"q": "?", "options": ["a", "b", "c", "d"], "answer": 0, "explain": "x"}]}


def _ai_fn(level, date, caller=None):
    art = dict(_AI); art["id"] = f"{date}-{level}-1"; art["level_label"] = level
    return art


def _real_fn(cand, date, index, caller=None):
    art = dict(_AI); art["id"] = f"{date}-real-{index}"; art["source"] = "real"
    art["origin_url"] = "u"; art["origin_name"] = "n"; art["level_label"] = "約 B2–C1"
    return art


def test_build_day_groups_all_levels():
    day = generate.build_day("2026-07-18", _ai_fn,
                             lambda: [{"title": "t", "link": "u", "text": "x", "origin_name": "n"}] * 3,
                             _real_fn)
    assert day["date"] == "2026-07-18"
    assert set(day["levels"]) == {"A1", "A2", "B1", "B2", "C1", "C2"}
    for arts in day["levels"].values():
        for a in arts:
            assert validate_article(a) == []


def test_build_day_fallbacks_to_ai_when_no_real():
    day = generate.build_day("2026-07-18", _ai_fn, lambda: [], _real_fn)
    # 沒有真實候選時 B2-C2 fallback 為 AI 生成，仍每級有內容
    for lvl in ("B2", "C1", "C2"):
        assert len(day["levels"][lvl]) >= 1


def test_build_day_retry_then_skip():
    # ai_fn 永遠回傳 schema 不合法的文章（title 空白）→ 重試一次後仍失敗，該級別維持空清單
    calls = {}

    def bad_ai_fn(level, date, caller=None):
        calls[level] = calls.get(level, 0) + 1
        art = dict(_AI); art["id"] = f"{date}-{level}-1"; art["level_label"] = level
        art["title"] = ""  # 不合法
        return art

    day = generate.build_day("2026-07-18", bad_ai_fn,
                             lambda: [{"title": "t", "link": "u", "text": "x", "origin_name": "n"}] * 3,
                             _real_fn)
    for lvl in ("A1", "A2", "B1"):
        assert day["levels"][lvl] == []
        assert calls[lvl] == 2  # 兩次嘗試皆失敗


def test_build_day_retry_succeeds_second_attempt():
    # ai_fn 第一次回傳不合法，第二次（重試）回傳合法 → 該級別最終有 1 篇文章
    calls = {}

    def flaky_ai_fn(level, date, caller=None):
        calls[level] = calls.get(level, 0) + 1
        art = dict(_AI); art["id"] = f"{date}-{level}-1"; art["level_label"] = level
        if calls[level] == 1:
            art["title"] = ""  # 第一次不合法
        return art

    day = generate.build_day("2026-07-18", flaky_ai_fn,
                             lambda: [{"title": "t", "link": "u", "text": "x", "origin_name": "n"}] * 3,
                             _real_fn)
    for lvl in ("A1", "A2", "B1"):
        assert len(day["levels"][lvl]) == 1
        assert calls[lvl] == 2


def test_build_day_fallback_on_real_failure():
    # 有候選文章，但 real_fn 執行失敗（例外）→ fallback 為 AI 生成，source 標為 ai
    def failing_real_fn(cand, date, index, caller=None):
        raise RuntimeError("real_fn 失敗")

    day = generate.build_day("2026-07-18", _ai_fn,
                             lambda: [{"title": "t", "link": "u", "text": "x", "origin_name": "n"}] * 3,
                             failing_real_fn)
    for lvl in ("B2", "C1", "C2"):
        arts = day["levels"][lvl]
        assert len(arts) == 1
        assert arts[0]["source"] == "ai"


def test_main_exits_when_zero_total():
    with tempfile.TemporaryDirectory() as d:
        orig_build_day = generate.build_day
        orig_content_dir = generate.CONTENT_DIR
        generate.CONTENT_DIR = d
        generate.build_day = lambda date, *a, **k: {
            "date": date, "levels": {lvl: [] for lvl in generate.LEVELS}
        }
        try:
            with pytest.raises(SystemExit) as exc_info:
                generate.main()
            assert exc_info.value.code == 1
            assert os.listdir(d) == []  # exit 發生在寫檔之前，不應留下任何檔案
        finally:
            generate.build_day = orig_build_day
            generate.CONTENT_DIR = orig_content_dir


def test_update_index_sorts_dates():
    with tempfile.TemporaryDirectory() as d:
        for name in ("2026-07-18.json", "2026-07-16.json", "index.json"):
            open(os.path.join(d, name), "w").write("{}")
        dates = generate.update_index(d)
        assert dates == ["2026-07-18", "2026-07-16"]
        written = json.load(open(os.path.join(d, "index.json")))
        assert written["dates"] == ["2026-07-18", "2026-07-16"]
