import tempfile
from dataclasses import replace
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

from prototypes.gameplay_bridge import GameplayBridge, GameplayContext
from prototypes.sims4_skill_reader import S4CLSkillReader
from prototypes.story_flow import StoryFlow, ChapterPlan, ObjectivePlan
from prototypes.story_tracking import StoryTracker
from prototypes.journal_store import JournalStore


class GameplayBridgeTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'journal.db'
        self.flow = StoryFlow(self.path)
        self.tracker = StoryTracker(self.path)
        selected = self.tracker.select_main_character('save', '10', '20')
        self.state = self.flow.start(selected, 'blueprint', (
            ChapterPlan('one', 'One', 10, (ObjectivePlan('skill', 'Reach level 4', True, 4, 5),)),
            ChapterPlan('two', 'Two', 12, (ObjectivePlan('next', 'Next', True),)),
        ), 0)
        self.context = GameplayContext('save', '10', '20', 'load-1')
        self.bridge = GameplayBridge(self.flow, self.state.id, self.context)

    def test_skill_completion_transitions_and_persists_once(self):
        self.assertEqual(self.bridge.observe_skill(self.context, 'skill', 3, 10), 'updated')
        self.bridge.observe_skill(self.context, 'skill', 4, 20)
        reopened = StoryFlow(self.path)
        bridge = GameplayBridge(reopened, self.state.id, self.context)
        self.assertEqual(bridge.observe_skill(self.context, 'skill', 4, 20), 'untracked')
        self.assertEqual(reopened.snapshot(self.state.id)[0].chapter_id, 'two')
        entries = JournalStore(self.path).entries('save', '20')
        self.assertEqual(sum(e.category == 'objective_completed' for e in entries), 1)

    def test_wrong_identity_or_load_never_updates(self):
        for field in ('save_id', 'household_id', 'sim_id', 'load_token'):
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.bridge.observe_skill(replace(self.context, **{field: 'other'}), 'skill', 4, 10)
        self.assertEqual(self.flow.snapshot(self.state.id)[1][0].progress, 0)
        with self.assertRaises(ValueError):
            GameplayBridge(self.flow, self.state.id, replace(self.context, sim_id='30'))

    def test_closed_and_paused_sessions(self):
        self.tracker.set_status(self.tracker.get(self.state.id), 'paused')
        self.assertEqual(self.bridge.observe_skill(self.context, 'skill', 4, 10), 'inactive')
        self.assertEqual(self.bridge.tick(self.context, 10), 'inactive')
        self.bridge.close()
        with self.assertRaises(ValueError):
            self.bridge.tick(self.context, 20)

    def test_lower_levels_and_repeated_observations_do_not_add_progress(self):
        self.bridge.observe_skill(self.context, 'skill', 2, 10)
        self.bridge.observe_skill(self.context, 'skill', 2, 20)
        self.bridge.observe_skill(self.context, 'skill', 1, 30)
        objective = self.flow.snapshot(self.state.id)[1][0]
        self.assertEqual((objective.progress, objective.last_progress_at), (2, 10))
        with self.assertRaises(ValueError):
            self.bridge.observe_skill(self.context, 'skill', 3, 5)

    def test_failed_write_can_retry_observation(self):
        with patch.object(JournalStore, 'record_entry', side_effect=RuntimeError('disk')):
            with self.assertRaises(RuntimeError):
                self.bridge.observe_skill(self.context, 'skill', 4, 10)
        self.assertEqual(self.flow.snapshot(self.state.id)[1][0].progress, 0)
        self.bridge.observe_skill(self.context, 'skill', 4, 10)
        self.assertEqual(self.flow.snapshot(self.state.id)[0].chapter_id, 'two')

    def test_tick_uses_sim_minutes_for_expiry(self):
        self.bridge.tick(self.context, 10 * 1440)
        state, objectives = self.flow.snapshot(self.state.id)
        self.assertEqual(state.chapter_id, 'two')
        self.assertTrue(objectives[0].overdue)

    def test_reader_is_read_only_and_ignores_temporary_skill_bonuses(self):
        sims, households, skills = Mock(), Mock(), Mock()
        sims.get_sim_id.return_value = 20
        households.get_household_id.return_value = 10
        skills.get_current_skill_level.return_value = 3.75
        reader = S4CLSkillReader(sims, households, skills)
        self.assertEqual(reader.observe(self.bridge, self.context, 'skill', 123, 10), 'updated')
        skills.get_skill.assert_called_once_with(sims.get_sim_info.return_value, 123, add=False)
        skills.get_current_skill_level.assert_called_once_with(
            sims.get_sim_info.return_value, 123, use_effective_skill_level=False)
        self.assertEqual(self.flow.snapshot(self.state.id)[1][0].progress, 3)
        households.get_household_id.return_value = 99
        with self.assertRaises(ValueError):
            reader.observe(self.bridge, self.context, 'skill', 123, 20)

    def test_unavailable_skill_and_invalid_data_do_not_complete(self):
        sims, households, skills = Mock(), Mock(), Mock()
        sims.get_sim_id.return_value = 20
        households.get_household_id.return_value = 10
        reader = S4CLSkillReader(sims, households, skills)
        skills.get_skill.return_value = None
        self.assertEqual(reader.observe(self.bridge, self.context, 'skill', 123, 10), 'unavailable')
        skills.get_skill.return_value = object()
        skills.get_current_skill_level.return_value = float('nan')
        with self.assertRaises(ValueError):
            reader.observe(self.bridge, self.context, 'skill', 123, 10)
        for value in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                self.bridge.observe_skill(self.context, 'skill', value, 10)
