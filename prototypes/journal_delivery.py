"""Coordinate delivery of a paid order and collection of its Journal."""
import logging



log = logging.getLogger(__name__)


class JournalDelivery:
    def __init__(self, access, place_parcel_once, collect_journal_once, *, remove_parcel=None, notify=None):
        self.access = access
        self.place_parcel_once = place_parcel_once
        self.collect_journal_once = collect_journal_once
        self.remove_parcel = remove_parcel
        self.notify = notify

    def deliver(self, save_id, sim_id, now, *, express=False):
        """Return the parcel ID, or None if delivery is not possible yet.

        The placement adapter resolves the household's current front door.
        Repeating a call for an order ID must recover the same physical parcel.
        """
        self.access._time(now)
        with self.access.store.transaction() as data:
            order = self.access._read(data, save_id, sim_id)
            if order is None or order.received_at is not None or now < order.due_at:
                return None
            parcels = data.setdefault("parcels", {})
            existing = parcels.get(order.order_id)
            if existing is not None:
                return existing
            if express and order.order_id not in parcels:
                return None
            parcel_id = self.place_parcel_once(save_id, order.household_id, order.order_id)
            if parcel_id is not None:
                self.access._identity(parcel_id)
            parcels[order.order_id] = parcel_id
        if parcel_id is not None:
            self._notify("delivered")
        return parcel_id

    def _notify(self, event):
        if self.notify is None:
            return
        try:
            self.notify(event)
        except Exception:
            log.exception("Life Journal %s notification failed", event)

    def collect(self, save_id, actor_id, parcel_id, now):
        """Transfer once into the ordering Sim's inventory, then unlock setup.

        The adapter returns True for a successful or previously completed
        transfer. False leaves the parcel available for an inventory retry.
        """
        self.access._identity(parcel_id)
        self.access._time(now)
        order = self.access.state(save_id, actor_id)
        if order is None or now < order.due_at:
            return None
        with self.access.store.transaction(write=False) as data:
            if data.get("parcels", {}).get(order.order_id) != parcel_id:
                return None
        if order.received_at is None:
            if self.collect_journal_once(save_id, actor_id, order.order_id, parcel_id) is not True:
                return None
            order = self.access.receive(save_id, actor_id, order.household_id,
                                        order.order_id, order.order_id, now)
            self._notify("collected")
        if self.remove_parcel is not None:
            self.remove_parcel(save_id, order.order_id, parcel_id)
        return order
