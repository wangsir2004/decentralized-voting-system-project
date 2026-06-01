import { expect } from "chai";
import { ethers } from "hardhat";
import { MerkleTree } from "merkletreejs";
import keccak256 from "keccak256";
import { buildWhitelistFromAddresses } from "../shared/merkle";

describe("shared merkle whitelist builder", function () {
  it("matches the existing merkletreejs whitelist format", function () {
    const voters = [
      "0x372ee50901D62F3b314936C9302b19F8F477716E",
      "0x223c397328A746dF817aAE4958a83Df9A7c1Cb97",
      "0x253f4a33c6e1920bA081200394B6EC10a729696B"
    ];
    const built = buildWhitelistFromAddresses(voters);
    const leaves = voters.map((address) => ethers.keccak256(ethers.solidityPacked(["address"], [ethers.getAddress(address)])));
    const tree = new MerkleTree(leaves, keccak256, { sortPairs: true });

    expect(built.merkleRoot).to.equal(tree.getHexRoot());
    expect(built.voters[2].proof).to.deep.equal(tree.getHexProof(leaves[2]));
  });

  it("rejects duplicate voter addresses before deployment", function () {
    expect(() => buildWhitelistFromAddresses([
      "0x372ee50901D62F3b314936C9302b19F8F477716E",
      "0x372ee50901D62F3b314936C9302b19F8F477716E"
    ])).to.throw("选民地址重复");
  });
});
