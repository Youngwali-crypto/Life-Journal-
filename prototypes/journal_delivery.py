"""Coordinate delivery of a paid order and collection of its Journal."""
from .database_session import database_session


class JournalDelivery:
    def __init__(self, access, place_parcel_once, collect_journal_once, *, remove_parcel=None):
        self.access = access
        self.place_parcel_once = place_parcel_once
        self.collect_journal_once = collect_journal_once
        self.remove_parcel = remove_parcel
        with database_session(access.path) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS journal_parcel (
                    order_id TEXT PRIMARY KEY, parcel_id TEXT
                )
            """)

    def deliver(self, save_id, sim_id, now, *, express=False):
        """Return the parcel ID, or None if delivery is not possible yet.

        The placement adapter resolves the household's current front door.
        Repeating a call for an order ID must recover the same physical parcel.
        """
        self.access._time(now)
        order = self.access.state(save_id, sim_id)
        if order is None or order.received_at is not None or now < order.due_at:
            return None
        with database_session(self.access.path) as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT parcel_id FROM journal_parcel WHERE order_id=?",
                (order.order_id,),
            ).fetchone()
            if row and row[0] is not None:
                return row[0]
            if express and row is None:
                return None
            parcel_id = self.place_parcel_once(save_id, order.household_id, order.order_id)
            if parcel_id is not None:
                self.access._identity(parcel_id)
            connection.execute("INSERT OR REPLACE INTO journal_parcel VALUES (?, ?)",
                               (order.order_id, parcel_id))
            return parcel_id

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
        with database_session(self.access.path) as connection:
            row = connection.execute(
                "SELECT parcel_id FROM journal_parcel WHERE order_id=?",
                (order.order_id,),
            ).fetchone()
        if row is None or row[0] != parcel_id:
            return None
        if order.received_at is None:
            if self.collect_journal_once(save_id, actor_id, order.order_id, parcel_id) is not True:
                return None
            order = self.access.receive(save_id, actor_id, order.household_id,
                                        order.order_id, order.order_id, now)
        if self.remove_parcel is not None:
            self.remove_parcel(save_id, order.order_id, parcel_id)
        return order
