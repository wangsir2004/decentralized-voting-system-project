import { expect } from "chai";
import { ethers, network } from "hardhat";
import { MerkleTree } from "merkletreejs";
import keccak256 from "keccak256";

function buildTree(addresses: string[]) {
  // 测试里的 leaf 生成方式与部署脚本、合约投票校验保持一致。
  const normalized = addresses.map((address) => ethers.getAddress(address));
  const leaves = normalized.map((address) => ethers.keccak256(ethers.solidityPacked(["address"], [address])));
  const tree = new MerkleTree(leaves, keccak256, { sortPairs: true });

  return {
    root: tree.getHexRoot(),
    proofFor(address: string) {
      const leaf = ethers.keccak256(ethers.solidityPacked(["address"], [ethers.getAddress(address)]));
      return tree.getHexProof(leaf);
    }
  };
}

async function latestTimestamp() {
  // 从最新区块读取时间戳，避免测试依赖本机时间造成链上时间偏差。
  const block = await ethers.provider.getBlock("latest");
  if (!block) throw new Error("latest block not found");
  return block.timestamp;
}

describe("VotingSystem", function () {
  async function deployFixture() {
    // fixture 统一准备两名白名单投票者和一名外部账户，覆盖正常与拒绝路径。
    const [, voterA, voterB, outsider] = await ethers.getSigners();
    const tree = buildTree([voterA.address, voterB.address]);
    const endTime = (await latestTimestamp()) + 3600;
    const candidates = ["Alice", "Bob", "Carol"];

    const VotingSystem = await ethers.getContractFactory("VotingSystem");
    const voting = await VotingSystem.deploy("Graduation Vote", candidates, endTime, tree.root);

    return { voting, voterA, voterB, outsider, tree, endTime, candidates };
  }

  it("initializes title, candidates, end time and merkle root", async function () {
    const { voting, endTime, candidates } = await deployFixture();

    expect(await voting.title()).to.equal("Graduation Vote");
    expect(await voting.votingEndTime()).to.equal(endTime);
    expect(await voting.getCandidates()).to.deep.equal(candidates);
    expect(await voting.isVotingOpen()).to.equal(true);
  });

  it("rejects deployment with fewer than two candidates", async function () {
    const [, voterA] = await ethers.getSigners();
    const tree = buildTree([voterA.address]);
    const endTime = (await latestTimestamp()) + 3600;
    const VotingSystem = await ethers.getContractFactory("VotingSystem");

    await expect(VotingSystem.deploy("Invalid Vote", ["Only One"], endTime, tree.root))
      .to.be.revertedWith("Invalid candidate count");
  });

  it("rejects deployment when end time is not in the future", async function () {
    const [, voterA] = await ethers.getSigners();
    const tree = buildTree([voterA.address]);
    const endTime = await latestTimestamp();
    const VotingSystem = await ethers.getContractFactory("VotingSystem");

    await expect(VotingSystem.deploy("Invalid Vote", ["Alice", "Bob"], endTime, tree.root))
      .to.be.revertedWith("Voting end time must be in the future");
  });

  it("allows a whitelisted voter to vote once", async function () {
    const { voting, voterA, tree } = await deployFixture();

    // 成功投票应同时触发事件、标记地址已投票并增加对应候选项票数。
    await expect(voting.connect(voterA).vote(1, tree.proofFor(voterA.address)))
      .to.emit(voting, "VoteCast")
      .withArgs(voterA.address, 1);

    expect(await voting.hasAddressVoted(voterA.address)).to.equal(true);
    const [, counts] = await voting.getResults();
    expect(counts[1]).to.equal(1);
  });

  it("rejects a non-whitelisted voter", async function () {
    const { voting, outsider } = await deployFixture();

    await expect(voting.connect(outsider).vote(0, [])).to.be.revertedWith("Address is not eligible");
  });

  it("rejects duplicate voting", async function () {
    const { voting, voterA, tree } = await deployFixture();
    const proof = tree.proofFor(voterA.address);

    await voting.connect(voterA).vote(0, proof);
    await expect(voting.connect(voterA).vote(1, proof)).to.be.revertedWith("Address has already voted");
  });

  it("rejects invalid candidate index", async function () {
    const { voting, voterA, tree } = await deployFixture();

    await expect(voting.connect(voterA).vote(99, tree.proofFor(voterA.address)))
      .to.be.revertedWith("Invalid candidate index");
  });

  it("rejects voting after the end time", async function () {
    const { voting, voterA, tree, endTime } = await deployFixture();

    // 直接推进 Hardhat 链上时间，验证截止时间由合约 block.timestamp 控制。
    await network.provider.send("evm_setNextBlockTimestamp", [endTime + 1]);
    await network.provider.send("evm_mine");

    await expect(voting.connect(voterA).vote(0, tree.proofFor(voterA.address)))
      .to.be.revertedWith("Voting has ended");
  });

  it("returns candidates and counts together", async function () {
    const { voting, voterA, voterB, tree, candidates } = await deployFixture();

    await voting.connect(voterA).vote(0, tree.proofFor(voterA.address));
    await voting.connect(voterB).vote(2, tree.proofFor(voterB.address));

    const [names, counts] = await voting.getResults();
    expect(names).to.deep.equal(candidates);
    expect(counts.map((count: bigint) => Number(count))).to.deep.equal([1, 0, 1]);
  });
});
