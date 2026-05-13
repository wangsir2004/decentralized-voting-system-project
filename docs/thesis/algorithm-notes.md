# 算法与安全分析笔记

## ECDSA 与地址伪匿名

Ethereum 账户由私钥、公钥和地址构成。设椭圆曲线 secp256k1 的基点为 `G`，阶为 `n`。用户私钥为 `d`，其中 `1 <= d < n`，对应公钥为：

```text
Q = dG
```

Ethereum 地址不是公钥本身，而是公钥哈希后的低 160 位：

```text
address = last_20_bytes(keccak256(publicKey))
```

因此地址长度为 20 字节，即 160 bit；而 Keccak-256 的哈希输出为 32 字节，即 256 bit。这就是“地址是 20 字节，哈希值是 32 字节”的原因。

用户通过 MetaMask 发起投票交易时，钱包会对交易摘要 `z` 签名，得到 `(r, s, v)`。ECDSA 验证的核心关系为：

```text
w  = s^(-1) mod n
u1 = z * w mod n
u2 = r * w mod n
R  = u1 * G + u2 * Q
accept <=> r == x(R) mod n
```

Ethereum 节点会在交易进入 EVM 执行前完成签名恢复和账户校验。智能合约中读取到的 `msg.sender` 已经是验证后的交易发送者地址，本系统不需要在合约里再次手写 ECDSA 验证逻辑。攻击者如果没有对应私钥，无法构造能通过节点验证的交易签名。

本系统不在链上保存真实身份信息，只保存地址层面的投票状态，因此实现的是地址维度的伪匿名。链上交易公开可查，如果地址与真实身份在链下发生关联，投票行为仍可能被追踪。论文中应表述为“地址伪匿名”，不要表述为“完全匿名投票”。

## 哈希碰撞概率

系统使用 Keccak-256 计算白名单叶子节点。哈希函数输出空间大小为：

```text
N = 2^256
```

若对 `k` 个不同输入计算哈希，完全不发生碰撞的概率为：

```text
P(no collision) = Π(i = 0 to k - 1) (1 - i / 2^256)
```

因此至少发生一次碰撞的概率为：

```text
P(collision) = 1 - Π(i = 0 to k - 1) (1 - i / 2^256)
```

当 `k << 2^128` 时，可用生日悖论近似：

```text
P(collision) ≈ k(k - 1) / 2^257
```

在本演示系统中，白名单地址数量为 `k = 3`：

```text
P(collision) ≈ 3 * 2 / 2^257 = 3 / 2^256 ≈ 2.59 * 10^(-77)
```

即使扩展到 `k = 1,000,000` 个地址：

```text
P(collision) ≈ 10^6 * (10^6 - 1) / 2^257 ≈ 4.32 * 10^(-66)
```

该概率远低于实际工程中可接受的风险阈值。因此，在本系统规模下，地址叶子哈希碰撞可以视为计算上不可行。

## Merkle Tree 白名单机制

选民地址先经过 Keccak-256 哈希处理：

```text
leaf_i = keccak256(abi.encodePacked(voterAddress_i))
```

本项目在 `scripts/generateWhitelist.ts` 中使用 `ethers.solidityPacked(["address"], [address])` 生成与 Solidity `abi.encodePacked(address)` 一致的输入字节。所有叶子节点构成 Merkle Tree，构造时启用 `sortPairs: true`，父节点计算可写为：

```text
parent = H(min(left, right) || max(left, right))
```

当某一层节点数量为奇数时，未配对节点上升到下一层，并在下一层继续参与组合。最终树根为：

```text
root = MerkleRoot(leaf_1, leaf_2, ..., leaf_n)
```

智能合约只保存 `merkleRoot`。投票时，前端根据当前钱包地址提交对应的 Merkle Proof。合约端执行：

```solidity
bytes32 leaf = keccak256(abi.encodePacked(msg.sender));
require(MerkleProof.verify(merkleProof, merkleRoot, leaf), "Address is not eligible");
```

设选民数量为 `n`，单个 proof 的长度约为：

```text
depth ≈ ceil(log2(n))
```

链上验证复杂度为 `O(log n)`。相比把完整选民列表写入链上并遍历验证的 `O(n)` 方案，Merkle Tree 明显降低链上存储量和验证 Gas。

## 防重复投票

合约使用地址到布尔值的映射记录投票状态：

```solidity
mapping(address => bool) private voted;
```

投票成功后立即写入状态：

```solidity
voted[msg.sender] = true;
voteCounts[candidateIndex] += 1;
```

同一地址再次调用 `vote` 会被回滚，错误信息为 `Address has already voted`。该机制保证每个白名单地址最多成功投票一次。

## 投票时间控制

合约在部署时写入 `votingEndTime`，并要求结束时间晚于当前区块时间：

```solidity
require(_votingEndTime > block.timestamp, "Voting end time must be in the future");
```

投票时检查：

```solidity
require(block.timestamp <= votingEndTime, "Voting has ended");
```

到达截止时间后，新的投票交易会被拒绝。Slither 会提示 `block.timestamp` 相关风险。该风险在随机数、抽奖、资金分配等场景中更敏感；本系统仅把它用于投票截止时间判断，不依赖秒级精度产生经济收益，因此可作为受控风险接受。演示和论文描述中应说明：截止时间以链上区块时间为准，临近截止秒提交的交易可能因打包时间差异失败。

## Checks-Effects-Interactions 分析

`vote` 函数执行顺序为：

```text
Checks:
  1. 检查投票是否结束
  2. 检查候选项索引是否合法
  3. 检查地址是否已投票
  4. 检查 Merkle Proof 是否有效

Effects:
  1. 写入 voted[msg.sender] = true
  2. 增加 voteCounts[candidateIndex]

Interactions:
  1. 无外部合约调用
  2. 无 ETH 转账
```

本合约不接收 ETH，不向外部地址转账，也不调用不可信外部合约。核心投票流程只修改内部状态并发出事件，不存在典型资金重入路径。

## Gas 记录

当前数据来自 `npm run test:gas`，测试环境为 Hardhat 内置网络，Solidity 版本为 `0.8.24`，优化器开启，`runs` 为 `200`。

| 操作 | Gas Used | 说明 |
| --- | ---: | --- |
| 本地部署 `VotingSystem` | `767,754` | 初始化标题、候选项、截止时间和 Merkle Root |
| 成功投票 `vote` 最小值 | `73,654` | 白名单账户首次投票 |
| 成功投票 `vote` 最大值 | `73,666` | proof 路径差异导致少量波动 |
| 成功投票 `vote` 平均值 | `73,661` | 5 次测试调用平均值 |
| 读取结果 `getResults` | 本地调用不消耗交易 Gas | `view` 方法，不产生链上状态变更 |

Sepolia 最新部署交易的真实部署 Gas 为 `903,205`，详见 `docs/deployments/sepolia.md`。
