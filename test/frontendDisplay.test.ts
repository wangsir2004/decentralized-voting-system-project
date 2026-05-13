import { expect } from "chai";
import {
  countTotalVotes,
  getLeadingCandidate,
  getNetworkLabel,
  getProofDepth,
  formatWalletError,
  shortenAddress,
  summarizeAbiFunctions
} from "../shared/display";

describe("frontend display utilities", function () {
  // 这些测试约束前端展示格式，避免组件和合约集成时出现文案或数据转换回退。
  it("shortens an ethereum address for dense UI panels", function () {
    expect(shortenAddress("0x5FbDB2315678afecb367f032d93F642f64180aa3")).to.equal("0x5FbD...0aa3");
    expect(shortenAddress("")).to.equal("未连接");
  });

  it("maps known chain ids to readable labels", function () {
    expect(getNetworkLabel(31337)).to.equal("Hardhat 本地网络");
    expect(getNetworkLabel(11155111)).to.equal("Sepolia 测试网");
    expect(getNetworkLabel(null)).to.equal("未知网络");
  });

  it("derives vote totals and leading candidate", function () {
    const candidates = ["方案 A", "方案 B", "方案 C"];
    const counts = [2, 5, 1];

    expect(countTotalVotes(counts)).to.equal(8);
    expect(getLeadingCandidate(candidates, counts)).to.deep.equal({ name: "方案 B", count: 5 });
  });

  it("handles empty results without fabricating a leader", function () {
    expect(countTotalVotes([])).to.equal(0);
    expect(getLeadingCandidate([], [])).to.deep.equal({ name: "暂无数据", count: 0 });
  });

  it("returns merkle proof depth from the current proof", function () {
    expect(getProofDepth(["0xaaa", "0xbbb"])).to.equal(2);
    expect(getProofDepth([])).to.equal(0);
  });

  it("summarizes callable ABI functions with Chinese labels", function () {
    const abi = [
      { type: "function", name: "vote" },
      { type: "function", name: "getResults" },
      { type: "event", name: "VoteCast" }
    ];

    expect(summarizeAbiFunctions(abi)).to.deep.equal(["提交投票", "读取投票结果"]);
  });

  it("formats rejected MetaMask transactions as a short Chinese message", function () {
    // ethers 会附带较长的交易上下文，最终 UI 只保留用户能理解的取消提示。
    const error = new Error(
      'user rejected action (action="sendTransaction", reason="rejected", code=ACTION_REJECTED, message="MetaMask Tx Signature: User denied transaction signature.")'
    );

    expect(formatWalletError(error, "提交投票失败。")).to.equal("你已取消钱包确认，本次操作没有提交到链上。");
  });
});
