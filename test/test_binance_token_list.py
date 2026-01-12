#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试币安Alpha交易代币列表获取接口
Test Binance Alpha Token List API
"""

import sys
import os
import json

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from binance_api import BinanceAPI
from logger import Logger


def test_get_binance_token_list():
    """测试获取币安Alpha交易代币列表"""
    print("\n" + "=" * 80)
    print("测试1：获取币安Alpha交易代币列表")
    print("=" * 80)
    
    # 创建logger和API实例
    logger = Logger(log_dir="log")
    api = BinanceAPI(logger=logger)
    
    try:
        print("\n正在获取代币列表...")
        data = api.get_binance_token_list()
        
        if not data:
            print("[FAIL] 未获取到代币列表数据")
            return False
        
        # 检查响应结构
        if not data.get('success'):
            print(f"[FAIL] API返回失败: {data.get('message', '未知错误')}")
            return False
        
        token_list = data.get('data', [])
        
        if not token_list:
            print("[FAIL] 代币列表为空")
            return False
        
        print(f"[OK] 成功获取 {len(token_list)} 个代币\n")
        
        # 显示前10个代币的基本信息
        print("前10个代币信息：")
        print("-" * 80)
        print(f"{'Symbol':<15} {'Alpha ID':<15} {'Name':<30} {'Chain':<10}")
        print("-" * 80)
        
        for i, token in enumerate(token_list[:10]):
            symbol = token.get('symbol', 'N/A')
            alpha_id = token.get('alphaId', 'N/A')
            name = token.get('name', 'N/A')
            chain = token.get('chainSymbol', 'N/A')
            
            print(f"{symbol:<15} {alpha_id:<15} {name[:30]:<30} {chain:<10}")
        
        print("-" * 80)
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 获取代币列表失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_find_aio_token():
    """查找AIO代币信息"""
    print("\n" + "=" * 80)
    print("测试2：查找 AIO 代币信息")
    print("=" * 80)
    
    # 创建logger和API实例
    logger = Logger(log_dir="log")
    api = BinanceAPI(logger=logger)
    
    try:
        print("\n正在获取代币列表并查找 AIO 代币...")
        data = api.get_binance_token_list()
        
        if not data or not data.get('success'):
            print("[FAIL] 未获取到代币列表数据")
            return False
        
        token_list = data.get('data', [])
        
        # 查找 AIO 代币（不区分大小写）
        aio_tokens = []
        for token in token_list:
            symbol = token.get('symbol', '').upper()
            name = token.get('name', '').upper()
            alpha_id = token.get('alphaId', '').upper()
            
            # 检查 symbol、name 或 alphaId 中是否包含 AIO
            if 'AIO' in symbol or 'AIO' in name or 'AIO' in alpha_id:
                aio_tokens.append(token)
        
        if not aio_tokens:
            print("[FAIL] 未找到 AIO 代币")
            print("\n正在显示所有代币的 Symbol，帮助排查...")
            print("-" * 80)
            all_symbols = [token.get('symbol', 'N/A') for token in token_list[:50]]
            print(f"前50个代币 Symbol: {', '.join(all_symbols)}")
            print("-" * 80)
            return False
        
        print(f"[OK] 找到 {len(aio_tokens)} 个相关代币\n")
        
        # 显示所有找到的 AIO 代币信息
        for idx, token in enumerate(aio_tokens, 1):
            print(f"=== AIO 代币 #{idx} ===")
            print("-" * 80)
            
            # 显示所有字段
            for key, value in token.items():
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value, ensure_ascii=False, indent=2)
                    print(f"{key}:")
                    print(value_str)
                else:
                    print(f"{key}: {value}")
            
            print("-" * 80)
            
            # 特别标注关键字段
            print("\n关键信息：")
            symbol = token.get('symbol', 'N/A')
            alpha_id = token.get('alphaId', 'N/A')
            name = token.get('name', 'N/A')
            chain = token.get('chainSymbol', 'N/A')
            contract_address = token.get('contractAddress', 'N/A')
            
            print(f"  Symbol:           {symbol}")
            print(f"  Alpha ID:         {alpha_id}")
            print(f"  名称:             {name}")
            print(f"  链:               {chain}")
            print(f"  合约地址:         {contract_address}")
            
            # 检查是否可以用于交易
            if alpha_id:
                print(f"\n  交易对符号:       {alpha_id}USDT")
            else:
                print(f"\n  ⚠️  未找到 Alpha ID，可能无法交易")
            
            print("\n")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 查找 AIO 代币失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_create_alpha_id_map():
    """测试创建Alpha ID映射"""
    print("\n" + "=" * 80)
    print("测试3：创建 Alpha ID 映射")
    print("=" * 80)
    
    # 创建logger和API实例
    logger = Logger(log_dir="log")
    api = BinanceAPI(logger=logger)
    
    try:
        print("\n正在获取代币列表并创建映射...")
        token_list_data = api.get_binance_token_list()
        
        if not token_list_data or not token_list_data.get('success'):
            print("[FAIL] 未获取到代币列表数据")
            return False
        
        alpha_id_map = api.create_alpha_id_map(token_list_data)
        
        if not alpha_id_map:
            print("[FAIL] 创建的映射为空")
            return False
        
        print(f"[OK] 成功创建 {len(alpha_id_map)} 个代币的映射\n")
        
        # 查找 AIO 相关的映射
        print("查找 AIO 相关的映射：")
        print("-" * 80)
        
        aio_mappings = {}
        for symbol, alpha_id in alpha_id_map.items():
            if 'AIO' in symbol.upper() or 'AIO' in alpha_id.upper():
                aio_mappings[symbol] = alpha_id
        
        if aio_mappings:
            print("找到以下 AIO 相关映射：")
            for symbol, alpha_id in aio_mappings.items():
                print(f"  {symbol} -> {alpha_id}")
        else:
            print("未找到 AIO 相关映射")
            print("\n显示前20个映射示例：")
            for i, (symbol, alpha_id) in enumerate(list(alpha_id_map.items())[:20], 1):
                print(f"  {i}. {symbol} -> {alpha_id}")
        
        print("-" * 80)
        return True
        
    except Exception as e:
        print(f"[FAIL] 创建映射失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("币安Alpha交易代币列表接口测试")
    print("=" * 80)
    
    try:
        # 测试1：获取代币列表
        result1 = test_get_binance_token_list()
        
        # 测试2：查找 AIO 代币
        result2 = test_find_aio_token()
        
        # 测试3：创建 Alpha ID 映射
        result3 = test_create_alpha_id_map()
        
        # 总结
        print("\n" + "=" * 80)
        print("测试结果总结")
        print("=" * 80)
        print(f"测试1 - 获取代币列表:        {'[PASS]' if result1 else '[FAIL]'}")
        print(f"测试2 - 查找 AIO 代币:       {'[PASS]' if result2 else '[FAIL]'}")
        print(f"测试3 - 创建 Alpha ID 映射:   {'[PASS]' if result3 else '[FAIL]'}")
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

