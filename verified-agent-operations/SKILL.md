---
name: evidence-to-action-permission-gate
version: 0.2.0
description: Use a local model to propose a structured evidence packet, then require human review and a deterministic gate before an agent action.
---

# Evidence-to-Action Permission Gate

Use this Skill when a local agent needs to turn a local text source into a
reviewable candidate evidence packet before an action workflow continues.

## Boundary

The local model is an extractor, not a fact oracle and not an authorization
authority. It may propose a claim, evidence list, boundary, and uncertainties.
The output must remain `QUERY` until a human reviews the source and chooses an
explicit decision. Never send credentials, customer data, unreleased papers,
private prompts, or commercial thresholds to the Skill.

## Workflow

1. Read a local UTF-8 text or Markdown file.
2. Call the local Ollama adapter at `http://127.0.0.1:11434/api/generate`.
3. Inspect the returned candidate and its uncertainties.
4. Keep the case at `QUERY` unless a human has verified the source and boundary.
5. Run `gate.py` with the reviewed decision. `ACT` requires at least one evidence item.

## Public implementation

Repository: https://github.com/mmjbds/proof-carrying-action/tree/main/verified-agent-operations

Run:

```text
python local_evidence_packet_builder.py examples/source.txt --model gemma3:4b
python gate.py --json '{"decision":"QUERY","claim":"...","evidence":[],"boundary":"..."}'
```

The adapter rejects non-local endpoints, has no external side effects, and
does not replace production permissions, evidence provenance, or human review.
