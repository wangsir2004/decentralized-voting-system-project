export type DeploymentEvidence = {
  chainId: number;
  address: string;
  deploymentTransactionHash?: string;
  deploymentGasUsed?: string;
  deployedAt?: string;
};

function isSameDeployment(left: DeploymentEvidence, right: DeploymentEvidence) {
  return left.chainId === right.chainId && left.address.toLowerCase() === right.address.toLowerCase();
}

export function preserveExportedDeploymentEvidence<T extends DeploymentEvidence>(
  deployment: T,
  exportedDeployment: DeploymentEvidence
): T {
  if (!isSameDeployment(deployment, exportedDeployment)) {
    return deployment;
  }

  return {
    ...deployment,
    deploymentTransactionHash: deployment.deploymentTransactionHash || exportedDeployment.deploymentTransactionHash || "",
    deploymentGasUsed: deployment.deploymentGasUsed || exportedDeployment.deploymentGasUsed || "",
    deployedAt: exportedDeployment.deployedAt || deployment.deployedAt || ""
  };
}
