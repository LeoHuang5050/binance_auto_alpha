#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试币安ALPHA交易接口 - get-exchange-info
Test Binance ALPHA Trade API - get-exchange-info
"""

import requests
import json
import time
from datetime import datetime

def test_get_exchange_info():
    """测试获取交易所信息接口"""
    
    print("=" * 60)
    print("币安ALPHA交易接口测试 - get-exchange-info")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 接口URL
    url = "https://www.binance.com/bapi/defi/v1/public/alpha-trade/get-exchange-info"
    
    # 请求头
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'https://www.binance.com/zh/alpha-trade',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        print("正在请求接口...")
        print(f"URL: {url}")
        print(f"请求头: {json.dumps(headers, indent=2, ensure_ascii=False)}")
        print("-" * 60)
        
        # 发送请求
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=30)
        end_time = time.time()
        
        # 响应信息
        print(f"响应状态码: {response.status_code}")
        print(f"响应时间: {(end_time - start_time):.2f}秒")
        print(f"响应头: {dict(response.headers)}")
        print("-" * 60)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ 接口调用成功!")
                print()
                
                # 解析响应数据
                if data.get('success') and data.get('code') == '000000':
                    exchange_data = data.get('data', {})
                    
                    print("📊 交易所信息:")
                    print(f"  时区: {exchange_data.get('timezone', 'N/A')}")
                    print(f"  OTO功能启用: {exchange_data.get('otoEnabled', 'N/A')}")
                    print()
                    
                    # 统计资产信息
                    assets = exchange_data.get('assets', [])
                    print(f"💰 支持的资产数量: {len(assets)}")
                    
                    # 统计交易对信息
                    symbols = exchange_data.get('symbols', [])
                    print(f"📈 支持的交易对数量: {len(symbols)}")
                    print()
                    
                    # 分析交易对状态
                    status_count = {}
                    for symbol in symbols:
                        status = symbol.get('status', 'UNKNOWN')
                        status_count[status] = status_count.get(status, 0) + 1
                    
                    print("📊 交易对状态统计:")
                    for status, count in status_count.items():
                        print(f"  {status}: {count}个")
                    print()
                    
                    # 显示部分交易对示例
                    print("🔍 交易对示例 (前10个):")
                    for i, symbol in enumerate(symbols[:10]):
                        print(f"  {i+1}. {symbol.get('symbol', 'N/A')} - {symbol.get('status', 'N/A')}")
                        print(f"     基础资产: {symbol.get('baseAsset', 'N/A')}")
                        print(f"     报价资产: {symbol.get('quoteAsset', 'N/A')}")
                        print(f"     价格精度: {symbol.get('pricePrecision', 'N/A')}")
                        print(f"     数量精度: {symbol.get('quantityPrecision', 'N/A')}")
                        print()
                    
                    # 查找ALPHA_22相关的交易对
                    print("🔍 ALPHA_22相关交易对:")
                    alpha_22_symbols = [s for s in symbols if 'ALPHA_22' in s.get('symbol', '')]
                    for symbol in alpha_22_symbols:
                        print(f"  {symbol.get('symbol', 'N/A')} - {symbol.get('status', 'N/A')}")
                        print(f"     基础资产: {symbol.get('baseAsset', 'N/A')}")
                        print(f"     报价资产: {symbol.get('quoteAsset', 'N/A')}")
                        print(f"     价格精度: {symbol.get('pricePrecision', 'N/A')}")
                        print(f"     数量精度: {symbol.get('quantityPrecision', 'N/A')}")
                        
                        # 显示过滤器信息
                        filters = symbol.get('filters', [])
                        print(f"     过滤器数量: {len(filters)}")
                        for filter_info in filters:
                            filter_type = filter_info.get('filterType', 'N/A')
                            if filter_type == 'LOT_SIZE':
                                print(f"        {filter_type}: 最小数量={filter_info.get('minQty', 'N/A')}, 最大数量={filter_info.get('maxQty', 'N/A')}")
                            elif filter_type == 'PRICE_FILTER':
                                print(f"        {filter_type}: 最小价格={filter_info.get('minPrice', 'N/A')}, 最大价格={filter_info.get('maxPrice', 'N/A')}")
                            elif filter_type == 'MIN_NOTIONAL':
                                print(f"        {filter_type}: 最小名义价值={filter_info.get('minNotional', 'N/A')}")
                        print()
                    
                    # 保存完整响应到文件
                    output_file = f"exchange_info_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"💾 完整响应已保存到: {output_file}")
                    
                else:
                    print("❌ 接口返回错误:")
                    print(f"  成功状态: {data.get('success', 'N/A')}")
                    print(f"  错误代码: {data.get('code', 'N/A')}")
                    print(f"  错误信息: {data.get('message', 'N/A')}")
                    print(f"  详细信息: {data.get('messageDetail', 'N/A')}")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"原始响应内容: {response.text[:500]}...")
                
        else:
            print(f"❌ HTTP请求失败:")
            print(f"  状态码: {response.status_code}")
            print(f"  响应内容: {response.text[:500]}...")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误")
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
    
    print("=" * 60)
    print("测试完成")

def test_specific_symbols():
    """测试特定交易对的信息"""
    
    print("\n" + "=" * 60)
    print("特定交易对信息测试")
    print("=" * 60)
    
    # 测试的交易对列表
    test_symbols = [
        "ALPHA_22USDT",  # KOGE
        "ALPHA_387USDT", # NUMI
        "ALPHA_347USDT", # WOD
        "ALPHA_373USDT", # ALEO
        "ALPHA_351USDT", # MCH
        "ALPHA_366USDT", # POP
        "ALPHA_382USDT", # AOP
        "ALPHA_372USDT", # ZEUS
        "ALPHA_386USDT", # FROGGIE
    ]
    
    url = "https://www.binance.com/bapi/defi/v1/public/alpha-trade/get-exchange-info"
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('code') == '000000':
                symbols = data.get('data', {}).get('symbols', [])
                
                print("🔍 特定交易对详细信息:")
                for symbol_name in test_symbols:
                    symbol_info = next((s for s in symbols if s.get('symbol') == symbol_name), None)
                    if symbol_info:
                        print(f"\n📊 {symbol_name}:")
                        print(f"  状态: {symbol_info.get('status', 'N/A')}")
                        print(f"  基础资产: {symbol_info.get('baseAsset', 'N/A')}")
                        print(f"  报价资产: {symbol_info.get('quoteAsset', 'N/A')}")
                        print(f"  价格精度: {symbol_info.get('pricePrecision', 'N/A')}")
                        print(f"  数量精度: {symbol_info.get('quantityPrecision', 'N/A')}")
                        print(f"  基础资产精度: {symbol_info.get('baseAssetPrecision', 'N/A')}")
                        print(f"  报价精度: {symbol_info.get('quotePrecision', 'N/A')}")
                        
                        # 显示重要的过滤器
                        filters = symbol_info.get('filters', [])
                        for filter_info in filters:
                            filter_type = filter_info.get('filterType', '')
                            if filter_type == 'LOT_SIZE':
                                print(f"  数量限制: {filter_info.get('minQty', 'N/A')} - {filter_info.get('maxQty', 'N/A')}")
                            elif filter_type == 'PRICE_FILTER':
                                print(f"  价格限制: {filter_info.get('minPrice', 'N/A')} - {filter_info.get('maxPrice', 'N/A')}")
                            elif filter_type == 'MIN_NOTIONAL':
                                print(f"  最小名义价值: {filter_info.get('minNotional', 'N/A')}")
                            elif filter_type == 'MAX_NOTIONAL':
                                print(f"  最大名义价值: {filter_info.get('maxNotional', 'N/A')}")
                    else:
                        print(f"❌ {symbol_name}: 未找到")
            else:
                print("❌ 获取交易所信息失败")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")

if __name__ == "__main__":
    print("币安ALPHA交易接口测试工具")
    print("Binance ALPHA Trade API Test Tool")
    print()
    
    # 测试获取交易所信息
    test_get_exchange_info()
    
    # 测试特定交易对
    test_specific_symbols()
    
    print("\n测试完成，感谢使用！")
