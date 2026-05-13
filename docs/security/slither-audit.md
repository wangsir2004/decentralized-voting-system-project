# Slither 智能合约审计报告

## 审计范围

| 项目 | 内容 |
| --- | --- |
| 审计工具 | Slither |
| 工具版本 | `0.11.5` |
| 审计命令 | `slither . --filter-paths "node_modules|artifacts|cache"` |
| 审计时间 | `2026-05-13` |
| 合约文件 | `contracts/VotingSystem.sol` |
| Solidity 版本 | `0.8.24` |
| 编译框架 | Hardhat |

原始 JSON 结果已保存到 `docs/security/slither-results.json`。

## 审计结果摘要

Slither 共分析 3 个合约对象和 101 个检测器，输出 3 条 `timestamp` 相关提示：

| 检测器 | 位置 | 说明 | 处理结论 |
| --- | --- | --- | --- |
| `timestamp` | `constructor` | 使用 `block.timestamp` 检查截止时间必须晚于部署时间 | 接受，属于部署参数有效性校验 |
| `timestamp` | `vote` | 使用 `block.timestamp` 判断投票是否截止 | 接受，属于投票业务截止时间 |
| `timestamp` | `isVotingOpen` | 使用 `block.timestamp` 返回投票开放状态 | 接受，属于只读状态展示 |

Slither 初次审计还提示 `votingEndTime` 和 `merkleRoot` 可以声明为 `immutable`。本轮已将二者改为：

```solidity
uint256 public immutable votingEndTime;
bytes32 public immutable merkleRoot;
```

复跑 Slither 后，`immutable-states` 提示已消除。

## 风险分析

`block.timestamp` 在链上由区块生产者给出，理论上存在小范围偏移，因此不适合直接用于随机数、抽奖、开奖或资金分配。本系统使用时间戳的目的仅是判断“投票是否超过截止时间”，不通过秒级时间差产生经济收益。

该风险的影响边界为：用户在截止时间附近提交交易时，交易是否被打包进截止时间前的区块会影响是否成功。这与现实投票系统中的截止时间一致，属于可解释的业务边界。

## 安全设计结论

- 合约不接收 ETH，不存在资金托管逻辑。
- 合约不向外部地址转账，不存在外部资金交互。
- `vote` 函数不调用不可信外部合约，重入风险低。
- 投票前完成时间、候选项、重复投票和白名单 proof 校验。
- 投票成功后先写入 `voted`，再增加候选项票数，状态变化清晰。
- 白名单只在链上保存 Merkle Root，不把完整选民列表写入合约存储。

综合判断：当前合约满足毕业设计演示场景下的安全要求。若进入真实生产级投票场景，还需要补充身份认证、隐私保护、链上治理流程、合约形式化验证和第三方安全审计。
