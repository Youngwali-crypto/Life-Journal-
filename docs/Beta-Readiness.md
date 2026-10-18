# First playable beta milestone

Target: one Main Character, Finding My Lane, Chapter I, and the documented
Find Two Friends objective. This is a development target, not a released beta.

Acceptance criteria:
- A packaged mod loads on a recorded Sims 4 build without script errors.
- Starting the blueprint identifies one Sim and activates one objective.
- Existing qualifying friends count; repeated relationship events do not double count.
- Progress moves from 0/2 to 1/2 to 2/2 using actual gameplay relationships.
- Completion records one journal entry and exposes the next objective.
- Saving, exiting, and reloading preserves progress and journal history per save and Sim.
- Installation, update, removal, and a clean-save smoke test are documented and verified.

## Current development evidence

The standalone TypeScript prototype has 12 fixture tests. The Python event mapper
implements the interface exercised by the four existing Python tests. Neither
prototype demonstrates game integration, persistence, notifications, or mod packaging.
Event escalation is an explicit operation: its caller must verify blueprint permission
and elapsed Sim time. No automatic timer or escalation integration is implemented.

## Next implementation steps

1. Record the tester's game build and PC platform; verify its embedded Python version
   and relationship/event APIs against that build before writing an adapter.
2. Implement a game-independent objective state machine with stable Sim identities,
   distinct friend counting, idempotent completion, and serialization tests.
3. Build a narrow Sims adapter for active Sim selection, relationship detection,
   player notification, and save-scoped persistence using verified APIs.
4. Add packaging with the verified Python toolchain; keep game resources outside Git.
5. Run the acceptance checklist in game and record results before tagging a beta.

Full story generation, all five chapters, therapy, My Circle, and complex branching
are deferred from this first milestone.

## Local checks

From `/workspace/Life-Journal-` in the prepared cloud environment:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/.life-journal-tools/venv/bin/python -m pytest -p no:cacheprovider -q
/workspace/.life-journal-tools/node_modules/.bin/vitest run --config /workspace/.life-journal-tools/vitest.config.mjs
```

These checks exercise prototypes only. In-game acceptance remains required.
