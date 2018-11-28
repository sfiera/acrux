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

import acrux
import acrux.text
import argparse
import itertools
import procyon
import puz
import sys


def ax2ipuz(pod):
    ax = acrux.load(pod)

    p = puz.Puzzle()
    p.title = ax.title
    p.author = ax.author
    p.copyright = ax.copyright
    p.width = ax.width
    p.height = ax.height
    p.version = (1, 4, b"\0")

    all_cells = list(itertools.chain(*ax.grid))
    p.fill = "".join(fill_char(cell) for cell in all_cells)
    p.solution = "".join(solution_char(cell) for cell in all_cells)

    for clue in sorted(ax.clues.values(), key=lambda c: (c.number, c.direction.value)):
        c = clue.text
        c = acrux.text.strip_html(c)
        c = acrux.text.to_latin1(c)
        p.clues.append(c)

    return p


def fill_char(cell):
    if cell.block:
        return "."
    return "-"


def solution_char(cell):
    if cell.block:
        return "."
    elif cell.options:
        return cell.options[0][0]
    return cell.text[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", metavar="IN.ax", nargs="?", type=argparse.FileType("r"))
    parser.add_argument("output", metavar="OUT.ipuz", nargs="?", type=argparse.FileType("wb"))
    opts = parser.parse_args()

    if opts.input is None:
        opts.input = sys.stdin
        input_name = "-"
    else:
        input_name = opts.input.name

    if opts.output is None:
        opts.output = sys.stdout
        output_name = "-"
    else:
        output_name = opts.output.name

    try:
        pod = procyon.load(opts.input)
    except procyon.ProcyonDecodeError as e:
        print("%s:%s" % (input_name, e))
        sys.exit(1)

    p = ax2ipuz(pod)
    opts.output.write(p.tobytes())


if __name__ == "__main__":
    main()
