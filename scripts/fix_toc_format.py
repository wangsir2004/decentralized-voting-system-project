from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}
W = NS["w"]
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def qn(name: str) -> str:
    prefix, local = name.split(":")
    if prefix != "w":
        raise ValueError(name)
    return f"{{{W}}}{local}"


def text_of(p: etree._Element) -> str:
    return "".join(t.text or "" for t in p.xpath(".//w:t", namespaces=NS))


def normalize(text: str) -> str:
    return " ".join(text.split())


def body_paragraphs(root: etree._Element) -> list[etree._Element]:
    body = root.find("w:body", namespaces=NS)
    if body is None:
        raise ValueError("document.xml has no body")
    return [child for child in body if child.tag == qn("w:p")]


def get_or_add(parent: etree._Element, child_name: str, first: bool = False) -> etree._Element:
    child = parent.find(child_name, namespaces=NS)
    if child is None:
        child = etree.Element(qn(child_name))
        if first:
            parent.insert(0, child)
        else:
            parent.append(child)
    return child


def remove_children(parent: etree._Element, names: set[str]) -> None:
    wanted = {qn(name) for name in names}
    for child in list(parent):
        if child.tag in wanted:
            parent.remove(child)


def rpr(font_east: str, font_west: str, size_half_points: str, *, bold: bool = False) -> etree._Element:
    r_pr = etree.Element(qn("w:rPr"))
    fonts = etree.Element(qn("w:rFonts"))
    fonts.set(qn("w:eastAsia"), font_east)
    fonts.set(qn("w:ascii"), font_west)
    fonts.set(qn("w:hAnsi"), font_west)
    fonts.set(qn("w:cs"), font_west)
    r_pr.append(fonts)
    if bold:
        r_pr.append(etree.Element(qn("w:b")))
        r_pr.append(etree.Element(qn("w:bCs")))
    for tag in ("w:sz", "w:szCs"):
        sz = etree.Element(qn(tag))
        sz.set(qn("w:val"), size_half_points)
        r_pr.append(sz)
    color = etree.Element(qn("w:color"))
    color.set(qn("w:val"), "000000")
    r_pr.append(color)
    underline = etree.Element(qn("w:u"))
    underline.set(qn("w:val"), "none")
    r_pr.append(underline)
    return r_pr


def text_run(text: str, font_east: str, font_west: str = "Times New Roman", size: str = "24", *, bold: bool = False) -> etree._Element:
    run = etree.Element(qn("w:r"))
    run.append(rpr(font_east, font_west, size, bold=bold))
    t = etree.Element(qn("w:t"))
    t.set(XML_SPACE, "preserve")
    t.text = text
    run.append(t)
    return run


def tab_run() -> etree._Element:
    run = etree.Element(qn("w:r"))
    # Keep the tab itself unstyled; the paragraph tab stop controls alignment.
    run.append(etree.Element(qn("w:tab")))
    return run


def set_toc_title_format(p: etree._Element) -> None:
    p_pr = get_or_add(p, "w:pPr", first=True)
    remove_children(p_pr, {"w:spacing", "w:jc", "w:rPr"})
    spacing = etree.Element(qn("w:spacing"))
    spacing.set(qn("w:line"), "300")
    spacing.set(qn("w:lineRule"), "auto")
    p_pr.append(spacing)
    jc = etree.Element(qn("w:jc"))
    jc.set(qn("w:val"), "center")
    p_pr.append(jc)
    for child in list(p):
        if child.tag != qn("w:pPr"):
            p.remove(child)
    p.append(text_run("目　　录", "黑体", "Times New Roman", "36", bold=False))


def entry_level(title: str) -> int:
    stripped = title.strip()
    if re.match(r"^\d+\.\d+(?:\.\d+)?\b", stripped):
        return 2
    if re.match(r"^A\.\d+\b", stripped):
        return 2
    return 1


def normalize_entry_title(title: str) -> str:
    title = title.strip()
    title = re.sub(r"\s+", " ", title)
    chapter = re.match(r"^(第[一二三四五六七八九十]+章)\s+(.+)$", title)
    if chapter:
        return f"{chapter.group(1)}　{chapter.group(2)}"
    section = re.match(r"^(\d+(?:\.\d+)+)\s+(.+)$", title)
    if section:
        return f"{section.group(1)}　{section.group(2)}"
    appendix = re.match(r"^(附录[A-Z])\s+(.+)$", title)
    if appendix:
        return f"{appendix.group(1)}　{appendix.group(2)}"
    appendix_section = re.match(r"^(A\.\d+)\s+(.+)$", title)
    if appendix_section:
        return f"{appendix_section.group(1)}　{appendix_section.group(2)}"
    if title == "致谢":
        return "致　　谢"
    return title


def set_entry_ppr(p: etree._Element, level: int) -> None:
    p_pr = get_or_add(p, "w:pPr", first=True)
    remove_children(p_pr, {"w:tabs", "w:spacing", "w:ind", "w:jc", "w:rPr"})

    p_style = p_pr.find("w:pStyle", namespaces=NS)
    if p_style is None:
        p_style = etree.Element(qn("w:pStyle"))
        p_pr.insert(0, p_style)
    p_style.set(qn("w:val"), "TOC1" if level == 1 else "TOC2")

    tabs = etree.Element(qn("w:tabs"))
    tab = etree.Element(qn("w:tab"))
    tab.set(qn("w:val"), "right")
    tab.set(qn("w:leader"), "dot")
    tab.set(qn("w:pos"), "8325")
    tabs.append(tab)
    p_pr.append(tabs)

    spacing = etree.Element(qn("w:spacing"))
    spacing.set(qn("w:before"), "0")
    spacing.set(qn("w:after"), "0")
    spacing.set(qn("w:line"), "300")
    spacing.set(qn("w:lineRule"), "auto")
    p_pr.append(spacing)

    ind = etree.Element(qn("w:ind"))
    ind.set(qn("w:left"), "0" if level == 1 else "480")
    ind.set(qn("w:firstLine"), "0")
    p_pr.append(ind)


def rebuild_entry(p: etree._Element, title: str, page: str, level: int) -> None:
    hyperlink = p.find("w:hyperlink", namespaces=NS)
    anchor = hyperlink.get(qn("w:anchor")) if hyperlink is not None else None
    history = hyperlink.get(qn("w:history")) if hyperlink is not None else "1"

    set_entry_ppr(p, level)
    for child in list(p):
        if child.tag != qn("w:pPr"):
            p.remove(child)

    container = etree.Element(qn("w:hyperlink")) if anchor else p
    if anchor:
        container.set(qn("w:anchor"), anchor)
        container.set(qn("w:history"), history or "1")

    is_chapter = level == 1
    container.append(text_run(title, "黑体" if is_chapter else "宋体", "Times New Roman", "24"))
    container.append(tab_run())
    container.append(text_run(page, "宋体", "Times New Roman", "24"))

    if anchor:
        p.append(container)


def find_toc_bounds(paragraphs: list[etree._Element]) -> tuple[int, int]:
    start = next((i for i, p in enumerate(paragraphs) if normalize(text_of(p)) == "目 录"), -1)
    if start < 0:
        start = next((i for i, p in enumerate(paragraphs) if text_of(p).strip() == "目　　录"), -1)
    if start < 0:
        raise ValueError("TOC title not found")

    for i in range(start + 1, len(paragraphs)):
        text = normalize(text_of(paragraphs[i]))
        if text == "第一章 绪论":
            return start, i
    raise ValueError("TOC end not found")


def fix_toc(root: etree._Element) -> dict:
    paragraphs = body_paragraphs(root)
    start, end = find_toc_bounds(paragraphs)
    set_toc_title_format(paragraphs[start])

    fixed = []
    skipped = []
    pattern = re.compile(r"^(?P<title>.+?)-\s*(?P<page>\d+)\s*-$")
    for idx in range(start + 1, end):
        text = text_of(paragraphs[idx]).strip()
        if not text:
            continue
        match = pattern.match(text)
        if not match:
            skipped.append({"index": idx, "text": text})
            continue
        title = normalize_entry_title(match.group("title"))
        page = match.group("page")
        level = entry_level(title)
        rebuild_entry(paragraphs[idx], title, page, level)
        fixed.append({"index": idx, "title": title, "page": page, "level": level})
    return {
        "toc_start": start,
        "toc_end": end,
        "fixed_entry_count": len(fixed),
        "fixed_entries": fixed,
        "skipped": skipped,
    }


def audit_toc(root: etree._Element) -> dict:
    paragraphs = body_paragraphs(root)
    start, end = find_toc_bounds(paragraphs)
    entries = []
    bad_hyphen_pages = []
    for idx in range(start + 1, end):
        text = text_of(paragraphs[idx]).strip()
        if not text:
            continue
        entries.append(text)
        if re.search(r"-\s*\d+\s*-", text):
            bad_hyphen_pages.append({"index": idx, "text": text})
    return {
        "toc_title": text_of(paragraphs[start]),
        "toc_entry_count": len(entries),
        "bad_hyphen_page_entries": bad_hyphen_pages,
        "toc_entries_preview": entries[:8],
        "toc_entries_tail": entries[-5:],
    }


def write_docx(input_docx: Path, output_docx: Path, document_xml: bytes) -> None:
    output_docx.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp_path = Path(tmp.name)
    try:
        with ZipFile(input_docx, "r") as zin, ZipFile(tmp_path, "w", ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "word/document.xml":
                    zout.writestr(item, document_xml)
                else:
                    zout.writestr(item, zin.read(item.filename))
        shutil.move(str(tmp_path), output_docx)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_docx", type=Path)
    parser.add_argument("output_docx", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    with ZipFile(args.input_docx, "r") as z:
        root = etree.fromstring(z.read("word/document.xml"))

    report = fix_toc(root)
    report["audit"] = audit_toc(root)
    xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone="yes")
    write_docx(args.input_docx, args.output_docx, xml)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
