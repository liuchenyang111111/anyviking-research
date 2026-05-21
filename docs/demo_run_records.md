# Demo 运行记录

这份文档集中记录项目自带 demo 的本地验证结果。生成的报告草稿位于 `reports/`，默认不会提交到 Git。

## 合成语料 Demo

运行日期：2026-05-22

语料路径：

```text
examples\synthetic_ai_news\source
```

导入目标：

```text
viking://resources/synthetic-ai-news
```

验证命令：

```powershell
.\examples\synthetic_ai_news\run_demo.ps1 -Question "为什么开源项目需要合成 demo 语料"
.\examples\synthetic_ai_news\run_research.ps1
```

验证结果：

```text
8 篇中文 markdown 合成资料
5 个调研章节
每节 Top 4
共 20 条 viking:// 引用
8 条 citation_stats
4 条 quality_warnings
```

输出文件：

```text
reports\synthetic_ai_news_research_draft.md
reports\synthetic_ai_news_research_draft.json
```

结论：

```text
不依赖旧项目路径
不复制新闻全文
不涉及第三方新闻版权
可以完整展示 import-local、search、research
```

## 新闻语料 Demo

运行日期：2026-05-21

阶段二补充验证日期：2026-05-22

语料路径：

```text
D:\Github\OpenViking_Run\workspace\news_raw\us-china-relations\2026-05-16
```

语料规模：

```text
26 篇 markdown 新闻文章
约 210 KB
```

导入目标：

```text
viking://resources/news-us-china-2026-05
```

验证命令：

```powershell
.\scripts\import_news_demo.ps1
ov-search-skill search "特朗普访华实际达成了哪些成果" --scope viking://resources/news-us-china-2026-05 --top-k 5 --documents-only --format text
ov-search-skill research examples\news_us_china\research_questions.yaml --output reports\news_us_china_research_draft.md --top-k 5
```

验证结果：

```text
7 个调研章节
每节 Top 5
共 35 条 viking:// 引用
```

输出文件：

```text
reports\news_us_china_research_draft.md
```

说明：

- 当前仓库不复制新闻全文，只记录旧项目本地路径和复现方式。
- 新闻 demo 用来证明真实语料检索链路。
- 公开展示优先使用合成语料 demo。
