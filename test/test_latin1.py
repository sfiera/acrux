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

from acrux.text import to_latin1


def test_simple():
    assert to_latin1("As ‘easy’ as “pie”") == "As 'easy' as \"pie\""
    assert to_latin1("–123") == "-123"
    assert to_latin1("a–b—c") == "a--b---c"
    assert to_latin1("November №3") == "November No.3"
    assert to_latin1("→L@@K←") == "-->L@@K<--"


def test_emoji():
    assert to_latin1("\u270a") == "[emoji: raised fist]"
    assert to_latin1("\U0001F446") == "[emoji: white up pointing backhand index]"
    assert to_latin1("\U0001F449") == "[emoji: white right pointing backhand index]"
    assert to_latin1("\U0001F525") == "[emoji: fire]"
    assert to_latin1("\U0001F600") == "[emoji: grinning face]"
    assert to_latin1("\U0001F648") == "[emoji: see-no-evil monkey]"
    assert to_latin1("\U0001F918") == "[emoji: sign of the horns]"


def test_keys():
    assert to_latin1("⌘") == "Cmd"
    assert to_latin1("⌘Z") == "Cmd-Z"
    assert to_latin1("Hits ⌘Z") == "Hits cmd-Z"
    assert to_latin1("⌃⌥⇧⌘C") == "Ctrl-opt-shift-cmd-C"


def test_fractions():
    assert to_latin1("1") == "1"
    assert to_latin1("1½") == "1½"

    assert to_latin1("⅓") == "1/3"
    assert to_latin1("1⅓") == "1 1/3"
    assert to_latin1("⅓⅔") == "1/3 2/3"
    assert to_latin1("⅛oz.") == "1/8 oz."

    assert to_latin1("¼½¾⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞") == "¼½¾ 1/3 2/3 1/5 2/5 3/5 4/5 1/6 5/6 1/8 3/8 5/8 7/8"


def test_accented():
    assert to_latin1("café") == "café"

    assert to_latin1("nǐ hǎo") == "ni hao"
    assert to_latin1("Dvořak") == "Dvorak"
    assert to_latin1("Cœur d’Alène") == "Coeur d'Alène"
    assert to_latin1("Ĳsselmeer") == "IJsselmeer"

    assert to_latin1("l\u01da") == "lü"
    assert to_latin1("l\xfc\u030c") == "lü"
    assert to_latin1("lu\u0308\u030c") == "lü"
