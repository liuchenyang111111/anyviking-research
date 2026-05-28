import json
import unittest

import httpx

from anyviking_research.connectors.anysearch import AnySearchConnector


class AnySearchConnectorTests(unittest.TestCase):
    def test_search_posts_expected_payload_and_normalizes_results(self) -> None:
        seen: dict[str, object] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen["url"] = str(request.url)
            seen["authorization"] = request.headers.get("authorization")
            seen["payload"] = json.loads(request.content.decode("utf-8"))
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "title": "Demo title",
                            "url": "https://example.com/demo",
                            "description": "Short summary",
                            "content": "Full content",
                            "source": "web",
                            "score": "0.7",
                            "quality_score": 0.9,
                            "published_at": "2026-05-01T00:00:00Z",
                            "raw_content": "raw",
                        }
                    ],
                    "metadata": {"request_id": "req_demo"},
                },
            )

        connector = AnySearchConnector(
            base_url="https://api.anysearch.test",
            api_key="test-key",
            transport=httpx.MockTransport(handler),
        )

        response = connector.search(
            "demo query",
            max_results=3,
            domains=["tech"],
            content_types=["web"],
            freshness="week",
        )

        self.assertEqual(seen["url"], "https://api.anysearch.test/v1/search")
        self.assertEqual(seen["authorization"], "Bearer test-key")
        self.assertEqual(
            seen["payload"],
            {
                "query": "demo query",
                "max_results": 3,
                "domains": ["tech"],
                "content_types": ["web"],
                "constraint": {"freshness": "week"},
            },
        )
        self.assertEqual(response.query, "demo query")
        self.assertEqual(response.metadata["request_id"], "req_demo")
        self.assertEqual(len(response.results), 1)
        self.assertEqual(response.results[0].title, "Demo title")
        self.assertEqual(response.results[0].score, 0.7)
        self.assertEqual(response.results[0].metadata["raw_content"], "raw")

    def test_search_accepts_anysearch_data_wrapped_response(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "code": 0,
                    "message": "success",
                    "data": {
                        "results": [
                            {
                                "title": "Wrapped result",
                                "url": "https://example.com/wrapped",
                                "content": "Wrapped content",
                            }
                        ],
                        "metadata": {"request_id": "req_wrapped"},
                    },
                },
            )

        connector = AnySearchConnector(
            base_url="https://api.anysearch.test",
            transport=httpx.MockTransport(handler),
        )

        response = connector.search("wrapped query", max_results=1)

        self.assertEqual(len(response.results), 1)
        self.assertEqual(response.results[0].title, "Wrapped result")
        self.assertEqual(response.metadata["request_id"], "req_wrapped")
        self.assertEqual(response.metadata["code"], 0)
        self.assertEqual(response.metadata["message"], "success")

    def test_search_rejects_invalid_limit(self) -> None:
        connector = AnySearchConnector(transport=httpx.MockTransport(lambda request: httpx.Response(200)))

        with self.assertRaisesRegex(ValueError, "between 1 and 100"):
            connector.search("demo", max_results=0)


if __name__ == "__main__":
    unittest.main()
