# Sepolia 部署记录

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 网络 | Sepolia |
| 合约 | `VotingSystem` |
| Chain ID | `11155111` |
| 合约地址 | `0x7140ecD54bf13bdc7A56364755fa8DAbFD3C2E28` |
| 部署交易 Hash | `0xa6b2bcfda0832e35ffe9f0e08781f3a25c551d4b16da586a0e42785841f62a86` |
| 部署账户 | `0x372ee50901D62F3b314936C9302b19F8F477716E` |
| 部署时间 | `2026-05-24T02:18:26.689Z` |
| 投票截止时间 | `2026-05-24T02:48:02.000Z` |
| 投票窗口 | 约 30 分钟 |
| Merkle Root | `0xb84d167dee14c531723adc7c8625c29224727496b7a19329eda9cbc6d15c4a21` |
| Etherscan 地址 | <https://sepolia.etherscan.io/address/0x7140ecD54bf13bdc7A56364755fa8DAbFD3C2E28> |
| Etherscan 部署交易 | <https://sepolia.etherscan.io/tx/0xa6b2bcfda0832e35ffe9f0e08781f3a25c551d4b16da586a0e42785841f62a86> |

## 白名单地址

| 序号 | 地址 |
| ---: | --- |
| 1 | `0x372ee50901D62F3b314936C9302b19F8F477716E` |
| 2 | `0x223c397328A746dF817aAE4958a83Df9A7c1Cb97` |
| 3 | `0x253f4a33c6e1920bA081200394B6EC10a729696B` |

白名单 Merkle Proof 已同步到 `apps/web/public/whitelist.json`。

## Gas 记录

| 操作 | Gas Used | 来源 | 说明 |
| --- | ---: | --- | --- |
| Sepolia 部署合约 | `903,205` | 部署交易回执 | 初始化标题、候选项、截止时间和 Merkle Root |
| 本地部署 `VotingSystem` | `767,754` | `npm run test:gas` | Hardhat 本地测试链估算值 |
| 成功投票 `vote` 最小值 | `73,654` | `npm run test:gas` | 白名单账户首次投票 |
| 成功投票 `vote` 最大值 | `73,666` | `npm run test:gas` | 不同 proof 路径产生细微差异 |
| 成功投票 `vote` 平均值 | `73,661` | `npm run test:gas` | 5 次测试调用平均值 |
| Sepolia 成功投票 | `74,413` | 投票交易回执 | 白名单部署账户为方案 A 投票 |

## 投票交易证据

| 项目 | 内容 |
| --- | --- |
| 投票账户 | `0x372ee50901D62F3b314936C9302b19F8F477716E` |
| 候选项 | 方案 A：区块链投票系统 |
| 投票交易 Hash | `0x9bc1ed5d902a984f86215e2ce01ffd0e3b95b041a101b5edc5fadd9b6adf629e` |
| 投票 Gas Used | `74,413` |
| 区块高度 | `10908830` |
| Etherscan 投票交易 | <https://sepolia.etherscan.io/tx/0x9bc1ed5d902a984f86215e2ce01ffd0e3b95b041a101b5edc5fadd9b6adf629e> |

## ABI 与前端同步

部署后已运行：

```bash
npm run export:frontend -- --network sepolia
```

前端部署配置已同步到 `apps/web/public/deployment.json`，其中包含合约地址、部署交易、链 ID、Merkle Root 和 ABI。
