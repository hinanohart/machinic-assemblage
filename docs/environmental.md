# Environmental axis — threshold and methodology

SPEC §3.3 says the environmental KPI is

```
environmental = min(1.0, max(0.0, 1 - kg / threshold))
```

where `kg` is `DeploymentContext.environmental_kgco2eq_estimate` and `threshold` defaults to
50 kgCO2eq per evaluation window.

## Why 50 kgCO2eq

It is a placeholder. The number is large enough that real production deployments hit it
quickly, and small enough that a small research deployment stays well below it. The intent
is to make the axis non-trivial without pretending we have a calibrated environmental model.

Operators should override the threshold via `environmental_threshold_kg=` when calling
`compute_three_ecologies()` and document their reasoning.

## Why not CodeCarbon

CodeCarbon is the obvious dependency. We do not pull it in for v0.1.0 because:

1. It adds a non-trivial install footprint to a protocol whose core dependency is one
   library (`pydantic`).
2. Its accuracy depends on the host's `intel_powergadget` / `nvidia-smi` availability,
   which makes the environmental axis silently bimodal across operators.
3. Real environmental accounting must account for the supply chain, not just runtime
   energy. CodeCarbon does not.

For v0.2.0 we will likely add an `[env]` extra that wires `compute_three_ecologies` to
CodeCarbon as one option among several, with an explicit per-method note about what is and
isn't covered. Until then: operators supply their own estimate or get `0.0` with a warning.

## What to put in the estimate

If you have CodeCarbon output: use it.

If you don't: an order-of-magnitude estimate is better than `None`. For comparison:

- Single API call to a frontier model: ~0.001 kgCO2eq (rough).
- One developer day on a laptop: ~0.5 kgCO2eq.
- One A100-day of training: ~5 kgCO2eq.

These are *order of magnitude*. The protocol does not care about precision; it cares about
honesty.

## os-climate

Tracked for v0.2.0; see `docs/open_questions.md`.
