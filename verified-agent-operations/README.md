# Evidence-to-Action Permission Gate

`Evidence-to-Action Permission Gate` is a small, dependency-free public
prototype for making an agent's next step explicit when evidence is incomplete.
It accepts synthetic cases and returns one of four visible states:

- `ACT`: the fixture lists at least one evidence item and a boundary.
- `WAIT`: defer while a condition is unresolved.
- `QUERY`: request a named source or missing field.
- `REFUSE`: keep a request outside the allowed public boundary.

The prototype validates structure; it does not decide whether a claim is true,
call a model, access the network, authorize money movement, control a robot, or
replace human review. The public examples are synthetic and have no external
side effects.

## Run

```text
python gate.py --demo
python gate.py --json '{"decision":"QUERY","claim":"Missing source","evidence":[],"boundary":"Ask first"}'
python -m unittest discover -s tests -v
```

## Release boundary

This repository contains only the public validator, schema-shaped fixtures,
`schema.json`, tests, and documentation. It excludes private prompts, answer keys, customer
data, provider receipts, production orchestration, deployment thresholds,
unreleased papers, and commercial algorithms. See
`docs/RELEASE_BOUNDARY_CN.md` before adding a fixture or integration.

## License

Code is released under the MIT License. Documentation is released under
Creative Commons Attribution 4.0 International unless a file states otherwise.
