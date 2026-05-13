from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "deliverables" / "graduation" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_REGULAR_PATH = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD_PATH = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_MONO_PATH = r"C:\Windows\Fonts\consola.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


FONT_TITLE = font(FONT_BOLD_PATH, 38)
FONT_H2 = font(FONT_BOLD_PATH, 26)
FONT = font(FONT_REGULAR_PATH, 21)
FONT_SMALL = font(FONT_REGULAR_PATH, 18)
FONT_MONO = font(FONT_MONO_PATH, 18)

BG = "#f7f7f4"
INK = "#1f2933"
MUTED = "#52616b"
BORDER = "#a7b0b7"
BLUE = "#2f6f88"
GREEN = "#4f8f73"
ORANGE = "#b7793f"
FILL = "#ffffff"
FILL2 = "#eef5f2"
FILL3 = "#fff4e6"


def text_size(draw: ImageDraw.ImageDraw, text: str, used_font: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=used_font)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, used_font: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        line = ""
        for char in paragraph:
            test = line + char
            if text_size(draw, test, used_font)[0] <= max_width or not line:
                line = test
            else:
                lines.append(line)
                line = char
        if line:
            lines.append(line)
    return lines


def centered_text(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    text: str,
    used_font: ImageFont.ImageFont,
    fill: str = INK,
    line_gap: int = 7,
) -> None:
    x1, y1, x2, y2 = rect
    lines = wrap_text(draw, text, used_font, x2 - x1 - 24)
    heights = [text_size(draw, line, used_font)[1] for line in lines]
    total = sum(heights) + line_gap * (len(lines) - 1)
    y = y1 + (y2 - y1 - total) / 2
    for line, height in zip(lines, heights):
        width, _ = text_size(draw, line, used_font)
        draw.text((x1 + (x2 - x1 - width) / 2, y), line, font=used_font, fill=fill)
        y += height + line_gap


def draw_box(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    label: str,
    fill: str = FILL,
    outline: str = BORDER,
    used_font: ImageFont.ImageFont = FONT,
    radius: int = 14,
) -> None:
    draw.rounded_rectangle(rect, radius=radius, fill=fill, outline=outline, width=2)
    centered_text(draw, rect, label, used_font)


def arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: str = BLUE,
    width: int = 3,
) -> None:
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    angle = math.atan2(y2 - y1, x2 - x1)
    length = 14
    spread = math.pi / 7
    p1 = (x2 - length * math.cos(angle - spread), y2 - length * math.sin(angle - spread))
    p2 = (x2 - length * math.cos(angle + spread), y2 - length * math.sin(angle + spread))
    draw.polygon([end, p1, p2], fill=color)


def polyline_arrow(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[int, int]],
    color: str = BLUE,
    width: int = 3,
) -> None:
    for start, end in zip(points, points[1:-1]):
        draw.line((start[0], start[1], end[0], end[1]), fill=color, width=width)
    arrow(draw, points[-2], points[-1], color=color, width=width)


def make_canvas(title: str, width: int = 1600, height: int = 950) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    draw.text((60, 42), title, font=FONT_TITLE, fill=INK)
    draw.line((60, 92, width - 60, 92), fill="#d8d8d2", width=2)
    return image, draw


def build_system_architecture() -> None:
    image, draw = make_canvas("系统总体架构图", 1600, 980)
    sections = [
        ("用户层", (90, 160, 360, 840), "#e8f1f2"),
        ("前端 DApp 层", (430, 160, 740, 840), "#eef5f2"),
        ("区块链交互层", (810, 160, 1110, 840), "#fff4e6"),
        ("链上合约层", (1180, 160, 1510, 840), "#f2f1ee"),
    ]
    for title, rect, fill in sections:
        draw.rounded_rectangle(rect, radius=18, fill=fill, outline=BORDER, width=2)
        draw.text((rect[0] + 24, rect[1] + 24), title, font=FONT_H2, fill=INK)

    draw_box(draw, (130, 250, 320, 350), "浏览器用户\n选民地址", fill=FILL2)
    draw_box(draw, (130, 430, 320, 530), "MetaMask\n交易签名", fill=FILL2)
    draw_box(draw, (470, 235, 700, 335), "React + Vite\n中文投票界面")
    draw_box(draw, (470, 395, 700, 495), "Ethers.js\n合约读写封装")
    draw_box(draw, (470, 555, 700, 655), "whitelist.json\nMerkle Proof")
    draw_box(draw, (850, 280, 1070, 380), "Sepolia RPC\n读取链上状态", fill=FILL3)
    draw_box(draw, (850, 500, 1070, 600), "交易广播\n等待确认", fill=FILL3)
    draw_box(draw, (1220, 225, 1470, 325), "VotingSystem.sol\n投票智能合约")
    draw_box(draw, (1220, 395, 1470, 495), "Merkle Root\n白名单资格校验")
    draw_box(draw, (1220, 565, 1470, 665), "VoteCast 事件\n结果公开查询")

    for start, end in [
        ((320, 300), (470, 285)),
        ((320, 480), (470, 445)),
        ((700, 445), (850, 330)),
        ((1070, 330), (1220, 275)),
        ((1070, 550), (1220, 610)),
    ]:
        arrow(draw, start, end)
    polyline_arrow(draw, [(700, 605), (770, 605), (770, 740), (1180, 740), (1180, 445), (1220, 445)])

    image.save(OUT_DIR / "system-architecture.png", quality=95)


def build_business_process() -> None:
    image, draw = make_canvas("业务流程图", 1600, 900)
    steps = [
        ("1", "管理员确定\n投票主题与候选项"),
        ("2", "整理选民地址\n生成白名单"),
        ("3", "部署合约\n写入 Merkle Root"),
        ("4", "选民连接钱包\n读取资格证明"),
        ("5", "选择候选项\n提交投票交易"),
        ("6", "合约校验\n防重复并计票"),
        ("7", "前端读取结果\n公开展示统计"),
    ]
    x = 65
    y = 360
    previous: tuple[int, int, int, int] | None = None
    for index, (num, label) in enumerate(steps):
        rect = (x, y, x + 190, y + 135)
        draw.ellipse((rect[0] - 24, rect[1] - 24, rect[0] + 26, rect[1] + 26), fill=BLUE)
        centered_text(draw, (rect[0] - 24, rect[1] - 24, rect[0] + 26, rect[1] + 26), num, FONT_H2, "white")
        draw_box(draw, rect, label, used_font=FONT_SMALL)
        if previous:
            arrow(draw, (previous[2], (previous[1] + previous[3]) // 2), (rect[0], (rect[1] + rect[3]) // 2), ORANGE)
        previous = rect
        x += 214
    draw.text((90, 620), "流程从投票配置、白名单生成开始，经合约部署、钱包签名和链上验证，最终通过前端公开展示统计结果。", font=FONT, fill=MUTED)

    image.save(OUT_DIR / "business-process.png", quality=95)


def build_voting_flow() -> None:
    image, draw = make_canvas("投票交易执行流程图", 1600, 980)
    flow = [
        ("开始", "选民进入 DApp，读取部署配置"),
        ("读取", "加载 whitelist.json，按当前地址匹配 proof"),
        ("签名", "MetaMask 对投票交易进行 ECDSA 签名"),
        ("校验", "合约检查时间、候选项、重复投票与 Merkle Proof"),
        ("写入", "voted[msg.sender]=true，voteCounts[index] 加一"),
        ("事件", "触发 VoteCast 事件，交易写入区块"),
        ("展示", "前端调用 getResults 展示实时结果"),
    ]
    coords = [
        (150, 180, 500, 280),
        (620, 180, 970, 280),
        (1090, 180, 1440, 280),
        (1090, 410, 1440, 530),
        (620, 410, 970, 530),
        (150, 410, 500, 530),
        (620, 670, 970, 790),
    ]
    for (short, label), rect in zip(flow, coords):
        fill = FILL2 if short in ["开始", "展示"] else FILL3 if short in ["签名", "事件"] else FILL
        draw_box(draw, rect, f"{short}\n{label}", fill=fill, used_font=FONT_SMALL)
    for a, b in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]:
        r1, r2 = coords[a], coords[b]
        arrow(draw, (r1[2], (r1[1] + r1[3]) // 2), (r2[0], (r2[1] + r2[3]) // 2))
    draw.text((120, 850), "核心约束：同一地址只能成功投票一次；非白名单地址或错误 proof 会被合约回滚。", font=FONT, fill=MUTED)
    image.save(OUT_DIR / "voting-flow.png", quality=95)


def build_merkle_flow() -> None:
    image, draw = make_canvas("Merkle Tree 白名单验证流程图", 1600, 980)
    leaves = [(150, 700, 390, 790), (520, 700, 760, 790), (890, 700, 1130, 790)]
    labels = ["leaf A\n0x088a...9644", "leaf B\n0x251f...b1b", "leaf C\n0xb155...0f27"]
    for rect, label in zip(leaves, labels):
        draw_box(draw, rect, label, fill=FILL2, used_font=FONT_SMALL)
    parents = [(330, 500, 580, 600), (750, 500, 1000, 600)]
    for rect, label in zip(parents, ["Hash(A,B)\n0x3066...db2f", "leaf C 上升\n参与下一层"]):
        draw_box(draw, rect, label, fill=FILL3, used_font=FONT_SMALL)
    root = (520, 260, 900, 370)
    draw_box(draw, root, "Merkle Root\n0xb84d167d...15c4a21", fill=FILL)
    for rect in [leaves[0], leaves[1]]:
        arrow(draw, ((rect[0] + rect[2]) // 2, rect[1]), ((parents[0][0] + parents[0][2]) // 2, parents[0][3]), GREEN)
    arrow(draw, ((leaves[2][0] + leaves[2][2]) // 2, leaves[2][1]), ((parents[1][0] + parents[1][2]) // 2, parents[1][3]), GREEN)
    for rect in parents:
        arrow(draw, ((rect[0] + rect[2]) // 2, rect[1]), ((root[0] + root[2]) // 2, root[3]))
    draw_box(draw, (1080, 260, 1460, 390), "合约端验证\nMerkleProof.verify(proof, root, leaf)", fill="#f8eded", used_font=FONT_SMALL)
    arrow(draw, (900, 315), (1080, 315), ORANGE)
    draw.text((110, 130), "地址先按 abi.encodePacked(address) 得到 20 字节输入，再经 Keccak-256 生成 32 字节叶子节点。", font=FONT, fill=MUTED)
    draw.text((110, 850), "本项目白名单地址数 n=3，proof 深度约为 ceil(log2(3))=2，链上验证复杂度为 O(log n)。", font=FONT, fill=MUTED)
    image.save(OUT_DIR / "merkle-proof-flow.png", quality=95)


def build_test_result_table() -> None:
    image, draw = make_canvas("测试结果汇总表", 1500, 780)
    headers = ["测试模块", "用例数", "覆盖内容", "结果"]
    rows = [
        ["前端显示工具", "7", "地址缩写、链 ID、票数统计、ABI 摘要、错误提示", "通过"],
        ["前端资源校验", "4", "部署配置、白名单、重复地址、Merkle Root 一致性", "通过"],
        ["部署脚本校验", "4", "候选项、地址格式、白名单生成与 proof 非空", "通过"],
        ["VotingSystem 合约", "9", "初始化、投票、拒绝非白名单、重复投票、截止时间、结果读取", "通过"],
    ]
    x0, y0 = 70, 160
    col_widths = [260, 120, 820, 150]
    row_height = 78
    x = x0
    for header, width in zip(headers, col_widths):
        draw.rounded_rectangle((x, y0, x + width, y0 + row_height), radius=8, fill=BLUE, outline=BLUE)
        centered_text(draw, (x, y0, x + width, y0 + row_height), header, FONT_SMALL, "white")
        x += width
    for i, row in enumerate(rows):
        y = y0 + row_height * (i + 1)
        x = x0
        for value, width in zip(row, col_widths):
            draw.rectangle((x, y, x + width, y + row_height), fill=FILL if i % 2 == 0 else "#f0f4f3", outline="#cfd6d9")
            centered_text(draw, (x + 6, y, x + width - 6, y + row_height), value, FONT_SMALL, GREEN if value == "通过" else INK)
            x += width
    draw.text((70, y0 + row_height * 6 + 10), "命令：npm test；结果：24 passing。Gas 统计命令 npm run test:gas 同样为 24 passing。", font=FONT_SMALL, fill=MUTED)
    image.save(OUT_DIR / "test-result-table.png", quality=95)


def build_gas_chart() -> None:
    image, draw = make_canvas("Gas 消耗分析图", 1500, 880)
    items = [
        ("本地部署", 767_754, BLUE),
        ("Sepolia 部署", 903_205, ORANGE),
        ("vote 平均", 73_661, GREEN),
        ("Sepolia 投票", 74_413, GREEN),
    ]
    max_value = max(value for _, value, _ in items)
    left, bottom = 180, 720
    bar_width = 180
    for index, (name, value, color) in enumerate(items):
        x = left + index * 280
        height = int((value / max_value) * 430)
        draw.rectangle((x, bottom - height, x + bar_width, bottom), fill=color)
        draw.text((x, bottom + 20), name, font=FONT_SMALL, fill=INK)
        value_text = f"{value:,}"
        width, _ = text_size(draw, value_text, FONT_SMALL)
        draw.text((x + (bar_width - width) / 2, bottom - height - 35), value_text, font=FONT_SMALL, fill=INK)
    draw.line((120, bottom, 1320, bottom), fill=INK, width=2)
    draw.line((120, 250, 120, bottom), fill=INK, width=2)
    draw.text((120, 180), "部署操作包含写入标题、候选项、截止时间和 Merkle Root；vote 操作包含 proof 验证与票数更新。", font=FONT_SMALL, fill=MUTED)
    image.save(OUT_DIR / "gas-comparison-chart.png", quality=95)


def build_deployment_table() -> None:
    image, draw = make_canvas("Sepolia 部署证据表", 1600, 900)
    rows = [
        ("合约地址", "0x6772e0193eAAA77cB89d135188f09e339C4dE66A"),
        ("部署交易 Hash", "0xd4a9205dc710acff89205baa79b7141634d9fef401679d5152ace233b03b7724"),
        ("投票交易 Hash", "0x810ce83b69781f3980b1ba3c7ab0975948c16d87713a80d9432be76ea7e95321"),
        ("部署账户", "0x372ee50901D62F3b314936C9302b19F8F477716E"),
        ("白名单根", "0xb84d167dee14c531723adc7c8625c29224727496b7a19329eda9cbc6d15c4a21"),
        ("部署 Gas", "903,205"),
        ("投票 Gas", "74,413"),
        ("投票窗口", "2026-05-13 14:46:55 至 15:16:55（约 30 分钟）"),
    ]
    x0, y0 = 90, 150
    for i, (key, value) in enumerate(rows):
        y = y0 + i * 78
        draw.rounded_rectangle((x0, y, x0 + 260, y + 58), radius=8, fill=FILL3, outline="#dec7aa")
        centered_text(draw, (x0, y, x0 + 260, y + 58), key, FONT_SMALL)
        draw.rounded_rectangle((x0 + 280, y, x0 + 1410, y + 58), radius=8, fill=FILL, outline="#cfd6d9")
        use_font = FONT_MONO if value.startswith("0x") else FONT_SMALL
        centered_text(draw, (x0 + 290, y, x0 + 1400, y + 58), value, use_font)
    draw.text((90, 805), "追溯链接：sepolia.etherscan.io/address/合约地址 与 sepolia.etherscan.io/tx/交易 Hash。", font=FONT_SMALL, fill=MUTED)
    image.save(OUT_DIR / "deployment-evidence-table.png", quality=95)


def build_security_summary() -> None:
    image, draw = make_canvas("安全审计结果摘要图", 1500, 780)
    items = [
        ("工具", "Slither 0.11.5"),
        ("命令", 'slither . --filter-paths "node_modules|artifacts|cache"'),
        ("分析对象", "contracts/VotingSystem.sol"),
        ("检测器数量", "101"),
        ("结果", "3 条 timestamp 提示，均为可解释业务边界"),
        ("关键结论", "无 ETH 托管、无外部合约调用、重入风险低"),
    ]
    x0, y0 = 90, 160
    for i, (key, value) in enumerate(items):
        y = y0 + i * 85
        draw.rounded_rectangle((x0, y, x0 + 260, y + 62), radius=8, fill="#edf2f7", outline="#cbd5e1")
        centered_text(draw, (x0, y, x0 + 260, y + 62), key, FONT_SMALL)
        draw.rounded_rectangle((x0 + 290, y, x0 + 1360, y + 62), radius=8, fill=FILL, outline="#cbd5e1")
        centered_text(draw, (x0 + 300, y, x0 + 1350, y + 62), value, FONT_SMALL, GREEN if i >= 4 else INK)
    image.save(OUT_DIR / "security-audit-summary.png", quality=95)


def main() -> None:
    build_system_architecture()
    build_business_process()
    build_voting_flow()
    build_merkle_flow()
    build_test_result_table()
    build_gas_chart()
    build_deployment_table()
    build_security_summary()
    print(f"Generated figures in {OUT_DIR}")


if __name__ == "__main__":
    main()
