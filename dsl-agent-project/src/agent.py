 # -*- coding: utf-8 -*-
"""
DSL Agent核心类
集成意图识别和DSL执行
"""

import os
import sys
from typing import Dict, List, Optional
from dsl_parser import DSLParser

from intent_recognizer import IntentRecognizer
from response_generator import ResponseGenerator

class DSLAgent:
    """DSL Agent核心类"""
    
    def __init__(self, dsl_file: str, api_key: Optional[str] = None):
        """
        初始化Agent
        
        Args:
            dsl_file: DSL脚本文件路径
            api_key: OpenAI API密钥
        """
        # 初始化组件
        self.dsl_parser = DSLParser(dsl_file)
        self.intent_recognizer = IntentRecognizer(api_key)
        self.response_generator = ResponseGenerator()
        # 从DSL加载意图
        self.available_intents = self.dsl_parser.get_intents()
        self.intent_names = [intent['name'] for intent in self.available_intents]
        
        # 对话历史
        self.conversation_history = []
    
    def process_message(self, user_input: str) -> List[str]:
        """ 处理用户消息 """
        # 1. 识别意图
        print(f"识别意图中...")
        intent = self.intent_recognizer.recognize_intent(
            user_input,
            context=self.dsl_parser.context,
            available_intents=self.intent_names
        )
        print(f"识别到意图: {intent}")

        # 2. 记录对话历史
        self.conversation_history.append({
            'user': user_input,
            'intent': intent
        })

        # 3. 执行DSL规则（可能返回 "__USE_LLM__" 标记）
        raw_responses = self.dsl_parser.process(intent, user_input)

        # 4. 替换 LLM 标记为真实生成内容
        final_responses = []
        for resp in raw_responses:
            if resp == "__USE_LLM__":
                llm_reply = self.response_generator.generate(
                    user_input=user_input,
                    intent=intent,
                    context=""  # TODO: 后续可传入历史上下文
                )
                final_responses.append(llm_reply)
            else:
                final_responses.append(resp)

        # 5. 记录最终响应
        self.conversation_history[-1]['responses'] = final_responses
        return final_responses
    
    def get_conversation_history(self) -> List[Dict]:
        """获取对话历史"""
        return self.conversation_history
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history.clear()
        self.dsl_parser.clear_context()
        