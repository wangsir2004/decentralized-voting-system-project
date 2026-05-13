import type { InterfaceAbi } from "ethers";
import {
  assertMatchingMerkleRoot,
  validateDeploymentConfig,
  validateWhitelistFile,
  type DeploymentResource,
  type WhitelistResource
} from "../../../../shared/validation";

export type DeploymentConfig = Omit<DeploymentResource, "abi"> & {
  abi: InterfaceAbi;
};

export type WhitelistFile = WhitelistResource;

export async function loadDeployment(): Promise<DeploymentConfig> {
  // Vite 会从 public 目录原样托管部署产物，路径保持为站点根目录。
  const response = await fetch("/deployment.json");
  if (!response.ok) {
    throw new Error("无法读取合约部署配置。");
  }

  return validateDeploymentConfig(await response.json()) as DeploymentConfig;
}

export async function loadWhitelist(): Promise<WhitelistFile> {
  const response = await fetch("/whitelist.json");
  if (!response.ok) {
    throw new Error("无法读取白名单配置。");
  }

  return validateWhitelistFile(await response.json());
}

export { assertMatchingMerkleRoot };
