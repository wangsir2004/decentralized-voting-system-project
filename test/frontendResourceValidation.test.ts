import { expect } from "chai";
import {
  assertMatchingMerkleRoot,
  validateDeploymentConfig,
  validateWhitelistFile
} from "../shared/validation";

const validDeployment = {
  network: "sepolia",
  chainId: 11155111,
  contractName: "VotingSystem",
  address: "0xf1793b5DE04811Aca913C450F3C4aF380E1e5297",
  deployer: "0x372ee50901D62F3b314936C9302b19F8F477716E",
  title: "Graduation Design Voting",
  candidates: ["方案 A", "方案 B"],
  votingEndTime: 1778664130,
  merkleRoot: "0x9a3e8214c917f9a4c48601b3135d1cdff0d69955d60e2da76a906ca579349b91",
  deploymentTransactionHash: "0x8aa3a6c20bf3a4bece025bf370f3ec8fe6b6859da5b20950ef7255852fb33f31",
  deploymentGasUsed: "959938",
  deployedAt: "2026-05-06T09:22:26.295Z",
  abi: []
};

const validWhitelist = {
  merkleRoot: "0x9a3e8214c917f9a4c48601b3135d1cdff0d69955d60e2da76a906ca579349b91",
  voters: [
    {
      address: "0x372ee50901D62F3b314936C9302b19F8F477716E",
      leaf: "0x088a6152115444eeb6b502d2f35d430b8c08e1fe7ce5c2cfbbf75da53bd49644",
      proof: []
    }
  ]
};

describe("frontend resource validation", function () {
  it("accepts a complete deployment config and whitelist", function () {
    const deployment = validateDeploymentConfig(validDeployment);
    const whitelist = validateWhitelistFile(validWhitelist);

    expect(deployment.chainId).to.equal(11155111);
    expect(whitelist.voters[0].address).to.equal("0x372ee50901D62F3b314936C9302b19F8F477716E");
  });

  it("rejects deployment configs missing required contract fields", function () {
    expect(() => validateDeploymentConfig({ ...validDeployment, address: "" }))
      .to.throw("合约地址无效");
  });

  it("rejects duplicate whitelist addresses", function () {
    expect(() => validateWhitelistFile({
      ...validWhitelist,
      voters: [validWhitelist.voters[0], { ...validWhitelist.voters[0] }]
    })).to.throw("白名单地址重复");
  });

  it("rejects deployment and whitelist merkle root mismatch", function () {
    const deployment = validateDeploymentConfig(validDeployment);
    const whitelist = validateWhitelistFile({
      ...validWhitelist,
      merkleRoot: "0xd4453790033a2bd762f526409b7f358023773723d9e9bc42487e4996869162b6"
    });

    expect(() => assertMatchingMerkleRoot(deployment, whitelist))
      .to.throw("部署配置与白名单默克尔根不一致");
  });
});
