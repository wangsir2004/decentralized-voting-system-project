import { expect } from "chai";
import { ethers } from "hardhat";
import { buildWhitelistFromAddresses } from "../shared/merkle";

async function latestTimestamp() {
  const block = await ethers.provider.getBlock("latest");
  if (!block) throw new Error("latest block not found");
  return block.timestamp;
}

describe("VotingFactory", function () {
  async function deployFixture() {
    const [creator, voterA, voterB] = await ethers.getSigners();
    const whitelist = buildWhitelistFromAddresses([voterA.address, voterB.address]);
    const endTime = (await latestTimestamp()) + 3600;
    const candidates = ["候选项 A", "候选项 B"];

    const VotingFactory = await ethers.getContractFactory("VotingFactory");
    const factory = await VotingFactory.deploy();

    return { factory, creator, voterA, voterB, whitelist, endTime, candidates };
  }

  it("creates an election contract and stores registry metadata", async function () {
    const { factory, creator, voterA, voterB, whitelist, endTime, candidates } = await deployFixture();

    await expect(factory.createElection("平台投票", candidates, endTime, whitelist.merkleRoot, [voterA.address, voterB.address]))
      .to.emit(factory, "ElectionCreated");

    expect(await factory.getElectionCount()).to.equal(1);
    const record = await factory.getElection(0);
    expect(record.creator).to.equal(creator.address);
    expect(record.title).to.equal("平台投票");
    expect(record.votingEndTime).to.equal(endTime);
    expect(record.merkleRoot).to.equal(whitelist.merkleRoot);
    expect(record.archived).to.equal(false);
    expect(await factory.getElectionVoters(0)).to.deep.equal([voterA.address, voterB.address]);
  });

  it("allows voters to use chain-listed whitelist addresses to rebuild proofs", async function () {
    const { factory, voterA, voterB, whitelist, endTime, candidates } = await deployFixture();

    await factory.createElection("平台投票", candidates, endTime, whitelist.merkleRoot, [voterA.address, voterB.address]);
    const record = await factory.getElection(0);
    const voters = await factory.getElectionVoters(0);
    const rebuiltWhitelist = buildWhitelistFromAddresses([...voters]);
    const voterEntry = rebuiltWhitelist.voters.find((entry) => entry.address === voterA.address);
    if (!voterEntry) throw new Error("missing voter proof");

    const voting = await ethers.getContractAt("VotingSystem", record.election);
    await voting.connect(voterA).vote(0, voterEntry.proof);

    const [, counts] = await voting.getResults();
    expect(counts[0]).to.equal(1);
  });

  it("rejects creating an election without whitelist voters", async function () {
    const { factory, whitelist, endTime, candidates } = await deployFixture();

    await expect(factory.createElection("无白名单投票", candidates, endTime, whitelist.merkleRoot, []))
      .to.be.revertedWith("Voter whitelist is required");
  });

  it("registers an existing VotingSystem contract for platform discovery", async function () {
    const { factory, voterA, voterB, whitelist, endTime, candidates } = await deployFixture();
    const VotingSystem = await ethers.getContractFactory("VotingSystem");
    const voting = await VotingSystem.deploy("旧版投票", candidates, endTime, whitelist.merkleRoot);
    const votingAddress = await voting.getAddress();

    await expect(factory.registerElection(votingAddress, [voterA.address, voterB.address]))
      .to.emit(factory, "ElectionCreated");

    const record = await factory.getElection(0);
    expect(record.election).to.equal(votingAddress);
    expect(record.title).to.equal("旧版投票");
    expect(await factory.getElectionVoters(0)).to.deep.equal([voterA.address, voterB.address]);
    await expect(factory.registerElection(votingAddress, [voterA.address, voterB.address]))
      .to.be.revertedWith("Election already registered");
  });

  it("allows only the creator to archive and restore an election record", async function () {
    const { factory, voterA, voterB, whitelist, endTime, candidates } = await deployFixture();

    await factory.createElection("平台投票", candidates, endTime, whitelist.merkleRoot, [voterA.address, voterB.address]);
    await expect(factory.connect(voterA).setElectionArchived(0, true))
      .to.be.revertedWith("Only creator can archive election");

    await expect(factory.setElectionArchived(0, true))
      .to.emit(factory, "ElectionArchived")
      .withArgs(0, true);
    expect((await factory.getElection(0)).archived).to.equal(true);

    await factory.setElectionArchived(0, false);
    expect((await factory.getElection(0)).archived).to.equal(false);
  });
});
