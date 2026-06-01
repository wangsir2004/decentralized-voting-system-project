import { expect } from "chai";
import type { DeploymentConfig } from "../apps/web/src/contracts/deployment";
import { preserveExportedDeploymentEvidence } from "../shared/deploymentEvidence";

const publicDeployment: DeploymentConfig = {
  network: "sepolia",
  chainId: 11155111,
  contractName: "VotingSystem",
  address: "0x02C0Df4A9528586689c89e97bB64439c3C9fFa36",
  deployer: "0x372ee50901D62F3b314936C9302b19F8F477716E",
  title: "基于智能合约的去中心化电子投票演示",
  candidates: ["方案 A", "方案 B"],
  votingEndTime: 1779877895,
  merkleRoot: "0xb84d167dee14c531723adc7c8625c29224727496b7a19329eda9cbc6d15c4a21",
  deploymentTransactionHash: "0x073f0d402491c8d28862f79c5b4b1fabcaf4544db6d33896a9bf5cb18ee78d2e",
  deploymentGasUsed: "1167383",
  factoryAddress: "0x83F9470c4be7bb2448D092556C9F61814D9e8bAC",
  factoryDeploymentTransactionHash: "0x15940f4724d1aef4723474b489078708fefe078f92aa6913a6fdeec89970a3f8",
  factoryDeploymentGasUsed: "1953361",
  deployedAt: "2026-05-24T10:32:02.023Z",
  abi: []
};

describe("frontend platform metadata", function () {
  it("preserves exported deployment evidence when the factory record is the public deployment", function () {
    const factoryDeployment: DeploymentConfig = {
      ...publicDeployment,
      address: publicDeployment.address.toLowerCase(),
      deploymentTransactionHash: "",
      deploymentGasUsed: "",
      deployedAt: "2026-05-24T10:32:00.000Z",
      source: "factory"
    };

    const merged = preserveExportedDeploymentEvidence(factoryDeployment, publicDeployment);

    expect(merged.deploymentTransactionHash).to.equal(publicDeployment.deploymentTransactionHash);
    expect(merged.deploymentGasUsed).to.equal(publicDeployment.deploymentGasUsed);
    expect(merged.deployedAt).to.equal(publicDeployment.deployedAt);
  });

  it("does not fabricate deployment evidence for a different factory election", function () {
    const factoryDeployment: DeploymentConfig = {
      ...publicDeployment,
      address: "0x1111111111111111111111111111111111111111",
      deploymentTransactionHash: "",
      deploymentGasUsed: "",
      deployedAt: "2026-05-24T10:40:00.000Z",
      source: "factory"
    };

    const merged = preserveExportedDeploymentEvidence(factoryDeployment, publicDeployment);

    expect(merged.deploymentTransactionHash).to.equal("");
    expect(merged.deploymentGasUsed).to.equal("");
    expect(merged.deployedAt).to.equal("2026-05-24T10:40:00.000Z");
  });
});
