"""In-memory delivery API prototype with no network or carrier dependency."""

from dataclasses import dataclass, field
from typing import Dict, Optional

from .journal_delivery_flow import (
    JournalOrder,
    JournalOrderStatus,
    JournalSettings,
    activate_life_journal_mod,
    configure_journal_settings,
    create_journal_order,
    update_order_status,
)


@dataclass
class JournalApiState:
    orders: Dict[str, JournalOrder] = field(default_factory=dict)


def create_order(
    state: JournalApiState,
    sim_id: str,
    household_id: str,
    shipping_address: str,
    tracking_id: Optional[str] = None,
) -> JournalOrder:
    if tracking_id is not None and any(
        order.tracking_id == tracking_id for order in state.orders.values()
    ):
        raise ValueError("Tracking ID is already assigned")
    order = create_journal_order(sim_id, household_id, shipping_address, tracking_id)
    state.orders[order.id] = order
    return order


def get_order(state: JournalApiState, order_id: str) -> Optional[JournalOrder]:
    return state.orders.get(order_id)


def update_tracking(
    state: JournalApiState, tracking_id: str, status: JournalOrderStatus,
) -> Optional[JournalOrder]:
    if not tracking_id:
        return None
    for order in state.orders.values():
        if order.tracking_id == tracking_id:
            updated = update_order_status(order, status)
            state.orders[order.id] = updated
            return updated
    return None


def confirm_delivery(state: JournalApiState, order_id: str) -> JournalOrder:
    order = update_order_status(state.orders[order_id], JournalOrderStatus.DELIVERED)
    state.orders[order_id] = order
    return order


def activate_mod(state: JournalApiState, order_id: str) -> JournalOrder:
    order = activate_life_journal_mod(state.orders[order_id])
    state.orders[order_id] = order
    return order


def configure_settings(
    state: JournalApiState, order_id: str, settings: JournalSettings,
) -> JournalOrder:
    order = configure_journal_settings(state.orders[order_id], settings)
    state.orders[order_id] = order
    return order
