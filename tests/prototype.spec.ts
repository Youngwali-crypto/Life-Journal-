import {
  createJournalOrder,
  updateOrderStatus,
  activateLifeJournalMod,
  configureLifeJournalSettings,
  canActivateLifeJournalMod,
  type JournalOrder,
} from "../prototypes/journal-delivery-flow";

describe("beta receive journal flow", () => {
  it("T13 createJournalOrder starts in created state and keeps the mod locked", () => {
    const order = createJournalOrder("sim-42", "household-7", "123 Willow Lane");

    expect(order.status).toBe("created");
    expect(order.modActivated).toBe(false);
    expect(canActivateLifeJournalMod(order)).toBe(false);
  });

  it("T14 delivery unlocks the mod only after the journal reaches the home", () => {
    const order = createJournalOrder("sim-42", "household-7", "123 Willow Lane");
    const shipped = updateOrderStatus(order, "shipped");
    const delivered = updateOrderStatus(shipped, "delivered");

    expect(delivered.status).toBe("delivered");
    expect(delivered.deliveredAt).toBeTruthy();
    expect(canActivateLifeJournalMod(delivered)).toBe(true);
  });

  it("T15 activation is rejected before delivery and settings are gated until activation", () => {
    const order = createJournalOrder("sim-42", "household-7", "123 Willow Lane");

    expect(() => activateLifeJournalMod(order)).toThrow(
      "Life Journal mod cannot activate until the journal has been delivered to the household."
    );

    const afterDelivery = updateOrderStatus(order, "delivered");
    const activated = activateLifeJournalMod(afterDelivery);

    expect(activated.modActivated).toBe(true);
    expect(() =>
      configureLifeJournalSettings(afterDelivery, {
        reminderFrequency: "weekly",
        promptsEnabled: true,
        privacyMode: "private",
      })
    ).toThrow("Settings can only be configured after delivery and activation.");

    expect(
      configureLifeJournalSettings(activated, {
        reminderFrequency: "weekly",
        promptsEnabled: true,
        privacyMode: "private",
      }).settings
    ).toEqual({
      reminderFrequency: "weekly",
      promptsEnabled: true,
      privacyMode: "private",
    });
  });
});
