#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试币安云钱包余额查询接口 - 根据代币符号获取余额
"""

import sys
import os
import json

# 添加父目录到 sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

import requests

def get_token_amount(csrf_token, cookie, symbol):
    """
    根据代币符号获取余额
    
    Args:
        csrf_token: CSRF令牌
        cookie: Cookie字符串
        symbol: 代币符号（例如 "AOP"）
        
    Returns:
        float: 代币数量，未找到返回0
    """
    url = "https://www.binance.com/bapi/defi/v1/private/wallet-direct/cloud-wallet/alpha"
    
    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'clienttype': 'web',
        'content-type': 'application/json',
        'csrftoken': csrf_token,
        'cookie': cookie,
        'lang': 'zh-CN',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('code') == '000000':
                token_list = data.get('data', {}).get('list', [])
                
                for token in token_list:
                    if token.get('symbol') == symbol:
                        amount = float(token.get('amount', 0))
                        print(f"找到代币 {symbol}: amount = {amount}")
                        return amount
                
                print(f"未找到代币: {symbol}")
                return 0
            else:
                print(f"API返回错误: {data.get('message', '未知错误')}")
                return 0
        else:
            print(f"请求失败: {response.status_code}")
            return 0
            
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return 0

if __name__ == "__main__":
    print("=" * 60)
    print("测试获取AOP代币余额")
    print("=" * 60)
    
    # 从配置文件读取认证信息
    try:
        config_path = os.path.join(parent_dir, 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        csrf_token = config.get('csrf_token', '')
        cookie = config.get('cookie', '')
    except Exception as e:
        print(f"读取配置文件失败: {str(e)}")
        csrf_token = ''
        cookie = ''
    
    if not csrf_token or not cookie:
        print("错误: 未找到认证信息，请先在配置文件中设置 csrf_token 和 cookie")
    else:
        print(f"CSRF Token: {csrf_token[:20]}...")
        print(f"Cookie: {cookie[:50]}...\n")
        
        # 获取AOP代币余额
        symbol = "AOP"
        amount = get_token_amount(csrf_token, cookie, symbol)
        
        print(f"\n结果: {symbol} 代币余额 = {amount}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)