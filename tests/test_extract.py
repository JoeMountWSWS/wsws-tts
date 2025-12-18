import json

import pytest

from wsws_tts.extract import _extract_paragraphs_from_content_data, _load_next_data


def test_extract_paragraphs_from_content_data_basic():
    content_data = [
        {
            "type": "element",
            "tagName": "p",
            "content": None,
            "attributes": [],
            "data": [],
            "assets": [],
            "children": [
                {
                    "type": "text",
                    "tagName": None,
                    "content": "Hello world.",
                    "attributes": [],
                    "data": [],
                    "assets": [],
                    "children": None,
                }
            ],
        },
        {
            "type": "element",
            "tagName": "blockquote",
            "content": None,
            "attributes": [],
            "data": [],
            "assets": [],
            "children": [
                {
                    "type": "text",
                    "tagName": None,
                    "content": "A quote.",
                    "attributes": [],
                    "data": [],
                    "assets": [],
                    "children": None,
                }
            ],
        },
    ]

    paras = _extract_paragraphs_from_content_data(content_data)
    assert paras == ["Hello world.", '"A quote."']


def test_load_next_data_finds_script():
    next_data = {"props": {"pageProps": {"initialData": {"page": {"title": "x"}}}}}
    html = f"""
    <html><head></head><body>
      <script id="__NEXT_DATA__" type="application/json">{json.dumps(next_data)}</script>
    </body></html>
    """
    parsed = _load_next_data(html)
    assert parsed["props"]["pageProps"]["initialData"]["page"]["title"] == "x"
