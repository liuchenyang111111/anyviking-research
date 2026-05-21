# Roadmap

## 已完成

### v0.1 通用检索 Skill

- Python 3.12 + OpenViking 0.3.17 环境验证。
- 项目专用 OpenViking 配置模板。
- `ov-search-skill health/status/import-local/tree/search`。
- smoke corpus 最小测试语料。
- JSON 和文本两种输出。
- `--documents-only` 过滤 OpenViking 自动摘要。

### v0.2 检索型调研 Workflow

- `ov-search-skill research`。
- YAML 多问题配置。
- markdown 检索草稿输出。
- 自动过滤明显无效占位回答。
- 新闻语料 demo 的 research 验证。

### v0.3 开源可复现 Demo

- `examples/synthetic_ai_news` 合成语料。
- 可复现的 `run_demo.ps1` 和 `run_research.ps1`。
- 公开演示不依赖旧项目路径，不复制新闻全文。

## 建议下一步

### v0.4 输出质量增强

- 增加 `--json-output`，把 research 结构化结果写入 JSON 文件。
- 增加结果去重，避免多个章节重复引用同一文档过多。
- 增加引用统计，输出每份文档被哪些问题命中。

### v0.5 外部资料接入

- 评估 AnySearch 作为公网资料发现入口。
- 将公网资料保存为 markdown 后导入 OpenViking。

### v0.6 Agent 集成

- 评估 MCP 或 OpenVikingBot。
- 优先保持当前 CLI 和 workflow 稳定，再接入更复杂的 Agent 能力。

## 暂不做

- Web UI。
- 大型仓库导入。
- 复杂 Agent planner。
- 自动生成完整最终报告。
