#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试单向下单功能脚本
"""

import requests
import json
import time
from datetime import datetime, timedelta

def get_latest_price(symbol):
    """获取最新价格"""
    try:
        url = "https://www.binance.com/bapi/defi/v1/public/alpha-trade/klines"
        params = {
            'symbol': symbol,
            'interval': '1s',  # 1秒间隔获取最新价格
            'limit': 1  # 只获取1条K线数据
        }
        
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Baggage': 'sentry-environment=prod,sentry-release=20250924-d1d0004c-2900,sentry-public_key=9445af76b2ba747e7b574485f2c998f7,sentry-trace_id=847f639347bc49be967b6777b03a413c,sentry-sample_rate=0.01,sentry-transaction=%2Falpha%2F%24chainSymbol%2F%24contractAddress,sentry-sampled=false',
            'Bnc-Uuid': 'e420e928-1b68-4ea2-991d-016cf1dc6f8b',
            'Clienttype': 'web',
            'Content-Type': 'application/json',
            'Cookie': 'theme=dark; bnc-uuid=e420e928-1b68-4ea2-991d-016cf1dc6f8b; _gid=GA1.2.951612344.1758819202; BNC_FV_KEY=33ea495bf3a5a79b884c5845faf9ca5e77e32ab5; ref=FEQE7YL0; lang=zh-CN; language=zh-CN; se_sd=AQPAhWVkMHTCRVWMRBgVgZZDBDA9TEQUlsN5aVEd1lcUgVVNWV4A1; se_gd=QZaVlDhAHQRA1IaRXUBMgZZAFVQcUBQUlpc5aVEd1lcUgG1NWVAP1; se_gsd=YDo2XDtWNTAgCSMrNAgnMzkECQIaBQYaV11BUl1QVllaJ1NT1; currentAccount=; logined=y; BNC-Location=CN; aws-waf-token=6a2e990f-c746-49ff-9096-b327596dd9d8:BgoAZZh3lccKAAAA:frs4tlGhn0srGqMVNdKjOUR6E1AopfP/a3uZHcPKLSFBKkQjYpgbOsjbsL/PuL7PzWy1a6xg+L7J/Hnb9L5xAb88hAOBFBDOL358HxuVvNgpN41Rqv/RGGnERAcxnm6cSRWMXbe+yCluzdyiGMFLc5oMXF4CTn0fUmdeBrXbkaCX0HYuT8/3xnMjVTs2E0cbasI=; _gcl_au=1.1.1119987010.1758819849; changeBasisTimeZone=; userPreferredCurrency=USD_USD; BNC_FV_KEY_T=101-wc4WPYO%2B3Rb7Mg3HHaWxA6MHkormTgmyD9rGzTzVOKwHQvo55bJ2lzMT%2BbZUdat95BcgrHgRyTlg0kkZjcN0DQ%3D%3D-IUTOKhlcGzLtvhtzcXChZg%3D%3D-8c; BNC_FV_KEY_EXPIRE=1758967585812; r20t=web.AE9CB0EBD5845F2CB6ADCA9667C1736A; r30t=1; cr00=22338F8E07EA42F2264AA39F47E723B7; d1og=web.1162735228.AFF6FA74AC2CB13655E400A8520AB977; r2o1=web.1162735228.F504CC1AB5DF2E043AFA12A07986B4D3; f30l=web.1162735228.BC38C5894270AA297AD43BECCDC49B3E; p20t=web.1162735228.94F8BF83B266E52880AC361D181FD0FE; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221162735228%22%2C%22first_id%22%3A%2219981cb2b079d5-0702e12ae9987a-26061951-3686400-19981cb2b08181c%22%2C%22props%22%3A%7B%22aws_waf_referrer%22%3A%22%7B%5C%22referrer%5C%22%3A%5C%22https%3A%2F%2Falpha123.uk%2F%5C%22%7D%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTk5ODFjYjJiMDc5ZDUtMDcwMmUxMmFlOTk4N2EtMjYwNjE5NTEtMzY4NjQwMC0xOTk4MWNiMmIwODE4MWMiLCIkaWRlbnRpdHlfbG9naW5faWQiOiIxMTYyNzM1MjI4In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%221162735228%22%7D%2C%22%24device_id%22%3A%2219981dc7d84bdb-0b69a1775381dc8-26061951-3686400-19981dc7d851c20%22%7D; _uetsid=a955dd009a3111f08ea99b841f36689a; _uetvid=a955d8909a3111f08c0c25e413aeab0c; _ga_3WP50LGEEC=GS2.1.s1758950440$o6$g1$t1758955852$j60$l0$h0; _ga=GA1.2.1952928982.1758819202; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Sep+27+2025+16%3A06%3A03+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202506.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=7e0430b4-07eb-4780-a2e2-48b9be3dd13c&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false',
            'csrftoken': '231efb54f001934bd7572f79523397f0',
            'device-info': 'eyJzY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsImF2YWlsYWJsZV9zY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsInN5c3RlbV92ZXJzaW9uIjoiV2luZG93cyAxMCIsImJyYW5kX21vZGVsIjoidW5rbm93biIsInN5c3RlbV9sYW5nIjoiemgtQ04iLCJ0aW1lem9uZSI6IkdNVCswODowMCIsInRpbWV6b25lT2Zmc2V0IjotNDgwLCJ1c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0MC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwibGlzdF9wbHVnaW4iOiJQREYgVmlld2VyLENocm9tZSBQREYgVmlld2VyLENocm9taXVtIFBERiBWaWV3ZXIsTWljcm9zb2Z0IEVkZ2UgUERGIFZpZXdlcixXZWJLaXQgYnVpbHQtaW4gUERGIiwiY2FudmFzX2NvZGUiOiI2NjAzODQyMyIsIndlYmdsX3ZlbmRvciI6Ikdvb2dsZSBJbmMuIChOVklESUEpIiwid2ViZ2xfcmVuZGVyZXIiOiJBTkdMRSAoTlZJRElBLCBOVklESUEgR2VGb3JjZSBSVFggMzA3MCAoMHgwMDAwMjQ4OCkgRGlyZWN0M0QxMSB2c181XzAgcHNfNV8wLCBEM0QxMSkiLCJhdWRpbyI6IjEyNC4wNDM0NzUyNzUxNjA3NCIsInBsYXRmb3JtIjoiV2luMzIiLCJ3ZWJfdGltZXpvbmUiOiJBc2lhL1NoYW5naGFpIiwiZGV2aWNlX25hbWUiOiJDaHJvbWUgVjE0MC4wLjAuMCAoV2luZG93cykiLCJmaW5nZXJwcmludCI6ImI0NzNmZjVhODA0ODU4YWQ2ZmYxYTdhNmQ2YzY0NjIzIiwiZGV2aWNlX2lkIjoiIiwicmVsYXRlZF9kZXZpY2VfaWRzIjoiIn0=',
            'fvideo-id': '33ea495bf3a5a79b884c5845faf9ca5e77e32ab5',
            'lang': 'zh-CN',
            'Priority': 'u=1, i',
            'Referer': 'https://www.binance.com/zh-CN/alpha/bsc/0xe6df05ce8c8301223373cf5b969afcb1498c5528',
            'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sentry-Trace': '847f639347bc49be967b6777b03a413c-ac242fc8bf0e51e2-0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'X-Passthrough-Token': '',
            'X-Trace-Id': '000f2190-8b35-4cb1-aa27-d62a5017a918',
            'X-Ui-Request-Trace': '000f2190-8b35-4cb1-aa27-d62a5017a918'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('code') == '000000' and data.get('success') == True:
            kline_data = data.get('data', [])
            if kline_data and len(kline_data) > 0:
                kline = kline_data[0]
                return float(kline[4])  # 收盘价（最新价格）
            else:
                return None
        else:
            print(f"获取价格失败: {data.get('message', '未知错误')}")
            return None
            
    except Exception as e:
        print(f"获取价格异常: {str(e)}")
        return None

def test_single_order():
    """测试单向交易功能（买单+卖单）"""
    
    # 配置信息
    csrf_token = "231efb54f001934bd7572f79523397f0"  # 请替换为你的CSRF token
    symbol = "ALPHA_22USDT"
    base_asset = symbol.replace('USDT', '')
    
    print(f"开始测试单向交易功能...")
    print(f"代币: {symbol}")
    print(f"基础资产: {base_asset}")
    print("-" * 50)
    
    # 第一步：获取最新价格并下买单
    print("=== 第一步：下买单 ===")
    print("正在获取最新价格...")
    latest_price = get_latest_price(symbol)
    if not latest_price:
        print("❌ 获取价格失败，使用默认价格")
        latest_price = 48.0
    else:
        print(f"✅ 获取到最新价格: ${latest_price}")
    
    # 计算买单参数
    base_amount = 1025
    working_quantity = base_amount / latest_price
    working_quantity_formatted = int(working_quantity * 10000) / 10000  # 截断到4位小数
    payment_amount = working_quantity_formatted * latest_price
    payment_amount_formatted = int(payment_amount * 100000000) / 100000000  # 截断到8位小数
    
    print(f"买单计算信息:")
    print(f"  基础金额: ${base_amount}")
    print(f"  最新价格: ${latest_price}")
    print(f"  原始代币份额: {working_quantity:.8f}")
    print(f"  截断后代币份额: {working_quantity_formatted}")
    print(f"  原始支付金额: {payment_amount:.8f}")
    print(f"  截断后支付金额: {payment_amount_formatted}")
    print("-" * 50)
    
    # 下单URL
    url = "https://www.binance.com/bapi/defi/v1/private/alpha-trade/order/place"
    
    # 请求头
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Baggage': 'sentry-environment=prod,sentry-release=20250924-d1d0004c-2900,sentry-public_key=9445af76b2ba747e7b574485f2c998f7,sentry-trace_id=847f639347bc49be967b6777b03a413c,sentry-sample_rate=0.01,sentry-transaction=%2Falpha%2F%24chainSymbol%2F%24contractAddress,sentry-sampled=false',
        'Bnc-Uuid': 'e420e928-1b68-4ea2-991d-016cf1dc6f8b',
        'Clienttype': 'web',
        'Content-Type': 'application/json',
        'Cookie': 'theme=dark; bnc-uuid=e420e928-1b68-4ea2-991d-016cf1dc6f8b; _gid=GA1.2.951612344.1758819202; BNC_FV_KEY=33ea495bf3a5a79b884c5845faf9ca5e77e32ab5; ref=FEQE7YL0; lang=zh-CN; language=zh-CN; se_sd=AQPAhWVkMHTCRVWMRBgVgZZDBDA9TEQUlsN5aVEd1lcUgVVNWV4A1; se_gd=QZaVlDhAHQRA1IaRXUBMgZZAFVQcUBQUlpc5aVEd1lcUgG1NWVAP1; se_gsd=YDo2XDtWNTAgCSMrNAgnMzkECQIaBQYaV11BUl1QVllaJ1NT1; currentAccount=; logined=y; BNC-Location=CN; aws-waf-token=6a2e990f-c746-49ff-9096-b327596dd9d8:BgoAZZh3lccKAAAA:frs4tlGhn0srGqMVNdKjOUR6E1AopfP/a3uZHcPKLSFBKkQjYpgbOsjbsL/PuL7PzWy1a6xg+L7J/Hnb9L5xAb88hAOBFBDOL358HxuVvNgpN41Rqv/RGGnERAcxnm6cSRWMXbe+yCluzdyiGMFLc5oMXF4CTn0fUmdeBrXbkaCX0HYuT8/3xnMjVTs2E0cbasI=; _gcl_au=1.1.1119987010.1758819849; changeBasisTimeZone=; userPreferredCurrency=USD_USD; BNC_FV_KEY_T=101-wc4WPYO%2B3Rb7Mg3HHaWxA6MHkormTgmyD9rGzTzVOKwHQvo55bJ2lzMT%2BbZUdat95BcgrHgRyTlg0kkZjcN0DQ%3D%3D-IUTOKhlcGzLtvhtzcXChZg%3D%3D-8c; BNC_FV_KEY_EXPIRE=1758967585812; r20t=web.AE9CB0EBD5845F2CB6ADCA9667C1736A; r30t=1; cr00=22338F8E07EA42F2264AA39F47E723B7; d1og=web.1162735228.AFF6FA74AC2CB13655E400A8520AB977; r2o1=web.1162735228.F504CC1AB5DF2E043AFA12A07986B4D3; f30l=web.1162735228.BC38C5894270AA297AD43BECCDC49B3E; p20t=web.1162735228.94F8BF83B266E52880AC361D181FD0FE; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221162735228%22%2C%22first_id%22%3A%2219981cb2b079d5-0702e12ae9987a-26061951-3686400-19981cb2b08181c%22%2C%22props%22%3A%7B%22aws_waf_referrer%22%3A%22%7B%5C%22referrer%5C%22%3A%5C%22https%3A%2F%2Falpha123.uk%2F%5C%22%7D%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTk5ODFjYjJiMDc5ZDUtMDcwMmUxMmFlOTk4N2EtMjYwNjE5NTEtMzY4NjQwMC0xOTk4MWNiMmIwODE4MWMiLCIkaWRlbnRpdHlfbG9naW5faWQiOiIxMTYyNzM1MjI4In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%221162735228%22%7D%2C%22%24device_id%22%3A%2219981dc7d84bdb-0b69a1775381dc8-26061951-3686400-19981dc7d851c20%22%7D; _uetsid=a955dd009a3111f08ea99b841f36689a; _uetvid=a955d8909a3111f08c0c25e413aeab0c; _ga_3WP50LGEEC=GS2.1.s1758950440$o6$g1$t1758955852$j60$l0$h0; _ga=GA1.2.1952928982.1758819202; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Sep+27+2025+16%3A06%3A03+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202506.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=7e0430b4-07eb-4780-a2e2-48b9be3dd13c&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false',
        'csrftoken': csrf_token,
        'device-info': 'eyJzY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsImF2YWlsYWJsZV9zY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsInN5c3RlbV92ZXJzaW9uIjoiV2luZG93cyAxMCIsImJyYW5kX21vZGVsIjoidW5rbm93biIsInN5c3RlbV9sYW5nIjoiemgtQ04iLCJ0aW1lem9uZSI6IkdNVCswODowMCIsInRpbWV6b25lT2Zmc2V0IjotNDgwLCJ1c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0MC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwibGlzdF9wbHVnaW4iOiJQREYgVmlld2VyLENocm9tZSBQREYgVmlld2VyLENocm9taXVtIFBERiBWaWV3ZXIsTWljcm9zb2Z0IEVkZ2UgUERGIFZpZXdlcixXZWJLaXQgYnVpbHQtaW4gUERGIiwiY2FudmFzX2NvZGUiOiI2NjAzODQyMyIsIndlYmdsX3ZlbmRvciI6Ikdvb2dsZSBJbmMuIChOVklESUEpIiwid2ViZ2xfcmVuZGVyZXIiOiJBTkdMRSAoTlZJRElBLCBOVklESUEgR2VGb3JjZSBSVFggMzA3MCAoMHgwMDAwMjQ4OCkgRGlyZWN0M0QxMSB2c181XzAgcHNfNV8wLCBEM0QxMSkiLCJhdWRpbyI6IjEyNC4wNDM0NzUyNzUxNjA3NCIsInBsYXRmb3JtIjoiV2luMzIiLCJ3ZWJfdGltZXpvbmUiOiJBc2lhL1NoYW5naGFpIiwiZGV2aWNlX25hbWUiOiJDaHJvbWUgVjE0MC4wLjAuMCAoV2luZG93cykiLCJmaW5nZXJwcmludCI6ImI0NzNmZjVhODA0ODU4YWQ2ZmYxYTdhNmQ2YzY0NjIzIiwiZGV2aWNlX2lkIjoiIiwicmVsYXRlZF9kZXZpY2VfaWRzIjoiIn0=',
        'fvideo-id': '33ea495bf3a5a79b884c5845faf9ca5e77e32ab5',
        'lang': 'zh-CN',
        'Priority': 'u=1, i',
        'Referer': 'https://www.binance.com/zh-CN/alpha/bsc/0xe6df05ce8c8301223373cf5b969afcb1498c5528',
        'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sentry-Trace': '847f639347bc49be967b6777b03a413c-ac242fc8bf0e51e2-0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'X-Passthrough-Token': '',
        'X-Trace-Id': '000f2190-8b35-4cb1-aa27-d62a5017a918',
        'X-Ui-Request-Trace': '000f2190-8b35-4cb1-aa27-d62a5017a918'
    }
    
    # 构建买单请求数据
    buy_payload = {
        "baseAsset": base_asset,
        "quoteAsset": "USDT",
        "side": "BUY",
        "price": latest_price,
        "quantity": working_quantity_formatted,
        "paymentDetails": [{"amount": str(payment_amount_formatted), "paymentWalletType": "CARD"}]
    }
    
    print("买单请求数据:")
    print(json.dumps(buy_payload, indent=2, ensure_ascii=False))
    print("-" * 50)
    
    try:
        # 发送买单请求
        print("发送买单请求...")
        response = requests.post(url, headers=headers, json=buy_payload, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print("-" * 50)
        
        if response.status_code == 200:
            data = response.json()
            print("响应内容:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("-" * 50)
            
            if data.get('code') == '000000' and 'data' in data:
                buy_order_id = data['data']  # data 直接就是订单ID
                print(f"✅ 买单下单成功!")
                print(f"买单订单ID: {buy_order_id}")
                
                # 第二步：获取最新价格并下卖单
                print("\n=== 第二步：下卖单 ===")
                print("正在获取最新价格...")
                sell_price = get_latest_price(symbol)
                if not sell_price:
                    print("❌ 获取价格失败，使用买单价格")
                    sell_price = latest_price
                else:
                    print(f"✅ 获取到最新价格: ${sell_price}")
                
                # 构建卖单请求数据
                sell_payload = {
                    "baseAsset": base_asset,
                    "quoteAsset": "USDT",
                    "side": "SELL",
                    "price": sell_price,
                    "quantity": working_quantity_formatted,  # 使用买单计算出的数量
                    "paymentDetails": [{"amount": str(working_quantity_formatted), "paymentWalletType": "ALPHA"}]
                }
                
                print(f"卖单计算信息:")
                print(f"  卖单价格: ${sell_price}")
                print(f"  卖单数量: {working_quantity_formatted}")
                print(f"  支付类型: ALPHA")
                print("-" * 50)
                
                print("卖单请求数据:")
                print(json.dumps(sell_payload, indent=2, ensure_ascii=False))
                print("-" * 50)
                
                # 发送卖单请求
                print("发送卖单请求...")
                sell_response = requests.post(url, headers=headers, json=sell_payload, timeout=10)
                
                print(f"卖单响应状态码: {sell_response.status_code}")
                print("-" * 50)
                
                if sell_response.status_code == 200:
                    sell_data = sell_response.json()
                    print("卖单响应内容:")
                    print(json.dumps(sell_data, indent=2, ensure_ascii=False))
                    print("-" * 50)
                    
                    if sell_data.get('code') == '000000' and 'data' in sell_data:
                        sell_order_id = sell_data['data']  # data 直接就是订单ID
                        print(f"✅ 卖单下单成功!")
                        print(f"卖单订单ID: {sell_order_id}")
                        
                        # 等待5秒后查询订单状态
                        print("\n等待5秒后查询订单状态...")
                        time.sleep(5)
                        
                        # 查询买单和卖单状态
                        print("=== 查询买单状态 ===")
                        check_single_order_status(buy_order_id)
                        print("\n=== 查询卖单状态 ===")
                        check_single_order_status(sell_order_id)
                        
                    else:
                        error_code = sell_data.get('code', 'unknown')
                        error_msg = sell_data.get('message', 'unknown error')
                        print(f"❌ 卖单下单失败 - 错误代码: {error_code}, 错误信息: {error_msg}")
                else:
                    print(f"❌ 卖单HTTP请求失败 - 状态码: {sell_response.status_code}")
                    print(f"卖单响应内容: {sell_response.text}")
                
            else:
                error_code = data.get('code', 'unknown')
                error_msg = data.get('message', 'unknown error')
                print(f"❌ 买单下单失败 - 错误代码: {error_code}, 错误信息: {error_msg}")
        else:
            print(f"❌ 买单HTTP请求失败 - 状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 下单异常: {str(e)}")

def check_single_order_status(order_id):
    """查询单个订单状态"""
    print(f"查询订单状态...")
    print(f"订单ID: {order_id}")
    print("-" * 50)
    
    try:
        # 获取今天和明天的时间戳
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_start = today_start + timedelta(days=1)
        
        start_time = int(today_start.timestamp() * 1000)
        end_time = int(tomorrow_start.timestamp() * 1000)
        
        url = "https://www.binance.com/bapi/defi/v1/private/alpha-trade/order/get-order-history-web"
        params = {
            'page': 1,
            'rows': 50,
            'startTime': start_time,
            'endTime': end_time
        }
        
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Baggage': 'sentry-environment=prod,sentry-release=20250924-d1d0004c-2900,sentry-public_key=9445af76b2ba747e7b574485f2c998f7,sentry-trace_id=847f639347bc49be967b6777b03a413c,sentry-sample_rate=0.01,sentry-transaction=%2Falpha%2F%24chainSymbol%2F%24contractAddress,sentry-sampled=false',
            'Bnc-Uuid': 'e420e928-1b68-4ea2-991d-016cf1dc6f8b',
            'Clienttype': 'web',
            'Content-Type': 'application/json',
            'Cookie': 'theme=dark; bnc-uuid=e420e928-1b68-4ea2-991d-016cf1dc6f8b; _gid=GA1.2.951612344.1758819202; BNC_FV_KEY=33ea495bf3a5a79b884c5845faf9ca5e77e32ab5; ref=FEQE7YL0; lang=zh-CN; language=zh-CN; se_sd=AQPAhWVkMHTCRVWMRBgVgZZDBDA9TEQUlsN5aVEd1lcUgVVNWV4A1; se_gd=QZaVlDhAHQRA1IaRXUBMgZZAFVQcUBQUlpc5aVEd1lcUgG1NWVAP1; se_gsd=YDo2XDtWNTAgCSMrNAgnMzkECQIaBQYaV11BUl1QVllaJ1NT1; currentAccount=; logined=y; BNC-Location=CN; aws-waf-token=6a2e990f-c746-49ff-9096-b327596dd9d8:BgoAZZh3lccKAAAA:frs4tlGhn0srGqMVNdKjOUR6E1AopfP/a3uZHcPKLSFBKkQjYpgbOsjbsL/PuL7PzWy1a6xg+L7J/Hnb9L5xAb88hAOBFBDOL358HxuVvNgpN41Rqv/RGGnERAcxnm6cSRWMXbe+yCluzdyiGMFLc5oMXF4CTn0fUmdeBrXbkaCX0HYuT8/3xnMjVTs2E0cbasI=; _gcl_au=1.1.1119987010.1758819849; changeBasisTimeZone=; userPreferredCurrency=USD_USD; BNC_FV_KEY_T=101-wc4WPYO%2B3Rb7Mg3HHaWxA6MHkormTgmyD9rGzTzVOKwHQvo55bJ2lzMT%2BbZUdat95BcgrHgRyTlg0kkZjcN0DQ%3D%3D-IUTOKhlcGzLtvhtzcXChZg%3D%3D-8c; BNC_FV_KEY_EXPIRE=1758967585812; r20t=web.AE9CB0EBD5845F2CB6ADCA9667C1736A; r30t=1; cr00=22338F8E07EA42F2264AA39F47E723B7; d1og=web.1162735228.AFF6FA74AC2CB13655E400A8520AB977; r2o1=web.1162735228.F504CC1AB5DF2E043AFA12A07986B4D3; f30l=web.1162735228.BC38C5894270AA297AD43BECCDC49B3E; p20t=web.1162735228.94F8BF83B266E52880AC361D181FD0FE; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221162735228%22%2C%22first_id%22%3A%2219981cb2b079d5-0702e12ae9987a-26061951-3686400-19981cb2b08181c%22%2C%22props%22%3A%7B%22aws_waf_referrer%22%3A%22%7B%5C%22referrer%5C%22%3A%5C%22https%3A%2F%2Falpha123.uk%2F%5C%22%7D%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTk5ODFjYjJiMDc5ZDUtMDcwMmUxMmFlOTk4N2EtMjYwNjE5NTEtMzY4NjQwMC0xOTk4MWNiMmIwODE4MWMiLCIkaWRlbnRpdHlfbG9naW5faWQiOiIxMTYyNzM1MjI4In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%221162735228%22%7D%2C%22%24device_id%22%3A%2219981dc7d84bdb-0b69a1775381dc8-26061951-3686400-19981dc7d851c20%22%7D; _uetsid=a955dd009a3111f08ea99b841f36689a; _uetvid=a955d8909a3111f08c0c25e413aeab0c; _ga_3WP50LGEEC=GS2.1.s1758950440$o6$g1$t1758955852$j60$l0$h0; _ga=GA1.2.1952928982.1758819202; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Sep+27+2025+16%3A06%3A03+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202506.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=7e0430b4-07eb-4780-a2e2-48b9be3dd13c&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false',
            'csrftoken': '231efb54f001934bd7572f79523397f0',
            'device-info': 'eyJzY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsImF2YWlsYWJsZV9zY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsInN5c3RlbV92ZXJzaW9uIjoiV2luZG93cyAxMCIsImJyYW5kX21vZGVsIjoidW5rbm93biIsInN5c3RlbV9sYW5nIjoiemgtQ04iLCJ0aW1lem9uZSI6IkdNVCswODowMCIsInRpbWV6b25lT2Zmc2V0IjotNDgwLCJ1c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0MC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwibGlzdF9wbHVnaW4iOiJQREYgVmlld2VyLENocm9tZSBQREYgVmlld2VyLENocm9taXVtIFBERiBWaWV3ZXIsTWljcm9zb2Z0IEVkZ2UgUERGIFZpZXdlcixXZWJLaXQgYnVpbHQtaW4gUERGIiwiY2FudmFzX2NvZGUiOiI2NjAzODQyMyIsIndlYmdsX3ZlbmRvciI6Ikdvb2dsZSBJbmMuIChOVklESUEpIiwid2ViZ2xfcmVuZGVyZXIiOiJBTkdMRSAoTlZJRElBLCBOVklESUEgR2VGb3JjZSBSVFggMzA3MCAoMHgwMDAwMjQ4OCkgRGlyZWN0M0QxMSB2c181XzAgcHNfNV8wLCBEM0QxMSkiLCJhdWRpbyI6IjEyNC4wNDM0NzUyNzUxNjA3NCIsInBsYXRmb3JtIjoiV2luMzIiLCJ3ZWJfdGltZXpvbmUiOiJBc2lhL1NoYW5naGFpIiwiZGV2aWNlX25hbWUiOiJDaHJvbWUgVjE0MC4wLjAuMCAoV2luZG93cykiLCJmaW5nZXJwcmludCI6ImI0NzNmZjVhODA0ODU4YWQ2ZmYxYTdhNmQ2YzY0NjIzIiwiZGV2aWNlX2lkIjoiIiwicmVsYXRlZF9kZXZpY2VfaWRzIjoiIn0=',
            'fvideo-id': '33ea495bf3a5a79b884c5845faf9ca5e77e32ab5',
            'lang': 'zh-CN',
            'Priority': 'u=1, i',
            'Referer': 'https://www.binance.com/zh-CN/alpha/bsc/0xe6df05ce8c8301223373cf5b969afcb1498c5528',
            'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sentry-Trace': '847f639347bc49be967b6777b03a413c-ac242fc8bf0e51e2-0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'X-Passthrough-Token': '',
            'X-Trace-Id': '000f2190-8b35-4cb1-aa27-d62a5017a918',
            'X-Ui-Request-Trace': '000f2190-8b35-4cb1-aa27-d62a5017a918'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '000000' and 'data' in data:
                orders = data['data'].get('list', [])
                print(f"找到 {len(orders)} 个订单")
                
                # 查找我们的订单
                order_found = False
                
                for order in orders:
                    if order.get('orderId') == order_id:
                        order_found = True
                        print(f"✅ 找到订单: {order_id}")
                        print(f"订单状态: {order.get('status')}")
                        print(f"订单类型: {order.get('side')}")
                        print(f"价格: {order.get('price')}")
                        print(f"数量: {order.get('quantity')}")
                        print(f"创建时间: {order.get('createTime')}")
                        break
                
                if not order_found:
                    print(f"❌ 未找到订单: {order_id}")
                    print("可能的原因:")
                    print("1. 订单还在处理中")
                    print("2. 订单创建失败")
                    print("3. 时间范围不匹配")
                    
            else:
                error_code = data.get('code', 'unknown')
                error_msg = data.get('message', 'unknown error')
                print(f"❌ 查询订单失败 - 错误代码: {error_code}, 错误信息: {error_msg}")
        else:
            print(f"❌ 查询订单HTTP请求失败 - 状态码: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 查询订单异常: {str(e)}")

def test_sell_order():
    """测试卖单"""
    print("\n" + "=" * 50)
    print("测试卖单功能...")
    print("=" * 50)
    
    # 配置信息
    csrf_token = "231efb54f001934bd7572f79523397f0"
    symbol = "ALPHA_22USDT"
    base_asset = symbol.replace('USDT', '')
    
    print(f"开始测试卖单功能...")
    print(f"代币: {symbol}")
    print(f"基础资产: {base_asset}")
    print("-" * 50)
    
    # 获取最新价格
    print("正在获取最新价格...")
    latest_price = get_latest_price(symbol)
    if not latest_price:
        print("❌ 获取价格失败，使用默认价格")
        latest_price = 48.0
    else:
        print(f"✅ 获取到最新价格: ${latest_price}")
    
    # 计算卖出数量：amount / 最新价格
    amount = 1025
    working_quantity = amount / latest_price
    
    print(f"计算信息:")
    print(f"  金额: ${amount}")
    print(f"  最新价格: ${latest_price}")
    print(f"  卖出数量: {working_quantity:.4f}")
    print("-" * 50)
    
    # 下单URL
    url = "https://www.binance.com/bapi/defi/v1/private/alpha-trade/order/place"
    
    # 请求头
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Baggage': 'sentry-environment=prod,sentry-release=20250924-d1d0004c-2900,sentry-public_key=9445af76b2ba747e7b574485f2c998f7,sentry-trace_id=847f639347bc49be967b6777b03a413c,sentry-sample_rate=0.01,sentry-transaction=%2Falpha%2F%24chainSymbol%2F%24contractAddress,sentry-sampled=false',
        'Bnc-Uuid': 'e420e928-1b68-4ea2-991d-016cf1dc6f8b',
        'Clienttype': 'web',
        'Content-Type': 'application/json',
        'Cookie': 'theme=dark; bnc-uuid=e420e928-1b68-4ea2-991d-016cf1dc6f8b; _gid=GA1.2.951612344.1758819202; BNC_FV_KEY=33ea495bf3a5a79b884c5845faf9ca5e77e32ab5; ref=FEQE7YL0; lang=zh-CN; language=zh-CN; se_sd=AQPAhWVkMHTCRVWMRBgVgZZDBDA9TEQUlsN5aVEd1lcUgVVNWV4A1; se_gd=QZaVlDhAHQRA1IaRXUBMgZZAFVQcUBQUlpc5aVEd1lcUgG1NWVAP1; se_gsd=YDo2XDtWNTAgCSMrNAgnMzkECQIaBQYaV11BUl1QVllaJ1NT1; currentAccount=; logined=y; BNC-Location=CN; aws-waf-token=6a2e990f-c746-49ff-9096-b327596dd9d8:BgoAZZh3lccKAAAA:frs4tlGhn0srGqMVNdKjOUR6E1AopfP/a3uZHcPKLSFBKkQjYpgbOsjbsL/PuL7PzWy1a6xg+L7J/Hnb9L5xAb88hAOBFBDOL358HxuVvNgpN41Rqv/RGGnERAcxnm6cSRWMXbe+yCluzdyiGMFLc5oMXF4CTn0fUmdeBrXbkaCX0HYuT8/3xnMjVTs2E0cbasI=; _gcl_au=1.1.1119987010.1758819849; changeBasisTimeZone=; userPreferredCurrency=USD_USD; BNC_FV_KEY_T=101-wc4WPYO%2B3Rb7Mg3HHaWxA6MHkormTgmyD9rGzTzVOKwHQvo55bJ2lzMT%2BbZUdat95BcgrHgRyTlg0kkZjcN0DQ%3D%3D-IUTOKhlcGzLtvhtzcXChZg%3D%3D-8c; BNC_FV_KEY_EXPIRE=1758967585812; r20t=web.AE9CB0EBD5845F2CB6ADCA9667C1736A; r30t=1; cr00=22338F8E07EA42F2264AA39F47E723B7; d1og=web.1162735228.AFF6FA74AC2CB13655E400A8520AB977; r2o1=web.1162735228.F504CC1AB5DF2E043AFA12A07986B4D3; f30l=web.1162735228.BC38C5894270AA297AD43BECCDC49B3E; p20t=web.1162735228.94F8BF83B266E52880AC361D181FD0FE; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221162735228%22%2C%22first_id%22%3A%2219981cb2b079d5-0702e12ae9987a-26061951-3686400-19981cb2b08181c%22%2C%22props%22%3A%7B%22aws_waf_referrer%22%3A%22%7B%5C%22referrer%5C%22%3A%5C%22https%3A%2F%2Falpha123.uk%2F%5C%22%7D%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTk5ODFjYjJiMDc5ZDUtMDcwMmUxMmFlOTk4N2EtMjYwNjE5NTEtMzY4NjQwMC0xOTk4MWNiMmIwODE4MWMiLCIkaWRlbnRpdHlfbG9naW5faWQiOiIxMTYyNzM1MjI4In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%221162735228%22%7D%2C%22%24device_id%22%3A%2219981dc7d84bdb-0b69a1775381dc8-26061951-3686400-19981dc7d851c20%22%7D; _uetsid=a955dd009a3111f08ea99b841f36689a; _uetvid=a955d8909a3111f08c0c25e413aeab0c; _ga_3WP50LGEEC=GS2.1.s1758950440$o6$g1$t1758955852$j60$l0$h0; _ga=GA1.2.1952928982.1758819202; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Sep+27+2025+16%3A06%3A03+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202506.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=7e0430b4-07eb-4780-a2e2-48b9be3dd13c&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false',
        'csrftoken': csrf_token,
        'device-info': 'eyJzY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsImF2YWlsYWJsZV9zY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsInN5c3RlbV92ZXJzaW9uIjoiV2luZG93cyAxMCIsImJyYW5kX21vZGVsIjoidW5rbm93biIsInN5c3RlbV9sYW5nIjoiemgtQ04iLCJ0aW1lem9uZSI6IkdNVCswODowMCIsInRpbWV6b25lT2Zmc2V0IjotNDgwLCJ1c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0MC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwibGlzdF9wbHVnaW4iOiJQREYgVmlld2VyLENocm9tZSBQREYgVmlld2VyLENocm9taXVtIFBERiBWaWV3ZXIsTWljcm9zb2Z0IEVkZ2UgUERGIFZpZXdlcixXZWJLaXQgYnVpbHQtaW4gUERGIiwiY2FudmFzX2NvZGUiOiI2NjAzODQyMyIsIndlYmdsX3ZlbmRvciI6Ikdvb2dsZSBJbmMuIChOVklESUEpIiwid2ViZ2xfcmVuZGVyZXIiOiJBTkdMRSAoTlZJRElBLCBOVklESUEgR2VGb3JjZSBSVFggMzA3MCAoMHgwMDAwMjQ4OCkgRGlyZWN0M0QxMSB2c181XzAgcHNfNV8wLCBEM0QxMSkiLCJhdWRpbyI6IjEyNC4wNDM0NzUyNzUxNjA3NCIsInBsYXRmb3JtIjoiV2luMzIiLCJ3ZWJfdGltZXpvbmUiOiJBc2lhL1NoYW5naGFpIiwiZGV2aWNlX25hbWUiOiJDaHJvbWUgVjE0MC4wLjAuMCAoV2luZG93cykiLCJmaW5nZXJwcmludCI6ImI0NzNmZjVhODA0ODU4YWQ2ZmYxYTdhNmQ2YzY0NjIzIiwiZGV2aWNlX2lkIjoiIiwicmVsYXRlZF9kZXZpY2VfaWRzIjoiIn0=',
        'fvideo-id': '33ea495bf3a5a79b884c5845faf9ca5e77e32ab5',
        'lang': 'zh-CN',
        'Priority': 'u=1, i',
        'Referer': 'https://www.binance.com/zh-CN/alpha/bsc/0xe6df05ce8c8301223373cf5b969afcb1498c5528',
        'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sentry-Trace': '847f639347bc49be967b6777b03a413c-ac242fc8bf0e51e2-0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'X-Passthrough-Token': '',
        'X-Trace-Id': '000f2190-8b35-4cb1-aa27-d62a5017a918',
        'X-Ui-Request-Trace': '000f2190-8b35-4cb1-aa27-d62a5017a918'
    }
    
    # 构建请求数据 - 卖单
    payload = {
        "baseAsset": base_asset,
        "quoteAsset": "USDT",
        "side": "SELL",
        "price": latest_price,
        "quantity": working_quantity,
        "paymentDetails": [{"amount": str(working_quantity), "paymentWalletType": "ALPHA"}]
    }
    
    print("卖单请求数据:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("-" * 50)
    
    try:
        # 发送卖单请求
        print("发送卖单请求...")
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("响应内容:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("-" * 50)
            
            if data.get('code') == '000000' and 'data' in data:
                order_id = data['data'].get('orderId')
                print(f"✅ 卖单创建成功!")
                print(f"订单ID: {order_id}")
                
                # 等待5秒后查询订单状态
                print("\n等待5秒后查询卖单状态...")
                time.sleep(5)
                
                # 查询订单历史
                check_single_order_status(order_id)
                
            else:
                error_code = data.get('code', 'unknown')
                error_msg = data.get('message', 'unknown error')
                print(f"❌ 卖单创建失败 - 错误代码: {error_code}, 错误信息: {error_msg}")
        else:
            print(f"❌ HTTP请求失败 - 状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 卖单异常: {str(e)}")

if __name__ == "__main__":
    print("币安ALPHA单向下单测试脚本")
    print("=" * 50)
    
    # 测试买单
    print("1. 测试买单功能")
    test_single_order()
    
    # 等待10秒
    print("\n等待10秒后测试卖单...")
    time.sleep(10)
    
    # 测试卖单
    print("\n2. 测试卖单功能")
    test_sell_order()
    
    print("\n测试完成!")
