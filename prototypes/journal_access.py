"""Persistent in-game Journal ordering/receipt/opening boundary.

Physical delivery is an external adapter responsibility. A receipt is committed
only after that adapter confirms delivery for the exact order and recipient.
Paid orders delegate funds to a trusted, idempotent wallet adapter.
"""
from dataclasses import dataclass, asdict, replace
from uuid import uuid4
from typing import Optional

from .journal_entry_log import JournalEntry
from .json_journal_store import JsonJournalStore


@dataclass(frozen=True)
class JournalAccessState:
    order_id: str
    save_id: str
    sim_id: str
    household_id: str
    ordered_at: int
    due_at: int
    received_at: Optional[int]
    receipt_id: Optional[str]
    activated_at: Optional[int]
    mode: Optional[str]


class JournalAccess:
    def __init__(self, path):
        self.path = str(path)
        self.store = JsonJournalStore(path)

    PRICE = 200

    def order_paid(self, save_id, sim_id, household_id, now, debit_once, *, replace_order_id=None):
        """Shared phone/computer path. Debit returns True for a new or prior charge.

        A False result guarantees no charge. Exceptions are ambiguous and leave
        the reservation intact so retry uses the same payment key.
        """
        self._identity(save_id, sim_id, household_id)
        self._time(now)
        if replace_order_id is not None:
            self._identity(replace_order_id)

        def already_ordered(existing):
            if replace_order_id is None:
                return existing is not None
            if existing is None:
                raise ValueError("Replacement requires a previously collected Journal")
            return existing.order_id != replace_order_id or existing.received_at is None

        owner = self._key(save_id, sim_id)
        with self.store.transaction() as data:
            existing = self._read(data, save_id, sim_id)
            if already_ordered(existing):
                return existing
            reservations = data.setdefault("purchases", {})
            if owner not in reservations:
                due_at = (now // 1440 + 1) * 1440 + 9 * 60
                reservations[owner] = [household_id, uuid4().hex, now, due_at]

        with self.store.transaction() as data:
            existing = self._read(data, save_id, sim_id)
            if already_ordered(existing):
                return existing
            reservations = data.setdefault("purchases", {})
            reservation = reservations.get(owner)
            if reservation is None:
                return None
            reserved_household, order_id, ordered_at, due_at = reservation
            if reserved_household != household_id:
                raise ValueError("Pending payment belongs to a different household")
            paid = debit_once(save_id, household_id, order_id, self.PRICE)
            if paid is not True and paid is not False:
                raise ValueError("Wallet must report whether the debit succeeded")
            if paid:
                state = JournalAccessState(order_id, save_id, sim_id, household_id, ordered_at,
                                           due_at, None, None,
                                           existing.activated_at if existing else None,
                                           existing.mode if existing else None)
                self._put(data, state)
                category = "journal_replacement_ordered" if existing else "journal_ordered"
                message = "Replacement Life Journal ordered." if existing else "Life Journal ordered."
                self._record(data, state, category, message, ordered_at)
            else:
                state = None
            del reservations[owner]
            return state

    @staticmethod
    def _time(now):
        if type(now) is not int or now < 0:
            raise ValueError('Use absolute nonnegative Sim minutes')

    @staticmethod
    def _identity(*values):
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError('Nonempty identity is required')

    @staticmethod
    def _key(save_id, sim_id):
        import json
        return json.dumps([save_id, sim_id])

    def _read(self, data, save_id, sim_id):
        row = data.get("orders", {}).get(self._key(save_id, sim_id))
        return JournalAccessState(**row) if row else None

    def _put(self, data, state):
        data.setdefault("orders", {})[self._key(state.save_id, state.sim_id)] = asdict(state)

    def state(self, save_id, sim_id):
        self._identity(save_id, sim_id)
        with self.store.transaction(write=False) as data:
            return self._read(data, save_id, sim_id)

    def order(self, save_id, sim_id, household_id, now, delivery_minutes):
        self._identity(save_id, sim_id, household_id)
        self._time(now)
        self._time(delivery_minutes)
        with self.store.transaction() as data:
            existing = self._read(data, save_id, sim_id)
            if existing:
                if existing.household_id != household_id:
                    raise ValueError('Recipient moved; reconcile the existing order')
                return existing
            if self._key(save_id, sim_id) in data.get("purchases", {}):
                raise ValueError("Finish the pending paid order first")
            state = JournalAccessState(uuid4().hex, save_id, sim_id, household_id,
                                       now, now + delivery_minutes, None, None, None, None)
            self._put(data, state)
            self._record(data, state, 'journal_ordered', 'Life Journal ordered.', now)
            return state

    def receive(self, save_id, sim_id, household_id, order_id, receipt_id, now):
        """Trusted adapter calls only after confirming actual physical delivery.

        Reuse the same order/receipt IDs after retries or reload; receipt ID must
        identify a stable delivery occurrence, never a transient object handle.
        """
        self._identity(save_id, sim_id, household_id, order_id, receipt_id)
        self._time(now)
        with self.store.transaction() as data:
            state = self._read(data, save_id, sim_id)
            if state is None or (state.order_id, state.household_id) != (order_id, household_id):
                raise ValueError('Delivery does not match the order and recipient')
            if state.received_at is not None:
                if state.receipt_id != receipt_id:
                    raise ValueError('Order already has a different delivery receipt')
                return state
            if now < state.due_at:
                raise ValueError('Delivery is not due yet')
            if any(row["save_id"] == save_id and row["receipt_id"] == receipt_id
                   for row in data.get("orders", {}).values()):
                raise ValueError("Receipt already belongs to another order")
            state = replace(state, received_at=now, receipt_id=receipt_id)
            self._put(data, state)
            self._record(data, state, 'journal_received', 'Life Journal received.', now)
            return self._read(data, save_id, sim_id)

    def opening(self, save_id, sim_id):
        state = self.state(save_id, sim_id)
        if state is None:
            return 'not_ordered'
        if state.received_at is None:
            return 'awaiting_delivery'
        return 'setup' if state.activated_at is None else 'journal'

    def start_free_journal(self, save_id, sim_id, now):
        self._identity(save_id, sim_id)
        self._time(now)
        with self.store.transaction() as data:
            state = self._read(data, save_id, sim_id)
            if state is None or state.received_at is None:
                raise ValueError('Receive the Journal before starting it')
            if now < state.received_at:
                raise ValueError('Opening cannot precede delivery')
            if state.activated_at is not None:
                return state
            state = replace(state, activated_at=now, mode="free")
            self._put(data, state)
            self._record(data, state, 'journal_started', 'Free Journal started.', now)
            return self._read(data, save_id, sim_id)

    @staticmethod
    def _record(data, state, category, text, now):
        JsonJournalStore.record(data, state.save_id, state.sim_id,
            JournalEntry('access:' + state.order_id + ':' + category,
                         'system', category, text, now))
