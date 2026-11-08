import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

from prototypes.journal_access import JournalAccess
from prototypes.journal_access_dialogs import JournalAccessDialogs
from prototypes.journal_store import JournalStore
from prototypes.journal_interface import JournalInterface


class JournalAccessTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'journal.db'
        self.access = JournalAccess(self.path)

    def order(self):
        return self.access.order('save', 'sim', 'house', 10, 60)

    def receive(self, order):
        return self.access.receive('save', 'sim', 'house', order.order_id, 'delivery-1', 70)

    def test_order_receive_setup_open_survives_reload(self):
        self.assertEqual(self.access.opening('save', 'sim'), 'not_ordered')
        order = self.order()
        self.assertEqual(self.access.opening('save', 'sim'), 'awaiting_delivery')
        self.access = JournalAccess(self.path)
        self.receive(order)
        self.assertEqual(self.access.opening('save', 'sim'), 'setup')
        self.access.start_free_journal('save', 'sim', 71)
        self.assertEqual(JournalAccess(self.path).opening('save', 'sim'), 'journal')
        self.assertEqual([e.category for e in JournalStore(self.path).entries('save', 'sim')],
                         ['journal_ordered', 'journal_received', 'journal_started'])

    def test_retries_keep_one_order_receipt_and_activation(self):
        order = self.order()
        self.assertEqual(self.access.order('save', 'sim', 'house', 20, 90), order)
        received = self.receive(order)
        self.assertEqual(self.receive(order), received)
        active = self.access.start_free_journal('save', 'sim', 71)
        self.assertEqual(self.access.start_free_journal('save', 'sim', 90), active)
        self.assertEqual(len(JournalStore(self.path).entries('save', 'sim')), 3)

    def test_not_due_or_wrong_recipient_cannot_receive(self):
        order = self.order()
        attempts = [('save', 'sim', 'house', order.order_id, 'd', 69),
                    ('other', 'sim', 'house', order.order_id, 'd', 70),
                    ('save', 'other', 'house', order.order_id, 'd', 70),
                    ('save', 'sim', 'other', order.order_id, 'd', 70),
                    ('save', 'sim', 'house', 'other', 'd', 70)]
        for args in attempts:
            with self.assertRaises(ValueError):
                self.access.receive(*args)
        self.assertEqual(self.access.opening('save', 'sim'), 'awaiting_delivery')
        with self.assertRaises(ValueError):
            self.access.start_free_journal('save', 'sim', 100)

    def test_failed_receipt_journal_write_rolls_back_and_retries(self):
        order = self.order()
        with patch.object(JournalStore, 'record_entry', side_effect=RuntimeError('disk')):
            with self.assertRaises(RuntimeError):
                self.receive(order)
        self.assertIsNone(self.access.state('save', 'sim').received_at)
        self.receive(order)
        self.assertEqual(self.access.opening('save', 'sim'), 'setup')

    def test_failed_activation_does_not_unlock(self):
        order = self.order()
        self.receive(order)
        with patch.object(JournalStore, 'record_entry', side_effect=RuntimeError('disk')):
            with self.assertRaises(RuntimeError):
                self.access.start_free_journal('save', 'sim', 71)
        self.assertEqual(self.access.opening('save', 'sim'), 'setup')
        self.access.start_free_journal('save', 'sim', 71)

    def test_history_belongs_to_sim_and_free_journal_opens(self):
        self.receive(self.order())
        self.access.start_free_journal('save', 'sim', 71)
        journal = JournalInterface(JournalStore(self.path), 'save', 'sim', 'Aaliyah',
                                   session_is_current=lambda: True)
        journal.save_entry(journal.begin_entry(), 'My Journal arrived!', 72)
        self.assertIn('My Journal arrived!', journal.page('Personal Entries').text)
        self.assertEqual(self.access.opening('other', 'sim'), 'not_ordered')
        self.assertEqual(self.access.opening('save', 'other'), 'not_ordered')

    def test_ui_routes_order_wait_setup_and_open_without_delivery_shortcut(self):
        dialogs = Mock()
        dialogs.journal = JournalInterface(JournalStore(self.path), 'save', 'sim', 'Aaliyah',
                                           session_is_current=lambda: True)
        dialogs.clock.return_value = 10
        ui = JournalAccessDialogs(self.access, dialogs, 'house', 60)
        ui.open()
        self.assertEqual(dialogs._menu.call_args.args[2][0][0], 'Order Journal')
        ui.order()
        self.assertEqual(dialogs._menu.call_args.args[0], 'Journal on its way')
        dialogs.open.assert_not_called()
        self.receive(self.access.state('save', 'sim'))
        ui.open()
        self.assertEqual(dialogs._menu.call_args.args[2][0][0], 'Start a Free Journal')
        dialogs.clock.return_value = 71
        ui.start_free()
        dialogs.open.assert_called_once_with()

    def test_closed_ui_and_invalid_time_cannot_order(self):
        dialogs = Mock()
        dialogs.journal = JournalInterface(JournalStore(self.path), 'save', 'sim', 'Aaliyah',
                                           session_is_current=lambda: False)
        ui = JournalAccessDialogs(self.access, dialogs, 'house', 60)
        with self.assertRaises(ValueError):
            ui.order()
        for value in (True, -1, 1.5):
            with self.assertRaises(ValueError):
                self.access.order('save', 'sim', 'house', 10, value)
        self.assertEqual(self.access.opening('save', 'sim'), 'not_ordered')
