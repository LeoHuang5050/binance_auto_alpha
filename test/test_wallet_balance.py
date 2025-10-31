#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试币安钱包资产接口(v2) - 根据原始代币符号获取余额
示例：MERL、USDT 等
"""

import sys
import os
import json

# 添加父目录到 sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

import requests

def get_token_amount_v2(csrf_token, cookie, symbol):
    """
    使用新资产接口获取余额
    Args:
        csrf_token: CSRF令牌
        cookie: Cookie字符串
        symbol: 原始代币符号（如 "MERL"）
    Returns:
        float: 代币数量，未找到返回0
    """
    url = "https://www.binance.com/bapi/asset/v2/private/asset-service/wallet/asset"
    params = {
        "needAlphaAsset": "true",
        "needEuFuture": "true",
        "needPnl": "true",
    }
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
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code != 200:
            print(f"请求失败: {resp.status_code}")
            return 0
        data = resp.json()
        assets = data.get('data') or []
        for item in assets:
            if item.get('asset') == symbol:
                amount = float(item.get('amount', '0') or '0')
                print(f"找到代币 {symbol}: amount = {amount}")
                return amount
        print(f"未找到代币: {symbol}")
        return 0
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return 0

if __name__ == "__main__":
    print("=" * 60)
    print("测试获取MERL代币余额（新接口）")
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
        
        # 获取MERL代币余额（使用原始代币名）
        symbol = "MERL"
        amount = get_token_amount_v2(csrf_token, cookie, symbol)
        
        print(f"\n结果: {symbol} 代币余额 = {amount}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)