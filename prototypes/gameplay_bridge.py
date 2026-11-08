"""Single-objective gameplay boundary. No game imports or automatic listeners.

Calls must run serially on the game thread. Bind a new bridge after each load;
never reuse a load token for another loaded save or an older save revision.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class GameplayContext:
    save_id: str
    household_id: str
    sim_id: str
    load_token: str


class GameplayBridge:
    def __init__(self, flow, story_id, context):
        if any(not isinstance(value, str) or not value.strip() for value in (
            context.save_id, context.household_id, context.sim_id, context.load_token
        )):
            raise ValueError('Save, household, Sim and load token are required')
        self.flow = flow
        self.story_id = story_id
        self.context = context
        self.closed = False
        self._check(context)

    def close(self):
        self.closed = True

    def _check(self, context):
        if self.closed or context != self.context:
            raise ValueError('Stale gameplay session; bind the loaded save again')
        state, objectives = self.flow.snapshot(self.story_id)
        if (state.save_id, state.household_id, state.sim_id) != (
            context.save_id, context.household_id, context.sim_id
        ):
            raise ValueError('Gameplay identity does not match the Main Character')
        return state, objectives

    def observe_skill(self, context, objective_id, level, now):
        """Absolute achieved level, never an increment. Existing levels count.

        One explicitly configured skill objective per call. Levels below stored
        progress do not erase achievements. Only whole levels count for now.
        """
        if type(level) is not int or level < 0:
            raise ValueError('Skill level must be a nonnegative integer')
        self.flow._validate_time(now)
        state, objectives = self._check(context)
        if state.status != 'active':
            return 'inactive'
        objective = next((item for item in objectives if item.id == objective_id), None)
        if objective is None:
            return 'untracked'
        if objective.completed_at is not None or level <= objective.progress:
            self.flow.tick(self.story_id, now)
            return 'unchanged'
        # The persisted flow already deduplicates this observation across retries.
        import json
        event_id = 'skill-observation:' + json.dumps([
            context.load_token, objective_id, level, now
        ], separators=(',', ':'))
        self.flow.update_progress(self.story_id, objective_id, level, now, event_id)
        return 'updated'

    def tick(self, context, now):
        self.flow._validate_time(now)
        state, _ = self._check(context)
        if state.status != 'active':
            return 'inactive'
        self.flow.tick(self.story_id, now)
        return 'ticked'
