"""Connect one loaded household's clock and object actions to JournalDelivery."""
from .database_session import database_session


class DeliveryRuntime:
    def __init__(self, delivery, save_id, household_id, clock, current):
        self.delivery = delivery
        self.save_id = save_id
        self.household_id = household_id
        self.clock = clock
        self.current = current
        self.last_tick = None

    def tick(self):
        if not self.current():
            return
        now = self.clock()
        self.delivery.access._time(now)
        if self.last_tick == now:
            return
        with database_session(self.delivery.access.path) as connection:
            recipients = connection.execute("""
                SELECT a.sim_id FROM journal_access a
                LEFT JOIN journal_parcel p ON p.order_id = a.order_id
                WHERE a.save_id = ? AND a.household_id = ? AND a.due_at <= ?
                  AND a.received_at IS NULL AND p.parcel_id IS NULL
            """, (self.save_id, self.household_id, now)).fetchall()
        for (sim_id,) in recipients:
            self.delivery.deliver(self.save_id, sim_id, now)
        self.last_tick = now

    def retry_delivery(self, actor_id):
        """Retry a failed drop-off for this lot's household."""
        if not self.current():
            return None
        order = self.delivery.access.state(self.save_id, actor_id)
        if order is None or order.household_id != self.household_id:
            return None
        return self.delivery.deliver(self.save_id, actor_id, self.clock(), express=True)

    def collect(self, actor_id, parcel_id):
        if self.current() and parcel_id is not None:
            return self.delivery.collect(self.save_id, actor_id, parcel_id, self.clock())
        return None

    def open_planner(self, actor_id, owned_planner, open_journal):
        if not self.current() or not owned_planner:
            return False
        if self.delivery.access.opening(self.save_id, actor_id) not in ("setup", "journal"):
            return False
        open_journal()
        return True
