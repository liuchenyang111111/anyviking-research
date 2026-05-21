# 项目上下文

这份文档是给项目负责人和 AI/Codex 看的项目记忆入口。它记录这个新项目为什么要做、旧项目已经验证了什么，以及新项目准备如何继续。

## 项目来源

旧项目路径：

```text
D:\Github\OpenViking_Run
```

旧项目已经验证过一条链路：

```text
新闻/RSS 资料
  -> 抓取正文并保存为 markdown
  -> 导入 OpenViking
  -> 通过 OpenViking 语义检索
  -> 让 AI 基于检索结果写回答或报告
```

## 新项目目标

新项目路径：

```text
D:\Github\OpenViking_Search_Skill
```

这个项目不再只做一个固定新闻主题，而是先整理成一个可复用的 OpenViking 本地语料检索 Skill。第二阶段重点是把环境、配置、最小语料导入、检索命令、项目 CLI 和轻量调研 workflow 跑清楚。第三阶段补充一套项目自写的合成 AI 新闻语料，让开源用户 clone 后也能完整复现 demo。

## 当前阶段边界

第二阶段先做：

- Python 3.12 虚拟环境。
- OpenViking 0.3.17。
- 本项目专用配置说明。
- 小型 markdown 测试语料。
- `ov find` 检索验证。
- `ov_search_skill` 最小 Python/CLI 包装。
- 旧项目新闻语料 demo。
- `ov-search-skill research` 检索型调研草稿。
- 合成 AI 新闻语料 demo：`examples/synthetic_ai_news`。

暂时不做：

- VikingBot。
- LLM 自动写完整报告。
- AnySearch。
- Web UI。
- 大型仓库导入。
