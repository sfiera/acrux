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

import collections
import enum
import re

FILE_KEYS = {"grid", "subs", "clues", "title", "author", "copyright"}
CELL_KEYS = {"text", "style"}

DEFAULT_REPLACEMENTS = {
    " ": {
        "empty": True,
    },
    "#": {
        "block": True,
    },
}


def load(pod):
    assert isinstance(pod, dict)
    keys = frozenset(pod)
    assert keys <= FILE_KEYS

    lines = pod["grid"].splitlines()
    grid = _load_grid(pod["grid"], pod.get("subs", {}))

    height = len(grid)
    width = max(len(line) for line in grid)
    for line in grid:
        while len(line) < width:
            line.append(Cell(empty=True))

    answers = _find_answers(grid)
    clues = {}
    answer_counts = collections.defaultdict(int)
    for c in answers:
        grid[c.y][c.x].number = c.number
        clues[c.answer, answer_counts[c.answer]] = c
        answer_counts[c.answer] += 1

    for answer, clue in pod.get("clues", {}).items():
        if not isinstance(clue, list):
            clue = [clue]
        for i, text in enumerate(clue):
            clues[answer, i].text = text

    return Crossword(
        grid=grid,
        clues=clues,
        title=pod.get("title"),
        author=pod.get("author"),
        copyright=pod.get("copyright"))


def _load_grid(grid, subs):
    lines = grid.splitlines()
    grid = []

    replace = DEFAULT_REPLACEMENTS.copy()
    replace.update(subs)
    matches = [re.escape(k) for k in replace]
    matches.sort(key=lambda x: -len(x))
    matches.append(".")

    pattern = re.compile("|".join(matches))
    for line in lines:
        grid.append([])
        pos = 0
        while pos < len(line):
            m = pattern.match(line, pos=pos)
            pos = m.end()
            m = m.group(0)
            if m in replace:
                m = replace[m]
            if isinstance(m, list):
                m = {"text": m[0], "options": m}
            if not isinstance(m, dict):
                m = {"text": m}
            grid[-1].append(Cell(**m))

    return grid


def _find_answers(grid):
    height = len(grid)
    width = len(grid[0])

    answers = []
    n = 0
    for y in range(height):
        for x in range(width):
            cell = grid[y][x]
            if cell.text is None:
                continue
            has_down = has_across = False
            if (y == 0) or (grid[y - 1][x].text is None):
                if (y < (height - 1)) and (grid[y + 1][x].text is not None):
                    has_down = True
            if (x == 0) or (grid[y][x - 1].text is None):
                if (x < (width - 1)) and (grid[y][x + 1].text is not None):
                    has_across = True
            if not (has_down or has_across):
                continue

            n += 1
            if has_across:
                answers.append(Clue(x, y, n, Dir.ACROSS, across_word(grid, x, y)))
            if has_down:
                answers.append(Clue(x, y, n, Dir.DOWN, down_word(grid, x, y)))

    return answers


def across_word(grid, x, y):
    line = grid[y]
    word = ""
    for x in range(x, len(line)):
        if line[x].text is None:
            break
        word += line[x].text
    return word


def down_word(grid, x, y):
    word = ""
    for y in range(y, len(grid)):
        if grid[y][x].text is None:
            break
        word += grid[y][x].text
    return word


class Crossword(object):
    def __init__(self, grid, clues, title=None, author=None, copyright=None):
        self.grid = grid
        self.clues = clues
        self.title = title
        self.author = author
        self.copyright = copyright

        self.width = len(grid[0])
        self.height = len(grid)
        assert all((len(line) == self.width) for line in grid)


class Cell(object):
    def __init__(self, text=None, options=None, style=[], block=False, empty=False, number=None):
        self.text = text
        self.options = options
        self.style = style
        self.block = block
        self.empty = empty
        self.number = number


class Dir(enum.Enum):
    ACROSS = 1
    DOWN = 2


class Clue(object):
    def __init__(self, x, y, number, direction, answer):
        self.x = x
        self.y = y
        self.number = number
        self.direction = direction
        self.text = None
        self.answer = answer
