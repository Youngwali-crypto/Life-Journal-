"""Experimental native S4CL Journal dialogs, not the custom book skin.

Bootstrap supplies a verified SimInfo, current-session guard and Sim clock.
No import-time registration; never auto-select a different Sim in callbacks.
"""

import sqlite3


class S4CLJournalDialogs:
    def __init__(self, journal, mod_identity, sim_info, sim_clock, api=None):
        self.journal, self.identity = journal, mod_identity
        self.sim_info, self.clock = sim_info, sim_clock
        if api is None:
            from sims4communitylib.dialogs.option_dialogs.common_choose_button_option_dialog import CommonChooseButtonOptionDialog
            from sims4communitylib.dialogs.option_dialogs.options.response.common_dialog_button_option import CommonDialogButtonOption
            from sims4communitylib.dialogs.option_dialogs.options.response.common_dialog_response_option_context import CommonDialogResponseOptionContext
            from sims4communitylib.dialogs.common_input_text_dialog import CommonInputTextDialog
            from sims4communitylib.dialogs.common_choice_outcome import CommonChoiceOutcome
            api = (CommonChooseButtonOptionDialog, CommonDialogButtonOption,
                   CommonDialogResponseOptionContext, CommonInputTextDialog, CommonChoiceOutcome.CHOICE_MADE)
        self.menu_type, self.button_type, self.context_type, self.input_type, self.accepted = api

    def _menu(self, title, body, actions, previous=None):
        self.journal._check()
        dialog = self.menu_type(self.identity, title, body,
                               include_previous_button=previous is not None,
                               on_previous=previous or (lambda: None))
        for label, callback in actions:
            def chosen(_identifier, _value, action=callback):
                self.journal._check()
                action()
            dialog.add_option(self.button_type(label, label, self.context_type(label), on_chosen=chosen))
        dialog.show(sim_info=self.sim_info)
        return dialog

    def open(self):
        actions = [(name, lambda section=name: self.show_page(section)) for name in self.journal.SECTIONS]
        actions.append(('Write an Entry', self.write_entry))
        return self._menu(self.journal.sim_name + "'s Life Journal",
                          'Your life. Your story. Your memories.', actions)

    def show_page(self, section, number=0):
        page = self.journal.page(section, number)
        actions = []
        if page.number > 0:
            actions.append(('Previous Page', lambda: self.show_page(section, page.number - 1)))
        if page.number + 1 < page.total:
            actions.append(('Next Page', lambda: self.show_page(section, page.number + 1)))
        if section == 'Personal Entries':
            actions.append(('Write an Entry', self.write_entry))
        return self._menu('{} · {}/{}'.format(page.title, page.number + 1, page.total),
                          page.text, actions, previous=self.open)

    def write_entry(self, draft=None, initial='', message='What would you like to remember?'):
        self.journal._check()
        draft = draft or self.journal.begin_entry()
        dialog = self.input_type(self.identity, 'Write an Entry', message, initial)
        def submitted(text, outcome):
            self.journal._check()
            if outcome != self.accepted:
                self.journal.cancel_entry(draft)
                return self.open()
            try:
                self.journal.save_entry(draft, text, self.clock())
            except ValueError as error:
                return self.write_entry(draft, text or '', str(error))
            except (OSError, sqlite3.Error):
                return self.write_entry(draft, text or '', 'Could not save. Your draft is still here; try again.')
            return self.show_page('Personal Entries')
        dialog.show(sim_info=self.sim_info, on_submit=submitted)
        return dialog
