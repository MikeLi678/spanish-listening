import requests
from bs4 import BeautifulSoup

RSS_FEEDS = [
    {"name": "BBC Mundo", "url": "https://www.bbc.com/mundo/index.xml"},
    {"name": "El País", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"},
]

_HEADERS = {"User-Agent": "Mozilla/5.0 (spanish-listening content bot)"}


def _http_get(url: str) -> str:
    resp = requests.get(url, headers=_HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_rss(xml: str) -> list[dict]:
    soup = BeautifulSoup(xml, "xml")
    items = []
    for it in soup.find_all("item"):
        title = it.find("title")
        link = it.find("link")
        if title and link and title.text.strip() and link.text.strip():
            items.append({"title": title.text.strip(), "link": link.text.strip()})
    return items


def extract_article_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    root = soup.find("article") or soup.body or soup
    paras = [p.get_text(" ", strip=True) for p in root.find_all("p")]
    paras = [p for p in paras if len(p) > 40]
    return "\n\n".join(paras)


def fetch_candidates(fetcher=_http_get) -> list[dict]:
    candidates = []
    for feed in RSS_FEEDS:
        try:
            items = parse_rss(fetcher(feed["url"]))
        except Exception as e:
            print(f"[fetch_real] RSS 失敗 {feed['name']}: {e}")
            continue
        for it in items[:3]:
            try:
                text = extract_article_text(fetcher(it["link"]))
            except Exception as e:
                print(f"[fetch_real] 文章抓取失敗 {it['link']}: {e}")
                continue
            if len(text) > 400:
                candidates.append({"title": it["title"], "link": it["link"],
                                   "text": text, "origin_name": feed["name"]})
    return candidates
