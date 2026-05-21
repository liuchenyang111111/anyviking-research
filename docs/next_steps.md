# 后续任务规划

当前第二阶段核心环境已经跑通：

```text
项目专用 config/ov.conf
-> openviking-server
-> 导入 examples/smoke_corpus
-> ov find 中文检索
-> ov-search-skill 中文检索
-> ov-search-skill research 生成检索草稿
```

## 1. 第一批真实语料

第一批真实语料选择旧项目里的中美关系新闻资料：

```text
D:\Github\OpenViking_Run\workspace\news_raw\us-china-relations\2026-05-16
```

导入目标：

```text
viking://resources/news-us-china-2026-05
```

这个资料集规模适中，适合做第一个真实 demo。

该 demo 已完成一次导入和检索验证，运行记录见 [新闻语料 Demo 运行记录](news_demo_run_record.md)。

## 2. 第二阶段新增成果

阶段二已经补上轻量检索型调研 workflow：

```text
research_questions.yaml
-> OpenViking 多问题检索
-> 过滤自动摘要和无效占位回答
-> reports/news_us_china_research_draft.md
```

当前验证结果：

- 7 个调研章节。
- 每节 Top 5。
- 共 35 条 `viking://` 引用。
- 输出报告保存在 `reports/`，不会提交到仓库。

说明文档见 [检索型调研 Workflow](research_workflow.md)。

## 3. 建议第三阶段目标

第三阶段目标是“开源可分发 demo 语料”和“报告草稿质量提升”：

```text
自写或可公开再分发资料
-> 导入 viking://resources/<demo-name>
-> 用 ov-search-skill search 验证检索
-> 用 ov-search-skill research 生成草稿
-> 写 demo 记录
```

交付物：

- [x] `examples/synthetic_ai_news/README.md`
- [x] `examples/synthetic_ai_news/source/`
- [x] `examples/synthetic_ai_news/queries.md`
- [x] `examples/synthetic_ai_news/research_questions.yaml`
- [x] `docs/synthetic_demo_run_record.md`

当前合成语料主题：

```text
AI 搜索与端侧智能产品趋势
```

导入目标：

```text
viking://resources/synthetic-ai-news
```

## 4. 后面再做的能力

开源可复现 demo 稳定后，再考虑：

- 增加 JSON 文件输出。
- 增加引用去重和分组。
- 让 AI 基于检索结果写短报告。
- 再评估 VikingBot。
- 再评估 AnySearch。

## 5. 当前不建议做

现在不建议马上做：

- Web UI。
- 大型仓库导入。
- 复杂 Agent planner。
- 多数据源混合检索。

先把一个真实资料 demo 打磨清楚，比堆功能更有展示价值。
