"""The deal tracker's fields module under a name of its own (session 3233, chain 192).

Energy Research Warehouse (ERW). warehouse/deals/fields.py (session 2232) and warehouse/policy/fields.py (session 3056)
were both importable as the top-level module `fields`. In one process the first one imported is cached under that name
and the other side receives it. Session 3233 gave the policy side its own name (warehouse/policy/policy_fields.py), and
the deals suite still failed on GitHub's runner (80 errors, "module 'fields' has no attribute 'STAGE_IDS'", run
42311026710) while it passed on the desktop. So neither side imports a module called `fields` any more: the deals
modules and tests import this one (`import deal_fields as fields`), which loads warehouse/deals/fields.py from its path
under the name `deal_fields`. warehouse/deals/fields.py is unchanged.
"""

import importlib.util
import os
import sys

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fields.py")
_NAME = "deal_fields_impl"

if _NAME in sys.modules:
    _mod = sys.modules[_NAME]
else:
    _spec = importlib.util.spec_from_file_location(_NAME, _PATH)
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules[_NAME] = _mod
    _spec.loader.exec_module(_mod)

sys.modules[__name__] = _mod
