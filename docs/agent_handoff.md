# DataExcavate Agent Handoff

生成日期：2026-05-30

## 当前任务背景

用户正在推进 `DataExcavate_Proj`，一个面向数据挖掘课程中期检查的 Minimum Runnable GraphRAG Baseline。当前重点已经从“实现最小 baseline”转向“验证运行、整理交接文档、规范协作与提交历史”。

不要重新从零理解项目；先按下面的阅读顺序进入状态。

## 必读顺序

1. `README.md`
   - 项目运行入口、环境配置、输出文件和当前范围。
2. `docs/PROJECT_HANDOFF.md`
   - 面向新成员的中文项目状态说明。
   - 包含 PRD、ADR、issue tracker、报告模板各自的作用。
3. `CONTEXT.md`
   - 项目术语表。后续写文档和 issue 时沿用这里的语言。
4. `.scratch/midterm-graphrag-baseline/PRD.md`
   - 最小 baseline 的范围来源。
5. `docs/adr/0001-midterm-baseline-uses-lightweight-graph-retrieval.md`
   - 架构决策：中期 baseline 使用 TF-IDF seed retrieval + 一跳规则共现图扩展，不引入 Neo4j、dense embeddings 或 mandatory LLM。
6. `.scratch/midterm-graphrag-baseline/issues/`
   - 7 个 issue 均已标记 `completed`，底部 comments 记录对应 commit 和完成内容。
7. `docs/COLLABORATOR_HANDOFF.md`
   - 面向合作者的缺陷、优化方向、分支/commit/PR/issue 协作规范。
8. `docs/项目中期进展报告模板.md`
   - 课程中期报告要求。报告需要 commit 统计、分支协作说明、目录结构、运行日志、指标表、失败案例和 AI 使用记录。

## 当前实现状态

最小 baseline 已实现，核心文件：

- `run_midterm.py`：一键 pipeline。
- `src/data_loader.py`：本地 JSON/JSONL 或 HuggingFace QASPER 加载。
- `src/preprocess.py`：Processed QASPER Slice 标准化。
- `src/audit.py`：数据审计。
- `src/retrieval.py`：纯标准库 TF-IDF RAG baseline。
- `src/graph_rag.py`：Rule-Based Co-Occurrence GraphRAG。
- `src/answering.py`：抽取式回答与 `INSUFFICIENT_EVIDENCE` 拒答。
- `src/evaluate.py`：Evidence Recall@5、Answer Token F1、Refusal Accuracy、latency 和 Failure Cases。
- `tests/`：pytest-style 测试和无依赖 smoke suite。

## 服务器验证状态

用户要求项目代码运行在远程服务器：

- Host alias：`nlpir2`
- 服务器：`121.37.159.108`
- 目标目录：`/opt/wuyufei`
- 当前已通过 `scp` 上传代码到：`/opt/wuyufei/DataExcavate_Proj`

已在服务器验证：

```bash
cd /opt/wuyufei/DataExcavate_Proj
python3 -m compileall src tests run_midterm.py
python3 tests/run_smoke_tests.py
```

结果：通过，输出 `smoke tests passed`。

用户随后允许安装全部依赖。服务器已安装：

```bash
apt-get update
apt-get install -y python3.10-venv
cd /opt/wuyufei/DataExcavate_Proj
python3 -m venv .venv
. .venv/bin/activate
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
python -m pytest
```

结果：完整 pytest 通过，`7 passed in 0.02s`。

也已在服务器用临时 QASPER-like fixture 运行 CLI：

```bash
python3 run_midterm.py --source /opt/wuyufei/tmp/qasper_fixture.jsonl --max-papers 1 --max-qas 1 --top-k 2 --output-dir /opt/wuyufei/tmp/dataexcavate_cli_smoke
```

结果：成功输出：

- `papers=1 qas=1`
- `baseline_recall@5=1.000`
- `graphrag_recall@5=1.000`
- `failure_cases=0`

注意：直接访问默认 PyPI 曾超时，最后使用清华 PyPI 镜像安装依赖成功。

## Git 状态与注意事项

截至本 handoff，远程 `main` 已包含：

- 最小 baseline 实现。
- 中文 README。
- `docs/PROJECT_HANDOFF.md`。
- `docs/COLLABORATOR_HANDOFF.md`。
- issue tracker 状态更新。

用户希望重写之前的 commit message，使 GitHub 上提交历史更详细。注意：这需要 rewrite 已 push 的历史，并使用 `git push --force-with-lease`。执行前应确保用户知道这会改变远程 commit hash，并可能影响其他协作者已拉取的本地分支。

## 建议技能

- `handoff`：继续交接当前上下文时使用。
- `documentation-writer`：继续写报告、README、协作说明时使用。
- `triage`：新增或更新 `.scratch/` issue 时使用。
- `diagnose`：服务器测试或 QASPER 加载失败时使用。
- `tdd`：继续开发 BM25、GraphRAG trace、LLM optional path 等功能时使用。

## 下一步建议

1. 若要完整跑 pytest，在服务器创建 venv 并安装依赖：
   ```bash
   cd /opt/wuyufei/DataExcavate_Proj
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python3 -m pytest
   ```
2. 若要跑真实 QASPER，小心 HuggingFace 下载和网络问题。
3. 若要改提交历史，先设计新的 commit message 列表，再执行非交互 rebase 或 filter-repo 等历史重写方式，最后 `git push --force-with-lease origin main`。
4. 不要提交 `results/`、`data/processed/`、`.venv/`、`.env` 或缓存。
