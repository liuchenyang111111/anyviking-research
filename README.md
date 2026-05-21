# OpenViking Search Skill

OpenViking Search Skill 是一个基于 [OpenViking](https://github.com/volcengine/OpenViking) 的本地语料检索 Skill 学习项目。

它的目标不是重新实现一个检索引擎，而是把 OpenViking 的本地语料导入、语义检索和 `viking://` 引用能力整理成一个更容易复现、调用和展示的开源项目。

一句话定位：

```text
OpenViking 本地语料通用检索 Skill，附带开源可复现合成 demo 和新闻调研 demo。
```

## 为什么做这个项目

OpenViking 本身已经能做资源导入、语义索引和检索。本项目做的是包装层：

- 统一配置和启动方式。
- 用 CLI 封装健康检查、导入、资源树和搜索。
- 返回结构化 JSON，方便 AI Agent 或脚本继续处理。
- 支持过滤 OpenViking 自动生成的摘要，只返回原始文档。
- 提供可复现的 smoke demo、合成语料 demo 和新闻调研 demo。
- 提供 `SKILL.md`，说明 AI Agent 什么时候、怎么使用这个检索能力。

可以类比为：

```text
OpenViking = 检索后端 / 上下文数据库
本项目 = 面向用户和 AI Agent 的检索工具包装层
```

## 核心流程

```text
本地资料
  -> 整理成 markdown
  -> 导入 OpenViking
  -> OpenViking 建立语义检索索引
  -> ov-search-skill 提出问题
  -> 返回带 viking:// URI 的检索结果
```

## 当前特性

- Python 3.12 + OpenViking 0.3.17 环境验证。
- 项目专用 OpenViking 配置模板。
- `ov-search-skill health`：检查服务健康状态。
- `ov-search-skill status`：查看 OpenViking 状态。
- `ov-search-skill import-local`：导入本地文件或文件夹。
- `ov-search-skill tree`：查看 `viking://` 资源树。
- `ov-search-skill search`：语义检索并输出 JSON 或文本。
- `--documents-only`：过滤 `.abstract.md` / `.overview.md`，优先返回原始文档。
- `ov-search-skill research`：读取 YAML 问题列表，生成检索型调研草稿。
- smoke corpus 最小测试语料。
- 合成 AI 新闻语料 demo，可直接开源复现。
- 旧项目中美关系新闻语料 demo。
- 不依赖 OpenViking 服务的最小单元测试。

## 快速开始

### 1. 创建并激活虚拟环境

```powershell
cd D:\Github\OpenViking_Search_Skill
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. 安装依赖

```powershell
python -m pip install --upgrade pip setuptools wheel
python -m pip install openviking
python -m pip install -e . --no-deps --no-build-isolation
```

确认版本：

```powershell
python --version
python -m pip show openviking
openviking-server --version
ov-search-skill --help
```

目标版本：

```text
Python 3.12.x
openviking 0.3.17
```

### 3. 准备配置

复制无密钥模板：

```powershell
Copy-Item config\ov.conf.example config\ov.conf
Copy-Item config\ovcli.conf.example config\ovcli.conf
```

然后编辑：

```text
config\ov.conf
```

把里面的 `YOUR_VOLCENGINE_API_KEY` 替换成你自己的模型服务 key。

真实配置文件已被 `.gitignore` 忽略，不应该提交到仓库。

### 4. 启动 OpenViking

```powershell
.\scripts\start_openviking.ps1
```

检查服务：

```powershell
ov-search-skill health
ov-search-skill status
```

### 5. 跑最小 demo

```powershell
ov-search-skill import-local examples\smoke_corpus --to viking://resources/smoke-corpus
ov-search-skill tree viking://resources/smoke-corpus -L 2
ov-search-skill search "第二阶段重点做什么" --scope viking://resources/smoke-corpus --top-k 3
```

或者一键烟测：

```powershell
.\scripts\smoke_test.ps1 -Question "第二阶段重点做什么"
```

### 6. 跑开源可复现 demo

```powershell
.\examples\synthetic_ai_news\run_demo.ps1 -Question "为什么开源项目需要合成 demo 语料"
```

生成检索型调研草稿：

```powershell
.\examples\synthetic_ai_news\run_research.ps1
```

## CLI 用法

```powershell
ov-search-skill health
ov-search-skill status
ov-search-skill status --json
ov-search-skill import-local <path> --to <viking-uri>
ov-search-skill tree <viking-uri> -L 2
ov-search-skill search "<query>" --scope <viking-uri> --top-k 5
ov-search-skill search "<query>" --scope <viking-uri> --format text
ov-search-skill search "<query>" --scope <viking-uri> --documents-only
ov-search-skill research <questions.yaml> --output reports\research_draft.md
ov-search-skill research <questions.yaml> --output reports\research_draft.md --json-output reports\research_draft.json
ov-search-skill research <questions.yaml> --output reports\research_draft.md --dedupe section --min-results-per-section 2
```

JSON 输出适合脚本和 AI Agent；文本输出适合人工查看。

`research` 会对 YAML 里的每个问题分别检索 OpenViking，然后输出带 `viking://` 引用的 markdown 草稿。它默认会过滤 OpenViking 自动摘要和明显无效的占位回答，并在报告末尾生成引用统计和质量提示。

## 合成 AI 新闻 Demo

这是推荐优先展示的开源 demo，因为语料是项目自写的，可以直接提交到仓库，不依赖本机旧项目路径，也没有新闻版权风险。

语料位置：

```text
examples\synthetic_ai_news\source
```

导入目标：

```text
viking://resources/synthetic-ai-news
```

运行：

```powershell
.\examples\synthetic_ai_news\run_demo.ps1
.\examples\synthetic_ai_news\run_research.ps1
```

## 新闻调研 Demo

旧项目新闻语料已经验证可以导入当前项目的 OpenViking workspace。

语料来源：

```text
D:\Github\OpenViking_Run\workspace\news_raw\us-china-relations\2026-05-16
```

导入目标：

```text
viking://resources/news-us-china-2026-05
```

运行：

```powershell
.\examples\news_us_china\run_demo.ps1 -Question "特朗普访华实际达成了哪些成果"
```

生成检索型调研草稿：

```powershell
.\examples\news_us_china\run_research.ps1
```

默认输出：

```text
reports\news_us_china_research_draft.md
```

说明：

- 当前仓库不复制新闻全文，避免版权和仓库体积问题。
- 新闻 demo 用来证明“真实语料 -> OpenViking -> 结构化检索”的链路。
- `reports/` 默认被 `.gitignore` 忽略，生成的报告草稿只留在本地。

## 测试

不依赖 OpenViking 服务的单元测试：

```powershell
python -m unittest discover -s tests
```

语法检查：

```powershell
python -m compileall src tests
```

GitHub Actions 会在推送或 Pull Request 时自动运行这些不依赖 OpenViking 服务的测试。

## 与 AnySearch 的关系

AnySearch Skill 是本项目的形态参考，不是当前版本的强依赖。

当前定位：

```text
AnySearch
  -> 公网搜索 / Agent search skill 形态参考

OpenViking
  -> 本地语料导入 / 语义检索 / viking:// 资源管理

本项目
  -> 把 OpenViking 包装成可复现、可调用的本地语料检索 Skill
```

未来可以考虑：

```text
AnySearch 搜公网
  -> 保存为 markdown
  -> 导入 OpenViking
  -> 用本项目统一检索
```

## OpenVikingBot 是否必需

不必需。

当前核心是通用检索 Skill。OpenVikingBot 可以作为后续增强方向，用来做对话式检索和报告生成，但不应该成为基础功能的强依赖。

## 文档地图

- [项目架构说明](docs/architecture.md)
- [从零安装与复现指南](docs/install_from_scratch.md)
- [FAQ](docs/faq.md)
- [项目基础概念说明](docs/project_basics.md)
- [检索型调研 Workflow](docs/research_workflow.md)
- [项目体检与下一阶段计划](docs/project_review_and_plan.md)
- [合成 AI 新闻语料 Demo](examples/synthetic_ai_news/README.md)
- [中美关系新闻语料 Demo](examples/news_us_china/README.md)
- [Demo 运行记录](docs/demo_run_records.md)
- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)

## 路线图

```text
v0.1 通用检索 Skill：配置、导入、检索、demo、文档
v0.2 新闻调研 workflow：多问题检索和 markdown 报告草稿
v0.3 开源可复现合成语料 demo
v0.4 引用质量增强：去重、引用统计、证据覆盖检查
v0.5 可插拔 AnySearch connector
v0.6 可插拔 MCP / OpenVikingBot adapter
```

## License

本项目使用 MIT License。

注意：本项目依赖的 OpenViking 是独立上游项目，当前 OpenViking 发布包标注为 AGPL-3.0，请同时遵守 OpenViking 自身许可证要求。
