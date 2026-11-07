"""The policy monitor's fields module under a name of its own (session 3233, chain 192).

Energy Research Warehouse (ERW). warehouse/policy/fields.py (session 3056) and warehouse/deals/fields.py (session 2232)
were both imported as the top-level module `fields`. In one process (the whole suite, as the landing gate runs it) the
first one imported is cached under that name and the other side receives it: the deals tests failed 80 times with
"module 'fields' has no attribute 'STAGE_IDS'" once the policy rows had landed. The policy side now imports this module
instead (`import policy_fields as pf`); it loads warehouse/policy/fields.py from its path under the name
`policy_fields`, so `fields` is left to the deals tracker. warehouse/policy/fields.py is unchanged.
"""

import importlib.util
import os
import sys

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fields.py")
_NAME = "policy_fields_impl"

if _NAME in sys.modules:
    _mod = sys.modules[_NAME]
else:
    _spec = importlib.util.spec_from_file_location(_NAME, _PATH)
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules[_NAME] = _mod
    _spec.loader.exec_module(_mod)

sys.modules[__name__] = _mod
