# Gameplay connection: first skill-reading slice

Status: development prototype, not an installable or in-game-validated mod.

## Implemented

- `GameplayBridge` routes an absolute skill level to one explicitly bound objective in the existing transactional StoryFlow.
- Context includes save, household, Main Character, and a unique loaded-session token. Close the bridge at unload; stale callbacks must retain their original token and are rejected.
- The optional `S4CLSkillReader` resolves the selected Sim, checks household membership, and reads a skill without adding or changing it. It excludes temporary effective-level bonuses. S4CL is an experimental backend, not yet a required dependency of the released mod.
- Existing skill levels count toward a reach-level objective. Only whole levels count in this slice. Lower levels do not remove earned progress; repeated observations do not refresh inactivity timestamps.
- Skill observations can trigger completion, chapter transition, and Journal entries. Sim-minute ticks can trigger expiry and carryover. Paused/completed stories are ignored.

## Integration contract

1. Load the Journal data associated with the exact game-save revision. The current standalone SQLite store does NOT implement save rollback/Save As synchronization.
2. Create a fresh GameplayContext and bridge for the selected story. Use canonical decimal strings for Sim and household IDs. The save ID and load token are supplied by bootstrap, never inferred from a Sim.
3. Bind one known skill tuning ID to a reach-level objective whose target is the desired skill level. Skill IDs must be verified against the installed game; no IDs are guessed here.
4. On the game thread, call reader.observe(bridge, context, objective_id, skill_id, absolute_sim_minutes). This is a live observation, not historical catch-up. Do not replace observation time with real-world time or time-of-day.
5. Call bridge.tick(context, absolute_sim_minutes) after observations, including when a skill is unavailable. No scheduler is installed by these modules.
6. Close and discard the bridge on save unload/switch. A fresh token rejects old callbacks but does not restore an older SQLite snapshot: save synchronization must precede automatic operation.

Calls are serial. Multiple simultaneous skill objectives and batch atomicity are not covered by this first slice. Late observations use the current StoryFlow expiry rules. An objective removed by a chapter transition cannot be credited retroactively.

## Still required before an in-game build

- Verify installed Sims 4 version/Python runtime and S4CL compatibility.
- Verify SQLite availability or provide a suitable persistence backend.
- Implement save/load lifecycle, game-clock extraction, callback registration/cleanup, and save-revision synchronization.
- Add sub-level skill progress so practicing without leveling up can protect against inactivity. Do not advertise complete activity detection yet.
- Add friendship, career, and completed-interaction readers with explicit objective semantics.
- Package the mod, run in a disposable test save, and verify reload, travel, pause, household changes, and an older-save load.

## Sources inspected

S4CL primary source and API documentation, inspected 2026-11-08:

- https://github.com/DeviantGameMods/Sims4CommunityLibrary/blob/main/Scripts/sims4communitylib/utils/sims/common_sim_skill_utils.py (`get_skill`, `get_current_skill_level`)
- https://github.com/DeviantGameMods/Sims4CommunityLibrary/blob/main/Scripts/sims4communitylib/utils/sims/common_household_utils.py
- https://sims4communitylibrarywiki.readthedocs.io/en/latest/sims4communitylib.utils.sims.html (`CommonSimUtils.get_sim_info`, `get_sim_id`, `CommonHouseholdUtils.get_household_id`)

These establish the experimental reader API; they do not establish compatibility with the user's installed game patch.

## Validation

Eight new unittest scenarios cover skill completion/reload, session and identity isolation, paused/closed sessions, repeated/lower levels, failed-write retry, Sim-time expiry, read-only S4CL calls, and invalid/unavailable data. S4CL calls use injected test doubles; no game runtime was available.
