# 合成语料 Demo 运行记录

运行日期：2026-05-22

## 1. 语料来源

合成语料路径：

```text
examples\synthetic_ai_news\source
```

语料规模：

```text
8 篇中文 markdown 合成资料
```

主题：

```text
AI 搜索与端侧智能产品趋势
```

这些资料为项目自写内容，不代表真实新闻报道，可以随仓库一起开源。

## 2. 导入目标

```text
viking://resources/synthetic-ai-news
```

## 3. 验证命令

一键检索 demo：

```powershell
.\examples\synthetic_ai_news\run_demo.ps1 -Question "为什么开源项目需要合成 demo 语料"
```

手动导入：

```powershell
ov-search-skill import-local examples\synthetic_ai_news\source --to viking://resources/synthetic-ai-news
```

手动检索：

```powershell
ov-search-skill search "端侧大模型和本地检索有什么关系" --scope viking://resources/synthetic-ai-news --top-k 5 --documents-only --format text
```

生成检索型调研草稿：

```powershell
.\examples\synthetic_ai_news\run_research.ps1
```

## 4. 验证结果

单次检索已成功返回合成语料中的原始 markdown 文档，例如：

```text
2026-05-13-data-governance-privacy
2026-05-15-product-roadmap-summary
2026-05-09-open-source-retrieval-tools
2026-05-11-ai-search-evaluation
```

research workflow 默认输出：

```text
reports\synthetic_ai_news_research_draft.md
```

本地验证结果：

```text
5 个调研章节
每节 Top 4
共 20 条 viking:// 引用
```

并确认没有出现明显无效占位回答，例如：

```text
没有找到相关结果
无法回答
尚未录入具体内容
```

该报告是本地生成产物，默认不会提交到 Git。

## 5. 当前结论

合成语料 demo 的目标是解决开源复现问题：

```text
不依赖旧项目路径
不复制新闻全文
不涉及第三方新闻版权
可以完整展示 import-local、search、research
```
