# -*- coding: utf-8 -*-
"""
测试获取特定订单状态
"""

import requests
import json
from datetime import datetime, timedelta

def get_today_and_tomorrow_timestamps():
    """获取今天和明天0点的时间戳（毫秒）"""
    # 获取当前时间
    now = datetime.now()
    
    # 获取今天0点
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 获取明天0点
    tomorrow_start = today_start + timedelta(days=1)
    
    # 转换为毫秒时间戳
    today_timestamp = int(today_start.timestamp() * 1000)
    tomorrow_timestamp = int(tomorrow_start.timestamp() * 1000)
    
    return today_timestamp, tomorrow_timestamp

def test_specific_order(order_id):
    """测试获取特定订单状态"""
    
    # 接口URL
    url = "https://www.binance.com/bapi/defi/v1/private/alpha-trade/order/get-order-history-web"
    
    # 动态获取时间戳
    start_time, end_time = get_today_and_tomorrow_timestamps()
    
    # 请求参数 - 获取所有状态的订单
    params = {
        'page': 1,
        'rows': 1,  # 获取更多订单以便查找
        'orderStatus': 'FILLED,PARTIALLY_FILLED,EXPIRED,CANCELED,REJECTED',
        'startTime': start_time,
        'endTime': end_time
    }
    
    # 请求头（私有接口，需要认证）
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
        'Cookie': 'theme=dark; bnc-uuid=e420e928-1b68-4ea2-991d-016cf1dc6f8b; _gid=GA1.2.951612344.1758819202; BNC_FV_KEY=33ea495bf3a5a79b884c5845faf9ca5e77e32ab5; ref=FEQE7YL0; lang=zh-CN; language=zh-CN; se_sd=AQPAhWVkMHTCRVWMRBgVgZZDBDA9TEQUlsN5aVEd1lcUgVVNWV4A1; se_gd=QZaVlDhAHQRA1IaRXUBMgZZAFVQcUBQUlpc5aVEd1lcUgG1NWVAP1; se_gsd=YDo2XDtWNTAgCSMrNAgnMzkECQIaBQYaV11BUl1QVllaJ1NT1; currentAccount=; logined=y; BNC-Location=CN; aws-waf-token=6a2e990f-c746-49ff-9096-b327596dd9d8:BgoAZZh3lccKAAAA:frs4tlGhn0srGqMVNdKjOUR6E1AopfP/a3uZHcPKLSFBKkQjYpgbOsjbsL/PuL7PzWy1a6xg+L7J/Hnb9L5xAb88hAOBFBDOL358HxuVvNgpN41Rqv/RGGnERAcxnm6cSRWMXbe+yCluzdyiGMFLc5oMXF4CTn0fUmdeBrXbkaCX0HYuT8/3xnMjVTs2E0cbasI=; _gcl_au=1.1.1119987010.1758819849; changeBasisTimeZone=; userPreferredCurrency=USD_USD; _uetsid=a955dd009a3111f08ea99b841f36689a; _uetvid=a955d8909a3111f08c0c25e413aeab0c; BNC_FV_KEY_T=101-wc4WPYO%2B3Rb7Mg3HHaWxA6MHkormTgmyD9rGzTzVOKwHQvo55bJ2lzMT%2BbZUdat95BcgrHgRyTlg0kkZjcN0DQ%3D%3D-IUTOKhlcGzLtvhtzcXChZg%3D%3D-8c; BNC_FV_KEY_EXPIRE=1758967585812; r20t=web.AE9CB0EBD5845F2CB6ADCA9667C1736A; r30t=1; cr00=22338F8E07EA42F2264AA39F47E723B7; d1og=web.1162735228.AFF6FA74AC2CB13655E400A8520AB977; r2o1=web.1162735228.F504CC1AB5DF2E043AFA12A07986B4D3; f30l=web.1162735228.BC38C5894270AA297AD43BECCDC49B3E; p20t=web.1162735228.94F8BF83B266E52880AC361D181FD0FE; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221162735228%22%2C%22first_id%22%3A%2219981cb2b079d5-0702e12ae9987a-26061951-3686400-19981cb2b08181c%22%2C%22props%22%3A%7B%22aws_waf_referrer%22%3A%22%7B%5C%22referrer%5C%22%3A%5C%22https%3A%2F%2Falpha123.uk%2F%5C%22%7D%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTk5ODFjYjJiMDc5ZDUtMDcwMmUxMmFlOTk4N2EtMjYwNjE5NTEtMzY4NjQwMC0xOTk4MWNiMmIwODE4MWMiLCIkaWRlbnRpdHlfbG9naW5faWQiOiIxMTYyNzM1MjI4In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%221162735228%22%7D%2C%22%24device_id%22%3A%2219981dc7d84bdb-0b69a1775381dc8-26061951-3686400-19981dc7d851c20%22%7D; _uetsid=a955dd009a3111f08ea99b841f36689a; _uetvid=a955d8909a3111f08c0c25e413aeab0c; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Sep+27+2025+14%3A21%3A39+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202506.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=7e0430b4-07eb-4780-a2e2-48b9be3dd13c&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false; _ga=GA1.1.1952928982.1758819202; _ga_3WP50LGEEC=GS2.1.s1758950440$o6$g1$t1758954356$j60$l0$h0',
        'csrftoken': '231efb54f001934bd7572f79523397f0',
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
    
    try:
        print(f"正在查找订单ID: {order_id}")
        print(f"请求URL: {url}")
        print(f"请求参数: {params}")
        
        # 显示时间范围
        start_dt = datetime.fromtimestamp(start_time / 1000)
        end_dt = datetime.fromtimestamp(end_time / 1000)
        print(f"查询时间范围: {start_dt.strftime('%Y-%m-%d %H:%M:%S')} 到 {end_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        # 发送请求
        response = requests.get(url, headers=headers, params=params)
        
        print(f"响应状态码: {response.status_code}")
        print("-" * 50)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ 请求成功!")
                print(f"完整响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                # 解析并查找特定订单
                if data.get('code') == '000000' and 'data' in data:
                    orders = data.get('data', [])
                    print(f"📊 获取到 {len(orders)} 条订单记录")
                    
                    # 查找目标订单
                    target_order = None
                    for order in orders:
                        if str(order.get('orderId')) == str(order_id):
                            target_order = order
                            break
                    
                    if target_order:
                        print(f"\n🎯 找到目标订单 {order_id}:")
                        print(f"  订单ID: {target_order.get('orderId')}")
                        print(f"  交易对: {target_order.get('symbol')}")
                        print(f"  方向: {target_order.get('side')}")
                        print(f"  类型: {target_order.get('type')}")
                        print(f"  状态: {target_order.get('status')}")
                        print(f"  价格: {target_order.get('price')} USDT")
                        print(f"  数量: {target_order.get('origQty')}")
                        print(f"  已成交数量: {target_order.get('executedQty')}")
                        print(f"  平均成交价: {target_order.get('avgPrice')} USDT")
                        print(f"  累计成交金额: {target_order.get('cumQuote')} USDT")
                        print(f"  手续费: {target_order.get('commission')}")
                        print(f"  基础资产: {target_order.get('baseAsset')}")
                        print(f"  计价资产: {target_order.get('quoteAsset')}")
                        print(f"  有效期类型: {target_order.get('timeInForce')}")
                        
                        # 转换时间戳为正常时间
                        timestamp = target_order.get('time')
                        if timestamp:
                            dt = datetime.fromtimestamp(timestamp / 1000)
                            print(f"  创建时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        update_time = target_order.get('updateTime')
                        if update_time:
                            dt = datetime.fromtimestamp(update_time / 1000)
                            print(f"  更新时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        return target_order
                    else:
                        print(f"\n❌ 未找到订单ID {order_id}")
                        print("\n📋 当前订单列表:")
                        for i, order in enumerate(orders, 1):
                            order_time = datetime.fromtimestamp(int(order.get('time', 0))/1000) if order.get('time') else '未知'
                            print(f"  {i}. ID={order.get('orderId')}, 状态={order.get('status')}, 方向={order.get('side')}, 时间={order_time.strftime('%H:%M:%S')}")
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
    print("测试获取特定订单状态")
    print("=" * 60)
    
    # 测试订单ID
    order_id = "152959615"
    
    result = test_specific_order(order_id)
    
    if result:
        print(f"\n🎯 测试完成，找到订单 {order_id}")
    else:
        print(f"\n❌ 测试失败，未找到订单 {order_id}")

if __name__ == "__main__":
    main()
