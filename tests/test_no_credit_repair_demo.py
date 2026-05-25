import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples"))

from run_no_credit_repair_demo import evaluate_packet  # noqa: E402


def test_no_credit_repair_blocks_action():
    packet = json.loads((ROOT / "examples" / "input.json").read_text(encoding="utf-8"))

    result = evaluate_packet(packet)

    assert result["allow_action"] is False
    assert result["credit_granted"] is False
    assert result["status"] == "NO_GO_REPAIR_REQUIRED"
    assert result["missing_receipts"] == ["exit", "terminal_join", "wait_policy"]

