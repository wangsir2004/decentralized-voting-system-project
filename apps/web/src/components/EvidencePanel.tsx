import type { DeploymentConfig } from "../contracts/deployment";
import type { LeadingCandidate } from "../utils/display";
import { getNetworkLabel, shortenAddress } from "../utils/display";
import { ShowcaseMetric } from "./ShowcaseMetric";

type EvidencePanelProps = {
  deployment: DeploymentConfig;
  totalVotes: number;
  leadingCandidate: LeadingCandidate;
  abiFunctions: string[];
};

export function EvidencePanel({ deployment, totalVotes, leadingCandidate, abiFunctions }: EvidencePanelProps) {
  return (
    <section className="evidence-grid">
      <article className="panel evidence-panel">
        <div className="panel-heading">
          <span>链上证据</span>
          <strong>部署记录</strong>
        </div>
        <div className="data-list">
          {/* 部署产物字段逐项展示，便于核对网络、地址、交易和 Gas 信息。 */}
          <div className="data-row"><span>部署网络</span><strong>{getNetworkLabel(deployment.chainId)} / {deployment.chainId}</strong></div>
          <div className="data-row"><span>合约地址</span><strong>{deployment.address}</strong></div>
          <div className="data-row"><span>部署账户</span><strong>{deployment.deployer}</strong></div>
          <div className="data-row"><span>部署交易哈希</span><strong>{deployment.deploymentTransactionHash || "未记录"}</strong></div>
          <div className="data-row"><span>部署燃料消耗</span><strong>{deployment.deploymentGasUsed ? `${deployment.deploymentGasUsed} 单位` : "未记录"}</strong></div>
          <div className="data-row"><span>部署时间</span><strong>{deployment.deployedAt || "未记录"}</strong></div>
        </div>
      </article>

      <article className="panel audit-panel">
        <div className="panel-heading">
          <span>结果审计</span>
          <strong>只读链上状态</strong>
        </div>
        <div className="metric-grid compact">
          <ShowcaseMetric label="总票数" value={totalVotes} />
          <ShowcaseMetric label="领先项" value={leadingCandidate.name} detail={`${leadingCandidate.count} 票`} tone="gold" />
          <ShowcaseMetric label="候选项" value={deployment.candidates.length} />
          <ShowcaseMetric label="合约" value={shortenAddress(deployment.address)} detail="投票智能合约" />
        </div>
        <div className="abi-cloud">
          {/* ABI 函数列表用于审计展示，只显示可调用函数名。 */}
          {abiFunctions.map((name) => (
            <span key={name}>{name}</span>
          ))}
        </div>
      </article>
    </section>
  );
}
