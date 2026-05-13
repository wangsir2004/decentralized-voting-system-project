import { shortenAddress } from "../utils/display";

type SecurityPanelProps = {
  merkleRoot: string;
  leaf: string;
  proofDepth: number;
  whitelistSize: number;
  eligible: boolean;
  hasVoted: boolean;
  isOpen: boolean;
};

export function SecurityPanel({
  merkleRoot,
  leaf,
  proofDepth,
  whitelistSize,
  eligible,
  hasVoted,
  isOpen
}: SecurityPanelProps) {
  // 检查项来自链上状态和本地 proof 匹配结果，用于向用户解释投票按钮为何可用或不可用。
  const checks = [
    { label: "白名单资格", value: eligible ? "证明匹配" : "未匹配", ok: eligible },
    { label: "重复投票", value: hasVoted ? "已投票" : "未投票", ok: !hasVoted },
    { label: "投票窗口", value: isOpen ? "开放中" : "已截止", ok: isOpen },
    { label: "候选项索引", value: "合约校验", ok: true }
  ];

  return (
    <section className="panel security-panel">
      <div className="panel-heading">
        <span>资格与安全校验</span>
        <strong>白名单证明</strong>
      </div>
      <div className="security-layout">
        <div className="proof-card">
          <p className="panel-label">默克尔根</p>
          <strong>{merkleRoot || "未记录"}</strong>
          <p className="panel-label">当前账户叶子节点</p>
          <span>{shortenAddress(leaf, "连接白名单账户后显示")}</span>
          <div className="proof-depth">
            <b>{proofDepth}</b>
            <small>证明深度 / 白名单 {whitelistSize || 0} 个地址</small>
          </div>
        </div>
        <div className="security-checks">
          {checks.map((check) => (
            <div className={`security-check ${check.ok ? "check-ok" : "check-warn"}`} key={check.label}>
              <span>{check.label}</span>
              <strong>{check.value}</strong>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
