"""Journal pages shared by native dialogs and a future custom book renderer."""
from dataclasses import dataclass
from uuid import uuid4

from .journal_entry_log import JournalEntry


@dataclass(frozen=True)
class JournalPage:
    title: str
    text: str
    number: int
    total: int


class JournalInterface:
    SECTIONS = ('My Story', 'Objectives', 'Personal Entries', 'Story Updates')
    PAGE_SIZE = 4
    MAX_ENTRY_LENGTH = 2000

    def __init__(self, store, save_id, sim_id, sim_name, *, flow=None,
                 story_id=None, session_is_current=lambda: False):
        if not save_id or not sim_id or not sim_name:
            raise ValueError('Journal owner is required')
        self.store, self.save_id, self.sim_id = store, save_id, sim_id
        self.sim_name, self.flow, self.story_id = sim_name, flow, story_id
        self.session_is_current = session_is_current
        self.closed = False
        self.drafts = {}

    def close(self):
        self.closed = True
        self.drafts.clear()

    def _check(self):
        if self.closed or not self.session_is_current():
            raise ValueError('Journal session expired; reopen the Journal')

    def _story(self):
        self._check()
        if self.story_id is None:
            return None, ()
        if self.flow is None:
            raise ValueError('Story flow is required')
        state, objectives = self.flow.snapshot(self.story_id)
        if state is None or (state.save_id, state.sim_id) != (self.save_id, self.sim_id):
            raise ValueError('Story does not belong to this Journal')
        return state, objectives

    def page(self, section, number=0):
        if section not in self.SECTIONS or type(number) is not int or number < 0:
            raise ValueError('Unknown Journal page')
        state, objectives = self._story()
        if section == 'My Story':
            rows = ['A place to remember your Sim\'s life.']
            rows.append('Free Journal — write your own story.' if state is None else
                        'Blueprint: {}\nChapter: {}\nStatus: {}'.format(
                            state.blueprint_id or 'Not started', state.chapter_id or 'Not started', state.status))
        elif section == 'Objectives':
            # Current objectives only. No future plan is exposed to the UI.
            rows = ['{}\n{} — {}/{}{}'.format(
                item.title, 'Required' if item.required else 'Optional', item.progress,
                item.target, ' — Complete' if item.completed_at is not None else
                (' — Overdue' if item.overdue else '')) for item in objectives]
        else:
            entries = self.store.entries(self.save_id, self.sim_id)
            rows = ['Sim day {} · {}\n{}'.format(
                entry.sim_minute // 1440 + 1, entry.category.replace('_', ' ').title(), entry.text)
                for entry in reversed(entries)
                if (entry.source == 'player') == (section == 'Personal Entries')]
        # One entry per reading page prevents long notes overflowing a list page.
        size = 1 if section in ('Personal Entries', 'Story Updates') else self.PAGE_SIZE
        total = max(1, (len(rows) + size - 1) // size)
        number = min(number, total - 1)
        selected = rows[number * size:(number + 1) * size]
        return JournalPage(section, '\n\n'.join(selected) or 'Nothing recorded here yet.', number, total)

    def focus_options(self):
        state, _ = self._story()
        if state is None or not hasattr(self.flow, 'response_previews'):
            return ()
        return self.flow.response_previews(self.story_id)

    def choose_focus(self, rule_id, now, event_id):
        self._story()
        if self.flow is None or not hasattr(self.flow, 'choose_response'):
            raise ValueError('No responsive story is active')
        return self.flow.choose_response(self.story_id, rule_id, now, event_id)

    def begin_entry(self):
        self._check()
        draft = uuid4().hex
        self.drafts[draft] = None
        return draft

    def cancel_entry(self, draft):
        self._check()
        self.drafts.pop(draft, None)

    def save_entry(self, draft, text, now):
        self._check()
        if draft not in self.drafts:
            raise ValueError('Unknown or cancelled entry')
        if not isinstance(text, str) or not text.strip() or len(text) > self.MAX_ENTRY_LENGTH:
            raise ValueError('Write between 1 and 2000 characters')
        if type(now) is not int or now < 0:
            raise ValueError('Invalid Sim time')
        prior = self.drafts[draft]
        if prior is not None:
            if prior.text != text.strip():
                raise ValueError('This entry was already saved')
            return prior
        state, _ = self._story()
        entry = JournalEntry('player:' + draft, 'player', 'personal', text.strip(), now,
                             state.chapter_id if state else None)
        saved = self.store.record_entry(self.save_id, self.sim_id, entry)
        self.drafts[draft] = saved
        return saved
