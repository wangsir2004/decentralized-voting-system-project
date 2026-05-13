// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {MerkleProof} from "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

contract VotingSystem {
    // 投票主题、截止时间和 Merkle 根公开暴露，方便前端直接读取链上配置。
    string public title;
    uint256 public votingEndTime;
    bytes32 public merkleRoot;

    // 候选项与票数按相同索引保存，避免额外映射带来的遍历成本。
    string[] private candidates;
    uint256[] private voteCounts;
    mapping(address => bool) private voted;

    event VoteCreated(string title, uint256 votingEndTime, bytes32 merkleRoot);
    event VoteCast(address indexed voter, uint256 indexed candidateIndex);

    constructor(
        string memory _title,
        string[] memory _candidates,
        uint256 _votingEndTime,
        bytes32 _merkleRoot
    ) {
        // 构造阶段一次性校验投票基础配置，防止部署出不可用的合约实例。
        require(bytes(_title).length > 0, "Title is required");
        require(_candidates.length >= 2, "Invalid candidate count");
        require(_votingEndTime > block.timestamp, "Voting end time must be in the future");
        require(_merkleRoot != bytes32(0), "Merkle root is required");

        title = _title;
        votingEndTime = _votingEndTime;
        merkleRoot = _merkleRoot;

        // 使用数组顺序作为候选项索引，前端提交的 candidateIndex 直接对应这里的票数位置。
        for (uint256 i = 0; i < _candidates.length; i++) {
            require(bytes(_candidates[i]).length > 0, "Candidate name is required");
            candidates.push(_candidates[i]);
            voteCounts.push(0);
        }

        emit VoteCreated(_title, _votingEndTime, _merkleRoot);
    }

    function vote(uint256 candidateIndex, bytes32[] calldata merkleProof) external {
        // 投票前先完成时间、候选项、重复投票和白名单资格校验。
        require(block.timestamp <= votingEndTime, "Voting has ended");
        require(candidateIndex < candidates.length, "Invalid candidate index");
        require(!voted[msg.sender], "Address has already voted");

        // leaf 的生成方式必须和 scripts/generateWhitelist.ts 保持一致，否则证明无法通过。
        bytes32 leaf = keccak256(abi.encodePacked(msg.sender));
        require(MerkleProof.verify(merkleProof, merkleRoot, leaf), "Address is not eligible");

        // 先标记已投票再累加票数，保持状态更新顺序清晰。
        voted[msg.sender] = true;
        voteCounts[candidateIndex] += 1;

        emit VoteCast(msg.sender, candidateIndex);
    }

    function getCandidates() external view returns (string[] memory) {
        return candidates;
    }

    function getResults() external view returns (string[] memory names, uint256[] memory counts) {
        // 一次性返回候选项和票数，前端图表无需发起两次链上读取。
        return (candidates, voteCounts);
    }

    function isVotingOpen() external view returns (bool) {
        return block.timestamp <= votingEndTime;
    }

    function hasAddressVoted(address voter) external view returns (bool) {
        return voted[voter];
    }

    function candidateCount() external view returns (uint256) {
        return candidates.length;
    }
}
