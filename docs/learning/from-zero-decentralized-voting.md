# 从零学会去中心化投票项目

本文面向第一次接触区块链项目的同学。目标不是让你背代码，而是让你能说清楚这个项目为什么这样设计，并能按同样思路重写一个简化版。

## 1. 先理解这个项目怎么想出来

传统电子投票系统通常由一个中心服务器保存选民、选票和结果。问题在于：

- 服务器故障会影响投票。
- 管理员理论上可以改数据库。
- 外部人员难以验证计票过程。
- 需要额外处理重复投票和投票截止规则。

区块链方案的核心想法是：把关键规则写进智能合约，把投票结果存在链上。合约部署后，规则公开、执行记录公开，任何人都可以读取最终票数。

本项目的最小目标是：

- 只有白名单地址可以投票。
- 每个地址只能投一次。
- 超过截止时间不能投票。
- 投票结果可以公开读取。
- 前端通过 MetaMask 让用户签名并提交交易。

## 2. 一张图理解系统

```text
选民钱包
  |
  | 连接 MetaMask，签名交易
  v
React 前端
  |
  | 读取 deployment.json 和 whitelist.json
  | 提交 vote(candidateIndex, merkleProof)
  v
Sepolia 上的 VotingSystem 合约
  |
  | 校验白名单、重复投票、截止时间
  v
链上票数 voteCounts
  |
  | getResults()
  v
前端图表和链上证据面板
```

前端不直接改票数。真正改变票数的是链上的 `vote()` 函数。前端只是帮用户把交易发给合约。

## 3. 目录分工

| 目录或文件 | 作用 |
| --- | --- |
| `contracts/VotingSystem.sol` | 智能合约，保存投票规则和票数 |
| `scripts/generateWhitelist.ts` | 根据选民地址生成 Merkle Root 和 Merkle Proof |
| `scripts/deploy.ts` | 部署合约，写入候选项、截止时间和 Merkle Root |
| `scripts/exportFrontendArtifact.ts` | 把合约地址和 ABI 同步给前端 |
| `data/voters.sample.json` | 白名单选民地址源文件 |
| `data/candidates.sample.json` | 候选项源文件 |
| `apps/web/src/hooks/useWallet.ts` | 连接 MetaMask，读取账户和网络 |
| `apps/web/src/hooks/useVotingContract.ts` | 读取链上状态，提交投票交易 |
| `apps/web/src/components/VotingPanel.tsx` | 候选项选择和投票提交面板 |
| `apps/web/src/components/ResultsChart.tsx` | 票数图表 |
| `apps/web/src/components/EvidencePanel.tsx` | 合约地址、部署交易、Gas 等链上证据 |
| `apps/web/public/deployment.json` | 前端读取的合约部署信息 |
| `apps/web/public/whitelist.json` | 前端读取的白名单 proof |
| `test/` | 合约、脚本和前端工具函数测试 |
| `docs/` | 论文、测试清单、部署记录和学习材料 |

## 4. 从零写合约的思路

先写状态变量。状态变量就是链上长期保存的数据。

```solidity
string public title;
uint256 public votingEndTime;
bytes32 public merkleRoot;

string[] private candidates;
uint256[] private voteCounts;
mapping(address => bool) private voted;
```

含义如下：

- `title`：投票标题。
- `votingEndTime`：截止时间，使用 Unix 秒级时间戳。
- `merkleRoot`：白名单根，用于校验某个地址是否有资格。
- `candidates`：候选项数组。
- `voteCounts`：每个候选项的票数，索引和 `candidates` 对齐。
- `voted`：记录某个地址是否已经投票。

再写构造函数。构造函数只在部署合约时执行一次，用于初始化投票。

```solidity
constructor(
    string memory _title,
    string[] memory _candidates,
    uint256 _votingEndTime,
    bytes32 _merkleRoot
) {
    require(bytes(_title).length > 0, "Title is required");
    require(_candidates.length >= 2, "Invalid candidate count");
    require(_votingEndTime > block.timestamp, "Voting end time must be in the future");
    require(_merkleRoot != bytes32(0), "Merkle root is required");

    title = _title;
    votingEndTime = _votingEndTime;
    merkleRoot = _merkleRoot;
}
```

再写投票函数。它是合约最核心的函数。

```solidity
function vote(uint256 candidateIndex, bytes32[] calldata merkleProof) external {
    require(block.timestamp <= votingEndTime, "Voting has ended");
    require(candidateIndex < candidates.length, "Invalid candidate index");
    require(!voted[msg.sender], "Address has already voted");

    bytes32 leaf = keccak256(abi.encodePacked(msg.sender));
    require(MerkleProof.verify(merkleProof, merkleRoot, leaf), "Address is not eligible");

    voted[msg.sender] = true;
    voteCounts[candidateIndex] += 1;
}
```

按顺序理解：

1. 检查是否超过截止时间。
2. 检查候选项编号是否合法。
3. 检查当前钱包是否已经投过票。
4. 根据当前钱包地址生成 `leaf`。
5. 用 `merkleProof` 和 `merkleRoot` 校验白名单资格。
6. 标记已投票。
7. 给候选项加 1 票。

最后写读取函数。

```solidity
function getResults() external view returns (string[] memory names, uint256[] memory counts) {
    return (candidates, voteCounts);
}

function isVotingOpen() external view returns (bool) {
    return block.timestamp <= votingEndTime;
}

function hasAddressVoted(address voter) external view returns (bool) {
    return voted[voter];
}
```

这些函数不会修改链上状态，只负责给前端读取数据。

## 5. Merkle 白名单怎么工作

如果把所有选民地址都存进合约，成本高，也不方便扩展。本项目采用 Merkle Tree。

基本流程：

```text
选民地址 -> keccak256(address) -> leaf
多个 leaf -> Merkle Tree -> merkleRoot
部署合约时只保存 merkleRoot
投票时前端提交当前地址的 merkleProof
合约用 MerkleProof.verify() 校验资格
```

`scripts/generateWhitelist.ts` 做两件事：

- 读取 `data/voters.sample.json`。
- 输出 `apps/web/public/whitelist.json`。

`whitelist.json` 里包含：

- `merkleRoot`：部署合约时写入链上。
- `voters`：每个地址对应的 `leaf` 和 `proof`。

注意：如果你改了白名单地址，就会生成新的 `merkleRoot`。旧合约仍然保存旧 root，所以必须重新部署合约。

## 6. 部署脚本怎么工作

`scripts/deploy.ts` 负责把投票规则部署到链上。关键数据来自三个地方：

```text
data/candidates.sample.json       -> 候选项
apps/web/public/whitelist.json    -> Merkle Root
脚本当前时间                         -> votingEndTime
```

当前截止时间逻辑是：

```ts
const now = Math.floor(Date.now() / 1000);
const votingEndTime = now + 7 * 24 * 60 * 60;
```

意思是：从部署那一刻起，7 天后截止。

常见修改方式：

```ts
// 5 分钟后截止，适合演示
const votingEndTime = now + 5 * 60;

// 1 小时后截止
const votingEndTime = now + 60 * 60;

// 指定北京时间截止
const votingEndTime = Math.floor(new Date("2026-05-20T18:00:00+08:00").getTime() / 1000);
```

合约部署完成后，脚本生成：

```text
deployments/sepolia.json
```

这里保存合约地址、部署交易 Hash、Gas、部署时间等证据。

## 7. 前端怎么连接链上

前端主要分为两个 hook。

`useWallet.ts` 负责钱包：

- 检测是否安装 MetaMask。
- 调用 `eth_requestAccounts` 请求用户授权。
- 读取当前账户地址。
- 读取当前网络 Chain ID。
- 监听账户切换和网络切换。

`useVotingContract.ts` 负责合约：

- 读取 `deployment.json` 获取合约地址和 ABI。
- 读取 `whitelist.json` 查找当前账户的 proof。
- 调用 `getResults()` 读取候选项和票数。
- 调用 `isVotingOpen()` 判断投票是否开放。
- 调用 `hasAddressVoted(account)` 判断是否已投票。
- 调用 `vote(candidateIndex, proof)` 提交投票交易。

提交投票时，用户会看到 MetaMask 确认窗口。用户确认后，交易才会上链。

## 8. 从零重写的推荐顺序

不要一上来写前端。推荐顺序如下：

1. 写 `VotingSystem.sol`，只实现候选项、票数和投票。
2. 加上防重复投票。
3. 加上投票截止时间。
4. 加上 Merkle 白名单校验。
5. 写合约测试，确认每个 `require` 都能触发。
6. 写 `generateWhitelist.ts`，生成 root 和 proof。
7. 写 `deploy.ts`，把合约部署到本地链。
8. 写最简单前端，只连接钱包和显示账户。
9. 前端读取 `getResults()`。
10. 前端提交 `vote()`。
11. 加 ECharts 图表和链上证据面板。
12. 最后部署到 Sepolia。

这个顺序的好处是：每一步都能单独验证，不会同时被合约、脚本、前端和钱包问题卡住。

## 9. 运行流程

首次安装依赖：

```powershell
npm install
```

生成白名单：

```powershell
npm run generate:whitelist
```

编译合约：

```powershell
npm run compile
```

运行测试：

```powershell
npm test
```

启动前端：

```powershell
npm run web:dev
```

浏览器访问：

```text
http://localhost:5173/
```

## 10. Sepolia 部署流程

先创建 `.env`：

```powershell
Copy-Item .env.example .env
notepad .env
```

填写：

```env
SEPOLIA_RPC_URL=你的 Sepolia RPC 地址
DEPLOYER_PRIVATE_KEY=0x你的部署钱包私钥
REPORT_GAS=false
```

注意：`.env` 不能提交到 Git，私钥不能发给任何人。

部署流程：

```powershell
npm run generate:whitelist
npm run deploy:sepolia
npm run export:frontend -- --network sepolia
npm run web:dev
```

如果改了白名单、候选项或截止时间，都要重新走这组命令。原因是这些数据会影响链上的合约初始化状态。

## 11. 答辩时怎么讲

可以按这段讲：

> 本系统是一个基于 Solidity 智能合约和 Ethereum Sepolia 测试网的去中心化电子投票系统。传统中心化投票系统依赖服务器保存选票，存在单点故障和数据篡改风险。本系统把投票规则写入智能合约，由链上逻辑校验投票资格、重复投票和截止时间，投票结果通过 `getResults()` 公开读取。

继续讲 Merkle 白名单：

> 为了避免把完整选民列表写入链上，系统使用 Merkle Tree。链上只保存 `merkleRoot`，前端根据当前钱包地址提交对应的 `merkleProof`。合约通过 `MerkleProof.verify()` 校验地址是否属于白名单。这样既减少链上存储，又能保证资格验证可公开复现。

讲前端：

> 前端使用 React、Ethers.js 和 MetaMask。用户连接钱包后，前端读取链上候选项和票数，判断当前账户是否在白名单中。用户提交投票时，MetaMask 弹出签名确认，交易确认后合约更新票数，前端再刷新图表。

讲部署证据：

> 系统已部署到 Sepolia 测试网。页面展示了合约地址、部署交易 Hash、Gas Used 和部署时间。这些信息可以在 Etherscan 上核验，作为系统真实上链运行的证据。

## 12. 必须能解释的 6 个问题

**为什么智能合约不能随便改？**

因为合约部署到链上后，代码和状态由区块链网络维护，不能像普通服务器数据库那样直接修改。这正是投票规则可信的基础。

**为什么改白名单要重新部署？**

因为合约里保存的是部署时的 `merkleRoot`。白名单变化会导致新的 root，旧合约无法识别新 proof。

**为什么用 `votingEndTime`？**

投票截止规则必须由合约执行，不能只靠前端按钮禁用。前端可以被绕过，但合约 `require(block.timestamp <= votingEndTime)` 不能被绕过。

**为什么用 Unix 秒级时间戳？**

Solidity 里的 `block.timestamp` 是秒级时间戳。脚本也必须生成同样单位的时间，才能和合约比较。

**为什么别人投票不需要你的 `.env` 私钥？**

`.env` 私钥只用于部署合约。投票人用自己的 MetaMask 钱包签名交易，不需要知道部署者私钥。

**怎么看最终票数？**

前端调用合约的 `getResults()`，返回候选项和票数数组。每个候选项票数相加就是总票数。

## 13. 学习检查清单

- [ ] 能画出用户、MetaMask、前端、合约、Sepolia 的关系。
- [ ] 能说清楚 `vote(candidateIndex, merkleProof)` 的执行步骤。
- [ ] 能解释 Merkle Root 和 Merkle Proof 的关系。
- [ ] 能修改 `data/voters.sample.json` 并重新生成白名单。
- [ ] 能修改 `scripts/deploy.ts` 的投票截止时间。
- [ ] 能重新部署 Sepolia 合约并同步前端。
- [ ] 能在页面上找到合约地址、部署交易 Hash 和 Gas Used。
- [ ] 能用自己的话解释为什么这个系统比普通中心化投票更透明。
