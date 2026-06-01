export type LeadingCandidate = {
  name: string;
  count: number;
};

// 地址只在 UI 中缩短展示，链上交互始终使用完整地址字符串。
export function shortenAddress(address: string, fallback = "未连接") {
  if (!address) return fallback;
  if (address.length <= 12) return address;

  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

export function getNetworkLabel(chainId: number | null) {
  if (chainId === 31337) return "Hardhat 本地网络";
  if (chainId === 11155111) return "Sepolia 测试网";
  if (chainId === null) return "未知网络";

  return `链编号 ${chainId}`;
}

// 票数在前端统一转成 number 后汇总，便于组件和测试复用。
export function countTotalVotes(counts: number[]) {
  return counts.reduce((total, count) => total + count, 0);
}

export function getLeadingCandidate(candidates: string[], counts: number[]): LeadingCandidate {
  if (!candidates.length || !counts.length) return { name: "暂无数据", count: 0 };

  let leaderIndex = 0;

  // 只在票数更大时更新领先者；相同票数保留更早出现的候选项。
  for (let index = 1; index < counts.length; index += 1) {
    if ((counts[index] ?? 0) > (counts[leaderIndex] ?? 0)) {
      leaderIndex = index;
    }
  }

  return {
    name: candidates[leaderIndex] ?? "暂无数据",
    count: counts[leaderIndex] ?? 0
  };
}

export function getProofDepth(proof: string[]) {
  return proof.length;
}

function readErrorField(error: unknown, field: string): string {
  // 钱包和 ethers 抛出的错误结构不固定，读取前先做类型保护。
  if (typeof error !== "object" || error === null || !(field in error)) return "";
  const value = (error as Record<string, unknown>)[field];
  return typeof value === "string" ? value : "";
}

function extractErrorText(error: unknown) {
  if (typeof error === "string") return error;
  if (error instanceof Error) return error.message;

  return [
    readErrorField(error, "shortMessage"),
    readErrorField(error, "reason"),
    readErrorField(error, "message"),
    readErrorField(error, "code")
  ].filter(Boolean).join(" ");
}

function cleanTechnicalMessage(message: string) {
  // 去掉 ethers 附带的 action、payload 等长参数，避免错误提示挤满界面。
  const withoutPayload = message
    .replace(/\s*\(action=.*$/i, "")
    .replace(/\s*payload=.*$/i, "")
    .trim();

  if (!withoutPayload) return "";
  return withoutPayload.length > 120 ? `${withoutPayload.slice(0, 120)}...` : withoutPayload;
}

export function formatWalletError(error: unknown, fallback = "操作失败。") {
  const text = extractErrorText(error);
  const normalized = text.toLowerCase();

  // 浏览器钱包取消交易会出现多个不同关键字，这里统一成可读中文提示。
  if (
    normalized.includes("action_rejected") ||
    normalized.includes("user rejected") ||
    normalized.includes("user denied") ||
    normalized.includes("ethers-user-denied") ||
    normalized.includes("code: 4001") ||
    normalized.includes("code=4001")
  ) {
    return "你已取消钱包确认，本次操作没有提交到链上。";
  }

  if (normalized.includes("insufficient funds")) {
    return "钱包余额不足，无法支付 Sepolia 测试网交易燃料费。";
  }

  if (normalized.includes("address has already voted")) {
    return "当前钱包地址已经投过票，不能重复投票。";
  }

  if (normalized.includes("address is not eligible")) {
    return "当前钱包地址不在白名单中，不能投票。";
  }

  if (normalized.includes("voting has ended")) {
    return "投票已截止，不能再提交。";
  }

  if (normalized.includes("invalid candidate index")) {
    return "候选项无效，请重新选择。";
  }

  if (normalized.includes("only creator can archive election")) {
    return "只有该投票的创建钱包可以归档或恢复这条记录。";
  }

  if (normalized.includes("election already registered")) {
    return "该投票合约已经登记到平台，不需要重复登记。";
  }

  if (normalized.includes("network") && normalized.includes("chain")) {
    return "当前钱包网络与合约网络不一致，请切换到 Sepolia 测试网。";
  }

  const technicalMessage = cleanTechnicalMessage(text);
  return technicalMessage ? `${fallback} ${technicalMessage}` : fallback;
}

type AbiEntry = {
  type?: unknown;
  name?: unknown;
};

const ABI_FUNCTION_LABELS: Record<string, string> = {
  candidateCount: "读取候选项数量",
  getCandidates: "读取候选项",
  getResults: "读取投票结果",
  hasAddressVoted: "查询是否已投票",
  isVotingOpen: "查询投票是否开放",
  merkleRoot: "读取白名单根",
  title: "读取投票主题",
  vote: "提交投票",
  votingEndTime: "读取截止时间"
};

export function summarizeAbiFunctions(abi: unknown) {
  if (!Array.isArray(abi)) return [];

  // ABI 来自部署产物，先过滤到函数条目，再展示可调用方法名。
  return abi
    .filter((entry): entry is AbiEntry => typeof entry === "object" && entry !== null)
    .filter((entry) => entry.type === "function" && typeof entry.name === "string")
    .map((entry) => ABI_FUNCTION_LABELS[entry.name as string] ?? "合约函数");
}
