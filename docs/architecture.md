# 项目架构说明

这个项目的核心定位是：

```text
OpenViking 本地语料通用检索 Skill
+ 可复现合成语料 demo
+ 新闻调研 demo
```

## 1. 分层关系

```text
本地资料
  -> markdown 语料
  -> OpenViking 资源导入
  -> OpenViking 语义索引
  -> ov-search-skill CLI / Python 包
  -> AI Agent 或用户使用检索结果
```

OpenViking 负责底层能力：

- 文件导入。
- `viking://` 资源管理。
- 语义索引。
- 检索和摘要。

本项目负责包装层：

- 项目专用配置说明。
- 导入、查看、检索的统一 CLI。
- 结构化 JSON 输出。
- 过滤自动摘要，只返回原始文档。
- 轻量检索型调研 workflow。
- 面向 AI Agent 的 `SKILL.md`。
- 可复现 demo。

## 2. 为什么不直接只用 OpenViking

OpenViking 是后端和底层工具，能力很完整，但对一个具体项目来说，还需要一层“使用约定”：

- 资料导入到哪个 URI。
- 查询时 scope 怎么写。
- 返回 JSON 还是表格。
- 是否过滤 `.abstract.md` / `.overview.md`。
- demo 怎么复现。
- AI Agent 什么时候该用这个检索工具。

这个项目就是把这些约定整理成开源项目。

## 3. 与 AnySearch 的关系

AnySearch Skill 是形态参考，不是当前 v1 的强依赖。

当前理解：

```text
AnySearch
  -> 公网搜索 / 网页内容获取 / Agent search skill 形态参考

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
  -> 后续用本项目统一检索
```

## 4. 当前目录职责

```text
src/ov_search_skill/
  Python 包和 CLI 源码。retrievers/ 负责检索适配，workflows/ 负责组合检索流程

scripts/
  Windows PowerShell 辅助脚本

examples/smoke_corpus/
  最小测试语料

examples/synthetic_ai_news/
  项目自写的合成 AI 新闻语料，适合开源复现完整 demo

examples/news_us_china/
  旧项目新闻调研 demo 的说明、查询问题和 research YAML 配置

docs/
  环境、架构、概念和运行记录

config/*.example
  无密钥配置模板
```

## 5. 当前稳定链路

```text
Python 3.12
-> openviking 0.3.17
-> config/ov.conf
-> openviking-server
-> ov-search-skill import-local
-> ov-search-skill search
-> ov-search-skill research
```

已验证语料：

- `examples/smoke_corpus`
- `examples/synthetic_ai_news`
- 旧项目中美关系新闻语料

## 6. 后续演进

建议按这个顺序继续：

```text
v0.1 通用检索 Skill：已完成基础链路
v0.2 新闻调研 workflow：已完成轻量检索草稿
v0.3 开源可复现合成语料 demo
v0.4 引用质量增强：去重、引用统计、证据覆盖检查
v0.5 可插拔 AnySearch connector
v0.6 可插拔 MCP / OpenVikingBot adapter
```

OpenVikingBot 暂时不作为核心依赖，只作为后续增强方向。
