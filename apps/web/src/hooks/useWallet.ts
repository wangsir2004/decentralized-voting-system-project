import { useEffect, useState } from "react";
import { BrowserProvider } from "ethers";
import { formatWalletError } from "../utils/display";

export type WalletState = {
  account: string;
  chainId: number | null;
  isConnecting: boolean;
  error: string;
};

const initialState: WalletState = {
  account: "",
  chainId: null,
  isConnecting: false,
  error: ""
};

export function useWallet() {
  const [state, setState] = useState<WalletState>(initialState);

  async function refreshAccount() {
    if (!window.ethereum) {
      setState((current) => ({ ...current, error: "未检测到浏览器钱包，请先安装钱包插件。" }));
      return;
    }

    try {
      const provider = new BrowserProvider(window.ethereum);
      // eth_accounts 只读取已授权账户，不会主动弹出连接授权窗口。
      const accounts = await provider.send("eth_accounts", []);
      const network = await provider.getNetwork();

      setState((current) => ({
        ...current,
        account: accounts[0] || "",
        chainId: Number(network.chainId),
        error: ""
      }));
    } catch (error) {
      setState((current) => ({
        ...current,
        account: "",
        chainId: null,
        error: formatWalletError(error, "读取钱包状态失败。")
      }));
    }
  }

  async function connect() {
    if (!window.ethereum) {
      setState((current) => ({ ...current, error: "未检测到浏览器钱包，请先安装钱包插件。" }));
      return;
    }

    setState((current) => ({ ...current, isConnecting: true, error: "" }));

    try {
      const provider = new BrowserProvider(window.ethereum);
      // eth_requestAccounts 会触发钱包授权，用户拒绝时交给 formatWalletError 转成中文提示。
      const accounts = await provider.send("eth_requestAccounts", []);
      const network = await provider.getNetwork();

      setState({
        account: accounts[0] || "",
        chainId: Number(network.chainId),
        isConnecting: false,
        error: ""
      });
    } catch (error) {
      setState((current) => ({
        ...current,
        isConnecting: false,
        error: formatWalletError(error, "连接钱包失败。")
      }));
    }
  }

  useEffect(() => {
    void refreshAccount();

    // 监听账户和网络变化，确保用户在钱包中切换后页面状态立即同步。
    const handleAccountsChanged = () => void refreshAccount();
    const handleChainChanged = () => void refreshAccount();

    window.ethereum?.on?.("accountsChanged", handleAccountsChanged);
    window.ethereum?.on?.("chainChanged", handleChainChanged);

    return () => {
      window.ethereum?.removeListener?.("accountsChanged", handleAccountsChanged);
      window.ethereum?.removeListener?.("chainChanged", handleChainChanged);
    };
  }, []);

  return {
    ...state,
    connect
  };
}
