# -*- coding: utf-8 -*-
"""测试DSL解析器功能（适配scripts目录结构）"""

import sys
import os

# ======================
# 修正Python路径：添加 scripts 目录（而非 src）
# ======================
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scripts_path = os.path.join(project_root, 'scripts')  # 关键：指向 scripts/

if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)
# ======================

# 现在可以从 scripts/ 目录导入
try:
    from dsl_parser import DSLParser
    print(f"✅ 成功导入 DSLParser，路径: {scripts_path}")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print(f"当前 sys.path: {sys.path}")
    sys.exit(1)

def test_order_number_intent():
    """测试订单号意图规则"""
    dsl_path = os.path.join(project_root, 'scripts', 'ecommerce.dsl.yaml')
    parser = DSLParser(dsl_path)
    
    # 查找 order_number 规则
    rule = None
    for r in parser.get_rules():
        if r.get('when') == 'order_number':
            rule = r
            break
    
    assert rule is not None, "未找到 order_number 规则"
    actions = rule.get('actions', [])
    assert len(actions) >= 1, "动作列表为空"
    assert "您的订单已发货" in actions[0]['content'], "响应内容不匹配"

def test_cancel_order_number_intent():
    """测试退货意图规则"""
    dsl_path = os.path.join(project_root, 'scripts', 'ecommerce.dsl.yaml')
    parser = DSLParser(dsl_path)
    
    # 查找 cancel_order_number 规则
    rule = None
    for r in parser.get_rules():
        if r.get('when') == 'cancel_order_number':
            rule = r
            break
    
    assert rule is not None, "未找到 cancel_order_number 规则"
    actions = rule.get('actions', [])
    assert len(actions) >= 1, "动作列表为空"
    assert "退款金额将于72小时内到账" in actions[0]['content'], "响应内容不匹配"

if __name__ == "__main__":
    test_order_number_intent()
    test_cancel_order_number_intent()
    print("✅ DSL解析器的意图规则测试通过！")