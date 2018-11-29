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

from setuptools import setup, find_packages

assert str is not bytes  # Python3 required

with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="acrux",
    version="0.0.0",
    description="Acrux Crossword Tools",
    long_description=readme,
    author="Chris Pickel",
    author_email="sfiera@twotaled.com",
    url="https://github.com/sfiera/acrux",
    license=license,
    python_requires='>=3.0',
    packages=find_packages(exclude=("test", )),
    entry_points={
        "console_scripts": [
            "ax2ipuz=acrux.bin.ax2ipuz:main",
            "ax2pdf=acrux.bin.ax2pdf:main",
            "ax2puz=acrux.bin.ax2puz:main",
        ],
    })
