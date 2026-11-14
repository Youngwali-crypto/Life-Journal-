from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock

from life_journal_bootstrap import order_dialog_resolver
from prototypes.journal_access import JournalAccess
from prototypes.journal_delivery import JournalDelivery


class JournalBootstrapTests(TestCase):
    def test_confirmation_and_delivery_share_owner_and_loaded_save(self):
        with TemporaryDirectory() as directory:
            access = JournalAccess(Path(directory) / "journal.db")
            current = Mock(return_value=True)
            debit = Mock(return_value=True)
            owner = SimpleNamespace(sim_info=SimpleNamespace(sim_id=7, household=3))
            visitor = SimpleNamespace(sim_info=SimpleNamespace(sim_id=8, household=4))

            def native(journal, sim, clock):
                return SimpleNamespace(journal=journal, clock=clock, _menu=Mock())

            resolve = order_dialog_resolver(
                access, "save-a", "3", lambda: 10, current, lambda sim: sim.household,
                lambda sim: "Aaliyah", native, debit,
            )
            self.assertIsNone(resolve(visitor))
            dialogs = resolve(owner)
            dialogs.order()
            confirm = dict(dialogs.dialogs._menu.call_args[0][2])["Place Order"]
            confirm()
            order = access.state("save-a", "7")
            self.assertIsNone(access.state("save-b", "7"))
            debit.assert_called_once_with("save-a", "3", order.order_id, 200)
            delivery = JournalDelivery(access, Mock(return_value="box"), Mock(return_value=True))
            self.assertEqual(delivery.deliver("save-a", "7", 1980), "box")
            self.assertIsNotNone(delivery.collect("save-a", "7", "box", 1980))
            self.assertEqual(access.opening("save-a", "7"), "setup")
            current.return_value = False
            with self.assertRaises(ValueError):
                confirm()
            self.assertIsNone(resolve(owner))
            debit.assert_called_once()
