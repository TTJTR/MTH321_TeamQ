# Report versions / 报告版本与恢复

| 版本 | 路径 | 状态 | Git 标签 |
|---|---|---|---|
| v1 | [report_v1](../report_v1/README.md) | 原样保留；基线 371cb73 | `report-v1` |
| v2 | [report_v2](../report_v2/README.md) | 保留的第 2–4 节与附录 C 章节交付版本 | `report-v2` |
| v3 / current | [report_v3](../report_v3/README.md) | 当前整合后的完整报告；包含 Abstract、Sections 1--5、References 和 Appendices A--C | 待建立 |

文件夹保存可直接阅读的报告快照；Git 标签保存配套的整个项目，包括代码和测试。  
Version folders hold readable report snapshots; Git tags recover the matching whole project.

## 日常更新 / Routine changes

克隆一次，开始工作前 `git pull`，修改后核对 `git diff`，
写明变更再 commit/push。

一般的小修改不需要新建版本文件夹。`report_v1/` 和 `report_v2/`
作为历史快照保留，当前整合报告位于 `report_v3/`。

当 v3 的报告、README、checklist、CHANGELOG、附录和 manifest
全部最终确定后，可为对应的完整项目状态建立 `report-v3` Git 标签。

大改前建议先提交一个命名清楚的检查点。

## 找到或恢复 / Recovery

```powershell
git log --oneline --decorate
git tag --list
git show report-v1:Project1/report_v1/Section2Draft_v5.tex
```

`git show` 只查看旧文件。

要恢复完整旧项目，可以在另一目录克隆仓库后执行：

```powershell
git switch --detach report-v1
```

或：

```powershell
git switch --detach report-v2
```

这样可以得到与对应标签匹配的代码、报告和数据，
不会覆盖当前工作文件。

切换本地版本前，应先保存或提交未提交的修改。

A separate clone checked out at a tag recovers a consistent complete version.
Save uncommitted changes before switching locally.

公共分支中的错误提交应使用：

```powershell
git revert <commit>
```

生成撤销提交，核对后再推送。

不要强制推送改写其他同学已经使用的历史。

当前工作输出位于项目级 `data/` 和 `figures/`；
正式输出随各 `report_vN/` 版本保存。

`report_v1/` 与 `report_v2/` 保留为历史报告快照，
`report_v3/` 为当前完整报告版本。

v3 的 `report-v3` Git 标签应在最终版本冻结后再建立。