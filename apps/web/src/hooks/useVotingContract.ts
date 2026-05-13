import { useCallback, useEffect, useState } from "react";
import { BrowserProvider, Contract, JsonRpcProvider } from "ethers";
import { assertMatchingMerkleRoot, loadWhitelist, type DeploymentConfig } from "../contracts/deployment";
import { formatWalletError } from "../utils/display";

export type VotingState = {
  candidates: string[];
  counts: number[];
  isOpen: boolean;
  hasVoted: boolean;
  eligible: boolean;
  proof: string[];
  leaf: string;
  whitelistSize: number;
  txHash: string;
  isLoading: boolean;
  isSubmitting: boolean;
  error: string;
};

const initialState: VotingState = {
  candidates: [],
  counts: [],
  isOpen: false,
  hasVoted: false,
  eligible: false,
  proof: [],
  leaf: "",
  whitelistSize: 0,
  txHash: "",
  isLoading: false,
  isSubmitting: false,
  error: ""
};

const READONLY_RPC_BY_CHAIN_ID: Record<number, string> = {
  11155111: "https://ethereum-sepolia-rpc.publicnode.com"
};

export function useVotingContract(deployment: DeploymentConfig | null, account: string) {
  const [state, setState] = useState<VotingState>(initialState);

  // refresh 同时读取白名单 JSON 和链上状态，使候选项、票数、资格信息保持同一轮快照。
  const refresh = useCallback(async () => {
    if (!deployment) return;

    setState((current) => ({ ...current, isLoading: true, error: "" }));

    try {
      const whitelist = await loadWhitelist();
      assertMatchingMerkleRoot(deployment, whitelist);
      // 白名单文件里的地址已规范化，这里再用小写比较兼容钱包返回的 checksum 地址。
      const entry = account
        ? whitelist.voters.find((item) => item.address.toLowerCase() === account.toLowerCase())
        : undefined;

      const readOnlyRpcUrl = READONLY_RPC_BY_CHAIN_ID[deployment.chainId];
      const provider = window.ethereum
        ? new BrowserProvider(window.ethereum)
        : readOnlyRpcUrl
          ? new JsonRpcProvider(readOnlyRpcUrl, deployment.chainId)
          : null;

      if (!provider) {
        // 没有钱包且缺少只读 RPC 时仍展示部署候选项和本地白名单状态。
        setState((current) => ({
          ...current,
          candidates: deployment.candidates,
          counts: deployment.candidates.map(() => 0),
          isOpen: Math.floor(Date.now() / 1000) <= deployment.votingEndTime,
          hasVoted: false,
          eligible: Boolean(entry),
          proof: entry?.proof ?? [],
          leaf: entry?.leaf ?? "",
          whitelistSize: whitelist.voters.length,
          isLoading: false,
          error: "未检测到浏览器钱包，请先安装钱包插件。"
        }));
        return;
      }

      const contract = new Contract(deployment.address, deployment.abi, provider);
      // 读操作使用 provider，不需要用户签名，也不会弹出钱包确认。
      const [names, rawCounts] = await contract.getResults();
      const isOpen = await contract.isVotingOpen();
      const hasVoted = account ? await contract.hasAddressVoted(account) : false;

      setState((current) => ({
        ...current,
        candidates: [...names],
        counts: rawCounts.map((count: bigint) => Number(count)),
        isOpen,
        hasVoted,
        eligible: Boolean(entry),
        proof: entry?.proof ?? [],
        leaf: entry?.leaf ?? "",
        whitelistSize: whitelist.voters.length,
        isLoading: false,
        error: window.ethereum ? "" : "未检测到浏览器钱包，当前以只读模式展示链上投票结果。"
      }));
    } catch (error) {
      setState((current) => ({
        ...current,
        isLoading: false,
        isOpen: false,
        eligible: false,
        proof: [],
        leaf: "",
        error: formatWalletError(error, "读取投票数据失败。")
      }));
    }
  }, [deployment, account]);

  async function submitVote(candidateIndex: number) {
    if (!deployment || !window.ethereum) return;

    setState((current) => ({ ...current, isSubmitting: true, error: "", txHash: "" }));

    try {
      const provider = new BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const contract = new Contract(deployment.address, deployment.abi, signer);
      // 提交投票时只发送候选项索引和当前账户的 Merkle proof，资格校验由合约完成。
      const tx = await contract.vote(candidateIndex, state.proof);

      setState((current) => ({ ...current, txHash: tx.hash }));
      // 等待交易确认后刷新链上结果，避免 UI 先展示未确认票数。
      await tx.wait();
      await refresh();
      setState((current) => ({ ...current, isSubmitting: false }));
    } catch (error) {
      setState((current) => ({
        ...current,
        isSubmitting: false,
        error: formatWalletError(error, "提交投票失败。")
      }));
    }
  }

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return {
    ...state,
    refresh,
    submitVote
  };
}
