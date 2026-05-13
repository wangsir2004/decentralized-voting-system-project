import fs from "fs";
import path from "path";
import { network } from "hardhat";

async function main() {
  const artifactPath = path.join(process.cwd(), "artifacts", "contracts", "VotingSystem.sol", "VotingSystem.json");
  const deploymentPath = path.join(process.cwd(), "deployments", `${network.name}.json`);
  const publicDir = path.join(process.cwd(), "apps", "web", "public");
  const outputPath = path.join(publicDir, "deployment.json");

  // Hardhat artifact 提供 ABI，部署记录提供地址和链 ID，前端需要二者组合后才能实例化合约。
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

  console.log(`前端部署配置已写入：${outputPath}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
