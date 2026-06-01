# 合作者交接文档：后续优化方向、缺陷与协作规范

本文档面向接下来继续开发的组员。当前项目已经有一个能支撑中期检查的最小 baseline，但它只是“可运行、可度量、可写报告”的起点，不代表模型效果已经优化。

## 当前 baseline 能做什么

当前 pipeline 由 `run_midterm.py` 串联：

1. 加载本地 QASPER-like JSON/JSONL 或下载缓存官方 QASPER v0.3 JSON。
2. 构建 Midterm Dataset Slice，默认约 20 篇论文、60 个 QA。
3. 写出 Processed QASPER Slice：
   - `processed/papers.jsonl`
   - `processed/qas.jsonl`
4. 生成数据审计：
   - 文档长度统计
   - 段落长度统计
   - evidence 缺失或不完整统计
   - unanswerable 问题比例
5. 运行 TF-IDF RAG Baseline。
6. 运行 Rule-Based Co-Occurrence GraphRAG。
7. 在 `graphrag_predictions.json` 中记录 `graph_trace`，用于解释 seed evidence、expanded terms、candidate evidence 和 graph bonus。
8. 生成抽取式回答或 `INSUFFICIENT_EVIDENCE` 拒答。
9. 计算指标：
   - Evidence Recall@5
   - Answer Token F1
   - Refusal Accuracy
   - Average Latency
10. 导出 Failure Cases，用于中期报告误差分析。

## 当前 baseline 的主要缺陷

### 1. 检索仍是简单 lexical 方法

`src/retrieval.py` 使用纯标准库 TF-IDF。优点是轻、稳定、CPU-only；缺点是不能处理同义表达、长距离语义相关和复杂问题改写。

后续可以考虑：

- 使用 `scikit-learn` 的 `TfidfVectorizer` 替换手写 TF-IDF，提高可靠性。
- 增加 BM25。
- 在不阻塞 baseline 的前提下增加 dense retrieval 对比。

### 2. 规则共现图非常粗糙

`src/graph_rag.py` 当前按 token 规则抽取 term，并基于段落共现连边。它能体现 GraphRAG-shaped pipeline，但不是高质量知识图谱。

缺陷包括：

- 没有实体规范化。
- 没有别名合并。
- 没有短语抽取。
- 没有关系类型。
- 图边权非常简单。

后续可以考虑：

- 增加 noun phrase / keyphrase 抽取。
- 给 co-occurrence edge 增加频次权重。
- 对 term 做 stopword、词形还原、大小写和符号归一。
- 继续完善 graph expansion trace，例如增加更细粒度的 neighbor path 或 edge weight 说明。

### 3. 回答生成只是抽取式句子选择

`src/answering.py` 当前选择最相关证据句作为答案。它可复现且不会引入 LLM 幻觉，但答案质量不高。

后续可以考虑：

- 增加多句 evidence answer。
- 增加答案长度限制。
- 对问题类型做简单分类，例如 yes/no、definition、method、result。
- Optional LLM Enhancement 作为非默认路径，把 evidence 改写成自然语言答案。

注意：LLM 路径必须保持 optional，不能影响默认 baseline 复现。

### 4. 拒答阈值很朴素

当前 Retrieval-Based Refusal 主要依赖最高检索分数过低。这个方法简单可测，但可能过度拒答或漏拒答。

后续可以考虑：

- 用 top-k 分数差距判断不确定性。
- 加入 graph match 作为拒答条件。
- 单独调参并报告 unanswerable 子集表现。

### 5. 指标只是最低限度

当前指标足够中期展示，但不等于全面评测。

后续可以考虑：

- Recall@1 / Recall@3 / Recall@5 对比。
- Precision@K。
- MRR。
- 按 answerable / unanswerable 分组统计。
- 按文档长度或证据缺失情况分组统计。

暂时不要引入 RAGAS、NLI 或人工评测作为必跑路径；这些可以作为终期增强，不应破坏当前一键复现。

## 优先级建议

### P0：先确保中期报告材料完整

负责人应先运行真实 QASPER 小切片，收集：

- `audit.json`
- `baseline_metrics.json`
- `graphrag_metrics.json`
- `failure_cases.json`
- 终端运行成功日志
- `tree -L 2` 仓库结构
- `git log --oneline` 提交统计

这些内容直接对应 `docs/项目中期进展报告模板.md`。

### P1：提高报告可解释性

建议增加：

- 利用 `graphrag_predictions.json` 中的 `graph_trace` 字段解释每个问题的 seed evidence、expanded terms、candidate evidence 和 graph bonus。
- 对比表中写清楚 baseline 与 proposed method 的差异。
- 从 `failure_cases.json` 中挑 2 个真实案例写入报告。

### P2：优化检索效果

建议小步做：

1. 先增加 BM25 或 sklearn TF-IDF。
2. 再调 graph bonus。
3. 再加 keyphrase extraction。
4. 最后考虑 dense retrieval。

每一步都必须保留 baseline 指标，不能只覆盖旧结果。

### P3：扩展 Optional LLM Enhancement

可以加入 DeepSeek 或其他 LLM 改写答案，但必须满足：

- 默认不开启。
- 没有 API key 时 baseline 仍能完整运行。
- 输出中明确标记 LLM answer 与 extractive answer。
- 报告中不要把 LLM 结果混成默认 baseline。

## 协作规范

中期报告模板明确会检查代码提交历史、模块划分、运行说明、分支协作和 commit 记录。后续协作建议按以下规则执行。

### 分支规则

不要直接在 `main` 上开发功能。建议分支命名：

- `feature/<short-topic>`：新功能，例如 `feature/bm25-retrieval`
- `fix/<short-topic>`：bug 修复，例如 `fix/qasper-evidence-mapping`
- `docs/<short-topic>`：文档，例如 `docs/midterm-report-materials`
- `experiment/<short-topic>`：实验性代码，例如 `experiment/dense-retrieval`

每个分支只做一类事情，避免把模型、文档、数据输出混在一个 PR。

### Commit 规则

中期模板会检查 commit 历史。建议：

- 每个组员至少 1 次有效 commit。
- 每个 issue 或功能至少 1 次 commit。
- commit message 用动宾结构，说明做了什么，例如：
  - `Add BM25 retrieval baseline`
  - `Export graph expansion traces`
  - `Document midterm experiment results`
- 不提交生成数据、缓存、`.env`、`results/` 或 `data/processed/`。

### PR 规则

推荐所有功能通过 PR 合并，即使是小项目也能留下协作证据。

PR 描述建议包含：

- 改动目的。
- 涉及文件。
- 运行命令。
- 关键指标或输出路径。
- 是否影响 README 或报告材料。

至少一名组员 review 后再合并。报告中可以写“使用 feature branch + PR review 协作”。

### Issue 规则

本项目 issue tracker 在 `.scratch/` 下：

- PRD：`.scratch/midterm-graphrag-baseline/PRD.md`
- Issues：`.scratch/midterm-graphrag-baseline/issues/`

新增任务时建议：

1. 先写 issue，说明目标、验收标准和依赖。
2. 再开分支实现。
3. 完成后把 issue `Status:` 改成 `completed`。
4. 在 issue 底部写明对应 commit 或 PR。

### 测试与运行规则

默认测试：

```bash
python3 -m pytest
```

无 pytest 环境时：

```bash
python3 tests/run_smoke_tests.py
```

真实数据运行：

```bash
python3 run_midterm.py --max-papers 20 --max-qas 60 --top-k 5 --output-dir results/midterm
```

运行结果不要提交到 Git。报告需要时，只复制关键日志、指标表和失败案例。

## 中期报告填充建议

按照 `docs/项目中期进展报告模板.md`，可以这样对应：

- 项目概述与当前状态：引用 README 和本文档。
- 代码仓库状态审计：用 `git log --oneline | wc -l`、GitHub Insights 和分支/PR 记录。
- 目录结构：运行 `tree -L 2` 后粘贴实际输出。
- 数据工程与审计：引用 `audit.json`。
- 数据流 Mermaid：从 `data_loader.py` 到 `run_midterm.py` 画流程。
- 基线模型：写 TF-IDF RAG Baseline，命令用 README 中的一键命令。
- 核心进阶算法：写 Rule-Based Co-Occurrence GraphRAG。
- 实验结果：对比 `baseline_metrics.json` 和 `graphrag_metrics.json`。
- 失败案例：引用 `failure_cases.json`，不能手编。
- 风险与排期：把本文档的缺陷和优化方向转成第 13-16 周计划。
- AI 工具使用记录：如实填写，不要把 AI 生成内容当成未经审查的最终结论。

## 下一步建议任务

1. 在统一环境中运行真实 QASPER 小切片，保存中期报告需要的指标。
2. 将 `failure_cases.json` 中至少 2 个案例整理成报告表格。
3. 增加 GraphRAG trace 输出，方便解释 graph expansion。
4. 加 BM25 或 sklearn TF-IDF 作为更可信 lexical baseline。
5. 增加 `docs/MIDTERM_REPORT_NOTES.md`，集中整理报告素材。
