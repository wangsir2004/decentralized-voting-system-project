import { useState } from "react";

type VotingPanelProps = {
  title: string;
  votingEndTime: number;
  account: string;
  candidates: string[];
  counts: number[];
  isOpen: boolean;
  eligible: boolean;
  hasVoted: boolean;
  networkReady: boolean;
  isSubmitting: boolean;
  txHash: string;
  error: string;
  onSubmit: (candidateIndex: number) => void;
};

export function VotingPanel({
  title,
  votingEndTime,
  account,
  candidates,
  counts,
  isOpen,
  eligible,
  hasVoted,
  networkReady,
  isSubmitting,
  txHash,
  error,
  onSubmit
}: VotingPanelProps) {
  const [selected, setSelected] = useState(0);
  // 禁用条件与合约 require 顺序保持一致，尽量在前端先给出明确提示。
  const disabled = !account || !networkReady || !isOpen || !eligible || hasVoted || isSubmitting || !candidates.length;
  const disabledReason = !account
    ? "连接钱包后可投票"
    : !networkReady
      ? "请切换到目标网络"
      : !isOpen
        ? "投票已截止"
        : !eligible
          ? "当前账户不在白名单中"
          : hasVoted
            ? "当前账户已投票"
            : isSubmitting
              ? "等待交易确认"
              : "资格通过，可提交投票";

  return (
    <section className="panel voting-panel operation-panel">
      <div className="panel-heading">
        <span>投票提交</span>
        <strong>{disabled ? "暂不可投" : "可以投票"}</strong>
      </div>
      <p className="panel-label">链上投票</p>
      <h2>{title}</h2>
      <p className="muted-text">截止时间：{new Date(votingEndTime * 1000).toLocaleString()}</p>
      <div className="status-grid">
        <span className={isOpen ? "status-ok" : "status-danger"}>{isOpen ? "投票开放中" : "投票已截止"}</span>
        <span className={eligible ? "status-ok" : "status-warn"}>
          {eligible ? "白名单证明匹配" : "白名单未匹配"}
        </span>
        <span className={hasVoted ? "status-warn" : "status-ok"}>
          {hasVoted ? "当前账户已投票" : "当前账户未投票"}
        </span>
      </div>

      <div className="candidate-list">
        {/* 候选项顺序即合约中的 candidateIndex，提交时直接传入当前索引。 */}
        {candidates.map((candidate, index) => (
          <label className="candidate-item" key={candidate}>
            <input
              type="radio"
              name="candidate"
              checked={selected === index}
              onChange={() => setSelected(index)}
            />
            <span className="candidate-index">#{index + 1}</span>
            <span className="candidate-name">{candidate}</span>
            <strong>{counts[index] ?? 0} 票</strong>
          </label>
        ))}
      </div>

      <button className="primary-button" disabled={disabled} onClick={() => onSubmit(selected)}>
        {isSubmitting ? "交易确认中..." : "提交投票"}
      </button>
      <p className="hint-text">{disabledReason}</p>

      {txHash && <p className="hint-text">交易哈希：{txHash}</p>}
      {error && <p className="error-text">{error}</p>}
    </section>
  );
}
