# -*- coding: utf-8 -*-
"""
测试获取账户余额接口
"""

import requests
import json
import urllib.parse
import os

def load_config():
    """从config.json加载配置"""
    config_file = "config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('csrf_token'), config.get('cookie')
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            return None, None
    else:
        print(f"❌ 配置文件不存在: {config_file}")
        return None, None

def test_balance_api():
    """测试获取账户余额接口"""
    
    # 从配置文件加载认证信息
    csrf_token, cookie = load_config()
    if not csrf_token or not cookie:
        print("❌ 无法从config.json获取认证信息，请先配置")
        return None
    
    print(f"✅ 已从config.json加载认证信息")
    print(f"   CSRF Token: {csrf_token[:20]}...")
    print(f"   Cookie长度: {len(cookie)} 字符")
    print("-" * 50)
    
    # 接口URL
    url = "https://www.binance.com/bapi/asset/v3/private/asset-service/wallet/wallet-group"
    
    # 请求头（使用私有接口，需要认证）
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Bnc-Level': '0',
        'Bnc-Location': 'CN',
        'Bnc-Time-Zone': 'Asia/Shanghai',
        'Bnc-Uuid': 'e420e928-1b68-4ea2-991d-016cf1dc6f8b',
        'Clienttype': 'web',
        'Content-Type': 'application/json',
        'Cookie': cookie,
        'csrftoken': csrf_token,
        'device-info': 'eyJzY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsImF2YWlsYWJsZV9zY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsInN5c3RlbV92ZXJzaW9uIjoiV2luZG93cyAxMCIsImJyYW5kX21vZGVsIjoidW5rbm93biIsInN5c3RlbV9sYW5nIjoiemgtQ04iLCJ0aW1lem9uZSI6IkdNVCswODowMCIsInRpbWV6b25lT2Zmc2V0IjotNDgwLCJ1c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0MC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwibGlzdF9wbHVnaW4iOiJQREYgVmlld2VyLENocm9tZSBQREYgVmlld2VyLENocm9taXVtIFBERiBWaWV3ZXIsTWljcm9zb2Z0IEVkZ2UgUERGIFZpZXdlcixXZWJLaXQgYnVpbHQtaW4gUERGIiwiY2FudmFzX2NvZGUiOiI2NjAzODQyMyIsIndlYmdsX3ZlbmRvciI6Ikdvb2dsZSBJbmMuIChOVklESUEpIiwid2ViZ2xfcmVuZGVyZXIiOiJBTkdMRSAoTlZJRElBLCBOVklESUEgR2VGb3JjZSBSVFggMzA3MCAoMHgwMDAwMjQ4OCkgRGlyZWN0M0QxMSB2c181XzAgcHNfNV8wLCBEM0QxMSkiLCJhdWRpbyI6IjEyNC4wNDM0NzUyNzUxNjA3NCIsInBsYXRmb3JtIjoiV2luMzIiLCJ3ZWJfdGltZXpvbmUiOiJBc2lhL1NoYW5naGFpIiwiZGV2aWNlX25hbWUiOiJDaHJvbWUgVjE0MC4wLjAuMCAoV2luZG93cykiLCJmaW5nZXJwcmludCI6ImI0NzNmZjVhODA0ODU4YWQ2ZmYxYTdhNmQ2YzY0NjIzIiwiZGV2aWNlX2lkIjoiIiwicmVsYXRlZF9kZXZpY2VfaWRzIjoiIn0=',
        'fvideo-id': '33ea495bf3a5a79b884c5845faf9ca5e77e32ab5',
        'fvideo-token': 'r4R1qH50iUiBSvkPxnk29hGEzOdVdsdK1PoVlT6ffvZ/MjoWsgdF2PVAMzhjjqaaYN8uQUjZfwbLIYLnvjaK+0JsjNR4eNpSUmddjCkrKVAbcD6VKcogkjBEGbgOoQrBIbaKP1/QYanSSqlXpTal5hQExJnFU0EwVWLUSs0Zr8PYXnzgfSaRTxbPy91QYSeYo=3b',
        'If-None-Match': 'W/"0fc5ed125198498515f07cb35f0655bb7"',
        'lang': 'zh-CN',
        'Priority': 'u=1, i',
        'Referer': 'https://www.binance.com/zh-CN/my/wallet/alpha',
        'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'X-Passthrough-Token': '',
        'X-Trace-Id': '14b00354-0504-4a31-a7c9-6206fcbda5cb',
        'X-Ui-Request-Trace': '14b00354-0504-4a31-a7c9-6206fcbda5cb'
    }
    
    # 请求参数
    params = {
        'quoteAsset': 'USDT',
        'needAlphaAsset': 'true',
        'needEuFuture': 'true'
    }
    
    try:
        print("正在测试获取账户余额接口...")
        print(f"请求URL: {url}")
        print(f"请求参数: {params}")
        print("-" * 50)
        
        # 发送请求
        response = requests.get(url, headers=headers, params=params)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print("-" * 50)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ 请求成功!")
                print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                # 解析并提取资金账户余额
                if data.get('code') == '000000' and 'data' in data:
                    funding_balance = None
                    alpha_balance = None
                    
                    for wallet_group in data['data']:
                        wallet_type = wallet_group.get('walletGroupType')
                        total_balance = wallet_group.get('totalBalance')
                        
                        if wallet_type == 'Funding':
                            funding_balance = total_balance
                            print(f"\n💰 资金账户余额: {funding_balance} USDT")
                        elif wallet_type == 'Alpha':
                            alpha_balance = total_balance
                            print(f"🪙 Alpha账户余额: {alpha_balance} ALPHA")
                    
                    # 返回资金账户余额
                    if funding_balance:
                        print(f"\n📊 提取的资金账户余额: {funding_balance}")
                        return funding_balance
                    else:
                        print("❌ 未找到资金账户余额")
                        return None
                else:
                    print(f"❌ API返回错误: {data.get('message', '未知错误')}")
                    return None
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"响应内容: {response.text}")
                return None
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return None

def main():
    """主函数"""
    print("=" * 60)
    print("测试获取账户余额接口")
    print("=" * 60)
    
    balance = test_balance_api()
    
    if balance:
        print(f"\n🎯 最终结果: 资金账户余额 = {balance} USDT")
    else:
        print("\n❌ 获取余额失败")

if __name__ == "__main__":
    main()
