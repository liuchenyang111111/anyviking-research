# OpenViking 环境搭建说明

本项目当前目标环境：

```text
Python 3.12
OpenViking 0.3.17
Windows + PowerShell + VSCode
```

## 1. 检查虚拟环境

在 VSCode 终端执行：

```powershell
cd D:\Github\OpenViking_Search_Skill
.\.venv\Scripts\Activate.ps1
python --version
python -m pip show openviking
openviking-server --version
ov --help
ov-search-skill --help
```

目标状态：

```text
Python 3.12.x
openviking 0.3.17
```

## 2. 理解 OpenViking 配置

OpenViking 默认会读取用户级配置，也就是 C 盘用户目录里的配置：

```text
C:\Users\ASUS\.openviking\ov.conf
C:\Users\ASUS\.openviking\ovcli.conf
```

可以把它理解成“这台电脑默认使用的 OpenViking 配置”。如果直接运行：

```powershell
openviking-server
```

OpenViking 通常会去读这个用户级配置。

本项目也可以使用项目内配置。项目内配置的好处是：这个项目用自己的 workspace，不会混到旧项目的数据目录里。

项目里已经准备了两个无密钥模板：

```text
config\ov.conf.example
config\ovcli.conf.example
```

真实配置文件不要提交到仓库。你可以从模板复制：

```powershell
Copy-Item config\ov.conf.example config\ov.conf
Copy-Item config\ovcli.conf.example config\ovcli.conf
```

然后把 `config\ov.conf` 里的 `YOUR_VOLCENGINE_API_KEY` 换成你自己的 key。真实文件已经被 `.gitignore` 忽略。

项目专用配置里建议使用这个 workspace：

```json
"storage": {
  "workspace": "D:/Github/OpenViking_Search_Skill/workspace"
}
```

## 3. 用指定配置启动服务

如果使用用户级配置：

```powershell
openviking-server
```

如果使用项目内配置：

```powershell
openviking-server --config config\ov.conf
```

项目也提供了一个启动脚本，会固定使用项目内配置：

```powershell
.\scripts\start_openviking.ps1
```

停止服务：

```powershell
.\scripts\stop_openviking.ps1
```

服务正常启动后会监听：

```text
http://127.0.0.1:1933
```

另开一个 VSCode 终端，检查服务：

```powershell
ov health
ov status
Invoke-RestMethod http://127.0.0.1:1933/health
```

## 4. 导入最小测试语料

先不要导入大仓库。先导入项目自带的小型 markdown 语料：

```powershell
ov-search-skill import-local examples\smoke_corpus --to viking://resources/smoke-corpus
```

查看导入结果：

```powershell
ov-search-skill status
ov-search-skill tree viking://resources/smoke-corpus -L 2
```

## 5. 测试语义检索

运行：

```powershell
ov find "第二阶段重点做什么" --uri viking://resources/smoke-corpus
```

目标是返回以 `viking://resources/smoke-corpus` 开头的结果。

## 6. 测试项目 CLI

项目 CLI 是对 OpenViking HTTP API 的一层薄包装，方便后面给 AI Agent 或脚本调用。

```powershell
ov-search-skill health
ov-search-skill search "第二阶段重点做什么" --scope viking://resources/smoke-corpus --top-k 3
ov-search-skill search "第二阶段重点做什么" --scope viking://resources/smoke-corpus --format text
ov-search-skill search "第二阶段重点做什么" --scope viking://resources/smoke-corpus --documents-only --format text
```

也可以一次跑完整烟测：

```powershell
.\scripts\smoke_test.ps1 -Question "第二阶段重点做什么"
```

## 7. 测试开源可复现 demo

环境和 smoke demo 通过后，可以运行合成语料 demo：

```powershell
.\examples\synthetic_ai_news\run_demo.ps1 -Question "为什么开源项目需要合成 demo 语料"
.\examples\synthetic_ai_news\run_research.ps1
```

这套语料在仓库内，不依赖旧项目路径，适合公开演示。

## 8. 当前阶段边界

当前核心链路：

```text
Python 3.12
-> openviking 0.3.17
-> OpenViking 配置
-> openviking-server
-> ov status
-> add-resource
-> ov find
-> 项目 CLI search
-> 项目 CLI research
```

这些暂时不做：

- VikingBot。
- LLM 自动写完整报告。
- AnySearch。
- Web UI。
- 大型 GitHub 仓库导入。
