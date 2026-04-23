# src/response_generator.py
import os
import json
import re
from dashscope import Generation

class ResponseGenerator:
    def __init__(self):
        # 读取 API Key
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("请设置 DASHSCOPE_API_KEY 环境变量")
        # 加载产品知识库
        self.products = self._load_products()

    def _load_products(self):
        """从 products.json 加载产品信息"""
        try:
            with open("products.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return {p["name"]: p for p in data["products"]}
        except Exception as e:
            print(f"⚠️ 无法加载 products.json: {e}")
            return {}

    def _chinese_to_arabic(self, text: str) -> str:
        """将“小米十七”转为“小米17”"""
        # 特殊映射：只处理常见型号
        mapping = {
            "十四": "14",
            "十五": "15",
            "十六": "16",
            "十七": "17",
            "十三": "13",
            "十二": "12",
            "十一": "11"
        }
        if "小米" in text:
            match = re.search(r"小米(.+)", text)
            if match:
                num_str = match.group(1).strip()
                if num_str in mapping:
                    return f"小米{mapping[num_str]}"
        return text

    def _extract_product_name(self, text: str) -> str:
        """从用户输入中提取手机型号，如 '小米17'"""
        # 先尝试匹配阿拉伯数字（小米17）
        match = re.search(r"(小米\d+)", text)
        if match:
            return match.group(1)
        # 再尝试匹配中文数字（小米十七）
        normalized = self._chinese_to_arabic(text)
        match2 = re.search(r"(小米\d+)", normalized)
        return match2.group(1) if match2 else ""

    def generate(self, user_input: str, intent: str, context: str = "") -> str:
        # 关键：先标准化输入
        product_name = self._extract_product_name(user_input)

        fact_snippet = ""
        if product_name in self.products:
            prod = self.products[product_name]
            fact_snippet = f"""已知事实（必须遵守）：
- {prod['name']} 已于 {prod['release_date']} 发布，状态：{prod['status']}
- 特点：{prod['description']}"""
        else:
            fact_snippet = """注意：如果用户提到的产品不在上述列表中（如小米18），请回答“尚未发布，预计明年上市”。"""

        # 根据不同的上下文类型构建不同的prompt
        if context and "hardware_support" in context:
            prompt = f"""你是一个专业的小米售后客服，正在处理用户的硬件故障问题。
        用户描述的问题：{user_input}
        请提供专业的硬件故障处理建议，包含：
        1. 安全提醒（立即停止使用设备）
        2. 处理建议（前往就近的小米授权服务中心）
        3. 必需携带的材料（购买凭证和保修卡）
        4. 官方服务链接：https://www.mi.com/service
        要求：语气关怀但专业，每次回复的表述要有所不同，但核心信息必须完整。请生成一句中文回复（不要解释，不要 markdown）："""

        elif context and "software_support" in context:
            prompt = f"""你是一个专业的小米技术支持客服，正在处理用户的软件问题。
        用户遇到的问题：{user_input}
        请提供专业的软件故障排除步骤，包含：
        1. 基础解决步骤（重启手机、清除相关应用缓存、检查系统更新）
        2. 进阶解决方案（备份重要数据后恢复出厂设置）
        3. 官方帮助链接：https://www.mi.com/service/support
        4. 进一步支持选项
        要求：语气友好且实用，每次回复的表述要有所不同，但解决方案必须准确。请生成一句中文回复（不要解释，不要 markdown）："""

        else:
            # 原有的产品查询逻辑
            prompt = f"""你是一个专业的小米电商客服，语气友好、简洁。
        {fact_snippet}
        规则：
        - 只基于上述事实回答，绝不编造不存在的信息。
        - 如果用户问的是已发布产品，请介绍其特点。
        - 如果不确定，就说"建议访问小米官网查询"。
        用户输入：{user_input}
        意图：{intent}
        请生成一句中文回复（不要解释，不要 markdown）："""
        try:
            response = Generation.call(
                model="qwen-max",
                api_key=self.api_key,
                prompt=prompt.strip(),
                result_format="message"
            )
            if response.status_code == 200:
                return response.output.choices[0].message.content.strip()
            else:
                return "抱歉，系统暂时无法回答。"
        except Exception as e:
            print(f"LLM 调用失败: {e}")
            return "您好！请问有什么可以帮您？"
        
