from clean import clean_text, normalize_entry


def test_clean_text_strips_html_and_whitespace():
    raw = "<p>Hello &amp; world</p>\n\nMore   text"
    assert clean_text(raw) == "Hello & world More text"


def test_normalize_entry_shapes_fields():
    entry = {
        "title": "<b>Title</b>",
        "link": "http://example.com",
        "summary": "<p>Summary</p>",
        "published": "2024-01-01",
    }
    normalized = normalize_entry(entry, source="NPR", section="top")
    assert normalized["source"] == "NPR"
    assert normalized["section"] == "top"
    assert normalized["title"] == "Title"
    assert normalized["summary"] == "Summary"
    assert normalized["link"] == "http://example.com"
