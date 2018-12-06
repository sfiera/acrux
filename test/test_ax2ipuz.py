#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2018 Chris Pickel
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import glob
import os
import sys
from io import StringIO
from .context import acrux

ROOT = os.path.dirname(os.path.dirname(__file__))
ACRUX = [os.path.basename(p) for p in glob.glob("%s/test/data/acrux/*" % ROOT)]
CASES = [os.path.splitext(ax)[0] for ax in ACRUX]


def test_ax2ipuz(case):
    with open("%s/test/data/acrux/%s.pn" % (ROOT, case)) as f:
        source = f.read()
    with open("%s/test/data/ipuz/%s.ipuz" % (ROOT, case)) as f:
        expected = f.read()

    sys.stdin = StringIO(source)
    sys.stdout = StringIO()
    acrux.bin.ax2ipuz.main(["ax2ipuz"])
    actual = sys.stdout.getvalue()
    sys.stdin = sys.__stdin__
    sys.stdout = sys.__stdout__

    assert expected == actual


def pytest_generate_tests(metafunc):
    metafunc.parametrize("case", CASES)
