"""Lifetime of Journal callbacks for one loaded lot.

The caller supplies the live Zone object. Travel ends this lifetime even
when the same save stays loaded. These tokens are never used as save IDs.
"""


class ZoneSession:
    def __init__(self):
        self.zone = None
        self._token = None

    def start(self, zone):
        if zone is None:
            raise ValueError("A loaded zone is required")
        if self.zone is not zone:
            self.zone = zone
            self._token = object()
        return self._token

    def stop(self, zone):
        if self.zone is zone:
            self.zone = None
            self._token = None

    def guard(self):
        """Capture this load's token for JournalInterface.session_is_current."""
        token = self._token
        return lambda: token is not None and self._token is token
