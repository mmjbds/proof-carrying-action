import importlib.util
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("builder", ROOT / "local_evidence_packet_builder.py")
BUILDER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BUILDER)


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.payload


class BuilderTests(unittest.TestCase):
    def fake_request(self, _request, timeout):
        self.assertEqual(timeout, 60)
        return FakeResponse(
            {
                "response": json.dumps(
                    {
                        "claim": "The source requires review before action.",
                        "evidence": ["fixture:source-001"],
                        "boundary": "Synthetic text only; no external side effect.",
                        "uncertainties": ["Human must confirm source scope."],
                    }
                )
            }
        )

    def test_builds_candidate_and_defaults_to_query(self):
        candidate = BUILDER.build_candidate_packet(
            "The source requires review before action.", request_fn=self.fake_request
        )
        self.assertTrue(candidate["review_required"])
        gate_case = BUILDER.to_gate_case(candidate)
        self.assertEqual(gate_case["decision"], "QUERY")

    def test_remote_endpoint_is_rejected(self):
        with self.assertRaises(BUILDER.BuilderError):
            BUILDER.build_candidate_packet(
                "text", endpoint="https://example.com/api/generate", request_fn=self.fake_request
            )

    def test_missing_candidate_field_is_rejected(self):
        def incomplete(_request, timeout):
            return FakeResponse({"response": json.dumps({"claim": "only claim"})})

        with self.assertRaises(BUILDER.BuilderError):
            BUILDER.build_candidate_packet("text", request_fn=incomplete)


if __name__ == "__main__":
    unittest.main()
