from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
DESKTOP = Path.home() / "Desktop"
TEMPLATE = DESKTOP / "毕业设计" / "4.毕业设计说明书格式新的模板.docx"
OUT_DOCX = ROOT / "deliverables" / "graduation" / "docx" / "王靖宇-毕业设计说明书-去中心化电子投票系统.docx"
FIG = ROOT / "deliverables" / "graduation" / "figures"
SHOT = ROOT / "deliverables" / "graduation" / "screenshots"

TITLE = "基于 Solidity 智能合约与 Ethereum 测试网的去中心化电子投票系统设计与实现"
AUTHOR = "王靖宇"
STUDENT_ID = "225288"
COLLEGE = "人工智能与数据科学学院"
MAJOR = "计算机科学与技术"
CLASS_NAME = "计算机224"
ADVISOR = "王立鹏"
ADVISOR_TITLE = "讲师"
REVIEWER = "闫文杰"
REVIEWER_TITLE = "副教授"


def set_run_font(run, east_asia: str = "宋体", ascii_font: str = "Times New Roman", size: int | None = 10.5, bold: bool = False):
    run.font.name = ascii_font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), east_asia)
    if size is not None:
        run.font.size = Pt(size)
    run.bold = bold


def set_paragraph_format(paragraph, first_line: bool = True):
    paragraph.paragraph_format.line_spacing = 1.25
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(0)
    if first_line:
        paragraph.paragraph_format.first_line_indent = Pt(21)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def clear_document(doc: Document) -> None:
    body = doc._body._element
    for child in list(body):
        if child.tag.endswith("sectPr"):
            continue
        body.remove(child)


def setup_document(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.6)
    section.bottom_margin = Cm(2.4)
    section.left_margin = Cm(2.8)
    section.right_margin = Cm(2.6)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    normal.font.size = Pt(10.5)

    for style_name in ["Heading 1", "Heading 2", "Heading 3"]:
        style = styles[style_name]
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体" if style_name != "Heading 3" else "宋体")
        style.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        style.font.bold = style_name != "Heading 3"

    styles["Heading 1"].font.size = Pt(18)
    styles["Heading 2"].font.size = Pt(16)
    styles["Heading 3"].font.size = Pt(12)


def add_center(doc: Document, text: str, size: int = 10.5, bold: bool = False, font_name: str = "宋体"):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.25
    run = p.add_run(text)
    set_run_font(run, east_asia=font_name, size=size, bold=bold)
    return p


def add_para(doc: Document, text: str, *, first_line: bool = True, bold_prefix: str | None = None):
    p = doc.add_paragraph()
    set_paragraph_format(p, first_line=first_line)
    if bold_prefix and text.startswith(bold_prefix):
        run1 = p.add_run(bold_prefix)
        set_run_font(run1, bold=True)
        run2 = p.add_run(text[len(bold_prefix):])
        set_run_font(run2)
    else:
        run = p.add_run(text)
        set_run_font(run)
    return p


def add_mono(doc: Document, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.left_indent = Pt(21)
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    for line in text.splitlines():
        run = p.add_run(line)
        set_run_font(run, east_asia="Consolas", ascii_font="Consolas", size=9.5)
        run.add_break()
    return p


def add_chapter(doc: Document, text: str):
    if len(doc.paragraphs) > 0:
        doc.add_page_break()
    p = doc.add_heading(text, level=1)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(12)
    for run in p.runs:
        set_run_font(run, east_asia="黑体", size=18, bold=True)
    return p


def add_section_heading(doc: Document, text: str, level: int = 2):
    p = doc.add_heading(text, level=level)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(12 if level == 2 else 6)
    p.paragraph_format.space_after = Pt(6)
    for run in p.runs:
        set_run_font(run, east_asia="黑体" if level == 2 else "宋体", size=16 if level == 2 else 12, bold=True)
    return p


def add_caption(doc: Document, text: str):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    set_run_font(run, size=9)
    return p


def set_cell(cell, text: str, bold: bool = False, align: WD_ALIGN_PARAGRAPH = WD_ALIGN_PARAGRAPH.CENTER):
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    set_run_font(run, size=9.5, bold=bold)


def set_table_borders(table):
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = f"w:{edge}"
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "6")
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), "9AA6B2")


def add_table(doc: Document, headers: list[str], rows: list[list[str]], widths: list[float] | None = None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    set_table_borders(table)
    for i, header in enumerate(headers):
        set_cell(table.rows[0].cells[i], header, bold=True)
        shade = OxmlElement("w:shd")
        shade.set(qn("w:fill"), "E8EEF2")
        table.rows[0].cells[i]._tc.get_or_add_tcPr().append(shade)
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            align = WD_ALIGN_PARAGRAPH.LEFT if len(value) > 18 else WD_ALIGN_PARAGRAPH.CENTER
            set_cell(cells[i], value, align=align)
    if widths:
        for row in table.rows:
            for idx, width in enumerate(widths):
                row.cells[idx].width = Inches(width)
    doc.add_paragraph()
    return table


def add_picture(doc: Document, image_path: Path, caption: str, width: float = 5.8):
    if not image_path.exists():
        add_para(doc, f"（图片缺失：{image_path.name}）")
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(image_path), width=Inches(width))
    add_caption(doc, caption)


def add_cover(doc: Document):
    for _ in range(3):
        doc.add_paragraph()
    add_center(doc, "毕业设计说明书", size=28, bold=True, font_name="黑体")
    doc.add_paragraph()
    add_center(doc, f"题       目：{TITLE}", size=14, font_name="楷体")
    add_center(doc, f"学       院：{COLLEGE}", size=14, font_name="楷体")
    add_center(doc, f"专       业：{MAJOR}", size=14, font_name="楷体")
    add_center(doc, f"作       者：{AUTHOR}  学号 {STUDENT_ID}  {CLASS_NAME}", size=14, font_name="楷体")
    add_center(doc, f"指 导 教 师：{ADVISOR}  {ADVISOR_TITLE}", size=14, font_name="楷体")
    add_center(doc, f"评   阅  者：{REVIEWER}  {REVIEWER_TITLE}", size=14, font_name="楷体")
    for _ in range(7):
        doc.add_paragraph()
    add_center(doc, "二〇二六 年 六 月", size=12, font_name="楷体")
    doc.add_page_break()


def add_declarations(doc: Document):
    add_center(doc, "原创性声明", size=16, bold=True, font_name="宋体")
    add_para(doc, "本人郑重声明：所呈交的毕业设计说明书，是本人在导师指导下，进行研究工作所取得的成果。除文中已经注明引用的内容外，本设计不包含任何他人或集体已经发表的作品内容，也不包含本人为获得其他学位而使用过的材料。对本设计所涉及的研究工作做出贡献的其他个人或集体，均已在文中以明确方式标明。本毕业设计说明书原创性声明的法律责任由本人承担。")
    doc.add_paragraph()
    add_para(doc, "作者签名：                      日期：      年    月    日", first_line=False)
    doc.add_paragraph()
    add_center(doc, "关于毕业设计说明书版权使用授权的说明", size=16, bold=True, font_name="宋体")
    add_para(doc, "本人完全了解河北工业大学关于收集、保存、使用毕业设计说明书的以下规定：本科生在校攻读学位期间毕业设计工作的知识产权单位属河北工业大学，学校有权采用影印、缩印、扫描、数字化或其他手段保存毕业设计说明书；学校有权提供本设计全文或者部分内容的阅览服务；学校有权将毕业设计说明书的全部或部分内容编入有关数据库进行检索、交流；学校有权向国家有关部门或者机构送交毕业设计说明书的复印件和电子版。")
    add_para(doc, "（保密的毕业设计说明书在解密后适用本授权说明）")
    doc.add_paragraph()
    add_para(doc, "作  者  签  名：                 日期：      年    月    日", first_line=False)
    add_para(doc, "导  师  签  名：                 日期：      年    月    日", first_line=False)
    doc.add_page_break()


def add_abstracts(doc: Document):
    add_center(doc, "摘　　要", size=18, bold=True, font_name="黑体")
    add_para(doc, "随着在线治理、数字化协同和远程办公场景不断扩展，电子投票系统需要在可用性、透明性、结果可复核和安全性之间取得平衡。传统中心化电子投票系统通常由单一服务端保存选民状态和计票结果，容易面临单点故障、内部人为干预、过程追溯困难和结果公信力不足等问题。针对上述问题，本文设计并实现了一种基于 Solidity 智能合约与 Ethereum Sepolia 测试网的去中心化电子投票系统。系统以 VotingSystem 智能合约承载投票主题、候选项、投票时间、白名单资格校验、防重复投票和链上计票等核心逻辑；采用 Merkle Tree 保存白名单根以降低链上存储成本；使用 React、Vite、TypeScript、Ethers.js 和 MetaMask 构建前端 DApp，实现钱包连接、资格证明读取、投票提交、交易回执展示和实时结果查询。")
    add_para(doc, "本文完成了需求分析、系统设计、合约实现、前端开发、自动化测试、Gas 消耗分析、安全审计和 Sepolia 测试网部署。测试结果显示，系统自动化测试共 24 个用例全部通过；本地部署 Gas 为 767,754，vote 方法平均 Gas 为 73,661；最新 Sepolia 部署合约地址为 0x6772e0193eAAA77cB89d135188f09e339C4dE66A，并完成了一笔真实投票交易。Slither 审计结果仅提示与投票截止时间相关的 timestamp 风险，该风险属于可解释的业务边界。实践结果表明，系统能够实现地址级资格控制、链上公开计票和结果可追溯，为小规模电子投票场景提供了一种可运行、可验证的实现方案。")
    add_para(doc, "关键词：去中心化投票；智能合约；Solidity；Merkle Tree；Ethereum；DApp", first_line=False, bold_prefix="关键词：")
    doc.add_page_break()

    add_center(doc, "ABSTRACT", size=18, bold=True, font_name="Times New Roman")
    add_para(doc, "With the expansion of online governance, digital collaboration and remote working scenarios, electronic voting systems need to balance usability, transparency, verifiability and security. Traditional centralized electronic voting systems usually store voter states and tallying results on a single server, which may lead to single point of failure, internal manipulation, weak process traceability and insufficient public trust. To address these problems, this thesis designs and implements a decentralized electronic voting system based on Solidity smart contracts and the Ethereum Sepolia test network. The VotingSystem smart contract is used to manage the voting title, candidates, voting period, whitelist verification, duplicate-vote prevention and on-chain tallying. A Merkle Tree whitelist is adopted so that only the Merkle root is stored on chain, reducing storage overhead. The front-end DApp is implemented with React, Vite, TypeScript, Ethers.js and MetaMask, supporting wallet connection, proof loading, vote submission, transaction receipt display and real-time result query.")
    add_para(doc, "The work covers requirement analysis, system design, smart contract implementation, front-end development, automated testing, gas consumption analysis, security auditing and deployment on Sepolia. The automated test suite contains 24 passed cases. The local deployment consumes 767,754 gas, while the average gas consumption of the vote method is 73,661. The latest deployed Sepolia contract address is 0x6772e0193eAAA77cB89d135188f09e339C4dE66A, and one real voting transaction has been submitted successfully. Slither reports only timestamp-related warnings for the voting deadline, which are treated as acceptable business constraints. The results show that the system can provide address-level eligibility control, transparent on-chain tallying and traceable voting evidence, offering an executable and verifiable prototype for small-scale electronic voting scenarios.")
    add_para(doc, "Key words: decentralized voting; smart contract; Solidity; Merkle Tree; Ethereum; DApp", first_line=False, bold_prefix="Key words:")
    doc.add_page_break()


def add_toc(doc: Document):
    add_center(doc, "目　　录", size=18, bold=True, font_name="黑体")
    toc_lines = [
        "第一章  绪论",
        "1.1  研究背景与意义",
        "1.2  国内外研究现状",
        "1.3  研究目标与主要内容",
        "1.4  论文结构安排",
        "第二章  相关技术基础",
        "2.1  Ethereum 与智能合约",
        "2.2  Solidity、Hardhat 与 OpenZeppelin",
        "2.3  ECDSA 签名与地址机制",
        "2.4  Keccak-256 与 Merkle Tree",
        "2.5  DApp 前端与钱包交互",
        "第三章  系统需求分析",
        "3.1  角色分析",
        "3.2  功能需求",
        "3.3  非功能需求",
        "3.4  威胁模型与设计边界",
        "第四章  系统总体设计",
        "4.1  总体架构设计",
        "4.2  业务流程设计",
        "4.3  投票交易流程设计",
        "4.4  合约状态与接口设计",
        "4.5  前端模块设计",
        "第五章  系统详细实现",
        "5.1  开发环境与工程结构",
        "5.2  智能合约实现",
        "5.3  白名单与 Merkle Proof 实现",
        "5.4  前端 DApp 实现",
        "5.5  部署与前端配置同步",
        "第六章  测试、安全审计与部署分析",
        "6.1  测试环境与测试策略",
        "6.2  自动化测试结果",
        "6.3  Gas 消耗分析",
        "6.4  安全审计与风险分析",
        "6.5  Sepolia 测试网部署结果",
        "第七章  总结与展望",
        "参考文献",
        "附录A  关键命令与运行证据",
        "致谢",
    ]
    for line in toc_lines:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.25
        p.paragraph_format.left_indent = Pt(21 if line[0].isdigit() else 0)
        run = p.add_run(line)
        set_run_font(run, east_asia="黑体" if line.startswith(("第一", "第二", "第三", "第四", "第五", "第六", "第七", "参考", "附录", "致谢")) else "宋体", size=10.5)


def add_body(doc: Document):
    add_chapter(doc, "第一章  绪论")
    add_section_heading(doc, "1.1  研究背景与意义")
    add_para(doc, "电子投票是信息化治理、组织决策和在线协作中的重要基础能力。与纸质投票相比，电子投票能够降低人工计票成本，提高结果统计效率，并支持远程参与。然而，传统电子投票系统通常以中心化服务器作为唯一可信执行主体，选民名单、投票状态和计票结果均由服务端数据库保存。当系统管理员权限过大、服务器遭受攻击或日志记录不完整时，投票过程可能难以被外部独立验证。")
    add_para(doc, "区块链技术通过分布式账本、密码学签名和不可篡改的交易记录，为投票系统提供了新的实现思路。将投票规则写入智能合约后，候选项、资格校验、重复投票限制和计票逻辑可以在链上按照公开代码自动执行。任何观察者都可以根据合约地址、交易 Hash 和事件日志复核投票过程，从而降低对中心化平台的单点信任依赖。")
    add_para(doc, "本文课题围绕“基于 Solidity 智能合约与 Ethereum 测试网的去中心化电子投票系统设计与实现”展开，目标不是构建真实政务选举系统，而是完成一个面向毕业设计和教学演示的小规模可执行原型。该原型重点验证智能合约投票、Merkle Tree 白名单、钱包签名、Sepolia 部署、链上结果查询和安全审计等关键技术路径。")
    add_section_heading(doc, "1.2  国内外研究现状")
    add_para(doc, "电子投票研究长期关注身份认证、投票匿名性、可验证计票、抗篡改和系统可用性等问题。传统方案多依赖中心化身份认证、数据库事务和审计日志来保障投票过程完整性。这类方案在工程实现上较成熟，但其可信基础仍集中在系统运营方和数据库管理方，外部审查者通常只能依赖事后报告或抽样日志。")
    add_para(doc, "近年来，区块链和智能合约被广泛用于可验证流程的原型研究。Ethereum 提供账户模型、交易签名、事件日志和合约虚拟机，使投票规则可以被编译为链上程序执行。基于智能合约的投票系统通常具有结果公开、流程可追溯、规则可检查等优势，但也存在交易成本、隐私保护、链上吞吐量和身份绑定等限制。因此，在毕业设计场景中，应明确系统边界，将其定位为小规模投票演示与技术验证，而不是直接替代真实大规模选举。")
    add_section_heading(doc, "1.3  研究目标与主要内容")
    add_para(doc, "本文的研究目标是设计并实现一个可运行、可部署、可测试、可追溯的去中心化电子投票系统。系统应支持管理员配置投票主题和候选项，支持使用地址白名单限制投票资格，支持选民通过钱包签名提交投票交易，支持合约自动拒绝非白名单地址、重复投票和超时投票，并支持前端读取链上结果。")
    add_para(doc, "围绕上述目标，本文完成以下工作：第一，设计投票系统的角色、功能需求、非功能需求和威胁边界；第二，基于 Solidity 编写 VotingSystem 智能合约，并使用 OpenZeppelin MerkleProof 完成白名单验证；第三，使用 Hardhat 搭建编译、测试、部署和 Gas 统计流程；第四，使用 React、TypeScript、Ethers.js 和 MetaMask 实现前端 DApp；第五，在 Sepolia 测试网上重新部署合约并提交真实投票交易；第六，使用 Slither 完成合约静态分析并形成审计记录。")
    add_section_heading(doc, "1.4  论文结构安排")
    add_para(doc, "全文共分为七章。第一章介绍研究背景、研究现状、研究目标和论文结构。第二章说明 Ethereum、Solidity、ECDSA、Keccak-256、Merkle Tree 和 DApp 钱包交互等相关技术。第三章给出系统需求分析和威胁模型。第四章描述系统总体架构、业务流程、投票流程、合约接口和前端模块。第五章介绍智能合约、白名单脚本、部署脚本和前端界面的具体实现。第六章给出测试结果、Gas 消耗、安全审计和 Sepolia 部署证据。第七章总结已完成工作并分析后续改进方向。")

    add_chapter(doc, "第二章  相关技术基础")
    add_section_heading(doc, "2.1  Ethereum 与智能合约")
    add_para(doc, "Ethereum 是支持智能合约的公有区块链平台。用户通过外部账户发起交易，交易经签名后广播到网络，由验证者打包进入区块。智能合约部署后拥有确定的合约地址，其代码和存储状态由链上节点共同维护。对于投票系统而言，合约可以作为公开的规则执行主体，保证投票限制和计票逻辑不依赖单一后端服务器。")
    add_para(doc, "本文选用 Sepolia 测试网进行部署。Sepolia 与主网具有相近的账户、交易和合约执行模型，但使用测试币支付 Gas，适合课程设计和毕业设计验证。系统最终部署合约地址、部署交易 Hash 和投票交易 Hash 均保存到部署记录中，便于复核。")
    add_section_heading(doc, "2.2  Solidity、Hardhat 与 OpenZeppelin")
    add_para(doc, "Solidity 是 Ethereum 生态中最常用的智能合约开发语言。本文合约使用 Solidity 0.8.24 编写，该版本内置整数溢出检查，减少了早期合约中常见的算术安全问题。Hardhat 用于合约编译、单元测试、部署脚本执行和 Gas 统计，能够将合约开发、测试和部署过程组织为可重复命令。")
    add_para(doc, "OpenZeppelin 是智能合约安全组件库。本文未自行实现 Merkle Proof 验证算法，而是使用 OpenZeppelin 的 MerkleProof 库完成 proof 校验，降低了手写密码学验证逻辑出错的概率。")
    add_section_heading(doc, "2.3  ECDSA 签名与地址机制")
    add_para(doc, "Ethereum 外部账户由私钥、公钥和地址构成。设 secp256k1 椭圆曲线的基点为 G，阶为 n，用户私钥为 d，且 1 ≤ d < n，则对应公钥为 Q = dG。Ethereum 地址不是完整公钥，而是对公钥进行 Keccak-256 哈希后取后 20 字节得到，因此地址长度为 20 字节，即 160 bit。")
    add_mono(doc, "Q = dG\naddress = last_20_bytes(keccak256(publicKey))")
    add_para(doc, "用户通过 MetaMask 发起投票交易时，钱包会对交易摘要 z 进行 ECDSA 签名，得到 (r, s, v)。节点在交易进入 EVM 执行前完成签名恢复和账户校验，合约中读取到的 msg.sender 已是验证后的交易发送者。因此，本系统在合约中不需要重复实现 ECDSA 验证，只需要基于 msg.sender 生成白名单叶子节点并校验 Merkle Proof。")
    add_mono(doc, "w  = s^(-1) mod n\nu1 = z * w mod n\nu2 = r * w mod n\nR  = u1 * G + u2 * Q\naccept <=> r == x(R) mod n")
    add_section_heading(doc, "2.4  Keccak-256 与 Merkle Tree")
    add_para(doc, "Keccak-256 是 Ethereum 中常用的哈希函数，输出长度为 32 字节，即 256 bit。本系统使用 Keccak-256 对白名单地址进行哈希，得到 Merkle Tree 的叶子节点。对于 k 个不同输入，哈希碰撞概率可用生日悖论近似分析。输出空间大小 N = 2^256，不发生碰撞的概率为：")
    add_mono(doc, "P(no collision) = Π(i = 0 to k - 1) (1 - i / 2^256)\nP(collision) = 1 - Π(i = 0 to k - 1) (1 - i / 2^256)\n当 k << 2^128 时，P(collision) ≈ k(k - 1) / 2^257")
    add_para(doc, "本系统白名单地址数为 k = 3，因此碰撞概率近似为 3 / 2^256，约等于 2.59 × 10^(-77)。即使扩展到 1,000,000 个地址，碰撞概率也约为 4.32 × 10^(-66)，在工程实践中可视为计算上不可行。")
    add_para(doc, "Merkle Tree 通过树形哈希结构将多个叶子节点压缩为一个根哈希。智能合约只保存 Merkle Root，前端在投票时提交当前地址对应的 proof。链上验证复杂度约为 O(log n)，相比将完整白名单写入合约并遍历验证的 O(n) 方案，能够显著降低链上存储和验证成本。")
    add_picture(doc, FIG / "merkle-proof-flow.png", "图2.1  Merkle Tree 白名单验证流程图", width=5.9)
    add_section_heading(doc, "2.5  DApp 前端与钱包交互")
    add_para(doc, "去中心化应用前端通常不直接保管用户私钥，而是通过浏览器钱包完成账户授权和交易签名。本文前端使用 Ethers.js 封装合约读写操作，读取类方法可通过浏览器钱包或 Sepolia 只读 RPC 获取链上状态，写入类方法必须由用户钱包签名后广播交易。该设计避免前端保存私钥，同时保留用户对交易提交的确认权。")

    add_chapter(doc, "第三章  系统需求分析")
    add_section_heading(doc, "3.1  角色分析")
    add_para(doc, "系统主要涉及管理员、选民和审查者三类角色。管理员负责确定投票主题、候选项、投票截止时间和白名单地址，并执行部署脚本。选民通过 MetaMask 钱包连接前端，在投票窗口内选择候选项并提交交易。审查者不需要拥有投票资格，也可以通过前端、部署记录和 Etherscan 链接验证合约地址、交易 Hash、事件日志和结果统计。")
    add_table(doc, ["角色", "职责", "主要操作"], [
        ["管理员", "初始化投票主题、候选项、截止时间和 Merkle Root", "运行白名单脚本、部署合约、导出前端配置"],
        ["选民", "在投票窗口内完成一次有效投票", "连接钱包、选择候选项、签名交易、查看结果"],
        ["审查者", "验证投票过程和结果", "查看部署记录、交易 Hash、链上结果和审计报告"],
    ], [1.1, 2.5, 2.3])
    add_section_heading(doc, "3.2  功能需求")
    add_para(doc, "系统功能需求包括投票初始化、白名单生成、钱包连接、资格校验、投票提交、重复投票限制、投票窗口控制、实时结果查询和部署证据展示。投票初始化由部署脚本完成，白名单由脚本生成 Merkle Root 和每个地址对应的 proof。前端读取当前账户后匹配 proof，并在提交投票时将候选项索引和 proof 一并发送给合约。")
    add_table(doc, ["编号", "需求", "实现方式"], [
        ["F1", "配置投票主题和候选项", "部署脚本构造 VotingSystem 合约参数"],
        ["F2", "限制白名单投票资格", "Merkle Root 上链，proof 由前端提交"],
        ["F3", "防止重复投票", "mapping(address => bool) 记录投票状态"],
        ["F4", "控制投票截止时间", "block.timestamp 与 votingEndTime 比较"],
        ["F5", "公开查询投票结果", "getResults 返回候选项和票数数组"],
        ["F6", "同步前端部署配置", "exportFrontendArtifact 导出 ABI 与合约地址"],
    ], [0.8, 2.0, 3.1])
    add_section_heading(doc, "3.3  非功能需求")
    add_para(doc, "非功能需求主要包括安全性、可追溯性、可测试性、可部署性和易用性。安全性要求合约拒绝无效 proof、重复投票、非法候选项和超时投票；可追溯性要求部署地址、交易 Hash、Gas 和白名单根可记录；可测试性要求通过自动化测试覆盖主要分支；可部署性要求支持 Sepolia 测试网部署；易用性要求前端采用中文界面，能清晰展示钱包状态、投票面板、结果图表和链上证据。")
    add_section_heading(doc, "3.4  威胁模型与设计边界")
    add_para(doc, "本系统重点防范的风险包括非白名单地址投票、同一地址重复投票、候选项索引越界、投票截止后继续投票和部署配置与前端展示不一致。系统通过智能合约校验和前端配置校验共同降低这些风险。")
    add_para(doc, "需要说明的是，本文系统实现的是地址维度的资格控制和地址伪匿名，并不提供真实身份认证、强匿名投票、抗胁迫投票和大规模隐私保护能力。链上交易公开可查，如果地址与真实身份在线下发生关联，投票行为仍可能被追踪。因此，本文将系统定位为去中心化电子投票原型和教学演示系统。")

    add_chapter(doc, "第四章  系统总体设计")
    add_section_heading(doc, "4.1  总体架构设计")
    add_para(doc, "系统采用前端 DApp、钱包签名、区块链 RPC 和链上智能合约协同的架构。前端负责展示界面、加载部署配置、匹配白名单 proof、调用合约读写方法；MetaMask 负责账户授权和交易签名；Sepolia RPC 负责读取链上状态和广播交易；VotingSystem 合约负责最终资格校验、状态写入和事件触发。")
    add_picture(doc, FIG / "system-architecture.png", "图4.1  系统总体架构图", width=5.9)
    add_section_heading(doc, "4.2  业务流程设计")
    add_para(doc, "业务流程从投票配置开始。管理员先确定投票主题、候选项和白名单地址，随后运行白名单生成脚本得到 Merkle Root 与 proof 列表。部署脚本将主题、候选项、截止时间和 Merkle Root 写入合约构造参数。选民进入前端后连接钱包，前端读取当前账户并匹配 proof，最后提交投票交易。合约完成校验后更新票数，前端通过 getResults 展示公开统计结果。")
    add_picture(doc, FIG / "business-process.png", "图4.2  业务流程图", width=5.9)
    add_section_heading(doc, "4.3  投票交易流程设计")
    add_para(doc, "投票交易属于链上写操作，必须由选民钱包签名。前端只负责构造 candidateIndex 和 merkleProof 参数，不能绕过合约校验。合约执行时先完成投票窗口、候选项索引、重复投票状态和 proof 有效性检查，再写入 voted 映射并增加候选项票数，最后触发 VoteCast 事件。")
    add_picture(doc, FIG / "voting-flow.png", "图4.3  投票交易执行流程图", width=5.9)
    add_section_heading(doc, "4.4  合约状态与接口设计")
    add_para(doc, "VotingSystem 合约保存投票主题 title、不可变投票截止时间 votingEndTime、不可变 merkleRoot、候选项数组 candidates、票数数组 voteCounts 和 voted 映射。候选项与票数按相同索引对应，避免额外映射带来的遍历成本。合约对外提供 vote、getCandidates、getResults、isVotingOpen、hasAddressVoted 和 candidateCount 等接口。")
    add_table(doc, ["接口", "类型", "说明"], [
        ["vote(uint256,bytes32[])", "写入", "提交候选项索引和 Merkle Proof，成功后更新票数"],
        ["getResults()", "读取", "一次性返回候选项名称和票数数组"],
        ["isVotingOpen()", "读取", "根据区块时间判断投票窗口是否开放"],
        ["hasAddressVoted(address)", "读取", "查询指定地址是否已经投票"],
        ["candidateCount()", "读取", "返回候选项数量"],
    ], [2.0, 1.0, 3.2])
    add_section_heading(doc, "4.5  前端模块设计")
    add_para(doc, "前端采用组件化设计，主要包括控制台首页、钱包连接面板、投票提交面板、实时结果图表、链上证据面板和资格安全校验面板。状态管理由 useWallet 和 useVotingContract 两个 Hook 完成，前者负责钱包连接和网络识别，后者负责读取部署配置、加载白名单、实例化合约、读取链上结果和提交交易。")

    add_chapter(doc, "第五章  系统详细实现")
    add_section_heading(doc, "5.1  开发环境与工程结构")
    add_para(doc, "项目采用 Node.js、npm、Hardhat、Solidity、React、Vite 和 TypeScript 构建。合约代码位于 contracts 目录，部署和白名单脚本位于 scripts 目录，前端应用位于 apps/web 目录，测试用例位于 test 目录，部署记录和论文支撑材料分别保存在 deployments、docs 和 deliverables 目录。")
    add_table(doc, ["目录或文件", "作用"], [
        ["contracts/VotingSystem.sol", "投票智能合约实现"],
        ["scripts/generateWhitelist.ts", "生成白名单 Merkle Root 和 proof"],
        ["scripts/deploy.ts", "部署合约到本地或 Sepolia 网络"],
        ["scripts/exportFrontendArtifact.ts", "导出前端 ABI 和部署配置"],
        ["apps/web/src", "React 前端源码"],
        ["test", "合约、脚本和前端资源自动化测试"],
        ["deliverables/graduation", "毕业设计说明书、截图、图表和报告"],
    ], [2.1, 4.2])
    add_section_heading(doc, "5.2  智能合约实现")
    add_para(doc, "合约构造函数对标题、候选项数量、投票截止时间和 Merkle Root 进行一次性校验，避免部署出不可用的合约实例。votingEndTime 和 merkleRoot 被声明为 immutable，部署后不可修改，既符合投票规则固定的业务要求，也减少了不必要的存储写入风险。")
    add_mono(doc, "require(bytes(_title).length > 0, \"Title is required\");\nrequire(_candidates.length >= 2, \"Invalid candidate count\");\nrequire(_votingEndTime > block.timestamp, \"Voting end time must be in the future\");\nrequire(_merkleRoot != bytes32(0), \"Merkle root is required\");")
    add_para(doc, "vote 函数采用 Checks-Effects-Interactions 思路。函数先进行所有输入和状态校验，再修改 voted 和 voteCounts。合约不接收 ETH，不向外部地址转账，也不调用不可信外部合约，因此不存在典型资金重入路径。")
    add_mono(doc, "require(block.timestamp <= votingEndTime, \"Voting has ended\");\nrequire(candidateIndex < candidates.length, \"Invalid candidate index\");\nrequire(!voted[msg.sender], \"Address has already voted\");\nbytes32 leaf = keccak256(abi.encodePacked(msg.sender));\nrequire(MerkleProof.verify(merkleProof, merkleRoot, leaf), \"Address is not eligible\");\nvoted[msg.sender] = true;\nvoteCounts[candidateIndex] += 1;")
    add_section_heading(doc, "5.3  白名单与 Merkle Proof 实现")
    add_para(doc, "白名单脚本接收地址数组后，对每个地址执行 checksum 规范化并拒绝重复地址。叶子节点计算方式与合约保持一致，即 keccak256(abi.encodePacked(address))。脚本生成 Merkle Root、每个地址的 leaf 和 proof，并写入前端 public 目录，供 DApp 在浏览器中读取。")
    add_para(doc, "当前白名单包含 3 个地址，Merkle Root 为 0xb84d167dee14c531723adc7c8625c29224727496b7a19329eda9cbc6d15c4a21。合约只保存根哈希，不保存完整地址列表，既减少链上存储，也避免直接在合约状态中暴露完整白名单。")
    add_section_heading(doc, "5.4  前端 DApp 实现")
    add_para(doc, "前端首页采用较深的棕黑色控制台风格，突出“去中心化电子投票系统”的毕业设计主题。页面顶部展示链上规则，主体区域展示系统说明、合约执行记录、钱包连接、投票提交、实时结果、链上证据和白名单校验状态。前端所有英文控制台名称和主要提示已替换为中文，使其更适合毕业设计演示。")
    add_picture(doc, SHOT / "system-overview-top.png", "图5.1  系统首页与合约执行记录", width=5.9)
    add_picture(doc, SHOT / "wallet-and-voting-panel.png", "图5.2  钱包连接与投票提交面板", width=5.9)
    add_picture(doc, SHOT / "results-and-evidence-panel.png", "图5.3  实时投票结果与链上证据面板", width=5.9)
    add_picture(doc, SHOT / "merkle-security-panel.png", "图5.4  白名单与 Merkle Proof 安全校验面板", width=5.9)
    add_section_heading(doc, "5.5  部署与前端配置同步")
    add_para(doc, "部署流程由 npm 脚本串联完成。首先运行白名单生成脚本，得到最新 Merkle Root；然后运行 Hardhat 部署脚本，将合约部署到 Sepolia；最后运行前端导出脚本，把合约地址、ABI、候选项、截止时间和部署交易 Hash 写入 apps/web/public/deployment.json。这样前端读取的配置与链上部署保持一致。")
    add_mono(doc, "npm run generate:whitelist\nnpm run deploy:sepolia\nnpm run export:frontend -- --network sepolia\nnpm run web:build")

    add_chapter(doc, "第六章  测试、安全审计与部署分析")
    add_section_heading(doc, "6.1  测试环境与测试策略")
    add_para(doc, "系统测试采用自动化测试与链上实测相结合的方式。自动化测试覆盖前端显示工具、前端资源校验、部署脚本输入校验和 VotingSystem 合约核心逻辑。链上实测使用 Sepolia 测试网部署合约，并通过白名单地址提交真实投票交易，以验证部署配置、交易签名、链上状态读取和前端展示是否一致。")
    add_section_heading(doc, "6.2  自动化测试结果")
    add_para(doc, "运行 npm test 后，测试套件共 24 个用例全部通过。其中 VotingSystem 合约测试覆盖初始化、白名单投票、非白名单拒绝、重复投票拒绝、非法候选项拒绝、投票截止拒绝和结果读取等关键路径。")
    add_table(doc, ["测试模块", "用例数", "覆盖内容", "结果"], [
        ["前端显示工具", "7", "地址缩写、链 ID、票数统计、ABI 摘要、错误提示", "通过"],
        ["前端资源校验", "4", "部署配置、白名单、重复地址、Merkle Root 一致性", "通过"],
        ["部署脚本校验", "4", "候选项、地址格式、白名单生成与 proof 非空", "通过"],
        ["VotingSystem 合约", "9", "初始化、投票、拒绝非白名单、重复投票、截止时间、结果读取", "通过"],
    ], [1.5, 0.8, 3.2, 0.8])
    add_picture(doc, FIG / "test-result-table.png", "图6.1  测试结果汇总图", width=5.7)
    add_section_heading(doc, "6.3  Gas 消耗分析")
    add_para(doc, "Gas 分析使用 npm run test:gas 执行。该命令将 REPORT_GAS 设置为 true，并在 Hardhat 测试完成后输出合约部署和方法调用的 Gas 消耗。结果显示，本地部署 VotingSystem 消耗 767,754 Gas，vote 方法最小值为 73,654，最大值为 73,666，平均值为 73,661。真实 Sepolia 部署交易消耗 903,205 Gas，真实投票交易消耗 74,413 Gas。")
    add_picture(doc, FIG / "gas-comparison-chart.png", "图6.2  Gas 消耗分析图", width=5.7)
    add_table(doc, ["操作", "Gas Used", "数据来源", "说明"], [
        ["本地部署", "767,754", "npm run test:gas", "初始化合约字节码和状态"],
        ["vote 平均值", "73,661", "npm run test:gas", "白名单投票平均消耗"],
        ["Sepolia 部署", "903,205", "部署交易回执", "真实测试网部署消耗"],
        ["Sepolia 投票", "74,413", "投票交易回执", "真实测试网投票消耗"],
    ], [1.4, 1.0, 1.4, 2.5])
    add_section_heading(doc, "6.4  安全审计与风险分析")
    add_para(doc, "本文使用 Slither 对合约进行静态分析，命令为 slither . --filter-paths \"node_modules|artifacts|cache\"。Slither 共分析 3 个合约对象和 101 个检测器，最终输出 3 条 timestamp 相关提示，位置分别为构造函数、vote 函数和 isVotingOpen 函数。")
    add_para(doc, "timestamp 风险的核心在于 block.timestamp 由区块生产者给出，理论上可能存在小范围偏移，不适合用于随机数、抽奖或资金分配。本系统仅使用 block.timestamp 判断投票截止时间，不依赖秒级精度产生经济收益，因此该风险属于可解释的业务边界。系统同时不存在 ETH 托管、外部合约调用和不可信回调，重入风险较低。")
    add_picture(doc, FIG / "security-audit-summary.png", "图6.3  Slither 安全审计结果摘要", width=5.7)
    add_section_heading(doc, "6.5  Sepolia 测试网部署结果")
    add_para(doc, "最新 Sepolia 合约地址为 0x6772e0193eAAA77cB89d135188f09e339C4dE66A，部署交易 Hash 为 0xd4a9205dc710acff89205baa79b7141634d9fef401679d5152ace233b03b7724。部署账户为 0x372ee50901D62F3b314936C9302b19F8F477716E，投票窗口约为 30 分钟。系统已使用部署账户完成一笔真实投票交易，交易 Hash 为 0x810ce83b69781f3980b1ba3c7ab0975948c16d87713a80d9432be76ea7e95321，区块高度为 10843573。")
    add_picture(doc, FIG / "deployment-evidence-table.png", "图6.4  Sepolia 部署证据表", width=5.9)
    add_picture(doc, SHOT / "system-home-chain-read.png", "图6.5  前端读取真实链上投票结果截图", width=4.8)

    add_chapter(doc, "第七章  总结与展望")
    add_section_heading(doc, "7.1  工作总结")
    add_para(doc, "本文围绕传统中心化电子投票系统存在的单点故障、数据易被人为干预和结果复核成本较高等问题，设计并实现了一个基于 Solidity 智能合约与 Ethereum Sepolia 测试网的去中心化电子投票系统。系统完成了从需求分析、总体设计、合约开发、前端实现、测试验证、安全审计到测试网部署的完整工程流程。")
    add_para(doc, "在技术实现上，系统使用 VotingSystem 合约固定投票规则，使用 Merkle Tree 白名单实现地址级资格控制，使用 mapping 防止重复投票，使用 Ethers.js 和 MetaMask 完成钱包交互，使用 Hardhat 组织测试与部署，使用 Slither 输出安全审计证据。最终系统能够在前端展示真实链上结果，并通过合约地址、交易 Hash、Gas 数据和测试报告进行追溯。")
    add_section_heading(doc, "7.2  不足与展望")
    add_para(doc, "受毕业设计周期和测试网场景限制，本文系统仍存在若干不足。第一，系统采用地址白名单，不包含真实身份认证和实名授权流程；第二，链上交易公开可查，无法提供强匿名和抗关联分析能力；第三，当前候选项和截止时间在部署后固定，不支持治理式动态变更；第四，系统面向小规模投票演示，尚未处理大规模并发、隐私保护和生产级运维监控问题。")
    add_para(doc, "后续可从四个方向继续完善：一是引入链下身份认证与链上凭证结合机制，提高资格发放可信度；二是研究零知识证明、盲签名或承诺揭示机制，增强投票隐私；三是扩展后台管理与多轮投票能力，提高系统可配置性；四是补充形式化验证、第三方审计和持续集成流程，使系统更接近生产级工程要求。")

    add_chapter(doc, "参考文献")
    refs = [
        "[1] Nakamoto S. Bitcoin: A Peer-to-Peer Electronic Cash System[EB/OL]. 2008.",
        "[2] Buterin V. Ethereum Whitepaper: A Next-Generation Smart Contract and Decentralized Application Platform[EB/OL]. 2014.",
        "[3] Wood G. Ethereum: A Secure Decentralised Generalised Transaction Ledger[R]. Ethereum Yellow Paper, 2024.",
        "[4] OpenZeppelin. Contracts Documentation: MerkleProof[EB/OL].",
        "[5] Solidity Team. Solidity Documentation, Version 0.8.x[EB/OL].",
        "[6] Hardhat. Ethereum Development Environment Documentation[EB/OL].",
        "[7] Trail of Bits. Slither: Static Analyzer for Solidity[EB/OL].",
        "[8] Johnson D, Menezes A, Vanstone S. The Elliptic Curve Digital Signature Algorithm (ECDSA)[J]. International Journal of Information Security, 2001.",
        "[9] Merkle R C. A Digital Signature Based on a Conventional Encryption Function[C]. CRYPTO, 1987.",
        "[10] Ethers.js Contributors. Ethers.js Documentation[EB/OL].",
    ]
    for ref in refs:
        add_para(doc, ref, first_line=False)

    add_chapter(doc, "附录A  关键命令与运行证据")
    add_section_heading(doc, "A.1  主要命令")
    add_mono(doc, "npm install\nnpm run compile\nnpm test\nnpm run test:gas\nnpm run generate:whitelist\nnpm run deploy:sepolia\nnpm run export:frontend -- --network sepolia\nnpm run web:build\nslither . --filter-paths \"node_modules|artifacts|cache\"")
    add_section_heading(doc, "A.2  最新部署与交易证据")
    add_table(doc, ["字段", "内容"], [
        ["合约地址", "0x6772e0193eAAA77cB89d135188f09e339C4dE66A"],
        ["部署交易 Hash", "0xd4a9205dc710acff89205baa79b7141634d9fef401679d5152ace233b03b7724"],
        ["投票交易 Hash", "0x810ce83b69781f3980b1ba3c7ab0975948c16d87713a80d9432be76ea7e95321"],
        ["白名单根", "0xb84d167dee14c531723adc7c8625c29224727496b7a19329eda9cbc6d15c4a21"],
        ["测试结果", "24 passing"],
        ["Slither 审计", "3 条 timestamp 提示，均已解释"],
    ], [1.4, 4.7])

    add_chapter(doc, "致谢")
    add_para(doc, "本毕业设计从选题、需求分析、系统设计到实现验证，得到了指导教师王立鹏老师的指导和帮助。老师在研究方向、系统边界、论文结构和工程规范方面提出了许多重要建议，使本文能够从单纯代码实现逐步完善为包含需求、设计、测试、部署和安全分析的完整毕业设计。")
    add_para(doc, "同时感谢学院在毕业设计过程中提供的模板、规范和阶段性检查要求。通过本课题的完成，作者进一步理解了区块链应用开发、智能合约安全、前端 DApp 交互和软件工程文档化的重要性。由于个人能力和时间有限，系统仍有不足之处，恳请各位老师批评指正。")


def main() -> None:
    OUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    # The school template is used as the formatting and structure reference. A
    # clean DOCX package is generated here because the original template carries
    # legacy OLE/media relationships that make LibreOffice PDF rendering fail.
    doc = Document()
    setup_document(doc)
    add_cover(doc)
    add_declarations(doc)
    add_abstracts(doc)
    add_toc(doc)
    add_body(doc)
    doc.save(OUT_DOCX)
    print(OUT_DOCX)


if __name__ == "__main__":
    main()
