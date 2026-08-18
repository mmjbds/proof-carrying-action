"""Build a human-reviewable evidence candidate with a local Ollama model.

The model is an extractor only. This module never turns a model response into
an authorized action. Callers must review the candidate and choose an explicit
gate decision before using ``gate.validate_case``.
"""

from __future__ import annotations

import argparse
import json
from typing import Any, Callable, Mapping
from urllib.parse import urlparse
from urllib.request import Request, urlopen


DEFAULT_ENDPOINT = "http://127.0.0.1:11434/api/generate"
DEFAULT_MODEL = "gemma3:4b"
ALLOWED_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
REQUIRED_FIELDS = ("claim", "evidence", "boundary")


class BuilderError(ValueError):
    """Raised when a local model candidate cannot be used safely."""


def _assert_local_endpoint(endpoint: str) -> None:
    parsed = urlparse(endpoint)
    if parsed.scheme != "http" or parsed.hostname not in ALLOWED_HOSTS:
        raise BuilderError("endpoint must be a local HTTP Ollama endpoint")
    if parsed.path.rstrip("/") != "/api/generate":
        raise BuilderError("endpoint must point to Ollama /api/generate")


def _request_local_model(
    endpoint: str,
    model: str,
    prompt: str,
    request_fn: Callable[..., Any] = urlopen,
) -> Mapping[str, Any]:
    _assert_local_endpoint(endpoint)
    body = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0, "num_predict": 512},
        }
    ).encode("utf-8")
    request = Request(endpoint, data=body, headers={"Content-Type": "application/json"})
    try:
        with request_fn(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as error:  # pragma: no cover - concrete transport errors vary
        raise BuilderError(f"local model call failed: {error}") from error
    if not isinstance(payload, dict):
        raise BuilderError("local model response must be a JSON object")
    return payload


def _decode_candidate(response: Mapping[str, Any]) -> dict[str, Any]:
    raw = response.get("response")
    if isinstance(raw, str):
        try:
            candidate = json.loads(raw)
        except json.JSONDecodeError as error:
            raise BuilderError("local model response is not valid JSON") from error
    else:
        candidate = raw
    if not isinstance(candidate, dict):
        raise BuilderError("local model candidate must be a JSON object")

    missing = [field for field in REQUIRED_FIELDS if field not in candidate]
    if missing:
        raise BuilderError(f"candidate missing fields: {', '.join(missing)}")
    claim = candidate["claim"]
    boundary = candidate["boundary"]
    evidence = candidate["evidence"]
    if not isinstance(claim, str) or not claim.strip():
        raise BuilderError("candidate claim must be a non-empty string")
    if not isinstance(boundary, str) or not boundary.strip():
        raise BuilderError("candidate boundary must be a non-empty string")
    if not isinstance(evidence, list) or any(
        not isinstance(item, str) or not item.strip() for item in evidence
    ):
        raise BuilderError("candidate evidence must be a list of non-empty strings")
    uncertainties = candidate.get("uncertainties", [])
    if not isinstance(uncertainties, list) or any(
        not isinstance(item, str) or not item.strip() for item in uncertainties
    ):
        raise BuilderError("candidate uncertainties must be a list of non-empty strings")
    return {
        "claim": claim.strip(),
        "evidence": [item.strip() for item in evidence],
        "boundary": boundary.strip(),
        "uncertainties": [item.strip() for item in uncertainties],
        "review_required": True,
    }


def build_candidate_packet(
    text: str,
    model: str = DEFAULT_MODEL,
    endpoint: str = DEFAULT_ENDPOINT,
    request_fn: Callable[..., Any] = urlopen,
) -> dict[str, Any]:
    """Extract a candidate packet; the result always requires human review."""
    if not isinstance(text, str) or not text.strip():
        raise BuilderError("input text must be non-empty")
    prompt = (
        "Extract a conservative evidence candidate from the text below. "
        "Return only JSON with string claim, string-array evidence, string "
        "boundary, and string-array uncertainties. Do not invent sources. "
        "If a source or boundary is absent, say so in uncertainties.\n\n"
        f"TEXT:\n{text.strip()}"
    )
    response = _request_local_model(endpoint, model, prompt, request_fn=request_fn)
    return _decode_candidate(response)


def to_gate_case(candidate: Mapping[str, Any], decision: str = "QUERY") -> dict[str, Any]:
    """Attach an explicit human-selected decision without auto-authorizing it."""
    if decision not in {"ACT", "WAIT", "QUERY", "REFUSE"}:
        raise BuilderError("decision must be ACT, WAIT, QUERY, or REFUSE")
    return {
        "decision": decision,
        "claim": candidate["claim"],
        "evidence": list(candidate["evidence"]),
        "boundary": candidate["boundary"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="UTF-8 local text or Markdown file")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--decision", choices=("ACT", "WAIT", "QUERY", "REFUSE"), default="QUERY")
    args = parser.parse_args()
    try:
        from pathlib import Path

        text = Path(args.input).read_text(encoding="utf-8")
        candidate = build_candidate_packet(text, model=args.model, endpoint=args.endpoint)
        print(json.dumps({"candidate": candidate, "gate_case": to_gate_case(candidate, args.decision)}, ensure_ascii=False, indent=2))
    except (OSError, BuilderError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
