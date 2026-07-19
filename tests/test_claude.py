import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from claude import parse_json


def test_parse_object():
    assert parse_json('前綴 {"a": 1} 後綴', None) == {"a": 1}


def test_parse_array():
    assert parse_json('```json\n[1,2,3]\n```', None) == [1, 2, 3]


def test_parse_fallback_on_garbage():
    assert parse_json("no json here", {"x": 0}) == {"x": 0}
