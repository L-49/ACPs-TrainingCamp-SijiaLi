# -*- coding: utf-8 -*-
"""DSL解析器模块用于解析和执行DSL脚本"""
import yaml
from typing import Dict, List, Any

class DSLParser:
    """DSL脚本解析器"""
    
    def __init__(self, dsl_file: str):
        """ 初始化解析器
        Args:
            dsl_file: DSL脚本文件路径
        """
        self.dsl_file = dsl_file
        self.script = self.load_script()
        self.context = {}  # 对话上下文

    def load_script(self) -> Dict:
        """加载和解析DSL脚本"""
        try:
            with open(self.dsl_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"加载DSL脚本失败: {e}")
            return {}

    def get_intents(self) -> List[Dict]:
        """获取所有定义的意图（关键修复）"""
        rules = self.get_rules()
        intents = []
        for rule in rules:
            when = rule.get('when')
            patterns = rule.get('patterns', [])
            if when:
                intents.append({
                    'name': when,
                    'patterns': patterns
                })
        return intents

    def get_rules(self) -> List[Dict]:
        """获取所有规则"""
        return self.script.get('rules', [])

    def find_matching_rule(self, intent: str, user_input: str = "") -> Dict:
        """ 根据意图查找匹配的规则
        Args:
            intent: 用户意图
            user_input: 用户原始输入（可选）
        Returns:
            匹配的规则，如果没有匹配则返回None
        """
        for rule in self.get_rules():
            if rule.get('when') == intent:
                # 检查条件（简化版，明天会完善）
                conditions = rule.get('conditions', [])
                if self.check_conditions(conditions):
                    return rule
        return None

    def check_conditions(self, conditions: List[str]) -> bool:
        """ 检查规则条件是否满足
        Args:
            conditions: 条件列表，格式如 ["has_order_number", "user_tier:vip"]
        Returns:
            是否满足所有条件
        """
        if not conditions:
            return True
        for condition in conditions:
            if not self._evaluate_condition(condition):
                return False
        return True

    def _evaluate_condition(self, condition: str) -> bool:
        """ 评估单个条件
        Args:
            condition: 条件字符串
        Returns:
            条件是否满足
        """
        # 解析条件
        if ':' in condition:
            key, expected_value = condition.split(':', 1)
            actual_value = self.context.get(key)
            return str(actual_value) == str(expected_value)
        else:
            # 布尔条件，检查上下文是否存在该键且为True
            return bool(self.context.get(condition, False))

    def update_context(self, key: str, value: Any):
        """更新对话上下文"""
        self.context[key] = value

    def clear_context(self):
        """清空对话上下文"""
        self.context.clear()

    def execute_actions(self, actions: List[Dict], user_input: str = "") -> List[str]:
        """ 执行动作列表
        Args:
            actions: 动作列表
        Returns:
            执行结果的响应列表
        """
        print(f"[DEBUG] user_input received: '{user_input}'")
        print(f"[DEBUG] 接收到的动作列表: {actions}")
        responses = []
        for action in actions:
            action_type = action.get('action')
            if action_type == 'respond':
                content = action.get('content', '')
                content = content.replace("{{input}}", user_input)
                responses.append(content)
            elif action_type == 'suggest':
                options = action.get('options', [])
                if options:
                    suggestions = "您可以考虑：" + "、".join(options)
                    responses.append(suggestions)
            elif action_type == 'escalate':
                target = action.get('to', '人工客服')
                responses.append(f"正在为您转接{target}...")
            elif action_type == 'set_context':
                key = action.get('key')
                value = action.get('value')
                if key:
                    self.context[key] = value
            elif action_type == 'call_tool':
                responses.append("__USE_LLM__")
            elif action_type == 'respond_with_llm':
                responses.append("__USE_LLM__") 
                # 注意：dsl_parser 不应直接依赖 LLM！
                # 所以我们返回一个特殊标记，由 Agent 层处理
        return responses

    def process(self, intent: str, user_input: str = "") -> List[str]:
        """ 处理用户输入
        Args:
            intent: 识别到的意图
            user_input: 用户原始输入
        Returns:
            响应列表
        """
        rule = self.find_matching_rule(intent, user_input)
        if rule:
            actions = rule.get('actions', [])
            return self.execute_actions(actions, user_input)
        else:
            return ["抱歉，我还没有学会处理这个问题。请换种方式问我，或者联系人工客服。"]