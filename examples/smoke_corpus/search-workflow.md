# 检索流程

这个项目的基础检索流程分为四步：

1. 把本地笔记或文档整理成 markdown。
2. 使用 `ov add-resource` 把 markdown 文件夹导入 OpenViking。
3. 等待 OpenViking 完成索引。
4. 使用 `ov find` 或项目 CLI 提出问题。

一次成功的最小测试，应该能返回以 `viking://resources/smoke-corpus` 开头的引用结果。

如果要做多问题调研，可以把问题写进 YAML 配置，再运行：

```powershell
ov-search-skill research <questions.yaml> --output reports\research_draft.md
```

这样会生成一份检索型草稿，而不是直接生成最终报告。
