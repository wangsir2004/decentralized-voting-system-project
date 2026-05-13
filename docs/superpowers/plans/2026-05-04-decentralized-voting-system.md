# 去中心化电子投票系统实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 从零实现一个可本地测试、可部署到 Sepolia、可用 MetaMask 演示、可支撑毕业论文的去中心化电子投票系统。

**架构：** 根目录使用 Hardhat 管理 Solidity 合约、测试、部署脚本和论文材料，`apps/web` 使用 React + Vite + TypeScript 构建 DApp。合约通过 Merkle Tree 白名单验证投票资格，前端读取部署产物、白名单 proof 和链上数据，完成钱包连接、投票提交和结果可视化。

**技术栈：** Solidity、Hardhat、OpenZeppelin、Merkle Tree、React、Vite、TypeScript、Ethers.js、ECharts、MetaMask、Sepolia。

---

## 文件结构

- 创建：`package.json`，根项目脚本和 Hardhat 依赖。
- 创建：`tsconfig.json`，根 TypeScript 配置。
- 创建：`hardhat.config.ts`，Hardhat 编译、网络、Gas reporter 配置。
- 创建：`.env.example`，Sepolia RPC、部署私钥和合约地址示例。
- 修改：`.gitignore`，补充 Hardhat、Vite、环境变量和部署临时文件忽略规则。
- 创建：`contracts/VotingSystem.sol`，投票智能合约。
- 创建：`test/VotingSystem.test.ts`，合约单元测试。
- 创建：`scripts/generateWhitelist.ts`，生成 Merkle Root 与 proof JSON。
- 创建：`scripts/deploy.ts`，部署合约并输出部署记录。
- 创建：`scripts/exportFrontendArtifact.ts`，把 ABI、地址、网络和白名单 proof 同步给前端。
- 创建：`data/voters.sample.json`，演示用选民地址样例。
- 创建：`data/candidates.sample.json`，演示用候选项样例。
- 创建：`deployments/.gitkeep`，保留部署记录目录。
- 创建：`docs/deployments/sepolia.md`，Sepolia 部署记录模板。
- 创建：`docs/thesis/algorithm-notes.md`，ECDSA、哈希、Merkle Tree 和 Gas 论文材料。
- 创建：`docs/testing/manual-test-checklist.md`，手工验收清单。
- 创建：`apps/web/package.json`，前端应用依赖和脚本。
- 创建：`apps/web/index.html`，Vite 入口。
- 创建：`apps/web/tsconfig.json`，前端 TypeScript 配置。
- 创建：`apps/web/vite.config.ts`，Vite 配置。
- 创建：`apps/web/src/main.tsx`，React 入口。
- 创建：`apps/web/src/App.tsx`，DApp 主页面。
- 创建：`apps/web/src/styles.css`，页面样式。
- 创建：`apps/web/src/types/ethereum.d.ts`，MetaMask 类型声明。
- 创建：`apps/web/src/contracts/deployment.ts`，前端读取部署配置。
- 创建：`apps/web/src/hooks/useWallet.ts`，钱包连接与网络状态。
- 创建：`apps/web/src/hooks/useVotingContract.ts`，合约读取和交易封装。
- 创建：`apps/web/src/components/WalletPanel.tsx`，钱包状态面板。
- 创建：`apps/web/src/components/VotingPanel.tsx`，投票交互面板。
- 创建：`apps/web/src/components/ResultsChart.tsx`，投票结果图表。
- 创建：`apps/web/public/deployment.json`，前端默认本地演示部署配置。
- 创建：`apps/web/public/whitelist.json`，前端默认白名单 proof 演示配置。

## 任务 1：初始化工程骨架

**文件：**
- 创建：`package.json`
- 创建：`tsconfig.json`
- 创建：`hardhat.config.ts`
- 创建：`.env.example`
- 修改：`.gitignore`
- 创建：`contracts/.gitkeep`
- 创建：`test/.gitkeep`
- 创建：`scripts/.gitkeep`
- 创建：`data/.gitkeep`
- 创建：`deployments/.gitkeep`

- [ ] **步骤 1：创建根项目配置**

写入 `package.json`：

```json
{
  "name": "decentralized-voting-system",
  "version": "0.1.0",
  "private": true,
  "description": "Solidity + Ethereum Sepolia decentralized voting graduation project.",
  "workspaces": [
    "apps/web"
  ],
  "scripts": {
    "compile": "hardhat compile",
    "test": "hardhat test",
    "test:gas": "REPORT_GAS=true hardhat test",
    "node": "hardhat node",
    "deploy:local": "hardhat run scripts/deploy.ts --network localhost",
    "deploy:sepolia": "hardhat run scripts/deploy.ts --network sepolia",
    "generate:whitelist": "hardhat run scripts/generateWhitelist.ts",
    "export:frontend": "hardhat run scripts/exportFrontendArtifact.ts",
    "web:dev": "npm run dev -w apps/web",
    "web:build": "npm run build -w apps/web",
    "web:preview": "npm run preview -w apps/web"
  },
  "devDependencies": {
    "@nomicfoundation/hardhat-toolbox": "^5.0.0",
    "@types/node": "^20.11.0",
    "dotenv": "^16.4.0",
    "hardhat": "^2.22.0",
    "hardhat-gas-reporter": "^1.0.10",
    "keccak256": "^1.0.6",
    "merkletreejs": "^0.4.0",
    "ts-node": "^10.9.2",
    "typescript": "^5.4.0"
  },
  "dependencies": {
    "@openzeppelin/contracts": "^5.0.0"
  }
}
```

- [ ] **步骤 2：创建 TypeScript 配置**

写入 `tsconfig.json`：

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "strict": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "skipLibCheck": true,
    "outDir": "dist"
  },
  "include": [
    "hardhat.config.ts",
    "scripts",
    "test"
  ]
}
```

- [ ] **步骤 3：创建 Hardhat 配置**

写入 `hardhat.config.ts`：

```ts
import { config as loadEnv } from "dotenv";
import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import "hardhat-gas-reporter";

loadEnv();

const sepoliaRpcUrl = process.env.SEPOLIA_RPC_URL || "";
const deployerPrivateKey = process.env.DEPLOYER_PRIVATE_KEY || "";

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.24",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    hardhat: {},
    localhost: {
      url: "http://127.0.0.1:8545"
    },
    sepolia: {
      url: sepoliaRpcUrl,
      accounts: deployerPrivateKey ? [deployerPrivateKey] : []
    }
  },
  gasReporter: {
    enabled: process.env.REPORT_GAS === "true",
    currency: "USD",
    showTimeSpent: true
  }
};

export default config;
```

- [ ] **步骤 4：创建环境变量示例**

写入 `.env.example`：

```bash
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
DEPLOYER_PRIVATE_KEY=0xyour_private_key_without_real_funds
REPORT_GAS=false
```

- [ ] **步骤 5：补充忽略规则**

确保 `.gitignore` 包含：

```gitignore
.superpowers/
任务书_converted.docx
任务书_extracted.txt

node_modules/
dist/
build/
coverage/
artifacts/
cache/
typechain-types/
deployments/*.local.json
deployments/*.tmp.json

.env
.env.*
!.env.example

apps/web/dist/
apps/web/node_modules/
```

- [ ] **步骤 6：创建空目录保留文件**

创建：

```text
contracts/.gitkeep
test/.gitkeep
scripts/.gitkeep
data/.gitkeep
deployments/.gitkeep
```

- [ ] **步骤 7：安装根依赖**

运行：

```bash
npm install
```

预期：生成 `package-lock.json`，`node_modules` 被 `.gitignore` 忽略。

- [ ] **步骤 8：验证 Hardhat 可运行**

运行：

```bash
npm run compile
```

预期：没有合约时也能完成 Hardhat 启动检查，若提示无合约可编译则可接受。

- [ ] **步骤 9：Commit**

```bash
git add .gitignore .env.example package.json package-lock.json tsconfig.json hardhat.config.ts contracts/.gitkeep test/.gitkeep scripts/.gitkeep data/.gitkeep deployments/.gitkeep
git commit -m "chore(工程): 初始化 Hardhat 项目骨架"
```

## 任务 2：准备白名单样例和 Merkle 生成脚本

**文件：**
- 创建：`data/voters.sample.json`
- 创建：`data/candidates.sample.json`
- 创建：`scripts/generateWhitelist.ts`
- 创建：`apps/web/public/.gitkeep`

- [ ] **步骤 1：创建候选项样例**

写入 `data/candidates.sample.json`：

```json
[
  "方案 A：区块链投票系统",
  "方案 B：传统中心化投票系统",
  "方案 C：混合式投票系统"
]
```

- [ ] **步骤 2：创建选民地址样例**

写入 `data/voters.sample.json`，地址使用 Hardhat 默认账户，方便本地演示：

```json
[
  "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
  "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
  "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
  "0x90F79bf6EB2c4f870365E785982E1f101E93b906"
]
```

- [ ] **步骤 3：编写白名单生成脚本**

写入 `scripts/generateWhitelist.ts`：

```ts
import fs from "fs";
import path from "path";
import { ethers } from "hardhat";
import { MerkleTree } from "merkletreejs";
import keccak256 from "keccak256";

type WhitelistEntry = {
  address: string;
  leaf: string;
  proof: string[];
};

async function main() {
  const votersPath = path.join(process.cwd(), "data", "voters.sample.json");
  const outputPath = path.join(process.cwd(), "apps", "web", "public", "whitelist.json");

  const voters = JSON.parse(fs.readFileSync(votersPath, "utf8")) as string[];
  const normalized = voters.map((address) => ethers.getAddress(address));
  const leaves = normalized.map((address) => ethers.keccak256(ethers.solidityPacked(["address"], [address])));
  const tree = new MerkleTree(leaves, keccak256, { sortPairs: true });
  const root = tree.getHexRoot();

  const entries: WhitelistEntry[] = normalized.map((address, index) => ({
    address,
    leaf: leaves[index],
    proof: tree.getHexProof(leaves[index])
  }));

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(
    outputPath,
    JSON.stringify({ merkleRoot: root, voters: entries }, null, 2) + "\n",
    "utf8"
  );

  console.log(`Merkle root: ${root}`);
  console.log(`Whitelist written to ${outputPath}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

- [ ] **步骤 4：创建前端 public 目录保留文件**

创建 `apps/web/public/.gitkeep`。

- [ ] **步骤 5：运行脚本验证输出**

运行：

```bash
npm run generate:whitelist
```

预期：输出 `Merkle root: 0x...`，并生成 `apps/web/public/whitelist.json`。

- [ ] **步骤 6：Commit**

```bash
git add data/voters.sample.json data/candidates.sample.json scripts/generateWhitelist.ts apps/web/public/.gitkeep apps/web/public/whitelist.json
git commit -m "feat(白名单): 添加 Merkle Tree 生成脚本"
```

## 任务 3：用 TDD 编写合约测试

**文件：**
- 创建：`test/VotingSystem.test.ts`
- 删除：`test/.gitkeep`

- [ ] **步骤 1：编写失败的合约测试**

写入 `test/VotingSystem.test.ts`：

```ts
import { expect } from "chai";
import { ethers, network } from "hardhat";
import { MerkleTree } from "merkletreejs";
import keccak256 from "keccak256";

function buildTree(addresses: string[]) {
  const normalized = addresses.map((address) => ethers.getAddress(address));
  const leaves = normalized.map((address) => ethers.keccak256(ethers.solidityPacked(["address"], [address])));
  const tree = new MerkleTree(leaves, keccak256, { sortPairs: true });

  return {
    root: tree.getHexRoot(),
    proofFor(address: string) {
      const leaf = ethers.keccak256(ethers.solidityPacked(["address"], [ethers.getAddress(address)]));
      return tree.getHexProof(leaf);
    }
  };
}

async function latestTimestamp() {
  const block = await ethers.provider.getBlock("latest");
  if (!block) throw new Error("latest block not found");
  return block.timestamp;
}

describe("VotingSystem", function () {
  async function deployFixture() {
    const [owner, voterA, voterB, outsider] = await ethers.getSigners();
    const tree = buildTree([voterA.address, voterB.address]);
    const endTime = (await latestTimestamp()) + 3600;
    const candidates = ["Alice", "Bob", "Carol"];

    const VotingSystem = await ethers.getContractFactory("VotingSystem");
    const voting = await VotingSystem.deploy("Graduation Vote", candidates, endTime, tree.root);

    return { voting, owner, voterA, voterB, outsider, tree, endTime, candidates };
  }

  it("initializes title, candidates, end time and merkle root", async function () {
    const { voting, endTime, candidates } = await deployFixture();

    expect(await voting.title()).to.equal("Graduation Vote");
    expect(await voting.votingEndTime()).to.equal(endTime);
    expect(await voting.getCandidates()).to.deep.equal(candidates);
    expect(await voting.isVotingOpen()).to.equal(true);
  });

  it("rejects deployment with fewer than two candidates", async function () {
    const [, voterA] = await ethers.getSigners();
    const tree = buildTree([voterA.address]);
    const endTime = (await latestTimestamp()) + 3600;
    const VotingSystem = await ethers.getContractFactory("VotingSystem");

    await expect(VotingSystem.deploy("Invalid Vote", ["Only One"], endTime, tree.root))
      .to.be.revertedWith("Invalid candidate count");
  });

  it("rejects deployment when end time is not in the future", async function () {
    const [, voterA] = await ethers.getSigners();
    const tree = buildTree([voterA.address]);
    const endTime = await latestTimestamp();
    const VotingSystem = await ethers.getContractFactory("VotingSystem");

    await expect(VotingSystem.deploy("Invalid Vote", ["Alice", "Bob"], endTime, tree.root))
      .to.be.revertedWith("Voting end time must be in the future");
  });

  it("allows a whitelisted voter to vote once", async function () {
    const { voting, voterA, tree } = await deployFixture();

    await expect(voting.connect(voterA).vote(1, tree.proofFor(voterA.address)))
      .to.emit(voting, "VoteCast")
      .withArgs(voterA.address, 1);

    expect(await voting.hasAddressVoted(voterA.address)).to.equal(true);
    const [, counts] = await voting.getResults();
    expect(counts[1]).to.equal(1);
  });

  it("rejects a non-whitelisted voter", async function () {
    const { voting, outsider } = await deployFixture();

    await expect(voting.connect(outsider).vote(0, [])).to.be.revertedWith("Address is not eligible");
  });

  it("rejects duplicate voting", async function () {
    const { voting, voterA, tree } = await deployFixture();
    const proof = tree.proofFor(voterA.address);

    await voting.connect(voterA).vote(0, proof);
    await expect(voting.connect(voterA).vote(1, proof)).to.be.revertedWith("Address has already voted");
  });

  it("rejects invalid candidate index", async function () {
    const { voting, voterA, tree } = await deployFixture();

    await expect(voting.connect(voterA).vote(99, tree.proofFor(voterA.address)))
      .to.be.revertedWith("Invalid candidate index");
  });

  it("rejects voting after the end time", async function () {
    const { voting, voterA, tree, endTime } = await deployFixture();

    await network.provider.send("evm_setNextBlockTimestamp", [endTime + 1]);
    await network.provider.send("evm_mine");

    await expect(voting.connect(voterA).vote(0, tree.proofFor(voterA.address)))
      .to.be.revertedWith("Voting has ended");
  });

  it("returns candidates and counts together", async function () {
    const { voting, voterA, voterB, tree, candidates } = await deployFixture();

    await voting.connect(voterA).vote(0, tree.proofFor(voterA.address));
    await voting.connect(voterB).vote(2, tree.proofFor(voterB.address));

    const [names, counts] = await voting.getResults();
    expect(names).to.deep.equal(candidates);
    expect(counts.map((count: bigint) => Number(count))).to.deep.equal([1, 0, 1]);
  });
});
```

- [ ] **步骤 2：运行测试验证失败**

运行：

```bash
npm test
```

预期：FAIL，报错包含 `HH700: Artifact for contract "VotingSystem" not found` 或 `Cannot find module`，因为合约尚未实现。

- [ ] **步骤 3：Commit**

```bash
git add test/VotingSystem.test.ts
git rm test/.gitkeep
git commit -m "test(合约): 添加投票系统核心测试"
```

## 任务 4：实现 VotingSystem 智能合约

**文件：**
- 创建：`contracts/VotingSystem.sol`
- 删除：`contracts/.gitkeep`

- [ ] **步骤 1：编写最小合约实现**

写入 `contracts/VotingSystem.sol`：

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {MerkleProof} from "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract VotingSystem is Ownable {
    string public title;
    uint256 public votingEndTime;
    bytes32 public merkleRoot;

    string[] private candidates;
    uint256[] private voteCounts;
    mapping(address => bool) private voted;

    event VoteCreated(string title, uint256 votingEndTime, bytes32 merkleRoot);
    event VoteCast(address indexed voter, uint256 indexed candidateIndex);

    constructor(
        string memory _title,
        string[] memory _candidates,
        uint256 _votingEndTime,
        bytes32 _merkleRoot
    ) Ownable(msg.sender) {
        require(bytes(_title).length > 0, "Title is required");
        require(_candidates.length >= 2, "Invalid candidate count");
        require(_votingEndTime > block.timestamp, "Voting end time must be in the future");
        require(_merkleRoot != bytes32(0), "Merkle root is required");

        title = _title;
        votingEndTime = _votingEndTime;
        merkleRoot = _merkleRoot;

        for (uint256 i = 0; i < _candidates.length; i++) {
            require(bytes(_candidates[i]).length > 0, "Candidate name is required");
            candidates.push(_candidates[i]);
            voteCounts.push(0);
        }

        emit VoteCreated(_title, _votingEndTime, _merkleRoot);
    }

    function vote(uint256 candidateIndex, bytes32[] calldata merkleProof) external {
        require(block.timestamp <= votingEndTime, "Voting has ended");
        require(candidateIndex < candidates.length, "Invalid candidate index");
        require(!voted[msg.sender], "Address has already voted");

        bytes32 leaf = keccak256(abi.encodePacked(msg.sender));
        require(MerkleProof.verify(merkleProof, merkleRoot, leaf), "Address is not eligible");

        voted[msg.sender] = true;
        voteCounts[candidateIndex] += 1;

        emit VoteCast(msg.sender, candidateIndex);
    }

    function getCandidates() external view returns (string[] memory) {
        return candidates;
    }

    function getResults() external view returns (string[] memory names, uint256[] memory counts) {
        return (candidates, voteCounts);
    }

    function isVotingOpen() external view returns (bool) {
        return block.timestamp <= votingEndTime;
    }

    function hasAddressVoted(address voter) external view returns (bool) {
        return voted[voter];
    }

    function candidateCount() external view returns (uint256) {
        return candidates.length;
    }
}
```

- [ ] **步骤 2：运行编译**

运行：

```bash
npm run compile
```

预期：PASS，生成 `artifacts/` 和 `typechain-types/`。

- [ ] **步骤 3：运行合约测试**

运行：

```bash
npm test
```

预期：所有 `VotingSystem` 测试通过。

- [ ] **步骤 4：运行 Gas 报告**

运行：

```bash
npm run test:gas
```

预期：测试通过，输出部署和 `vote` 方法 Gas 数据。记录关键数字到后续 `docs/thesis/algorithm-notes.md`。

- [ ] **步骤 5：Commit**

```bash
git add contracts/VotingSystem.sol
git rm contracts/.gitkeep
git commit -m "feat(合约): 实现 Merkle 白名单投票合约"
```

## 任务 5：实现部署脚本和前端部署产物导出

**文件：**
- 创建：`scripts/deploy.ts`
- 创建：`scripts/exportFrontendArtifact.ts`
- 创建：`docs/deployments/sepolia.md`
- 修改：`deployments/.gitkeep`

- [ ] **步骤 1：编写部署脚本**

写入 `scripts/deploy.ts`：

```ts
import fs from "fs";
import path from "path";
import { ethers, network } from "hardhat";

type WhitelistFile = {
  merkleRoot: string;
};

async function main() {
  const whitelistPath = path.join(process.cwd(), "apps", "web", "public", "whitelist.json");
  const candidatesPath = path.join(process.cwd(), "data", "candidates.sample.json");

  const whitelist = JSON.parse(fs.readFileSync(whitelistPath, "utf8")) as WhitelistFile;
  const candidates = JSON.parse(fs.readFileSync(candidatesPath, "utf8")) as string[];
  const now = Math.floor(Date.now() / 1000);
  const votingEndTime = now + 7 * 24 * 60 * 60;
  const title = "Graduation Design Voting";

  const VotingSystem = await ethers.getContractFactory("VotingSystem");
  const voting = await VotingSystem.deploy(title, candidates, votingEndTime, whitelist.merkleRoot);
  await voting.waitForDeployment();

  const address = await voting.getAddress();
  const deploymentTx = voting.deploymentTransaction();
  const receipt = deploymentTx ? await deploymentTx.wait() : null;

  const output = {
    network: network.name,
    chainId: Number((await ethers.provider.getNetwork()).chainId),
    contractName: "VotingSystem",
    address,
    title,
    candidates,
    votingEndTime,
    merkleRoot: whitelist.merkleRoot,
    deploymentTransactionHash: deploymentTx?.hash || "",
    deploymentGasUsed: receipt?.gasUsed?.toString() || "",
    deployedAt: new Date().toISOString()
  };

  fs.mkdirSync(path.join(process.cwd(), "deployments"), { recursive: true });
  const outputPath = path.join(process.cwd(), "deployments", `${network.name}.json`);
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2) + "\n", "utf8");

  console.log(`VotingSystem deployed to ${address}`);
  console.log(`Deployment saved to ${outputPath}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

- [ ] **步骤 2：编写前端导出脚本**

写入 `scripts/exportFrontendArtifact.ts`：

```ts
import fs from "fs";
import path from "path";
import { network } from "hardhat";

async function main() {
  const artifactPath = path.join(process.cwd(), "artifacts", "contracts", "VotingSystem.sol", "VotingSystem.json");
  const deploymentPath = path.join(process.cwd(), "deployments", `${network.name}.json`);
  const publicDir = path.join(process.cwd(), "apps", "web", "public");
  const outputPath = path.join(publicDir, "deployment.json");

  const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));
  const deployment = JSON.parse(fs.readFileSync(deploymentPath, "utf8"));

  fs.mkdirSync(publicDir, { recursive: true });
  fs.writeFileSync(
    outputPath,
    JSON.stringify(
      {
        ...deployment,
        abi: artifact.abi
      },
      null,
      2
    ) + "\n",
    "utf8"
  );

  console.log(`Frontend deployment artifact written to ${outputPath}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

- [ ] **步骤 3：创建 Sepolia 部署记录模板**

写入 `docs/deployments/sepolia.md`：

```markdown
# Sepolia 部署记录

## 基本信息

| 项目 | 内容 |
| --- | --- |
| 网络 | Sepolia |
| 合约 | VotingSystem |
| 合约地址 | 执行 Sepolia 部署后记录 `deployments/sepolia.json.address` |
| 部署交易 Hash | 执行 Sepolia 部署后记录 `deploymentTransactionHash` |
| 部署账户 | 执行 Sepolia 部署后记录部署钱包地址 |
| 部署时间 | 执行 Sepolia 部署后记录 `deployedAt` |
| Merkle Root | 执行 Sepolia 部署后记录 `merkleRoot` |

## Gas 记录

| 操作 | Gas Used | 交易 Hash | 说明 |
| --- | ---: | --- | --- |
| 部署合约 | 记录部署回执中的 Gas Used | 记录部署交易 Hash | 初始化标题、候选项、截止时间和 Merkle Root |
| 成功投票 | 记录投票回执中的 Gas Used | 记录成功投票交易 Hash | 白名单账户首次投票 |
| 重复投票失败 | 记录失败交易或本地测试结果 | 记录失败交易 Hash 或测试名称 | 合约回滚，不计入有效票数 |

## ABI 与前端同步

部署后运行：

```bash
npm run export:frontend -- --network sepolia
```
```

- [ ] **步骤 4：本地部署验证**

终端 1 运行：

```bash
npm run node
```

终端 2 运行：

```bash
npm run generate:whitelist
npm run deploy:local
npm run export:frontend -- --network localhost
```

预期：生成 `deployments/localhost.json` 和 `apps/web/public/deployment.json`。

- [ ] **步骤 5：Commit**

```bash
git add scripts/deploy.ts scripts/exportFrontendArtifact.ts docs/deployments/sepolia.md deployments/.gitkeep apps/web/public/deployment.json
git commit -m "feat(部署): 添加合约部署与前端产物导出"
```

## 任务 6：初始化 React DApp 前端

**文件：**
- 创建：`apps/web/package.json`
- 创建：`apps/web/index.html`
- 创建：`apps/web/tsconfig.json`
- 创建：`apps/web/vite.config.ts`
- 创建：`apps/web/src/main.tsx`
- 创建：`apps/web/src/App.tsx`
- 创建：`apps/web/src/styles.css`
- 创建：`apps/web/src/types/ethereum.d.ts`

- [ ] **步骤 1：创建前端 package**

写入 `apps/web/package.json`：

```json
{
  "name": "@decentralized-voting-system/web",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "echarts": "^5.5.0",
    "ethers": "^6.11.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "vite": "^5.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.4.0"
  }
}
```

- [ ] **步骤 2：创建 HTML 入口**

写入 `apps/web/index.html`：

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>去中心化电子投票系统</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **步骤 3：创建前端 TypeScript 配置**

写入 `apps/web/tsconfig.json`：

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["DOM", "DOM.Iterable", "ES2020"],
    "allowJs": false,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "module": "ESNext",
    "moduleResolution": "Node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"],
  "references": []
}
```

- [ ] **步骤 4：创建 Vite 配置**

写入 `apps/web/vite.config.ts`：

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173
  }
});
```

- [ ] **步骤 5：创建 React 入口**

写入 `apps/web/src/main.tsx`：

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

- [ ] **步骤 6：创建临时 App**

写入 `apps/web/src/App.tsx`：

```tsx
export default function App() {
  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">Ethereum Sepolia DApp</p>
        <h1>去中心化电子投票系统</h1>
        <p>正在连接智能合约、钱包与链上投票结果。</p>
      </section>
    </main>
  );
}
```

- [ ] **步骤 7：创建基础样式**

写入 `apps/web/src/styles.css`：

```css
:root {
  color: #18202f;
  background: #eef3f7;
  font-family: "Noto Sans SC", "Microsoft YaHei", sans-serif;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-width: 320px;
}

button,
input {
  font: inherit;
}

.app-shell {
  min-height: 100vh;
  padding: 32px;
  background:
    linear-gradient(135deg, rgba(31, 90, 109, 0.16), transparent 34%),
    linear-gradient(225deg, rgba(177, 69, 51, 0.12), transparent 38%),
    #eef3f7;
}

.hero {
  max-width: 1120px;
  margin: 0 auto;
  padding: 56px 0 24px;
}

.eyebrow {
  margin: 0 0 12px;
  color: #3c6f7d;
  font-weight: 700;
}

h1 {
  margin: 0 0 16px;
  font-size: 44px;
  line-height: 1.15;
}

@media (max-width: 720px) {
  .app-shell {
    padding: 20px;
  }

  h1 {
    font-size: 32px;
  }
}
```

- [ ] **步骤 8：声明 MetaMask 类型**

写入 `apps/web/src/types/ethereum.d.ts`：

```ts
import type { Eip1193Provider } from "ethers";

declare global {
  interface Window {
    ethereum?: Eip1193Provider & {
      isMetaMask?: boolean;
      on?: (event: string, handler: (...args: unknown[]) => void) => void;
      removeListener?: (event: string, handler: (...args: unknown[]) => void) => void;
    };
  }
}

export {};
```

- [ ] **步骤 9：安装前端依赖并构建**

运行：

```bash
npm install
npm run web:build
```

预期：前端 TypeScript 检查和 Vite 构建通过。

- [ ] **步骤 10：Commit**

```bash
git add apps/web package-lock.json
git commit -m "feat(前端): 初始化 React DApp 应用"
```

## 任务 7：实现钱包连接与部署配置读取

**文件：**
- 创建：`apps/web/src/contracts/deployment.ts`
- 创建：`apps/web/src/hooks/useWallet.ts`
- 创建：`apps/web/src/components/WalletPanel.tsx`
- 修改：`apps/web/src/App.tsx`

- [ ] **步骤 1：创建部署配置读取模块**

写入 `apps/web/src/contracts/deployment.ts`：

```ts
export type DeploymentConfig = {
  network: string;
  chainId: number;
  contractName: string;
  address: string;
  title: string;
  candidates: string[];
  votingEndTime: number;
  merkleRoot: string;
  deploymentTransactionHash: string;
  deploymentGasUsed: string;
  deployedAt: string;
  abi: unknown[];
};

export async function loadDeployment(): Promise<DeploymentConfig> {
  const response = await fetch("/deployment.json");
  if (!response.ok) {
    throw new Error("无法读取合约部署配置");
  }

  return response.json() as Promise<DeploymentConfig>;
}
```

- [ ] **步骤 2：创建钱包 Hook**

写入 `apps/web/src/hooks/useWallet.ts`：

```ts
import { useEffect, useState } from "react";
import { BrowserProvider } from "ethers";

export type WalletState = {
  account: string;
  chainId: number | null;
  isConnecting: boolean;
  error: string;
};

const initialState: WalletState = {
  account: "",
  chainId: null,
  isConnecting: false,
  error: ""
};

export function useWallet() {
  const [state, setState] = useState<WalletState>(initialState);

  async function refreshAccount() {
    if (!window.ethereum) {
      setState((current) => ({ ...current, error: "未检测到 MetaMask，请先安装钱包。" }));
      return;
    }

    const provider = new BrowserProvider(window.ethereum);
    const accounts = await provider.send("eth_accounts", []);
    const network = await provider.getNetwork();

    setState((current) => ({
      ...current,
      account: accounts[0] || "",
      chainId: Number(network.chainId),
      error: ""
    }));
  }

  async function connect() {
    if (!window.ethereum) {
      setState((current) => ({ ...current, error: "未检测到 MetaMask，请先安装钱包。" }));
      return;
    }

    setState((current) => ({ ...current, isConnecting: true, error: "" }));

    try {
      const provider = new BrowserProvider(window.ethereum);
      const accounts = await provider.send("eth_requestAccounts", []);
      const network = await provider.getNetwork();

      setState({
        account: accounts[0] || "",
        chainId: Number(network.chainId),
        isConnecting: false,
        error: ""
      });
    } catch (error) {
      setState((current) => ({
        ...current,
        isConnecting: false,
        error: error instanceof Error ? error.message : "连接钱包失败。"
      }));
    }
  }

  useEffect(() => {
    void refreshAccount();

    const handleAccountsChanged = () => void refreshAccount();
    const handleChainChanged = () => void refreshAccount();

    window.ethereum?.on?.("accountsChanged", handleAccountsChanged);
    window.ethereum?.on?.("chainChanged", handleChainChanged);

    return () => {
      window.ethereum?.removeListener?.("accountsChanged", handleAccountsChanged);
      window.ethereum?.removeListener?.("chainChanged", handleChainChanged);
    };
  }, []);

  return {
    ...state,
    connect
  };
}
```

- [ ] **步骤 3：创建钱包面板**

写入 `apps/web/src/components/WalletPanel.tsx`：

```tsx
type WalletPanelProps = {
  account: string;
  chainId: number | null;
  expectedChainId: number | null;
  isConnecting: boolean;
  error: string;
  onConnect: () => void;
};

function shorten(address: string) {
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

export function WalletPanel({
  account,
  chainId,
  expectedChainId,
  isConnecting,
  error,
  onConnect
}: WalletPanelProps) {
  const wrongNetwork = Boolean(account && chainId && expectedChainId && chainId !== expectedChainId);

  return (
    <section className="panel wallet-panel">
      <div>
        <p className="panel-label">钱包状态</p>
        <h2>{account ? shorten(account) : "未连接钱包"}</h2>
        <p>当前网络：{chainId ?? "未知"}，目标网络：{expectedChainId ?? "读取中"}</p>
      </div>
      <button className="primary-button" onClick={onConnect} disabled={isConnecting}>
        {account ? "刷新钱包" : isConnecting ? "连接中..." : "连接 MetaMask"}
      </button>
      {wrongNetwork && <p className="error-text">请切换到部署配置对应的网络。</p>}
      {error && <p className="error-text">{error}</p>}
    </section>
  );
}
```

- [ ] **步骤 4：接入 App**

修改 `apps/web/src/App.tsx`：

```tsx
import { useEffect, useState } from "react";
import { WalletPanel } from "./components/WalletPanel";
import { DeploymentConfig, loadDeployment } from "./contracts/deployment";
import { useWallet } from "./hooks/useWallet";

export default function App() {
  const wallet = useWallet();
  const [deployment, setDeployment] = useState<DeploymentConfig | null>(null);
  const [deploymentError, setDeploymentError] = useState("");

  useEffect(() => {
    loadDeployment()
      .then(setDeployment)
      .catch((error) => setDeploymentError(error instanceof Error ? error.message : "读取部署配置失败。"));
  }, []);

  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">Ethereum Sepolia DApp</p>
        <h1>去中心化电子投票系统</h1>
        <p>连接钱包，验证白名单资格，并将投票结果写入智能合约。</p>
      </section>

      <div className="dashboard">
        <WalletPanel
          account={wallet.account}
          chainId={wallet.chainId}
          expectedChainId={deployment?.chainId ?? null}
          isConnecting={wallet.isConnecting}
          error={wallet.error || deploymentError}
          onConnect={wallet.connect}
        />
      </div>
    </main>
  );
}
```

- [ ] **步骤 5：补充样式**

追加到 `apps/web/src/styles.css`：

```css
.dashboard {
  max-width: 1120px;
  margin: 0 auto;
  display: grid;
  gap: 18px;
}

.panel {
  border: 1px solid rgba(72, 91, 111, 0.18);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.86);
  padding: 22px;
  box-shadow: 0 18px 50px rgba(36, 52, 71, 0.08);
}

.panel-label {
  margin: 0 0 6px;
  color: #5e7783;
  font-size: 13px;
  font-weight: 700;
}

.wallet-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  flex-wrap: wrap;
}

.primary-button {
  border: 0;
  border-radius: 6px;
  background: #1f5a6d;
  color: white;
  cursor: pointer;
  padding: 12px 18px;
  font-weight: 700;
}

.primary-button:disabled {
  cursor: not-allowed;
  opacity: 0.62;
}

.error-text {
  width: 100%;
  color: #b14533;
  font-weight: 700;
}
```

- [ ] **步骤 6：构建验证**

运行：

```bash
npm run web:build
```

预期：PASS。

- [ ] **步骤 7：Commit**

```bash
git add apps/web/src
git commit -m "feat(钱包): 添加 MetaMask 连接与部署配置读取"
```

## 任务 8：实现合约读取、投票提交和结果可视化

**文件：**
- 创建：`apps/web/src/hooks/useVotingContract.ts`
- 创建：`apps/web/src/components/VotingPanel.tsx`
- 创建：`apps/web/src/components/ResultsChart.tsx`
- 修改：`apps/web/src/App.tsx`
- 修改：`apps/web/src/styles.css`

- [ ] **步骤 1：实现合约 Hook**

写入 `apps/web/src/hooks/useVotingContract.ts`：

```ts
import { useCallback, useEffect, useState } from "react";
import { BrowserProvider, Contract } from "ethers";
import type { DeploymentConfig } from "../contracts/deployment";

type WhitelistFile = {
  merkleRoot: string;
  voters: Array<{
    address: string;
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
  txHash: string;
  isLoading: boolean;
  isSubmitting: boolean;
  error: string;
};

const initialState: VotingState = {
  candidates: [],
  counts: [],
  isOpen: false,
  hasVoted: false,
  eligible: false,
  proof: [],
  txHash: "",
  isLoading: false,
  isSubmitting: false,
  error: ""
};

export function useVotingContract(deployment: DeploymentConfig | null, account: string) {
  const [state, setState] = useState<VotingState>(initialState);

  const refresh = useCallback(async () => {
    if (!deployment || !window.ethereum) return;

    setState((current) => ({ ...current, isLoading: true, error: "" }));

    try {
      const provider = new BrowserProvider(window.ethereum);
      const contract = new Contract(deployment.address, deployment.abi, provider);
      const whitelistResponse = await fetch("/whitelist.json");
      const whitelist = (await whitelistResponse.json()) as WhitelistFile;
      const entry = whitelist.voters.find((item) => item.address.toLowerCase() === account.toLowerCase());
      const [names, rawCounts] = await contract.getResults();
      const isOpen = await contract.isVotingOpen();
      const hasVoted = account ? await contract.hasAddressVoted(account) : false;

      setState((current) => ({
        ...current,
        candidates: [...names],
        counts: rawCounts.map((count: bigint) => Number(count)),
        isOpen,
        hasVoted,
        eligible: Boolean(entry),
        proof: entry?.proof ?? [],
        isLoading: false,
        error: ""
      }));
    } catch (error) {
      setState((current) => ({
        ...current,
        isLoading: false,
        error: error instanceof Error ? error.message : "读取投票数据失败。"
      }));
    }
  }, [deployment, account]);

  async function submitVote(candidateIndex: number) {
    if (!deployment || !window.ethereum) return;

    setState((current) => ({ ...current, isSubmitting: true, error: "", txHash: "" }));

    try {
      const provider = new BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const contract = new Contract(deployment.address, deployment.abi, signer);
      const tx = await contract.vote(candidateIndex, state.proof);

      setState((current) => ({ ...current, txHash: tx.hash }));
      await tx.wait();
      await refresh();
      setState((current) => ({ ...current, isSubmitting: false }));
    } catch (error) {
      setState((current) => ({
        ...current,
        isSubmitting: false,
        error: error instanceof Error ? error.message : "提交投票失败。"
      }));
    }
  }

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return {
    ...state,
    refresh,
    submitVote
  };
}
```

- [ ] **步骤 2：实现投票面板**

写入 `apps/web/src/components/VotingPanel.tsx`：

```tsx
import { useState } from "react";

type VotingPanelProps = {
  title: string;
  votingEndTime: number;
  account: string;
  candidates: string[];
  isOpen: boolean;
  eligible: boolean;
  hasVoted: boolean;
  isSubmitting: boolean;
  txHash: string;
  error: string;
  onSubmit: (candidateIndex: number) => void;
};

export function VotingPanel({
  title,
  votingEndTime,
  account,
  candidates,
  isOpen,
  eligible,
  hasVoted,
  isSubmitting,
  txHash,
  error,
  onSubmit
}: VotingPanelProps) {
  const [selected, setSelected] = useState(0);
  const disabled = !account || !isOpen || !eligible || hasVoted || isSubmitting;

  return (
    <section className="panel voting-panel">
      <p className="panel-label">链上投票</p>
      <h2>{title}</h2>
      <p>截止时间：{new Date(votingEndTime * 1000).toLocaleString()}</p>
      <div className="status-grid">
        <span>{isOpen ? "投票开放中" : "投票已截止"}</span>
        <span>{eligible ? "当前账户在白名单中" : "当前账户不在白名单中"}</span>
        <span>{hasVoted ? "当前账户已投票" : "当前账户未投票"}</span>
      </div>

      <div className="candidate-list">
        {candidates.map((candidate, index) => (
          <label className="candidate-item" key={candidate}>
            <input
              type="radio"
              name="candidate"
              checked={selected === index}
              onChange={() => setSelected(index)}
            />
            <span>{candidate}</span>
          </label>
        ))}
      </div>

      <button className="primary-button" disabled={disabled} onClick={() => onSubmit(selected)}>
        {isSubmitting ? "交易确认中..." : "提交投票"}
      </button>

      {txHash && <p className="hint-text">交易 Hash：{txHash}</p>}
      {error && <p className="error-text">{error}</p>}
    </section>
  );
}
```

- [ ] **步骤 3：实现图表组件**

写入 `apps/web/src/components/ResultsChart.tsx`：

```tsx
import { useEffect, useRef } from "react";
import * as echarts from "echarts";

type ResultsChartProps = {
  candidates: string[];
  counts: number[];
};

export function ResultsChart({ candidates, counts }: ResultsChartProps) {
  const chartRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    const chart = echarts.init(chartRef.current);
    chart.setOption({
      tooltip: {},
      grid: { left: 24, right: 24, top: 32, bottom: 32, containLabel: true },
      xAxis: { type: "category", data: candidates },
      yAxis: { type: "value", minInterval: 1 },
      series: [
        {
          type: "bar",
          data: counts,
          itemStyle: { color: "#1f5a6d" },
          label: { show: true, position: "top" }
        }
      ]
    });

    const handleResize = () => chart.resize();
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.dispose();
    };
  }, [candidates, counts]);

  return (
    <section className="panel">
      <p className="panel-label">结果可视化</p>
      <h2>实时投票结果</h2>
      <div className="chart" ref={chartRef} />
    </section>
  );
}
```

- [ ] **步骤 4：接入 App**

修改 `apps/web/src/App.tsx`：

```tsx
import { useEffect, useState } from "react";
import { ResultsChart } from "./components/ResultsChart";
import { VotingPanel } from "./components/VotingPanel";
import { WalletPanel } from "./components/WalletPanel";
import { DeploymentConfig, loadDeployment } from "./contracts/deployment";
import { useWallet } from "./hooks/useWallet";
import { useVotingContract } from "./hooks/useVotingContract";

export default function App() {
  const wallet = useWallet();
  const [deployment, setDeployment] = useState<DeploymentConfig | null>(null);
  const [deploymentError, setDeploymentError] = useState("");
  const voting = useVotingContract(deployment, wallet.account);

  useEffect(() => {
    loadDeployment()
      .then(setDeployment)
      .catch((error) => setDeploymentError(error instanceof Error ? error.message : "读取部署配置失败。"));
  }, []);

  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">Ethereum Sepolia DApp</p>
        <h1>去中心化电子投票系统</h1>
        <p>连接钱包，验证白名单资格，并将投票结果写入智能合约。</p>
      </section>

      <div className="dashboard">
        <WalletPanel
          account={wallet.account}
          chainId={wallet.chainId}
          expectedChainId={deployment?.chainId ?? null}
          isConnecting={wallet.isConnecting}
          error={wallet.error || deploymentError}
          onConnect={wallet.connect}
        />

        {deployment && (
          <>
            <VotingPanel
              title={deployment.title}
              votingEndTime={deployment.votingEndTime}
              account={wallet.account}
              candidates={voting.candidates}
              isOpen={voting.isOpen}
              eligible={voting.eligible}
              hasVoted={voting.hasVoted}
              isSubmitting={voting.isSubmitting}
              txHash={voting.txHash}
              error={voting.error}
              onSubmit={voting.submitVote}
            />
            <ResultsChart candidates={voting.candidates} counts={voting.counts} />
          </>
        )}
      </div>
    </main>
  );
}
```

- [ ] **步骤 5：补充样式**

追加到 `apps/web/src/styles.css`：

```css
.voting-panel {
  display: grid;
  gap: 14px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.status-grid span,
.candidate-item {
  border: 1px solid rgba(72, 91, 111, 0.16);
  border-radius: 6px;
  background: #f8fbfd;
  padding: 12px;
}

.candidate-list {
  display: grid;
  gap: 10px;
}

.candidate-item {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.hint-text {
  color: #355d43;
  word-break: break-all;
}

.chart {
  width: 100%;
  height: 360px;
}

@media (max-width: 720px) {
  .status-grid {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **步骤 6：构建验证**

运行：

```bash
npm run web:build
```

预期：PASS。

- [ ] **步骤 7：Commit**

```bash
git add apps/web/src
git commit -m "feat(投票): 实现前端投票和结果可视化"
```

## 任务 9：补充论文材料、测试清单和运行说明

**文件：**
- 修改：`README.md`
- 创建：`docs/thesis/algorithm-notes.md`
- 创建：`docs/testing/manual-test-checklist.md`

- [ ] **步骤 1：补充 README 运行说明**

追加到 `README.md`：

```markdown
## 本地开发

### 安装依赖

```bash
npm install
```

### 生成白名单

```bash
npm run generate:whitelist
```

### 编译与测试合约

```bash
npm run compile
npm test
npm run test:gas
```

### 本地部署

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

## Sepolia 部署

1. 复制 `.env.example` 为 `.env`。
2. 填写 `SEPOLIA_RPC_URL` 和 `DEPLOYER_PRIVATE_KEY`。
3. 确保部署账户有 Sepolia 测试 ETH。
4. 运行：

```bash
npm run generate:whitelist
npm run deploy:sepolia
npm run export:frontend -- --network sepolia
```
```

- [ ] **步骤 2：创建论文算法笔记**

写入 `docs/thesis/algorithm-notes.md`：

```markdown
# 算法与安全分析笔记

## ECDSA 与地址伪匿名

Ethereum 账户由私钥、公钥和地址构成。用户通过 MetaMask 对交易签名，合约通过 `msg.sender` 获取交易发起地址。系统不保存真实身份，只保存地址投票状态，因此实现的是地址层面的伪匿名。

局限性：链上交易公开可查，若地址与真实身份在链下发生关联，则仍可能泄露投票行为。

## 哈希与 Merkle Tree

选民地址先经过：

```text
leaf = keccak256(abi.encodePacked(voterAddress))
```

所有叶子节点构成 Merkle Tree。合约只保存 `merkleRoot`，投票时用户提交 Merkle Proof。若选民数量为 `n`，proof 长度约为 `log2(n)`，验证复杂度为 `O(log n)`，优于在链上遍历完整选民列表的 `O(n)`。

## 防重复投票

合约使用：

```solidity
mapping(address => bool) private voted;
```

投票成功后立刻设置 `voted[msg.sender] = true`，同一地址再次投票会被回滚。

## 重入攻击分析

本合约不接收 ETH，不向外部地址转账，也不调用不可信外部合约。核心 `vote` 流程只修改内部状态并发出事件，因此不存在典型资金重入路径。

## Gas 记录

| 操作 | Gas Used | 说明 |
| --- | ---: | --- |
| 部署合约 | 从 `npm run test:gas` 输出中记录 | 初始化候选项和 Merkle Root |
| 成功投票 | 从 `npm run test:gas` 输出中记录 | 白名单账户首次投票 |
| 读取结果 | 记录为 view 方法 | view 方法，本地调用不消耗链上 Gas |
```

- [ ] **步骤 3：创建手工测试清单**

写入 `docs/testing/manual-test-checklist.md`：

```markdown
# 手工测试清单

## 钱包与网络

- [ ] 未安装 MetaMask 时显示明确提示。
- [ ] 未连接钱包时显示「未连接钱包」。
- [ ] 连接钱包后显示缩略地址。
- [ ] 网络不匹配时显示切换网络提示。

## 投票流程

- [ ] 白名单账户可以看到「当前账户在白名单中」。
- [ ] 非白名单账户无法提交投票。
- [ ] 白名单账户可以提交一次投票。
- [ ] 投票成功后显示交易 Hash。
- [ ] 投票成功后图表票数刷新。
- [ ] 同一账户第二次投票被拒绝。
- [ ] 投票截止时间后按钮不可用或交易被合约拒绝。

## 论文证据

- [ ] 保存 Sepolia 合约地址。
- [ ] 保存部署交易 Hash。
- [ ] 保存至少一笔成功投票交易 Hash。
- [ ] 记录部署和投票 Gas 消耗。
- [ ] 截图保存钱包连接、投票提交、结果图表。
```

- [ ] **步骤 4：文档检查**

运行：

```powershell
$patterns = @("待" + "定", "T" + "ODO", "后续" + "实现", "T" + "BD")
foreach ($pattern in $patterns) {
  rg -n $pattern README.md docs
}
```

预期：没有未完成标记；部署记录模板使用明确的数据来源说明。

- [ ] **步骤 5：Commit**

```bash
git add README.md docs/thesis/algorithm-notes.md docs/testing/manual-test-checklist.md
git commit -m "docs(论文): 补充算法分析和测试清单"
```

## 任务 10：端到端本地验证与推送

**文件：**
- 修改：`docs/deployments/sepolia.md`，仅在完成 Sepolia 部署后记录真实结果。
- 修改：`apps/web/public/deployment.json`，由导出脚本生成。
- 修改：`apps/web/public/whitelist.json`，由白名单脚本生成。

- [ ] **步骤 1：全量安装**

运行：

```bash
npm install
```

预期：根依赖和 `apps/web` 依赖安装完成。

- [ ] **步骤 2：生成白名单**

运行：

```bash
npm run generate:whitelist
```

预期：`apps/web/public/whitelist.json` 包含 `merkleRoot` 和每个样例地址的 `proof`。

- [ ] **步骤 3：编译合约**

运行：

```bash
npm run compile
```

预期：PASS。

- [ ] **步骤 4：运行合约测试**

运行：

```bash
npm test
```

预期：所有测试 PASS。

- [ ] **步骤 5：运行 Gas 测试**

运行：

```bash
npm run test:gas
```

预期：所有测试 PASS，并输出 Gas 报告。

- [ ] **步骤 6：构建前端**

运行：

```bash
npm run web:build
```

预期：PASS，生成 `apps/web/dist/`。

- [ ] **步骤 7：本地链部署演示**

终端 1：

```bash
npm run node
```

终端 2：

```bash
npm run deploy:local
npm run export:frontend -- --network localhost
npm run web:dev
```

预期：浏览器打开 `http://localhost:5173` 后可以连接 MetaMask 本地网络，并完成样例账户投票流程。

- [ ] **步骤 8：Sepolia 部署**

在 `.env` 填写真实配置后运行：

```bash
npm run deploy:sepolia
npm run export:frontend -- --network sepolia
```

预期：生成 `deployments/sepolia.json`，并将真实地址、交易 Hash、Gas 数据填入 `docs/deployments/sepolia.md`。

- [ ] **步骤 9：最终 Git 检查**

运行：

```bash
git status --short
```

预期：只显示有意提交的文档或部署产物变更；`.env`、`node_modules/`、`artifacts/`、`cache/` 不应被跟踪。

- [ ] **步骤 10：最终提交和推送**

```bash
git add README.md docs apps/web/public/deployment.json apps/web/public/whitelist.json deployments/sepolia.json
git commit -m "docs(部署): 记录测试网部署和验证结果"
git push
```

预期：GitHub `main` 分支包含完整项目代码、测试、前端、文档和部署记录。
