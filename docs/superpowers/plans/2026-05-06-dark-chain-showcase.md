# 暗链投票安全控制台实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 将当前 React DApp 优化为「暗链投票安全控制台」风格的项目展示页面，同时保留钱包连接、投票提交和结果图表能力。

**架构：** 保持 `useWallet` 和 `useVotingContract` 作为数据与链上交互边界，在 `App.tsx` 中组装展示数据。新增纯展示组件承载首屏、证据区和安全区，新增仓库级 `shared/display.ts` 统一处理地址缩写、票数统计、Proof 深度和 ABI 摘要等可测试逻辑，前端通过 `apps/web/src/utils/display.ts` re-export 复用。

**技术栈：** React 18、Vite、TypeScript、Ethers.js、ECharts、Hardhat 测试。

---

## 文件结构

- 创建：`shared/display.ts`  
  展示层纯函数，负责地址缩写、Chain ID 文案、票数统计、Proof 深度、ABI 方法摘要。
- 创建：`apps/web/src/utils/display.ts`  
  re-export 仓库级展示工具，解决 Hardhat CJS 测试和 Vite ESM 前端的类型边界。
- 创建：`test/frontendDisplay.test.ts`  
  使用现有 Hardhat/Mocha/Chai 测试工具验证展示层纯函数。
- 创建：`apps/web/src/components/ShowcaseMetric.tsx`  
  复用指标卡组件。
- 创建：`apps/web/src/components/CommandHero.tsx`  
  首屏暗链控制台、链路拓扑和合约终端。
- 创建：`apps/web/src/components/EvidencePanel.tsx`  
  合约部署证据、ABI 摘要和结果审计指标。
- 创建：`apps/web/src/components/SecurityPanel.tsx`  
  Merkle Proof 和安全约束说明。
- 修改：`apps/web/src/App.tsx`  
  组装新页面结构和派生展示数据。
- 修改：`apps/web/src/components/WalletPanel.tsx`  
  升级钱包与网络状态展示。
- 修改：`apps/web/src/components/VotingPanel.tsx`  
  升级投票操作面板。
- 修改：`apps/web/src/components/ResultsChart.tsx`  
  改为暗色图表风格并支持空状态。
- 修改：`apps/web/src/hooks/useVotingContract.ts`  
  将白名单 Leaf 和 Proof 深度所需数据暴露给展示层。
- 修改：`apps/web/src/styles.css`  
  重写为暗链控制台视觉系统。

## 任务 1：展示工具函数

**文件：**
- 创建：`test/frontendDisplay.test.ts`
- 创建：`shared/display.ts`
- 创建：`apps/web/src/utils/display.ts`

- [ ] **步骤 1：编写失败的测试**

```typescript
import { expect } from "chai";
import {
  countTotalVotes,
  getLeadingCandidate,
  getNetworkLabel,
  getProofDepth,
  shortenAddress,
  summarizeAbiFunctions
} from "../shared/display";

describe("frontend display utilities", function () {
  it("shortens an ethereum address for dense UI panels", function () {
    expect(shortenAddress("0x5FbDB2315678afecb367f032d93F642f64180aa3")).to.equal("0x5FbD...0aa3");
    expect(shortenAddress("")).to.equal("未连接");
  });

  it("maps known chain ids to readable labels", function () {
    expect(getNetworkLabel(31337)).to.equal("Hardhat Local");
    expect(getNetworkLabel(11155111)).to.equal("Sepolia");
    expect(getNetworkLabel(null)).to.equal("未知网络");
  });

  it("derives vote totals and leading candidate", function () {
    const candidates = ["方案 A", "方案 B", "方案 C"];
    const counts = [2, 5, 1];

    expect(countTotalVotes(counts)).to.equal(8);
    expect(getLeadingCandidate(candidates, counts)).to.deep.equal({ name: "方案 B", count: 5 });
  });

  it("handles empty results without fabricating a leader", function () {
    expect(countTotalVotes([])).to.equal(0);
    expect(getLeadingCandidate([], [])).to.deep.equal({ name: "暂无数据", count: 0 });
  });

  it("returns merkle proof depth from the current proof", function () {
    expect(getProofDepth(["0xaaa", "0xbbb"])).to.equal(2);
    expect(getProofDepth([])).to.equal(0);
  });

  it("summarizes callable ABI function names", function () {
    const abi = [
      { type: "function", name: "vote" },
      { type: "function", name: "getResults" },
      { type: "event", name: "VoteCast" }
    ];

    expect(summarizeAbiFunctions(abi)).to.deep.equal(["vote", "getResults"]);
  });
});
```

- [ ] **步骤 2：运行测试验证失败**

运行：`npm test -- --grep "frontend display utilities"`  
预期：FAIL，报错包含 `Cannot find module '../apps/web/src/utils/display'`。

- [ ] **步骤 3：实现最少工具函数**

```typescript
import type { InterfaceAbi } from "ethers";

export type LeadingCandidate = {
  name: string;
  count: number;
};

export function shortenAddress(address: string, fallback = "未连接") {
  if (!address) return fallback;
  if (address.length <= 12) return address;
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

export function getNetworkLabel(chainId: number | null) {
  if (chainId === 31337) return "Hardhat Local";
  if (chainId === 11155111) return "Sepolia";
  if (chainId === null) return "未知网络";
  return `Chain ${chainId}`;
}

export function countTotalVotes(counts: number[]) {
  return counts.reduce((total, count) => total + count, 0);
}

export function getLeadingCandidate(candidates: string[], counts: number[]): LeadingCandidate {
  if (!candidates.length || !counts.length) return { name: "暂无数据", count: 0 };

  let leaderIndex = 0;
  for (let index = 1; index < counts.length; index += 1) {
    if ((counts[index] ?? 0) > (counts[leaderIndex] ?? 0)) leaderIndex = index;
  }

  return { name: candidates[leaderIndex] ?? "暂无数据", count: counts[leaderIndex] ?? 0 };
}

export function getProofDepth(proof: string[]) {
  return proof.length;
}

export function summarizeAbiFunctions(abi: InterfaceAbi) {
  return abi
    .filter((entry) => typeof entry === "object" && entry !== null && "type" in entry && entry.type === "function")
    .map((entry) => ("name" in entry && typeof entry.name === "string" ? entry.name : "anonymous"))
    .filter((name) => name !== "anonymous");
}
```

- [ ] **步骤 4：运行测试验证通过**

运行：`npm test -- --grep "frontend display utilities"`  
预期：PASS，`frontend display utilities` 测试全部通过。

## 任务 2：暴露白名单展示数据

**文件：**
- 修改：`apps/web/src/hooks/useVotingContract.ts`
- 测试：`npm run web:build`

- [ ] **步骤 1：扩展类型**

在 `WhitelistFile` 的 voter 条目中加入 `leaf`，在 `VotingState` 中加入 `leaf` 和 `whitelistSize`：

```typescript
type WhitelistFile = {
  merkleRoot: string;
  voters: Array<{
    address: string;
    leaf?: string;
    proof: string[];
  }>;
};

export type VotingState = {
  candidates: string[];
  counts: number[];
  isOpen: boolean;
  hasVoted: boolean;
  eligible: boolean;
  proof: string[];
  leaf: string;
  whitelistSize: number;
  txHash: string;
  isLoading: boolean;
  isSubmitting: boolean;
  error: string;
};
```

- [ ] **步骤 2：补齐初始值与刷新赋值**

```typescript
const initialState: VotingState = {
  candidates: [],
  counts: [],
  isOpen: false,
  hasVoted: false,
  eligible: false,
  proof: [],
  leaf: "",
  whitelistSize: 0,
  txHash: "",
  isLoading: false,
  isSubmitting: false,
  error: ""
};
```

刷新时设置：

```typescript
leaf: entry?.leaf ?? "",
whitelistSize: whitelist.voters.length,
```

- [ ] **步骤 3：运行构建验证类型**

运行：`npm run web:build`  
预期：PASS。

## 任务 3：新增展示组件

**文件：**
- 创建：`apps/web/src/components/ShowcaseMetric.tsx`
- 创建：`apps/web/src/components/CommandHero.tsx`
- 创建：`apps/web/src/components/EvidencePanel.tsx`
- 创建：`apps/web/src/components/SecurityPanel.tsx`

- [ ] **步骤 1：创建指标卡组件**

```tsx
type ShowcaseMetricProps = {
  label: string;
  value: string | number;
  detail?: string;
  tone?: "cyan" | "gold" | "danger";
};

export function ShowcaseMetric({ label, value, detail, tone = "cyan" }: ShowcaseMetricProps) {
  return (
    <div className={`showcase-metric metric-${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      {detail && <small>{detail}</small>}
    </div>
  );
}
```

- [ ] **步骤 2：创建首屏组件**

`CommandHero.tsx` 接收部署配置、账户、Chain ID、票数总量、领先项和白名单规模，渲染暗链首屏、节点拓扑和合约终端。

- [ ] **步骤 3：创建证据组件**

`EvidencePanel.tsx` 接收部署配置、总票数、领先项和 ABI 方法摘要，渲染部署证据与结果审计卡。

- [ ] **步骤 4：创建安全组件**

`SecurityPanel.tsx` 接收 Merkle Root、Proof 深度、Leaf、资格状态和安全约束说明，渲染算法与安全区。

- [ ] **步骤 5：运行构建验证组件类型**

运行：`npm run web:build`  
预期：PASS。

## 任务 4：接入新页面结构

**文件：**
- 修改：`apps/web/src/App.tsx`
- 修改：`apps/web/src/components/WalletPanel.tsx`
- 修改：`apps/web/src/components/VotingPanel.tsx`
- 修改：`apps/web/src/components/ResultsChart.tsx`

- [ ] **步骤 1：在 `App.tsx` 计算展示数据**

使用 `countTotalVotes`、`getLeadingCandidate`、`getNetworkLabel`、`getProofDepth`、`summarizeAbiFunctions`。

- [ ] **步骤 2：替换页面结构**

页面顺序为：顶部 HUD 与 `CommandHero`、钱包/投票操作区、结果与证据区、安全区。

- [ ] **步骤 3：升级钱包面板**

`WalletPanel` 使用状态标签和网络标签展示当前钱包状态。

- [ ] **步骤 4：升级投票面板**

`VotingPanel` 展示资格矩阵、候选项序号、票数和禁用原因。

- [ ] **步骤 5：升级图表暗色主题**

`ResultsChart` 使用暗色坐标轴、Tooltip、渐变柱色和空状态占位。

- [ ] **步骤 6：运行构建验证**

运行：`npm run web:build`  
预期：PASS。

## 任务 5：重写暗链控制台样式并验证

**文件：**
- 修改：`apps/web/src/styles.css`

- [ ] **步骤 1：替换基础视觉系统**

定义深色背景、HUD、面板、按钮、状态标签、拓扑节点、终端、指标卡、图表容器和响应式布局。

- [ ] **步骤 2：检查颜色分布**

扫描 CSS，确认不是单一紫色、米色或普通蓝灰主题。主视觉应为近黑 + 青绿 + 金色。

- [ ] **步骤 3：运行完整验证**

运行：

```bash
npm test
npm run web:build
```

预期：全部 PASS。

- [ ] **步骤 4：浏览器验证**

启动：`npm run web:dev`  
检查桌面宽度和移动宽度：

- 首屏不是空白。
- 图表正常渲染。
- 长地址不会撑破面板。
- 投票按钮禁用状态可理解。
- 暗链控制台风格明显。
