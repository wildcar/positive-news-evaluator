"""Unit tests for preparer.py: image extraction, retelling parse, HTML, own DB."""

from __future__ import annotations

import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import evaluator
import preparer
from preparer import (
    build_page,
    extract_illustrations,
    open_own_db,
    parse_retelling,
    prepared_ids,
    record_error,
    save_prepared,
)

ARTICLE_HTML = b"""
<html><head>
<meta property="og:image" content="https://site.test/lead.jpg">
</head><body>
<article>
<figure><img src="/img/one.jpg" alt="alt one"><figcaption>Caption one</figcaption></figure>
<p>text</p>
<figure><img data-src="https://site.test/img/two.png"><figcaption>Caption two</figcaption></figure>
<img src="lazy.webp" alt="loose alt">
<img src="data:image/gif;base64,AAAA">
</article></body></html>
"""


class ExtractIllustrationsTests(unittest.TestCase):
    def test_order_captions_and_resolution(self):
        items = extract_illustrations(ARTICLE_HTML, "https://site.test/news/1", limit=10)
        urls = [i["url"] for i in items]
        self.assertEqual(urls[0], "https://site.test/lead.jpg")  # og:image first
        self.assertIn("https://site.test/img/one.jpg", urls)     # relative resolved
        self.assertIn("https://site.test/img/two.png", urls)     # data-src (lazy) picked up
        self.assertIn("https://site.test/news/lazy.webp", urls)  # loose img resolved
        self.assertNotIn("data:image/gif;base64,AAAA", urls)     # data: URI dropped
        by_url = {i["url"]: i["caption"] for i in items}
        self.assertEqual(by_url["https://site.test/img/one.jpg"], "Caption one")
        self.assertEqual(by_url["https://site.test/news/lazy.webp"], "loose alt")

    def test_limit_and_dedup(self):
        items = extract_illustrations(ARTICLE_HTML, "https://site.test/", limit=2)
        self.assertEqual(len(items), 2)
        html = b'<img src="/a.jpg"><img src="/a.jpg">'
        self.assertEqual(len(extract_illustrations(html, "https://site.test/", 10)), 1)


class ParseRetellingTests(unittest.TestCase):
    def test_list_body(self):
        title, paras = parse_retelling({"title": "  Заголовок  ", "body": ["Раз", " Два ", ""]})
        self.assertEqual(title, "Заголовок")
        self.assertEqual(paras, ["Раз", "Два"])

    def test_string_body_split_on_blank_lines(self):
        _, paras = parse_retelling({"title": "T", "body": "Первый абзац.\n\nВторой абзац."})
        self.assertEqual(paras, ["Первый абзац.", "Второй абзац."])

    def test_missing_title(self):
        with self.assertRaises(evaluator.EvaluationInvalid):
            parse_retelling({"body": ["x"]})

    def test_empty_body(self):
        with self.assertRaises(evaluator.EvaluationInvalid):
            parse_retelling({"title": "T", "body": []})

    def test_long_dashes_normalized(self):
        title, paras = parse_retelling({"title": "Мышь — рекордсмен", "body": ["Она живёт долго — и активно."]})
        self.assertEqual(title, "Мышь - рекордсмен")
        self.assertEqual(paras, ["Она живёт долго - и активно."])
        self.assertNotIn("—", title + paras[0])


class BuildPageTests(unittest.TestCase):
    def test_structure_and_escaping(self):
        images = [{"path": "/var/lib/news-evaluator/media/5/1.jpg", "caption": "Подпись <b>", "source_url": "https://s/x"}]
        page = build_page("Заголовок & <", ["Абзац раз", "Абзац два"], images,
                          "https://site.test/news/5", "/var/lib/news-evaluator/pages")
        self.assertIn("<h1>Заголовок &amp; &lt;</h1>", page)
        self.assertEqual(page.count("<p>"), 2)
        self.assertIn('src="../media/5/1.jpg"', page)          # path relative to pages dir
        self.assertIn("<figcaption>Подпись &lt;b&gt;</figcaption>", page)
        self.assertIn('<footer>Источник: <a href="https://site.test/news/5">site.test</a>', page)

    def test_no_images_no_figure(self):
        page = build_page("T", ["Один абзац"], [], "", "/pages")
        self.assertNotIn("<figure>", page)
        self.assertNotIn("<footer>", page)


class OwnDbTests(unittest.TestCase):
    def setUp(self):
        self.con = open_own_db(":memory:")

    def tearDown(self):
        self.con.close()

    def test_save_and_list_prepared(self):
        images = [{"path": "/m/5/1.jpg", "caption": "c", "source_url": "https://s/1"}]
        save_prepared(self.con, 5, "Заголовок", "<html>", "/p/5.html", "deepseek-chat", images)
        self.assertEqual(prepared_ids(self.con), {5})
        row = self.con.execute("SELECT status, retold_title FROM prepared_item WHERE news_id=5").fetchone()
        self.assertEqual((row["status"], row["retold_title"]), ("prepared", "Заголовок"))
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM illustration WHERE news_id=5").fetchone()[0], 1)

    def test_resave_replaces_illustrations(self):
        save_prepared(self.con, 5, "t", "h", "p", "m", [{"path": "/a", "caption": "", "source_url": ""}])
        save_prepared(self.con, 5, "t", "h", "p", "m", [{"path": "/b", "caption": "", "source_url": ""},
                                                        {"path": "/c", "caption": "", "source_url": ""}])
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM illustration WHERE news_id=5").fetchone()[0], 2)

    def test_error_then_recovery(self):
        record_error(self.con, 7, "boom")
        self.assertEqual(prepared_ids(self.con), set())  # errors are not 'prepared'
        row = self.con.execute("SELECT status, error FROM prepared_item WHERE news_id=7").fetchone()
        self.assertEqual((row["status"], row["error"]), ("error", "boom"))
        save_prepared(self.con, 7, "t", "h", "p", "m", [])
        self.assertEqual(prepared_ids(self.con), {7})


if __name__ == "__main__":
    unittest.main()
