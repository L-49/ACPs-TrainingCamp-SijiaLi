# -*- coding: utf-8 -*-
# COMMIT TEST 2025-12-02
# src/main.py
import os
import sys

# 将 src 目录加入 Python 路径
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# 确保 scripts 目录也能被访问
scripts_dir = os.path.join(os.path.dirname(src_dir), 'scripts')
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

# 现在可以导入
from agent import DSLAgent

def main():
    print("DSL Agent 项目启动成功！")
    print("正在加载电商客服脚本...")
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dsl_path = os.path.join(project_root, 'scripts', 'ecommerce.dsl.yaml')
    
    if not os.path.exists(dsl_path):
        print(f"❌ 错误：DSL 脚本不存在: {dsl_path}")
        return
    
    try:
        agent = DSLAgent(dsl_file=dsl_path)
        print("✅ Agent 初始化成功！")
        print("\n💬 欢迎使用智能客服！输入 'quit' 退出。")
        
        while True:
            user_input = input("\n👤 用户: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break
            if not user_input:
                continue
                
            responses = agent.process_message(user_input)
            for resp in responses:
                print(f"🤖 客服: {resp}")
                
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
