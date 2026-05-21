# 项目阶段汇报：OpenViking Search Skill

## 1. 项目背景

前一阶段已经完成了一个新闻调研 + OpenViking 的实验项目：

```text
RSS 新闻资料
-> markdown
-> OpenViking 导入
-> 语义检索
-> 调研报告
```

这个旧项目证明了 OpenViking 可以作为本地语料检索后端，支撑新闻调研类任务。

本阶段根据“整理一下、开源、构建为通用检索，并参考 anysearch-skill”的方向，对旧项目进行了重新定位和开源化整理。

## 2. 当前项目定位

当前项目不再定位为单一新闻调研脚本，而是：

```text
OpenViking 本地语料通用检索 Skill
+ 开源可复现合成语料 demo
+ 新闻调研 demo
```

其中：

- OpenViking 负责本地资料导入、索引、`viking://` 资源管理和语义检索。
- 本项目负责配置、CLI 包装、结构化输出、Skill 文档和 demo。
- 合成 AI 新闻语料作为推荐开源 demo，用来证明 clone 后可复现。
- 新闻调研作为本地 example 保留，用来证明真实语料检索链路。
- AnySearch 当前作为 Skill 形态参考，暂不作为 v0.1 强依赖。

## 3. 已完成内容

### 环境与配置

- 使用 Python 3.12。
- 安装并验证 OpenViking 0.3.17。
- 建立项目专用 `config/ov.conf`。
- 使用当前项目 `workspace/`，避免和旧项目数据混在一起。

### CLI 工具

已实现：

```powershell
ov-search-skill health
ov-search-skill status
ov-search-skill status --json
ov-search-skill import-local <path> --to <viking-uri>
ov-search-skill tree <viking-uri> -L 2
ov-search-skill search "<query>" --scope <viking-uri>
```

支持：

- JSON 输出。
- 文本输出。
- `--documents-only` 过滤 OpenViking 自动摘要文件。

### Demo

已完成三个 demo：

```text
examples/smoke_corpus
examples/synthetic_ai_news
examples/news_us_china
```

合成 AI 新闻 demo 包含 8 篇自写 markdown 资料，主题为：

```text
AI 搜索与端侧智能产品趋势
```

该 demo 可以直接提交到开源仓库，用来复现：

```text
import-local
-> search
-> research
```

新闻 demo 已导入旧项目 26 篇 markdown 新闻，并验证：

```text
viking://resources/news-us-china-2026-05
```

可以针对特朗普访华、中美议题、台湾军购等问题返回相关资源。

### 检索型调研 Workflow

已实现阶段二轻量 workflow：

```powershell
ov-search-skill research examples\news_us_china\research_questions.yaml --output reports\news_us_china_research_draft.md --top-k 5
```

能力包括：

- 读取 YAML 调研问题。
- 每个章节独立检索 OpenViking。
- 默认过滤 `.abstract.md` / `.overview.md` 自动摘要。
- 默认过滤“没有找到相关结果”“无法回答”等无效占位回答。
- 输出带 `viking://` 引用的 markdown 草稿。

本地已验证新闻 demo 可生成 7 个章节、35 条引用的检索草稿。

### 开源整理

已补充：

- `README.md`
- `SKILL.md`
- `LICENSE`
- `docs/architecture.md`
- `docs/install_from_scratch.md`
- `docs/faq.md`
- `docs/open_source_checklist.md`
- `docs/news_demo_run_record.md`
- 单元测试

## 4. 对 AnySearch 的理解

AnySearch Skill 的价值主要在于“搜索能力如何包装成 AI Agent 可用的 Skill”。

本项目参考的是它的形态，而不是直接依赖它的 API。

当前关系：

```text
AnySearch
  -> 公网搜索 Skill 参考

OpenViking
  -> 本地语料检索后端

本项目
  -> OpenViking 的通用检索 Skill 包装
```

未来可以把 AnySearch 作为公网资料 connector：

```text
AnySearch 搜公网
-> 保存为 markdown
-> 导入 OpenViking
-> 统一用 ov-search-skill 检索
```

## 5. OpenVikingBot 的位置

当前阶段不把 OpenVikingBot 作为核心依赖。

原因：

- 环境复杂度更高。
- 对复现不友好。
- 当前目标是通用检索，不是完整对话 Agent。

后续可以作为增强方向：

```text
v0.1 通用检索 Skill
v0.2 新闻调研 workflow
v0.3 可选 OpenVikingBot / MCP 集成
```

## 6. 当前结论

项目已经从一个特定新闻调研实验，整理成了一个更通用的 OpenViking 检索 Skill 雏形。

当前可以展示的核心能力：

```text
本地资料导入
-> OpenViking 语义检索
-> 结构化 JSON 输出
-> viking:// 引用
-> 可复现合成语料 demo
-> 新闻调研 demo
```

下一步建议继续做：

- 更完整的 research workflow 测试。
- 可选 JSON 文件输出和引用去重。
- 可选 MCP / OpenVikingBot 集成。
