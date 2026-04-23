# -*- coding: utf-8 -*-
"""
测试通义千问API连接
"""

import os
from dotenv import load_dotenv

def test_dashscope_api():
    """测试通义千问API连接"""
    load_dotenv()
    
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("错误: 未找到DASHSCOPE_API_KEY环境变量")
        print("请在.env文件中添加: DASHSCOPE_API_KEY=你的API密钥")
        return
    
    print(f"API密钥前几位: {api_key[:10]}...")
    
    # 测试导入
    try:
        import dashscope # type: ignore
        dashscope.api_key = api_key
        print("dashscope导入成功")
        
        # 简单测试
        from dashscope import Generation # type: ignore
        response = Generation.call(
            model='qwen-turbo',
            prompt='你好',
            max_tokens=10
        )
        
        if response.status_code == 200:
            print("API连接测试成功!")
            print(f"响应: {response.output.text}")
        else:
            print(f"API调用失败: {response.code} - {response.message}")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_dashscope_api()