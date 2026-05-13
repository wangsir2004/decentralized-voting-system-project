# Sepolia 部署记录

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 网络 | Sepolia |
| 合约 | VotingSystem |
| Chain ID | `11155111` |
| 合约地址 | `0xf1793b5DE04811Aca913C450F3C4aF380E1e5297` |
| 部署交易 Hash | `0x8aa3a6c20bf3a4bece025bf370f3ec8fe6b6859da5b20950ef7255852fb33f31` |
| 部署账户 | `0x372ee50901D62F3b314936C9302b19F8F477716E` |
| 部署时间 | `2026-05-06T09:22:26.295Z` |
| Merkle Root | `0x9a3e8214c917f9a4c48601b3135d1cdff0d69955d60e2da76a906ca579349b91` |
| Etherscan | <https://sepolia.etherscan.io/address/0xf1793b5DE04811Aca913C450F3C4aF380E1e5297> |

## Gas 记录

| 操作 | Gas Used | 交易 Hash | 说明 |
| --- | ---: | --- | --- |
| 部署合约 | `959,938` | `0x8aa3a6c20bf3a4bece025bf370f3ec8fe6b6859da5b20950ef7255852fb33f31` | 初始化标题、候选项、截止时间和 Merkle Root |
| 成功投票 | 记录投票回执中的 Gas Used | 记录成功投票交易 Hash | 白名单账户首次投票 |
| 重复投票失败 | 记录失败交易或本地测试结果 | 记录失败交易 Hash 或测试名称 | 合约回滚，不计入有效票数 |

## ABI 与前端同步

部署后运行：

```bash
npm run export:frontend -- --network sepolia
```

前端部署配置已同步到 `apps/web/public/deployment.json`。
