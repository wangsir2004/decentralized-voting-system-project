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

export type WhitelistFile = {
  merkleRoot: string;
  voters: WhitelistEntry[];
};

export function normalizeVoterAddresses(voters: string[]) {
  if (!Array.isArray(voters) || !voters.length) {
    throw new Error("选民白名单不能为空");
  }

  const seen = new Set<string>();

  return voters.map((address) => {
    const normalized = ethers.getAddress(address);
    const key = normalized.toLowerCase();
    if (seen.has(key)) {
      throw new Error(`选民地址重复：${normalized}`);
    }
    seen.add(key);
    return normalized;
  });
}

export function buildWhitelist(voters: string[]): WhitelistFile {
  // 先用 ethers 规范化地址，确保大小写校验和链上 leaf 计算一致。
  const normalized = normalizeVoterAddresses(voters);
  // leaf 计算方式必须与 VotingSystem.vote 中的 abi.encodePacked(address) 对齐。
  const leaves = normalized.map((address) => ethers.keccak256(ethers.solidityPacked(["address"], [address])));
  const tree = new MerkleTree(leaves, keccak256, { sortPairs: true });
  const root = tree.getHexRoot();

  // 前端按当前钱包地址查找 proof，并把 proof 原样提交给合约校验。
  const entries: WhitelistEntry[] = normalized.map((address, index) => ({
    address,
    leaf: leaves[index],
    proof: tree.getHexProof(leaves[index])
  }));

  return { merkleRoot: root, voters: entries };
}

async function main() {
  const votersPath = path.join(process.cwd(), "data", "voters.sample.json");
  const outputPath = path.join(process.cwd(), "apps", "web", "public", "whitelist.json");

  const voters = JSON.parse(fs.readFileSync(votersPath, "utf8")) as string[];
  const whitelist = buildWhitelist(voters);

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(
    outputPath,
    JSON.stringify(whitelist, null, 2) + "\n",
    "utf8"
  );

  console.log(`默克尔根：${whitelist.merkleRoot}`);
  console.log(`白名单文件已写入：${outputPath}`);
}

if (require.main === module) {
  main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
}
