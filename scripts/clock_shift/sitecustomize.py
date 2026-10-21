"""Moves this Python process's clock forward, for scripts/suite_shifted.py (session 534).

Python imports a module named sitecustomize at start-up when one is on its path.
scripts/suite_shifted.py puts this folder first on PYTHONPATH and sets
ERW_CLOCK_SHIFT_SECONDS, so the suite, and every Python process it starts that
inherits the environment, reads a clock that many seconds ahead. Nothing here runs
unless that variable is set: with the folder off PYTHONPATH it is never imported.

What is moved: time.time and time.time_ns (and gmtime, localtime, ctime and strftime
called without a time), datetime.datetime.now, utcnow and today, datetime.date.today,
and pandas.Timestamp.now, utcnow and today. The clock keeps
ticking, shifted by a constant. pandas is imported first
(see below), so every python child pays its import time: a deadline loop still ends. time.monotonic and
time.perf_counter are left alone. Files keep the mtimes the real clock gave them.
"""
import os

_SHIFT = os.environ.get("ERW_CLOCK_SHIFT_SECONDS", "").strip()

if _SHIFT:
    import datetime as _dt
    import sys as _sys
    import time as _time

    _OFF = float(_SHIFT)
    _real_time = _time.time
    _real_time_ns = _time.time_ns
    _real_gmtime, _real_localtime = _time.gmtime, _time.localtime
    _real_ctime, _real_strftime = _time.ctime, _time.strftime

    def _time_fn():
        return _real_time() + _OFF

    def _time_ns_fn():
        return _real_time_ns() + int(_OFF * 1_000_000_000)

    def _gmtime(secs=None):
        return _real_gmtime(_time_fn() if secs is None else secs)

    def _localtime(secs=None):
        return _real_localtime(_time_fn() if secs is None else secs)

    def _ctime(secs=None):
        return _real_ctime(_time_fn() if secs is None else secs)

    def _strftime(fmt, t=None):
        return _real_strftime(fmt, _localtime() if t is None else t)

    _time.time, _time.time_ns = _time_fn, _time_ns_fn
    _time.gmtime, _time.localtime = _gmtime, _localtime
    _time.ctime, _time.strftime = _ctime, _strftime

    _RealDate, _RealDatetime = _dt.date, _dt.datetime
    _DELTA = _dt.timedelta(seconds=_OFF)

    class _DateMeta(type):
        def __instancecheck__(cls, obj):
            return isinstance(obj, _RealDate)

        def __subclasscheck__(cls, sub):
            return issubclass(sub, _RealDate)

    class _DatetimeMeta(_DateMeta):
        def __instancecheck__(cls, obj):
            return isinstance(obj, _RealDatetime)

        def __subclasscheck__(cls, sub):
            return issubclass(sub, _RealDatetime)

    class ShiftedDate(_RealDate, metaclass=_DateMeta):
        @classmethod
        def today(cls):
            return (_RealDatetime.now() + _DELTA).date()

    class ShiftedDatetime(_RealDatetime, metaclass=_DatetimeMeta):
        @classmethod
        def now(cls, tz=None):
            return _RealDatetime.now(tz) + _DELTA

        @classmethod
        def utcnow(cls):
            return _RealDatetime.now(_dt.timezone.utc).replace(tzinfo=None) + _DELTA

        @classmethod
        def today(cls):
            return _RealDatetime.now() + _DELTA

    ShiftedDate.__name__ = ShiftedDate.__qualname__ = "date"
    ShiftedDatetime.__name__ = ShiftedDatetime.__qualname__ = "datetime"
    ShiftedDate.__module__ = ShiftedDatetime.__module__ = "datetime"

    def _patch_pandas(pd):
        ts = pd.Timestamp
        real_now = ts.now

        def now(tz=None):
            return real_now(tz) + pd.Timedelta(seconds=_OFF)

        def utcnow():
            return real_now("UTC") + pd.Timedelta(seconds=_OFF)

        def today(tz=None):
            return now(tz).tz_localize(None) if tz is not None else now()

        try:
            ts.now, ts.utcnow, ts.today = staticmethod(now), staticmethod(utcnow), staticmethod(today)
        except TypeError as exc:
            _sys.stderr.write(f"clock_shift: pandas.Timestamp not patched: {exc}\n")

    # pandas's compiled classes subclass datetime.datetime when pandas is imported, and the
    # process dies (a stack overflow) if that is not the real type by then: so pandas is
    # imported first, with the real datetime, and its Timestamp's clock patched after.
    try:
        import pandas as _pd
    except ImportError:
        _pd = None
    if _pd is not None:
        _patch_pandas(_pd)
    _dt.date, _dt.datetime = ShiftedDate, ShiftedDatetime
