# 中美关系新闻语料 Demo

这个 demo 使用旧项目里的新闻语料，验证 OpenViking 对真实新闻资料的导入和检索能力。

## 语料来源

旧项目本地路径：

```text
D:\Github\OpenViking_Run\workspace\news_raw\us-china-relations\2026-05-16
```

语料规模：

```text
26 篇 markdown 新闻文章
约 210 KB
```

这些文件来自旧项目的 RSS 新闻抓取流程，包含 BBC 中文和 The Guardian 等来源。当前新项目不复制新闻全文，只记录导入路径、查询问题和验证方式。

## OpenViking 资源路径

建议导入到：

```text
viking://resources/news-us-china-2026-05
```

## 导入命令

```powershell
ov-search-skill import-local D:\Github\OpenViking_Run\workspace\news_raw\us-china-relations\2026-05-16 --to viking://resources/news-us-china-2026-05
```

## 检索命令

```powershell
ov find "特朗普访华实际达成了哪些成果" --uri viking://resources/news-us-china-2026-05
ov-search-skill search "特朗普访华实际达成了哪些成果" --scope viking://resources/news-us-china-2026-05 --top-k 5 --format text
ov-search-skill search "特朗普访华实际达成了哪些成果" --scope viking://resources/news-us-china-2026-05 --top-k 5 --documents-only --format text
```

更多问题见 [queries.md](queries.md)。

也可以一键运行 demo：

```powershell
.\examples\news_us_china\run_demo.ps1 -Question "特朗普访华实际达成了哪些成果"
```

## 检索型调研草稿

阶段二新增了轻量 research workflow。它不会直接生成最终分析结论，而是读取一组调研问题，逐个检索 OpenViking，并输出带 `viking://` 引用的 markdown 草稿。

配置文件：

```text
examples\news_us_china\research_questions.yaml
```

运行：

```powershell
.\examples\news_us_china\run_research.ps1
```

直接调用 CLI：

```powershell
ov-search-skill research examples\news_us_china\research_questions.yaml --output reports\news_us_china_research_draft.md --top-k 5
```

输出：

```text
reports\news_us_china_research_draft.md
```

默认行为：

- 每个章节保留 Top 5 检索结果。
- 过滤 OpenViking 自动生成的 `.abstract.md` / `.overview.md`。
- 过滤明显无效的占位回答，例如“没有找到相关结果”“无法回答”。

如果过滤后结果太少，可以调大候选池：

```powershell
ov-search-skill research examples\news_us_china\research_questions.yaml --output reports\news_us_china_research_draft.md --top-k 5 --fetch-k 60
```

本次运行记录见 [../../docs/news_demo_run_record.md](../../docs/news_demo_run_record.md)。
