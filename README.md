# Beta Receive Journal Flow

This prototype captures the beta test flow for the Life Journal feature.

## Core rule

The Life Journal mod must remain inactive until the physical journal has been delivered to the Sim's household.

## Flow

1. A Sim places an order for the Life Journal.
2. The order is created and tracked with a shipment status.
3. The journal moves through tracking states such as `created`, `shipped`, and `out_for_delivery`.
4. Once a carrier update reports `delivered`, the journal is considered received.
5. Only after delivery can the Life Journal mod be activated.
6. After the mod is active, the user can choose their Life Journal settings.

## Prototype contract

The repo includes the following prototype files:

- `prototypes/journal-delivery-flow.ts` — lifecycle logic for journal ordering, delivery, mod activation, and settings.
- `prototypes/journal-api.ts` — API-style contract for creating orders, tracking progress, confirming delivery, and activating the mod.
- `tests/prototype.spec.ts` — tests validating the delivery-gated activation flow.

## Key behavior

- `createJournalOrder(...)` creates a journal order in the `created` state.
- `updateOrderStatus(...)` moves the order through shipping stages.
- `canActivateLifeJournalMod(order)` returns `true` only when the journal is `delivered`.
- `activateLifeJournalMod(order)` throws if the journal has not been delivered yet.
- `configureLifeJournalSettings(...)` throws until activation has happened.

## Example sequence

```ts
const order = createJournalOrder("sim-42", "household-7", "123 Willow Lane", "TRK-9001");

const shipped = updateOrderStatus(order, "shipped");
const delivered = updateOrderStatus(shipped, "delivered");
const activated = activateLifeJournalMod(delivered);
const configured = configureLifeJournalSettings(activated, {
  reminderFrequency: "weekly",
  promptsEnabled: true,
  privacyMode: "private",
});
```

## Intended beta test

This is the intended beta behavior for the first release of the journal delivery system:

- Only begin the Life Journal mod after the journal is physically received.
- Allow post-delivery configuration for journaling preferences and notifications.
- Keep activation behind the delivery gate until the user has actually received the journal.
