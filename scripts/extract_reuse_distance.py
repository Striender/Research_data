#!/usr/bin/env python3

import os
import runpy

script_dir = os.path.dirname(os.path.abspath(__file__))
runpy.run_path(os.path.join(script_dir, "extract_resus_distance.py"), run_name="__main__")
