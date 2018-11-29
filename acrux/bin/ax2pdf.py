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

import acrux
import acrux.text
import argparse
import io
import json
import procyon
import sys
from reportlab import platypus
from reportlab.lib import colors, pagesizes, styles, units
from reportlab.platypus import flowables

outer_line = colors.black
inner_line = colors.Color(0.4, 0.4, 0.4)
circle_line = colors.Color(0.2, 0.2, 0.2)


def ax2pdf(pod):
    ax = acrux.load(pod)
    pdf = io.BytesIO()
    doc = platypus.SimpleDocTemplate(
        pdf,
        pagesize=pagesizes.landscape(pagesizes.A4),
        topMargin=10 * units.mm,
        leftMargin=10 * units.mm,
        rightMargin=10 * units.mm,
        bottomMargin=10 * units.mm)

    sample_style_sheet = styles.getSampleStyleSheet()
    title_style = sample_style_sheet["Title"]
    heading1_style = sample_style_sheet["Heading1"]
    body_style = sample_style_sheet["BodyText"]
    title_style.alignment = 0
    title_style.fontSize = 18
    title_style.leading = 36
    heading1_style.fontSize = 14
    heading1_style.leading = 16
    body_style.fontSize = 13
    body_style.leading = 15
    clue_number_style = body_style.clone("ClueNumber")
    clue_number_style.alignment = 2
    caption_style = body_style.clone("ClueNumber")
    caption_style.fontSize = 10

    title = [platypus.Paragraph(ax.title, title_style)]

    grid_column = []
    grid = CrosswordGrid(ax)
    grid_column.append(grid)
    grid_column.append(
        platypus.Paragraph("<a href=\"https://twotaled.com/cross/\">twotaled.com/cross/</a>",
                           caption_style))

    across_cells = []
    down_cells = []
    for clue in sorted(ax.clues.values(), key=lambda clue: clue.number):
        if clue.direction == acrux.Dir.ACROSS:
            cells = across_cells
        else:
            cells = down_cells
        cells.append([
            platypus.Paragraph("%d." % clue.number, clue_number_style),
            platypus.Paragraph(acrux.text.to_latin1(clue.text), body_style),
        ])

    clue_style = platypus.TableStyle([
        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0.5 * units.mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0.5 * units.mm),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * units.mm),
    ])
    across_column = []
    across_column.append(platypus.Paragraph("Across", heading1_style))
    across_column.append(
        platypus.Table(across_cells, colWidths=[8.5 * units.mm, None], style=clue_style))
    down_column = []
    down_column.append(platypus.Paragraph("Down", heading1_style))
    down_column.append(
        platypus.Table(down_cells, colWidths=[8.5 * units.mm, None], style=clue_style))

    flows = [
        platypus.Table(
            [[title, "", ""], [across_column, down_column, grid_column]],
            colWidths=[None, None, grid.width + 5 * units.mm],
            style=platypus.TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("SPAN", (0, 0), (-1, 0)),
            ]))
    ]

    doc.build(flows, onFirstPage=on_first_page(ax))
    data = pdf.getvalue()
    pdf.close()
    return data


def on_first_page(ax):
    def fn(canvas, doc):
        canvas.setTitle(ax.title)
        canvas.setAuthor(ax.author)

    return fn


class CrosswordGrid(flowables.Flowable):
    def __init__(self, ax):
        self.ax = ax
        self.width = ((8.5 * ax.width) + (0.25 * (ax.width - 1)) + (0.75 * 2)) * units.mm
        self.height = ((8.5 * ax.height) + (0.25 * (ax.height - 1)) + (0.75 * 2)) * units.mm

    def wrap(self, *args):
        return (0, self.width)

    def draw(self):
        self._draw_blocks()
        self._draw_lines()
        self._draw_circles()
        self._draw_numbers()

    def _at(self, x, y):
        return ((0.625 + (x * 8.75)) * units.mm,
                (0.625 + ((self.ax.height - y) * 8.75)) * units.mm)

    def _draw_blocks(self):
        for y, row in enumerate(self.ax.grid):
            for x, cell in enumerate(row):
                if cell.block:
                    self.canv.setFillColor(colors.black)
                    left, top = self._at(x, y)
                    right, bottom = self._at(x + 1, y + 1)
                    self.canv.rect(left, top, right - left, bottom - top, fill=True, stroke=False)

    def _draw_lines(self):
        hard_edges = set()
        soft_edges = set()
        for x in range(self.ax.width):
            for y in range(self.ax.height):
                if is_empty(self.ax, x, y):
                    continue

                if is_empty(self.ax, x - 1, y):
                    hard_edges.add((x, y + 1, x, y))
                else:
                    soft_edges.add((x, y, x, y + 1))
                if is_empty(self.ax, x + 1, y):
                    hard_edges.add((x + 1, y, x + 1, y + 1))

                if is_empty(self.ax, x, y - 1):
                    hard_edges.add((x, y, x + 1, y))
                else:
                    soft_edges.add((x, y, x + 1, y))
                if is_empty(self.ax, x, y + 1):
                    hard_edges.add((x + 1, y + 1, x, y + 1))

        self._draw_soft_edges(soft_edges)
        self._draw_hard_edges(hard_edges)

    def _draw_soft_edges(self, soft_edges):
        self.canv.setFillColor(colors.transparent)
        self.canv.setStrokeColor(inner_line)
        self.canv.setLineWidth(0.25 * units.mm)
        for ax, ay, bx, by in soft_edges:
            ax1, ay1 = self._at(ax, ay)
            bx1, by1 = self._at(bx, by)
            p = self.canv.beginPath()
            p.moveTo(ax1, ay1)
            p.lineTo(bx1, by1)
            p.close()
            self.canv.drawPath(p)

    def _draw_hard_edges(self, hard_edges):
        self.canv.setFillColor(colors.transparent)
        self.canv.setStrokeColor(outer_line)
        self.canv.setLineWidth(0.75 * units.mm)

        while hard_edges:
            # Pick the top-most, left-most starting edge.
            curr = sorted(hard_edges)[0]
            hard_edges.remove(curr)
            ax, ay, bx, by = curr
            poly = [(ax, ay), (bx, by)]

            # Wind around, preferring a left turn where possible; else straight; else right. If
            # none of those three is possible, the polygon is done.
            while True:
                adjustments = [(by - ay, bx - ax), (bx - ax, by - ay), (ay - by, ax - bx)]
                candidates = [(bx, by, bx + dx, by + dy) for dx, dy in adjustments]
                try:
                    curr = next(c for c in candidates if c in hard_edges)
                except StopIteration:
                    break
                hard_edges.remove(curr)
                ax, ay, bx, by = curr

                # Avoid unnecessary midpoints in a straight edge.
                if (poly[-2][0] == poly[-1][0] == bx) or (poly[-2][1] == poly[-1][1] == by):
                    poly.pop()
                poly.append((bx, by))
            poly.pop()

            # Convert from grid space to paper space.
            poly = [self._at(x, y) for x, y in poly]

            # Push vertices 0.25 mm to the left. If the winding is clockwise, this is outward. If
            # the winding is counter-clockwise, this is inward.
            for i in range(len(poly)):
                (ax, ay), (bx, by) = poly[i], poly[(i + 1) % len(poly)]
                if ax < bx:
                    ay += 0.25 * units.mm
                    by += 0.25 * units.mm
                elif ax > bx:
                    ay -= 0.25 * units.mm
                    by -= 0.25 * units.mm
                elif ay > by:
                    ax += 0.25 * units.mm
                    bx += 0.25 * units.mm
                elif ay < by:
                    ax -= 0.25 * units.mm
                    bx -= 0.25 * units.mm
                poly[i], poly[(i + 1) % len(poly)] = (ax, ay), (bx, by)

            p = self.canv.beginPath()
            p.moveTo(*poly[0])
            for x, y in poly[1:]:
                p.lineTo(x, y)
            p.close()
            self.canv.drawPath(p)

    def _draw_circles(self):
        self.canv.setFillColor(colors.transparent)
        self.canv.setStrokeColor(circle_line)
        self.canv.setLineWidth(0.25 * units.mm)

        for y, row in enumerate(self.ax.grid):
            for x, cell in enumerate(row):
                if "circle" in cell.style:
                    left, top = self._at(x, y)
                    right, bottom = self._at(x + 1, y + 1)
                    cx, cy = (left + right) / 2, (top + bottom) / 2
                    r = right - cx - (0.25 * units.mm)
                    p = self.canv.beginPath()
                    p.circle(cx, cy, r)
                    self.canv.drawPath(p)

    def _draw_numbers(self):
        for y, row in enumerate(self.ax.grid):
            for x, cell in enumerate(row):
                if cell.number:
                    left, top = self._at(x, y)
                    textobject = self.canv.beginText()
                    textobject.setTextOrigin(left + 1, top - 6)
                    textobject.setFont("Helvetica", 7)
                    textobject.setFillColor(colors.black)
                    textobject.textLine(str(cell.number))
                    self.canv.drawText(textobject)


def is_empty(ax, x, y):
    if not ((0 <= x < ax.width) and (0 <= y < ax.height)):
        return True
    return ax.grid[y][x].empty


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", metavar="IN.ax", nargs="?", type=argparse.FileType("r"))
    parser.add_argument("output", metavar="OUT.pdf", nargs="?", type=argparse.FileType("wb"))
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

    pdf = ax2pdf(pod)
    opts.output.write(pdf)


if __name__ == "__main__":
    main()
