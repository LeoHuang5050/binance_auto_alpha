#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试取消所有委托功能
Test Cancel All Orders
"""

import requests
import json
import os

def load_config():
    """加载配置文件"""
    config_file = "config.json"
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('csrf_token'), config.get('cookie')
    except Exception as e:
        print(f"加载配置文件失败: {e}")
    return None, None

def test_cancel_all_orders():
    """测试取消所有委托"""
    print("=== 测试取消所有委托 ===")
    
    # 加载认证信息
    csrf_token, cookie = load_config()
    if not csrf_token or not cookie:
        print("❌ 请先设置认证信息")
        return False
    
    print(f"✅ 已加载认证信息")
    print(f"CSRF Token: {csrf_token[:10]}...")
    print(f"Cookie: {cookie[:50]}...")
    
    # 请求URL
    url = "https://www.binance.com/bapi/defi/v1/private/alpha-trade/order/cancel-all"
    
    # 请求头
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Baggage': 'sentry-environment=prod,sentry-release=20250924-d1d0004c-2900,sentry-public_key=9445af76b2ba747e7b574485f2c998f7,sentry-trace_id=847f639347bc49be967b6777b03a413c,sentry-sample_rate=0.01,sentry-transaction=%2Falpha%2F%24chainSymbol%2F%24contractAddress,sentry-sampled=false',
        'Bnc-Uuid': 'e420e928-1b68-4ea2-991d-016cf1dc6f8b',
        'Clienttype': 'web',
        'Content-Type': 'application/json',
        'Cookie': cookie,
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
    
    # 请求数据（空payload）
    payload = {}
    
    print(f"\n📤 发送请求:")
    print(f"URL: {url}")
    print(f"Method: POST")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # 发送请求
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        print(f"\n📥 响应信息:")
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应内容: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('code') == '000000' and data.get('success') == True:
                print("✅ 取消所有委托成功!")
                return True
            else:
                print(f"❌ 取消委托失败 - 错误代码: {data.get('code')}, 错误信息: {data.get('message')}")
                return False
        else:
            print(f"❌ 请求失败 - HTTP状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {str(e)}")
        return False

def main():
    """主函数"""
    print("币安ALPHA交易 - 取消所有委托测试")
    print("=" * 50)
    
    success = test_cancel_all_orders()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试完成 - 成功")
    else:
        print("💥 测试完成 - 失败")

if __name__ == "__main__":
    main()
