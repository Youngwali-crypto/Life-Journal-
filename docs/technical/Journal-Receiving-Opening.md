# Receiving and opening Life Journal

## Implemented prototype

`JournalAccess` persists one order per save/Sim. Its flow is:

Order → Await delivery → Confirmed receipt → First-open setup → Free Journal → Journal interface.

The order uses absolute Sim minutes and a caller-supplied delivery delay. Repeated order actions return the existing order without restarting its timer. Receipt confirmation validates order, save, Sim, household, and due time. A stable receipt ID makes repeated delivery callbacks idempotent. A receipt ID cannot be reused for a different order in the same save.

Receiving unlocks setup; it does not activate a Blueprint or choose a Main Character. Start a Free Journal activates participation and opens the existing native Journal interface. Decide Later leaves setup pending. Later openings bypass setup. Ordering, receiving, and starting each create one Journal history record in the same SQLite transaction as their state change. Failed history writes roll back the whole change.

History belongs to the Sim. No persistent history is keyed by a physical object handle, and this prototype has no history deletion on object loss.

## Native UI integration

Construct `JournalAccessDialogs(access, dialogs, household_id, delivery_minutes)` with the existing S4CLJournalDialogs instance, verified household, and selected delay. Route the future order/open interaction to `.open()`. The dialog controller checks the Journal's current-session guard before actions. There is no player-facing manual receipt button.

A trusted physical-delivery adapter must call `receive(save_id, sim_id, household_id, order_id, receipt_id, now)` only after verifying the Journal reached the intended recipient. Passing due time alone is insufficient. Persist/reuse delivery identity across retries. Reconcile household moves instead of silently delivering to another household.

Game object creation/inventory delivery and SQLite writes are not one atomic transaction. The future adapter must recover from a crash between creating the object and recording receipt without spawning another object. No automatic spawning is provided until that protocol and object tuning are verified.

## Decisions intentionally left open

- Computer versus phone ordering, physical journal asset, mailbox versus inventory, delivery delay, and Simoleon cost.
- No funds are deducted and no real-world shipping addresses or carrier integrations are used.
- Generate My Story and Choose a Story Blueprint remain planned setup options. They are not exposed as working buttons because the selection/generation handlers do not exist. The development setup screen says so and offers Free Journal.
- Transferring journals, replacement orders, existing free-journal migration and household-move handling need explicit policies. One order per save/Sim is the current prototype restriction.

The earlier in-memory delivery prototype on PR #6 remains untouched; it uses wall-clock timestamps. This game-specific service does not import or migrate those orders.

## Not yet an in-game delivery

The native launch interaction, Journal object/tuning, actual object creation/delivery, startup and save callbacks, save rollback synchronization, and mod packaging are still absent. Tests use ordinary Python and dialog stand-ins. No claim is made that the Journal arrives in a running Sims 4 game yet. This change provides the persistent lifecycle and interface routing those hooks will call.

## Verification

Eight new tests cover lifecycle/reload, duplicate actions, invalid recipients and early receipts, transactional receipt failure, activation rollback, owner-scoped Free Journal entries, native UI routing, and invalid/stale actions. All 48 local unittest tests pass. New files parse with Python 3.7 grammar; this is not installed-game runtime validation.
