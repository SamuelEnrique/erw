#!/usr/bin/env python3
"""Build docs/coverage.md (session 2 entry point, kept for compatibility).

Energy Research Warehouse (ERW). Since session 3 the coverage builder lives in
warehouse/metadata/build_coverage.py, which also writes
warehouse/metadata/coverage.csv. This file only calls it:

    python warehouse/validate/build_coverage.py
"""

import os
import runpy

runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "metadata",
                            "build_coverage.py"), run_name="__main__")
