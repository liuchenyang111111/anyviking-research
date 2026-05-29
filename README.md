# AnyViking Research

[中文](#中文) | [English](#english)

## 中文

AnyViking Research 是一个 CLI 桥接工具：

```text
AnySearch -> 本地 markdown -> OpenViking -> viking:// 检索
```

它负责把 AnySearch 找到的公网资料保存到本地，再导入 OpenViking。之后，用户自己的 Agent 可以通过 `anyviking search`、OpenViking API/CLI，或未来的 MCP server 检索这些资料。

它不是搜索引擎，不替代 OpenViking，也不是完整 Agent 产品。

参考上游项目：

- [AnySearch Skill](https://github.com/anysearch-ai/anysearch-skill)
- [AnySearch 文档](https://www.anysearch.com/docs)
- [OpenViking](https://github.com/volcengine/OpenViking)
- [OpenViking 文档](https://docs.openviking.ai/)

### 已实现

| 命令 | 作用 |
| --- | --- |
| `anyviking doctor` | 检查本地环境 |
| `anyviking health` | 检查 OpenViking 服务 |
| `anyviking status` | 查看 OpenViking 状态 |
| `anyviking search-web` | 调用 AnySearch 搜索公网 |
| `anyviking fetch-web` | 保存搜索结果为 raw JSON、markdown 和 manifest |
| `anyviking sync` | 搜索、保存，并导入 OpenViking |
| `anyviking import-local` | 导入已有本地文件 |
| `anyviking tree` | 查看 `viking://` 资源树 |
| `anyviking search` | 检索已导入 OpenViking 的资料 |

暂未实现：Web UI、MCP server、Docker Compose、VikingBot 封装、完整自动报告生成。

### 部署关系

这个项目现在仍然是三段式部署：

```text
1. AnySearch
   远端搜索能力。本项目只调用它，不实现搜索引擎。

2. OpenViking
   本地存储、索引和检索服务。

3. AnyViking Research
   本项目。负责保存网页资料、整理成本地 markdown、导入 OpenViking。
```

安装脚本可以帮你装本项目和 Python 依赖，但不能自动替你申请 AnySearch key，也不能替你配置模型服务密钥。

### 快速安装

Windows PowerShell：

```powershell
git clone https://github.com/liuchenyang111111/anyviking-research.git
cd anyviking-research
.\install.ps1
.\.venv\Scripts\anyviking.exe doctor
```

如果 PowerShell 阻止脚本执行，可以用：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
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

### 手动安装

Windows：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .[openviking] --no-build-isolation
```

Linux / macOS：

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e '.[openviking]' --no-build-isolation
```

开发者额外安装打包工具：

```bash
python -m pip install -e '.[dev,openviking]' --no-build-isolation
```

### 配置 OpenViking

复制配置模板：

```powershell
Copy-Item config\ov.conf.example config\ov.conf
Copy-Item config\ovcli.conf.example config\ovcli.conf
```

Linux / macOS：

```bash
cp config/ov.conf.example config/ov.conf
cp config/ovcli.conf.example config/ovcli.conf
```

编辑 `config/ov.conf`，填入你自己的模型服务配置。真实配置文件已被 `.gitignore` 忽略。

启动 OpenViking：

```powershell
.\scripts\start_openviking.ps1
```

```bash
./scripts/start_openviking.sh
```

检查服务：

```bash
anyviking health
```

停止 OpenViking：

```powershell
.\scripts\stop_openviking.ps1
```

```bash
./scripts/stop_openviking.sh
```

### 配置 AnySearch

如果你有 AnySearch key：

```powershell
$env:ANYSEARCH_API_KEY = "your-key"
```

Linux / macOS：

```bash
export ANYSEARCH_API_KEY="your-key"
```

没有 key 时可以先试匿名请求，但稳定性和额度取决于 AnySearch 服务。

### 跑通主流程

只搜索公网：

```bash
anyviking search-web "OpenViking GitHub" --max-results 3
```

保存搜索结果到本地：

```bash
anyviking fetch-web "OpenViking GitHub" --max-results 3 --output data/web/openviking-github
```

保存并导入 OpenViking：

```bash
anyviking sync "OpenViking GitHub" --max-results 3 --output data/web/openviking-github --to viking://resources/openviking-github
```

查看资源树：

```bash
anyviking tree viking://resources/openviking-github -L 2
```

检索已导入资料：

```bash
anyviking search "What is OpenViking?" --scope viking://resources/openviking-github --top-k 3 --format text --documents-only
```

### Agent 怎么读取资料

`viking://resources/...` 是 OpenViking 的虚拟 URI，不是普通文件路径。

Agent 需要调用一个工具来读它，例如：

```bash
anyviking search "your question" --scope viking://resources/your-topic --format json --documents-only
```

也可以让 Agent 直接接 OpenViking API/CLI。VikingBot 不是必须的。

### 本地输出

这些都是本地运行产物，不应该提交：

```text
data/       AnySearch 结果和 markdown 文件
workspace/  OpenViking 本地数据库、索引、日志
reports/    本地生成输出，如果后续命令需要
```

这些也不会提交：

```text
config/ov.conf
config/ovcli.conf
.env
```

### 常见问题

#### `anyviking` 找不到

先确认虚拟环境已经激活。也可以直接运行：

```powershell
.\.venv\Scripts\anyviking.exe doctor
```

Linux / macOS：

```bash
.venv/bin/anyviking doctor
```

#### OpenViking 连接失败

先确认配置文件存在，再启动服务：

```bash
anyviking doctor
./scripts/start_openviking.sh
anyviking health
```

Windows 使用：

```powershell
.\scripts\start_openviking.ps1
anyviking health
```

#### AnySearch 请求失败

常见原因：

- 网络不可用。
- AnySearch 拒绝匿名请求。
- API key 没有设置。
- 请求参数过窄，导致没有结果。

先设置 `ANYSEARCH_API_KEY`，再用较小的 `--max-results` 测试。

#### 导入成功但搜不到

先看导入位置是否正确：

```bash
anyviking tree viking://resources/your-topic -L 2
```

再放大检索数量：

```bash
anyviking search "question" --scope viking://resources/your-topic --top-k 10 --format text --documents-only
```

更多排错见 [docs/troubleshooting.md](docs/troubleshooting.md)。

### 发布状态

当前推荐从源码安装。PyPI / TestPyPI 发布工作流已准备好，但实际发布需要仓库所有者在 PyPI 和 TestPyPI 配置 Trusted Publishing，或提供发布凭据。步骤见 [docs/publishing.md](docs/publishing.md)。

### 开发检查

```bash
python -m unittest discover -s tests
python -m compileall -q src tests
python -m build
python -m twine check dist/*
```

## English

AnyViking Research is a CLI bridge:

```text
AnySearch -> local markdown -> OpenViking -> viking:// retrieval
```

It saves public web results from AnySearch, writes them as local markdown, and imports them into OpenViking. Another Agent can then retrieve the indexed material through `anyviking search`, the OpenViking API/CLI, or a future MCP server.

It is not a search engine, not an OpenViking replacement, and not a full Agent product.

Upstream references:

- [AnySearch Skill](https://github.com/anysearch-ai/anysearch-skill)
- [AnySearch docs](https://www.anysearch.com/docs)
- [OpenViking](https://github.com/volcengine/OpenViking)
- [OpenViking docs](https://docs.openviking.ai/)

### Implemented

| Command | Purpose |
| --- | --- |
| `anyviking doctor` | Check local readiness |
| `anyviking health` | Check the OpenViking service |
| `anyviking status` | Show OpenViking status |
| `anyviking search-web` | Search public web sources through AnySearch |
| `anyviking fetch-web` | Save results as raw JSON, markdown, and a manifest |
| `anyviking sync` | Search, save, and import into OpenViking |
| `anyviking import-local` | Import existing local files |
| `anyviking tree` | Inspect a `viking://` resource tree |
| `anyviking search` | Search indexed OpenViking data |

Not implemented yet: Web UI, MCP server, Docker Compose, VikingBot wrapper, and automatic full report generation.

### Deployment Model

```text
1. AnySearch
   Remote web search. This project calls it but does not implement it.

2. OpenViking
   Local storage, indexing, and retrieval.

3. AnyViking Research
   This package. It saves web material, writes markdown, and imports it.
```

The install scripts set up this package and Python dependencies. They cannot create AnySearch credentials or model-provider credentials for you.

### Quick Install

Windows PowerShell:

```powershell
git clone https://github.com/liuchenyang111111/anyviking-research.git
cd anyviking-research
.\install.ps1
.\.venv\Scripts\anyviking.exe doctor
```

Linux / macOS:

```bash
git clone https://github.com/liuchenyang111111/anyviking-research.git
cd anyviking-research
./install.sh
source .venv/bin/activate
anyviking doctor
```

### Manual Install

Windows:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .[openviking] --no-build-isolation
```

Linux / macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e '.[openviking]' --no-build-isolation
```

### Configure

Copy OpenViking config templates, then edit `config/ov.conf` with your own model-provider settings:

```bash
cp config/ov.conf.example config/ov.conf
cp config/ovcli.conf.example config/ovcli.conf
```

Start OpenViking:

```bash
./scripts/start_openviking.sh
anyviking health
```

Optional AnySearch key:

```bash
export ANYSEARCH_API_KEY="your-key"
```

### Run

```bash
anyviking search-web "OpenViking GitHub" --max-results 3
anyviking fetch-web "OpenViking GitHub" --max-results 3 --output data/web/openviking-github
anyviking sync "OpenViking GitHub" --max-results 3 --output data/web/openviking-github --to viking://resources/openviking-github
anyviking search "What is OpenViking?" --scope viking://resources/openviking-github --top-k 3 --format text --documents-only
```

### Notes For Agents

`viking://` is a virtual OpenViking URI, not a normal file path. An Agent needs a tool such as `anyviking search`, OpenViking CLI/API, or a future MCP server to read it.

### Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md).

### Tests And Packaging

```bash
python -m unittest discover -s tests
python -m compileall -q src tests
python -m build
python -m twine check dist/*
```

Publishing to TestPyPI/PyPI is prepared through GitHub Actions, but it requires repository-owner Trusted Publishing setup. See [docs/publishing.md](docs/publishing.md).

## License

AnyViking Research uses the MIT License. OpenViking is a separate upstream dependency; follow OpenViking's license terms when using it.
