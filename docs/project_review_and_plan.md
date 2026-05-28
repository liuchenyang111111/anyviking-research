# 项目体检与下一阶段计划

本计划面向当前项目的后续开发，不是对外宣传稿。目标是让项目继续保持“小而稳”的结构，同时为 AnySearch、MCP、OpenVikingBot 这类后续能力预留可插拔空间。

## 1. 当前体检结论

当前项目已经具备一个开源项目雏形：

```text
OpenViking 本地语料检索
-> CLI 包装
-> smoke demo
-> 合成语料 demo
-> 新闻语料 demo
-> research markdown/json 输出
-> GitHub Actions 单元测试
```

本地 Git 状态已经验证过：

- `.venv/` 未提交。
- `workspace/` 未提交。
- 真实 `config/ov.conf` 和 `config/ovcli.conf` 未提交。
- `reports/*.md` 和 `reports/*.json` 未提交。
- 当前已提交版本包含两个 commit。

代码结构目前是健康的：

```text
src/anyviking_research/retrievers/
  检索后端适配层

src/anyviking_research/workflows/
  多步骤工作流

src/anyviking_research/cli.py
  命令行入口
```

文档已经精简到比较合适的规模：

```text
README.md
SKILL.md
ROADMAP.md
CHANGELOG.md
docs/
examples/
```

## 2. 当前不建议马上做的事

这些功能有价值，但现在不建议马上做：

- Web UI。
- 自动生成完整最终报告。
- 大型 GitHub 仓库导入。
- 复杂 Agent planner。
- 把 AnySearch、MCP、OpenVikingBot 硬写进主流程。

原因是当前项目最有价值的地方是“可复现、可解释、可扩展”。如果过早接入复杂 Agent，会让学习成本和调试成本突然升高。

## 3. v0.4：引用质量增强

状态：已实现。

### 目标

让 `ar research` 生成的草稿更适合阅读、复查和后续交给 Agent 使用。

当前 research 已经能输出：

- markdown 草稿。
- JSON 结构化结果。
- `viking://` 引用。

本阶段补上的能力是：

- 结果去重。
- 引用统计。
- 证据覆盖检查。

### 3.1 结果去重

问题：

同一章节里可能出现同一个 URI 多次，或者不同章节反复出现同一篇文档。

建议策略：

```text
--dedupe section
```

默认开启章节内去重：同一章节中，同一个 URI 只保留分数最高的一条。

保留可选模式：

```text
--dedupe none
```

方便调试 OpenViking 原始返回结果。

暂时不建议做全局强去重，因为同一篇资料出现在多个章节里有时是合理的。

### 3.2 引用统计

在报告末尾新增：

```markdown
## 引用统计
```

统计每个 URI：

- 标题。
- URI。
- 命中次数。
- 出现在哪些章节。
- 最高分数。

JSON 输出中新增：

```json
"citation_stats": []
```

这能让用户快速看出：

- 哪些资料是核心资料。
- 哪些章节依赖同一批资料。
- 哪些资料只出现一次。

### 3.3 证据覆盖检查

新增一个轻量检查：

```text
每个章节是否至少有 N 条结果
重复引用比例是否过高
是否出现空章节
```

报告末尾新增：

```markdown
## 质量提示
```

例如：

```text
- “数据治理与开源安全”章节只有 2 条结果，建议扩大检索问题或调大 --fetch-k。
- 5 个章节中有 4 个都引用了同一篇资料，建议人工确认是否证据过度集中。
```

### 3.4 v0.4 交付物

- 已更新 `src/anyviking_research/workflows/research.py`。
- 已新增 citation stats 数据结构。
- 已更新 markdown 渲染。
- 已更新 JSON 输出。
- 已新增 CLI 参数：

```powershell
--dedupe section
--dedupe none
--no-citation-stats
```

- 已更新测试。
- 已更新 `docs/research_workflow.md`。

## 4. v0.5：可插拔 AnySearch Connector

### 目标

AnySearch 不进入核心检索链路，而是作为“公网资料发现入口”。

推荐流程：

```text
AnySearch 搜公网
-> 保存结果为 markdown
-> ar import-local
-> OpenViking 建索引
-> ar search/research
```

不建议一开始做：

```text
ar search 同时查 OpenViking 和 AnySearch
```

因为这会让“本地语料检索”和“实时公网搜索”混在一起，难以解释结果来源。

### 4.1 插件目录建议

```text
src/anyviking_research/connectors/
  __init__.py
  base.py
  anysearch.py
```

接口形状：

```python
class SourceConnector(Protocol):
    def fetch(self, query: str, *, limit: int) -> list[SourceDocument]:
        ...
```

AnySearch connector 只负责获取资料，不负责语义检索。

### 4.2 CLI 形状

建议新增：

```powershell
ar fetch-web "AI search tools" --provider anysearch --output data\web\ai-search
```

然后用户再运行：

```powershell
ar import-local data\web\ai-search --to viking://resources/ai-search-web
```

这样链路非常清楚：

```text
fetch-web = 找资料并落地 markdown
import-local = 导入 OpenViking
search/research = 检索 OpenViking
```

### 4.3 可插拔要求

- 默认安装不需要 AnySearch API key。
- 没有配置 key 时，核心命令仍然可用。
- AnySearch 配置放在 `.env` 或用户本地配置中，不能写进仓库。
- AnySearch 输出目录默认进入 `data/`，并由 `.gitignore` 忽略，除非用户明确要提交 demo。

## 5. v0.6：可插拔 MCP / OpenVikingBot Adapter

### 目标

把当前 CLI/research 能力暴露给 Agent，但不让 Agent 能力污染核心代码。

建议目录：

```text
src/anyviking_research/adapters/
  __init__.py
  mcp.py
  openviking_bot.py
```

### 5.1 MCP Adapter

MCP adapter 应该只是调用已有能力：

```text
MCP tool: health
MCP tool: search
MCP tool: research
```

它不应该重新实现检索。

### 5.2 OpenVikingBot Adapter

OpenVikingBot adapter 可以放在后面评估，原则是：

- Bot 是可选体验层。
- 不影响 `ar search`。
- 不影响 `ar research`。
- 不要求普通用户必须安装 Bot 依赖。

### 5.3 可选依赖

未来可以在 `pyproject.toml` 里加：

```toml
[project.optional-dependencies]
mcp = [...]
bot = [...]
anysearch = [...]
```

默认安装仍然保持轻量：

```powershell
python -m pip install -e .
```

需要扩展时再安装：

```powershell
python -m pip install -e ".[mcp]"
python -m pip install -e ".[anysearch]"
```

## 6. 明天测试清单

在推 GitHub 前，建议按这个顺序测：

```powershell
.\scripts\smoke_test.ps1 -Question "第二阶段重点做什么"
.\examples\synthetic_ai_news\run_demo.ps1 -Question "为什么开源项目需要合成 demo 语料"
.\examples\synthetic_ai_news\run_research.ps1
ar research examples\synthetic_ai_news\research_questions.yaml --output reports\synthetic_ai_news_research_draft.md --json-output reports\synthetic_ai_news_research_draft.json --top-k 4
python -m unittest discover -s tests
python -m compileall src tests
```

确认：

- README 显示正常。
- 合成 demo 可完整运行。
- research 报告包含“引用统计”和“质量提示”。
- `reports/` 生成文件不进入 Git。
- `config/ov.conf` 不进入 Git。
- GitHub Actions 文件存在。

## 7. 推荐下一步执行顺序

1. 明天本地测试。
2. 推到 GitHub，先 Private。
3. 确认 GitHub 页面没有泄露配置或报告。
4. 确认 v0.4 引用质量增强在真实 demo 中表现正常。
5. v0.4 稳定后，再设计 v0.5 AnySearch connector。
6. 最后再评估 v0.6 MCP / OpenVikingBot adapter。
