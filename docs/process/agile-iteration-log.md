# 敏捷迭代与 Git 记录

## 版本控制方式

本项目使用 Git 进行版本控制，主分支为 `main`，远程仓库为：

```text
https://github.com/wangsir2004/decentralized-voting-system-project.git
```

提交信息采用中文语义化提交格式：

```text
<type>(<scope>): <subject>
```

例如：

```text
chore(工程): 初始化毕业设计项目版本库
docs(安全): 补充算法推导与审计材料
```

## 迭代记录

| 迭代 | 目标 | 主要产物 | 验证方式 |
| --- | --- | --- | --- |
| MVP-1 | 完成基础投票合约 | `contracts/VotingSystem.sol`、Hardhat 测试 | `npm test` |
| MVP-2 | 完成白名单机制 | `scripts/generateWhitelist.ts`、`apps/web/public/whitelist.json` | 白名单生成脚本和合约测试 |
| MVP-3 | 完成前端 DApp 演示 | `apps/web/src`、中文投票界面 | `npm run web:build` |
| MVP-4 | 完成 Sepolia 部署 | `deployments/sepolia.json`、`apps/web/public/deployment.json` | `npm run deploy:sepolia` |
| MVP-5 | 补齐论文与审计材料 | `docs/thesis/algorithm-notes.md`、`docs/security/slither-audit.md` | `npm run test:gas`、`slither` |

## 可核验命令

查看提交历史：

```bash
git log --oneline --decorate
```

查看远程仓库：

```bash
git remote -v
```

查看当前工作区状态：

```bash
git status --short
```

推送到 GitHub：

```bash
git push origin main
```

## 工程规范说明

- `.env` 已加入 `.gitignore`，避免 RPC、私钥等敏感配置上传到 GitHub。
- 仓库提供 `.env.example`，用于说明必要环境变量。
- 部署产物集中保存在 `deployments/sepolia.json`。
- 前端公开读取的合约配置集中保存在 `apps/web/public/deployment.json`。
- 论文与验收证据集中保存在 `docs` 目录下。
