from dedupe import dedupe_items


def test_dedupe_by_link_and_title_similarity():
    items = [
        {"title": "Breaking News One", "link": "http://a", "section": "top", "source": "NPR", "published": ""},
        {"title": "Breaking News One!", "link": "http://a", "section": "top", "source": "NPR", "published": ""},
        {"title": "Breaking News  One", "link": "http://b", "section": "top", "source": "AP", "published": ""},
    ]

    unique = dedupe_items(items)
    assert len(unique) == 2
    assert unique[0]["link"] == "http://a"
    assert unique[1]["link"] == "http://b"
