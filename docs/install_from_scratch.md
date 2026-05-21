# 从零安装与复现指南

这份文档假设你刚拿到项目，还没有配置过当前项目环境。

## 1. 前置条件

推荐环境：

```text
Windows 11
PowerShell
VSCode
Python 3.12
OpenViking 0.3.17
```

确认 Python 3.12：

```powershell
py -0p
py -3.12 --version
```

## 2. 创建虚拟环境

```powershell
cd D:\Github\OpenViking_Search_Skill
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

如果 PowerShell 不允许激活脚本，执行一次：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

然后重新激活：

```powershell
.\.venv\Scripts\Activate.ps1
```

## 3. 安装依赖

```powershell
python -m pip install --upgrade pip setuptools wheel
python -m pip install openviking
python -m pip install -e . --no-deps --no-build-isolation
```

确认：

```powershell
python -m pip show openviking
openviking-server --version
ov-search-skill --help
```

目标：

```text
openviking 0.3.17
```

## 4. 准备配置

复制模板：

```powershell
Copy-Item config\ov.conf.example config\ov.conf
Copy-Item config\ovcli.conf.example config\ovcli.conf
```

编辑：

```text
config\ov.conf
```

把：

```text
YOUR_VOLCENGINE_API_KEY
```

替换成自己的火山引擎 API key。

模板默认使用相对路径：

```json
"storage": {
  "workspace": "workspace"
}
```

用本项目的 `scripts\start_openviking.ps1` 启动时，工作目录会固定到项目根目录，所以这个相对路径会落到当前项目的 `workspace\`。
如果你手动从别的目录启动 `openviking-server`，建议把这里改成你的项目绝对路径。

## 5. 启动服务

```powershell
.\scripts\start_openviking.ps1
```

检查：

```powershell
ov-search-skill health
ov-search-skill status
```

如果健康检查失败，先看 [FAQ](faq.md)。

## 6. 跑 smoke demo

```powershell
.\scripts\smoke_test.ps1 -Question "第二阶段重点做什么"
```

成功时应该看到：

```text
OpenViking health ok
导入 examples\smoke_corpus 成功
ov find 返回 viking://resources/smoke-corpus 结果
ov-search-skill search 返回 JSON 结果
```

## 7. 跑合成语料 demo

这是推荐优先运行的开源可复现 demo，因为语料已经在仓库里：

```powershell
.\examples\synthetic_ai_news\run_demo.ps1 -Question "为什么开源项目需要合成 demo 语料"
.\examples\synthetic_ai_news\run_research.ps1
```

成功时应该看到：

```text
导入 examples\synthetic_ai_news\source 成功
search 返回 viking://resources/synthetic-ai-news 结果
research 生成 reports\synthetic_ai_news_research_draft.md
```

## 8. 跑新闻 demo

新闻 demo 依赖旧项目本地语料路径：

```text
D:\Github\OpenViking_Run\workspace\news_raw\us-china-relations\2026-05-16
```

如果这个路径存在，运行：

```powershell
.\examples\news_us_china\run_demo.ps1 -Question "特朗普访华实际达成了哪些成果"
```

如果没有旧项目语料，可以先跳过新闻 demo。

## 9. 跑单元测试

```powershell
python -m unittest discover -s tests
python -m compileall src tests
```

这两个命令不需要 OpenViking 服务和 API key。

## 10. 停止服务

```powershell
.\scripts\stop_openviking.ps1
```
