[English](README.md) | [简体中文](README-ZH.md)

# AnyViking Research

AnyViking Research 是一个 CLI 桥接工具，用来把 AnySearch 的公网搜索结果保存成本地 Markdown，再导入 OpenViking，供后续 Agent 检索。

```text
AnySearch -> 本地 markdown -> OpenViking -> viking:// 检索
```

当前阶段主要聚焦四件事：

- 通过 AnySearch 搜索公网资料
- 把原始 JSON、Markdown 和 manifest 保存到本地
- 把保存好的资料导入 OpenViking
- 让你自己的 Agent 通过 `anyviking search` 或 OpenViking API/CLI 检索这些资料

仓库里还附带了一个可选的 Agent Skill，位置在 [skills/anyviking-research](skills/anyviking-research)。它的作用是把这套工作流写成稳定的使用说明，方便 Agent 按固定流程调用。

## 参考项目

- [AnySearch Skill](https://github.com/anysearch-ai/anysearch-skill)
- [AnySearch 文档](https://www.anysearch.com/docs)
- [OpenViking](https://github.com/volcengine/OpenViking)
- [OpenViking 文档](https://docs.openviking.ai/)

## 运行要求

- Python `3.12`
- 本地可用的 OpenViking 安装
- 可选的 `ANYSEARCH_API_KEY`，有的话联网搜索会更稳定

## 快速开始

Windows PowerShell：

```powershell
git clone https://github.com/liuchenyang111111/anyviking-research.git
cd anyviking-research
.\install.ps1
.\.venv\Scripts\anyviking.exe doctor
```

Linux / macOS：

```bash
git clone https://github.com/liuchenyang111111/anyviking-research.git
cd anyviking-research
./install.sh
source .venv/bin/activate
anyviking doctor
```

安装开发依赖：

```powershell
.\install.ps1 -Dev
```

```bash
./install.sh --dev
```

## 配置 OpenViking

先复制示例配置：

```powershell
Copy-Item config\ov.conf.example config\ov.conf
Copy-Item config\ovcli.conf.example config\ovcli.conf
```

```bash
cp config/ov.conf.example config/ov.conf
cp config/ovcli.conf.example config/ovcli.conf
```

编辑 `config/ov.conf`，填入你自己的模型服务配置，然后启动 OpenViking：

```powershell
.\scripts\start_openviking.ps1
```

```bash
./scripts/start_openviking.sh
```

检查服务是否正常：

```bash
anyviking health
```

## 配置 AnySearch

如果你有 AnySearch key：

```powershell
$env:ANYSEARCH_API_KEY = "your-key"
```

```bash
export ANYSEARCH_API_KEY="your-key"
```

如果你要连接别的兼容端点，也可以设置：

```powershell
$env:ANYSEARCH_API_URL = "https://your-endpoint.example"
```

```bash
export ANYSEARCH_API_URL="https://your-endpoint.example"
```

对于直接访问 OpenViking HTTP 服务的命令，CLI 还会读取 `OPENVIKING_URL`。

## 主要命令

| 命令 | 作用 |
| --- | --- |
| `anyviking doctor` | 检查本地环境是否就绪 |
| `anyviking health` | 检查 OpenViking 健康状态 |
| `anyviking status` | 查看 OpenViking 服务状态 |
| `anyviking search-web` | 通过 AnySearch 搜索公网 |
| `anyviking fetch-web` | 保存原始 JSON、Markdown 和 manifest |
| `anyviking sync` | 搜索、保存并导入 OpenViking |
| `anyviking import-local` | 导入已有本地文件或目录 |
| `anyviking tree` | 查看 `viking://` 资源树 |
| `anyviking search` | 检索已导入的 OpenViking 内容 |

更多命令说明见：[docs/cli_reference.md](docs/cli_reference.md)

## 一条典型链路

只搜索：

```bash
anyviking search-web "OpenViking GitHub" --max-results 3
```

把搜索结果保存到本地：

```bash
anyviking fetch-web "OpenViking GitHub" --max-results 3 --output data/web/openviking-github
```

保存并导入 OpenViking：

```bash
anyviking sync "OpenViking GitHub" --max-results 3 --output data/web/openviking-github --to viking://resources/openviking-github
```

查看导入后的资源树：

```bash
anyviking tree viking://resources/openviking-github -L 2
```

检索已导入资料：

```bash
anyviking search "What is OpenViking?" --scope viking://resources/openviking-github --top-k 3 --format text --documents-only
```

## 本地产物

下面这些运行产物只保留在本地，默认不会提交到 Git：

```text
data/       AnySearch 抓取结果和 markdown 文件
workspace/  OpenViking 本地数据库、索引和日志
reports/    可选的本地生成输出
config/ov.conf
config/ovcli.conf
.env
```

## Agent 怎么读取这些资料

`viking://resources/...` 是 OpenViking 的虚拟 URI，不是普通文件路径。

Agent 需要借助一个工具来读它，例如：

```bash
anyviking search "your question" --scope viking://resources/your-topic --format json --documents-only
```

也可以直接接 OpenViking API/CLI。

## 文档

- [docs/configuration.md](docs/configuration.md)
- [docs/troubleshooting.md](docs/troubleshooting.md)
- [docs/architecture.md](docs/architecture.md)

## 验证命令

```bash
python -m unittest discover -s tests
python -m compileall -q src tests
python -m build
python -m twine check dist/*
```

## 许可证

AnyViking Research 使用 MIT License。OpenViking 仍然是独立的上游依赖，使用时请遵守它自己的许可证条款。
