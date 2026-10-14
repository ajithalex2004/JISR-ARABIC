"""AI drafts survive the JSON slips Gemini makes in long replies."""
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from backend.errors import ApplicationError
from backend.modules.curriculum import drafting


class TestParseModelJson(unittest.TestCase):
    def test_trailing_commas_comments_and_fences_are_repaired(self):
        text = '```json\n{"title": "أَلْعَابِي، وَهِوَايَاتِي", // heading\n "items": [1, 2,], /* note */ "x": {"y": "a, }",},}\n```'
        self.assertEqual(drafting.parse_model_json(text),
                         {"title": "أَلْعَابِي، وَهِوَايَاتِي", "items": [1, 2], "x": {"y": "a, }"}})

    def test_text_inside_strings_is_untouched(self):
        text = '{"q": "قال: \\"مرحبا\\" // ليس تعليقا /* ولا هذا */", "n": 1,}'
        self.assertEqual(drafting.parse_model_json(text)["q"], 'قال: "مرحبا" // ليس تعليقا /* ولا هذا */')

    def test_unrepairable_json_raises_value_error(self):
        with self.assertRaises(ValueError):
            drafting.parse_model_json('{"a": }')


class TestGeneratorRetries(unittest.TestCase):
    def _generator(self, replies):
        client = MagicMock()
        client.files.upload.return_value = "uploaded-page"
        client.models.generate_content.side_effect = [SimpleNamespace(text=r) for r in replies]
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test"}), patch("google.genai.Client", return_value=client):
            return drafting.gemini_generator(), client

    def test_bad_reply_is_retried(self):
        generate, client = self._generator(['{"a": 1 "b": 2}', '{"a": 1, "b": 2}'])
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "page_8.png"
            page.write_bytes(b"png")
            self.assertEqual(generate("prompt", [page]), {"a": 1, "b": 2})
        self.assertEqual(client.models.generate_content.call_count, 2)
        self.assertEqual(client.files.upload.call_count, 1)

    def test_gives_up_after_three_unreadable_replies(self):
        generate, client = self._generator(['{"a": }'] * 3)
        with self.assertRaises(ApplicationError) as ctx:
            generate("prompt", [])
        self.assertIn("after 3 attempts", str(ctx.exception.detail))
        self.assertEqual(client.models.generate_content.call_count, 3)


if __name__ == "__main__":
    unittest.main()
