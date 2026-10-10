# Extensible cryptic clue example library

`editorial/clue-examples.json` is the canonical, append-only-in-spirit example collection.

## Adding an example

Add a JSON object to `examples` with a stable unique `id`, exact `clue`, `answer`, `device` array, `parse`, `definition`, `surface`, transferable `lesson`, `provenance`, `status` and `tags`. Use statuses `reference`, `draft`, `rejected`. Do not call a draft a verified reference.

Prefer examples supplied by solvers or published examples where quotation is permitted. Capture provenance and avoid wholesale reproduction of published clue collections. Check the exact parse; record any looseness in the definition.

## How the composer should use it

1. Retrieve **contrasting** examples by relevant device, surface opportunity and failure mode.
2. Extract a **transferable principle** from each; do not copy its phrasing or insist on its mechanism.
3. Explore unrelated devices and lateral constructions as well.
4. Generate candidate surfaces, mechanically check supported operations, and submit for editorial assessment.
5. Feed newly accepted and rejected candidates back into the library with explanations.
6. Periodically inspect for overrepresented devices and repetitive surface settings.

Run `python scripts/validate_clue_examples.py` to check structure and basic consistency. This validation does **not** certify clue fairness or literary quality.
