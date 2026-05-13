# Sepolia 部署记录

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 网络 | Sepolia |
| 合约 | `VotingSystem` |
| Chain ID | `11155111` |
| 合约地址 | `0x27D45F85F300d4169D01cA1561388583cF8253D9` |
| 部署交易 Hash | `0x06779ad4e5a6bb7ff72501d842d18310817489c3def8c46becb5436c8344d77b` |
| 部署账户 | `0x372ee50901D62F3b314936C9302b19F8F477716E` |
| 部署时间 | `2026-05-13T05:39:49.687Z` |
| 投票截止时间 | `2026-05-13T06:09:31.000Z` |
| 投票窗口 | 约 30 分钟 |
| Merkle Root | `0xb84d167dee14c531723adc7c8625c29224727496b7a19329eda9cbc6d15c4a21` |
| Etherscan 地址 | <https://sepolia.etherscan.io/address/0x27D45F85F300d4169D01cA1561388583cF8253D9> |
| Etherscan 交易 | <https://sepolia.etherscan.io/tx/0x06779ad4e5a6bb7ff72501d842d18310817489c3def8c46becb5436c8344d77b> |

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

## ABI 与前端同步

部署后已运行：

```bash
npm run export:frontend -- --network sepolia
```

前端部署配置已同步到 `apps/web/public/deployment.json`，其中包含合约地址、部署交易、链 ID、Merkle Root 和 ABI。
