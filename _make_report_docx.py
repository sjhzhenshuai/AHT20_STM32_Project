# -*- coding: utf-8 -*-
"""Generate the combined Experiment 4 report DOCX from Markdown."""

import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image

BASE = Path(r"G:\文件\个人文件\作业\嵌入式基础\实验4")
MD = BASE / "实验4_综合实验报告.md"
OUT = BASE / "实验4_综合实验报告.docx"

DARK = RGBColor(0x1F, 0x3A, 0x5F)
MID = RGBColor(0x2E, 0x4A, 0x6B)
GRAY = RGBColor(0x59, 0x59, 0x59)
LIGHT = RGBColor(0x7F, 0x7F, 0x7F)
BODY_EA = "宋体"
HEAD_EA = "黑体"
BODY_LATIN = "Times New Roman"
HEAD_LATIN = "Arial"
MONO = "Consolas"


def set_run_font(run, size=12, bold=None, color=None, mono=False, ea=BODY_EA):
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


def shade_paragraph(p, fill="F2F2F2"):
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    pPr.append(shd)


def bottom_border(p, color="1F3A5F", sz="8"):
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), sz)
    bottom.set(qn("w:space"), "6")
    bottom.set(qn("w:color"), color)
    pBdr.append(bottom)
    pPr.append(pBdr)


def add_runs(p, text, size=12, color=None, bold=False):
    tokens = re.split(r"(\*\*.*?\*\*|`.*?`)", text)
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**") and len(tok) > 4:
            run = p.add_run(tok[2:-2])
            set_run_font(run, size=size, bold=True, color=color)
        elif tok.startswith("`") and tok.endswith("`") and len(tok) > 2:
            run = p.add_run(tok[1:-1])
            set_run_font(run, size=size - 0.5, mono=True, color=RGBColor(0xA3, 0x15, 0x15))
        else:
            run = p.add_run(tok)
            set_run_font(run, size=size, bold=bold, color=color)


def add_hyperlink(paragraph, url, text, size=11):
    part = paragraph.part
    r_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    rPr.append(color)
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rPr.append(u)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), str(int(size * 2)))
    rPr.append(sz)
    new_run.append(rPr)
    t = OxmlElement("w:t")
    t.text = text
    t.set(qn("xml:space"), "preserve")
    new_run.append(t)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run(text)
    set_run_font(run, size=9, color=GRAY)
    return p


def add_code_block(doc, lines):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.left_indent = Cm(0.3)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.0
    shade_paragraph(p)
    for i, line in enumerate(lines):
        run = p.add_run(line if line else " ")
        set_run_font(run, size=8.5, mono=True)
        if i != len(lines) - 1:
            run.add_break()


def shade_cell(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def add_table(doc, rows):
    if not rows:
        return
    ncols = max(len(r) for r in rows)
    rows = [r + [""] * (ncols - len(r)) for r in rows]
    table = doc.add_table(rows=len(rows), cols=ncols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    total = 16.0
    widths = [total / ncols] * ncols
    if ncols == 2:
        widths = [4.4, 11.6]
    elif ncols == 3:
        widths = [4.2, 5.9, 5.9]
    elif ncols == 4:
        widths = [3.6, 4.2, 4.0, 4.2]
    elif ncols == 5:
        widths = [2.9, 3.0, 3.2, 3.2, 3.7]
    font_size = 8.2 if (ncols >= 5 or len(rows) > 12) else 9.0
    for i, row in enumerate(rows):
        trPr = table.rows[i]._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        if i == 0:
            trPr.append(OxmlElement("w:tblHeader"))
        for j, text in enumerate(row):
            cell = table.cell(i, j)
            cell.width = Cm(widths[j])
            p = cell.paragraphs[0]
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.0
            add_runs(p, text, size=font_size)
            if i == 0:
                for run in p.runs:
                    run.bold = True
                shade_cell(cell, "D9E2F3")
    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(2)


def add_image(doc, path, alt, max_w=16.0, max_h=20.5):
    p = Path(path)
    if not p.is_absolute():
        p = BASE / p
    with Image.open(p) as im:
        w, h = im.size
    width = min(max_w, max_h * w / h)
    doc.add_picture(str(p), width=Cm(width))
    pic_para = doc.paragraphs[-1]
    pic_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pic_para.paragraph_format.first_line_indent = Cm(0)
    pic_para.paragraph_format.space_before = Pt(6)
    pic_para.paragraph_format.space_after = Pt(0)
    add_caption(doc, alt)


def add_video(doc, path, caption):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    add_hyperlink(p, path, f"{caption}（点击打开 {path}）", size=11)
    add_caption(doc, caption)


def add_page_number_footer(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("— ")
    set_run_font(run, size=9, color=GRAY)
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    r = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = "1"
    r.append(t)
    fld.append(r)
    p._p.append(fld)
    run = p.add_run(" —")
    set_run_font(run, size=9, color=GRAY)


def add_header(section):
    header = section.header
    p = header.paragraphs[0]
    p.paragraph_format.tab_stops.add_tab_stop(Cm(16.6), 2)  # right tab
    run = p.add_run("嵌入式基础实验4 · uC/OS-II + AHT20")
    set_run_font(run, size=9, color=LIGHT)
    run = p.add_run("\t综合实验报告")
    set_run_font(run, size=9, color=LIGHT)
    bottom_border(p, "BFC9D6", "4")


def main():
    text = MD.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Extract cover
    cover_lines = []
    body_start = 0
    for i, l in enumerate(lines):
        if l.strip() == "<!-- pagebreak -->":
            body_start = i + 1
            break
        cover_lines.append(l)

    title = ""
    subtitles = []
    cover_table = []
    for l in cover_lines:
        s = l.strip()
        if s.startswith("# ") and not title:
            title = s[2:].strip()
        elif s.startswith("## "):
            subtitles.append(s[3:].strip())
        elif s.startswith("|"):
            raw = s.strip().strip("|")
            cells = [c.strip() for c in raw.split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                continue
            cover_table.append(cells)

    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.2)
    section.right_margin = Cm(2.0)
    section.header_distance = Cm(1.2)
    section.footer_distance = Cm(1.2)
    section.different_first_page_header_footer = True

    set_style_font(doc.styles["Normal"], 12, False, RGBColor(0x1A, 0x1A, 0x1A), BODY_LATIN, BODY_EA)
    doc.styles["Normal"].paragraph_format.line_spacing = 1.5
    doc.styles["Normal"].paragraph_format.space_after = Pt(4)
    for name, size in (("Heading 1", 16), ("Heading 2", 14), ("Heading 3", 12.5)):
        set_style_font(doc.styles[name], size, True, DARK, HEAD_LATIN, HEAD_EA)
        doc.styles[name].paragraph_format.space_before = Pt(16 if name == "Heading 1" else 10)
        doc.styles[name].paragraph_format.space_after = Pt(8 if name == "Heading 1" else 5)
        doc.styles[name].paragraph_format.keep_with_next = True
        doc.styles[name].paragraph_format.line_spacing = 1.15

    # Cover page
    for _ in range(4):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("嵌入式基础课程实验报告")
    set_run_font(r, size=13, color=GRAY, ea=HEAD_EA)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    r = p.add_run(title)
    set_run_font(r, size=24, bold=True, color=DARK, ea=HEAD_EA)

    for sub in subtitles[:2]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        r = p.add_run(sub)
        set_run_font(r, size=14.5, bold=True, color=MID, ea=HEAD_EA)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    bottom_border(p, "1F3A5F", "10")

    for _ in range(2):
        doc.add_paragraph()

    if cover_table:
        table = doc.add_table(rows=len(cover_table), cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Table Grid"
        for i, row in enumerate(cover_table):
            c0, c1 = table.cell(i, 0), table.cell(i, 1)
            c0.width = Cm(4.2)
            c1.width = Cm(10.8)
            p0 = c0.paragraphs[0]
            p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r0 = p0.add_run(row[0] if row else "")
            set_run_font(r0, size=11, bold=True, ea=HEAD_EA)
            p1 = c1.paragraphs[0]
            r1 = p1.add_run(row[1] if len(row) > 1 else "")
            set_run_font(r1, size=11)

    for _ in range(3):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("2026 年 10 月 30 日")
    set_run_font(r, size=12, color=GRAY, ea=HEAD_EA)

    doc.add_page_break()
    add_header(section)
    add_page_number_footer(section)

    # Body parser
    i = body_start
    pending = []
    skip_caption = False

    def flush():
        nonlocal pending
        if pending:
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Cm(0.85)
            add_runs(p, "".join(pending))
            pending = []

    while i < len(lines):
        line = lines[i]
        s = line.strip()

        if s == "<!-- pagebreak -->":
            flush()
            doc.add_page_break()
            i += 1
            continue

        if s.startswith("```"):
            flush()
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i].rstrip("\n"))
                i += 1
            i += 1
            add_code_block(doc, code)
            continue

        if s.startswith("|"):
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

        m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", s)
        if m:
            flush()
            alt, path = m.group(1), m.group(2)
            max_w, max_h = 16.0, 20.5
            if Path(path).name in ("1.jpg", "2.jpg", "3.jpg"):
                max_w, max_h = 15.0, 12.0
            elif Path(path).name in ("16.png", "17.png"):
                max_w, max_h = 15.0, 12.0
            elif Path(path).name in ("32.png", "33.png", "34.png", "35.png", "36.png", "37.png"):
                max_w, max_h = 16.0, 10.5
            elif Path(path).name == "18.png":
                max_w, max_h = 16.0, 10.0
            elif Path(path).name in ("38.png", "39.png"):
                max_w, max_h = 14.5, 12.0
            elif Path(path).name == "40.jpg":
                max_w, max_h = 9.5, 21.0
            add_image(doc, path, alt, max_w, max_h)
            skip_caption = True
            i += 1
            continue

        m = re.match(r"\[([^\]]+)\]\(([^)]+\.mp4)\)", s)
        if m:
            flush()
            add_video(doc, m.group(2), m.group(1))
            skip_caption = True
            i += 1
            continue

        if s.startswith("*") and s.endswith("*") and len(s) > 2 and ("图 " in s or "视频 " in s):
            if skip_caption:
                skip_caption = False
                i += 1
                continue
            flush()
            add_caption(doc, s[1:-1])
            i += 1
            continue

        if s.startswith("#"):
            flush()
            level = len(s) - len(s.lstrip("#"))
            h = s[level:].strip().replace("`", "")
            if level == 2:
                if re.match(r"^(3|4|5|6|7|附录 A|附录 B|附录 C|附录 D)\b", h) and not h.startswith("3.1"):
                    doc.add_page_break()
                doc.add_heading(h, level=1)
            elif level == 3:
                doc.add_heading(h, level=2)
            elif level == 4:
                doc.add_heading(h, level=3)
            else:
                doc.add_heading(h, level=3)
            i += 1
            continue

        if s.startswith("> "):
            flush()
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.left_indent = Cm(0.5)
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(6)
            add_runs(p, s[2:], size=10.5, color=GRAY)
            for run in p.runs:
                run.italic = True
            i += 1
            continue

        m = re.match(r"^(\s*)[-*] (.*)$", line)
        if m:
            flush()
            indent = len(m.group(1))
            p = doc.add_paragraph(style="List Bullet 2" if indent >= 2 else "List Bullet")
            p.paragraph_format.first_line_indent = Cm(0)
            add_runs(p, m.group(2))
            i += 1
            continue

        if re.match(r"^\d+\. ", s):
            flush()
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Cm(-0.45)
            p.paragraph_format.left_indent = Cm(0.75)
            p.paragraph_format.space_after = Pt(2)
            add_runs(p, s)
            i += 1
            continue

        if not s:
            flush()
            i += 1
            continue

        pending.append(s)
        i += 1

    flush()

    doc.core_properties.title = title
    doc.core_properties.subject = "嵌入式基础实验4：uC/OS-II 移植与 AHT20 温湿度采集"
    doc.core_properties.author = "嵌入式基础实验"
    doc.save(OUT)

    check = Document(OUT)
    print(f"saved: {OUT}")
    print(f"paragraphs={len(check.paragraphs)} tables={len(check.tables)} inline_shapes={len(check.inline_shapes)}")
    print(f"size={OUT.stat().st_size/1024/1024:.1f} MB")


if __name__ == "__main__":
    main()