# Hiccups, Hurdles, and Crossroads

## Status and purpose

Status: Design draft. No gameplay implementation.

This document expands the existing concepts in the [Life Journal Overview](../Life-Journal-Overview.md) and [Story Blueprint System](Story%20Blueprint-System.md).

Existing core principles are preserved. New timing ranges, event examples, escalation thresholds, and scheduling rules below are proposals for review, not finalized decisions or verified Sims 4 capabilities.

## Core distinctions

| System | Story purpose | Player experience |
| --- | --- | --- |
| Hiccup | A smaller, short-term complication | Something needs attention; the story can continue through several responses. |
| Hurdle | A significant obstacle or ongoing conflict | The Sim must adapt, seek support, change direction, or live with an unresolved issue. |
| Crossroad | A meaningful decision between reasonable paths | The player chooses what matters now, with tradeoffs that can shape later events. |

A Hiccup does not always escalate. A Hurdle can arise without a preceding Hiccup. A Crossroad can occur during either complication or during ordinary story progression.

Choices should create context, not a visible good-versus-bad score.

## Chapter placement for Finding My Lane

| Chapter | Role of these systems |
| --- | --- |
| I — Branching Out | Keep discovery low pressure. Any complication should support exploration rather than establish major outside conflict. |
| II — Choosing My Lane | Introduce smaller Hiccups and early Crossroads tied to emerging friendships, interests, career, education, or romance. |
| III — Outside Noise | Use established routes and earlier decisions to create stronger Hurdles, competing priorities, and consequential Crossroads. |

Chapter III should feel like a shift because meaningful choices begin producing stronger consequences. It should not generate unrelated drama simply because a chapter changed.

## Shared event design

Every event should describe:

- Stable event ID and title.
- Blueprint, chapter, and relevant route.
- Eligibility: relationships, prior decisions, gameplay context, and required packs.
- Trigger: what makes this event appropriate now.
- Involved Sims and what happens if one becomes unavailable.
- Player-facing explanation of why it appeared.
- Response options and any follow-up objectives.
- Timing: decision deadline, objective deadline, and any ongoing resolution period.
- Immediate and possible later consequences.
- What the Journal records.
- Repeat rules, cooldown, and conflict with other active events.
- Content boundaries and fallback when required gameplay is unavailable.

Separate decision timing from follow-through. Selecting “talk to my friend” is a commitment; the conversation objective may still need to be completed.

Whether actions can be detected automatically requires technical research. A player confirmation may be used where appropriate, but must be identified explicitly.

## Hiccups

### Proposed response rules

Do not use one universal one-day response timer.

For review, use a short, event-specific response window, with **6–18 Sim hours** as a starting range for everyday Hiccups. A scheduled event may instead use its actual start time. These values are proposals and must be tested for playability.

A Hiccup may offer responses such as:

- Address the issue directly.
- Ask a relevant Sim for help.
- Reschedule or make a smaller commitment.
- Set a boundary.
- Let the opportunity pass.

Letting something pass is not automatically failure. The consequence should match what the Sim actually missed or left unresolved.

### Draft Chapter II examples

| Hiccup | Eligibility and trigger | Responses | Possible follow-through |
| --- | --- | --- | --- |
| Left on Read | A developing friendship has an unanswered invitation; detection method remains open. | Follow up, suggest another time, give space. | A new invitation objective or an unresolved expectation. One unanswered message alone should not produce a major conflict. |
| Pulled in Two Directions | A hobby commitment and an invitation overlap. | Keep the hobby plan, join the friend, reschedule one. | Reinforce one emerging route while leaving another opportunity for later. |
| A Comment That Sticks | A relevant friend questions an interest the Sim has repeatedly pursued. | Explain its importance, brush it off, seek another perspective. | Reflection, a conversation objective, or evidence of a repeated unsupportive pattern. |
| Falling Behind | An education route is active and a relevant coursework objective remains incomplete. | Catch up, ask for support, adjust social plans. | Resolve the backlog or retain context for an education Hurdle if the pattern continues. |

These events must not assume that an invitation, comment, or conflict happened unless it is observed in gameplay or clearly introduced as a Life Journal story event.

### Escalation proposal

Escalation requires a related pattern, an important unresolved commitment, or an explicit major story trigger.

For an initial design test, consider a Hurdle after **two related unresolved Hiccups**, provided the issue is still relevant. This threshold is provisional. Unrelated Hiccups must not be pooled into one punishment counter.

Before escalation, explain the unresolved pattern to the player. A single ordinary missed opportunity should usually remain a small event.

## Hurdles

### Proposed resolution rules

A Hurdle should support several responses and may involve a sequence of objectives.

Use **2–5 Sim days** as a provisional range for a manageable multi-step response, only when a deadline serves the story. Some conflicts should instead remain active until a relevant milestone or resolution. Do not force every Hurdle onto a timer.

Distinguish:

- Resolved: the issue is addressed.
- Adapted: the Sim changes plans or accepts a new direction.
- Ongoing: the issue remains part of the story.
- Closed by changed circumstances: the original problem no longer applies.

These are narrative outcomes, not a ranking of the player.

### Draft Chapter III examples

| Hurdle | Relevant trigger | Reasonable paths | Possible story change |
| --- | --- | --- | --- |
| My Circle Is Pulling Me Apart | Repeated conflicting expectations among relevant Circle members. | Bring people together, maintain separate friendships, set boundaries, step back. | Change who receives attention or belongs in My Circle; generate relationship objectives. |
| This Lane Is Costing Me | A strong career or education route repeatedly conflicts with another valued route. | Reduce commitments, seek support, renegotiate priorities, explore another direction. | Adapt the current route rather than treating a change of mind as defeat. |
| Support With Conditions | A relevant Sim repeatedly offers support only if the Main Character follows their preferred path. | Accept the arrangement, negotiate, seek independent support, decline. | Affect reliance, boundaries, and later relationship events. |
| The Interest Nobody Takes Seriously | A chosen hobby repeatedly receives dismissive responses in established story events. | Keep pursuing it, find a supportive community, explain its value, reconsider it. | Develop independence, new relationships, or a different interest. |

Story consequences and actual game effects must be distinguished. A Journal record or follow-up objective does not automatically change a relationship score, career, or academic result.

## Crossroads

### Choice rules

Present two to four understandable options where practical. Explain the immediate commitment without revealing exact ending formulas.

Each option should have:

- A clear reason a player might choose it.
- An immediate consequence or follow-up objective.
- A possible later consequence.
- An outcome if promised follow-through does not happen.

A choice may prioritize one route without permanently locking out others.

Offer “not now,” a delay, or an alternative when the situation allows it. If timing is essential, state the deadline and what happens when it expires. Expiry must not silently select a major life decision for the player.

### Draft Crossroad 1 — Same Night, Different Plans

Chapter II or III. Requires an established social route and a relevant career opportunity.

| Choice | Immediate direction | Possible later effect |
| --- | --- | --- |
| Go with friends | Prioritize the social plan. | Reinforce connection; another career opportunity may be needed. |
| Attend the networking event | Prioritize career exploration. | Create a career follow-up; a friend may want to reconnect. |
| Attempt both | Commit to a feasible split plan. | Gain both experiences or create a missed commitment if the plan falls through. |
| Wait for friends | Ask whether friends will join the opportunity. | Shared support if they agree; a new decision if they decline or the opportunity expires. |

“Attempt both” needs a feasible schedule. It should not guarantee double rewards.

### Draft Crossroad 2 — Is This My Lane, or Their Plan?

Chapter III. Requires a developed route and established outside pressure.

- Continue the chosen route while setting a boundary.
- Try the other Sim's suggestion as a limited experiment.
- Pause and reflect before committing.
- Seek another perspective from a relevant Circle member.

Trying advice should remain reversible where practical. It should not automatically mean the Main Character has lost independence.

### Draft Crossroad 3 — Who Gets My Time?

Chapter II or III. Requires two relationships with competing needs.

- Support one Sim now and make a later plan with the other.
- Reverse those priorities.
- Suggest a shared activity when appropriate.
- State that the Main Character needs time for themselves.

Follow-up should depend on expectations and actions, not assume every unchosen Sim becomes hostile.

### Draft Crossroad 4 — Keep Going, or Change Direction?

Chapter III. Requires a developed route that has encountered a meaningful Hurdle.

- Continue with a revised plan.
- Seek help before deciding.
- Explore an alternative while retaining the current route.
- Step away and begin a different direction.

Both persistence and changing direction can lead to legitimate endings.

## Scheduling and player control — proposals

- Begin with one active Hiccup and one active Hurdle at most; validate the workload before expanding.
- Avoid overlapping urgent decisions.
- Suppress duplicate events and use an event-specific cooldown before repetition.
- Match story intensity to player settings and boundaries.
- Use Sim time for gameplay deadlines; pause behavior during loading, menus, travel, and inactive-household play requires research.
- When a story is intentionally paused, explain what happens to its events and timers.
- Do not delete an event's history when its circumstances change.
- If a target Sim becomes unavailable, adapt or close the event without treating the player as having failed automatically.

## Journal and endings

Record the event, relevant context, choice, follow-through, and outcome. Keep the player's interpretation separate from automatic records.

Ending evaluation may consider patterns of choices and outcomes across the Blueprint. One ordinary Hiccup should not decide the ending on its own. Different endings remain legitimate conclusions.

## Design walkthrough

Chapter II: The Sim repeatedly pursues painting and develops a friendship.

A Comment That Sticks introduces a friend's dismissive response as a clearly identified story event.

The player explains why painting matters and completes the follow-up conversation objective.

The Journal records the response. The event resolves; escalation is unnecessary.

If similar dismissive events remain unresolved later, Chapter III may make The Interest Nobody Takes Seriously eligible.

That Hurdle can introduce Is This My Lane, or Their Plan? A revised plan, supportive new relationship, or changed interest can all be meaningful outcomes.

This is an illustrative path, not a mandatory sequence.

## Open decisions and technical research

Design decisions still needing review:

- Hiccup timing ranges and exceptions.
- Hurdle timing and which events have no deadline.
- Escalation thresholds and repeat cooldowns.
- Simultaneous-event limits.
- Final event wording, response options, and chapter eligibility.

Technical research still needed:

- Reliable gameplay triggers and relationship observation.
- Sim-time timers and inactive-household behavior.
- Notification and choice UI capabilities.
- Follow-through detection and manual confirmation.
- Persistent event state, save/reload, and update migration.
- Optional pack requirements and fallback behavior.

These systems remain outside the first basic objective prototype. Once that loop works, a later small test can exercise one Hiccup, one Crossroad, and one Hurdle before expanding the event catalog.
