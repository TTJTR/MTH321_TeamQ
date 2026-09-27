# MTH321 Project 1 / MTH321 项目一

**English:** [README_EN.md](README_EN.md) explains setup, every source file,
all eight generated figures, their CSV data, and the experiment settings.

**中文：** [README_ZH.md](README_ZH.md) 说明安装运行、每个代码文件、
八张图片、对应 CSV，以及实验参数。

The aligned report is [Section2Draft_v5.tex](report_v1/Section2Draft_v5.tex),
and the revision record is [CHANGELOG_V5.md](CHANGELOG_V5.md).
对应的 v5 理论正文及逐项修改记录见上述两个文件。
The `report/` directory contains earlier drafts; `report_v1/` is the current submission.
`report/` 保存早期草稿；当前提交版在 `report_v1/`。

The code-only acceptance record and runnable checks are in
[report_v1/checklist/](report_v1/checklist/README.md).
仅针对代码的验收清单和可运行验证见上述目录。

The eight report images are committed under [report_v1/figures/](report_v1/figures/).
八张报告图片随 `report_v1/figures/` 一起提交；运行代码也可重新生成。

The two runnable code versions implement the same algorithms:
`code/` has English documentation, and `code_zh/` has Chinese documentation.
两套代码的算法相同：`code/` 是英文注释版，`code_zh/` 是中文注释版。

From this directory / 在本目录运行：

```powershell
python -m pip install -r requirements.txt
python code/run_all.py       # English source / 英文源码
python code_zh/run_all.py    # Chinese source / 中文源码
python -B -m unittest discover -s report_v1/checklist -v
```

Each run writes its own `figures/` directory. / 两套代码分别写入各自的 `figures/` 目录。
