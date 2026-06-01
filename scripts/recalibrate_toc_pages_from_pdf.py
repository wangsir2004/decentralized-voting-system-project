from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W = NS["w"]


def qn(name: str) -> str:
    prefix, local = name.split(":")
    if prefix != "w":
        raise ValueError(name)
    return f"{{{W}}}{local}"


def text_of(p: etree._Element) -> str:
    return "".join(t.text or "" for t in p.xpath(".//w:t", namespaces=NS))


def normalize(text: str) -> str:
    text = re.sub(r"\s+", "", text)
    text = text.replace("　", "")
    return text


def body_paragraphs(root: etree._Element) -> list[etree._Element]:
    body = root.find("w:body", namespaces=NS)
    if body is None:
        raise ValueError("document.xml has no body")
    return [child for child in body if child.tag == qn("w:p")]


def find_toc_bounds(paragraphs: list[etree._Element]) -> tuple[int, int]:
    start = next((i for i, p in enumerate(paragraphs) if normalize(text_of(p)) == "目录"), -1)
    if start < 0:
        raise ValueError("TOC title not found")
    for i in range(start + 1, len(paragraphs)):
        if normalize(text_of(paragraphs[i])) == "第一章绪论":
            return start, i
    raise ValueError("TOC end not found")


def extract_pdf_pages(pdf: Path, pdftotext: str) -> list[str]:
    info = subprocess.run(
        ["pdfinfo", str(pdf)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        check=True,
    )
    match = re.search(r"^Pages:\s+(\d+)", info.stdout, re.M)
    if not match:
        raise RuntimeError("Could not determine PDF page count")
    pages = []
    for page in range(1, int(match.group(1)) + 1):
        result = subprocess.run(
            [pdftotext, "-f", str(page), "-l", str(page), "-layout", str(pdf), "-"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=True,
        )
        pages.append(result.stdout)
    return pages


def visible_footer_number(page_text: str, fallback: int) -> int:
    for line in reversed([line.strip() for line in page_text.splitlines()]):
        if re.fullmatch(r"\d{1,3}", line):
            return int(line)
    return fallback


def parse_toc_entry(p: etree._Element) -> tuple[str, str, etree._Element] | None:
    hyperlink = p.find("w:hyperlink", namespaces=NS)
    container = hyperlink if hyperlink is not None else p
    texts = container.xpath(".//w:t", namespaces=NS)
    if len(texts) < 2:
        return None
    title = texts[0].text or ""
    page = texts[-1].text or ""
    if not page.isdigit():
        return None
    return title, page, texts[-1]


def recalibrate(docx: Path, pdf: Path, out: Path, report_path: Path, min_pdf_page: int, pdftotext: str) -> dict:
    pages = extract_pdf_pages(pdf, pdftotext)
    page_norm = [normalize(page) for page in pages]
    footers = [visible_footer_number(page, i + 1) for i, page in enumerate(pages)]

    with ZipFile(docx, "r") as z:
        root = etree.fromstring(z.read("word/document.xml"))

    paragraphs = body_paragraphs(root)
    start, end = find_toc_bounds(paragraphs)
    updates = []
    missing = []
    for idx in range(start + 1, end):
        parsed = parse_toc_entry(paragraphs[idx])
        if not parsed:
            continue
        title, old_page, page_node = parsed
        needle = normalize(title)
        actual = None
        actual_pdf_page = None
        for pdf_index in range(max(min_pdf_page - 1, 0), len(page_norm)):
            if needle and needle in page_norm[pdf_index]:
                actual = footers[pdf_index]
                actual_pdf_page = pdf_index + 1
                break
        if actual is None:
            missing.append({"index": idx, "title": title, "old": old_page})
            continue
        page_node.text = str(actual)
        updates.append(
            {
                "index": idx,
                "title": title,
                "old": int(old_page),
                "new": int(actual),
                "pdf_page": actual_pdf_page,
            }
        )

    xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone="yes")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp_path = Path(tmp.name)
    try:
        with ZipFile(docx, "r") as zin, ZipFile(tmp_path, "w", ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "word/document.xml":
                    zout.writestr(item, xml)
                else:
                    zout.writestr(item, zin.read(item.filename))
        shutil.move(str(tmp_path), out)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    report = {
        "toc_start": start,
        "toc_end": end,
        "pdf_page_count": len(pages),
        "updated": len(updates),
        "updates": updates,
        "missing": missing,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--min-pdf-page", type=int, default=9)
    parser.add_argument("--pdftotext", default="pdftotext")
    args = parser.parse_args()
    report = recalibrate(args.docx, args.pdf, args.out, args.report, args.min_pdf_page, args.pdftotext)
    print(json.dumps({"updated": report["updated"], "missing": report["missing"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
