# -*- coding: utf-8 -*-
"""
意图识别模块
使用通义千问API识别用户输入的意图
"""

import os
from typing import List, Dict, Optional
import dashscope # type: ignore
from dashscope import Generation # type: ignore
from dotenv import load_dotenv

class IntentRecognizer:
    """基于通义千问的意图识别器"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化意图识别器
        
        Args:
            api_key: 通义千问API密钥，如果为None则从环境变量读取
        """
        # 加载环境变量
        load_dotenv()
        
        # 设置API密钥
        self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY')
        if not self.api_key:
            raise ValueError("通义千问API密钥未设置。请在.env文件中设置DASHSCOPE_API_KEY")
        
        # 设置通义千问API密钥
        dashscope.api_key = self.api_key
        
        # 模型配置
        self.model = os.getenv('DASHSCOPE_MODEL', 'qwen-turbo')
        
        # 意图类别
        self.intent_categories = [
            "greeting","welcome",  # 问候
            "product_query",  # 产品查询
            "buy_product",
            "order_query",
            "order_number",
            "order_status",  # 订单状态
            "refund",  # 退款退货
            "complaint",  # 投诉
            "technical_support",  # 技术支持
            "payment_issue",  # 支付问题
            "cancel_order", "cancel_order_number",
            "after_sales", "hardware_issue", "software_issue", 
            "other"  # 其他
        ]
    
    def extract_intents_from_dsl(self, dsl_file: str) -> List[str]:
        """
        从DSL脚本中提取意图类别
        
        Args:
            dsl_file: DSL脚本文件路径
            
        Returns:
            意图类别列表
        """
        import yaml
        try:
            with open(dsl_file, 'r', encoding='utf-8') as f:
                dsl_data = yaml.safe_load(f)
            
            intents = []
            for intent_def in dsl_data.get('intents', []):
                intents.append(intent_def.get('name'))
            
            return intents
        except Exception as e:
            print(f"从DSL提取意图失败: {e}")
            return self.intent_categories
    
    def recognize_intent(self, user_input: str, context: Dict = None, 
                        available_intents: List[str] = None) -> str:
        """
        识别用户输入的意图
        
        Args:
            user_input: 用户输入文本
            context: 对话上下文
            available_intents: 可用的意图列表
            
        Returns:
            识别到的意图名称
        """
        if available_intents is None:
            available_intents = self.intent_categories
        
        # 构建提示词
        prompt = self._build_prompt(user_input, available_intents, context)
        
        try:
            response = Generation.call(
                model=self.model,
                prompt=prompt,
                temperature=0.3,
                max_tokens=50
            )
            
            if response.status_code == 200:
                intent = response.output.text.strip().lower()
            else:
                print(f"API调用失败: {response.code} - {response.message}")
                # 回退到基于关键词的简单识别
                return self._fallback_intent_recognition(user_input, available_intents)
            
            # 验证意图是否在可用列表中
            if intent in available_intents:
                return intent
            else:
                # 如果不在列表中，查找最相似的意图
                return self._find_closest_intent(intent, available_intents)
                
        except Exception as e:
            print(f"意图识别失败: {e}")
            # 回退到基于关键词的简单识别
            return self._fallback_intent_recognition(user_input, available_intents)
    
# 修改前（缺少订单号规则）：
# "- 如果用户提到订单、物流、快递、发货、送到哪，返回 'order_query'"

    # 修改后（添加关键规则）：
    def _build_prompt(self, user_input: str, available_intents: List[str], context: Dict = None) -> str:
        intents_str = ', '.join(available_intents)
        prompt = (
            f"你是一个电商客服意图分类器。请根据用户的输入，严格从以下选项中选择一个最匹配的意图：\n"
            f"{intents_str}\n\n"
            f"用户输入：\"{user_input}\"\n\n"
            f"要求：\n"
            f"- 如果用户输入是数字、无意义字符、乱码或无法理解的内容，请返回 'other'\n"
            f"- 如果用户输入是问候语（如“你好”、“嗨”、“在吗”），返回 'welcome'\n"
            f"- 如果用户询问产品、商品、推荐、有什么可买，或提到具体商品名称（如“手机”、“小米”、“电脑”、“耳机”），返回 'product_query'\n"
            f"- 如果用户提到订单、物流、快递、发货、送到哪，返回 'order_query'\n"
            f"- 如果用户说“退货”、“退款”、“退钱”、“不要了”、“质量差”，返回 'cancel_order'\n"
            f"- 如果用户输入是4位数字（如'1234'），返回 'order_number'  # ✅ 新增关键规则\n"
            f"- 如果用户输入是4位数字后跟退款原因（如'1234退款原因'、'1234 退款原因'、'1234产品有瑕疵'、'1234操作失误'），返回 'cancel_order_number'  \n"
            f"- 如果用户提到售后、保修、退换货、换电池，返回 'after_sales'\n"
            f"- 如果用户提到开机异常、开不了机、无法开机、音量键失效、音量键坏了、屏幕碎掉、屏幕破裂、黑屏、屏幕不亮、手机进水、进水了、无法唤出小爱同学、小爱同学没反应，返回 'hardware_issue'\n"
            f"- 如果用户提到系统卡顿、手机卡死、应用闪退、软件崩溃、系统更新失败、无法连接WiFi、蓝牙连不上、相机打不开、指纹识别失灵，返回 'software_issue'\n"
            f"- 如果用户输入包含4位数字且包含'退款'、'退货'、'瑕疵'、'质量'等退款相关词汇，返回 'cancel_order_number'（优先级高于product_query）"  
            # 产品查询规则调整：
            f"- 如果用户询问产品、商品、推荐、有什么可买，或提到具体商品名称（如'手机'、'小米'、'电脑'、'耳机'），且不包含4位数字和退款词汇，返回 'product_query'"
            f"- 必须只输出意图名称，不要任何其他文字、标点或解释。\n\n"
            f"意图："
        )
        return prompt
    def _find_closest_intent(self, intent: str, available_intents: List[str]) -> str:
        """查找最相似的意图"""
        # 简单实现：检查是否包含关键词
        intent_lower = intent.lower()
        
        for available in available_intents:
            if available in intent_lower or intent_lower in available:
                return available
        
        # 如果找不到匹配的，返回"other"
        return "other"
    
    def _fallback_intent_recognition(self, user_input: str, 
                                   available_intents: List[str]) -> str:
        """回退的意图识别方法（基于关键词）"""
        user_input_lower = user_input.lower()
        # 新增：处理数字订单号
        if "order_number" in available_intents:
            if user_input.isdigit() and len(user_input) == 4:
                return "order_number"
        
        # 增强：处理带原因的退货（更灵活的模式匹配）
        if "cancel_order_number" in available_intents:
            # 匹配4位数字+任何中文字符
            import re
            # 匹配4位数字开头，后面跟着中文字符的模式
            if re.match(r'^\d{4}[\u4e00-\u9fa5]+', user_input):
                # 进一步检查是否包含退款相关词汇
                refund_keywords = ["退款", "退货", "瑕疵", "不要", "质量", "差", "坏", "问题"]
                if any(kw in user_input for kw in refund_keywords):
                    return "cancel_order_number"
                
        # 关键词映射
        keyword_mapping = {
        "greeting": ["你好", "hello", "hi", "您好", "在吗"],
        "product_query": [
            "产品", "商品", "买什么", "推荐", "有什么",
            # ✅ 新增具体产品关键词
            "小米", "手机", "电脑", "耳机", "平板", "手表"
        ],
        "order_status": ["订单", "发货", "物流", "快递", "送到哪"],
        "refund": ["退款", "退货", "退钱", "不满意", "质量"],
        "complaint": ["投诉", "举报", "差评", "生气", "愤怒"],
        "technical_support": ["登录", "密码", "账号", "用不了", "bug"],
        "payment_issue": ["支付", "付款", "扣款", "交易", "钱"],
        "after_sales": ["售后", "保修", "退换货", "换电池"],
        "hardware_issue": [
            "开机异常", "开不了机", "无法开机", "音量键", "屏幕碎", "屏幕破", 
            "黑屏", "屏幕不亮", "进水", "小爱同学", "唤不出"
        ],
        "software_issue": [
            "系统卡顿", "手机卡死", "应用闪退", "软件崩溃", "系统更新", 
            "WiFi", "蓝牙", "相机", "指纹识别"
        ]
    }
        
        for intent, keywords in keyword_mapping.items():
            if intent in available_intents:
                for keyword in keywords:
                    if keyword in user_input_lower:
                        return intent
        
        return "other"