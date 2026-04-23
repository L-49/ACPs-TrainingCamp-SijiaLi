# DSL Agent项目：基于领域特定语言的多业务场景Agent

## 项目概述
本项目实现了一个基于**领域特定语言（DSL）** 的智能客服Agent，通过**大语言模型（LLM）意图识别**驱动DSL脚本执行，支持电商和技术支持两大业务场景。系统能准确处理：
- 产品查询（如"小米17怎么样？"）
- 订单管理（4位订单号查询/取消）
- 售后服务（退换货政策）
- 技术问题（登录/支付故障）

## 核心技术栈
- **DSL设计**：YAML格式规则脚本（`scripts/*.yaml`）
- **意图识别**：DashScope Qwen API（通义千问）
- **动态回复**：LLM生成产品信息（基于`products.json`知识库）
- **多场景支持**：电商 + 技术支持双DSL脚本

## 项目结构
dsl-agent-project/
├── src/                  # 核心代码
│   ├── dsl_parser.py     # DSL解析器（支持actions字段）
│   ├── intent_recognizer.py # LLM意图识别器
│   ├── response_generator.py # LLM动态回复生成
│   └── main.py           # 主入口
├── scripts/              # DSL脚本范例
│   ├── ecommerce.dsl.yaml  # 电商客服规则
│   └── tech_support.dsl.yaml # 技术支持规则
├── products.json         # 产品知识库（小米14/15/17系列）
├── docs/
│   └── development_log.md # 完整开发日志（6天记录）
├── design_notes.md       # LLM辅助开发过程记录
└── README.md             # 本文件

## DSL语法示例
### 电商场景（`ecommerce.dsl.yaml`）
```yaml
rules:
  - when: order_number      # 意图名称
    patterns: ["1234"]      # 匹配模式
    actions:                # 执行动作
      - action: respond
        content: "您的订单已发货，预计明天送达。"
      - action: set_context
        key: order_status
        value: shipped