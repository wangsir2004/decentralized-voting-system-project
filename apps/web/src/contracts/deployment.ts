import type { InterfaceAbi } from "ethers";
import {
  assertMatchingMerkleRoot,
  validateDeploymentConfig,
  validateWhitelistFile,
  type DeploymentResource,
  type WhitelistResource
} from "../../../../shared/validation";
import { buildWhitelistFromAddresses } from "../../../../shared/merkle";

export type DeploymentConfig = Omit<DeploymentResource, "abi"> & {
  abi: InterfaceAbi;
  source?: "public" | "local" | "factory";
  factoryAbi?: InterfaceAbi;
  voters?: string[];
  electionId?: number;
};

export type WhitelistFile = WhitelistResource;

export type VotingContractArtifact = {
  contractName: string;
  abi: InterfaceAbi;
  bytecode: string;
};

export type StoredElection = {
  id: string;
  deployment: DeploymentConfig;
  whitelist: WhitelistFile;
  savedAt: string;
};

const ACTIVE_DEPLOYMENT_KEY = "dvoting.activeDeployment.v1";
const ACTIVE_WHITELIST_KEY = "dvoting.activeWhitelist.v1";
const LOCAL_ELECTIONS_KEY = "dvoting.localElections.v1";

function hasStorage() {
  return typeof window !== "undefined" && Boolean(window.localStorage);
}

function requireHexBytecode(value: unknown) {
  if (typeof value !== "string" || !/^0x[0-9a-fA-F]+$/.test(value) || value.length <= 2) {
    throw new Error("合约字节码无效，请先重新导出前端合约产物。");
  }

  return value;
}

function readLocalDeployment(): DeploymentConfig | null {
  if (!hasStorage()) return null;

  const rawDeployment = window.localStorage.getItem(ACTIVE_DEPLOYMENT_KEY);
  if (!rawDeployment) return null;

  try {
    return {
      ...(validateDeploymentConfig(JSON.parse(rawDeployment)) as DeploymentConfig),
      source: "local"
    };
  } catch {
    window.localStorage.removeItem(ACTIVE_DEPLOYMENT_KEY);
    window.localStorage.removeItem(ACTIVE_WHITELIST_KEY);
    return null;
  }
}

function electionIdFor(deployment: Pick<DeploymentConfig, "chainId" | "address">) {
  return `${deployment.chainId}:${deployment.address.toLowerCase()}`;
}

function normalizeStoredElection(value: unknown): StoredElection | null {
  if (typeof value !== "object" || value === null) return null;
  const record = value as Record<string, unknown>;

  try {
    const deployment = {
      ...(validateDeploymentConfig(record.deployment) as DeploymentConfig),
      source: "local" as const
    };
    const whitelist = validateWhitelistFile(record.whitelist);
    return {
      id: typeof record.id === "string" ? record.id : electionIdFor(deployment),
      deployment,
      whitelist,
      savedAt: typeof record.savedAt === "string" ? record.savedAt : deployment.deployedAt || ""
    };
  } catch {
    return null;
  }
}

export function readLocalElections(): StoredElection[] {
  if (!hasStorage()) return [];

  const raw = window.localStorage.getItem(LOCAL_ELECTIONS_KEY);
  if (!raw) return [];

  try {
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed
      .map(normalizeStoredElection)
      .filter((entry): entry is StoredElection => Boolean(entry));
  } catch {
    window.localStorage.removeItem(LOCAL_ELECTIONS_KEY);
    return [];
  }
}

function writeLocalElections(elections: StoredElection[]) {
  if (!hasStorage()) return;

  window.localStorage.setItem(LOCAL_ELECTIONS_KEY, JSON.stringify(elections));
}

export async function loadPublicDeployment(): Promise<DeploymentConfig> {
  // Vite 会从 public 目录原样托管部署产物，路径保持为站点根目录。
  const response = await fetch("/deployment.json");
  if (!response.ok) {
    throw new Error("无法读取合约部署配置。");
  }

  return {
    ...(validateDeploymentConfig(await response.json()) as DeploymentConfig),
    source: "public"
  };
}

export async function loadDeployment(): Promise<DeploymentConfig> {
  const localDeployment = readLocalDeployment();
  if (localDeployment) return localDeployment;

  return loadPublicDeployment();
}

export async function loadVotingContractArtifact(): Promise<VotingContractArtifact> {
  const response = await fetch("/voting-system-artifact.json");
  if (!response.ok) {
    throw new Error("无法读取前端合约字节码，请先运行 npm run export:frontend。");
  }

  const artifact = await response.json() as Record<string, unknown>;
  if (!Array.isArray(artifact.abi)) {
    throw new Error("合约 ABI 无效，请重新导出前端合约产物。");
  }

  return {
    contractName: typeof artifact.contractName === "string" ? artifact.contractName : "VotingSystem",
    abi: artifact.abi as InterfaceAbi,
    bytecode: requireHexBytecode(artifact.bytecode)
  };
}

export function saveLocalDeployment(deployment: DeploymentConfig, whitelist: WhitelistFile) {
  if (!hasStorage()) return;

  window.localStorage.setItem(ACTIVE_DEPLOYMENT_KEY, JSON.stringify({ ...deployment, source: undefined }));
  window.localStorage.setItem(ACTIVE_WHITELIST_KEY, JSON.stringify(whitelist));

  const stored: StoredElection = {
    id: electionIdFor(deployment),
    deployment: { ...deployment, source: "local" },
    whitelist,
    savedAt: new Date().toISOString()
  };
  const remaining = readLocalElections().filter((entry) => entry.id !== stored.id);
  writeLocalElections([stored, ...remaining].slice(0, 20));
}

export function clearLocalDeployment() {
  if (!hasStorage()) return;

  window.localStorage.removeItem(ACTIVE_DEPLOYMENT_KEY);
  window.localStorage.removeItem(ACTIVE_WHITELIST_KEY);
}

export function activateLocalElection(id: string): DeploymentConfig | null {
  if (!hasStorage()) return null;

  const election = readLocalElections().find((entry) => entry.id === id);
  if (!election) return null;

  window.localStorage.setItem(ACTIVE_DEPLOYMENT_KEY, JSON.stringify({ ...election.deployment, source: undefined }));
  window.localStorage.setItem(ACTIVE_WHITELIST_KEY, JSON.stringify(election.whitelist));
  return { ...election.deployment, source: "local" };
}

export async function loadWhitelist(): Promise<WhitelistFile> {
  const response = await fetch("/whitelist.json");
  if (!response.ok) {
    throw new Error("无法读取白名单配置。");
  }

  return validateWhitelistFile(await response.json());
}

export async function loadWhitelistForDeployment(deployment: DeploymentConfig): Promise<WhitelistFile> {
  if (deployment.voters?.length) {
    return buildWhitelistFromAddresses(deployment.voters);
  }

  if (deployment.source === "local" && hasStorage()) {
    const rawWhitelist = window.localStorage.getItem(ACTIVE_WHITELIST_KEY);
    if (rawWhitelist) {
      return validateWhitelistFile(JSON.parse(rawWhitelist));
    }
  }

  return loadWhitelist();
}

export { assertMatchingMerkleRoot };
