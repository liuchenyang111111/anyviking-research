# 检索型调研 Workflow

阶段二新增的 `research` 命令，用来把“多个调研问题 -> 多次 OpenViking 检索 -> markdown 草稿”整理成一个可复现流程。

它现在不是完整自动写报告工具，而是一个更稳的中间层：

```text
YAML 调研问题
-> 逐个调用 OpenViking 检索
-> 过滤自动摘要和无效占位回答
-> 输出带 viking:// 引用的 markdown 草稿
```

## 为什么先做这个

直接让 AI 写最终报告容易混入未经确认的结论。当前 workflow 先只做资料召回和引用整理，方便后面人工阅读、筛选，再决定是否接 LLM 或 OpenVikingBot。

这个设计适合学习项目，因为每一步都能看见：

- 问题是怎么组织的。
- 检索范围是哪个 `viking://` URI。
- 每个问题返回了哪些资料。
- 哪些资料可以继续作为报告引用。

## 配置文件格式

示例见：

```text
examples\news_us_china\research_questions.yaml
```

核心字段：

```yaml
topic_title: "调研标题"
ov_root_uri: "viking://resources/news-us-china-2026-05"

sections:
  - id: background
    heading: "背景与铺垫"
    question: |
      请检索这个主题的背景和关键事实。
```

说明：

- `topic_title` 会成为输出 markdown 的标题。
- `ov_root_uri` 是 OpenViking 检索范围。
- `sections` 是调研章节列表。
- 每个 `question` 会独立执行一次检索。

## 运行命令

推荐用示例脚本：

```powershell
.\examples\news_us_china\run_research.ps1
```

也可以直接调用 CLI：

```powershell
ov-search-skill research examples\news_us_china\research_questions.yaml --output reports\news_us_china_research_draft.md --top-k 5
```

输出文件：

```text
reports\news_us_china_research_draft.md
```

`reports/` 默认不会提交到 Git，因为它是本地生成结果。

## 重要参数

```powershell
--top-k 5
```

每个问题最终保留多少条结果。

```powershell
--fetch-k 40
```

每个问题先从 OpenViking 拉多少条候选结果。默认会在需要过滤时自动多取候选；如果语料噪声多，可以手动调大。

```powershell
--include-summaries
```

保留 OpenViking 自动生成的 `.abstract.md` 和 `.overview.md`。默认不保留。

```powershell
--keep-unhelpful
```

保留明显无效的占位回答，例如“没有找到相关结果”或“无法回答”。默认不保留。

```powershell
--json
```

在终端额外输出结构化 JSON，方便后续脚本或 Agent 读取。

## 当前验证结果

使用旧项目新闻语料：

```text
viking://resources/news-us-china-2026-05
```

已验证：

- 7 个调研章节。
- 每节 Top 5。
- 共 35 条 `viking://` 引用。
- 已过滤明显无效的占位回答。

使用开源可复现合成语料：

```text
viking://resources/synthetic-ai-news
```

已验证：

- 5 个调研章节。
- 每节 Top 4。
- 共 20 条 `viking://` 引用。
- 已过滤明显无效的占位回答。

## 后续方向

下一步可以在这个 workflow 上继续加：

- JSON 文件输出。
- 引用去重和分组。
- LLM 摘要生成。
- OpenVikingBot 或 MCP 集成。
- AnySearch 抓取公网资料后导入 OpenViking。
