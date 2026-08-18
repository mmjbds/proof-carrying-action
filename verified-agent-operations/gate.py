"""Small, dependency-free evidence-to-action permission gate.

This public package is a toy validator for synthetic evidence only. It is not
an authorization service, safety certification, or production policy engine.
"""

from __future__ import annotations

import argparse
import json
from typing import Any, Mapping


DECISIONS = frozenset({"ACT", "WAIT", "QUERY", "REFUSE"})
REQUIRED_FIELDS = ("decision", "claim", "evidence", "boundary")


class GateError(ValueError):
    """Raised when a gate input violates the public schema."""


def validate_case(case: Mapping[str, Any]) -> dict[str, Any]:
    """Return a normalized case or raise ``GateError``.

    The validator deliberately checks structure and explicit boundary text. It
    does not infer truth, rank evidence, call a model, or authorize a real
    action.
    """
    missing = [field for field in REQUIRED_FIELDS if field not in case]
    if missing:
        raise GateError(f"missing required fields: {', '.join(missing)}")

    decision = case["decision"]
    if decision not in DECISIONS:
        raise GateError("decision must be ACT, WAIT, QUERY, or REFUSE")

    claim = case["claim"]
    boundary = case["boundary"]
    evidence = case["evidence"]
    if not isinstance(claim, str) or not claim.strip():
        raise GateError("claim must be a non-empty string")
    if not isinstance(boundary, str) or not boundary.strip():
        raise GateError("boundary must be a non-empty string")
    if not isinstance(evidence, list):
        raise GateError("evidence must be a list")
    if any(not isinstance(item, str) or not item.strip() for item in evidence):
        raise GateError("each evidence item must be a non-empty string")

    if decision == "ACT" and not evidence:
        raise GateError("ACT requires at least one evidence item")
    if decision in {"WAIT", "QUERY", "REFUSE"} and not evidence:
        status = "no evidence" if decision != "REFUSE" else "refusal without evidence"
    else:
        status = "evidence listed"

    return {
        "decision": decision,
        "claim": claim.strip(),
        "evidence": [item.strip() for item in evidence],
        "boundary": boundary.strip(),
        "status": status,
    }


def run_demo() -> None:
    """Print deterministic examples for a reviewer or a short demo video."""
    examples = (
        {
            "decision": "ACT",
            "claim": "A synthetic fixture contains the required fields.",
            "evidence": ["fixture:allow-001", "validator:required-fields"],
            "boundary": "Synthetic example only; no external side effect.",
        },
        {
            "decision": "QUERY",
            "claim": "The requested action lacks a named evidence source.",
            "evidence": [],
            "boundary": "Ask for a source before any action is considered.",
        },
        {
            "decision": "REFUSE",
            "claim": "The request would disclose private material.",
            "evidence": [],
            "boundary": "Private prompts, credentials, and customer data stay private.",
        },
    )
    for example in examples:
        try:
            print(json.dumps(validate_case(example), ensure_ascii=False, sort_keys=True))
        except GateError as error:
            print(json.dumps({"error": str(error)}, ensure_ascii=False, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="print deterministic synthetic examples")
    parser.add_argument("--json", type=str, help="validate one JSON object")
    args = parser.parse_args()
    if args.demo:
        run_demo()
        return
    if args.json:
        try:
            value = json.loads(args.json)
            print(json.dumps(validate_case(value), ensure_ascii=False, sort_keys=True))
        except (json.JSONDecodeError, GateError) as error:
            parser.error(str(error))
        return
    parser.error("use --demo or --json")


if __name__ == "__main__":
    main()
