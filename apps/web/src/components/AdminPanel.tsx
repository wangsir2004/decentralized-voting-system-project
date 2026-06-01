import { useMemo, useState } from "react";
import { BrowserProvider, Contract } from "ethers";
import { buildWhitelistFromAddresses } from "../../../../shared/merkle";
import {
  type DeploymentConfig,
  type StoredElection,
  type VotingContractArtifact,
  type WhitelistFile
} from "../contracts/deployment";
import type { FactoryElection } from "../contracts/platform";
import { formatWalletError, getNetworkLabel, shortenAddress } from "../utils/display";

type AdminPanelProps = {
  account: string;
  chainId: number | null;
  artifact: VotingContractArtifact | null;
  activeDeployment: DeploymentConfig | null;
  platformDeployment: DeploymentConfig | null;
  factoryElections: FactoryElection[];
  archivedFactoryElections: FactoryElection[];
  localElections: StoredElection[];
  onElectionCreated: (deployment: DeploymentConfig) => void;
  onRefreshFactoryElections: () => void;
  onSelectFactoryElection: (id: string) => void;
  onSelectElection: (id: string) => void;
  onResetPublicDeployment: () => void;
};

function splitLines(value: string) {
  return value
    .split(/[\s,，;；]+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function downloadJson(filename: string, data: unknown) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function deploymentForExport(deployment: DeploymentConfig) {
  const { source: _source, ...publicDeployment } = deployment;
  return publicDeployment;
}

export function AdminPanel({
  account,
  chainId,
  artifact,
  activeDeployment,
  platformDeployment,
  factoryElections,
  archivedFactoryElections,
  localElections,
  onElectionCreated,
  onRefreshFactoryElections,
  onSelectFactoryElection,
  onSelectElection,
  onResetPublicDeployment
}: AdminPanelProps) {
  const [title, setTitle] = useState("基于智能合约的去中心化电子投票");
  const [candidates, setCandidates] = useState(["方案 A", "方案 B", "方案 C"]);
  const [durationHours, setDurationHours] = useState(72);
  const [whitelistText, setWhitelistText] = useState(
    [
      "0x372ee50901D62F3b314936C9302b19F8F477716E",
      "0x223c397328A746dF817aAE4958a83Df9A7c1Cb97",
      "0x253f4a33c6e1920bA081200394B6EC10a729696B"
    ].join("\n")
  );
  const [isDeploying, setIsDeploying] = useState(false);
  const [archivingId, setArchivingId] = useState("");
  const [error, setError] = useState("");
  const [pendingHash, setPendingHash] = useState("");
  const [existingElectionAddress, setExistingElectionAddress] = useState("");
  const [lastDeployment, setLastDeployment] = useState<DeploymentConfig | null>(null);
  const [lastWhitelist, setLastWhitelist] = useState<WhitelistFile | null>(null);

  const normalizedCandidates = useMemo(
    () => candidates.map((candidate) => candidate.trim()).filter(Boolean),
    [candidates]
  );

  const whitelistPreview = useMemo(() => {
    try {
      return buildWhitelistFromAddresses(splitLines(whitelistText));
    } catch {
      return null;
    }
  }, [whitelistText]);
  const activeElectionId = activeDeployment ? `${activeDeployment.chainId}:${activeDeployment.address.toLowerCase()}` : "";
  const platform = platformDeployment?.factoryAddress ? platformDeployment : activeDeployment;

  function updateCandidate(index: number, value: string) {
    setCandidates((current) => current.map((candidate, candidateIndex) => (
      candidateIndex === index ? value : candidate
    )));
  }

  function removeCandidate(index: number) {
    setCandidates((current) => current.filter((_, candidateIndex) => candidateIndex !== index));
  }

  function addCandidate() {
    setCandidates((current) => [...current, `方案 ${current.length + 1}`]);
  }

  async function deployElection() {
    if (!window.ethereum) {
      setError("未检测到浏览器钱包，不能从前端部署合约。");
      return;
    }

    if (!artifact) {
      setError("缺少 VotingSystem 合约字节码，请先运行 npm run export:frontend。");
      return;
    }

    if (!platform?.factoryAddress || !platform.factoryAbi?.length) {
      setError("当前前端没有平台工厂合约地址，请重新部署并导出前端配置。");
      return;
    }

    if (!title.trim()) {
      setError("投票标题不能为空。");
      return;
    }

    if (normalizedCandidates.length < 2) {
      setError("候选项至少需要 2 个。");
      return;
    }

    if (!Number.isFinite(durationHours) || durationHours <= 0) {
      setError("投票时长必须大于 0。");
      return;
    }

    setIsDeploying(true);
    setError("");
    setPendingHash("");

    try {
      const whitelist = buildWhitelistFromAddresses(splitLines(whitelistText));
      const provider = new BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const deployer = await signer.getAddress();
      const network = await provider.getNetwork();
      const targetChainId = Number(network.chainId);
      const votingEndTime = Math.floor(Date.now() / 1000) + Math.round(durationHours * 60 * 60);
      const voterAddresses = whitelist.voters.map((entry) => entry.address);
      const factory = new Contract(platform.factoryAddress, platform.factoryAbi, signer);
      const tx = await factory.createElection(title.trim(), normalizedCandidates, votingEndTime, whitelist.merkleRoot, voterAddresses);

      setPendingHash(tx.hash);
      const receipt = await tx.wait();
      const count = Number(await factory.getElectionCount());
      const electionId = count - 1;
      const record = await factory.getElection(electionId);
      const address = typeof record.election === "string" ? record.election : record[0];

      const deployment: DeploymentConfig = {
        network: targetChainId === 11155111 ? "sepolia" : `chain-${targetChainId}`,
        chainId: targetChainId,
        contractName: artifact.contractName || "VotingSystem",
        address,
        deployer,
        title: title.trim(),
        candidates: normalizedCandidates,
        votingEndTime,
        merkleRoot: whitelist.merkleRoot,
        deploymentTransactionHash: tx?.hash ?? "",
        deploymentGasUsed: receipt?.gasUsed?.toString() ?? "",
        factoryAddress: platform.factoryAddress,
        factoryAbi: platform.factoryAbi,
        factoryDeploymentTransactionHash: platform.factoryDeploymentTransactionHash,
        factoryDeploymentGasUsed: platform.factoryDeploymentGasUsed,
        deployedAt: new Date().toISOString(),
        abi: artifact.abi,
        source: "factory",
        voters: voterAddresses,
        electionId
      };

      setLastDeployment(deployment);
      setLastWhitelist(whitelist);
      onElectionCreated(deployment);
    } catch (caught) {
      setError(formatWalletError(caught, "前端部署投票合约失败。"));
    } finally {
      setIsDeploying(false);
    }
  }

  async function registerExistingElection() {
    if (!window.ethereum) {
      setError("未检测到浏览器钱包，不能登记已有合约。");
      return;
    }

    if (!artifact) {
      setError("缺少 VotingSystem 合约 ABI，请先运行 npm run export:frontend。");
      return;
    }

    if (!platform?.factoryAddress || !platform.factoryAbi?.length) {
      setError("当前前端没有平台工厂合约地址，请重新部署并导出前端配置。");
      return;
    }

    setIsDeploying(true);
    setError("");
    setPendingHash("");

    try {
      const whitelist = buildWhitelistFromAddresses(splitLines(whitelistText));
      const provider = new BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const deployer = await signer.getAddress();
      const network = await provider.getNetwork();
      const targetChainId = Number(network.chainId);
      const voterAddresses = whitelist.voters.map((entry) => entry.address);
      const factory = new Contract(platform.factoryAddress, platform.factoryAbi, signer);
      const tx = await factory.registerElection(existingElectionAddress.trim(), voterAddresses);

      setPendingHash(tx.hash);
      const receipt = await tx.wait();
      const count = Number(await factory.getElectionCount());
      const electionId = count - 1;
      const record = await factory.getElection(electionId);
      const address = typeof record.election === "string" ? record.election : record[0];
      const voting = new Contract(address, artifact.abi, provider);
      const chainCandidates = await voting.getCandidates();

      const deployment: DeploymentConfig = {
        network: targetChainId === 11155111 ? "sepolia" : `chain-${targetChainId}`,
        chainId: targetChainId,
        contractName: artifact.contractName || "VotingSystem",
        address,
        deployer,
        title: typeof record.title === "string" ? record.title : String(record[2] ?? ""),
        candidates: [...chainCandidates],
        votingEndTime: Number(record.votingEndTime ?? record[3]),
        merkleRoot: typeof record.merkleRoot === "string" ? record.merkleRoot : String(record[4] ?? ""),
        deploymentTransactionHash: tx.hash,
        deploymentGasUsed: receipt?.gasUsed?.toString() ?? "",
        factoryAddress: platform.factoryAddress,
        factoryAbi: platform.factoryAbi,
        factoryDeploymentTransactionHash: platform.factoryDeploymentTransactionHash,
        factoryDeploymentGasUsed: platform.factoryDeploymentGasUsed,
        deployedAt: new Date().toISOString(),
        abi: artifact.abi,
        source: "factory",
        voters: voterAddresses,
        electionId
      };

      setLastDeployment(deployment);
      setLastWhitelist(whitelist);
      onElectionCreated(deployment);
    } catch (caught) {
      setError(formatWalletError(caught, "登记已有投票合约失败。"));
    } finally {
      setIsDeploying(false);
    }
  }

  async function setFactoryElectionArchived(election: FactoryElection, archived: boolean) {
    if (!window.ethereum) {
      setError("未检测到浏览器钱包，不能归档投票记录。");
      return;
    }

    if (!platform?.factoryAddress || !platform.factoryAbi?.length) {
      setError("当前前端没有平台工厂合约地址，请重新部署并导出前端配置。");
      return;
    }

    const electionId = election.deployment.electionId;
    if (typeof electionId !== "number") {
      setError("该投票缺少链上编号，不能归档。");
      return;
    }

    setArchivingId(election.id);
    setError("");

    try {
      const provider = new BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const factory = new Contract(platform.factoryAddress, platform.factoryAbi, signer);
      const tx = await factory.setElectionArchived(electionId, archived);
      await tx.wait();
      onRefreshFactoryElections();
    } catch (caught) {
      setError(formatWalletError(caught, archived ? "归档投票记录失败。" : "恢复投票记录失败。"));
    } finally {
      setArchivingId("");
    }
  }

  function renderFactoryElectionRow(election: FactoryElection, archived: boolean) {
    return (
      <div className="contract-card" key={election.id}>
        <button
          type="button"
          className="contract-row"
          onClick={() => onSelectFactoryElection(election.id)}
        >
          <span>
            <b>{election.deployment.title}</b>
            <small>{election.deployment.address}</small>
          </span>
          <strong>{activeElectionId === election.id ? "当前使用" : "切换"}</strong>
        </button>
        <div className="contract-actions">
          <button
            type="button"
            className="secondary-button"
            disabled={Boolean(archivingId)}
            onClick={() => setFactoryElectionArchived(election, !archived)}
          >
            {archivingId === election.id ? "等待确认..." : archived ? "恢复显示" : "归档隐藏"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <section className="panel admin-panel">
      <div className="panel-heading">
        <span>投票管理后台</span>
        <strong>{activeDeployment?.source === "local" ? "本机新部署" : "默认部署"}</strong>
      </div>

      <div className="admin-layout">
        <div className="admin-form">
          <div className="contract-manager">
            <div className="panel-heading compact-heading">
              <span>合约切换</span>
              <strong>链上列表</strong>
            </div>
            <button type="button" className="contract-row" onClick={onResetPublicDeployment}>
              <span>
                <b>默认部署合约</b>
                <small>来自服务器 deployment.json，可作为平台入口</small>
              </span>
              <strong>{activeDeployment?.source === "public" ? "当前使用" : "切换"}</strong>
            </button>
            <button type="button" className="secondary-button" onClick={onRefreshFactoryElections}>
              刷新链上投票列表
            </button>

            {factoryElections.length ? (
              factoryElections.map((election) => renderFactoryElectionRow(election, false))
            ) : (
              <p className="hint-text">平台工厂里还没有读到链上投票。创建成功后，其他电脑刷新网站也能读取这条记录。</p>
            )}

            {archivedFactoryElections.length ? <p className="panel-label">已归档记录</p> : null}
            {archivedFactoryElections.map((election) => renderFactoryElectionRow(election, true))}

            {localElections.length ? <p className="panel-label">本机旧版历史</p> : null}

            {localElections.length ? (
              localElections.map((election) => (
                <div className="contract-card" key={election.id}>
                  <button
                    type="button"
                    className="contract-row"
                    onClick={() => onSelectElection(election.id)}
                  >
                    <span>
                      <b>{election.deployment.title}</b>
                      <small>{election.deployment.address}</small>
                    </span>
                    <strong>{activeElectionId === election.id ? "当前使用" : "切换"}</strong>
                  </button>
                  <div className="contract-actions">
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => downloadJson("deployment.json", deploymentForExport(election.deployment))}
                    >
                      导出部署配置
                    </button>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => downloadJson("whitelist.json", election.whitelist)}
                    >
                      导出白名单
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <p className="hint-text">本机还没有从前端部署过新投票。部署成功后会在这里保留历史，旧合约不会消失。</p>
            )}
          </div>

          <label className="form-field">
            <span>投票标题</span>
            <input value={title} onChange={(event) => setTitle(event.target.value)} />
          </label>

          <div className="form-field">
            <span>候选项</span>
            <div className="candidate-editor">
              {candidates.map((candidate, index) => (
                <div className="candidate-editor-row" key={index}>
                  <input value={candidate} onChange={(event) => updateCandidate(index, event.target.value)} />
                  <button type="button" className="ghost-button" onClick={() => removeCandidate(index)} disabled={candidates.length <= 2}>
                    删除
                  </button>
                </div>
              ))}
              <button type="button" className="secondary-button" onClick={addCandidate}>添加候选项</button>
            </div>
          </div>

          <label className="form-field">
            <span>投票时长（小时）</span>
            <input
              type="number"
              min="1"
              step="1"
              value={durationHours}
              onChange={(event) => setDurationHours(Number(event.target.value))}
            />
          </label>

          <label className="form-field">
            <span>白名单地址</span>
            <textarea value={whitelistText} onChange={(event) => setWhitelistText(event.target.value)} rows={5} />
          </label>

          <button className="primary-button" disabled={isDeploying || !account} onClick={deployElection}>
            {isDeploying ? "等待钱包确认和链上部署..." : "用钱包部署新投票合约"}
          </button>

          <div className="import-existing">
            <label className="form-field">
              <span>登记已有投票合约地址</span>
              <input
                value={existingElectionAddress}
                onChange={(event) => setExistingElectionAddress(event.target.value)}
                placeholder="0x..."
              />
            </label>
            <button className="secondary-button" disabled={isDeploying || !account || !existingElectionAddress.trim()} onClick={registerExistingElection}>
              把已有合约登记到平台
            </button>
          </div>
        </div>

        <div className="admin-summary">
          <div className="data-list">
            <div className="data-row"><span>当前钱包</span><strong>{shortenAddress(account)}</strong></div>
            <div className="data-row"><span>当前网络</span><strong>{getNetworkLabel(chainId)}</strong></div>
            <div className="data-row"><span>候选项数量</span><strong>{normalizedCandidates.length}</strong></div>
            <div className="data-row"><span>白名单数量</span><strong>{whitelistPreview?.voters.length ?? "地址待校验"}</strong></div>
            <div className="data-row"><span>默克尔根</span><strong>{whitelistPreview?.merkleRoot ?? "地址有效后自动生成"}</strong></div>
            <div className="data-row"><span>当前合约</span><strong>{activeDeployment?.address ?? "未读取"}</strong></div>
          </div>

          <p className="hint-text">
            这里不是修改旧合约，而是通过平台工厂创建一个新的投票合约，并把投票地址、标题、截止时间和白名单地址写入链上注册表。其他电脑打开同一网站后可以从链上读取这条投票记录。
          </p>

          {pendingHash && <p className="hint-text">部署交易 Hash：{pendingHash}</p>}
          {lastDeployment && lastWhitelist && (
            <div className="export-actions">
              <button type="button" className="secondary-button" onClick={() => downloadJson("deployment.json", deploymentForExport(lastDeployment))}>
                导出 deployment.json
              </button>
              <button type="button" className="secondary-button" onClick={() => downloadJson("whitelist.json", lastWhitelist)}>
                导出 whitelist.json
              </button>
            </div>
          )}
          {error && <p className="error-text">{error}</p>}
        </div>
      </div>
    </section>
  );
}
