# AnyViking Research

[中文](#中文) | [English](#english)

## 中文

AnyViking Research 是一个 CLI 工具，用来把 AnySearch 找到的公网资料保存成本地 markdown，然后导入 OpenViking，让用户自己的 Agent 可以通过 `viking://` 范围检索这些资料。

它不是搜索引擎，也不是 OpenViking 的替代品，也不是完整的 Agent 产品。

```text
AnySearch
  负责公网搜索

AnyViking Research
  负责保存、整理、导入、查询

OpenViking
  负责本地资源存储、索引和 viking:// 检索
```

上游请看 [AnySearch Skill](https://github.com/anysearch-ai/anysearch-skill) 和 [AnySearch 文档](https://www.anysearch.com/docs)。  
下游请看 [OpenViking](https://github.com/volcengine/OpenViking) 和 [OpenViking 文档](https://docs.openviking.ai/)。

### 当前状态

已经实现：

- `ar doctor`：检查本地环境。
- `ar search-web`：通过 AnySearch 搜索公网。
- `ar fetch-web`：把搜索结果保存为 raw JSON、markdown 和 manifest。
- `ar sync`：搜索网页，保存 markdown，然后导入 OpenViking。
- `ar import-local`：导入已有本地语料。
- `ar tree`：查看 OpenViking 的 `viking://` 资源树。
- `ar search`：检索已导入 OpenViking 的资料。

没有实现：

- 一键安装包。
- Docker / docker-compose 部署。
- Web UI。
- MCP server。
- VikingBot 封装。
- 内置示例语料。
- 自动写完整调研报告。

如果你没有 AnySearch 或 OpenViking，当前不能一条命令跑完整链路。你需要先安装本项目和 OpenViking，并准备好 AnySearch 访问能力。

### 部署模型

这个项目现在是三段式部署：

```text
1. AnySearch
   远端搜索能力。通常通过 API key 或匿名请求访问。

2. OpenViking
   本地服务。需要安装并启动 openviking-server。

3. AnyViking Research
   本项目。提供 ar 命令，把两者串起来。
```

当前没有把这三者打成一个安装包。后续可以考虑：

- Docker Compose。
- Windows 一键启动脚本。
- pipx 安装。
- MCP server 封装。

但现在公开仓库先保持 CLI-first，方便调试每一层。

### 安装

先克隆仓库：

```powershell
git clone https://github.com/liuchenyang111111/anyviking-research.git
cd anyviking-research
```

创建虚拟环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

安装项目和 OpenViking 依赖：

```powershell
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .[openviking] --no-build-isolation
```

开发者可以安装额外打包工具：

```powershell
python -m pip install -e .[dev,openviking] --no-build-isolation
```

如果没有激活虚拟环境，可以直接运行：

```powershell
.\.venv\Scripts\ar.exe doctor
```

### 配置 OpenViking

复制配置模板：

```powershell
Copy-Item config\ov.conf.example config\ov.conf
Copy-Item config\ovcli.conf.example config\ovcli.conf
```

编辑 `config\ov.conf`，填入你自己的模型服务配置。真实配置文件不要提交到 Git。

启动 OpenViking：

```powershell
.\scripts\start_openviking.ps1
```

检查服务：

```powershell
ar health
```

### 配置 AnySearch

AnySearch 是上游搜索能力。项目里只调用它，不实现它。

如果你有 AnySearch key：

```powershell
$env:ANYSEARCH_API_KEY = "your-key"
```

如果没有 key，可以先试匿名请求，但稳定性和额度取决于 AnySearch 服务。

### 一次跑通完整流程

检查环境：

```powershell
ar doctor
```

只搜索公网：

```powershell
ar search-web "OpenViking GitHub" --max-results 3
```

保存搜索结果到本地：

```powershell
ar fetch-web "OpenViking GitHub" --max-results 3 --output data\web\openviking-github
```

保存并导入 OpenViking：

```powershell
ar sync "OpenViking GitHub" --max-results 3 --output data\web\openviking-github --to viking://resources/openviking-github
```

查看资源树：

```powershell
ar tree viking://resources/openviking-github -L 2
```

检索已导入资料：

```powershell
ar search "What is OpenViking?" --scope viking://resources/openviking-github --top-k 3 --format text --documents-only
```

### 常用命令和参数

| 命令 | 作用 | 常用参数 |
| --- | --- | --- |
| `ar doctor` | 检查环境 | `--json` |
| `ar health` | 检查 OpenViking 服务 | `--url` |
| `ar search-web` | 搜索公网 | `--max-results`, `--domain`, `--language`, `--freshness` |
| `ar fetch-web` | 搜索并保存本地文件 | `--output`, `--max-results` |
| `ar sync` | 搜索、保存并导入 OpenViking | `--output`, `--to`, `--max-results` |
| `ar import-local` | 导入本地语料 | `--to` |
| `ar tree` | 查看资源树 | `-L` |
| `ar search` | 检索 OpenViking | `--scope`, `--top-k`, `--format`, `--documents-only` |

### Agent 怎么读取资料

`viking://resources/...` 不是普通文件路径。Agent 不能靠字符串本身读取内容。

Agent 需要一个工具，例如：

```powershell
ar search "your question" --scope viking://resources/your-topic --format json --documents-only
```

也可以让用户自己的 Agent 直接接 OpenViking API、OpenViking CLI，或者后续接 MCP server。

不需要 VikingBot。VikingBot 只是另一种上层封装。

### 输出目录

这些目录都是本地运行产物，不上传 GitHub：

```text
data/       fetch-web 和 sync 保存的网页资料
reports/    本地生成输出，如果某些命令需要
workspace/  OpenViking 本地工作区
```

真实配置也不上传：

```text
config/ov.conf
config/ovcli.conf
.env
```

### 常见问题

#### `ar` 找不到

先确认虚拟环境是否激活。也可以直接用：

```powershell
.\.venv\Scripts\ar.exe doctor
```

#### OpenViking 连接失败

先启动服务：

```powershell
.\scripts\start_openviking.ps1
```

再检查：

```powershell
ar health
```

#### AnySearch 请求失败

可能原因：

- 没有网络。
- AnySearch 服务拒绝请求。
- 匿名额度不稳定。
- API key 没有设置。

可以设置：

```powershell
$env:ANYSEARCH_API_KEY = "your-key"
```

#### 导入成功但搜不到

可以检查：

```powershell
ar tree viking://resources/your-topic -L 2
```

然后增大检索数量：

```powershell
ar search "question" --scope viking://resources/your-topic --top-k 10 --format text --documents-only
```

### 项目结构

```text
src/anyviking_research/     Python 源码
tests/                      单元测试
config/                     OpenViking 配置模板
scripts/                    启停 OpenViking 的脚本
skills/anyviking-research/  Agent Skill 包
docs/                       补充文档
```

### 测试

```powershell
python -m unittest discover -s tests
python -m compileall -q src tests
```

## English

AnyViking Research is a CLI bridge that saves public web search results as local markdown files, imports them into OpenViking, and lets another Agent retrieve them through a `viking://` scope.

It is not a search engine, not a replacement for OpenViking, and not a full Agent product.

```text
AnySearch
  discovers public web sources

AnyViking Research
  saves, normalizes, imports, and queries

OpenViking
  stores local resources and returns viking:// retrieval results
```

Upstream search is based on [AnySearch Skill](https://github.com/anysearch-ai/anysearch-skill) and [AnySearch docs](https://www.anysearch.com/docs).  
Local indexing and retrieval are based on [OpenViking](https://github.com/volcengine/OpenViking) and [OpenViking docs](https://docs.openviking.ai/).

### Current Status

Implemented:

- `ar doctor`
- `ar search-web`
- `ar fetch-web`
- `ar sync`
- `ar import-local`
- `ar tree`
- `ar search`

Not implemented:

- one-click installer
- Docker / docker-compose
- Web UI
- MCP server
- VikingBot wrapper
- bundled demo corpus
- automatic final report generation

### Install

```powershell
git clone https://github.com/liuchenyang111111/anyviking-research.git
cd anyviking-research
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

Edit `config\ov.conf` and set your own model provider credentials.

Optional AnySearch key:

```powershell
$env:ANYSEARCH_API_KEY = "your-key"
```

### Run

```powershell
.\scripts\start_openviking.ps1
ar doctor
ar search-web "OpenViking GitHub" --max-results 3
ar sync "OpenViking GitHub" --max-results 3 --output data\web\openviking-github --to viking://resources/openviking-github
ar search "What is OpenViking?" --scope viking://resources/openviking-github --top-k 3 --format text --documents-only
```

### Notes For Agents

`viking://` is a virtual OpenViking URI. An Agent needs a tool such as `ar search`, OpenViking CLI/API, or a future MCP server to read it.

### Tests

```powershell
python -m unittest discover -s tests
python -m compileall -q src tests
```

## License

AnyViking Research uses the MIT License. OpenViking is a separate upstream dependency; follow OpenViking's license terms when using it.
