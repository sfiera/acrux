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
import argparse
import json
import procyon
import sys

_IPUZ_HEADER = """
, "title": %s
, "author": %s
, "copyright": %s
, "dimensions": { "width": 9, "height": 9 }
""".strip()


def ax2ipuz(pod):
    ax = acrux.load(pod)
    ipuz = {
        "version": "http://ipuz.org/v1",
        "kind": ["http://ipuz.org/crossword#1"],
    }

    if ax.title is not None:
        ipuz["title"] = ax.title
    if ax.author is not None:
        ipuz["author"] = ax.author
    if ax.copyright is not None:
        ipuz["copyright"] = ax.copyright
    ipuz["dimensions"] = {"width": ax.width, "height": ax.height}

    puzzle = ipuz["puzzle"] = []
    solution = ipuz["solution"] = []

    for line in ax.grid:
        puzzle.append([])
        solution.append([])
        for cell in line:
            if cell.block:
                puzzle[-1].append("#")
                solution[-1].append("#")
            elif "circle" in cell.style:
                puzzle[-1].append({"cell": cell.number or 0, "style": {"shapebg": "circle"}})
                solution[-1].append(cell.text)
            else:
                puzzle[-1].append(cell.number or 0)
                solution[-1].append(cell.text)

    ipuz["clues"] = {}
    across = ipuz["clues"]["Across"] = []
    down = ipuz["clues"]["Down"] = []
    for c in ax.clues.values():
        if c.direction == acrux.Dir.ACROSS:
            clues = across
        else:
            clues = down
        clues.append([c.number, c.text])

    return ipuz


def dump_ipuz(x, f, indent):
    f.write('{ "version": %s\n' % (json.dumps(x["version"], ensure_ascii=False)))
    f.write(', "kind": %s\n' % (json.dumps(x["kind"], ensure_ascii=False)))
    for k in ["title", "author", "copyright"]:
        if k in x:
            f.write(', "%s": %s\n' % (k, json.dumps(x[k], ensure_ascii=False)))
    f.write(', "dimensions": %s\n' % (json.dumps(x["dimensions"], ensure_ascii=False)))

    for k in ["puzzle", "solution"]:
        f.write(', "%s":\n' % k)
        line_prefix = "  [ "
        for row in aligned(x[k]):
            f.write(line_prefix)
            line_prefix = "  , "
            cell_prefix = "["
            for cell, padding in row:
                f.write(cell_prefix)
                cell_prefix = ", " + (" " * padding)
                f.write(cell)
            f.write(" " * padding)
            f.write("]\n")
        f.write("  ]\n")

    f.write(', "clues":\n')
    f.write('  { "Across":\n')
    clue_prefix = "    [ "
    for clue in x["clues"]["Across"]:
        f.write(clue_prefix)
        clue_prefix = "    , "
        json.dump(clue, f, ensure_ascii=False)
        f.write("\n")
    f.write("    ]\n")
    f.write('  , "Down":\n')
    clue_prefix = "    [ "
    for clue in x["clues"]["Down"]:
        f.write(clue_prefix)
        clue_prefix = "    , "
        json.dump(clue, f, ensure_ascii=False)
        f.write("\n")
    f.write("    ]\n")
    f.write("  }\n")
    f.write("}\n")


def aligned(grid):
    grid = [[json.dumps(cell, ensure_ascii=False) for cell in row] for row in grid]

    result = []
    width = max(len(row) for row in grid)
    max_width = max(max(len(cell) for cell in row) for row in grid)
    for row in grid:
        result.append([])
        for i, cell in enumerate(row):
            result[-1].append((cell, max_width - len(cell)))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", metavar="IN.ax", nargs="?", type=argparse.FileType("r"))
    parser.add_argument("output", metavar="OUT.ipuz", nargs="?", type=argparse.FileType("w"))
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

    ipuz = ax2ipuz(pod)
    dump_ipuz(ipuz, opts.output, indent=2)


if __name__ == "__main__":
    main()
