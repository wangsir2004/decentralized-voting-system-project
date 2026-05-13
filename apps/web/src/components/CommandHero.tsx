import type { DeploymentConfig } from "../contracts/deployment";
import type { LeadingCandidate } from "../utils/display";
import { shortenAddress } from "../utils/display";
import { ShowcaseMetric } from "./ShowcaseMetric";

type CommandHeroProps = {
  deployment: DeploymentConfig | null;
  account: string;
  chainId: number | null;
  networkLabel: string;
  totalVotes: number;
  leadingCandidate: LeadingCandidate;
  whitelistSize: number;
  proofDepth: number;
};

export function CommandHero({
  deployment,
  account,
  chainId,
  networkLabel,
  totalVotes,
  leadingCandidate,
  whitelistSize,
  proofDepth
}: CommandHeroProps) {
  // 部署信息加载前先使用空字符串，让 shortenAddress 负责展示占位文案。
  const contractAddress = deployment?.address ?? "";
  const merkleRoot = deployment?.merkleRoot ?? "";
  const deployHash = deployment?.deploymentTransactionHash ?? "";

  return (
    <section className="command-hero">
      <article className="hero-intro panel">
        <p className="eyebrow">基于智能合约的电子投票系统</p>
        <h1>去中心化电子投票系统</h1>
        <p className="hero-copy">
          系统面向传统中心化投票中的单点故障、数据易被干预和计票效率不足等问题，
          通过钱包签名、默克尔白名单、智能合约计票和链上结果公开查询，完成安全、透明、高效的投票闭环。
        </p>
        <div className="metric-grid">
          <ShowcaseMetric label="当前网络" value={networkLabel} detail={`链编号：${chainId ?? "未知"}`} />
          <ShowcaseMetric
            label="合约地址"
            value={shortenAddress(contractAddress, "读取中")}
            detail={deployment ? "投票智能合约" : "等待部署信息"}
            tone="gold"
          />
          <ShowcaseMetric label="累计票数" value={totalVotes} detail={`领先：${leadingCandidate.name}`} />
          <ShowcaseMetric
            label="白名单证明"
            value={`${proofDepth}/${whitelistSize || 0}`}
            detail={account ? "当前账户证明深度" : "连接钱包后校验"}
          />
        </div>
      </article>

      <article className="chain-map panel">
        <div className="panel-heading">
          <span>链上投票流程</span>
          <strong>{deployment ? "合约已部署" : "等待部署信息"}</strong>
        </div>
        <div className="chain-ring ring-one" />
        <div className="chain-ring ring-two" />
        {/* 拓扑线条只负责视觉表达，不参与任何链上状态计算。 */}
        <div className="chain-link link-wallet" />
        <div className="chain-link link-root" />
        <div className="chain-link link-proof" />
        <div className="chain-link link-event" />
        <div className="chain-link link-chart" />
        <div className="core-node">
          <span>投票智能合约</span>
          <small>{shortenAddress(contractAddress, "等待合约地址")}</small>
        </div>
        <div className="map-node node-wallet">钱包<br />签名</div>
        <div className="map-node node-root gold">默克尔<br />根</div>
        <div className="map-node node-proof">资格<br />证明</div>
        <div className="map-node node-event">投票<br />事件</div>
        <div className="map-node node-result gold">实时<br />结果</div>
        <div className="hash-strip">
          <span>白名单根：{shortenAddress(merkleRoot, "未记录")}</span>
          <span>部署交易：{shortenAddress(deployHash, "未记录")}</span>
        </div>
      </article>

      <aside className="contract-terminal panel">
        <div className="terminal-head">
          <span>合约执行记录</span>
          <strong>已校验</strong>
        </div>
        <div className="terminal-lines">
          <p><span>1</span> 部署脚本已生成投票合约</p>
          <p className="gold">合约地址：{shortenAddress(contractAddress, "等待中")}</p>
          <p>提交投票：选择候选项并附带白名单证明</p>
          <p>资格校验：账户属于白名单</p>
          <p>重复校验：当前地址尚未投票</p>
          <p className="danger">拒绝：无效证明、重复投票或超过截止时间</p>
        </div>
      </aside>
    </section>
  );
}
