# 毕业设计测试结果摘要

## 测试环境

- 项目路径：`D:\codex\decentralized-voting-system-project`
- 测试框架：Hardhat + Mocha/Chai
- Solidity 版本：`0.8.24`
- 验证命令：`npm test`
- 执行结果：`24 passing`

## 用例覆盖情况

| 测试模块 | 用例数 | 覆盖内容 | 结果 |
| --- | ---: | --- | --- |
| 前端显示工具 | 7 | 地址缩写、链 ID 展示、票数统计、领先项计算、ABI 摘要、钱包错误提示 | 通过 |
| 前端资源校验 | 4 | 部署配置、白名单、重复地址、Merkle Root 一致性校验 | 通过 |
| 部署脚本校验 | 4 | 重复地址、候选项列表、Merkle Root、白名单 proof 生成 | 通过 |
| `VotingSystem` 合约 | 9 | 初始化、白名单投票、拒绝非白名单、拒绝重复投票、拒绝非法候选项、截止时间、结果读取 | 通过 |

## 结论

测试结果表明，系统核心投票流程、白名单校验、重复投票限制、部署脚本输入校验和前端展示工具均可正常工作。原始测试输出保存于 `deliverables/graduation/reports/test-output.txt`，可作为论文测试章节的支撑材料。
