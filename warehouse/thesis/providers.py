#!/usr/bin/env python3
"""Thesis Builder (platform tool 27), session 150: the data providers of the fetch stage, as the server names them.

Energy Research Warehouse (ERW). Session 135 wrote the stage for PitchBook alone: a run writes a request, a person
pastes it into a Claude chat that holds their own PitchBook connector, and pastes the answer back on /thesis (the
format erw-pitchbook-1). Session 150 makes the stage provider-agnostic and adds Harmonic (erw-harmonic-1) and
Crunchbase (erw-crunchbase-1) beside it.

This module is the server's list of the providers: the id, the label, the format each expects back, and the terms
line. It calls nothing: no provider, no connector, no model, no network. The site holds the same list with what
belongs to the page (the request text of the two new providers, the readers of a pasted answer, the mapping of each
provider's fields to the run's facts): site/lib/thesis/providers.ts. site/scripts/test-thesis-providers.mjs checks
that the two lists say the same.

What does NOT change here:
  - run.pitchbook_request and the text it writes (warehouse/thesis/run.py): an erw-pitchbook-1 request is made by the
    run, as before, and saved on the run's row with its one-time key. tests/test_session150.py holds a request made by
    the code of main before this session and checks that the code still makes it, byte for byte.
  - the store: public.thesis_runs is not altered. A record that names no provider (every request and answer written
    before this session, the pending request of run 20261006T193517Z-50a8be among them) is PitchBook's, read so in
    code by provider_of below and by providerOf on the site. Nothing stored is rewritten.

The request text of Harmonic and Crunchbase is made by the site at the moment a person chooses the provider, from the
companies and the discovery search the run already saved in its request: a run needs no new stage, no new column and
no new spend for a second or third provider.
"""

import collections
import hashlib

Provider = collections.namedtuple("Provider", "id label format terms")

_OWN = ("{label} figures here are your own licensed copy: brought by you from your own account, shown to you, and not "
        "published, redistributed or kept in the public warehouse.")

PITCHBOOK = Provider(
    "pitchbook", "PitchBook", "erw-pitchbook-1",
    _OWN.format(label="PitchBook") + " PitchBook's public terms page was not read: it answered a plain request with HTTP 403 on 8 October 2026.")
HARMONIC = Provider(
    "harmonic", "Harmonic", "erw-harmonic-1",
    _OWN.format(label="Harmonic") + " Harmonic's Terms of Service (read 8 October 2026): \"You will not (and will not allow anyone else to): [...] "
    "provide, sell, transfer, sublicense, lend, distribute, or otherwise allow others to access or use the Services or the data obtained through the Services;\"")
CRUNCHBASE = Provider(
    "crunchbase", "Crunchbase", "erw-crunchbase-1",
    _OWN.format(label="Crunchbase") + " Crunchbase's License Agreement (read 8 October 2026): \"Except as otherwise expressly set forth herein, "
    "Licensee may not license, sublicense, sell, offer to sell, distribute or otherwise provide any Crunchbase data to any third parties.\"")

PROVIDERS = (PITCHBOOK, HARMONIC, CRUNCHBASE)          # PitchBook first: the default, as before session 150
BY_ID = {p.id: p for p in PROVIDERS}
BY_FORMAT = {p.format: p for p in PROVIDERS}
DEFAULT = PITCHBOOK


def provider_of(record):
    """The provider of a stored record (a request, an answer). One that names its provider is that provider's; one
    that names only a format is that format's; one that names neither was written before session 150 and is
    PitchBook's. This is how an old record is read: it is never rewritten."""
    if isinstance(record, dict):
        if record.get("provider") in BY_ID:
            return BY_ID[record["provider"]]
        if record.get("format") in BY_FORMAT:
            return BY_FORMAT[record["format"]]
    return PITCHBOOK


def stamp(provider_id, pasted_text, pasted_at):
    """What every fact of a provider's answer carries: the provider's id, the format, the time pasted and the SHA-256
    of the pasted text (its UTF-8 bytes, as pasted)."""
    p = BY_ID[provider_id]
    return {"provider": p.id, "format": p.format, "pasted_at": pasted_at,
            "pasted_sha256": hashlib.sha256(pasted_text.encode("utf-8")).hexdigest()}
