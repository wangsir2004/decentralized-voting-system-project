import { Contract, JsonRpcProvider } from "ethers";
import type { DeploymentConfig } from "./deployment";
import { preserveExportedDeploymentEvidence } from "../../../../shared/deploymentEvidence";

export type FactoryElection = {
  id: string;
  deployment: DeploymentConfig;
  archived: boolean;
};

const READONLY_RPC_BY_CHAIN_ID: Record<number, string> = {
  11155111: "https://ethereum-sepolia-rpc.publicnode.com"
};

function getRecordValue(record: unknown, key: string, index: number) {
  if (typeof record === "object" && record !== null && key in record) {
    return (record as Record<string, unknown>)[key];
  }

  return Array.isArray(record) ? record[index] : undefined;
}

function asString(value: unknown) {
  return typeof value === "string" ? value : "";
}

function asNumber(value: unknown) {
  return typeof value === "bigint" ? Number(value) : Number(value || 0);
}

function asBoolean(value: unknown) {
  return typeof value === "boolean" ? value : Boolean(value);
}

export function hasFactoryRegistry(deployment: DeploymentConfig | null) {
  return Boolean(deployment?.factoryAddress && deployment?.factoryAbi?.length);
}

export function getReadProvider(chainId: number) {
  const rpcUrl = READONLY_RPC_BY_CHAIN_ID[chainId];
  if (!rpcUrl) {
    throw new Error("当前网络缺少只读 RPC，无法读取平台投票列表。");
  }

  return new JsonRpcProvider(rpcUrl, chainId);
}

export async function loadFactoryElections(baseDeployment: DeploymentConfig): Promise<FactoryElection[]> {
  if (!baseDeployment.factoryAddress || !baseDeployment.factoryAbi?.length) {
    return [];
  }

  const provider = getReadProvider(baseDeployment.chainId);
  const factory = new Contract(baseDeployment.factoryAddress, baseDeployment.factoryAbi, provider);
  const count = Number(await factory.getElectionCount());
  const elections: FactoryElection[] = [];

  for (let index = 0; index < count; index += 1) {
    const record = await factory.getElection(index);
    const voters = await factory.getElectionVoters(index);
    const address = asString(getRecordValue(record, "election", 0));
    const voting = new Contract(address, baseDeployment.abi, provider);
    const candidates = await voting.getCandidates();
    const votingEndTime = asNumber(getRecordValue(record, "votingEndTime", 3));
    const createdAt = asNumber(getRecordValue(record, "createdAt", 5));
    const archived = asBoolean(getRecordValue(record, "archived", 6));

    const deployment = preserveExportedDeploymentEvidence({
        ...baseDeployment,
        address,
        deployer: asString(getRecordValue(record, "creator", 1)),
        title: asString(getRecordValue(record, "title", 2)),
        candidates: [...candidates],
        votingEndTime,
        merkleRoot: asString(getRecordValue(record, "merkleRoot", 4)),
        deploymentTransactionHash: "",
        deploymentGasUsed: "",
        deployedAt: createdAt ? new Date(createdAt * 1000).toISOString() : "",
        source: "factory" as const,
        voters: [...voters],
        electionId: index
      }, baseDeployment);

    elections.push({
      id: `${baseDeployment.chainId}:${address.toLowerCase()}`,
      archived,
      deployment
    });
  }

  return elections.reverse();
}
