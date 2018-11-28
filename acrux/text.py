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

assert str is not bytes  # Python 3 required

import html.parser
import re
import unicodedata


def strip_html(s):
    class ToTextParser(html.parser.HTMLParser):
        def __init__(self):
            self.reset()
            self.strict = False
            self.convert_charrefs = True
            self.data = []

        def handle_data(self, d):
            self.data.append(d)

        def get_data(self):
            return ''.join(self.data)

    p = ToTextParser()
    p.feed(s)
    return p.get_data()


def _replace_negative(m):
    return "-%s" % m.group(1)


_SIMPLE = {
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'",
    "–": "--",
    "—": "---",
    "…": "...",
    "№": "No.",
    "←": "<--",
    "⇐": "<==",
    "⇒": "==>",
    "→": "-->",
    "Œ": "OE",
    "œ": "oe",
}


def _replace_simple(m):
    return _SIMPLE[m.group(0)]


def _replace_emoji(m):
    return "[emoji: %s]" % unicodedata.name(m.group(0)).lower()


_MODIFIER_KEYS = {
    "⌘": "cmd",
    "⇧": "shift",
    "⌥": "opt",
    "⌃": "ctrl",
}


def _replace_modifier_key(m):
    s = _MODIFIER_KEYS[m.group(0)]
    if m.group(2) is not None:
        s += "-"
    if m.group(1) is not None:
        s = s.title()
    return s


_FRACTIONS = {
    "⅓": "1/3",
    "⅔": "2/3",
    "⅕": "1/5",
    "⅖": "2/5",
    "⅗": "3/5",
    "⅘": "4/5",
    "⅙": "1/6",
    "⅚": "5/6",
    "⅛": "1/8",
    "⅜": "3/8",
    "⅝": "5/8",
    "⅞": "7/8",
}


def _replace_fraction(m):
    s = _FRACTIONS[m.group(0)]
    if m.group(1) is not None:
        s = " %s" % s
    if m.group(2) is not None:
        s = "%s " % s
    return s


def _replace_accented(m):
    s = unicodedata.normalize("NFKD", m.group(0))
    start = 0
    result = []
    for end in range(len(s) + 1):
        if start == end:
            continue
        seg = unicodedata.normalize("NFC", s[start:end])
        try:
            seg = seg.encode("latin1")
        except UnicodeEncodeError as e:
            if end > (start + 1):
                result.append(unicodedata.normalize("NFC", s[start:end - 1]))
            start = end
    if end > start:
        result.append(unicodedata.normalize("NFC", s[start:end]))
    s = "".join(result)
    assert s
    return s


_SUBS = [
    (re.compile("–(\d)"), _replace_negative),
    (re.compile("[“”‘’–—…№←⇐⇒→Œœ]"), _replace_simple),
    (re.compile("[\U0001F3FB-\U0001F3FF]"), ""),  # emoji skin color
    (re.compile("[\u270a\U0001F300-\U0001F6FF\U0001F900-\U0001F9FF]"), _replace_emoji),
    (re.compile("(^)?[⌘⇧⌥⌃]((?=\S))?"), _replace_modifier_key),
    (re.compile("((?<=[^⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞ \t]))?[⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]((?=\S))?"), _replace_fraction),
    (re.compile("[\u0100-\u02af]|.[\u0300-\u036f]+"), _replace_accented),
    (re.compile("π"), "pi"),
]


def to_latin1(s):
    for r, repl in _SUBS:
        s = r.sub(repl, s)
    s.encode("latin1")  # Assert encodable
    return s