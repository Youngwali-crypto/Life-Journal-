from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock

from prototypes.journal_access import JournalAccess
from prototypes.journal_delivery import JournalDelivery


class DeliveryCoordinatorTests(TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.access = JournalAccess(Path(directory.name) / "journal.db")
        self.wallet = Mock(return_value=True)
        self.order = self.access.order_paid("save", "sim", "house", 10, self.wallet)
        self.place = Mock(return_value="box")
        self.transfer = Mock(return_value=True)
        self.delivery = JournalDelivery(self.access, self.place, self.transfer)

    def test_next_morning_and_failed_dropoff_retry(self):
        self.assertIsNone(self.delivery.deliver("save", "sim", 1979))
        self.assertIsNone(self.delivery.deliver("save", "sim", 1980, express=True))
        self.place.assert_not_called()
        self.place.side_effect = [None, "box"]
        self.assertIsNone(self.delivery.deliver("save", "sim", 1980))
        self.assertEqual(self.delivery.deliver("save", "sim", 1990, express=True), "box")
        reopened = JournalDelivery(JournalAccess(self.access.path), self.place, self.transfer)
        self.assertEqual(reopened.deliver("save", "sim", 2000), "box")
        self.assertEqual(self.place.call_count, 2)
        self.wallet.assert_called_once()

    def test_only_owner_can_collect_and_failed_inventory_can_retry(self):
        self.delivery.deliver("save", "sim", 1980)
        self.assertIsNone(self.delivery.collect("save", "another-sim", "box", 1980))
        self.transfer.assert_not_called()
        self.transfer.side_effect = [False, True]
        self.assertIsNone(self.delivery.collect("save", "sim", "box", 1980))
        self.assertEqual(self.access.opening("save", "sim"), "awaiting_delivery")
        received = self.delivery.collect("save", "sim", "box", 1981)
        self.assertEqual(self.access.opening("save", "sim"), "setup")
        self.assertEqual(self.delivery.collect("save", "sim", "box", 1982), received)
        self.assertEqual(self.transfer.call_count, 2)
        self.wallet.assert_called_once()

    def test_loaded_household_clock_drives_dropoff_and_stale_actions_stop(self):
        from prototypes.delivery_runtime import DeliveryRuntime
        from prototypes.zone_session import ZoneSession

        session = ZoneSession()
        zone = object()
        session.start(zone)
        clock = Mock(return_value=1979)
        runtime = DeliveryRuntime(self.delivery, "save", "house", clock, session.guard())
        runtime.tick()
        self.place.assert_not_called()
        clock.return_value = 1980
        runtime.tick()
        runtime.tick()
        self.place.assert_called_once_with("save", "house", self.order.order_id)
        open_journal = Mock()
        self.assertFalse(runtime.open_planner("sim", True, open_journal))
        self.assertIsNotNone(runtime.collect("sim", "box"))
        self.assertFalse(runtime.open_planner("sim", False, open_journal))
        self.assertTrue(runtime.open_planner("sim", True, open_journal))
        session.stop(zone)
        self.assertFalse(runtime.open_planner("sim", True, open_journal))
        self.assertIsNone(runtime.collect("sim", "box"))
        open_journal.assert_called_once()
