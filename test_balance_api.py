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
        'Cookie': 'aws-waf-token=fc640539-45cf-458d-8a69-0d1535da71ab:CQoAjXBnjGUrAgAA:bT7XbrOHNuBRPY8lTle4VMnhERoNnFG+GVlFyPo2rYqmujH1xHKyo0iGz8arafjOMOzNeILuBoLmeSULJKqIaibEpL/7NiTxJPVwjRRFW3Dqc+mgiCS3qx2RoCxd2rxCu7UBZ3bmNWmnhEylgP6gDJ5GOvra1P7JSqC3yvHAnXwc52gmlNGBn9RjZzBG3vwxm3U=; theme=dark; bnc-uuid=f56aacad-cdb0-404b-a2c1-5354a641283b; language=en; se_sd=AYPUQUBEFFHExMaAFFxcgZZDACgkTERVlIdJZVkJ1ldWwCVNWVAB1; se_gd=QgLGRWwsKDICRMXtaFg8gZZAAVxkOBRVlFSJZVkJ1ldWwVFNWV0B1; se_gsd=RgMlPz9vICsiFhEoJTY0MwQpAlQIBQVRVVhHW1FTVllbAlNT1; sajssdk_2015_cross_new_user=1; BNC_FV_KEY=33b25091b9a9a8c3b1f099a25e5d4d4262f5eb5f; BNC_FV_KEY_T=101-vieiOvPpjutdXbmxKeZdER5fKQ2FJAKrjsfO5Xaxk5AnDS%2FjfCGMD%2B%2BIPtFtU5b%2BxjYm3qX%2BRzxJaGqU8a96mA%3D%3D-8YiwmX46tdoboWvS0FCdPQ%3D%3D-fe; BNC_FV_KEY_EXPIRE=1759006749292; _gid=GA1.2.574576987.1758985153; s9r1=1537FA246B772257577AA3B7C8292B2D; r20t=web.B3A5597CCFD48EB5D3EA6F7B5AFA3468; r30t=1; cr00=504AA679D0E85666CE0FA25CE7CE8854; d1og=web.1163710816.8E76FD19CFC0DA5C7B92DEA0869C3804; r2o1=web.1163710816.2923C96CDFB591824B234CF78BD61658; f30l=web.1163710816.F5462CD4E0EEDA7537439A601490D190; currentAccount=; logined=y; BNC-Location=CN; p20t=web.1163710816.B858FBC3DA178BFDA697CA5C1E177B82; lang=zh-CN; language=zh-CN; _ga_3WP50LGEEC=GS2.1.s1758985153$o1$g1$t1758985230$j45$l0$h0; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Sep+27+2025+23%3A10%3A36+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202506.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=665c2234-30d7-4a15-8b7f-18490b9fb192&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false; _ga=GA1.2.479831411.1758985153; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221163710816%22%2C%22first_id%22%3A%221998baf4fb319e9-0e7777777777778-26061951-3686400-1998baf4fb422e4%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTk5OGJhZjRmYjMxOWU5LTBlNzc3Nzc3Nzc3Nzc3OC0yNjA2MTk1MS0zNjg2NDAwLTE5OThiYWY0ZmI0MjJlNCIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjExNjM3MTA4MTYifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%221163710816%22%7D%7D',
        'csrftoken': '6a220250d134b8409dec5808e4bc9476',
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
