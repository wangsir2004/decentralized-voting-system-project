import fs from "fs";
import path from "path";
import { ethers, network } from "hardhat";

type WhitelistFile = {
  merkleRoot: string;
  voters: Array<{ address: string }>;
};

const BYTES32_PATTERN = /^0x[0-9a-fA-F]{64}$/;
const ZERO_BYTES32 = `0x${"0".repeat(64)}`;

export function validateCandidates(candidates: string[]) {
  if (!Array.isArray(candidates) || candidates.length < 2) {
    throw new Error("候选项数量无效");
  }

  for (const candidate of candidates) {
    if (typeof candidate !== "string" || !candidate.trim()) {
      throw new Error("候选项名称不能为空");
    }
  }

  return candidates;
}

export function validateMerkleRoot(merkleRoot: string) {
  if (
    typeof merkleRoot !== "string" ||
    !BYTES32_PATTERN.test(merkleRoot) ||
    merkleRoot.toLowerCase() === ZERO_BYTES32
  ) {
    throw new Error("默克尔根不能为空");
  }

  return merkleRoot;
}

async function main() {
  const whitelistPath = path.join(process.cwd(), "apps", "web", "public", "whitelist.json");
  const candidatesPath = path.join(process.cwd(), "data", "candidates.sample.json");

  // 部署脚本复用前端白名单文件，保证合约 merkleRoot 与 UI proof 来源一致。
  const whitelist = JSON.parse(fs.readFileSync(whitelistPath, "utf8")) as WhitelistFile;
  const candidates = validateCandidates(JSON.parse(fs.readFileSync(candidatesPath, "utf8")) as string[]);
  const merkleRoot = validateMerkleRoot(whitelist.merkleRoot);
  const now = Math.floor(Date.now() / 1000);
  // 默认投票窗口为 3 天，便于公网部署后留出充分的远程演示和测试时间。
  const votingEndTime = now + 3 * 24 * 60 * 60;
  const title = "基于智能合约的去中心化电子投票演示";

  const VotingFactory = await ethers.getContractFactory("VotingFactory");
  const [deployerSigner] = await ethers.getSigners();
  const votingFactory = await VotingFactory.deploy();
  await votingFactory.waitForDeployment();

  const factoryAddress = await votingFactory.getAddress();
  const factoryDeploymentTx = votingFactory.deploymentTransaction();
  const factoryReceipt = factoryDeploymentTx ? await factoryDeploymentTx.wait() : null;
  const deployer = await deployerSigner.getAddress();
  const voterAddresses = whitelist.voters.map((entry) => entry.address);
  const createTx = await votingFactory.createElection(title, candidates, votingEndTime, merkleRoot, voterAddresses);
  const createReceipt = await createTx.wait();
  const electionRecord = await votingFactory.getElection(0);
  const address = electionRecord.election;

  // 输出文件同时服务部署追踪和前端读取，字段保持显式便于论文与验收截图引用。
  const output = {
    network: network.name,
    chainId: Number((await ethers.provider.getNetwork()).chainId),
    contractName: "VotingSystem",
    address,
    deployer: deployer || "",
    title,
    candidates,
    votingEndTime,
    merkleRoot,
    deploymentTransactionHash: createTx.hash || "",
    deploymentGasUsed: createReceipt?.gasUsed?.toString() || "",
    factoryAddress,
    factoryDeploymentTransactionHash: factoryDeploymentTx?.hash || "",
    factoryDeploymentGasUsed: factoryReceipt?.gasUsed?.toString() || "",
    deployedAt: new Date().toISOString()
  };

  fs.mkdirSync(path.join(process.cwd(), "deployments"), { recursive: true });
  const outputPath = path.join(process.cwd(), "deployments", `${network.name}.json`);
  // 统一落盘到 deployments/{network}.json，再由 exportFrontendArtifact 同步给前端。
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2) + "\n", "utf8");

  console.log(`投票平台工厂合约已部署到：${factoryAddress}`);
  console.log(`默认投票智能合约已创建到：${address}`);
  console.log(`部署记录已保存到：${outputPath}`);
}

if (require.main === module) {
  main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
}
