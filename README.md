# AnyViking Research

[中文](#中文) | [English](#english)

## 中文

AnyViking Research 是一个命令行工具，把公网搜索结果整理成 OpenViking 可以检索的本地资料。

它不是搜索引擎，也不是 OpenViking 的替代品。它做的是中间这一段：

```text
AnySearch 发现网页
-> AnyViking Research 保存为 markdown 并导入
-> OpenViking 建索引并提供 viking:// 检索
-> 用户自己的 Agent 调用检索结果继续分析
```

上游能力参考 [AnySearch Skill](https://github.com/anysearch-ai/anysearch-skill) 和 [AnySearch 文档](https://www.anysearch.com/docs)。  
下游存储和检索参考 [OpenViking](https://github.com/volcengine/OpenViking) 和 [OpenViking 文档](https://docs.openviking.ai/)。

### 已经实现

- `ar doctor`：检查本地环境。
- `ar search-web`：调用 AnySearch 搜公网。
- `ar fetch-web`：把搜索结果保存成 raw JSON、markdown 和 manifest。
- `ar sync`：搜索网页，保存 markdown，然后导入 OpenViking。
- `ar import-local`：把本地文件夹导入 OpenViking。
- `ar tree`：查看 `viking://` 资源树。
- `ar search`：在 OpenViking 里检索已入库资料。

### 不做什么

- 不内置示例语料。
- 不上传 `reports/`、`data/`、`workspace/`。
- 不上传真实 `config/ov.conf`、`config/ovcli.conf`。
- 不把 roadmap/changelog 放在 GitHub 上。
- 不要求使用 VikingBot；用户自己的 Agent 可以通过 `ar search` 或 OpenViking 工具读取资料。

### 安装

```powershell
cd D:\Github\anyviking-research
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .[openviking] --no-build-isolation
```

开发时可以装额外工具：

```powershell
python -m pip install -e .[dev,openviking] --no-build-isolation
```

### 配置

复制 OpenViking 配置模板：

```powershell
Copy-Item config\ov.conf.example config\ov.conf
Copy-Item config\ovcli.conf.example config\ovcli.conf
```

编辑 `config\ov.conf`，填入你自己的模型服务 key。真实配置不要提交。

AnySearch key 是可选的：

```powershell
$env:ANYSEARCH_API_KEY = "your-key"
```

检查环境：

```powershell
ar doctor
```

### 常用流程

启动 OpenViking：

```powershell
.\scripts\start_openviking.ps1
ar health
```

只搜索网页：

```powershell
ar search-web "OpenViking GitHub" --max-results 3
```

搜索并保存成本地 markdown：

```powershell
ar fetch-web "OpenViking GitHub" --max-results 3 --output data\web\openviking-github
```

搜索、保存并导入 OpenViking：

```powershell
ar sync "OpenViking GitHub" --max-results 3 --output data\web\openviking-github --to viking://resources/openviking-github
```

查询已经入库的资料：

```powershell
ar search "What is OpenViking?" --scope viking://resources/openviking-github --top-k 3 --format text --documents-only
```

### Agent 怎么用

仓库里有一个 Skill 包：

```text
skills/anyviking-research/
```

这个 Skill 不直接搜索，也不直接写 OpenViking。它只告诉 Agent 什么时候该调用 `ar search-web`、`ar fetch-web`、`ar sync`、`ar search`。

Agent 需要能运行终端命令。如果 `ar` 不在 PATH 里，可以直接用：

```powershell
.\.venv\Scripts\ar.exe doctor
```

### 项目结构

```text
src/anyviking_research/     Python 源码
tests/                      单元测试
config/                     OpenViking 配置模板
scripts/                    启停 OpenViking 的本地脚本
skills/anyviking-research/  Agent Skill 包
docs/                       简短文档
```

### 测试

```powershell
python -m unittest discover -s tests
python -m compileall -q src tests
```

## English

AnyViking Research is a CLI tool that turns public web search results into local OpenViking resources.

It is not a search engine and it does not replace OpenViking. It only connects the two sides:

```text
AnySearch discovers web pages
-> AnyViking Research saves markdown and imports it
-> OpenViking indexes resources and exposes viking:// retrieval
-> the user's own Agent reads the indexed evidence
```

Upstream discovery is based on [AnySearch Skill](https://github.com/anysearch-ai/anysearch-skill) and [AnySearch docs](https://www.anysearch.com/docs).  
Local indexing and retrieval are based on [OpenViking](https://github.com/volcengine/OpenViking) and [OpenViking docs](https://docs.openviking.ai/).

### What Works

- `ar doctor`: check the local environment.
- `ar search-web`: search the public web with AnySearch.
- `ar fetch-web`: save results as raw JSON, markdown, and a manifest.
- `ar sync`: search, save markdown, and import into OpenViking.
- `ar import-local`: import an existing local folder into OpenViking.
- `ar tree`: inspect a `viking://` resource tree.
- `ar search`: retrieve indexed OpenViking resources.

### Install

```powershell
cd D:\Github\anyviking-research
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .[openviking] --no-build-isolation
```

### Configure

```powershell
Copy-Item config\ov.conf.example config\ov.conf
Copy-Item config\ovcli.conf.example config\ovcli.conf
```

Edit `config\ov.conf` and set your own model provider credentials. Do not commit real config files.

Optional AnySearch key:

```powershell
$env:ANYSEARCH_API_KEY = "your-key"
```

### Common Workflow

```powershell
.\scripts\start_openviking.ps1
ar health
```

```powershell
ar sync "OpenViking GitHub" --max-results 3 --output data\web\openviking-github --to viking://resources/openviking-github
```

```powershell
ar search "What is OpenViking?" --scope viking://resources/openviking-github --top-k 3 --format text --documents-only
```

### Repository Layout

```text
src/anyviking_research/     Python package
tests/                      unit tests
config/                     OpenViking config examples
scripts/                    local OpenViking helper scripts
skills/anyviking-research/  packaged Agent Skill
docs/                       short human-facing docs
```

### Tests

```powershell
python -m unittest discover -s tests
python -m compileall -q src tests
```

## License

AnyViking Research uses the MIT License. OpenViking is a separate upstream dependency; follow OpenViking's license terms when using it.
