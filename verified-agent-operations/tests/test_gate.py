import importlib.util
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("gate", ROOT / "gate.py")
GATE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(GATE)


class GateTests(unittest.TestCase):
    def test_allow_fixture_is_valid(self):
        case = json.loads((ROOT / "examples" / "allow.json").read_text(encoding="utf-8"))
        result = GATE.validate_case(case)
        self.assertEqual(result["decision"], "ACT")
        self.assertEqual(len(result["evidence"]), 2)

    def test_refuse_fixture_is_valid_without_evidence(self):
        case = json.loads((ROOT / "examples" / "refuse.json").read_text(encoding="utf-8"))
        self.assertEqual(GATE.validate_case(case)["decision"], "REFUSE")

    def test_query_and_wait_fixtures_are_valid(self):
        for name, expected in (("query.json", "QUERY"), ("wait.json", "WAIT")):
            case = json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))
            self.assertEqual(GATE.validate_case(case)["decision"], expected)

    def test_act_without_evidence_fails_closed(self):
        case = {
            "decision": "ACT",
            "claim": "A claim",
            "evidence": [],
            "boundary": "No side effect",
        }
        with self.assertRaises(GATE.GateError):
            GATE.validate_case(case)

    def test_unknown_decision_is_rejected(self):
        case = {
            "decision": "GUESS",
            "claim": "A claim",
            "evidence": ["fixture"],
            "boundary": "Bounded",
        }
        with self.assertRaises(GATE.GateError):
            GATE.validate_case(case)


if __name__ == "__main__":
    unittest.main()
