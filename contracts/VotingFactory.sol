// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {VotingSystem} from "./VotingSystem.sol";

// 工厂合约负责创建和登记多场投票，前端可以通过它统一发现所有投票活动。
// 每一场具体投票仍由独立的 VotingSystem 合约保存规则和票数。
contract VotingFactory {
    // 只保存投票列表需要展示和检索的元数据，不在工厂合约里重复保存票数。
    struct ElectionRecord {
        address election;
        address creator;
        string title;
        uint256 votingEndTime;
        bytes32 merkleRoot;
        uint256 createdAt;
        bool archived;
    }

    // elections 保存平台内所有投票活动；electionVoters 保存对应投票的白名单地址。
    ElectionRecord[] private elections;
    mapping(uint256 => address[]) private electionVoters;
    // 防止同一个 VotingSystem 地址被重复登记，避免前端列表出现重复记录。
    mapping(address => bool) private registeredElection;

    event ElectionCreated(
        uint256 indexed electionId,
        address indexed election,
        address indexed creator,
        string title,
        uint256 votingEndTime,
        bytes32 merkleRoot
    );
    event ElectionArchived(uint256 indexed electionId, bool archived);

    function createElection(
        string memory title,
        string[] memory candidates,
        uint256 votingEndTime,
        bytes32 merkleRoot,
        address[] memory voters
    ) external returns (address electionAddress) {
        require(voters.length > 0, "Voter whitelist is required");

        // 为本次投票单独部署一个 VotingSystem，保证不同投票之间的候选项和票数互不影响。
        VotingSystem election = new VotingSystem(title, candidates, votingEndTime, merkleRoot);
        electionAddress = address(election);

        // 部署完成后立即登记到工厂列表，供管理端和前端查询。
        _registerElection(electionAddress, title, votingEndTime, merkleRoot, voters);
    }

    function registerElection(address electionAddress, address[] memory voters) external {
        require(electionAddress != address(0), "Invalid election address");

        // 兼容已经单独部署的 VotingSystem：读取链上配置后补登记到工厂合约。
        VotingSystem election = VotingSystem(electionAddress);
        _registerElection(
            electionAddress,
            election.title(),
            election.votingEndTime(),
            election.merkleRoot(),
            voters
        );
    }

    function getElectionCount() external view returns (uint256) {
        return elections.length;
    }

    function getElection(uint256 electionId) external view returns (ElectionRecord memory) {
        require(electionId < elections.length, "Election does not exist");
        return elections[electionId];
    }

    function getElectionVoters(uint256 electionId) external view returns (address[] memory) {
        require(electionId < elections.length, "Election does not exist");
        return electionVoters[electionId];
    }

    function setElectionArchived(uint256 electionId, bool archived) external {
        require(electionId < elections.length, "Election does not exist");
        require(msg.sender == elections[electionId].creator, "Only creator can archive election");

        // 归档只影响平台列表展示，不会修改 VotingSystem 内部的投票结果。
        elections[electionId].archived = archived;
        emit ElectionArchived(electionId, archived);
    }

    function _registerElection(
        address electionAddress,
        string memory title,
        uint256 votingEndTime,
        bytes32 merkleRoot,
        address[] memory voters
    ) private {
        require(!registeredElection[electionAddress], "Election already registered");
        require(voters.length > 0, "Voter whitelist is required");

        // 工厂只记录投票的索引信息，真实投票逻辑仍在 electionAddress 指向的合约中执行。
        elections.push(ElectionRecord({
            election: electionAddress,
            creator: msg.sender,
            title: title,
            votingEndTime: votingEndTime,
            merkleRoot: merkleRoot,
            createdAt: block.timestamp,
            archived: false
        }));
        registeredElection[electionAddress] = true;

        uint256 electionId = elections.length - 1;
        for (uint256 i = 0; i < voters.length; i++) {
            require(voters[i] != address(0), "Invalid voter address");
            // 白名单原始地址保存在工厂中，便于前端生成或匹配 Merkle proof。
            electionVoters[electionId].push(voters[i]);
        }

        emit ElectionCreated(electionId, electionAddress, msg.sender, title, votingEndTime, merkleRoot);
    }
}
