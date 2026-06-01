from __future__ import annotations

import argparse
import copy
import json
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
    return "".join(text.split()).replace("　", "")


def body(root: etree._Element) -> etree._Element:
    body_el = root.find("w:body", namespaces=NS)
    if body_el is None:
        raise ValueError("document.xml has no w:body")
    return body_el


def body_paragraphs(root: etree._Element) -> list[etree._Element]:
    return [child for child in body(root) if child.tag == qn("w:p")]


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


def set_pg_num_type(sect: etree._Element, *, fmt: str, start: str | None) -> None:
    remove_children(sect, {"w:pgNumType"})
    pg = etree.Element(qn("w:pgNumType"))
    pg.set(qn("w:fmt"), fmt)
    if start is not None:
        pg.set(qn("w:start"), start)
    # Put after footer/header references and before page geometry when possible.
    insert_at = 0
    for i, child in enumerate(list(sect)):
        if child.tag in {qn("w:headerReference"), qn("w:footerReference"), qn("w:type")}:
            insert_at = i + 1
    sect.insert(insert_at, pg)


def footer_xml(jc: str, sample_text: str = "1") -> bytes:
    ftr = etree.Element(qn("w:ftr"), nsmap={"w": W})
    p = etree.SubElement(ftr, qn("w:p"))
    p_pr = etree.SubElement(p, qn("w:pPr"))
    jc_el = etree.SubElement(p_pr, qn("w:jc"))
    jc_el.set(qn("w:val"), jc)

    fld = etree.SubElement(p, qn("w:fldSimple"))
    fld.set(qn("w:instr"), "PAGE   \\* MERGEFORMAT")
    r = etree.SubElement(fld, qn("w:r"))
    r_pr = etree.SubElement(r, qn("w:rPr"))
    fonts = etree.SubElement(r_pr, qn("w:rFonts"))
    fonts.set(qn("w:ascii"), "Times New Roman")
    fonts.set(qn("w:hAnsi"), "Times New Roman")
    fonts.set(qn("w:eastAsia"), "宋体")
    fonts.set(qn("w:cs"), "Times New Roman")
    for tag in ("w:sz", "w:szCs"):
        sz = etree.SubElement(r_pr, qn(tag))
        sz.set(qn("w:val"), "21")
    t = etree.SubElement(r, qn("w:t"))
    t.set(XML_SPACE, "preserve")
    t.text = sample_text
    return etree.tostring(ftr, xml_declaration=True, encoding="UTF-8", standalone="yes")


def set_footer_refs(sect: etree._Element, even_id: str, default_id: str) -> None:
    for child in list(sect):
        if child.tag == qn("w:footerReference"):
            sect.remove(child)
    insert_at = 0
    for i, child in enumerate(list(sect)):
        if child.tag == qn("w:headerReference"):
            insert_at = i + 1
    even = etree.Element(qn("w:footerReference"))
    even.set(qn("w:type"), "even")
    even.set("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id", even_id)
    default = etree.Element(qn("w:footerReference"))
    default.set(qn("w:type"), "default")
    default.set("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id", default_id)
    sect.insert(insert_at, even)
    sect.insert(insert_at + 1, default)


def fix_sections(root: etree._Element) -> dict:
    b = body(root)
    paragraphs = body_paragraphs(root)
    toc_start = next(i for i, p in enumerate(paragraphs) if normalize(text_of(p)) == "目录")
    body_start = next(i for i, p in enumerate(paragraphs) if normalize(text_of(p)) == "第一章绪论")
    toc_end_para = paragraphs[body_start - 1]
    body_sect = b.find("w:sectPr", namespaces=NS)
    if body_sect is None:
        raise ValueError("final body sectPr not found")

    # The current final section incorrectly contains both TOC and body. Clone it
    # onto the blank paragraph just before chapter 1, so TOC becomes its own
    # Roman-numbered section and the final body section can restart at 1.
    p_pr = get_or_add(toc_end_para, "w:pPr", first=True)
    old_para_sect = p_pr.find("w:sectPr", namespaces=NS)
    if old_para_sect is not None:
        p_pr.remove(old_para_sect)
    toc_sect = copy.deepcopy(body_sect)
    p_pr.append(toc_sect)

    # Reuse the existing body footer relationships, but replace those footer
    # parts with clean PAGE fields. Section pgNumType controls Roman/Arabic.
    even_id = "rId31"
    default_id = "rId32"
    set_footer_refs(toc_sect, even_id, default_id)
    set_pg_num_type(toc_sect, fmt="upperRoman", start=None)

    set_footer_refs(body_sect, even_id, default_id)
    set_pg_num_type(body_sect, fmt="decimal", start="1")

    return {
        "toc_start_para": toc_start,
        "body_start_para": body_start,
        "toc_section_break_para": body_start - 1,
        "toc_pgNumType": {"fmt": "upperRoman", "start": None},
        "body_pgNumType": {"fmt": "decimal", "start": "1"},
        "footer_relationships_reused": {"even": even_id, "default": default_id},
    }


def write_docx(input_docx: Path, output_docx: Path, replacements: dict[str, bytes]) -> None:
    output_docx.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp_path = Path(tmp.name)
    try:
        with ZipFile(input_docx, "r") as zin, ZipFile(tmp_path, "w", ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = replacements.get(item.filename)
                if data is None:
                    data = zin.read(item.filename)
                zout.writestr(item, data)
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
        document_root = etree.fromstring(z.read("word/document.xml"))

    report = fix_sections(document_root)
    replacements = {
        "word/document.xml": etree.tostring(
            document_root, xml_declaration=True, encoding="UTF-8", standalone="yes"
        ),
        # rId31 -> footer5.xml is the even-page footer; rId32 -> footer6.xml is default.
        "word/footer5.xml": footer_xml("left", "2"),
        "word/footer6.xml": footer_xml("right", "1"),
    }
    write_docx(args.input_docx, args.output_docx, replacements)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
