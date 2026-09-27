import unittest
from pathlib import Path
from unittest.mock import patch

import filetr


class SentenceSplitTests(unittest.TestCase):
    def test_split_sentences_keeps_punctuation_and_ignores_blank_parts(self):
        self.assertEqual(
            filetr.split_sentences("Перше речення. Друге речення!  Третє?"),
            ["Перше речення.", "Друге речення!", "Третє?"],
        )

    def test_split_sentences_empty_input(self):
        self.assertEqual(filetr.split_sentences(" \n "), [])


class ConfigTests(unittest.TestCase):
    def test_read_config_checks_required_fields(self):
        with patch.object(filetr.Path, "open") as mocked_open:
            mocked_open.return_value.__enter__.return_value.read.return_value = (
                '{"input_file":"sample_uk.txt"}'
            )
            # json.load uses the file object's read method.
            with self.assertRaises(ValueError):
                filetr.read_config(Path("config.json"))

    def test_resolve_output_path_adds_language_code(self):
        source = Path("/project/source.txt")
        self.assertEqual(
            filetr._resolve_output_path(source, "en"),
            Path("/project/source_en.txt"),
        )


if __name__ == "__main__":
    unittest.main()