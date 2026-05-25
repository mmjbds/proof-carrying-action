"""Run a toy proof-carrying action check.

This demo uses synthetic data only. It does not connect to any brokerage,
robotics system, customer workflow, or production action gate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_RECEIPTS = ("entry", "exit", "terminal_join", "wait_policy", "counterfactual")


def evaluate_packet(packet: dict) -> dict:
    receipts = packet.get("receipts", {})
    closed = [name for name in REQUIRED_RECEIPTS if receipts.get(name)]
    missing = [name for name in REQUIRED_RECEIPTS if not receipts.get(name)]
    no_credit = packet.get("credit_policy") == "NO_CREDIT_REPAIR_INTENT_ONLY"
    allow_action = not missing and not no_credit and packet.get("warrant", {}).get("risk_gate") == "open"

    return {
        "action_id": packet.get("action_id"),
        "allow_action": allow_action,
        "closed_receipts": closed,
        "missing_receipts": missing,
        "credit_granted": bool(allow_action),
        "status": "ACTION_ALLOWED" if allow_action else "NO_GO_REPAIR_REQUIRED",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a toy proof-carrying action packet.")
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("input.json"))
    parser.add_argument("--expected", type=Path, default=Path(__file__).with_name("expected_output.json"))
    parser.add_argument("--check", action="store_true", help="Compare against expected output.")
    args = parser.parse_args()

    packet = json.loads(args.input.read_text(encoding="utf-8"))
    result = evaluate_packet(packet)
    print(json.dumps(result, indent=2, sort_keys=True))

    if args.check:
        expected = json.loads(args.expected.read_text(encoding="utf-8"))
        if result != expected:
            raise SystemExit("Proof-envelope check failed.")


if __name__ == "__main__":
    main()

