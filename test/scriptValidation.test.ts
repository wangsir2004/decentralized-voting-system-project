import { expect } from "chai";
import { validateCandidates, validateMerkleRoot } from "../scripts/deploy";
import { buildWhitelist, normalizeVoterAddresses } from "../scripts/generateWhitelist";

describe("deployment script validation", function () {
  it("rejects duplicate voter addresses after checksum normalization", function () {
    expect(() => normalizeVoterAddresses([
      "0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266",
      "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    ])).to.throw("选民地址重复");
  });

  it("rejects invalid candidate lists before deployment", function () {
    expect(() => validateCandidates(["Only One"])).to.throw("候选项数量无效");
    expect(() => validateCandidates(["Alice", " "])).to.throw("候选项名称不能为空");
  });

  it("rejects an empty merkle root before deployment", function () {
    expect(() => validateMerkleRoot("0x0000000000000000000000000000000000000000000000000000000000000000"))
      .to.throw("默克尔根不能为空");
  });

  it("builds a whitelist with a non-empty merkle root and voter proofs", function () {
    const whitelist = buildWhitelist([
      "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
      "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    ]);

    expect(whitelist.merkleRoot).to.match(/^0x[0-9a-fA-F]{64}$/);
    expect(whitelist.voters).to.have.length(2);
    expect(whitelist.voters[0].proof).to.have.length(1);
  });
});
