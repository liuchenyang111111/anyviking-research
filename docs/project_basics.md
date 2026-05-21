# 项目基础概念说明

这份文档给第一次从“单文件脚本”过渡到“小型 Python 项目”的同学看。

## 1. 什么是最小包

你以前写单文件代码时，可能是这样：

```text
main.py
```

所有代码都放在一个文件里。这个方式适合小练习，但项目稍微变大后会遇到几个问题：

- 代码越来越长，不好找。
- 检索、配置、命令行、报告生成混在一起。
- 别的脚本很难复用里面的一部分功能。

所以 Python 项目通常会拆成“包”。本项目的包是：

```text
src/ov_search_skill/
```

可以把它理解成一个小工具箱。工具箱里目前有：

```text
src/ov_search_skill/
  __init__.py
  cli.py
  retrievers/
    base.py
    openviking.py
```

其中：

- `__init__.py`：告诉 Python 这里是一个包，也负责暴露常用对象。
- `cli.py`：命令行入口。
- `retrievers/base.py`：定义“检索结果长什么样”。
- `retrievers/openviking.py`：真正调用 OpenViking HTTP API 做检索。

有了包之后，别的代码就可以这样复用：

```python
from ov_search_skill import OpenVikingRetriever

retriever = OpenVikingRetriever()
results = retriever.search("第二阶段重点做什么")
```

这就是“最小包”的作用：先把项目最核心、最可复用的能力整理出来。

## 2. 什么是 CLI

CLI 是 command line interface 的缩写，意思是“命令行接口”。

简单说，就是让你可以在终端里调用项目功能。

比如本项目支持：

```powershell
python -m ov_search_skill.cli health
python -m ov_search_skill.cli search "第二阶段重点做什么" --scope viking://resources/smoke-corpus --top-k 3
```

这比每次都写 Python 代码更方便。

CLI 的价值是：

- 人可以直接在终端测试。
- 脚本可以调用。
- 以后 AI Agent 也可以把它当作一个工具来用。

## 3. 什么是 pyproject.toml

`pyproject.toml` 是 Python 项目的配置文件。

它告诉 Python 和 pip：

- 项目叫什么。
- 需要什么 Python 版本。
- 依赖哪些第三方库。
- 哪个函数可以作为命令行入口。

本项目里这段：

```toml
[project.scripts]
ov-search-skill = "ov_search_skill.cli:main"
```

意思是：以后如果把项目安装成可编辑包，就可以直接运行：

```powershell
ov-search-skill search "第二阶段重点做什么"
```

当前阶段先用：

```powershell
python -m ov_search_skill.cli search "第二阶段重点做什么"
```

项目完成可编辑安装后，也可以直接用：

```powershell
ov-search-skill search "第二阶段重点做什么"
```

这就是为什么前面要“安装成可编辑包”：不是为了发布到网上，而是为了开发时能像使用正式工具一样使用当前项目。

## 4. 什么是 .gitignore

`.gitignore` 是给 Git 用的忽略清单。

它的作用是告诉 Git：哪些文件不要提交到仓库。

本项目里需要忽略这些东西：

- `.venv/`：虚拟环境，里面是安装的第三方库，文件很多，不应该提交。
- `__pycache__/`：Python 自动生成的缓存文件，不需要提交。
- `.env`：可能放密钥，不应该提交。
- `workspace/`：OpenViking 的本地数据目录，可能很大，也可能包含本地资料。
- `config/ov.conf`：真实配置，里面有 API key，不能提交。
- `config/ovcli.conf`：本机 CLI 配置，不需要提交。

但模板文件可以提交：

```text
config/ov.conf.example
config/ovcli.conf.example
```

模板文件不放真实密钥，只告诉别人应该怎么配置。

## 5. 用户级配置和项目配置

OpenViking 默认会读 C 盘用户目录里的配置：

```text
C:\Users\ASUS\.openviking\ov.conf
```

这叫用户级配置，可以理解成“这台电脑默认的 OpenViking 配置”。

本项目也可以有自己的配置：

```text
D:\Github\OpenViking_Search_Skill\config\ov.conf
```

启动时指定它：

```powershell
openviking-server --config config\ov.conf
```

这样好处是当前项目的数据会进入当前项目的 workspace，不会混到旧项目目录里。

## 6. 当前项目为什么要这样拆

这个项目不是为了炫技拆目录，而是为了后面自然长大：

```text
现在：
  本地 markdown -> OpenViking -> search CLI

以后：
  本地文档 -> OpenViking -> 检索接口 -> 报告 workflow / AI Agent Skill
```

所以现在先建立一个很小但清楚的结构，后面再加新闻调研、报告生成、AnySearch 或 VikingBot 时，就不用把所有东西塞回一个大脚本里。
