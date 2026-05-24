# 代码与交付材料修改说明

## 代码修改

| 文件 | 修改内容 |
| --- | --- |
| `apps/web/src/hooks/useVotingContract.ts` | 增加 Sepolia 只读 RPC 回退逻辑，使未安装浏览器钱包时仍可读取真实链上投票结果，便于系统演示与论文截图。 |
| `scripts/generateGraduationFigures.py` | 新增毕业设计图表生成脚本，用于生成系统架构图、业务流程图、投票流程图、Merkle 验证图、测试表、Gas 图和部署证据图。 |

## 部署与配置同步

| 文件 | 修改内容 |
| --- | --- |
| `deployments/sepolia.json` | 更新为最新 Sepolia 合约地址、部署交易 Hash、部署 Gas 和 3 天投票窗口。 |
| `apps/web/public/deployment.json` | 同步前端运行所需的 ABI、合约地址和部署配置。 |
| `docs/deployments/sepolia.md` | 更新最新部署记录、真实投票交易和 Etherscan 追溯链接。 |
| `docs/security/slither-results.json` | 更新 Slither 最新审计 JSON 输出。 |
| `docs/process/method-compliance-checklist.md` | 同步最新合约地址与方法要求完成度。 |

## 交付材料

- `deliverables/graduation/screenshots`：系统运行截图与分区截图。
- `deliverables/graduation/figures`：论文可插入图表。
- `deliverables/graduation/reports`：测试、Gas、部署、Slither、代码修改摘要。
- `deliverables/graduation/docx`：最终毕业设计说明书输出目录。

## 注意事项

`.env` 文件未提交。当前测试网私钥曾在对话中暴露，建议在最终归档前更换测试部署钱包，并停止继续使用该私钥管理任何有价值资产。
