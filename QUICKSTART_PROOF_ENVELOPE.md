# Quickstart: Proof Envelope

Run:

```bash
python examples/run_no_credit_repair_demo.py --check
```

Expected outcome:

- The packet is valid as a repair work order.
- The packet is not allowed to act.
- The missing proof fields are listed.
- The no-credit policy remains active.

This is the intended behavior. A proof-carrying action system can produce a positive result by refusing to act when proof is incomplete.

