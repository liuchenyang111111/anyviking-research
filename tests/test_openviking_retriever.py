import unittest

from ov_search_skill.retrievers.openviking import OpenVikingRetriever


class OpenVikingRetrieverTests(unittest.TestCase):
    def test_title_from_uri_decodes_tail_and_strips_markdown_suffix(self) -> None:
        title = OpenVikingRetriever._title_from_uri(
            "viking://resources/demo/%E6%96%B0%E9%97%BB.md"
        )

        self.assertEqual(title, "新闻")

    def test_score_parses_numeric_values(self) -> None:
        self.assertEqual(OpenVikingRetriever._score("0.42"), 0.42)
        self.assertIsNone(OpenVikingRetriever._score(None))
        self.assertIsNone(OpenVikingRetriever._score("not-a-number"))


if __name__ == "__main__":
    unittest.main()
