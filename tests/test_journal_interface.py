import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch
import sqlite3

from prototypes.journal_interface import JournalInterface
from prototypes.journal_store import JournalStore
from prototypes.journal_entry_log import JournalEntry
from prototypes.sims4_journal_dialogs import S4CLJournalDialogs
from prototypes.story_flow import StoryFlow, ChapterPlan, ObjectivePlan
from prototypes.story_tracking import StoryTracker


class JournalInterfaceTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'journal.db'
        self.store = JournalStore(self.path)
        self.current = True
        self.journal = JournalInterface(self.store, 'save', 'sim', 'Aaliyah',
                                        session_is_current=lambda: self.current)

    def test_free_journal_write_reload_and_duplicate_submit(self):
        self.assertIn('Free Journal', self.journal.page('My Story').text)
        draft = self.journal.begin_entry()
        self.journal.save_entry(draft, 'A small win.', 1440)
        self.journal.save_entry(draft, 'A small win.', 1441)
        self.assertEqual(len(JournalStore(self.path).entries('save', 'sim')), 1)
        self.assertIn('A small win.', self.journal.page('Personal Entries').text)
        self.assertIn('Sim day 2', self.journal.page('Personal Entries').text)
        with self.assertRaises(ValueError):
            self.journal.save_entry(draft, 'Changed text', 1442)

    def test_cancel_invalid_and_expired_drafts_do_not_write(self):
        draft = self.journal.begin_entry()
        for value in (' ', 'a' * 2001, None):
            with self.assertRaises(ValueError):
                self.journal.save_entry(draft, value, 0)
        self.journal.cancel_entry(draft)
        with self.assertRaises(ValueError):
            self.journal.save_entry(draft, 'Cancelled', 0)
        draft = self.journal.begin_entry()
        self.current = False
        with self.assertRaises(ValueError):
            self.journal.save_entry(draft, 'Stale', 0)
        self.assertEqual(self.store.entries('save', 'sim'), ())

    def test_sections_pagination_and_owner_isolation(self):
        for i in range(6):
            self.store.record_entry('save', 'sim', JournalEntry(str(i), 'player', 'personal', 'Note ' + str(i), i))
        self.store.record_entry('other', 'sim', JournalEntry('secret', 'player', 'personal', 'Other save', 0))
        self.store.record_entry('save', 'other', JournalEntry('secret', 'player', 'personal', 'Other Sim', 0))
        self.store.record_entry('save', 'sim', JournalEntry('event', 'system', 'hiccup', 'Story event', 0))
        self.assertEqual(self.journal.page('Personal Entries').total, 6)
        self.assertIn('Note 5', self.journal.page('Personal Entries').text)
        self.assertIn('Note 0', self.journal.page('Personal Entries', 99).text)
        self.assertNotIn('Other', self.journal.page('Personal Entries').text)
        self.assertIn('Story event', self.journal.page('Story Updates').text)
        self.assertNotIn('Note', self.journal.page('Story Updates').text)

    def test_story_pages_do_not_advance_time_or_reveal_future_objectives(self):
        flow = StoryFlow(self.path)
        tracker = StoryTracker(self.path)
        state = flow.start(tracker.select_main_character('save', 'house', 'sim'), 'lane', (
            ChapterPlan('one', 'One', 10, (ObjectivePlan('friend', 'Find a friend', True),)),
            ChapterPlan('two', 'Two', 12, (ObjectivePlan('secret', 'Future surprise', True),)),
        ), 0)
        self.journal.flow, self.journal.story_id = flow, state.id
        before = self.store.entries('save', 'sim')
        page = self.journal.page('Objectives')
        self.assertIn('Find a friend', page.text)
        self.assertNotIn('Future surprise', page.text)
        self.assertEqual(before, self.store.entries('save', 'sim'))
        self.journal.sim_id = 'other'
        with self.assertRaises(ValueError):
            self.journal.page('My Story')

    def dialogs(self):
        menu, button, context, input_type = Mock(), Mock(), Mock(), Mock()
        adapter = S4CLJournalDialogs(self.journal, object(), object(), lambda: 10,
                                    (menu, button, context, input_type, 'accept'))
        return adapter, menu, button, input_type

    def test_native_menu_callbacks_and_paging(self):
        adapter, menu, button, _ = self.dialogs()
        adapter.open()
        self.assertEqual(button.call_count, 5)
        # Invoke the Personal Entries button captured during construction.
        button.call_args_list[2].kwargs['on_chosen']('Personal Entries', 'Personal Entries')
        self.assertIn('Personal Entries', menu.call_args.args[1])
        menu.return_value.show.assert_called_with(sim_info=adapter.sim_info)

    def test_native_cancel_does_not_save_and_accept_does(self):
        adapter, _, _, input_type = self.dialogs()
        adapter.write_entry()
        callback = input_type.return_value.show.call_args.kwargs['on_submit']
        callback('Never save', 'cancel')
        self.assertEqual(self.store.entries('save', 'sim'), ())
        adapter.write_entry()
        callback = input_type.return_value.show.call_args.kwargs['on_submit']
        callback('My first entry', 'accept')
        self.assertEqual(self.store.entries('save', 'sim')[0].text, 'My first entry')

    def test_storage_failure_keeps_draft_for_retry(self):
        adapter, _, _, input_type = self.dialogs()
        adapter.write_entry()
        callback = input_type.return_value.show.call_args.kwargs['on_submit']
        with patch.object(self.store, 'record_entry', side_effect=sqlite3.OperationalError('disk')):
            callback('Keep this draft', 'accept')
        self.assertEqual(input_type.call_args.args[3], 'Keep this draft')
        callback = input_type.return_value.show.call_args.kwargs['on_submit']
        callback('Keep this draft', 'accept')
        self.assertEqual(len(self.store.entries('save', 'sim')), 1)

    def test_closed_session_rejects_delayed_ui_callback(self):
        adapter, _, _, input_type = self.dialogs()
        adapter.write_entry()
        callback = input_type.return_value.show.call_args.kwargs['on_submit']
        self.journal.close()
        with self.assertRaises(ValueError):
            callback('Too late', 'accept')
        self.assertEqual(self.store.entries('save', 'sim'), ())
