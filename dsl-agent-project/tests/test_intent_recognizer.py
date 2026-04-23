# -*- coding: utf-8 -*-
"""测试意图识别的回退机制"""

import sys
import os

# 添加 src 目录到 Python 路径
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from intent_recognizer import IntentRecognizer

def test_order_number_recognition():
    """测试纯数字订单号识别"""
    recognizer = IntentRecognizer(api_key="fake_key")
    
    # 直接调用回退机制（绕过API调用）
    intents_list = ["order_number", "cancel_order_number", "product_query"]
    result = recognizer._fallback_intent_recognition("1234", intents_list)
    assert result == "order_number", f"期望 order_number，实际得到 {result}"

def test_cancel_order_with_reason():
    """测试带原因的退货请求（无空格输入）"""
    recognizer = IntentRecognizer(api_key="fake_key")
    
    intents_list = ["order_number", "cancel_order_number", "product_query"]
    result = recognizer._fallback_intent_recognition("1245产品瑕疵", intents_list)
    assert result == "cancel_order_number", f"期望 cancel_order_number，实际得到 {result}"

def test_product_query_chinese_numbers():
    """测试中文数字产品查询"""
    recognizer = IntentRecognizer(api_key="fake_key")
    
    intents_list = ["order_number", "cancel_order_number", "product_query"]
    result = recognizer._fallback_intent_recognition("小米十七", intents_list)
    assert result == "product_query", f"期望 product_query，实际得到 {result}"

if __name__ == "__main__":
    test_order_number_recognition()
    test_cancel_order_with_reason()
    test_product_query_chinese_numbers()
    print("✅ 意图识别测试通过！")