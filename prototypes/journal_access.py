"""Persistent in-game Journal ordering/receipt/opening boundary.

Physical delivery is an external adapter responsibility. A receipt is committed
only after that adapter confirms delivery for the exact order and recipient.
Paid orders delegate funds to a trusted, idempotent wallet adapter.
"""
from dataclasses import dataclass
from uuid import uuid4
from typing import Optional

from .database_session import database_session
from .journal_entry_log import JournalEntry
from .journal_store import JournalStore


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
        JournalStore(path)
        with database_session(self.path) as connection:
            connection.execute('''CREATE TABLE IF NOT EXISTS journal_access (
                order_id TEXT PRIMARY KEY, save_id TEXT NOT NULL,
                sim_id TEXT NOT NULL, household_id TEXT NOT NULL,
                ordered_at INTEGER NOT NULL, due_at INTEGER NOT NULL,
                received_at INTEGER, receipt_id TEXT, activated_at INTEGER,
                mode TEXT, UNIQUE(save_id, sim_id), UNIQUE(save_id, receipt_id)
            )''')

            connection.execute("""CREATE TABLE IF NOT EXISTS journal_purchase (
                save_id TEXT NOT NULL, sim_id TEXT NOT NULL,
                household_id TEXT NOT NULL, order_id TEXT NOT NULL,
                ordered_at INTEGER NOT NULL, due_at INTEGER NOT NULL,
                PRIMARY KEY (save_id, sim_id)
            )""")

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

        owner = (save_id, sim_id)
        reservation_query = "SELECT household_id, order_id, ordered_at, due_at FROM journal_purchase WHERE save_id=? AND sim_id=?"
        with database_session(self.path) as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = self._read(connection, *owner)
            if already_ordered(existing):
                return existing
            if connection.execute(reservation_query, owner).fetchone() is None:
                due_at = (now // 1440 + 1) * 1440 + 9 * 60
                connection.execute("INSERT INTO journal_purchase VALUES (?, ?, ?, ?, ?, ?)",
                                   owner + (household_id, uuid4().hex, now, due_at))

        with database_session(self.path) as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = self._read(connection, *owner)
            if already_ordered(existing):
                return existing
            reservation = connection.execute(reservation_query, owner).fetchone()
            if reservation is None:
                return None
            reserved_household, order_id, ordered_at, due_at = reservation
            if reserved_household != household_id:
                raise ValueError("Pending payment belongs to a different household")
            paid = debit_once(save_id, household_id, order_id, self.PRICE)
            if paid is not True and paid is not False:
                raise ValueError("Wallet must report whether the debit succeeded")
            if paid:
                if existing is None:
                    connection.execute("INSERT INTO journal_access VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, NULL, NULL)",
                                       (order_id, save_id, sim_id, household_id, ordered_at, due_at))
                    category, message = "journal_ordered", "Life Journal ordered."
                else:
                    connection.execute("""
                        UPDATE journal_access
                        SET order_id=?, household_id=?, ordered_at=?, due_at=?,
                            received_at=NULL, receipt_id=NULL
                        WHERE save_id=? AND sim_id=?
                    """, (order_id, household_id, ordered_at, due_at, save_id, sim_id))
                    category, message = "journal_replacement_ordered", "Replacement Life Journal ordered."
                state = self._read(connection, *owner)
                self._record(connection, state, category, message, ordered_at)
            else:
                state = None
            connection.execute("DELETE FROM journal_purchase WHERE save_id=? AND sim_id=?", owner)
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
    def _read(connection, save_id, sim_id):
        row = connection.execute('SELECT * FROM journal_access WHERE save_id=? AND sim_id=?',
                                 (save_id, sim_id)).fetchone()
        return JournalAccessState(*row) if row else None

    def state(self, save_id, sim_id):
        self._identity(save_id, sim_id)
        with database_session(self.path) as connection:
            return self._read(connection, save_id, sim_id)

    def order(self, save_id, sim_id, household_id, now, delivery_minutes):
        self._identity(save_id, sim_id, household_id)
        self._time(now)
        self._time(delivery_minutes)
        with database_session(self.path) as connection:
            connection.execute('BEGIN IMMEDIATE')
            existing = self._read(connection, save_id, sim_id)
            if existing:
                if existing.household_id != household_id:
                    raise ValueError('Recipient moved; reconcile the existing order')
                return existing
            if connection.execute("SELECT 1 FROM journal_purchase WHERE save_id=? AND sim_id=?",
                                  (save_id, sim_id)).fetchone():
                raise ValueError("Finish the pending paid order first")
            connection.execute('INSERT INTO journal_access VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, NULL, NULL)',
                               (uuid4().hex, save_id, sim_id, household_id, now, now + delivery_minutes))
            state = self._read(connection, save_id, sim_id)
            self._record(connection, state, 'journal_ordered', 'Life Journal ordered.', now)
            return state

    def receive(self, save_id, sim_id, household_id, order_id, receipt_id, now):
        """Trusted adapter calls only after confirming actual physical delivery.

        Reuse the same order/receipt IDs after retries or reload; receipt ID must
        identify a stable delivery occurrence, never a transient object handle.
        """
        self._identity(save_id, sim_id, household_id, order_id, receipt_id)
        self._time(now)
        with database_session(self.path) as connection:
            connection.execute('BEGIN IMMEDIATE')
            state = self._read(connection, save_id, sim_id)
            if state is None or (state.order_id, state.household_id) != (order_id, household_id):
                raise ValueError('Delivery does not match the order and recipient')
            if state.received_at is not None:
                if state.receipt_id != receipt_id:
                    raise ValueError('Order already has a different delivery receipt')
                return state
            if now < state.due_at:
                raise ValueError('Delivery is not due yet')
            connection.execute('UPDATE journal_access SET received_at=?, receipt_id=? WHERE order_id=?',
                               (now, receipt_id, order_id))
            self._record(connection, state, 'journal_received', 'Life Journal received.', now)
            return self._read(connection, save_id, sim_id)

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
        with database_session(self.path) as connection:
            connection.execute('BEGIN IMMEDIATE')
            state = self._read(connection, save_id, sim_id)
            if state is None or state.received_at is None:
                raise ValueError('Receive the Journal before starting it')
            if now < state.received_at:
                raise ValueError('Opening cannot precede delivery')
            if state.activated_at is not None:
                return state
            connection.execute("UPDATE journal_access SET activated_at=?, mode='free' WHERE order_id=?",
                               (now, state.order_id))
            self._record(connection, state, 'journal_started', 'Free Journal started.', now)
            return self._read(connection, save_id, sim_id)

    @staticmethod
    def _record(connection, state, category, text, now):
        JournalStore('', connection=connection).record_entry(state.save_id, state.sim_id,
            JournalEntry('access:' + state.order_id + ':' + category,
                         'system', category, text, now))
