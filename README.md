# Decentralized Voting System

基于 Solidity 智能合约和 Ethereum Sepolia 测试网的去中心化电子投票系统毕业设计项目。

## 制作方向

本项目采用「工程完整型 MVP + 论文增强」路线：

- 使用 Solidity + Hardhat 实现投票智能合约。
- 使用 React + Vite + TypeScript + Ethers.js 构建 DApp 前端。
- 使用 MetaMask 连接钱包并提交链上投票交易。
- 使用 Merkle Tree 白名单验证选民资格，避免在链上保存完整选民列表。
- 在 Sepolia 测试网部署，并记录合约地址、ABI、交易 Hash 和 Gas 数据。
- 为毕业论文沉淀系统架构、数据流、测试、安全分析和算法论证材料。

## 当前文档

- [任务书研读总结](./任务书研读总结.md)
- [从零学会去中心化投票项目](./docs/learning/from-zero-decentralized-voting.md)
- [系统设计规格](./docs/superpowers/specs/2026-05-04-decentralized-voting-system-design.md)
- [实施计划](./docs/superpowers/plans/2026-05-04-decentralized-voting-system.md)
- [算法与安全分析笔记](./docs/thesis/algorithm-notes.md)
- [Slither 智能合约审计报告](./docs/security/slither-audit.md)
- [敏捷迭代与 Git 记录](./docs/process/agile-iteration-log.md)
- [方法要求完成度对照表](./docs/process/method-compliance-checklist.md)
- [人工测试清单](./docs/testing/manual-test-checklist.md)
- [Sepolia 部署记录](./docs/deployments/sepolia.md)

## 本地开发

### 安装依赖

```bash
npm install
```

### 生成白名单

```bash
npm run generate:whitelist
```

该命令会读取 `data/voters.sample.json`，生成 `apps/web/public/whitelist.json`，其中包含 Merkle Root 和每个样例地址的 Merkle Proof。

### 编译与测试合约

```bash
npm run compile
npm test
npm run test:gas
```

当前 Gas 参考数据来自 `npm run test:gas`：

- `vote` 平均约 `73,661` gas。
- `VotingSystem` 本地部署约 `767,754` gas。
- Sepolia 最新部署交易消耗 `903,205` gas。

### 本地链部署

终端 1：

```bash
npm run node
```

终端 2：

```bash
npm run deploy:local
npm run export:frontend -- --network localhost
```

### 启动前端

```bash
npm run web:dev
```

浏览器打开 Vite 输出的本地地址。使用 MetaMask 连接 Hardhat 本地网络后，可以用 `data/voters.sample.json` 中的样例账户演示投票流程。

## Sepolia 部署

1. 复制 `.env.example` 为 `.env`。
2. 填写 `SEPOLIA_RPC_URL` 和 `DEPLOYER_PRIVATE_KEY`。
3. 确保部署账户拥有 Sepolia 测试 ETH。
4. 运行：

```bash
npm run generate:whitelist
npm run deploy:sepolia
npm run export:frontend -- --network sepolia
```

部署完成后，将真实合约地址、部署交易 Hash、Gas 数据和 Etherscan 链接记录到 `docs/deployments/sepolia.md`。

## 安全审计

本项目使用 Slither 进行智能合约静态分析：

```bash
slither . --filter-paths "node_modules|artifacts|cache"
```

审计结论和风险解释见 `docs/security/slither-audit.md`。
