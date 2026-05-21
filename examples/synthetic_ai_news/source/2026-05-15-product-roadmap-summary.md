# 产品路线建议：先做可靠检索，再做自动报告

> 本文为 OpenViking Search Skill 项目 demo 使用的合成资料，不代表真实新闻报道。

## 摘要

一个面向 AI Agent 的本地检索项目，合理路线是先把可靠检索做好，再逐步增加调研草稿、自动报告、Bot 和外部搜索连接器。

## 阶段建议

第一阶段应该完成环境和基础命令：Python 虚拟环境、OpenViking 配置、最小语料导入、健康检查、单次搜索和 JSON 输出。这个阶段重点是“能稳定跑”。

第二阶段可以增加轻量 research workflow：把多个问题写进 YAML，逐个检索本地语料，输出带 URI 的 markdown 草稿。这个阶段重点是“能组织资料”，不是直接替用户下结论。

第三阶段适合补充可开源分发的 demo 语料。自写合成资料能让别人 clone 项目后完整复现，不依赖旧项目路径，也不涉及新闻版权。

第四阶段再评估 OpenVikingBot、MCP 或 AnySearch。Bot 适合对话式体验，AnySearch 适合公网资料发现，但它们都不应该抢在基础检索稳定之前。

## 风险提醒

过早接入复杂 Agent planner 会增加调试难度。更稳妥的做法是保持模块边界清晰：OpenViking 负责检索后端，本项目负责 CLI、Skill 文档、demo 和 workflow。

## 关键词

产品路线、阶段规划、research workflow、开源 demo、OpenVikingBot、AnySearch、MCP
