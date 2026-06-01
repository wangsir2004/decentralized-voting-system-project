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


def qn(local: str) -> str:
    prefix, name = local.split(":")
    if prefix != "w":
        raise ValueError(local)
    return f"{{{W}}}{name}"


def normalize(text: str) -> str:
    return " ".join(text.split())


def paragraph_text(p: etree._Element) -> str:
    return "".join(t.text or "" for t in p.xpath(".//w:t", namespaces=NS))


def direct_body_paragraphs(root: etree._Element) -> list[etree._Element]:
    body = root.find("w:body", namespaces=NS)
    if body is None:
        raise ValueError("word/document.xml has no body")
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


def remove_children(parent: etree._Element, child_names: set[str]) -> None:
    wanted = {qn(name) for name in child_names}
    for child in list(parent):
        if child.tag in wanted:
            parent.remove(child)


def set_paragraph_format(p: etree._Element) -> None:
    p_pr = get_or_add(p, "w:pPr", first=True)
    remove_children(p_pr, {"w:jc", "w:ind", "w:spacing", "w:numPr"})

    jc = etree.Element(qn("w:jc"))
    jc.set(qn("w:val"), "left")
    p_pr.append(jc)

    ind = etree.Element(qn("w:ind"))
    # Matches the provided sample: number starts at the left edge, wrapped
    # lines hang by about 2.5 Chinese characters.
    ind.set(qn("w:left"), "525")
    ind.set(qn("w:hanging"), "525")
    ind.set(qn("w:hangingChars"), "250")
    p_pr.append(ind)

    spacing = etree.Element(qn("w:spacing"))
    spacing.set(qn("w:before"), "0")
    spacing.set(qn("w:after"), "0")
    spacing.set(qn("w:line"), "300")
    spacing.set(qn("w:lineRule"), "auto")
    p_pr.append(spacing)


def set_run_format(
    r: etree._Element,
    *,
    superscript: bool | None = None,
    hyperlink: bool = False,
    size_half_points: str = "21",
) -> None:
    r_pr = get_or_add(r, "w:rPr", first=True)
    remove_children(
        r_pr,
        {
            "w:rFonts",
            "w:sz",
            "w:szCs",
            "w:color",
            "w:u",
            "w:vertAlign",
            "w:rStyle",
            "w:highlight",
        },
    )

    fonts = etree.Element(qn("w:rFonts"))
    fonts.set(qn("w:eastAsia"), "宋体")
    fonts.set(qn("w:ascii"), "Times New Roman")
    fonts.set(qn("w:hAnsi"), "Times New Roman")
    fonts.set(qn("w:cs"), "Times New Roman")
    r_pr.append(fonts)

    size = etree.Element(qn("w:sz"))
    size.set(qn("w:val"), size_half_points)
    r_pr.append(size)
    size_cs = etree.Element(qn("w:szCs"))
    size_cs.set(qn("w:val"), size_half_points)
    r_pr.append(size_cs)

    color = etree.Element(qn("w:color"))
    color.set(qn("w:val"), "000000")
    r_pr.append(color)

    if hyperlink:
        underline = etree.Element(qn("w:u"))
        underline.set(qn("w:val"), "none")
        r_pr.append(underline)

    if superscript:
        va = etree.Element(qn("w:vertAlign"))
        va.set(qn("w:val"), "superscript")
        r_pr.append(va)


def normalize_reference_text(p: etree._Element) -> bool:
    text_nodes = p.xpath(".//w:t", namespaces=NS)
    if not text_nodes:
        return False
    original = paragraph_text(p)
    text = original.strip()
    text = re.sub(r"^\[(\d+)]\s*", r"[\1] ", text)
    if text and not text.endswith((".", "。")):
        text += "."
    if text == original:
        return False

    for t in text_nodes:
        t.text = ""
    text_nodes[0].text = text
    # Preserve spaces after the reference number in Word XML.
    text_nodes[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return True


def ensure_reference_bookmarks(root: etree._Element, refs: list[tuple[int, etree._Element]]) -> int:
    existing = {
        b.get(qn("w:name"))
        for b in root.xpath(".//w:bookmarkStart", namespaces=NS)
        if b.get(qn("w:name"))
    }
    max_id = 0
    for b in root.xpath(".//w:bookmarkStart|.//w:bookmarkEnd", namespaces=NS):
        raw = b.get(qn("w:id"))
        if raw and raw.isdigit():
            max_id = max(max_id, int(raw))

    added = 0
    next_id = max_id + 1
    for number, p in refs:
        name = f"ref_{number}"
        if name in existing:
            continue
        start = etree.Element(qn("w:bookmarkStart"))
        start.set(qn("w:id"), str(next_id))
        start.set(qn("w:name"), name)
        end = etree.Element(qn("w:bookmarkEnd"))
        end.set(qn("w:id"), str(next_id))

        insert_at = 1 if p.find("w:pPr", namespaces=NS) is not None else 0
        p.insert(insert_at, start)
        p.append(end)
        existing.add(name)
        added += 1
        next_id += 1
    return added


def format_reference_section(root: etree._Element) -> dict:
    paragraphs = direct_body_paragraphs(root)
    texts = [normalize(paragraph_text(p)) for p in paragraphs]
    ref_idx = next((i for i, text in enumerate(texts) if text == "参考文献"), -1)
    if ref_idx < 0:
        raise ValueError("Reference heading not found")
    end_idx = next((i for i, text in enumerate(texts) if i > ref_idx and text.startswith("附录")), len(paragraphs))

    refs: list[tuple[int, etree._Element]] = []
    text_changes = 0
    for p in paragraphs[ref_idx + 1 : end_idx]:
        match = re.match(r"^\[(\d+)]", normalize(paragraph_text(p)))
        if not match:
            continue
        refs.append((int(match.group(1)), p))
        set_paragraph_format(p)
        if normalize_reference_text(p):
            text_changes += 1
        for r in p.xpath(".//w:r", namespaces=NS):
            set_run_format(r)

    added_bookmarks = ensure_reference_bookmarks(root, refs)
    return {
        "reference_heading_index": ref_idx,
        "reference_end_index": end_idx,
        "reference_count": len(refs),
        "reference_numbers": [n for n, _ in refs],
        "reference_text_changes": text_changes,
        "added_reference_bookmarks": added_bookmarks,
    }


def format_citation_hyperlinks(root: etree._Element) -> dict:
    count = 0
    anchors: list[str] = []
    for hyperlink in root.xpath(".//w:hyperlink[@w:anchor]", namespaces=NS):
        anchor = hyperlink.get(qn("w:anchor"))
        if not anchor or not re.fullmatch(r"ref_\d+", anchor):
            continue
        ref_no = anchor.split("_", 1)[1]
        hyperlink.set(qn("w:history"), "1")
        hyperlink.set(qn("w:tooltip"), f"跳转到参考文献[{ref_no}]")
        anchors.append(anchor)
        for r in hyperlink.xpath(".//w:r", namespaces=NS):
            # Body citations follow the thesis body citation style: square
            # brackets in superscript, using the body-size 12 pt text.
            set_run_format(r, superscript=True, hyperlink=True, size_half_points="24")
        count += 1
    return {
        "citation_hyperlink_count": count,
        "citation_hyperlink_targets": sorted(set(anchors), key=lambda x: int(x.split("_")[1])),
    }


def collect_bookmarks(root: etree._Element) -> set[str]:
    return {
        b.get(qn("w:name"))
        for b in root.xpath(".//w:bookmarkStart", namespaces=NS)
        if b.get(qn("w:name"))
    }


def audit(root: etree._Element, reference_numbers: list[int]) -> dict:
    bookmarks = collect_bookmarks(root)
    missing_targets = []
    for hyperlink in root.xpath(".//w:hyperlink[@w:anchor]", namespaces=NS):
        anchor = hyperlink.get(qn("w:anchor"))
        if anchor and anchor.startswith("ref_") and anchor not in bookmarks:
            missing_targets.append(anchor)

    paragraphs = direct_body_paragraphs(root)
    ref_idx = next((i for i, p in enumerate(paragraphs) if normalize(paragraph_text(p)) == "参考文献"), -1)
    end_idx = next(
        (i for i, p in enumerate(paragraphs) if i > ref_idx and normalize(paragraph_text(p)).startswith("附录")),
        len(paragraphs),
    )
    format_issues = []
    for p in paragraphs[ref_idx + 1 : end_idx]:
        text = normalize(paragraph_text(p))
        if not re.match(r"^\[(\d+)]", text):
            continue
        p_pr = p.find("w:pPr", namespaces=NS)
        ind = p_pr.find("w:ind", namespaces=NS) if p_pr is not None else None
        spacing = p_pr.find("w:spacing", namespaces=NS) if p_pr is not None else None
        jc = p_pr.find("w:jc", namespaces=NS) if p_pr is not None else None
        if jc is None or jc.get(qn("w:val")) != "left":
            format_issues.append(f"{text[:16]}: jc")
        if ind is None or ind.get(qn("w:left")) != "525" or ind.get(qn("w:hanging")) != "525":
            format_issues.append(f"{text[:16]}: ind")
        if (
            spacing is None
            or spacing.get(qn("w:before")) != "0"
            or spacing.get(qn("w:after")) != "0"
            or spacing.get(qn("w:line")) != "300"
        ):
            format_issues.append(f"{text[:16]}: spacing")

    return {
        "missing_hyperlink_targets": sorted(set(missing_targets)),
        "reference_bookmark_count": sum(1 for n in reference_numbers if f"ref_{n}" in bookmarks),
        "reference_format_issues": format_issues,
    }


def write_docx_with_document_xml(input_docx: Path, output_docx: Path, document_xml: bytes) -> None:
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

    ref_report = format_reference_section(root)
    citation_report = format_citation_hyperlinks(root)
    audit_report = audit(root, ref_report["reference_numbers"])
    report = {
        **ref_report,
        **citation_report,
        **audit_report,
    }

    document_xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone="yes")
    write_docx_with_document_xml(args.input_docx, args.output_docx, document_xml)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
