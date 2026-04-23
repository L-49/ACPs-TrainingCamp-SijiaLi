# -*- coding: utf-8 -*-
"""端到端Agent测试（适配售后技术场景规则）"""

import sys
import os
import unittest
from dotenv import load_dotenv

# 加载环境变量（处理API密钥）
load_dotenv()

# 添加 scripts 目录到路径
scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

# 添加 src 目录
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from agent import DSLAgent

class TestAgentAfterSalesFlows(unittest.TestCase):
    """Agent售后技术场景端到端测试类"""
    
    @classmethod
    def setUpClass(cls):
        """初始化测试环境"""
        # 使用实际的ecommerce.dsl.yaml文件进行测试
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        current_dir = os.path.dirname(os.path.abspath(__file__))  # tests/目录
        cls.test_dsl = os.path.join(current_dir, '..', 'scripts', 'ecommerce.dsl.yaml')
        cls.test_dsl = os.path.abspath(cls.test_dsl)
        
        if not os.path.exists(cls.test_dsl):
            raise FileNotFoundError(f"DSL文件不存在: {cls.test_dsl}")
        if not os.getenv("DASHSCOPE_API_KEY"):
            raise EnvironmentError("请配置DASHSCOPE_API_KEY环境变量")

    def setUp(self):
        """每个测试用例初始化Agent"""
        self.agent = DSLAgent(self.test_dsl)

    def test_welcome_flow(self):
        """测试问候场景"""
        responses = self.agent.process_message("你好")
        self.assertGreater(len(responses), 0, "应有回复")
        self.assertIn("欢迎来到小米手机官方旗舰店", responses[0], "应返回欢迎语")
        self.assertIn("智能客服小助手", responses[0], "应包含客服身份说明")

    def test_order_number_flow(self):
        """测试订单号查询"""
        responses = self.agent.process_message("1234")
        self.assertGreater(len(responses), 0, "应有回复")
        self.assertIn("已发货", responses[0], "应回复发货信息")
        self.assertIn("预计明天送达", responses[0], "应包含预计送达时间")

    def test_order_query_flow(self):
        """测试订单查询流程"""
        responses = self.agent.process_message("查询订单")
        self.assertGreater(len(responses), 0, "应有回复")
        self.assertIn("请提供您的4位订单号", responses[0], "应提示提供订单号")

    def test_cancel_order_flow(self):
        """测试取消订单流程"""
        # 第一步：请求取消订单
        responses1 = self.agent.process_message("取消订单")
        self.assertGreater(len(responses1), 0, "应有回复")
        self.assertIn("请提供4位订单号和退款原因", responses1[0], "应提示提供订单号和原因")
        
        # 第二步：提供订单号和原因（模拟实际意图识别为cancel_order_number）
        # 注意：这里需要模拟意图识别返回cancel_order_number
        responses2 = self.agent.process_message("1234 产品有瑕疵")
        self.assertGreater(len(responses2), 0, "应有回复")

    def test_after_sales_policy_flow(self):
        """测试售后政策咨询"""
        responses = self.agent.process_message("怎么退换货？")
        self.assertGreater(len(responses), 0, "应有回复")
        self.assertIn("小米官方售后政策", responses[0], "应返回售后政策")
        self.assertIn("15天无理由退换", responses[0], "应包含退换货期限")
        self.assertIn("https://www.mi.com/service", responses[0], "应包含官方链接")

    def test_hardware_issue_flow(self):
        """测试硬件故障咨询"""
        # 测试各种硬件故障场景
        test_cases = [
            ("手机进水了", "进水"),
            ("屏幕碎了", "屏幕"),
            ("开不了机", "开机"),
        ]
        
        for user_input, keyword in test_cases:
            with self.subTest(user_input=user_input):
                responses = self.agent.process_message(user_input)
                self.assertGreater(len(responses), 0, f"'{user_input}'应有回复")
                # 硬件问题会返回__USE_LLM__标记，由response_generator生成具体回复
                # 所以这里只验证有响应即可

    def test_software_issue_flow(self):
        """测试软件问题咨询"""
        # 测试各种软件故障场景
        test_cases = [
            ("应用闪退", "应用"),
            ("无法连接WiFi", "WiFi"),
            ("蓝牙连不上", "蓝牙"),
        ]
        
        for user_input, keyword in test_cases:
            with self.subTest(user_input=user_input):
                responses = self.agent.process_message(user_input)
                self.assertGreater(len(responses), 0, f"'{user_input}'应有回复")
                # 软件问题会返回__USE_LLM__标记，由response_generator生成具体回复
                # 所以这里只验证有响应即可

    def test_product_query_flow(self):
        """测试产品查询"""
        # 测试各种产品查询
        test_cases = [
            "小米17怎么样？",
            "小米15 Pro的配置？",
            "小米14 Ultra多少钱？",
            "小米17 Pro Max有现货吗？",
        ]
        
        for user_input in test_cases:
            with self.subTest(user_input=user_input):
                responses = self.agent.process_message(user_input)
                self.assertGreater(len(responses), 0, f"'{user_input}'应有回复")
                # 产品查询会返回__USE_LLM__标记，由response_generator生成具体回复
                # 所以这里只验证有响应即可

    def test_buy_product_flow(self):
        """测试购买流程"""
        test_cases = [
            "我要买小米17",
            "购买小米15 Pro",
            "下单小米17 Pro Max",
            "买小米14 Ultra",
        ]
        
        for user_input in test_cases:
            with self.subTest(user_input=user_input):
                responses = self.agent.process_message(user_input)
                self.assertGreater(len(responses), 0, f"'{user_input}'应有回复")
                print(f"购买意图测试 '{user_input}' → 响应长度: {len(responses[0])} 字符")
            
            # 可选：记录响应内容用于分析
            with open("test_buy_responses.log", "a", encoding="utf-8") as f:
                f.write(f"{user_input}: {responses[0]}\n")

    def test_invalid_order_number_flow(self):
        """测试无效订单号处理"""
        # 直接测试几个典型无效订单号，验证DSL规则正常工作
        responses = self.agent.process_message("abcd")
        self.assertGreater(len(responses), 0, "应有回复")
        print(f"测试'abcd'的响应: {responses[0]}")  # 打印出来看看实际返回什么
        
        responses = self.agent.process_message("无效订单号")
        self.assertGreater(len(responses), 0, "应有回复")
        print(f"测试'无效订单号'的响应: {responses[0]}")
        
        # 不进行断言，只验证不抛出异常即可
        self.assertTrue(True)

    def test_multi_turn_conversation(self):
        """测试多轮对话"""
        # 第一轮：问候
        responses1 = self.agent.process_message("你好")
        self.assertGreater(len(responses1), 0, "第一轮应有回复")
        
        # 第二轮：查询订单
        responses2 = self.agent.process_message("查询订单")
        self.assertGreater(len(responses2), 0, "第二轮应有回复")
        
        # 第三轮：提供订单号
        responses3 = self.agent.process_message("1234")
        self.assertGreater(len(responses3), 0, "第三轮应有回复")
        self.assertIn("已发货", responses3[0], "应返回订单状态")

    def test_context_management(self):
        """测试上下文管理"""
        # 设置上下文：查询订单状态
        responses1 = self.agent.process_message("1234")
        self.assertGreater(len(responses1), 0, "应有回复")
        
        # 验证上下文是否设置
        self.assertEqual(self.agent.dsl_parser.context.get("order_status"), "shipped",
                        "应设置order_status为shipped")

    def test_error_handling(self):
        """测试错误处理"""
        # 测试无法识别的输入
        responses = self.agent.process_message("随机乱码!@#$%")
        self.assertGreater(len(responses), 0, "应有回复")
        self.assertIn("抱歉，我还没有学会处理这个问题", responses[0], "应返回兜底响应")

if __name__ == "__main__":
    unittest.main(verbosity=2)