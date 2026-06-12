# Neo4j 知识图谱接入指南

面向开题报告中的「实体-关系图谱 + 子图检索」，在本项目现有 QASPER pipeline 上增量接入 Neo4j。

---

## 1. 和当前实现的区别

| 维度 | 当前 `graph_rag.py` | Neo4j 知识图谱 |
|------|---------------------|----------------|
| 存储 | Python 内存 dict | Neo4j 持久化图数据库 |
| 节点 | 词项（term） | Paper / Paragraph / Term（可扩展 Entity） |
| 边 | 共现邻居 | `MENTIONS`、`CO_OCCURS`、可选 `USES`/`ACHIEVES` |
| 检索 | 内存扩展 + TF-IDF rerank | Cypher 子图查询 + TF-IDF rerank |
| 依赖 | 无 | Docker + `neo4j` Python driver |

**建议策略**：保留现有轻量 GraphRAG 作为 CPU baseline；Neo4j 作为**可选增强路径**，用于终期报告展示「开题方案落地」。

---

## 2. 图 Schema（课程项目最小版）

```text
(Paper)          论文节点
(Paragraph)      段落节点，带 paragraph_id / text / section
(Term)           从段落抽取的词项（≥4 字符，过滤 stopwords）

(Paper)<-[:IN_PAPER]-(Paragraph)
(Paragraph)-[:MENTIONS]->(Term)
```

检索时通过 **Term 桥接**：query 词 → 命中段落 → 同段/共享 Term 的其他段落（无需显式 CO_OCCURS 边，入库更快）。

**可选进阶**（开题报告中的 Method-uses-Dataset 等）：

```text
(Term)-[:USES]->(Term)       # 规则：uses/using + 宾语
(Term)-[:ACHIEVES]->(Term)    # 规则：achieves/accuracy + 数值
```

Term 按 `paper_id` 隔离，避免跨论文错误连边。

---

## 3. 环境准备

### 3.1 启动 Neo4j（Docker）

项目根目录已提供 `docker-compose.yml`：

```bash
docker compose up -d
```

浏览器打开 http://localhost:7474 ，默认账号：

- 用户名：`neo4j`
- 密码：`graphrag123`

### 3.2 Python 依赖

```bash
conda activate dataexcavate
pip install -r requirements-neo4j.txt
```

环境变量（可选，有默认值）：

```bash
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=graphrag123
```

---

## 4. 构建图谱（入库）

从已处理的 QASPER slice 构建图：

```bash
# 先跑 pipeline 生成 processed/papers.jsonl
python run_midterm.py --max-papers 20 --max-qas 60 --output-dir results/midterm

# 写入 Neo4j（--clear 会先清空库）
python scripts/build_neo4j_graph.py \
  --papers results/midterm/processed/papers.jsonl \
  --clear
```

入库逻辑见 `src/neo4j_graph.py` 的 `Neo4jGraphStore.ingest_papers()`：

1. 创建 Paper / Paragraph 节点
2. 对每段抽词 → Term 节点 + `MENTIONS` 边
3. 同段词项两两连 `CO_OCCURS`（weight 累加）

---

## 5. 子图检索（GraphRAG 查询）

核心 Cypher 思路：

```cypher
// 1) 从 query 词项出发
MATCH (seed:Term {paper_id: $paper_id})
WHERE seed.name IN $query_terms

// 2) 一跳共现扩展
OPTIONAL MATCH (seed)-[:CO_OCCURS]-(neighbor:Term {paper_id: $paper_id})

// 3) 找回所属段落
WITH collect(DISTINCT seed) + collect(DISTINCT neighbor) AS terms
UNWIND terms AS t
MATCH (p:Paragraph {paper_id: $paper_id})-[:MENTIONS]->(t)
RETURN DISTINCT p.paragraph_id AS paragraph_id, p.text AS text
```

Python 侧：`Neo4jGraphStore.retrieve_paragraph_candidates()` 返回候选段落，再用现有 `TfidfRetriever` rerank（与 `graph_rag.py` 一致）。

---

## 6. 与现有 pipeline 集成

```bash
# 对比 TF-IDF / 内存 GraphRAG / Neo4j GraphRAG（需 Neo4j 已启动且已入库）
python scripts/run_neo4j_baseline.py \
  --papers results/midterm/processed/papers.jsonl \
  --qas results/midterm/processed/qas.jsonl \
  --top-k 5 \
  --output-dir results/neo4j_compare
```

输出 `neo4j_predictions.json` 与 `neo4j_metrics.json`，指标与 `evaluate.py` 一致。

**接入 `run_midterm.py` 的方式**（可选）：增加 `--graph-backend memory|neo4j` 参数，默认 `memory` 保持可复现。

---

## 7. 开题报告怎么写

诚实描述三层演进：

1. **开题**：Neo4j + 实体关系抽取 + LLM 生成
2. **中期 ADR-0001**：CPU-only 共现图，保证可复现
3. **终期**：Neo4j 持久化 + 规则 Term 图，作为 GraphRAG 的「工程化升级」

**不要_claim** 已做 LLM 关系抽取或 RAGAS，除非真的实现了。

---

## 8. 常见问题

| 问题 | 处理 |
|------|------|
| Docker 未启动 | `docker compose up -d`，检查 `bolt://localhost:7687` |
| 密码不对 | 修改 `docker-compose.yml` 与环境变量一致 |
| 入库慢 | 先用 20 papers slice，不要一次全量 888 篇 |
| 效果不如内存版 | 正常；Neo4j 价值在持久化、可视化、可扩展 schema |
| 答辩 Demo | Neo4j Browser 展示子图 + 终端跑 `run_neo4j_baseline.py` |

---

## 9. 可视化检查

Neo4j Browser 中执行：

```cypher
MATCH (p:Paper {paper_id: '1909.00694'})<-[:IN_PAPER]-(para:Paragraph)-[:MENTIONS]->(t:Term)
RETURN p, para, t LIMIT 50
```

可直观看到段落-词项结构，用于答辩展示。
