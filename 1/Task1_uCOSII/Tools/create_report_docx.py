# -*- coding: utf-8 -*-
"""Convert the Task 1 Markdown report to a formatted DOCX."""

import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BASE = Path(__file__).resolve().parents[2]
MD = BASE / "任务一_uCOS-II移植报告.md"
OUT = BASE / "任务一_uCOS-II移植报告.docx"

BODY_EA = "宋体"
HEAD_EA = "微软雅黑"
BODY_LATIN = "Times New Roman"
HEAD_LATIN = "Arial"
MONO = "Consolas"
DARK = RGBColor(0x1F, 0x3A, 0x5F)


def set_run_font(run, size=10.5, bold=None, color=None, mono=False, ea=BODY_EA):
    run.font.name = MONO if mono else BODY_LATIN
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    latin = MONO if mono else BODY_LATIN
    rFonts.set(qn("w:ascii"), latin)
    rFonts.set(qn("w:hAnsi"), latin)
    rFonts.set(qn("w:eastAsia"), ea)


def set_style_font(style, size, bold, color, latin, ea):
    style.font.name = latin
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.color.rgb = color
    rPr = style.element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), latin)
    rFonts.set(qn("w:hAnsi"), latin)
    rFonts.set(qn("w:eastAsia"), ea)


def add_runs(p, text, size=10.5, color=None):
    tokens = re.split(r"(\*\*.*?\*\*|`.*?`)", text)
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**") and len(tok) > 4:
            run = p.add_run(tok[2:-2])
            set_run_font(run, size=size, bold=True, color=color)
        elif tok.startswith("`") and tok.endswith("`") and len(tok) > 2:
            run = p.add_run(tok[1:-1])
            set_run_font(run, size=size - 0.5, mono=True, color=color)
        else:
            run = p.add_run(tok)
            set_run_font(run, size=size, color=color)


def shade_cell(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def shade_paragraph(p, fill="F2F2F2"):
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    pPr.append(shd)


def add_code_block(doc, lines):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.25)
    p.paragraph_format.right_indent = Cm(0.1)
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.0
    shade_paragraph(p)
    for i, line in enumerate(lines):
        run = p.add_run(line if line else " ")
        set_run_font(run, size=8.5, mono=True)
        if i != len(lines) - 1:
            run.add_break()


def add_table(doc, rows):
    if not rows:
        return
    ncols = max(len(r) for r in rows)
    rows = [r + [""] * (ncols - len(r)) for r in rows]
    table = doc.add_table(rows=len(rows), cols=ncols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    width = 16.0 / ncols
    for i, row in enumerate(rows):
        trPr = table.rows[i]._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        if i == 0:
            trPr.append(OxmlElement("w:tblHeader"))
        for j, text in enumerate(row):
            cell = table.cell(i, j)
            cell.width = Cm(width)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            add_runs(p, text, size=9)
            if i == 0:
                for run in p.runs:
                    run.bold = True
                shade_cell(cell, "D9E2F3")
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_footer(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("STM32F103C8T6 + uC/OS-II 任务一    第 ")
    set_run_font(run, size=8, color=RGBColor(0x70, 0x70, 0x70))
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    r = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = "1"
    r.append(t)
    fld.append(r)
    p._p.append(fld)
    run = p.add_run(" 页")
    set_run_font(run, size=8, color=RGBColor(0x70, 0x70, 0x70))


def main():
    text = MD.read_text(encoding="utf-8")
    lines = text.splitlines()

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.2)
    section.right_margin = Cm(2.0)

    set_style_font(doc.styles["Normal"], 10.5, False, RGBColor(0x20, 0x20, 0x20), BODY_LATIN, BODY_EA)
    doc.styles["Normal"].paragraph_format.line_spacing = 1.22
    doc.styles["Normal"].paragraph_format.space_after = Pt(5)
    for name, size in (("Heading 1", 16), ("Heading 2", 13), ("Heading 3", 11.5)):
        set_style_font(doc.styles[name], size, True, DARK, HEAD_LATIN, HEAD_EA)
        doc.styles[name].paragraph_format.space_before = Pt(12 if name != "Heading 3" else 8)
        doc.styles[name].paragraph_format.space_after = Pt(5)
    for name in ("List Bullet", "List Number"):
        set_style_font(doc.styles[name], 10.5, False, RGBColor(0x20, 0x20, 0x20), BODY_LATIN, BODY_EA)
        doc.styles[name].paragraph_format.space_after = Pt(2)

    # ---- cover ----
    for _ in range(3):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("嵌入式实时操作系统（RTOS）实验报告")
    set_run_font(run, size=15, bold=True, color=RGBColor(0x40, 0x40, 0x40), ea=HEAD_EA)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    run = p.add_run("任务一")
    set_run_font(run, size=26, bold=True, color=DARK, ea=HEAD_EA)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    run = p.add_run("uC/OS-II 在 STM32F103C8T6 上的移植与多任务实验")
    set_run_font(run, size=18, bold=True, color=DARK, ea=HEAD_EA)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    run = p.add_run("—— 1 s / 3 s LED 控制 + 2 s 串口问候 ——")
    set_run_font(run, size=11, color=RGBColor(0x60, 0x60, 0x60), ea=HEAD_EA)

    for _ in range(4):
        doc.add_paragraph()

    info = [
        ("课程名称", "嵌入式实时操作系统"),
        ("实验题目", "uC/OS-II 移植与多任务实验"),
        ("开发环境", "Keil MDK 5.38 + ARM Compiler 6.19 + DAPLink"),
        ("目标芯片", "STM32F103C8T6（Cortex-M3，64 KB Flash / 20 KB SRAM）"),
        ("姓    名", "____________________"),
        ("学    号", "____________________"),
        ("日    期", "2026 年 10 月 30 日"),
    ]
    table = doc.add_table(rows=len(info), cols=2)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, (k, v) in enumerate(info):
        c0, c1 = table.cell(i, 0), table.cell(i, 1)
        c0.width = Cm(4.2)
        c1.width = Cm(11.8)
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r0 = p0.add_run(k)
        set_run_font(r0, size=10.5, bold=True, ea=HEAD_EA)
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        set_run_font(r1, size=10.5)

    doc.add_page_break()
    add_footer(section)

    # ---- body ----
    i = 0
    pending = []
    first_h1 = True

    def flush():
        nonlocal pending
        if pending:
            p = doc.add_paragraph()
            add_runs(p, "".join(pending))
            pending = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            flush()
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i].rstrip("\n"))
                i += 1
            i += 1
            add_code_block(doc, code)
            continue

        if stripped.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                raw = lines[i].strip().strip("|")
                cells = [c.strip() for c in raw.split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                    rows.append(cells)
                i += 1
            add_table(doc, rows)
            continue

        if stripped.startswith("#"):
            flush()
            level = len(stripped) - len(stripped.lstrip("#"))
            title = stripped[level:].strip().replace("`", "")
            if level == 1:
                if first_h1:
                    first_h1 = False
                    i += 1
                    continue
                doc.add_heading(title, level=1)
            elif level == 2:
                doc.add_heading(title, level=1)
            elif level == 3:
                doc.add_heading(title, level=2)
            else:
                doc.add_heading(title, level=3)
            i += 1
            continue

        if stripped == "---":
            flush()
            i += 1
            continue

        if stripped.startswith("> "):
            flush()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.5)
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(6)
            add_runs(p, stripped[2:], size=9.5, color=RGBColor(0x60, 0x60, 0x60))
            for run in p.runs:
                run.italic = True
            i += 1
            continue

        m = re.match(r"^(\s*)[-*] (.*)$", line)
        if m:
            flush()
            indent = len(m.group(1))
            p = doc.add_paragraph(style="List Bullet 2" if indent >= 2 else "List Bullet")
            add_runs(p, m.group(2))
            i += 1
            continue

        if re.match(r"^\d+\. ", stripped):
            flush()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.75)
            p.paragraph_format.first_line_indent = Cm(-0.45)
            p.paragraph_format.space_after = Pt(2)
            add_runs(p, stripped)
            i += 1
            continue

        if not stripped:
            flush()
            i += 1
            continue

        pending.append(stripped)
        i += 1

    flush()

    doc.core_properties.title = "任务一：uC/OS-II 在 STM32F103C8T6 上的移植与多任务实验"
    doc.core_properties.subject = "嵌入式实时操作系统实验报告"
    doc.core_properties.author = "嵌入式 RTOS 实验"
    doc.save(OUT)

    # basic validation
    check = Document(OUT)
    print(f"saved: {OUT}")
    print(f"paragraphs={len(check.paragraphs)} tables={len(check.tables)} sections={len(check.sections)}")
    print(f"first text: {check.paragraphs[0].text!r}")


if __name__ == "__main__":
    main()