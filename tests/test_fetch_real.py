import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from fetch_real import parse_rss, extract_article_text

_RSS = """<?xml version="1.0"?><rss><channel>
<item><title>Noticia uno</title><link>https://example.com/1</link></item>
<item><title>Noticia dos</title><link>https://example.com/2</link></item>
</channel></rss>"""

_HTML = "<html><body><article>"\
        "<p>Primer parrafo largo de prueba con contenido sustancial y significativo.</p>"\
        "<p>Segundo parrafo con mas texto detallado e informacion relevante al articulo.</p>"\
        "</article></body></html>"


def test_parse_rss_returns_items():
    items = parse_rss(_RSS)
    assert len(items) == 2
    assert items[0]["title"] == "Noticia uno"
    assert items[0]["link"] == "https://example.com/1"


def test_extract_article_text_joins_paragraphs():
    text = extract_article_text(_HTML)
    assert "Primer parrafo" in text
    assert "Segundo parrafo" in text
