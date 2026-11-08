import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from prototypes.responsive_objectives import ResponsiveStoryFlow, ResponseRule, example_response_rules
from prototypes.story_flow import ChapterPlan, ObjectivePlan
from prototypes.story_tracking import StoryTracker
from prototypes.journal_store import JournalStore
from prototypes.journal_interface import JournalInterface


class ResponsiveObjectiveTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'story.db'
        self.flow = ResponsiveStoryFlow(self.path)
        self.tracker = StoryTracker(self.path)
        self.state = self.flow.start(self.tracker.select_main_character('save', 'house', 'sim'),
            'finding-my-lane', (
                ChapterPlan('one', 'One', 10, (ObjectivePlan('base', 'Base work', True, 1, 4),)),
                ChapterPlan('two', 'Two', 12, (ObjectivePlan('next', 'Next work', True),)),
            ), 0)
        self.flow.configure_responses(self.state.id, example_response_rules('one'))

    def context(self, facts, now=10, event='facts'):
        return self.flow.update_story_context(self.state.id, facts, now, event)

    def test_only_relevant_options_and_at_most_two(self):
        self.assertEqual(self.flow.response_previews(self.state.id), ())
        self.context(dict(career_state='unemployed', support_received=True, enrolled=True, focus_choice='education'))
        self.assertEqual([r[0] for r in self.flow.response_previews(self.state.id)], ['career-reset', 'support'])
        self.flow.choose_response(self.state.id, 'career-reset', 20, 'choice')
        self.assertEqual([r[0] for r in self.flow.response_previews(self.state.id)], ['support', 'university'])

    def test_stale_context_removes_options_without_inventing_conflict(self):
        self.context({'career_state': 'unemployed'})
        self.context({'career_state': 'promoted'}, 20, 'promotion')
        self.assertEqual(self.flow.response_previews(self.state.id)[0][0], 'celebrate')
        with self.assertRaises(ValueError):
            self.flow.choose_response(self.state.id, 'career-reset', 21, 'stale')
        self.context({}, 22, 'unknown')
        self.assertEqual(self.flow.response_previews(self.state.id), ())

    def test_preview_has_no_timer_and_selected_deadline_starts_at_choice(self):
        self.context({'support_received': True})
        self.assertEqual(len(self.flow.snapshot(self.state.id)[1]), 1)
        self.flow.choose_response(self.state.id, 'support', 1000, 'choose')
        objective = self.flow.snapshot(self.state.id)[1][-1]
        self.assertEqual((objective.started_at, objective.deadline), (1000, 1000 + 2 * 1440))
        self.flow.update_progress(self.state.id, 'base', 1, 1001, 'base-done')
        self.assertEqual(self.flow.snapshot(self.state.id)[0].chapter_id, 'one')
        self.flow.update_progress(self.state.id, objective.id, 1, 1002, 'support-done')
        self.assertEqual(self.flow.snapshot(self.state.id)[0].chapter_id, 'two')

    def test_unselected_options_do_not_block_chapter_and_required_selected_carries(self):
        self.context({'support_received': True})
        self.flow.choose_response(self.state.id, 'support', 20, 'choose')
        self.flow.tick(self.state.id, 10 * 1440)
        state, objectives = self.flow.snapshot(self.state.id)
        self.assertEqual(state.chapter_id, 'two')
        self.assertTrue(next(o for o in objectives if o.id == 'response-support').overdue)
        self.assertEqual(self.flow.response_previews(self.state.id), ())

    def test_retries_reload_and_payload_conflicts(self):
        self.context({'support_received': True})
        self.flow.choose_response(self.state.id, 'support', 20, 'choose')
        reopened = ResponsiveStoryFlow(self.path)
        reopened.choose_response(self.state.id, 'support', 20, 'choose')
        self.assertEqual(len(reopened.snapshot(self.state.id)[1]), 2)
        with self.assertRaises(ValueError):
            reopened.choose_response(self.state.id, 'career-reset', 20, 'choose')
        records = JournalStore(self.path).entries('save', 'sim')
        self.assertEqual(sum(e.category == 'objective_activated' for e in records), 1)

    def test_failed_journal_write_rolls_back_choice(self):
        self.context({'support_received': True})
        with patch.object(JournalStore, 'record_entry', side_effect=RuntimeError('disk')):
            with self.assertRaises(RuntimeError):
                self.flow.choose_response(self.state.id, 'support', 20, 'choose')
        self.assertEqual(len(self.flow.snapshot(self.state.id)[1]), 1)
        self.assertEqual(self.flow.response_previews(self.state.id)[0][0], 'support')
        self.flow.choose_response(self.state.id, 'support', 20, 'choose')

    def test_paused_old_time_wrong_scope_and_invalid_context(self):
        self.context({'support_received': True})
        with self.assertRaises(ValueError):
            self.context({}, 1, 'old')
        with self.assertRaises(ValueError):
            self.context({'bad': []}, 20, 'invalid')
        self.tracker.set_status(self.tracker.get(self.state.id), 'paused')
        self.assertEqual(self.flow.response_previews(self.state.id), ())
        with self.assertRaises(ValueError):
            self.flow.choose_response(self.state.id, 'support', 20, 'paused')

    def test_journal_focus_selection_and_no_university_without_enrollment(self):
        self.context({'focus_choice': 'education', 'support_received': True})
        journal = JournalInterface(JournalStore(self.path), 'save', 'sim', 'Aaliyah',
            flow=self.flow, story_id=self.state.id, session_is_current=lambda: True)
        self.assertEqual([r[0] for r in journal.focus_options()], ['support'])
        journal.choose_focus('support', 20, 'journal-choice')
        self.assertIn('Follow up', journal.page('Objectives').text)

    def test_optional_response_does_not_hold_up_completion(self):
        self.context({'career_state': 'promoted'})
        self.flow.choose_response(self.state.id, 'celebrate', 20, 'celebrate')
        self.flow.update_progress(self.state.id, 'base', 1, 21, 'complete')
        self.assertEqual(self.flow.snapshot(self.state.id)[0].chapter_id, 'two')

    def test_unselected_candidates_are_not_required_work(self):
        self.context({'support_received': True})
        self.flow.update_progress(self.state.id, 'base', 1, 20, 'complete')
        self.assertEqual(self.flow.snapshot(self.state.id)[0].chapter_id, 'two')
