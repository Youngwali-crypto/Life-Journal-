import {
  createJournalOrder,
  activateLifeJournalMod,
  configureLifeJournalSettings,
  canActivateLifeJournalMod,
  type JournalOrder,
  type JournalOrderStatus,
  type JournalSettings,
  updateOrderStatus,
} from "./journal-delivery-flow";

export interface CreateJournalOrderRequest {
  simId: string;
  householdId: string;
  shippingAddress: string;
  trackingId?: string;
}

export interface UpdateTrackingRequest {
  trackingId: string;
  status: JournalOrderStatus;
}

export interface JournalApiState {
  orders: Record<string, JournalOrder>;
}

export function createJournalApiState(): JournalApiState {
  return { orders: {} };
}

export function createOrderApi(
  state: JournalApiState,
  request: CreateJournalOrderRequest
): JournalOrder {
  const order = createJournalOrder(
    request.simId,
    request.householdId,
    request.shippingAddress,
    request.trackingId
  );

  state.orders[order.id] = order;
  return order;
}

export function getOrderApi(
  state: JournalApiState,
  orderId: string
): JournalOrder | undefined {
  return state.orders[orderId];
}

export function updateTrackingApi(
  state: JournalApiState,
  request: UpdateTrackingRequest
): JournalOrder | undefined {
  const order = Object.values(state.orders).find(
    candidate => candidate.trackingId === request.trackingId
  );

  if (!order) {
    return undefined;
  }

  const updatedOrder = updateOrderStatus(order, request.status);
  state.orders[order.id] = updatedOrder;
  return updatedOrder;
}

export function confirmDeliveryApi(
  state: JournalApiState,
  orderId: string
): JournalOrder {
  const order = state.orders[orderId];
  if (!order) {
    throw new Error(`Order ${orderId} not found.`);
  }

  const delivered = updateOrderStatus(order, "delivered");
  state.orders[order.id] = delivered;
  return delivered;
}

export function activateJournalModApi(
  state: JournalApiState,
  orderId: string
): JournalOrder {
  const order = state.orders[orderId];
  if (!order) {
    throw new Error(`Order ${orderId} not found.`);
  }

  if (!canActivateLifeJournalMod(order)) {
    throw new Error(
      "Life Journal mod cannot activate until the journal has been delivered to the household."
    );
  }

  const activated = activateLifeJournalMod(order);
  state.orders[order.id] = activated;
  return activated;
}

export function configureJournalSettingsApi(
  state: JournalApiState,
  orderId: string,
  settings: JournalSettings
): JournalOrder {
  const order = state.orders[orderId];
  if (!order) {
    throw new Error(`Order ${orderId} not found.`);
  }

  const configured = configureLifeJournalSettings(order, settings);
  state.orders[order.id] = configured;
  return configured;
}

export const journalApi = {
  createJournalApiState,
  createOrderApi,
  getOrderApi,
  updateTrackingApi,
  confirmDeliveryApi,
  activateJournalModApi,
  configureJournalSettingsApi,
};

// Example request flow:
// POST /api/journal/orders { simId, householdId, shippingAddress, trackingId }
// PATCH /api/journal/orders/tracking { trackingId, status }
// POST /api/journal/orders/:id/confirm-delivery
// POST /api/journal/orders/:id/activate-mod
// POST /api/journal/orders/:id/settings { reminderFrequency, promptsEnabled, privacyMode }
