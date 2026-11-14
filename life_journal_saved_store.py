"""Journal JSON stored in S4CL's mod_data folder, keyed by game save ID."""
from copy import deepcopy
from prototypes.json_journal_store import JsonJournalStore


class SavedJournalStore(JsonJournalStore):
    def __init__(self, identity, identifier, current):
        from sims4communitylib.persistence.persistence_services.common_file_persistence_service import CommonFilePersistenceService
        self.service = CommonFilePersistenceService(
            per_save=False, custom_file_name='life_journal_{}.json'.format(identifier))
        self.identity = identity
        self.identifier = identifier
        self.current = current

    def _read(self):
        if not self.current():
            raise ValueError('Journal save session expired')
        data = self.service.load(self.identity, identifier=self.identifier)
        if not data:
            return {'version': 1, 'entries': []}
        if data.get('version') != 1 or not isinstance(data.get('entries'), list):
            raise ValueError('Unsupported saved Journal data')
        return deepcopy(data)

    def _write(self, data):
        if not self.current():
            raise ValueError('Journal save session expired')
        if not self.service.save(self.identity, data, identifier=self.identifier):
            raise OSError('Could not store Journal data in this game save')
