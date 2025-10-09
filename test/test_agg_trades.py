#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试获取聚合成交数据接口
"""

import requests
import json
from datetime import datetime
import urllib.parse

def test_agg_trades():
    """测试获取聚合成交数据接口"""
    
    # 接口URL
    url = "https://www.binance.com/bapi/defi/v1/public/alpha-trade/agg-trades"
    
    # 请求参数
    params = {
        'symbol': 'ALPHA_347USDT',
        'limit': 2  # 获取最近2条交易记录
    }
    
    # 请求头（公开接口，不需要认证）
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
    }
    
    try:
        print("正在测试获取聚合成交数据接口...")
        print(f"请求URL: {url}")
        print(f"请求参数: {params}")
        print("-" * 50)
        
        # 发送请求
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        # 解析响应
        data = response.json()
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # 分析响应数据
        if isinstance(data, dict) and data.get('code') == '000000':
            trades = data.get('data', [])
            print(f"\n✅ 接口调用成功!")
            print(f"获取到 {len(trades)} 条交易记录")
            
            if len(trades) > 0:
                print("\n📊 交易记录详情:")
                for i, trade in enumerate(trades, 1):
                    print(f"\n交易 {i}:")
                    print(f"  聚合交易ID: {trade.get('a')}")
                    print(f"  价格: {trade.get('p')} USDT")
                    print(f"  数量: {trade.get('q')}")
                    print(f"  第一笔交易ID: {trade.get('f')}")
                    print(f"  最后一笔交易ID: {trade.get('l')}")
                    print(f"  是否为买方主动: {trade.get('m')}")
                    
                    # 转换时间戳为正常时间
                    timestamp = trade.get('T')
                    if timestamp:
                        dt = datetime.fromtimestamp(timestamp / 1000)
                        print(f"  交易时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print("\n📭 没有找到交易记录")
                
        elif isinstance(data, list) and len(data) > 0:
            print(f"\n✅ 接口调用成功!")
            print(f"获取到 {len(data)} 条交易记录")
            
            print("\n📊 交易记录详情:")
            for i, trade in enumerate(data, 1):
                print(f"\n交易 {i}:")
                print(f"  聚合交易ID: {trade.get('a')}")
                print(f"  价格: {trade.get('p')} USDT")
                print(f"  数量: {trade.get('q')}")
                print(f"  第一笔交易ID: {trade.get('f')}")
                print(f"  最后一笔交易ID: {trade.get('l')}")
                print(f"  是否为买方主动: {trade.get('m')}")
                
                # 转换时间戳为正常时间
                timestamp = trade.get('T')
                if timestamp:
                    dt = datetime.fromtimestamp(timestamp / 1000)
                    print(f"  交易时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                
        elif isinstance(data, list) and len(data) == 0:
            print("\n📭 没有找到交易记录")
        else:
            print(f"\n❌ 响应格式异常: {type(data)}")
            if isinstance(data, dict):
                print(f"错误信息: {data.get('message', '未知错误')}")
                print(f"响应代码: {data.get('code', '未知')}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {str(e)}")
        print(f"原始响应: {response.text}")
    except Exception as e:
        print(f"❌ 未知错误: {str(e)}")

if __name__ == "__main__":
    test_agg_trades()
