from __future__ import annotations

import os
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
XML = "http://www.w3.org/XML/1998/namespace"
NS = {"w": W, "m": M}

ET.register_namespace("w", W)
ET.register_namespace("m", M)


def qn(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(t.text or "" for t in paragraph.findall(".//w:t", NS) + paragraph.findall(".//m:t", NS)).strip()


def w_run_tab() -> ET.Element:
    run = ET.Element(qn(W, "r"))
    ET.SubElement(run, qn(W, "tab"))
    return run


def w_run_text(text: str) -> ET.Element:
    run = ET.Element(qn(W, "r"))
    r_pr = ET.SubElement(run, qn(W, "rPr"))
    sz = ET.SubElement(r_pr, qn(W, "sz"))
    sz.set(qn(W, "val"), "24")
    tab = ET.SubElement(run, qn(W, "tab"))
    tab.tail = None
    t = ET.SubElement(run, qn(W, "t"))
    t.text = text
    return run


def math_run(text: str) -> ET.Element:
    run = ET.Element(qn(M, "r"))
    r_pr = ET.SubElement(run, qn(W, "rPr"))
    fonts = ET.SubElement(r_pr, qn(W, "rFonts"))
    fonts.set(qn(W, "ascii"), "Cambria Math")
    fonts.set(qn(W, "hAnsi"), "Cambria Math")
    fonts.set(qn(W, "cs"), "Cambria Math")
    ET.SubElement(r_pr, qn(W, "noProof"))
    sz = ET.SubElement(r_pr, qn(W, "sz"))
    sz.set(qn(W, "val"), "24")
    t = ET.SubElement(run, qn(M, "t"))
    if text.startswith(" ") or text.endswith(" "):
        t.set(qn(XML, "space"), "preserve")
    t.text = text
    return run


def ssup(base: str, sup_text: str) -> ET.Element:
    node = ET.Element(qn(M, "sSup"))
    e = ET.SubElement(node, qn(M, "e"))
    e.append(math_run(base))
    sup = ET.SubElement(node, qn(M, "sup"))
    sup.append(math_run(sup_text))
    return node


def frac(num_parts: list[ET.Element], den_parts: list[ET.Element]) -> ET.Element:
    node = ET.Element(qn(M, "f"))
    f_pr = ET.SubElement(node, qn(M, "fPr"))
    f_type = ET.SubElement(f_pr, qn(M, "type"))
    f_type.set(qn(M, "val"), "bar")
    num = ET.SubElement(node, qn(M, "num"))
    for part in num_parts:
        num.append(part)
    den = ET.SubElement(node, qn(M, "den"))
    for part in den_parts:
        den.append(part)
    return node


def product(term_parts: list[ET.Element]) -> ET.Element:
    node = ET.Element(qn(M, "nary"))
    nary_pr = ET.SubElement(node, qn(M, "naryPr"))
    chr_node = ET.SubElement(nary_pr, qn(M, "chr"))
    chr_node.set(qn(M, "val"), "∏")
    lim_loc = ET.SubElement(nary_pr, qn(M, "limLoc"))
    lim_loc.set(qn(M, "val"), "undOvr")
    grow = ET.SubElement(nary_pr, qn(M, "grow"))
    grow.set(qn(M, "val"), "1")
    sub = ET.SubElement(node, qn(M, "sub"))
    sub.append(math_run("i=0"))
    sup = ET.SubElement(node, qn(M, "sup"))
    sup.append(math_run("k-1"))
    e = ET.SubElement(node, qn(M, "e"))
    for part in term_parts:
        e.append(part)
    return node


def formula_27() -> list[ET.Element]:
    return [math_run("N = "), ssup("2", "256")]


def product_term() -> list[ET.Element]:
    return [
        math_run("(1 - "),
        frac([math_run("i")], [ssup("2", "256")]),
        math_run(")"),
    ]


def formula_28() -> list[ET.Element]:
    return [math_run("P(no collision) = "), product(product_term())]


def formula_29() -> list[ET.Element]:
    return [math_run("P(collision) = 1 - "), product(product_term())]


def formula_210() -> list[ET.Element]:
    return [
        math_run("k ≪ "),
        ssup("2", "128"),
        math_run(", P(collision) ≈ "),
        frac([math_run("k(k - 1)")], [ssup("2", "257")]),
    ]


FORMULAS = {
    "(2.7)": formula_27,
    "(2.8)": formula_28,
    "(2.9)": formula_29,
    "(2.10)": formula_210,
}


def replace_with_formula(paragraph: ET.Element, number: str, parts: list[ET.Element]) -> None:
    p_pr = paragraph.find("w:pPr", NS)
    for child in list(paragraph):
        if child is not p_pr:
            paragraph.remove(child)
    if p_pr is None:
        p_pr = ET.Element(qn(W, "pPr"))
        paragraph.insert(0, p_pr)

    paragraph.append(w_run_tab())
    math = ET.Element(qn(M, "oMath"))
    for part in parts:
        math.append(part)
    paragraph.append(math)
    paragraph.append(w_run_text(number))


def main() -> None:
    src = Path(os.environ["DOCX_SRC"])
    out = Path(os.environ["DOCX_OUT"])
    out.parent.mkdir(parents=True, exist_ok=True)

    changed: list[str] = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        with zipfile.ZipFile(src, "r") as zin:
            zin.extractall(tmp)

        document_xml = tmp / "word" / "document.xml"
        tree = ET.parse(document_xml)
        root = tree.getroot()

        for paragraph in root.findall(".//w:p", NS):
            text = paragraph_text(paragraph)
            for number, builder in FORMULAS.items():
                if text.endswith(number):
                    replace_with_formula(paragraph, number, builder())
                    changed.append(number)
                    break

        tree.write(document_xml, encoding="utf-8", xml_declaration=True)

        with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for file_path in tmp.rglob("*"):
                if file_path.is_file():
                    zout.write(file_path, file_path.relative_to(tmp).as_posix())

    print(f"output={out}")
    print("changed=" + ",".join(changed))


if __name__ == "__main__":
    main()
