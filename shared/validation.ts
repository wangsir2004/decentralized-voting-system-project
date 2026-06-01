export type DeploymentResource = {
  network: string;
  chainId: number;
  contractName: string;
  address: string;
  deployer: string;
  title: string;
  candidates: string[];
  votingEndTime: number;
  merkleRoot: string;
  deploymentTransactionHash: string;
  deploymentGasUsed: string;
  factoryAddress?: string;
  factoryDeploymentTransactionHash?: string;
  factoryDeploymentGasUsed?: string;
  factoryAbi?: unknown[];
  deployedAt: string;
  abi: unknown[];
};

export type WhitelistResource = {
  merkleRoot: string;
  voters: Array<{
    address: string;
    leaf?: string;
    proof: string[];
  }>;
};

const ADDRESS_PATTERN = /^0x[0-9a-fA-F]{40}$/;
const BYTES32_PATTERN = /^0x[0-9a-fA-F]{64}$/;
const ZERO_BYTES32 = `0x${"0".repeat(64)}`;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function requireString(record: Record<string, unknown>, field: string, label: string) {
  const value = record[field];
  if (typeof value !== "string" || !value.trim()) {
    throw new Error(`${label}不能为空。`);
  }

  return value;
}

function optionalString(record: Record<string, unknown>, field: string) {
  const value = record[field];
  return typeof value === "string" ? value : "";
}

function requireAddress(value: unknown, label: string) {
  if (typeof value !== "string" || !ADDRESS_PATTERN.test(value)) {
    throw new Error(`${label}无效。`);
  }

  return value;
}

function requireBytes32(value: unknown, label: string) {
  if (typeof value !== "string" || !BYTES32_PATTERN.test(value) || value.toLowerCase() === ZERO_BYTES32) {
    throw new Error(`${label}无效。`);
  }

  return value;
}

function requireCandidates(value: unknown) {
  if (!Array.isArray(value) || value.length < 2) {
    throw new Error("候选项数量无效。");
  }

  return value.map((candidate) => {
    if (typeof candidate !== "string" || !candidate.trim()) {
      throw new Error("候选项名称不能为空。");
    }

    return candidate;
  });
}

export function validateDeploymentConfig(value: unknown): DeploymentResource {
  if (!isRecord(value)) {
    throw new Error("部署配置格式无效。");
  }

  const chainId = value.chainId;
  const votingEndTime = value.votingEndTime;
  const abi = value.abi;
  const factoryAbi = value.factoryAbi;
  const deployer = optionalString(value, "deployer");
  const factoryAddress = optionalString(value, "factoryAddress");

  if (typeof chainId !== "number" || !Number.isInteger(chainId) || chainId <= 0) {
    throw new Error("链编号无效。");
  }

  if (typeof votingEndTime !== "number" || !Number.isInteger(votingEndTime) || votingEndTime <= 0) {
    throw new Error("投票截止时间无效。");
  }

  if (!Array.isArray(abi)) {
    throw new Error("合约 ABI 无效。");
  }

  if (factoryAddress && !ADDRESS_PATTERN.test(factoryAddress)) {
    throw new Error("平台工厂合约地址无效。");
  }

  if (factoryAbi !== undefined && !Array.isArray(factoryAbi)) {
    throw new Error("平台工厂 ABI 无效。");
  }

  if (deployer && !ADDRESS_PATTERN.test(deployer)) {
    throw new Error("部署账户地址无效。");
  }

  return {
    network: requireString(value, "network", "网络名称"),
    chainId,
    contractName: requireString(value, "contractName", "合约名称"),
    address: requireAddress(value.address, "合约地址"),
    deployer,
    title: requireString(value, "title", "投票标题"),
    candidates: requireCandidates(value.candidates),
    votingEndTime,
    merkleRoot: requireBytes32(value.merkleRoot, "默克尔根"),
    deploymentTransactionHash: optionalString(value, "deploymentTransactionHash"),
    deploymentGasUsed: optionalString(value, "deploymentGasUsed"),
    factoryAddress,
    factoryDeploymentTransactionHash: optionalString(value, "factoryDeploymentTransactionHash"),
    factoryDeploymentGasUsed: optionalString(value, "factoryDeploymentGasUsed"),
    factoryAbi: Array.isArray(factoryAbi) ? factoryAbi : undefined,
    deployedAt: optionalString(value, "deployedAt"),
    abi
  };
}

export function validateWhitelistFile(value: unknown): WhitelistResource {
  if (!isRecord(value)) {
    throw new Error("白名单文件格式无效。");
  }

  if (!Array.isArray(value.voters)) {
    throw new Error("白名单地址列表无效。");
  }

  const seen = new Set<string>();
  const voters = value.voters.map((entry) => {
    if (!isRecord(entry)) {
      throw new Error("白名单地址条目无效。");
    }

    const address = requireAddress(entry.address, "白名单地址");
    const normalized = address.toLowerCase();
    if (seen.has(normalized)) {
      throw new Error("白名单地址重复。");
    }
    seen.add(normalized);

    const proof = entry.proof;
    if (!Array.isArray(proof)) {
      throw new Error("白名单证明无效。");
    }

    const leaf = entry.leaf === undefined ? undefined : requireBytes32(entry.leaf, "白名单叶子节点");

    return {
      address,
      leaf,
      proof: proof.map((item) => requireBytes32(item, "白名单证明"))
    };
  });

  return {
    merkleRoot: requireBytes32(value.merkleRoot, "白名单默克尔根"),
    voters
  };
}

export function assertMatchingMerkleRoot(
  deployment: Pick<DeploymentResource, "merkleRoot">,
  whitelist: Pick<WhitelistResource, "merkleRoot">
) {
  if (deployment.merkleRoot.toLowerCase() !== whitelist.merkleRoot.toLowerCase()) {
    throw new Error("部署配置与白名单默克尔根不一致。");
  }
}
