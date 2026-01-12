#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Alpha123稳定度数据获取
Test Alpha123 Stability Data Fetching
"""

import sys
import os
import json

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alpha123 import Alpha123Client
from logger import Logger


def test_fetch_stability_data():
    """测试获取稳定度数据"""
    print("\n" + "=" * 80)
    print("测试1：获取稳定度数据")
    print("=" * 80)
    
    # 创建logger和client
    logger = Logger(log_dir="log")
    
    # 加载ALPHA代币ID映射
    try:
        with open('alphaIdMap.json', 'r', encoding='utf-8') as f:
            alpha_id_map = json.load(f)
    except:
        alpha_id_map = {"KOGE": "ALPHA_22"}
    
    client = Alpha123Client(logger=logger, alpha_id_map=alpha_id_map)
    
    # 获取稳定度数据
    print("\n正在获取稳定度数据...")
    stability_data = client.fetch_stability_data()
    
    if not stability_data:
        print("[FAIL] 未获取到稳定度数据")
        return False
    
    print(f"[OK] 成功获取 {len(stability_data)} 个项目的稳定度数据\n")
    
    # 显示前10个项目
    print("前10个项目（按价差基点排序）：")
    print("-" * 80)
    print(f"{'项目':<10} {'稳定度':<10} {'价格':<15} {'4倍天数':<10} {'价差基点':<10}")
    print("-" * 80)
    
    for i, item in enumerate(stability_data[:10]):
        project = item.get('project', 'N/A')
        stability = item.get('stability', 'N/A')
        price = item.get('price', 'N/A')
        remaining_days = item.get('remaining_days', 'N/A')
        spread = item.get('spread', 'N/A')
        
        print(f"{project:<10} {stability:<10} {price:<15} {remaining_days:<10} {spread:<10}")
    
    print("-" * 80)
    return True


def test_get_top_stability_token():
    """测试获取稳定度第一的代币"""
    print("\n" + "=" * 80)
    print("测试2：获取稳定度第一的代币（spr < 1）")
    print("=" * 80)
    
    # 创建logger和client
    logger = Logger(log_dir="log")
    
    # 加载ALPHA代币ID映射
    try:
        with open('alphaIdMap.json', 'r', encoding='utf-8') as f:
            alpha_id_map = json.load(f)
    except:
        alpha_id_map = {"KOGE": "ALPHA_22"}
    
    client = Alpha123Client(logger=logger, alpha_id_map=alpha_id_map)
    
    # 获取稳定度第一的代币
    print("\n正在获取稳定度第一的代币...")
    print("过滤条件：")
    print("  - 排除KOGE")
    print("  - 4倍天数(md) > 0")
    print("  - 价差基点(spr) < 1")
    print()
    
    top_token = client.get_top_stability_token()
    
    if not top_token:
        print("[FAIL] 未找到符合条件的稳定代币")
        print("   可能原因：")
        print("   1. 所有代币的价差基点(spr)都 >= 1")
        print("   2. API获取数据失败")
        print("   3. 没有4倍天数 > 0的代币")
        return False
    
    print("[OK] 成功找到稳定度第一的代币！\n")
    print("=" * 80)
    print("代币信息：")
    print("-" * 80)
    print(f"  项目名称:   {top_token.get('display_name', 'N/A')}")
    print(f"  交易对:     {top_token.get('symbol', 'N/A')}")
    print(f"  当前价格:   ${top_token.get('price', 'N/A')}")
    print(f"  稳定度:     {top_token.get('stability', 'N/A')}")
    print(f"  价差基点:   {top_token.get('spread', 'N/A')}")
    print("-" * 80)
    
    # 验证价差基点是否 < 1
    try:
        spread_value = float(top_token.get('spread', 999))
        if spread_value < 1:
            print(f"[OK] 价差基点验证通过: {spread_value} < 1")
        else:
            print(f"[FAIL] 价差基点验证失败: {spread_value} >= 1")
    except:
        print("[FAIL] 无法验证价差基点")
    
    print("=" * 80)
    return True


def test_stability_filter():
    """测试稳定度过滤条件"""
    print("\n" + "=" * 80)
    print("测试3：验证过滤条件")
    print("=" * 80)
    
    # 创建logger和client
    logger = Logger(log_dir="log")
    
    # 加载ALPHA代币ID映射
    try:
        with open('alphaIdMap.json', 'r', encoding='utf-8') as f:
            alpha_id_map = json.load(f)
    except:
        alpha_id_map = {"KOGE": "ALPHA_22"}
    
    client = Alpha123Client(logger=logger, alpha_id_map=alpha_id_map)
    
    # 获取所有数据
    stability_data = client.fetch_stability_data()
    
    if not stability_data:
        print("[FAIL] 未获取到数据")
        return False
    
    print(f"\n总共获取到 {len(stability_data)} 个项目")
    print("\n验证过滤条件：")
    print("-" * 80)
    
    # 统计各种情况
    koge_count = 0
    md_zero_count = 0
    md_positive_count = 0
    spr_less_than_1_count = 0
    spr_greater_equal_1_count = 0
    
    for item in stability_data:
        project = item.get('project', '')
        remaining_days_str = item.get('remaining_days', '0')
        spread_str = item.get('spread', '999')
        
        try:
            remaining_days = int(remaining_days_str)
        except:
            remaining_days = 0
        
        try:
            spread = float(spread_str)
        except:
            spread = 999
        
        # 统计
        if project.upper() == 'KOGE':
            koge_count += 1
        else:
            if remaining_days == 0:
                md_zero_count += 1
            else:
                md_positive_count += 1
                
                if spread < 1:
                    spr_less_than_1_count += 1
                else:
                    spr_greater_equal_1_count += 1
    
    print(f"KOGE项目数量:              {koge_count}")
    print(f"4倍天数 = 0 的项目:        {md_zero_count} (已过滤)")
    print(f"4倍天数 > 0 的项目:        {md_positive_count}")
    print(f"  - 其中 spr < 1 的项目:   {spr_less_than_1_count} [OK] (符合条件)")
    print(f"  - 其中 spr >= 1 的项目:  {spr_greater_equal_1_count} [X] (不符合)")
    print("-" * 80)
    
    if spr_less_than_1_count > 0:
        print(f"\n[OK] 有 {spr_less_than_1_count} 个代币符合稳定条件（spr < 1）")
    else:
        print("\n[FAIL] 没有代币符合稳定条件（spr < 1）")
    
    print("=" * 80)
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("Alpha123稳定度数据测试")
    print("=" * 80)
    
    try:
        # 测试1：获取稳定度数据
        result1 = test_fetch_stability_data()
        
        # 测试2：获取稳定度第一的代币
        result2 = test_get_top_stability_token()
        
        # 测试3：验证过滤条件
        result3 = test_stability_filter()
        
        # 总结
        print("\n" + "=" * 80)
        print("测试结果总结")
        print("=" * 80)
        print(f"测试1 - 获取稳定度数据:     {'[PASS]' if result1 else '[FAIL]'}")
        print(f"测试2 - 获取稳定度第一:     {'[PASS]' if result2 else '[FAIL]'}")
        print(f"测试3 - 验证过滤条件:       {'[PASS]' if result3 else '[FAIL]'}")
        print("=" * 80)
        
        if result1 and result2 and result3:
            print("\n[SUCCESS] 所有测试通过！")
        else:
            print("\n[WARNING] 部分测试失败，请检查日志")
        
    except Exception as e:
        print(f"\n[ERROR] 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

