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

import sys
import os

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

import acrux  # noqa: E402,F401
import acrux.text  # noqa: E402,F401
import acrux.bin.ax2ipuz  # noqa: E402,F401
import acrux.bin.ax2pdf  # noqa: E402,F401
import acrux.bin.ax2puz  # noqa: E402,F401
