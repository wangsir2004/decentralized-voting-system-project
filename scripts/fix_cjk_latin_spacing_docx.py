from __future__ import annotations

import os
import re
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
ET.register_namespace("w", NS["w"])

# Chinese characters, full-width punctuation, and CJK punctuation.
CJK_RE = r"[\u3000-\u303f\u3400-\u9fff\uf900-\ufaff\uff00-\uffef]"
LATIN_RE = r"[A-Za-z]"


def is_cjk_like(ch: str) -> bool:
    return bool(re.match(CJK_RE + r"$", ch))


def is_latin_like(ch: str) -> bool:
    return bool(re.match(LATIN_RE + r"$", ch))


def is_boundary_pair(left: str | None, right: str | None) -> bool:
    if not left or not right:
        return False
    return (is_cjk_like(left) and is_latin_like(right)) or (
        is_latin_like(left) and is_cjk_like(right)
    )


def first_non_space(text: str) -> str | None:
    for ch in text:
        if ch not in (" ", "\u00a0"):
            return ch
    return None


def last_non_space(text: str) -> str | None:
    for ch in reversed(text):
        if ch not in (" ", "\u00a0"):
            return ch
    return None


def prev_non_space(texts: list[str], idx: int) -> str | None:
    for j in range(idx - 1, -1, -1):
        ch = last_non_space(texts[j])
        if ch:
            return ch
    return None


def next_non_space(texts: list[str], idx: int) -> str | None:
    for j in range(idx + 1, len(texts)):
        ch = first_non_space(texts[j])
        if ch:
            return ch
    return None


def fix_in_node(text: str) -> str:
    text = re.sub(f"(?<={CJK_RE})[ \u00a0]+(?={LATIN_RE})", "", text)
    text = re.sub(f"(?<={LATIN_RE})[ \u00a0]+(?={CJK_RE})", "", text)
    return text


def disable_auto_spacing(p_pr: ET.Element) -> bool:
    # Word/WPS can visually add East Asian/Latin spacing even without literal spaces.
    changed = False
    for tag in ("autoSpaceDE", "autoSpaceDN"):
        el = p_pr.find(f"w:{tag}", NS)
        if el is None:
            el = ET.Element(f"{{{NS['w']}}}{tag}")
            p_pr.append(el)
            changed = True
        val_attr = f"{{{NS['w']}}}val"
        if el.get(val_attr) != "0":
            el.set(val_attr, "0")
            changed = True
    return changed


def fix_paragraph(paragraph: ET.Element) -> tuple[int, int, int]:
    nodes = paragraph.findall(".//w:t", NS)
    changed_nodes = 0
    removed_spaces = 0

    # Handle CJK/Latin boundaries that occur inside a single text node.
    for node in nodes:
        old = node.text or ""
        new = fix_in_node(old)
        if new != old:
            node.text = new
            changed_nodes += 1
            removed_spaces += len(old) - len(new)

    texts = [node.text or "" for node in nodes]

    # Handle boundaries split across runs, e.g. "Solidity" + " 合约".
    for i, node in enumerate(nodes):
        text = texts[i]
        if not text:
            continue

        old = text
        if set(text) <= {" ", "\u00a0"}:
            left = prev_non_space(texts, i)
            right = next_non_space(texts, i)
            if is_boundary_pair(left, right):
                text = ""
        else:
            leading = len(text) - len(text.lstrip(" \u00a0"))
            if leading:
                left = prev_non_space(texts, i)
                right = first_non_space(text[leading:]) or next_non_space(texts, i)
                if is_boundary_pair(left, right):
                    text = text[leading:]

            trailing = len(text) - len(text.rstrip(" \u00a0"))
            if trailing:
                left = last_non_space(text[:-trailing]) or prev_non_space(texts, i)
                right = next_non_space(texts, i)
                if is_boundary_pair(left, right):
                    text = text[:-trailing]

        if text != old:
            node.text = text
            texts[i] = text
            changed_nodes += 1
            removed_spaces += len(old) - len(text)

    p_pr = paragraph.find("w:pPr", NS)
    if p_pr is None:
        p_pr = ET.Element(f"{{{NS['w']}}}pPr")
        paragraph.insert(0, p_pr)
    auto_changed = int(disable_auto_spacing(p_pr))

    return changed_nodes, removed_spaces, auto_changed


def process_xml_file(path: Path) -> tuple[int, int, int]:
    tree = ET.parse(path)
    root = tree.getroot()
    changed_nodes = 0
    removed_spaces = 0
    auto_changed = 0

    for paragraph in root.findall(".//w:p", NS):
        changed, removed, auto = fix_paragraph(paragraph)
        changed_nodes += changed
        removed_spaces += removed
        auto_changed += auto

    # Disable inherited Chinese typography spacing in styles and numbering too.
    style_p_prs = root.findall(".//w:style/w:pPr", NS)
    numbering_p_prs = root.findall(".//w:lvl/w:pPr", NS)
    for p_pr in style_p_prs + numbering_p_prs:
        auto_changed += int(disable_auto_spacing(p_pr))

    if changed_nodes or auto_changed:
        tree.write(path, encoding="utf-8", xml_declaration=True)

    return changed_nodes, removed_spaces, auto_changed


def main() -> None:
    src = Path(os.environ["DOCX_SRC"])
    out = Path(os.environ["DOCX_OUT"])
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        with zipfile.ZipFile(src, "r") as zin:
            zin.extractall(tmp)

        total_changed = 0
        total_removed = 0
        total_auto = 0
        xml_paths = [
            tmp / "word" / "document.xml",
            tmp / "word" / "styles.xml",
            tmp / "word" / "numbering.xml",
            *sorted((tmp / "word").glob("header*.xml")),
            *sorted((tmp / "word").glob("footer*.xml")),
            *sorted((tmp / "word").glob("footnotes.xml")),
            *sorted((tmp / "word").glob("endnotes.xml")),
        ]
        for xml_path in xml_paths:
            if not xml_path.exists():
                continue
            changed, removed, auto = process_xml_file(xml_path)
            total_changed += changed
            total_removed += removed
            total_auto += auto

        with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for file_path in tmp.rglob("*"):
                if file_path.is_file():
                    zout.write(file_path, file_path.relative_to(tmp).as_posix())

    print(f"output={out}")
    print(f"changed_text_nodes={total_changed}")
    print(f"removed_spaces={total_removed}")
    print(f"disabled_auto_spacing_blocks={total_auto}")


if __name__ == "__main__":
    main()
