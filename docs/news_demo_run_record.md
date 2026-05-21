# 新闻语料 Demo 运行记录

运行日期：2026-05-21

阶段二补充验证日期：2026-05-22

## 1. 语料来源

旧项目新闻语料路径：

```text
D:\Github\OpenViking_Run\workspace\news_raw\us-china-relations\2026-05-16
```

语料规模：

```text
26 篇 markdown 新闻文章
约 210 KB
```

当前新项目没有复制新闻全文，只通过 OpenViking 导入本地路径。

## 2. 导入目标

```text
viking://resources/news-us-china-2026-05
```

导入脚本：

```powershell
.\scripts\import_news_demo.ps1
```

脚本会执行：

```text
检查 OpenViking 服务
-> 统计 markdown 文件
-> ov add-resource 导入语料
-> ov wait 等待后台处理完成
-> ov tree 查看资源树
```

## 3. 验证命令

OpenViking 原生命令：

```powershell
ov find "特朗普访华实际达成了哪些成果" --uri viking://resources/news-us-china-2026-05
```

项目 CLI：

```powershell
ov-search-skill search "特朗普访华实际达成了哪些成果" --scope viking://resources/news-us-china-2026-05 --top-k 5 --format text
```

只看原始文档，过滤 OpenViking 自动生成的 `.abstract.md` / `.overview.md`：

```powershell
ov-search-skill search "特朗普访华实际达成了哪些成果" --scope viking://resources/news-us-china-2026-05 --top-k 5 --documents-only --format text
```

## 4. 验证结果

检索成功返回了新闻相关资源，包括：

```text
特朗普訪華結果分析美國盯著3B中國盯著3T誰佔了上風
Trump leaves China without breakthroughs...
17名美國商界領袖隨特朗普訪華尚未有大訂單浮出水面
What was actually achieved at Trump and Xi...
```

针对问题：

```text
台湾军购案和特朗普访华有什么关系
```

检索成功命中：

```text
特朗普訪華前夕_台灣立法院通過閹割版對美軍購案背後的內外角力
```

## 5. 观察到的现象

OpenViking 会同时返回两类结果：

- 原始文档，比如具体新闻 `.md`。
- 自动生成的摘要文档，比如 `.abstract.md`、`.overview.md`。

如果目标是“快速了解资料集”，摘要结果很有用。

如果目标是“引用原始资料写报告”，建议使用：

```powershell
--documents-only
```

这样项目 CLI 会过滤自动摘要，优先返回原始新闻文档。

## 6. 当前结论

旧项目新闻语料已经成功接入当前新项目的 OpenViking workspace。当前链路已经跑通：

```text
旧项目新闻 markdown
-> 当前项目 OpenViking 配置
-> viking://resources/news-us-china-2026-05
-> ov find
-> ov-search-skill search
```

下一步可以基于这个真实语料 demo 做：

- 固定一组查询问题。
- 生成一个小型检索报告。
- 再决定是否接入 VikingBot，或继续扩展当前轻量 report workflow。

## 7. 阶段二 research workflow 验证

阶段二已经新增：

```powershell
ov-search-skill research examples\news_us_china\research_questions.yaml --output reports\news_us_china_research_draft.md --top-k 5
```

本地验证结果：

```text
7 个调研章节
每节 Top 5
共 35 条 viking:// 引用
```

并确认过滤掉了明显无效的占位回答，例如：

```text
没有找到相关结果
无法回答
尚未录入具体内容
```

输出文件：

```text
reports\news_us_china_research_draft.md
```

该文件属于本地生成产物，已被 `.gitignore` 忽略。
