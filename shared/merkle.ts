import { concat, getAddress, getBytes, keccak256, solidityPacked } from "ethers";

export type WhitelistEntry = {
  address: string;
  leaf: string;
  proof: string[];
};

export type BuiltWhitelist = {
  merkleRoot: string;
  voters: WhitelistEntry[];
};

const ZERO_BYTES32 = `0x${"0".repeat(64)}`;

export function normalizeVoterAddresses(addresses: string[]) {
  if (!Array.isArray(addresses) || !addresses.length) {
    throw new Error("选民白名单不能为空。");
  }

  const seen = new Set<string>();
  return addresses.map((address) => {
    const normalized = getAddress(address.trim());
    const key = normalized.toLowerCase();
    if (seen.has(key)) {
      throw new Error(`选民地址重复：${normalized}`);
    }
    seen.add(key);
    return normalized;
  });
}

function hashLeaf(address: string) {
  return keccak256(solidityPacked(["address"], [address]));
}

function sortPair(left: string, right: string) {
  return left.toLowerCase() <= right.toLowerCase() ? [left, right] : [right, left];
}

function hashPair(left: string, right: string) {
  const [first, second] = sortPair(left, right);
  return keccak256(concat([getBytes(first), getBytes(second)]));
}

function buildLevels(leaves: string[]) {
  const levels = [leaves];
  let current = leaves;

  while (current.length > 1) {
    const next: string[] = [];
    for (let index = 0; index < current.length; index += 2) {
      const left = current[index];
      const right = current[index + 1];
      next.push(right ? hashPair(left, right) : left);
    }
    levels.push(next);
    current = next;
  }

  return levels;
}

function proofFor(levels: string[][], leafIndex: number) {
  const proof: string[] = [];
  let index = leafIndex;

  for (let levelIndex = 0; levelIndex < levels.length - 1; levelIndex += 1) {
    const level = levels[levelIndex];
    const pairIndex = index % 2 === 0 ? index + 1 : index - 1;

    if (pairIndex < level.length) {
      proof.push(level[pairIndex]);
    }

    index = Math.floor(index / 2);
  }

  return proof;
}

export function buildWhitelistFromAddresses(addresses: string[]): BuiltWhitelist {
  const normalized = normalizeVoterAddresses(addresses);
  const leaves = normalized.map(hashLeaf);
  const levels = buildLevels(leaves);
  const merkleRoot = levels.at(-1)?.[0] ?? ZERO_BYTES32;

  if (merkleRoot === ZERO_BYTES32) {
    throw new Error("默克尔根生成失败。");
  }

  return {
    merkleRoot,
    voters: normalized.map((address, index) => ({
      address,
      leaf: leaves[index],
      proof: proofFor(levels, index)
    }))
  };
}
