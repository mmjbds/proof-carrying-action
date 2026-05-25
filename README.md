# Proof-Carrying Action

A minimal reference protocol for high-risk AI actions that must carry evidence before they can be executed.

## Quick Start

```bash
python examples/run_no_credit_repair_demo.py --check
python -m pytest
```

## Core Idea

An AI recommendation is not an action unless it carries a closed proof packet: warrant, falsifier, receipts, null arms, regret attribution, and clean-learning status.

## What This Repository Provides

- Public schemas for warrants and receipts.
- A no-credit repair demo.
- A toy closure gap board.
- A claim-boundary verifier.

## What This Repository Does Not Do

- It does not trade.
- It does not provide financial advice.
- It does not connect to brokerage, robot, or customer systems.
- It does not release private production gates.

## Correct Interpretation

The first positive result of a proof-carrying action system can be restraint: knowing that it does not yet have proof to act.

See `CLAIM_BOUNDARY.md` before adapting the protocol to any real domain.
