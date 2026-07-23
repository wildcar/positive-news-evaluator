"""Unit tests for publisher.py: content builders, HTTP encoding, own DB, run loop.

No network: platform sends are exercised through monkeypatched adapters."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import publisher
from publisher import (
    PublishError,
    PublisherConfig,
    build_site_text,
    build_tg_caption,
    build_vk_message,
    encode_multipart,
    input_val,
    open_own_db,
    parse_markdown,
    publication_status,
    source_name_from_url,
    _abs_url,
)

MARKDOWN_DOC = (
    "# Заголовок\n\n"
    "Первый абзац с «кавычками» и амперсандом & знаком.\n\n"
    "Второй абзац.\n\n"
    "Третий абзац.\n\n"
    "Источник: [site.test](https://site.test/a)"
)


class ParseMarkdownTests(unittest.TestCase):
    def test_parses_title_paragraphs_source(self):
        title, paras, url, name = parse_markdown(MARKDOWN_DOC)
        self.assertEqual(title, "Заголовок")
        self.assertEqual(len(paras), 3)
        self.assertEqual(paras[0], "Первый абзац с «кавычками» и амперсандом & знаком.")
        self.assertEqual(paras[2], "Третий абзац.")
        self.assertEqual((url, name), ("https://site.test/a", "site.test"))

    def test_source_line_not_in_paragraphs(self):
        _, paras, _, _ = parse_markdown(MARKDOWN_DOC)
        self.assertTrue(all("Источник" not in p for p in paras))

    def test_empty(self):
        self.assertEqual(parse_markdown(""), ("", [], "", ""))

    def test_source_name_falls_back_to_host(self):
        _, _, url, name = parse_markdown("# T\n\nabc\n\nИсточник: [](https://www.foo.test/x)")
        self.assertEqual((url, name), ("https://www.foo.test/x", "foo.test"))


class SourceNameTests(unittest.TestCase):
    def test_strips_www(self):
        self.assertEqual(source_name_from_url("https://www.upi.com/x/y"), "upi.com")
        self.assertEqual(source_name_from_url("https://ria.ru/z"), "ria.ru")


class TelegramCaptionTests(unittest.TestCase):
    def test_structure_and_escaping(self):
        cap = build_tg_caption("A & B", ["one", "two"], "https://site.test/a", "site.test", 1024)
        self.assertIn("<b>A &amp; B</b>", cap)
        self.assertIn("one\n\ntwo", cap)
        self.assertIn('<a href="https://site.test/a">Источник: site.test</a>', cap)

    def test_truncates_paragraphs_to_fit(self):
        paras = ["x" * 500, "y" * 500, "z" * 500]
        cap = build_tg_caption("T", paras, "https://s.test/a", "s.test", 1024)
        self.assertLessEqual(len(cap), 1024)
        # the link (source) is kept even when paragraphs are dropped
        self.assertIn("Источник", cap)

    def test_title_only_when_nothing_fits(self):
        cap = build_tg_caption("Title", ["x" * 5000], "", "", 1024)
        self.assertLessEqual(len(cap), 1024)
        self.assertIn("Title", cap)


class VkAndSiteTextTests(unittest.TestCase):
    def test_vk_message_has_title_body_source(self):
        msg = build_vk_message("Заголовок", ["a", "b"], "https://s.test/a", "s.test")
        self.assertTrue(msg.startswith("Заголовок"))
        self.assertIn("a\n\nb", msg)
        self.assertIn("Источник: https://s.test/a", msg)

    def test_site_text_neasden_markup(self):
        text = build_site_text("pic.jpg", ["a", "b"], "https://s.test/a", "s.test")
        self.assertTrue(text.startswith("pic.jpg\n\n"))
        self.assertIn("Источник: ((https://s.test/a s.test))", text)

    def test_site_text_without_image(self):
        text = build_site_text("", ["a"], "https://s.test/a", "s.test")
        self.assertFalse(text.startswith("\n"))
        self.assertTrue(text.startswith("a"))


class MultipartTests(unittest.TestCase):
    def test_encodes_fields_and_file(self):
        ctype, body = encode_multipart(
            {"chat_id": "-100", "caption": "hi"},
            {"photo": ("p.jpg", b"\xff\xd8bytes", "image/jpeg")},
        )
        self.assertIn("multipart/form-data; boundary=", ctype)
        self.assertIn(b'name="chat_id"', body)
        self.assertIn(b'filename="p.jpg"', body)
        self.assertIn(b"\xff\xd8bytes", body)
        self.assertTrue(body.rstrip().endswith(b"--"))


class InputValTests(unittest.TestCase):
    def test_by_id_then_name_and_unescape(self):
        page = '<input id="token" value="ab&amp;cd"><input name="old-stamp" value="123">'
        self.assertEqual(input_val(page, "token"), "ab&cd")
        self.assertEqual(input_val(page, "old-stamp"), "123")
        self.assertEqual(input_val(page, "missing"), "")

    def test_abs_url(self):
        self.assertEqual(_abs_url("https://x.test", "/a/b/"), "https://x.test/a/b/")
        self.assertEqual(_abs_url("https://x.test", "https://x.test/c"), "https://x.test/c")
        self.assertEqual(_abs_url("https://x.test", ""), "")


class ConfigTests(unittest.TestCase):
    def test_enabled_platforms_gate_on_secrets(self):
        self.assertEqual(PublisherConfig().enabled_platforms(), [])
        cfg = PublisherConfig(tg_token="t", site_password="p", vk_token="v", vk_group_id="7")
        self.assertEqual(cfg.enabled_platforms(), ["telegram", "site", "vk"])
        # VK needs both token and group id
        self.assertEqual(PublisherConfig(vk_token="v").enabled_platforms(), [])


class OwnDbTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / "own.sqlite3")

    def tearDown(self):
        self.tmp.cleanup()

    def test_record_publication_upserts_and_counts_attempts(self):
        con = open_own_db(self.path)
        con.execute("INSERT INTO prepared_item (news_id, status) VALUES (5, 'prepared')")
        con.commit()
        publisher.record_publication(con, 5, "telegram", "error", None, "boom")
        publisher.record_publication(con, 5, "telegram", "ok", "https://t.me/x/1", None)
        rows = con.execute("SELECT status, url, attempts FROM publication WHERE news_id=5").fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "ok")
        self.assertEqual(rows[0]["attempts"], 2)
        self.assertEqual(publication_status(con, 5), {"telegram": "ok"})
        con.close()

    def test_mark_published(self):
        con = open_own_db(self.path)
        con.execute("INSERT INTO prepared_item (news_id, status) VALUES (9, 'prepared')")
        con.commit()
        publisher.mark_published(con, 9)
        row = con.execute("SELECT status, published_at FROM prepared_item WHERE news_id=9").fetchone()
        self.assertEqual(row["status"], "published")
        self.assertIsNotNone(row["published_at"])
        con.close()


class RunLoopTests(unittest.TestCase):
    """End-to-end run() with fake adapters: idempotency and label transition."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.own_path = str(Path(self.tmp.name) / "own.sqlite3")
        own = open_own_db(self.own_path)
        own.execute(
            "INSERT INTO prepared_item (news_id, status, retold_title, retold_body_md, prepared_at) "
            "VALUES (1, 'prepared', 'T', ?, '2026-07-23T10:00:00')",
            ("# T\n\npara one\n\npara two\n\nИсточник: [site.test](https://site.test/a)",),
        )
        own.commit()
        own.close()
        # telegram + site enabled, vk off
        self.cfg = PublisherConfig(own_db=self.own_path, tg_token="tok", site_password="pw")
        self._orig = dict(publisher.ADAPTERS)

    def tearDown(self):
        publisher.ADAPTERS.clear()
        publisher.ADAPTERS.update(self._orig)
        self.tmp.cleanup()

    def test_all_platforms_ok_marks_published(self):
        calls: list[str] = []
        publisher.ADAPTERS["telegram"] = lambda cfg, item, dry: (calls.append("tg"), "https://t.me/x/1")[1]
        publisher.ADAPTERS["site"] = lambda cfg, item, dry: (calls.append("site"), "https://site/x")[1]
        rc = publisher.run(self.cfg, limit=10, dry_run=False, only=None)
        self.assertEqual(rc, 0)
        self.assertEqual(sorted(calls), ["site", "tg"])
        con = open_own_db(self.own_path)
        self.assertEqual(con.execute("SELECT status FROM prepared_item WHERE news_id=1").fetchone()["status"], "published")
        con.close()

    def test_partial_failure_keeps_prepared_then_retries_only_failed(self):
        def ok(cfg, item, dry):
            return "https://ok"

        def boom(cfg, item, dry):
            raise PublishError("site down")

        publisher.ADAPTERS["telegram"] = ok
        publisher.ADAPTERS["site"] = boom
        rc = publisher.run(self.cfg, limit=10, dry_run=False, only=None)
        self.assertEqual(rc, 1)  # a failure returns non-zero
        con = open_own_db(self.own_path)
        self.assertEqual(con.execute("SELECT status FROM prepared_item WHERE news_id=1").fetchone()["status"], "prepared")
        self.assertEqual(publication_status(con, 1), {"telegram": "ok", "site": "error"})
        con.close()

        # second run: telegram is already ok, so only site is retried — make it succeed
        seen: list[str] = []
        publisher.ADAPTERS["telegram"] = lambda cfg, item, dry: (seen.append("tg"), "x")[1]
        publisher.ADAPTERS["site"] = lambda cfg, item, dry: (seen.append("site"), "https://site/ok")[1]
        rc = publisher.run(self.cfg, limit=10, dry_run=False, only=None)
        self.assertEqual(rc, 0)
        self.assertEqual(seen, ["site"])  # telegram skipped, only the failed platform retried
        con = open_own_db(self.own_path)
        self.assertEqual(con.execute("SELECT status FROM prepared_item WHERE news_id=1").fetchone()["status"], "published")
        con.close()

    def test_dry_run_writes_nothing(self):
        publisher.ADAPTERS["telegram"] = lambda cfg, item, dry: "should-not-record"
        publisher.ADAPTERS["site"] = lambda cfg, item, dry: "should-not-record"
        publisher.run(self.cfg, limit=10, dry_run=True, only=None)
        con = open_own_db(self.own_path)
        self.assertEqual(con.execute("SELECT COUNT(*) FROM publication").fetchone()[0], 0)
        self.assertEqual(con.execute("SELECT status FROM prepared_item WHERE news_id=1").fetchone()["status"], "prepared")
        con.close()


if __name__ == "__main__":
    unittest.main()
