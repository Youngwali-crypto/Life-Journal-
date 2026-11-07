import sqlite3
import tempfile
from pathlib import Path
from unittest import TestCase

from prototypes.story_tracking import StoryTracker


class StoryTrackerTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "journal.db"
        self.tracker = StoryTracker(self.path)

    def test_role_story_and_objectives_survive_reload(self):
        selected = self.tracker.select_main_character("save", "household", "sim")
        self.assertIsNone(selected.blueprint_id)
        story = self.tracker.start_blueprint(selected, "finding-my-lane", "chapter-1", ("friends",))
        reopened = StoryTracker(self.path)
        self.assertEqual(reopened.active("save", "household"), story)
        changed = reopened.update_chapter(story, "chapter-2", ("career", "friends"))
        self.assertEqual(changed.objective_ids, ("career", "friends"))
        self.assertEqual(changed.chapter_id, "chapter-2")

    def test_pause_switch_and_resume_enforce_one_main_character(self):
        first = self.tracker.select_main_character("save", "household", "sim-1")
        with self.assertRaises(sqlite3.IntegrityError):
            self.tracker.select_main_character("save", "household", "sim-2")
        paused = self.tracker.set_status(first, "paused")
        second = self.tracker.select_main_character("save", "household", "sim-2")
        with self.assertRaises(sqlite3.IntegrityError):
            self.tracker.set_status(paused, "active")
        self.assertEqual(self.tracker.get(paused.id), paused)
        self.tracker.set_status(second, "completed")
        resumed = self.tracker.set_status(paused, "active")
        self.assertEqual(self.tracker.active("save", "household"), resumed)

    def test_stale_updates_cannot_overwrite_newer_progress(self):
        selected = self.tracker.select_main_character("save", "household", "sim")
        story = self.tracker.start_blueprint(selected, "finding-my-lane", "chapter-1")
        with self.assertRaises(ValueError):
            self.tracker.set_status(selected, "paused")
        self.assertEqual(self.tracker.get(story.id), story)

    def test_saves_and_households_are_independent(self):
        self.tracker.select_main_character("save", "household", "sim")
        self.tracker.select_main_character("other-save", "household", "sim")
        self.tracker.select_main_character("save", "other-household", "other-sim")
        with self.assertRaises(sqlite3.IntegrityError):
            self.tracker.select_main_character("save", "third-household", "sim")
