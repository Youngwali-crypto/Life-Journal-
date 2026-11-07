import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from prototypes.chapter_progression import SIM_MINUTES_PER_DAY as DAY
from prototypes.journal_store import JournalStore
from prototypes.story_flow import ChapterPlan, ObjectivePlan, StoryFlow
from prototypes.story_tracking import StoryTracker


PLANS = (
    ChapterPlan("chapter-1", "Branching Out", 10, (
        ObjectivePlan("friends", "Find Two Friends", True, 2, 4),
        ObjectivePlan("hobby", "Explore a Hobby", True, 1, 4),
        ObjectivePlan("venue", "Visit the Venue", False, 1, 3, ("chapter-2",)),
        ObjectivePlan("outfit", "Choose an Outfit", False, 1, 3),
    )),
    ChapterPlan("chapter-2", "Choosing My Lane", 12, (
        ObjectivePlan("career", "Choose a Career", True, 1, 6),
    )),
    ChapterPlan("chapter-3", "Outside Noise", 12, (
        ObjectivePlan("decision", "Make a Decision", True, 1, 6),
    )),
)


class StoryFlowTests(TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "journal.db"
        self.flow = StoryFlow(self.path)
        self.tracker = StoryTracker(self.path)
        self.journal = JournalStore(self.path)
        self.selected = self.tracker.select_main_character("save", "household", "sim")
        self.story = self.flow.start(self.selected, "finding-my-lane", PLANS, 0)

    def records(self, category):
        return tuple(
            entry for entry in self.journal.entries("save", "sim")
            if entry.category == category
        )

    def test_completion_connects_progress_tracking_and_journal_across_reload(self):
        self.flow.update_progress(self.story.id, "friends", 1, DAY, "friend-one")
        self.flow = StoryFlow(self.path)
        self.flow.update_progress(self.story.id, "friends", 2, 2 * DAY, "friend-two")
        state = self.flow.update_progress(self.story.id, "hobby", 1, 3 * DAY, "hobby-done")
        self.assertEqual(state.chapter_id, "chapter-2")
        self.assertEqual(state.objective_ids, ("venue", "career"))
        state, objectives = self.flow.snapshot(state.id)
        career = next(item for item in objectives if item.id == "career")
        self.assertEqual(career.started_at, 3 * DAY)
        self.assertEqual(len(self.records("objective_completed")), 2)
        self.assertEqual(len(self.records("chapter_started")), 2)
        self.assertEqual(self.records("hurdle"), ())
        self.assertEqual(self.flow.tick(state.id, 15 * DAY - 1).chapter_id, "chapter-2")
        self.assertEqual(self.flow.tick(state.id, 15 * DAY).chapter_id, "chapter-3")

    def test_expiry_preserves_progress_and_creates_one_combined_hurdle(self):
        self.flow.update_progress(self.story.id, "friends", 1, 2 * DAY, "friend-one")
        state = self.flow.tick(self.story.id, 10 * DAY)
        self.assertEqual(state.objective_ids, ("friends", "hobby", "venue", "career"))
        _, objectives = self.flow.snapshot(state.id)
        self.assertEqual(objectives[0].progress, 1)
        self.assertEqual(objectives[0].deadline, 22 * DAY)
        self.assertTrue(objectives[0].overdue)
        self.assertEqual(len(self.records("hurdle")), 1)
        self.flow.tick(state.id, 22 * DAY)
        self.assertEqual(len(self.records("hurdle")), 2)
        self.assertIn("Growing consequences", self.records("hurdle")[-1].text)

    def test_recent_progress_protects_overdue_objective_and_hiccup_is_recorded_once(self):
        self.flow.update_progress(self.story.id, "friends", 1, 3 * DAY, "friend-one")
        self.flow.tick(self.story.id, 4 * DAY)
        hiccups = self.records("hiccup")
        self.assertEqual(len(hiccups), 1)  # Unworked hobby only.
        self.assertIn("hobby", hiccups[0].id)
        self.flow.tick(self.story.id, 4 * DAY + 1)
        self.flow.tick(self.story.id, 5 * DAY)
        self.assertEqual(len(self.records("hiccup")), 2)

    def test_retries_after_transition_and_reload_do_not_duplicate_records(self):
        self.flow.update_progress(self.story.id, "friends", 2, DAY, "friends-done")
        self.flow.update_progress(self.story.id, "hobby", 1, 2 * DAY, "hobby-done")
        before = self.journal.entries("save", "sim")
        reopened = StoryFlow(self.path)
        state = reopened.update_progress(self.story.id, "hobby", 1, 2 * DAY, "hobby-done")
        self.assertEqual(state.chapter_id, "chapter-2")
        self.assertEqual(self.journal.entries("save", "sim"), before)
        with self.assertRaises(ValueError):
            reopened.update_progress(self.story.id, "hobby", 2, 2 * DAY, "hobby-done")

    def test_failed_journal_write_rolls_back_completion_and_transition(self):
        self.flow.update_progress(self.story.id, "friends", 2, DAY, "friends-done")
        before = self.journal.entries("save", "sim")
        real_write = JournalStore.record_entry

        def fail_on_new_chapter(store, save_id, sim_id, entry):
            if entry.category == "chapter_started":
                raise RuntimeError("Simulated storage failure")
            return real_write(store, save_id, sim_id, entry)

        with patch.object(JournalStore, "record_entry", fail_on_new_chapter):
            with self.assertRaises(RuntimeError):
                self.flow.update_progress(self.story.id, "hobby", 1, 2 * DAY, "hobby-done")
        state, objectives = self.flow.snapshot(self.story.id)
        self.assertEqual(state.chapter_id, "chapter-1")
        self.assertIsNone(next(item for item in objectives if item.id == "hobby").completed_at)
        self.assertEqual(self.journal.entries("save", "sim"), before)
        self.assertEqual(
            self.flow.update_progress(self.story.id, "hobby", 1, 2 * DAY, "hobby-done").chapter_id,
            "chapter-2",
        )

    def test_concurrent_duplicate_updates_are_applied_once(self):
        def complete():
            return self.flow.update_progress(self.story.id, "friends", 2, DAY, "friends-done")
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: complete(), range(2)))
        self.assertEqual(results[0], results[1])
        self.assertEqual(len(self.records("objective_completed")), 1)

    def test_late_tick_catches_up_and_final_chapter_releases_household(self):
        state = self.flow.tick(self.story.id, 40 * DAY)
        self.assertEqual(state.status, "completed")
        self.assertIsNone(self.tracker.active("save", "household"))
        self.assertEqual(len(self.records("chapter_ended")), 3)
        self.assertEqual(len(self.records("blueprint_ended")), 1)
        self.assertEqual(self.records("blueprint_ended")[0].sim_minute, 34 * DAY)

    def test_completion_at_deadline_gets_credit_without_entry_hurdle(self):
        self.flow.update_progress(self.story.id, "friends", 2, DAY, "friends-done")
        self.flow.update_progress(self.story.id, "hobby", 1, 10 * DAY, "hobby-done")
        self.assertIn("(expired)", self.records("chapter_ended")[0].text)
        self.assertEqual(self.records("hurdle"), ())
        self.assertEqual(self.records("objective_completed")[-1].sim_minute, 10 * DAY)

    def test_old_clock_and_unknown_objectives_cannot_change_state(self):
        self.flow.tick(self.story.id, DAY)
        before = self.flow.snapshot(self.story.id)
        with self.assertRaises(ValueError):
            self.flow.update_progress(self.story.id, "friends", 1, DAY - 1, "late")
        with self.assertRaises(ValueError):
            self.flow.update_progress(self.story.id, "unknown", 1, 12 * DAY, "unknown")
        self.assertEqual(self.flow.snapshot(self.story.id), before)

    def test_paused_story_rejects_new_progress(self):
        paused = self.tracker.set_status(self.story, "paused")
        with self.assertRaises(ValueError):
            self.flow.update_progress(self.story.id, "friends", 1, DAY, "friend-one")
        self.assertEqual(self.tracker.get(paused.id), paused)
