"""The package's errors, in words: one sentence each that says what to do (session 1013, chain 070).

Energy Research Warehouse (ERW), docs/methods/packages.md, "Errors, in words". The Stata and R packages say the same
sentences (packages/stata/erw.ado, packages/r/erw/R/erw.R), and packages/conformance/conformance.json holds them, so
a test can hold the three to one wording. `{tables_call}` is the language's own call that lists the tables
(erw.tables(), erw tables, erw_tables()); every other placeholder is filled the same way in the three.
"""

WORDS = {
    "no_network": "The ERW's {where} could not be reached ({reason}). Check the network connection, then try again.",
    "not_found": "No ERW table named {table}. {tables_call} lists every table{near}.",
    "held": "{table} is not public: {verdict}. {words} The ERW's license record: {url}",
    "empty_window": "No rows of {table} start in [{start}, {end}); its rows run from {ts_min} to {ts_max}.",
    "redivis_token": "Set REDIVIS_API_TOKEN to a token from https://redivis.com/workspace/settings/tokens, then try again.",
    "live_keys": "Set ERW_LIVE_URL and ERW_LIVE_KEY to the live set's address and key (the ERW gives them on request), "
                 "then try again.",
    # session 1056 (chain 072): a date that cannot be read, and a window with no time in it, said before any request
    "bad_date": "The {side} {value} is not a date the ERW reads: write it as YYYY-MM-DD, or YYYY-MM-DDTHH:MM:SSZ in UTC, "
                "then try again.",
    "bad_window": "The start {start} is not before the end {end}, so the window [start, end) holds no time: give a start "
                  "before the end, then try again.",
    # session 1056: a table of the record that the live set does not hold (it said "No ERW table named", which is wrong)
    "not_live": "{table} is not in the live set: {tables_call} says which tables are (in_live); read it from the Stanford "
                "dataset or a clone's tables instead.",
    "row_limit": "The live set answered a page of {got} rows where {page} were asked for: a fault of the package, not of "
                 "your call; please tell the ERW (https://github.com/SamuelEnrique/erw/issues).",
}

TABLES_CALL = "erw.tables()"


def say(kind: str, **kw) -> str:
    """The sentence for a failure, its placeholders filled."""
    return WORDS[kind].format(tables_call=TABLES_CALL, **kw)


def near(names) -> str:
    """'; with a close name: a, b' for the not-found sentence, or ''."""
    names = list(names)
    return f"; with a close name: {', '.join(names)}" if names else ""


def missing_key(name: str) -> str:
    """The sentence for a key the environment and .env do not hold."""
    if name == "REDIVIS_API_TOKEN":
        return say("redivis_token")
    if name in ("ERW_LIVE_URL", "ERW_LIVE_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY"):
        return say("live_keys")
    return f"Set {name} (in the environment or a .env file), then try again."
