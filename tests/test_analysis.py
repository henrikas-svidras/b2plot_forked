#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Dummy conftest.py for b2plot.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""

import pytest
import b2plot as bp
import numpy as np


def test_divideEfficiency():
    t = np.ones(10)
    res = bp.analysis.divideEfficiency(t,t)
    assert np.mean(res[0]) == 1, "braindead test"


def test_divideEfficiency_half():
    t = np.ones(10)
    res = bp.analysis.divideEfficiency(t,t*2)
    assert np.mean(res[0]) == 0.5, "should be 0.5"    
