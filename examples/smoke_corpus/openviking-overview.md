# OpenViking 最小测试语料

OpenViking 在这个项目里作为本地语义检索服务使用。这个测试语料故意做得很小，用来在导入大型仓库或新闻资料之前，先验证环境是否能跑通。

预期流程是：启动 `openviking-server`，把这个文件夹导入为 OpenViking 资源，然后针对生成的 `viking://` 资源路径进行自然语言检索。
