"""Licensed-source connectors for the Thesis Builder (platform tool 27), session 25: the interface, not yet wired.

The bring-your-own-license rule (docs/methods/thesis_builder.md): a licensed database (PitchBook, Harmonic,
Crunchbase, ...) is read only with the user's own credential, supplied at run time through the environment; its rows go
into that user's workbook only, marked "licensed, user's own account, not stored in the ERW", and never into an ERW
table, a Supabase table, a Redivis upload, a log line or a file in git. The ERW holds no licensed data.

    from connectors import available
    for conn in available():          # the connectors whose credential is set
        rows = conn.landscape(niche)   # [LANDSCAPE row dicts]
        rows = conn.capital(niche)     # [CAPITAL row dicts]

A connector is a subclass of LicensedConnector with NAME, CREDENTIAL_ENV and the two methods. The three here are stubs:
their fetch raises NotWired until the vendor's API call is written and tested against a real account; their mapping
from the vendor's documented fields to the ERW's row shapes is in place, so wiring one means writing fetch() only.
"""

import os

LICENSED_MARK = "licensed, user's own account, not stored in the ERW"
LANDSCAPE = ["name", "website", "description", "founders", "stage", "raised", "location", "signal", "licensed"]
CAPITAL = ["date", "company", "kind", "amount", "currency", "investors", "licensed"]


class NotWired(RuntimeError):
    """The connector's API call is not written yet."""


class LicensedConnector:
    NAME = ""
    CREDENTIAL_ENV = ""  # the environment variable that holds the user's own credential; never logged, never stored

    def __init__(self, credential):
        if not credential:
            raise ValueError(f"{self.NAME}: no credential")
        self._credential = credential

    def __repr__(self):  # the credential never appears in a repr, a log or an error
        return f"<{self.NAME} connector (credential from {self.CREDENTIAL_ENV})>"

    # the vendor's API: to be written per connector
    def fetch_companies(self, niche):
        raise NotWired(f"{self.NAME}: the API call is not written yet (session 25 stub)")

    def fetch_rounds(self, niche):
        raise NotWired(f"{self.NAME}: the API call is not written yet (session 25 stub)")

    # the vendor's fields to the ERW's shapes
    def to_landscape(self, rec):
        raise NotImplementedError

    def to_capital(self, rec):
        raise NotImplementedError

    def landscape(self, niche):
        return [dict(self.to_landscape(x), licensed=LICENSED_MARK) for x in self.fetch_companies(niche)]

    def capital(self, niche):
        return [dict(self.to_capital(x), licensed=LICENSED_MARK) for x in self.fetch_rounds(niche)]


def available():
    """The connectors whose credential is set in the environment, instantiated with it."""
    from .crunchbase import Crunchbase
    from .harmonic import Harmonic
    from .pitchbook import PitchBook
    out = []
    for cls in (PitchBook, Harmonic, Crunchbase):
        cred = os.environ.get(cls.CREDENTIAL_ENV, "").strip()
        if cred:
            out.append(cls(cred))
    return out
