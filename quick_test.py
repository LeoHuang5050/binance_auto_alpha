#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试币安ALPHA交易接口
Quick Test for Binance ALPHA Trade API
"""

import requests
import json
from datetime import datetime

def quick_test():
    """快速测试接口"""
    
    print("🚀 币安ALPHA交易接口快速测试")
    print("=" * 50)
    
    url = "https://www.binance.com/bapi/defi/v1/public/alpha-trade/get-exchange-info"
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        print("📡 正在请求接口...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success') and data.get('code') == '000000':
                exchange_data = data.get('data', {})
                
                print("✅ 接口调用成功!")
                print(f"📊 时区: {exchange_data.get('timezone', 'N/A')}")
                print(f"🔧 OTO功能: {'启用' if exchange_data.get('otoEnabled') else '禁用'}")
                
                assets = exchange_data.get('assets', [])
                symbols = exchange_data.get('symbols', [])
                
                print(f"💰 支持资产: {len(assets)}个")
                print(f"📈 交易对数量: {len(symbols)}个")
                
                # 统计状态
                status_count = {}
                for symbol in symbols:
                    status = symbol.get('status', 'UNKNOWN')
                    status_count[status] = status_count.get(status, 0) + 1
                
                print("\n📊 交易对状态:")
                for status, count in status_count.items():
                    print(f"  {status}: {count}个")
                
                # 查找ALPHA_22
                alpha_22_symbols = [s for s in symbols if 'ALPHA_22' in s.get('symbol', '')]
                if alpha_22_symbols:
                    print(f"\n🔍 ALPHA_22交易对:")
                    for symbol in alpha_22_symbols:
                        print(f"  {symbol.get('symbol')} - {symbol.get('status')}")
                        print(f"    价格精度: {symbol.get('pricePrecision')}")
                        print(f"    数量精度: {symbol.get('quantityPrecision')}")
                        
                        # 显示重要过滤器
                        for filter_info in symbol.get('filters', []):
                            if filter_info.get('filterType') == 'LOT_SIZE':
                                print(f"    数量范围: {filter_info.get('minQty')} - {filter_info.get('maxQty')}")
                            elif filter_info.get('filterType') == 'MIN_NOTIONAL':
                                print(f"    最小名义价值: {filter_info.get('minNotional')}")
                
                print(f"\n💾 完整数据已保存到: exchange_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                with open(f"exchange_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
            else:
                print("❌ 接口返回错误:")
                print(f"  代码: {data.get('code')}")
                print(f"  消息: {data.get('message')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print("\n测试完成! 🎉")

if __name__ == "__main__":
    quick_test()
