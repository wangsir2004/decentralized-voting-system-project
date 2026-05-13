export {
  // Web 端只做转发，保证测试和页面共用同一套展示格式化逻辑。
  countTotalVotes,
  formatWalletError,
  getLeadingCandidate,
  getNetworkLabel,
  getProofDepth,
  shortenAddress,
  summarizeAbiFunctions
} from "../../../../shared/display";

export type { LeadingCandidate } from "../../../../shared/display";
