# 算法与安全分析笔记

## ECDSA 与地址伪匿名

Ethereum 账户由私钥、公钥和地址构成。用户通过 MetaMask 对交易签名，智能合约通过 `msg.sender` 获取交易发起地址。本系统不在链上保存真实身份信息，只保存地址层面的投票状态，因此实现的是地址维度的伪匿名。

该设计可以降低真实身份暴露风险，但不能提供严格匿名性。链上交易公开可查，如果地址与真实身份在链下发生关联，投票行为仍可能被追踪。论文中应将其表述为「地址伪匿名」，而不是「完全匿名投票」。

## 哈希与 Merkle Tree

选民地址先经过 Keccak-256 哈希处理：

```text
leaf = keccak256(abi.encodePacked(voterAddress))
```

所有叶子节点构成 Merkle Tree。智能合约只保存 `merkleRoot`，投票时由前端提交对应地址的 Merkle Proof。合约用 `MerkleProof.verify` 验证该地址是否属于白名单。

若选民数量为 `n`，单个 proof 的长度约为 `log2(n)`，链上验证复杂度为 `O(log n)`。相比把完整选民列表写入链上并遍历验证的 `O(n)` 方案，Merkle Tree 更节省存储和 Gas。

## 防重复投票

合约使用地址到布尔值的映射记录投票状态：

```solidity
mapping(address => bool) private voted;
```

投票成功后立即设置：

```solidity
voted[msg.sender] = true;
```

同一地址再次调用 `vote` 会被回滚，错误信息为 `Address has already voted`。该机制保证每个白名单地址最多成功投票一次。

## 投票时间控制

合约在部署时写入 `votingEndTime`，并要求结束时间晚于当前区块时间。投票时检查：

```solidity
require(block.timestamp <= votingEndTime, "Voting has ended");
```

到达截止时间后，新的投票交易会被拒绝。前端也会读取 `isVotingOpen()`，用于禁用提交按钮和展示投票状态。

## 重入攻击分析

本合约不接收 ETH，不向外部地址转账，也不调用不可信外部合约。核心 `vote` 流程只修改内部状态并发出事件，不存在典型资金重入路径。

从 Checks-Effects-Interactions 模式看，`vote` 函数没有外部交互阶段。合约主要风险不在重入，而在白名单 proof、投票截止时间和前端网络配置是否正确。

## Gas 记录

当前数据来自 `npm run test:gas`，测试环境为 Hardhat 内置网络，Solidity 版本为 `0.8.24`，优化器开启，`runs` 为 `200`。

| 操作 | Gas Used | 说明 |
| --- | ---: | --- |
| 部署 `VotingSystem` | `869,715` | 初始化标题、候选项、截止时间和 Merkle Root |
| 成功投票 `vote` | 平均 `77,880` | 验证 Merkle Proof、检查候选项、写入投票状态 |
| 读取结果 `getResults` | 本地调用不消耗交易 Gas | `view` 方法，不产生链上状态变更 |

Sepolia 部署后，应在 `docs/deployments/sepolia.md` 中补充真实链上交易 Hash 和区块浏览器链接。
