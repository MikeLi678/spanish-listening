import os
import sys
import json
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from schema import validate_article, LEVELS
from generate_ai import generate_ai_article
from fetch_real import fetch_candidates
from process_real import process_real_article

CONTENT_DIR = os.path.join(os.path.dirname(__file__), "..", "content")
_LOW = ["A1", "A2", "B1"]
_HIGH = ["B2", "C1", "C2"]
# 每個等級最多帶入多少個「已教過的字」給 AI 避開（取最近的，避免 A1 有限字彙被榨乾）
_AVOID_CAP = 120


def _taipei_today() -> str:
    return datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")


def collect_used_words(content_dir=CONTENT_DIR, cap=_AVOID_CAP) -> dict:
    """掃過往內容，回傳 {level: [已當過重點單字的字]}，同級最近的排前面、去重、上限 cap。"""
    dates = []
    try:
        for name in os.listdir(content_dir):
            if name.endswith(".json") and name != "index.json" and name[0].isdigit():
                dates.append(name[:-5])
    except OSError:
        return {}
    dates.sort(reverse=True)  # 最近的日期先處理

    used = {lvl: [] for lvl in LEVELS}
    seen = {lvl: set() for lvl in LEVELS}
    for date in dates:
        try:
            with open(os.path.join(content_dir, f"{date}.json"), encoding="utf-8") as f:
                day = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        for level, arts in day.get("levels", {}).items():
            if level not in used:
                continue
            for a in arts:
                for w in a.get("words", []):
                    word = (w.get("word") or "").strip()
                    key = word.lower()
                    if word and key not in seen[level] and len(used[level]) < cap:
                        seen[level].add(key)
                        used[level].append(word)
    return used


def _try(fn, label):
    """執行 fn，非法/例外時重試一次，仍失敗回 None。"""
    for attempt in (1, 2):
        try:
            art = fn()
            errs = validate_article(art)
            if not errs:
                return art
            print(f"[generate] {label} 驗證失敗(第{attempt}次): {errs}")
        except Exception as e:
            print(f"[generate] {label} 例外(第{attempt}次): {e}")
    return None


def build_day(date, ai_fn=generate_ai_article,
              candidates_fn=fetch_candidates, real_fn=process_real_article,
              used=None) -> dict:
    levels = {lvl: [] for lvl in LEVELS}
    used = used or {}

    for lvl in _LOW:
        art = _try(lambda l=lvl: ai_fn(l, date, avoid=used.get(l)), f"AI {lvl}")
        if art:
            levels[lvl].append(art)

    try:
        candidates = candidates_fn()
    except Exception as e:
        print(f"[generate] 抓取候選失敗: {e}")
        candidates = []

    for i, lvl in enumerate(_HIGH):
        art = None
        if i < len(candidates):
            cand = candidates[i]
            art = _try(lambda c=candidates[i], l=lvl, idx=i: real_fn(c, date, idx + 1, avoid=used.get(l)),
                       f"real {lvl}")
        if art is None:
            # fallback：真實內容不足或失敗，改 AI 生成（用 B1 規格但標高階 label）
            fb = _try(lambda l=lvl: _fallback_ai(l, date, ai_fn, avoid=used.get(l)), f"fallback {lvl}")
            if fb:
                art = fb
        if art:
            levels[lvl].append(art)

    return {"date": date, "levels": levels}


def _fallback_ai(lvl, date, ai_fn, avoid=None):
    art = ai_fn("B1", date, avoid=avoid)
    art["id"] = f"{date}-{lvl}-fallback"
    art["level_label"] = f"約 {lvl}（AI 生成）"
    art["source"] = "ai"
    return art


def update_index(content_dir=CONTENT_DIR) -> list[str]:
    """寫出輕量清單 index.json：含日期陣列與各篇摘要（不含全文），
    讓首頁只抓一次就能列出所有文章，不必逐日抓完整內容。"""
    dates = []
    for name in os.listdir(content_dir):
        if name.endswith(".json") and name != "index.json" and name[0].isdigit():
            dates.append(name[:-5])
    dates.sort(reverse=True)

    days = []
    for date in dates:
        try:
            with open(os.path.join(content_dir, f"{date}.json"), encoding="utf-8") as f:
                day = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"[update_index] 略過壞掉的 {date}.json: {e}")
            continue
        articles = []
        for level, arts in day.get("levels", {}).items():
            for a in arts:
                articles.append({
                    "id": a.get("id", ""),
                    "level": level,
                    "title": a.get("title", ""),
                    "source": a.get("source", "ai"),
                    "level_label": a.get("level_label", level),
                    "origin_name": a.get("origin_name", ""),
                })
        days.append({"date": date, "articles": articles})

    with open(os.path.join(content_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump({"dates": dates, "days": days}, f, ensure_ascii=False, indent=2)
    return dates


def main():
    os.makedirs(CONTENT_DIR, exist_ok=True)
    date = _taipei_today()
    print(f"[generate] 產生 {date} 內容...")
    used = collect_used_words(CONTENT_DIR)
    print(f"[generate] 避開已教過的單字：" +
          ", ".join(f"{lvl}={len(used.get(lvl, []))}" for lvl in LEVELS))
    day = build_day(date, used=used)
    total = sum(len(v) for v in day["levels"].values())
    if total == 0:
        print("[generate] 沒有任何內容產生，中止。", file=sys.stderr)
        sys.exit(1)
    path = os.path.join(CONTENT_DIR, f"{date}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(day, f, ensure_ascii=False, indent=2)
    print(f"[generate] 已寫入 {path}（{total} 篇）")
    dates = update_index()
    print(f"[generate] index 更新，共 {len(dates)} 天")


if __name__ == "__main__":
    main()
