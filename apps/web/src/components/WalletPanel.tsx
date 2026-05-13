import { getNetworkLabel, shortenAddress } from "../utils/display";

type WalletPanelProps = {
  account: string;
  chainId: number | null;
  expectedChainId: number | null;
  isConnecting: boolean;
  error: string;
  onConnect: () => void;
};

export function WalletPanel({
  account,
  chainId,
  expectedChainId,
  isConnecting,
  error,
  onConnect
}: WalletPanelProps) {
  // 钱包网络必须与 deployment.json 中的 chainId 一致，否则提交交易会落到错误网络。
  const wrongNetwork = Boolean(account && chainId && expectedChainId && chainId !== expectedChainId);
  const connected = Boolean(account);

  return (
    <section className="panel wallet-panel operation-panel">
      <div className="panel-heading">
        <span>钱包连接</span>
        <strong>{connected ? "账户已识别" : "等待连接"}</strong>
      </div>
      <div className="wallet-body">
        <div>
          <p className="panel-label">钱包状态</p>
          <h2>{connected ? shortenAddress(account) : "未连接钱包"}</h2>
          <p className="muted-text">
            当前网络：{getNetworkLabel(chainId)} / 目标网络：{getNetworkLabel(expectedChainId)}
          </p>
        </div>
        <button className="primary-button" onClick={onConnect} disabled={isConnecting}>
          {connected ? "刷新钱包" : isConnecting ? "连接中..." : "连接钱包"}
        </button>
      </div>
      <div className="status-line">
        <span className={`status-chip ${connected ? "status-ok" : "status-warn"}`}>
          {connected ? "账户已连接" : "等待账户"}
        </span>
        <span className={`status-chip ${wrongNetwork ? "status-danger" : "status-ok"}`}>
          {wrongNetwork ? "网络不匹配" : "网络可用"}
        </span>
      </div>
      {wrongNetwork && <p className="error-text">请切换到部署配置对应的网络。</p>}
      {error && <p className="error-text">{error}</p>}
    </section>
  );
}
