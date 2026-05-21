# 合成 AI 新闻语料 Demo

这个 demo 使用项目自写的合成资料，演示 OpenViking Search Skill 的完整开源可复现链路。

## 为什么需要这个 demo

旧项目新闻语料可以证明真实资料检索能力，但它有两个问题：

- 文件在本机旧项目目录里，别人 clone 仓库后没有这些资料。
- 新闻全文可能有版权风险，不适合直接提交到开源仓库。

所以这里新增一套自写语料。它不是现实新闻，而是围绕“AI 搜索与端侧智能产品趋势”写的模拟资料，目的是让任何人都能复现：

```text
本地 markdown 资料
-> OpenViking 导入
-> ov-search-skill search
-> ov-search-skill research
```

## 语料内容

源码目录：

```text
examples\synthetic_ai_news\source
```

规模：

```text
8 篇中文 markdown 合成资料
```

主题包括：

- AI 搜索市场。
- 端侧大模型设备。
- Agent 浏览器与工作流。
- 企业知识库检索。
- 开源检索工具生态。
- AI 搜索评测。
- 数据治理与隐私。
- 产品路线建议。

每篇文档都明确标注：

```text
本文为 OpenViking Search Skill 项目 demo 使用的合成资料，不代表真实新闻报道。
```

## OpenViking 资源路径

建议导入到：

```text
viking://resources/synthetic-ai-news
```

## 一键运行检索 demo

```powershell
.\examples\synthetic_ai_news\run_demo.ps1 -Question "为什么开源项目需要合成 demo 语料"
```

脚本会执行：

```text
检查 OpenViking 健康状态
-> 导入合成语料
-> 查看资源树
-> 执行一次 documents-only 检索
```

## 生成检索型调研草稿

```powershell
.\examples\synthetic_ai_news\run_research.ps1
```

输出：

```text
reports\synthetic_ai_news_research_draft.md
```

这个文件是本地生成产物，默认不会提交到 Git。

## 手动命令

导入：

```powershell
ov-search-skill import-local examples\synthetic_ai_news\source --to viking://resources/synthetic-ai-news
```

检索：

```powershell
ov-search-skill search "端侧大模型和本地检索有什么关系" --scope viking://resources/synthetic-ai-news --top-k 5 --documents-only --format text
```

生成草稿：

```powershell
ov-search-skill research examples\synthetic_ai_news\research_questions.yaml --output reports\synthetic_ai_news_research_draft.md --top-k 4
```

更多问题见 [queries.md](queries.md)。
