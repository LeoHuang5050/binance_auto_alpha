# -*- coding: utf-8 -*-
"""
测试获取账户余额接口
"""

import requests
import json
import urllib.parse

def test_balance_api():
    """测试获取账户余额接口"""
    
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
        'Cookie': 'userPreferredCurrency=USD_USD; theme=dark; bnc-uuid=e3d34cdc-dad4-41a8-b8c3-f2042799329b; ref=853138814; se_sd=xcRAgQl8UQVDVUSUXDQNgZZVFAFEBEZVlEMRdVER1ldVAVFNWVcD1; se_gsd=dyM0BUdhNi0gGVoqJTIhMDUxVRQNAgAOV1hBVFdXVllbHVNT1; BNC_FV_KEY=333f598b3f63a44eb8c939a4ca9752d45f2bc0e5; BNC_FV_KEY_T=101-Wv6t2mMLlzxIsEobHy79i5Alwpyu0tQYr6gK90EjKXKnpkMGWHZ3vicdglF8aJoVi1C6WkZgc6lRoxBOkQcljw%3D%3D-%2BGc1VMAMsngUkxziTCpwTw%3D%3D-28; BNC_FV_KEY_EXPIRE=1758995166760; aws-waf-token=f51c20bf-ca17-46c4-a1ae-8170a88eb813:AQoAoKZRQv8hAAAA:R7fAvv+xxRzDj4pIUwIBDqCn8VA4hJ6Z6LJVFUzDaMzUrcySSsljvsGIryv7cm843FSBkZWXtgTAZHUD8u4uPF+jWUZSxLABF841Cmhf/svwJt2WcyBcRBvNx/+j9dGzWkwEZf9YcggWuuIy+ePkrzSl7MuUyftFZeIbY239awqkQAKQpHvgfwZcpT+FSUi39e0=; r20t=web.030CD6B8AB22028A00532CD17E6C7256; r30t=1; cr00=7AB1895BC94017CA3D7179499671F745; d1og=web.1163565041.43F3984342CB03749DD4ED58A82FE68A; r2o1=web.1163565041.26D890BFFBC74626F1969F23D02EB745; f30l=web.1163565041.C462167733210C87A8BF6CEB6125D28E; currentAccount=; logined=y; BNC-Location=CN; p20t=web.1163565041.894E9AF3B04AA8E28E02AC4461DFFC06; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221163565041%22%2C%22first_id%22%3A%22190f2fcd817165b-0918290424cd5c8-26001f51-3686400-190f2fcd8181c32%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkwZjJmY2Q4MTcxNjViLTA5MTgyOTA0MjRjZDVjOC0yNjAwMWY1MS0zNjg2NDAwLTE5MGYyZmNkODE4MWMzMiIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjExNjM1NjUwNDEifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%221163565041%22%7D%2C%22%24device_id%22%3A%22190f2fcd817165b-0918290424cd5c8-26001f51-3686400-190f2fcd8181c32%22%7D; OptanonAlertBoxClosed=2025-09-27T12:21:49.486Z; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Sep+27+2025+20%3A48%3A00+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202506.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=ad2bcea7-7b88-4559-ad67-d83007ad689d&interactionCount=2&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false&intType=1&geolocation=JP%3B13',
        'csrftoken': '0a9039efb796b346900e3669e479ddb5',
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
