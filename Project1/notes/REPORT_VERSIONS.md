# Report versions / 报告版本与恢复

| 版本 | 路径 | 状态 | Git 标签 |
|---|---|---|---|
| v1 | [report_v1](../report_v1/README.md) | 原样保留；基线 371cb73 | `report-v1` |
| v2 | [report_v2](../report_v2/README.md) | 本次第 2–4 节与附录 C | `report-v2` |
| v3 / final | 尚未建立 | 后续正式交付再创建 | 届时建立 |

文件夹保存可直接阅读的报告快照；Git 标签保存配套的整个项目，包括代码和测试。
Version folders hold readable snapshots; Git tags recover the matching whole project.

## 日常更新 / Routine changes

克隆一次，开始工作前 git pull，修改后核对 git diff，写明变更再 commit/push。
一次小修改不必新建文件夹；正式交付时再建 report_v3 / report_final，
更新索引并建立对应标签。大改前先提交一个命名清楚的检查点。

## 找到或恢复 / Recovery

```powershell
git log --oneline --decorate
git tag --list
git show report-v1:Project1/report_v1/Section2Draft_v5.tex
```

show 只查看旧文件。要完整旧项目，在另一目录克隆仓库后执行
`git switch --detach report-v1` 或 `report-v2`，得到配套代码、报告和数据，
不会覆盖工作文件。切换本地版本前先保存或提交未提交改动。

A separate clone checked out at a tag recovers a consistent complete version.
Save uncommitted changes before switching locally.

公共分支的错误提交用 `git revert <commit>` 生成撤销提交，核对后推送；
不要强制推送改写其他同学已使用的历史。
当前工作输出在项目级 data/ 和 figures/；正式输出随各 report_vN 保存。
v1 的完整数据/代码也可从 report-v1 标签恢复。
