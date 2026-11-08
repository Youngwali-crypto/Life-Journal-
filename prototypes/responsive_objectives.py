"""Opt-in, authored response objectives driven by verified story context.

Context comes from trusted game/choice adapters, never inferred from journal
prose. Candidate previews are not active work and have no ticking deadline.
"""
import json
from dataclasses import asdict, dataclass
from typing import Tuple

from .database_session import database_session
from .journal_store import JournalStore
from .story_flow import StoryFlow, ObjectivePlan
from .story_tracking import StoryTracker


@dataclass(frozen=True)
class ResponseRule:
    id: str
    blueprint_id: str
    chapter_ids: Tuple[str, ...]
    conditions: dict
    objective: ObjectivePlan


class ResponsiveStoryFlow(StoryFlow):
    def configure_responses(self, story_id, rules):
        """Persist an immutable rule pool before supplying context."""
        rules = list(rules)
        encoded = json.loads(json.dumps([asdict(rule) for rule in rules]))
        ids = set()
        objective_ids = set()
        for rule in encoded:
            if not rule['id'] or rule['id'] in ids or not rule['blueprint_id'] or not rule['chapter_ids']:
                raise ValueError('Response rules need unique IDs and a Blueprint/chapter scope')
            self._validate_context(rule['conditions'])
            if not rule['conditions']:
                raise ValueError('Responses require actual story conditions')
            self._validate_plans([dict(id='response', title='Response', max_days=1,
                                       objectives=[rule['objective']])])
            if rule['objective']['id'] in objective_ids:
                raise ValueError('Response objective IDs must be unique')
            if rule['objective']['deadline_days'] is None:
                raise ValueError('Specify a realistic response deadline')
            ids.add(rule['id'])
            objective_ids.add(rule['objective']['id'])
        with database_session(self.path) as connection:
            connection.execute('BEGIN IMMEDIATE')
            data = self._load(connection, story_id)
            existing_ids = {o['id'] for c in data['plan'] for o in c['objectives']}
            chapters = {c['id'] for c in data['plan']}
            if objective_ids & existing_ids or any(
                r['blueprint_id'] != data['blueprint_id'] or not set(r['chapter_ids']) <= chapters for r in encoded
            ):
                raise ValueError('Rules must match the story and not reuse planned objective IDs')
            old = data.get('responses')
            if old is not None:
                if old['rules'] != encoded:
                    raise ValueError('Response pool already configured; migration required')
                return
            data['responses'] = dict(rules=encoded, context={}, receipts={}, chosen=[])
            self._save(connection, story_id, data)

    @staticmethod
    def _validate_context(context):
        if not isinstance(context, dict) or any(
            not isinstance(k, str) or not k.strip() or type(v) not in (str, bool, int)
            for k, v in context.items()
        ):
            raise ValueError('Context must map named facts to strings, booleans or integers')

    @staticmethod
    def _eligible(state, data):
        response = data.get('responses', {})
        if state.status != 'active':
            return []
        facts = response.get('context', {})
        return [rule for rule in response.get('rules', [])
                if rule['id'] not in response['chosen']
                and rule['blueprint_id'] == state.blueprint_id
                and state.chapter_id in rule['chapter_ids']
                and all(k in facts and type(facts[k]) is type(v) and facts[k] == v
                        for k, v in rule['conditions'].items())]

    def response_previews(self, story_id):
        with database_session(self.path) as connection:
            connection.execute('BEGIN')
            data = self._load(connection, story_id)
            state = StoryTracker(self.path, connection=connection).get(story_id)
            return tuple((r['id'], r['objective']['title']) for r in self._eligible(state, data)[:2])

    def update_story_context(self, story_id, facts, now, event_id):
        """Replace the complete context snapshot; omitted facts become unknown."""
        self._validate_context(facts)
        return self._change_response(story_id, now, event_id, 'context', facts)

    def choose_response(self, story_id, rule_id, now, event_id):
        return self._change_response(story_id, now, event_id, 'choose', rule_id)

    def _change_response(self, story_id, now, event_id, operation, payload):
        self._validate_time(now)
        if not isinstance(event_id, str) or not event_id.strip():
            raise ValueError('A stable occurrence ID is required')
        with database_session(self.path) as connection:
            connection.execute('BEGIN IMMEDIATE')
            data = self._load(connection, story_id)
            tracker = StoryTracker(self.path, connection=connection)
            journal = JournalStore(self.path, connection=connection)
            state = tracker.get(story_id)
            response = data.get('responses')
            if response is None:
                raise ValueError('Configure response rules first')
            receipt = [operation, payload, now]
            if event_id in response['receipts']:
                if response['receipts'][event_id] != receipt:
                    raise ValueError('Response occurrence ID reused with different data')
                return state
            if state.status != 'active' or now < data['last_time']:
                raise ValueError('Requires an active story and ordered Sim time')
            if state.chapter_id != data['plan'][data['index']]['id']:
                raise ValueError('Reconcile external chapter changes first')
            # A choice at/after chapter expiry cannot resurrect outgoing work.
            state = self._advance(tracker, journal, state, data, now)
            if operation == 'context':
                response['context'] = dict(payload)
            else:
                eligible = self._eligible(state, data)[:2]
                rule = next((r for r in eligible if r['id'] == payload), None)
                if rule is None:
                    raise ValueError('This focus is no longer available; refresh the Journal')
                objective = self._new_objectives(dict(objectives=[rule['objective']]), now)[0]
                data['objectives'].append(objective)
                response['chosen'].append(rule['id'])
                state = tracker.update_chapter(state, state.chapter_id,
                                               tuple(o['id'] for o in data['objectives']))
                self._record(journal, state, 'objective_activated',
                             'New focus: ' + objective['title'], now, objective['id'])
            response['receipts'][event_id] = receipt
            data['last_time'] = now
            self._save(connection, story_id, data)
            return state

    @staticmethod
    def _save(connection, story_id, data):
        connection.execute('UPDATE story_flow SET data=? WHERE story_id=?',
                           (json.dumps(data), story_id))


def example_response_rules(chapter_id):
    """Illustrative content only; durations and requirements need author review."""
    return (
        ResponseRule('career-reset', 'finding-my-lane', (chapter_id,),
                     {'career_state': 'unemployed'},
                     ObjectivePlan('response-career', 'Explore a new career direction', True, 1, 3)),
        ResponseRule('support', 'finding-my-lane', (chapter_id,),
                     {'support_received': True},
                     ObjectivePlan('response-support', 'Follow up with the Sim who supported you', True, 1, 2)),
        ResponseRule('university', 'finding-my-lane', (chapter_id,),
                     {'enrolled': True, 'focus_choice': 'education'},
                     ObjectivePlan('response-major', 'Explore a major that fits your interests', True, 1, 4)),
        ResponseRule('celebrate', 'finding-my-lane', (chapter_id,),
                     {'career_state': 'promoted'},
                     ObjectivePlan('response-celebrate', 'Celebrate your promotion with someone close', False, 1, 2)),
    )
