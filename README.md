# MTH321

Numerical analysis coursework. The current Project 1 delivery is
[report_v2](Project1/report_v2/README.md): Sections 2–4 and Appendix C.
The earlier [report_v1](Project1/report_v1/README.md) is preserved.
Sections 1 and 5 remain for team integration.

## Project 1: run and verify

Run from the cloned repository:

~~~powershell
cd Project1
python -m pip install -r requirements.txt
python -B code/run_all.py
python -B -m unittest discover -s test -v
~~~

English and Chinese source, file descriptions, figure descriptions and
reproduction settings: [English README](Project1/README_EN.md) /
[中文 README](Project1/README_ZH.md).

Source is in code/ and code_zh/, tests in test/, current numerical evidence
in data/, and working plots in figures/. Submitted reports contain their own
figures and datasets. Early drafts and dated reviews are archived under notes/.

版本与恢复：[report version index](Project1/notes/REPORT_VERSIONS.md).
Git tags report-v1 and report-v2 identify the corresponding whole-project states.
Later formal deliveries can use report_v3 or report_final.
