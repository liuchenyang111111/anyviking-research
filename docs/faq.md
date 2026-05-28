# FAQ

## 1. OpenViking 已经能检索了，为什么还要做这个项目？

OpenViking 是底层检索后端，本项目是包装层。

OpenViking 负责：

- 导入资源。
- 建立语义索引。
- 管理 `viking://` URI。
- 执行检索。

本项目负责：

- 统一配置和启动方式。
- 封装常用命令。
- 输出结构化 JSON。
- 过滤自动摘要，优先返回原始文档。
- 提供 AI Agent 可读的 `SKILL.md`。
- 提供可复现 demo 和文档。

## 2. Skill 是什么？

这里的 Skill 不是模型能力，而是给 AI Agent 使用的一套工具说明和调用约定。

`SKILL.md` 会告诉 Agent：

- 什么时候该用这个工具。
- 怎么检查服务。
- 怎么导入资料。
- 怎么检索。
- 什么情况下用 `--documents-only`。

## 3. AnySearch 是不是必须接入？

不是。

当前 AnySearch 只是形态参考。它展示了一个搜索工具如何包装成 Agent Skill。

未来可以考虑：

```text
AnySearch 搜公网
-> 保存为 markdown
-> 导入 OpenViking
-> 用本项目统一检索
```

## 4. OpenVikingBot 还需要吗？

当前基础版本不需要。

基础链路是：

```text
OpenViking Server
-> ar
-> JSON 检索结果
```

OpenVikingBot 可以以后作为增强功能，用来做对话式检索和报告生成。

## 5. 用户级配置和项目配置有什么区别？

用户级配置在：

```text
C:\Users\ASUS\.openviking\ov.conf
```

这是这台电脑默认的 OpenViking 配置。

项目配置在：

```text
config\ov.conf
```

本项目推荐用项目配置启动：

```powershell
openviking-server --config config\ov.conf
```

这样当前项目的数据会进入当前项目的 `workspace/`。

## 6. 为什么不能提交 config/ov.conf？

因为真实 `config/ov.conf` 里会有 API key。

仓库只提交：

```text
config/ov.conf.example
```

真实配置已被 `.gitignore` 忽略。

## 7. 为什么新闻全文不复制进仓库？

新闻文章可能涉及版权，直接复制进开源仓库不稳。

所以当前新闻 demo 只记录：

- 旧项目本地语料路径。
- 导入命令。
- 查询问题。
- 运行记录。

## 7.1 合成 demo 语料是什么？

合成 demo 语料是项目自己写的一组 markdown 文档，不是真实新闻。

位置：

```text
examples\synthetic_ai_news\source
```

它的作用是让别人 clone 仓库后，不依赖你的旧项目路径，也能完整复现：

```text
import-local -> search -> research
```

公开演示时优先用这套语料，旧新闻 demo 只作为本机真实语料验证。

## 8. 搜索结果里的 .abstract.md 和 .overview.md 是什么？

这是 OpenViking 自动生成的摘要文件。

它们适合快速理解资料集，但如果你要引用原始文档，可以加：

```powershell
--documents-only
```

例如：

```powershell
ar search "特朗普访华成果" --scope viking://resources/news-us-china-2026-05 --documents-only
```

## 9. ar 找不到怎么办？

先确认项目已经可编辑安装：

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e . --no-deps --no-build-isolation
```

再运行：

```powershell
ar --help
```

## 10. health 失败怎么办？

先确认 OpenViking 服务是否启动：

```powershell
.\scripts\start_openviking.ps1
```

再检查：

```powershell
ar health
```

如果仍失败，检查：

- `config/ov.conf` 是否存在。
- API key 是否正确。
- 端口 `1933` 是否被占用。
- `storage.workspace` 是否能写入。

## 11. research 命令和 search 命令有什么区别？

`search` 是问一次，返回一次检索结果。

`research` 是读一个 YAML 文件，对多个调研问题分别执行检索，然后生成一份 markdown 草稿。

可以理解为：

```text
search = 单次检索
research = 多次检索 + 草稿整理
```

`research` 默认会过滤 OpenViking 自动摘要和明显无效的占位回答，更适合后续写报告。
