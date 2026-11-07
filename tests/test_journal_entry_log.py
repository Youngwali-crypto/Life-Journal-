from unittest import TestCase

from prototypes.journal_entry_log import JournalEntryLog


class JournalEntryLogTests(TestCase):
    def setUp(self):
        self.log = JournalEntryLog("save-1", "sim-1")

    def test_free_journal_accepts_player_notes_without_a_blueprint(self):
        note = self.log.add_player_entry("I met someone new today.", 10)
        self.assertEqual(note.source, "player")
        self.assertEqual(note.category, "personal")
        self.assertIsNone(note.chapter_id)
        self.assertEqual(self.log.entries(), (note,))

    def test_story_records_and_personal_entries_share_chronological_history(self):
        note = self.log.add_player_entry("Tomorrow I want to try something new.", 30)
        completion = self.log.record_story_event(
            "objective-completed:find-two-friends", "objective_completed",
            "Objective completed: Find Two Friends.", 10, chapter_id="chapter-1",
        )
        hiccup = self.log.record_story_event(
            "hiccup:missed-meetup", "hiccup", "Hiccup: Missed the meetup.", 30,
            chapter_id="chapter-2",
        )

        self.assertEqual(completion.source, "system")
        self.assertEqual(completion.chapter_id, "chapter-1")
        self.assertEqual(hiccup.category, "hiccup")
        self.assertEqual(self.log.entries(), (completion, note, hiccup))

    def test_retry_keeps_the_first_story_record_without_duplicates(self):
        first = self.log.record_story_event("completed-1", "objective_completed", "Done.", 10)
        retry = self.log.record_story_event("completed-1", "objective_completed", "Done.", 20)
        self.assertIs(retry, first)
        self.assertEqual(self.log.entries(), (first,))

    def test_blank_text_is_rejected_and_histories_are_separate(self):
        with self.assertRaises(ValueError):
            self.log.add_player_entry("   ", 10)
        with self.assertRaises(ValueError):
            self.log.record_story_event("event-1", "hiccup", " ", 10)

        self.log.add_player_entry("My first entry.", 10)
        self.assertEqual(len(self.log.entries()), 1)
        self.assertEqual(JournalEntryLog("save-1", "sim-2").entries(), ())
        self.assertEqual(JournalEntryLog("save-2", "sim-1").entries(), ())
