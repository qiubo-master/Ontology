# 汽车后市场智能客服 Ontology MVP

这是《汽车后市场智能客服 Ontology 产品需求与架构设计 V1.0》的可运行实现。项目覆盖客户聊天、人工审核、Ontology 配置和运营审计四个端，当前所有外部依赖均使用 Mock Adapter。

## 快速启动

```bash
python3 app.py
```

打开 <http://127.0.0.1:8000>。

运行测试：

```bash
python3 -m unittest discover -s tests -v
```

## 演示建议

- `我的宝马3系想换轮胎，推荐一下`：对象解析 + 商品推荐 + RAG 证据。
- `查一下订单 SO20260001`：订单对象查询。
- `取消预约 AP20260001`：生成 Action，用户确认后执行。
- `我要投诉门店态度很差`：高风险转人工审核。
- `理赔进度 CL20260001`：理赔对象和状态查询。

## 架构边界

- `ontology/catalog.py`：意图、能力、对象、规则和动作的可执行配置。
- `ontology/runtime.py`：统一运行状态与编排，不依赖具体模型或工具实现。
- `ontology/adapters.py`：模型、知识、工具、对象数据接口及 Mock 实现。
- `ontology/store.py`：会话、审核、审计和配置版本的内存仓库。
- `web/`：四端合一的演示工作台。

后续接真实系统时，优先替换 Adapter；对象与 Capability 契约保持不变。生产化还需接入持久化数据库、企业身份认证、密钥管理、消息队列、真实评估集和可观测平台。

## ForgeOps CI/CD 发布

项目已接入 `CSS-Deploy-Center` 的中央部署流水线，生产发布分支为 `master`。Ontology 仓库只负责无生产密钥的自动测试和容器构建规范；Tailscale、SSH、服务器激活、健康检查和版本回滚统一由 CI/CD 中台执行。

- 默认部署目录：`/opt/ontology-platform`
- 默认服务端口：`8090`
- 健康检查：`/api/health`
- 默认资源：2 CPU / 2GB 内存
- 版本策略：不可变版本目录，保留最近五个版本

Ontology 仓库不保存服务器、SSH 或 Tailscale Secret。部署凭据只在 `CSS-Deploy-Center` 的 GitHub `production` Environment 配置一次；新增标准项目时只需在中台登记仓库、分支、端口、健康检查和资源档位。

日常发布：代码合并并推送到 `master` 后，在 ForgeOps 中选择“汽车后市场 Ontology”，点击“发布最新版本”。回滚时点击“回滚上一版本”，业务数据不会被删除。
