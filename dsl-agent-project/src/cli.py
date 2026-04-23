# -*- coding: utf-8 -*-
"""
命令行界面
"""

import os
import sys
from typing import List
from .agent import DSLAgent

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_welcome():
    """打印欢迎信息"""
    print("=" * 50)
    print("        DSL Agent 智能客服系统")
    print("=" * 50)
    print("命令说明:")
    print("  - 输入消息与客服对话")
    print("  - 输入 'history' 查看对话历史")
    print("  - 输入 'clear' 清空对话历史")
    print("  - 输入 'context' 查看当前上下文")
    print("  - 输入 'help' 显示帮助")
    print("  - 输入 'exit' 或 'quit' 退出")
    print("=" * 50)

def print_responses(responses: List[str]):
    """打印响应"""
    for response in responses:
        print(f"\n🤖 客服: {response}")

def main():
    """主函数"""
    # 清屏
    clear_screen()
    print_welcome()
    
    # 获取DSL脚本路径
    script_dir = os.path.join(os.path.dirname(__file__), '..', 'scripts')
    dsl_file = os.path.join(script_dir, 'ecommerce.dsl.yaml')
    
    if not os.path.exists(dsl_file):
        print(f"错误: DSL文件不存在: {dsl_file}")
        print(f"请确保已创建DSL脚本文件")
        return
    
    try:
        # 初始化Agent
        print(f"\n正在加载DSL脚本: {os.path.basename(dsl_file)}")
        agent = DSLAgent(dsl_file)
        print("系统初始化完成！")
        
        # 对话循环
        while True:
            try:
                user_input = input("\n👤 你: ").strip()
                
                if not user_input:
                    continue
                
                # 处理命令
                if user_input.lower() in ['exit', 'quit']:
                    print("感谢使用，再见！")
                    break
                
                elif user_input.lower() == 'history':
                    history = agent.get_conversation_history()
                    if history:
                        print("\n📜 对话历史:")
                        for i, entry in enumerate(history, 1):
                            print(f"{i}. 你: {entry['user']}")
                            print(f"   意图: {entry.get('intent', '未知')}")
                            if 'responses' in entry:
                                for response in entry['responses']:
                                    print(f"   客服: {response}")
                    else:
                        print("暂无对话历史")
                    continue
                
                elif user_input.lower() == 'clear':
                    agent.clear_history()
                    print("对话历史已清空")
                    continue
                
                elif user_input.lower() == 'context':
                    context = agent.dsl_parser.context
                    if context:
                        print("\n📊 当前上下文:")
                        for key, value in context.items():
                            print(f"  {key}: {value}")
                    else:
                        print("当前无上下文信息")
                    continue
                
                elif user_input.lower() == 'help':
                    print_welcome()
                    continue
                
                # 处理用户消息
                responses = agent.process_message(user_input)
                print_responses(responses)
                
            except KeyboardInterrupt:
                print("\n\n检测到中断，正在退出...")
                break
            except Exception as e:
                print(f"处理消息时出错: {e}")
    
    except Exception as e:
        print(f"初始化失败: {e}")
        print("请检查：")
        print("1. .env文件是否存在并包含OPENAI_API_KEY")
        print("2. DSL脚本文件是否正确")
        print("3. 网络连接是否正常")

if __name__ == "__main__":
    main()