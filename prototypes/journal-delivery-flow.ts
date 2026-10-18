export type JournalOrderStatus =
  | "created"
  | "processing"
  | "shipped"
  | "out_for_delivery"
  | "delivered";

export interface JournalSettings {
  reminderFrequency: "daily" | "weekly" | "monthly";
  promptsEnabled: boolean;
  privacyMode: "private" | "shared";
}

export interface JournalOrder {
  id: string;
  simId: string;
  householdId: string;
  shippingAddress: string;
  status: JournalOrderStatus;
  trackingId?: string;
  createdAt: string;
  deliveredAt?: string;
  modActivated: boolean;
  settings?: JournalSettings;
}

function iso(date: Date): string {
  return date.toISOString();
}

export function createJournalOrder(
  simId: string,
  householdId: string,
  shippingAddress: string,
  trackingId?: string
): JournalOrder {
  return {
    id: `journal-order-${simId}-${Date.now()}`,
    simId,
    householdId,
    shippingAddress,
    status: "created",
    trackingId,
    createdAt: iso(new Date()),
    modActivated: false,
  };
}

export function updateOrderStatus(
  order: JournalOrder,
  nextStatus: JournalOrderStatus
): JournalOrder {
  order.status = nextStatus;

  if (nextStatus === "delivered") {
    order.deliveredAt = iso(new Date());
    order.modActivated = false;
  }

  return order;
}

export function canActivateLifeJournalMod(order: JournalOrder): boolean {
  return order.status === "delivered" && Boolean(order.deliveredAt) && !order.modActivated;
}

export function activateLifeJournalMod(order: JournalOrder): JournalOrder {
  if (!canActivateLifeJournalMod(order)) {
    throw new Error(
      "Life Journal mod cannot activate until the journal has been delivered to the household."
    );
  }

  order.modActivated = true;
  return order;
}

export function configureLifeJournalSettings(
  order: JournalOrder,
  settings: JournalSettings
): JournalOrder {
  if (!order.modActivated) {
    throw new Error("Settings can only be configured after delivery and activation.");
  }

  order.settings = settings;
  return order;
}

export function simulateDeliveryTimeline(
  order: JournalOrder,
  stages: JournalOrderStatus[]
): JournalOrder[] {
  const timeline: JournalOrder[] = [order];

  stages.forEach(status => {
    const next = updateOrderStatus({ ...timeline[timeline.length - 1] }, status);
    timeline.push(next);
  });

  return timeline;
}

export const betaReceiveJournalFlow = {
  createJournalOrder,
  updateOrderStatus,
  canActivateLifeJournalMod,
  activateLifeJournalMod,
  configureLifeJournalSettings,
  simulateDeliveryTimeline,
};

// Example flow:
// 1. Sim orders the journal.
// 2. Journal is shipped and tracked.
// 3. The journal is delivered to the household.
// 4. Only after delivery is the Life Journal mod activated.
// 5. After activation, the user chooses their preferred settings.
