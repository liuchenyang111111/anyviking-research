# 开源检查清单

这个清单用于把项目整理成可以发布到 GitHub 的 v0.1。

## 必须完成

- [x] 使用 Python 虚拟环境。
- [x] 提供 `.gitignore`。
- [x] 提供 MIT `LICENSE`。
- [x] 不提交 `.venv/`。
- [x] 不提交 `workspace/`。
- [x] 不提交真实 `config/ov.conf`。
- [x] 提供无密钥配置模板。
- [x] README 说明项目定位。
- [x] 提供最小 smoke corpus。
- [x] 提供可开源分发的合成 demo 语料。
- [x] 提供旧项目新闻 demo 说明。
- [x] 提供启动、停止、烟测脚本。
- [x] 提供 `SKILL.md`。
- [x] 提供架构说明。
- [x] 提供运行记录。
- [x] 提供从零安装与复现指南。
- [x] 提供 FAQ。
- [x] 提供项目阶段汇报。
- [x] README 按开源首页结构整理。

## 发布前需要确认

- [x] 是否初始化 git 仓库。
- [x] 是否选择并确认开源许可证。
- [ ] 是否需要把项目名改成更正式的英文名。
- [x] 是否需要补截图或命令输出示例。
- [x] 是否需要添加自动化测试。
- [x] 是否需要写一份给学长看的项目汇报。

## 敏感信息检查

发布前检查这些文件不要包含 API key：

```text
README.md
PROJECT_CONTEXT.md
SKILL.md
docs/
examples/
scripts/
config/*.example
```

不要提交这些文件：

```text
config/ov.conf
config/ovcli.conf
workspace/
.venv/
```

## 版权注意

新闻 demo 当前不把新闻全文复制进仓库，只记录旧项目本地语料路径、查询问题和运行记录。

公开演示优先使用：

```text
examples/synthetic_ai_news
```

这套语料为项目自写合成资料，可以提交到仓库。旧新闻 demo 继续作为本机真实语料验证，不复制新闻全文。
