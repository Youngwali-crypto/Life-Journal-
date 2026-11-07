"""Game-independent physical journal delivery and activation rules."""

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Iterable, List, Optional
from uuid import uuid4


class JournalOrderStatus(str, Enum):
    CREATED = "created"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"


_DELIVERY_STAGES = tuple(JournalOrderStatus)


@dataclass(frozen=True)
class JournalSettings:
    reminder_frequency: str
    prompts_enabled: bool
    privacy_mode: str

    def __post_init__(self):
        if self.reminder_frequency not in ("daily", "weekly", "monthly"):
            raise ValueError("Invalid reminder frequency")
        if not isinstance(self.prompts_enabled, bool):
            raise ValueError("prompts_enabled must be a boolean")
        if self.privacy_mode not in ("private", "shared"):
            raise ValueError("Invalid privacy mode")


@dataclass(frozen=True)
class JournalOrder:
    id: str
    sim_id: str
    household_id: str
    shipping_address: str = field(repr=False)
    created_at: str
    tracking_id: Optional[str] = None
    status: JournalOrderStatus = JournalOrderStatus.CREATED
    delivered_at: Optional[str] = None
    mod_activated: bool = False
    settings: Optional[JournalSettings] = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_journal_order(
    sim_id: str,
    household_id: str,
    shipping_address: str,
    tracking_id: Optional[str] = None,
) -> JournalOrder:
    return JournalOrder(
        id="journal-order-" + uuid4().hex,
        sim_id=sim_id,
        household_id=household_id,
        shipping_address=shipping_address,
        tracking_id=tracking_id,
        created_at=_utc_now(),
    )


def update_order_status(order: JournalOrder, status: JournalOrderStatus) -> JournalOrder:
    status = JournalOrderStatus(status)
    if _DELIVERY_STAGES.index(status) <= _DELIVERY_STAGES.index(order.status):
        return order

    delivered_at = _utc_now() if status == JournalOrderStatus.DELIVERED else None
    return replace(order, status=status, delivered_at=delivered_at)


def can_activate_life_journal_mod(order: JournalOrder) -> bool:
    return (
        order.status == JournalOrderStatus.DELIVERED
        and order.delivered_at is not None
        and not order.mod_activated
    )


def activate_life_journal_mod(order: JournalOrder) -> JournalOrder:
    if not can_activate_life_journal_mod(order):
        raise ValueError("Activation requires a delivered journal and can only occur once")
    return replace(order, mod_activated=True)


def configure_journal_settings(order: JournalOrder, settings: JournalSettings) -> JournalOrder:
    if not order.mod_activated:
        raise ValueError("Settings require delivery and activation")
    return replace(order, settings=settings)


def simulate_delivery_timeline(
    order: JournalOrder, stages: Iterable[JournalOrderStatus],
) -> List[JournalOrder]:
    timeline = [order]
    for status in stages:
        timeline.append(update_order_status(timeline[-1], status))
    return timeline
