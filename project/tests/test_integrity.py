import tempfile
import unittest
from pathlib import Path

from utils import helpers


class HelperTests(unittest.TestCase):
    def test_hash_file_sha1_deterministic(self) -> None:
        content = b"Diligent Candidate"
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)
        try:
            first = helpers.hash_file_sha1(tmp_path)
            second = helpers.hash_file_sha1(tmp_path)
            self.assertEqual(first, second)
            self.assertEqual(len(first), 40)
        finally:
            tmp_path.unlink(missing_ok=True)


class SchemaTests(unittest.TestCase):
    def test_schema_has_submission_meta_table(self) -> None:
        schema_text = (helpers.BASE_DIR / "db" / "schema.sql").read_text(encoding="utf-8")
        self.assertIn("submission_meta", schema_text)
        self.assertIn("tool_used", schema_text)


if __name__ == "__main__":
    unittest.main()

