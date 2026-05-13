# Gas 消耗分析摘要

## 验证命令

```bash
npm run test:gas
```

执行结果为 `24 passing`。Gas 统计由 `hardhat-gas-reporter` 生成，原始输出保存于 `deliverables/graduation/reports/gas-output.txt`。

## Gas 数据

| 操作 | Gas Used | 数据来源 | 说明 |
| --- | ---: | --- | --- |
| 本地部署 `VotingSystem` | 767,754 | `npm run test:gas` | 部署合约并初始化标题、候选项、截止时间和 Merkle Root |
| `vote` 最小值 | 73,654 | `npm run test:gas` | 白名单地址首次投票 |
| `vote` 最大值 | 73,666 | `npm run test:gas` | 不同 proof 路径造成少量波动 |
| `vote` 平均值 | 73,661 | `npm run test:gas` | 5 次成功调用平均值 |
| Sepolia 部署交易 | 903,205 | Sepolia 部署回执 | 合约真实测试网部署 Gas |
| Sepolia 投票交易 | 74,413 | Sepolia 投票回执 | 部署账户真实投票交易 Gas |

## 分析结论

部署交易 Gas 明显高于单次投票交易，主要原因是部署阶段需要写入合约字节码并初始化候选项数组。投票交易主要消耗来自 Merkle Proof 验证、重复投票状态写入和候选项票数更新。`getResults`、`isVotingOpen` 等 `view` 方法用于前端读取，不改变链上状态，在本地调用场景下不产生交易 Gas。
