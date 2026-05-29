import unittest

from anyviking_research.cli import _is_generated_summary


class CliHelperTests(unittest.TestCase):
    def test_generated_summary_filter_matches_openviking_summary_files(self) -> None:
        self.assertTrue(_is_generated_summary("viking://resources/demo/.abstract.md"))
        self.assertTrue(_is_generated_summary("viking://resources/demo/.overview.md"))

    def test_generated_summary_filter_keeps_original_documents(self) -> None:
        self.assertFalse(_is_generated_summary("viking://resources/demo/article.md"))
        self.assertFalse(_is_generated_summary("viking://resources/demo/overview-notes.md"))


if __name__ == "__main__":
    unittest.main()
