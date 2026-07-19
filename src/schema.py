LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
_REQUIRED = ["id", "source", "level_label", "title", "text", "words", "quiz"]


def validate_article(article: dict) -> list[str]:
    errors = []
    for f in _REQUIRED:
        if f not in article or article[f] in (None, "", []):
            errors.append(f"missing or empty field: {f}")
    if errors:
        return errors

    if article["source"] == "real":
        for f in ("origin_url", "origin_name"):
            if not article.get(f):
                errors.append(f"real source missing field: {f}")

    if not isinstance(article["words"], list) or not article["words"]:
        errors.append("words must be a non-empty list")
    else:
        for i, w in enumerate(article["words"]):
            for f in ("word", "pos", "zh", "example"):
                if not w.get(f):
                    errors.append(f"words[{i}] missing field: {f}")

    quiz = article["quiz"]
    if not isinstance(quiz, list) or not quiz:
        errors.append("quiz must be a non-empty list")
    else:
        for i, q in enumerate(quiz):
            opts = q.get("options")
            if not isinstance(opts, list) or len(opts) != 4:
                errors.append(f"quiz[{i}] must have exactly 4 options")
                continue
            ans = q.get("answer")
            if not isinstance(ans, int) or not (0 <= ans < 4):
                errors.append(f"quiz[{i}] answer out of range")
            for f in ("q", "explain"):
                if not q.get(f):
                    errors.append(f"quiz[{i}] missing field: {f}")
    return errors
