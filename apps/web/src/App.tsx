import { useEffect, useState } from "react";
import { AdminPanel } from "./components/AdminPanel";
import { CommandHero } from "./components/CommandHero";
import { EvidencePanel } from "./components/EvidencePanel";
import { ResultsChart } from "./components/ResultsChart";
import { SecurityPanel } from "./components/SecurityPanel";
import { VotingPanel } from "./components/VotingPanel";
import { WalletPanel } from "./components/WalletPanel";
import {
  activateLocalElection,
  clearLocalDeployment,
  DeploymentConfig,
  loadDeployment,
  loadPublicDeployment,
  loadVotingContractArtifact,
  readLocalElections,
  StoredElection,
  VotingContractArtifact
} from "./contracts/deployment";
import { FactoryElection, loadFactoryElections } from "./contracts/platform";
import { useWallet } from "./hooks/useWallet";
import { useVotingContract } from "./hooks/useVotingContract";
import {
  countTotalVotes,
  getLeadingCandidate,
  getNetworkLabel,
  getProofDepth,
  formatWalletError,
  summarizeAbiFunctions
} from "./utils/display";

export default function App() {
  const wallet = useWallet();
  const [deployment, setDeployment] = useState<DeploymentConfig | null>(null);
  const [platformDeployment, setPlatformDeployment] = useState<DeploymentConfig | null>(null);
  const [contractArtifact, setContractArtifact] = useState<VotingContractArtifact | null>(null);
  const [localElections, setLocalElections] = useState<StoredElection[]>([]);
  const [factoryElections, setFactoryElections] = useState<FactoryElection[]>([]);
  const [view, setView] = useState<"vote" | "admin">(() => (window.location.hash === "#admin" ? "admin" : "vote"));
  const [deploymentError, setDeploymentError] = useState("");
  const voting = useVotingContract(deployment, wallet.account);
  // 这些派生数据只服务展示层，原始链上数据仍保存在 voting 和 deployment 状态中。
  const totalVotes = countTotalVotes(voting.counts);
  const leadingCandidate = getLeadingCandidate(voting.candidates, voting.counts);
  const networkLabel = getNetworkLabel(wallet.chainId);
  const proofDepth = getProofDepth(voting.proof);
  const abiFunctions = deployment ? summarizeAbiFunctions(deployment.abi).slice(0, 8) : [];
  const networkReady = Boolean(deployment && wallet.chainId === deployment.chainId);
  const visibleFactoryElections = factoryElections.filter((election) => !election.archived);

  useEffect(() => {
    // 前端启动时读取 public/deployment.json，失败时保留页面并展示错误提示。
    async function boot() {
      try {
        const publicDeployment = await loadPublicDeployment();
        setPlatformDeployment(publicDeployment);
        const elections = await loadFactoryElections(publicDeployment);
        setFactoryElections(elections);
        const visibleElections = elections.filter((election) => !election.archived);
        const loadedDeployment = await loadDeployment();
        const loadedId = `${loadedDeployment.chainId}:${loadedDeployment.address.toLowerCase()}`;
        const matchingElection = visibleElections.find((election) => election.id === loadedId);

        setDeployment(loadedDeployment.source === "local"
          ? loadedDeployment
          : matchingElection?.deployment ?? visibleElections[0]?.deployment ?? publicDeployment);
      } catch (error) {
        setDeploymentError(formatWalletError(error, "读取部署配置失败。"));
      }
    }

    void boot();

    loadVotingContractArtifact()
      .then(setContractArtifact)
      .catch((error) => setDeploymentError(formatWalletError(error, "读取合约字节码失败。")));

    setLocalElections(readLocalElections());
  }, []);

  useEffect(() => {
    const syncViewFromHash = () => setView(window.location.hash === "#admin" ? "admin" : "vote");
    window.addEventListener("hashchange", syncViewFromHash);
    return () => window.removeEventListener("hashchange", syncViewFromHash);
  }, []);

  function openView(nextView: "vote" | "admin") {
    setView(nextView);
    window.history.replaceState(null, "", nextView === "admin" ? "#admin" : window.location.pathname);
  }

  function handleElectionCreated(nextDeployment: DeploymentConfig) {
    setDeployment(nextDeployment);
    setLocalElections(readLocalElections());
    void refreshFactoryElections(platformDeployment ?? nextDeployment);
    openView("vote");
  }

  function selectLocalElection(id: string) {
    const nextDeployment = activateLocalElection(id);
    if (nextDeployment) {
      setDeployment(nextDeployment);
      openView("vote");
    }
  }

  async function resetPublicDeployment() {
    clearLocalDeployment();
    setDeploymentError("");

    try {
      const publicDeployment = await loadPublicDeployment();
      setPlatformDeployment(publicDeployment);
      const elections = await loadFactoryElections(publicDeployment);
      setFactoryElections(elections);
      const visibleElections = elections.filter((election) => !election.archived);
      setDeployment(visibleElections[0]?.deployment ?? publicDeployment);
      openView("vote");
    } catch (error) {
      setDeploymentError(formatWalletError(error, "恢复默认部署配置失败。"));
    }
  }

  async function refreshFactoryElections(baseDeployment = platformDeployment ?? deployment) {
    if (!baseDeployment) return;

    try {
      const elections = await loadFactoryElections(baseDeployment);
      setFactoryElections(elections);
      const visibleElections = elections.filter((election) => !election.archived);
      if (visibleElections.length) {
        setDeployment(visibleElections[0].deployment);
      }
    } catch (error) {
      setDeploymentError(formatWalletError(error, "读取平台投票列表失败。"));
    }
  }

  function selectFactoryElection(id: string) {
    const election = factoryElections.find((item) => item.id === id);
      if (election) {
        setDeployment(election.deployment);
      openView("vote");
    }
  }

  return (
    <main className="app-shell">
      <header className="top-hud">
        <div className="brand-lockup">
          <span className="brand-mark" />
          <span>去中心化电子投票系统</span>
        </div>
        <div className="hud-ticker">
          {/* 展示合约核心调用路径，便于演示时快速说明投票链路。 */}
          链上规则：白名单根 / 投票提交 / 投票事件记录 / 结果公开查询
        </div>
        <div className="hud-tags">
          <span>智能合约</span>
          <span>以太坊测试网</span>
          <span>钱包签名</span>
          <button type="button" className="hud-action" onClick={() => openView(view === "admin" ? "vote" : "admin")}>
            {view === "admin" ? "返回投票大厅" : "创建/管理投票"}
          </button>
        </div>
      </header>

      {view === "admin" ? (
        <AdminPanel
          account={wallet.account}
          chainId={wallet.chainId}
          artifact={contractArtifact}
          activeDeployment={deployment}
          platformDeployment={platformDeployment}
          factoryElections={visibleFactoryElections}
          archivedFactoryElections={factoryElections.filter((election) => election.archived)}
          localElections={localElections}
          onElectionCreated={handleElectionCreated}
          onRefreshFactoryElections={() => refreshFactoryElections()}
          onSelectFactoryElection={selectFactoryElection}
          onSelectElection={selectLocalElection}
          onResetPublicDeployment={resetPublicDeployment}
        />
      ) : (
        <>
          <CommandHero
            deployment={deployment}
            account={wallet.account}
            chainId={wallet.chainId}
            networkLabel={networkLabel}
            totalVotes={totalVotes}
            leadingCandidate={leadingCandidate}
            whitelistSize={voting.whitelistSize}
            proofDepth={proofDepth}
          />

          <section className="operation-grid">
            <WalletPanel
              account={wallet.account}
              chainId={wallet.chainId}
              expectedChainId={deployment?.chainId ?? null}
              isConnecting={wallet.isConnecting}
              error={wallet.error || deploymentError}
              onConnect={wallet.connect}
            />

            {deployment && (
              <VotingPanel
                title={deployment.title}
                votingEndTime={deployment.votingEndTime}
                account={wallet.account}
                candidates={voting.candidates}
                counts={voting.counts}
                isOpen={voting.isOpen}
                eligible={voting.eligible}
                hasVoted={voting.hasVoted}
                networkReady={networkReady}
                isSubmitting={voting.isSubmitting}
                txHash={voting.txHash}
                error={voting.error}
                onSubmit={voting.submitVote}
              />
            )}
          </section>

          {deployment && (
            // 部署配置可用后再展示需要链上地址和 ABI 的结果与安全面板。
            <>
              <section className="results-grid">
                <ResultsChart candidates={voting.candidates} counts={voting.counts} />
                <EvidencePanel
                  deployment={deployment}
                  totalVotes={totalVotes}
                  leadingCandidate={leadingCandidate}
                  abiFunctions={abiFunctions}
                />
              </section>
              <SecurityPanel
                merkleRoot={deployment.merkleRoot}
                leaf={voting.leaf}
                proofDepth={proofDepth}
                whitelistSize={voting.whitelistSize}
                eligible={voting.eligible}
                hasVoted={voting.hasVoted}
                isOpen={voting.isOpen}
              />
            </>
          )}
        </>
      )}

      {!deployment && (
        <section className="panel loading-panel">
          <div className="panel-heading">
            <span>部署配置</span>
            <strong>读取中</strong>
          </div>
          <p>{deploymentError || "正在读取链上部署配置..."}</p>
        </section>
      )}
    </main>
  );
}
