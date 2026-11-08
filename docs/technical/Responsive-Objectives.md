# Story-responsive objectives

## Implemented

`ResponsiveStoryFlow` extends StoryFlow with a saved, immutable pool of authored rules, a complete context snapshot, limited focus previews, and explicit player selection. Each rule belongs to one Blueprint, names eligible chapters, matches exact typed facts, and defines its objective, requirement flag, target, deadline and optional relevance list.

Trusted game/choice adapters call `update_story_context(story_id, facts, now, event_id)` with a complete verified snapshot. Omitted facts become unknown; missing conditions never match. No text interpretation or invented conflict is used. Context receipt IDs prevent replay from restoring stale facts.

The Journal Objectives page exposes at most two eligible response choices in authored rule order. This ordering is a prototype display policy, not urgency-based focus selection. Only the player activates a response via `choose_response`. Choosing consumes that rule once per story, starts its deadline at selection, updates tracked objective IDs and writes a Journal record atomically. A failed write rolls everything back. Previewing starts no timer and creates no required work.

Selected objectives then use existing StoryFlow progress, chapter handoff, required carryover and optional relevance behavior. Current objectives remain active until completed or processed by the chapter rules. Changing context withdraws unselected options; it does not erase already-selected responsibilities. Paused stories cannot choose a new response. Old timestamps and changed retry payloads are rejected. Choices are checked again at submission so stale menus cannot activate an ineligible response.

## Entry points

1. Use ResponsiveStoryFlow wherever StoryFlow was constructed.
2. Start the Blueprint and call configure_responses with its authored rule pool. Existing stories can opt in without losing stored objectives. Reconfiguring a different pool requires a migration.
3. Supply complete context snapshots on verified game changes and explicit story choices, using absolute Sim minutes and stable occurrence IDs.
4. Pass that same flow to JournalInterface. The native dialog adapter adds up to two Focus buttons under Objectives.
5. Complete selected objectives through the normal progress adapter. Candidate eligibility is not evidence of objective completion.

The API is game-independent; caller/session/save/Sim verification remains the existing bridge/bootstrap responsibility. No new automatic gameplay detectors are claimed here.

## Example content, not finalized story design

The example rule factory uses three required possibilities and one optional possibility: new career direction after unemployment, following up on support received, exploring a major when enrolled and choosing education, and celebrating a promotion. Durations, required flags, wording, and completion detection are illustrative test content. No particular Sim or relationship is invented. Before shipping targeted social objectives, bind the actual supporting Sim as well as the trigger.

## Limits

- This limits response previews, not all legacy fixed-plan objectives. Legacy chapter plans still activate their full fixed list. It is not a full replacement for chapter-level reveal sequencing.
- Unchosen candidates never gate progression; all selected required work participates normally. This does not enforce a final required/optional ratio for every possible selected path.
- Context is an exact fact snapshot, not a history inference engine, ranking model or text generator. Active-objective adaptation/cancellation, branching outcome effects, relationship-target binding, eligibility expiry, and focus-switch pause timers remain follow-ups.
- Authored rules are consumed once per story; repeatable responses need a separate occurrence policy.
- Rules cannot share objective IDs with the static plan. Blueprint/chapter scope is validated at configuration.
- Calls run serially on the game thread. The loaded-save integration and in-game testing remain pending.

## Validation

Ten new tests cover contextual eligibility and two-item previews, changed/unknown facts, choice-time deadlines, completion gates, required carryover, retry/reload protection, Journal-write rollback, pause/time validation, Journal focus integration, and optional/unselected objectives not blocking progression. All 58 local unittest tests pass. Existing function tests are also run directly; Python 3.7 grammar checking is not an installed-game runtime test.
