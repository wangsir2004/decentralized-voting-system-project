import fs from "fs";
import path from "path";
import { buildWhitelistFromAddresses, normalizeVoterAddresses } from "../shared/merkle";

type WhitelistEntry = {
  address: string;
  leaf: string;
  proof: string[];
};

export type WhitelistFile = {
  merkleRoot: string;
  voters: WhitelistEntry[];
};

export function buildWhitelist(voters: string[]): WhitelistFile {
  return buildWhitelistFromAddresses(voters);
}

export { normalizeVoterAddresses };

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
