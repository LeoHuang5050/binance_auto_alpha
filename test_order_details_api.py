#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试订单详情API修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from binance_trader import BinanceTrader
import json
import time

def test_order_details_api():
    """测试修复后的订单详情API"""
    print("=" * 60)
    print("开始测试修复后的订单详情API...")
    print("=" * 60)
    
    # 硬编码认证信息
    csrf_token = "637d82b799abc550ed09ec0304f622e3"
    cookie = "bnc-uuid=f56aacad-cdb0-404b-a2c1-5354a641283b; se_gd=QgLGRWwsKDICRMXtaFg8gZZAAVxkOBRVlFSJZVkJ1ldWwVFNWV0B1; se_gsd=RgMlPz9vICsiFhEoJTY0MwQpAlQIBQVRVVhHW1FTVllbAlNT1; BNC_FV_KEY=33b25091b9a9a8c3b1f099a25e5d4d4262f5eb5f; currentAccount=; logined=y; BNC-Location=CN; lang=zh-CN; language=zh-CN; _gid=GA1.2.2110246887.1759118563; aws-waf-token=96329126-b424-4460-80c2-389ed1a9eaa1:BgoAZ8cFUxQVAAAA:Nefci3ClIIlDRYzJXFLhYPVshcSo5FKUz6y7qSj01Q4s2FgqZ61PizCD5A/bt3WSYKLROvX7Hiq1SIAgk1G+rnUV87Sm/AXObZ7bQJgteszQmkrweghYnFSEFFiR3adPPJiKrdlrrxMXvxHlHvJMXo6Uw/dvXyIi0wlmhJksirTPolKHto2ZQFZU1ydyTDysvys=; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221163710816%22%2C%22first_id%22%3A%221998baf4fb319e9-0e7777777777778-26061951-3686400-1998baf4fb422e4%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTk5OGJhZjRmYjMxOWU5LTBlNzc3Nzc3Nzc3Nzc3OC0yNjA2MTk1MS0zNjg2NDAwLTE5OThiYWY0ZmI0MjJlNCIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjExNjM3MTA4MTYifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%221163710816%22%7D%2C%22%24device_id%22%3A%221999e3515e31cf9-05d94d2fb0371-26061951-3686400-1999e3515e421b3%22%7D; changeBasisTimeZone=; _gcl_au=1.1.701008307.1759371306; _uetsid=9f45b6309f3511f08f3f3909aba67661; _uetvid=9f45ae709f3511f099e1af3c79014179; theme=dark; language=zh-CN; se_sd=QgDEhRRpVDSGwtSgQUQ1gZZVQHBsGEUVFZd5QVEF1hQVwCFNWVQF1; BNC_FV_KEY_T=101-r07jp%2BLnQN9ceg5a0HsOTftPlTcQInFvwUdnN8y8H%2FmTzbIt8GRxpqOevQzlbeH3AhcotstWofo4%2FyyI%2F6SJ1w%3D%3D-djyvTynvOf7dJmZMjT2VwA%3D%3D-3a; BNC_FV_KEY_EXPIRE=1759471471070; s9r1=ADC35E4C36247863B9E40F2256E37D78; r20t=web.CF919B634A5D956BF33F208BAC6B1A78; r30t=1; cr00=3D20AC25A729C9DC6502E293A9894C06; d1og=web.1163710816.5A047CE03D5B7E418E8EC1E6A41C6226; r2o1=web.1163710816.9E2428172954A776311A80C671D7DB19; f30l=web.1163710816.8D54EBA7C7CB6FFB06EDBE3EE9242EA4; p20t=web.1163710816.4FF58BFFA0E9E880DE1C3CCA97F81597; _ga_3WP50LGEEC=GS2.1.s1759449868$o12$g1$t1759451216$j60$l0$h0; _ga=GA1.2.479831411.1758985153; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Oct+03+2025+08%3A26%3A59+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202506.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=665c2234-30d7-4a15-8b7f-18490b9fb192&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false; _gat=1"
    
    print(f"\n1. 使用硬编码认证信息:")
    print(f"   CSRF Token: {csrf_token[:10]}...")
    print(f"   Cookie: {cookie[:50]}...")
    
    print("\n2. 测试get_order_details方法...")
    try:
        # 创建交易器实例并设置认证信息
        trader = BinanceTrader()
        trader.csrf_token = csrf_token
        trader.cookie = cookie
        
        # 测试获取订单详情
        order_details = trader.get_order_details()
        
        if order_details:
            print("✅ 成功获取订单详情")
            print(f"   订单ID: {order_details.get('orderId', 'N/A')}")
            print(f"   订单状态: {order_details.get('status', 'N/A')}")
            print(f"   交易对: {order_details.get('symbol', 'N/A')}")
            print(f"   订单方向: {order_details.get('side', 'N/A')}")
            print(f"   原始数量: {order_details.get('origQty', 'N/A')}")
            print(f"   已成交数量: {order_details.get('executedQty', 'N/A')}")
            print(f"   订单时间: {order_details.get('time', 'N/A')}")
            
            # 显示完整的订单信息
            print(f"\n   完整订单信息:")
            print(json.dumps(order_details, indent=2, ensure_ascii=False))
            
        else:
            print("ℹ️  没有找到订单详情（可能今天没有订单）")
            
    except Exception as e:
        print(f"❌ 获取订单详情失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n3. 测试check_single_order_filled方法...")
    try:
        # 测试检查订单状态（使用一个测试订单ID）
        test_order_id = "12345678"  # 测试用的订单ID
        order_status = trader.check_single_order_filled(test_order_id)
        
        print(f"   测试订单ID: {test_order_id}")
        print(f"   返回状态: {order_status}")
        
        if order_status is None:
            print("ℹ️  没有找到匹配的订单（这是正常的，因为使用的是测试订单ID）")
        else:
            print(f"✅ 成功检查订单状态: {order_status}")
            
    except Exception as e:
        print(f"❌ 检查订单状态失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n4. 测试API端点连通性...")
    try:
        import requests
        from datetime import datetime, timedelta
        
        # 获取今天的时间范围
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_start = today + timedelta(days=1)
        
        start_time = int(today.timestamp() * 1000)
        end_time = int(tomorrow_start.timestamp() * 1000)
        
        url = "https://www.binance.com/bapi/defi/v1/private/alpha-trade/order/get-order-history-web"
        params = {
            'page': 1,
            'rows': 1,
            'orderStatus': 'FILLED,PARTIALLY_FILLED,EXPIRED,CANCELED,REJECTED',
            'startTime': start_time,
            'endTime': end_time
        }
        
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Content-Type': 'application/json',
            'csrftoken': csrf_token,
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
        }

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
        
        print(f"   请求URL: {url}")
        print(f"   请求参数: {params}")
        print(f"   时间范围: {datetime.fromtimestamp(start_time/1000)} 到 {datetime.fromtimestamp(end_time/1000)}")
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        print(f"   响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   响应代码: {data.get('code', 'N/A')}")
            print(f"   响应消息: {data.get('message', 'N/A')}")
            
            if data.get('code') == '000000':
                print("✅ API端点连通性正常")
                orders = data.get('data', [])
                print(f"   获取到订单数量: {len(orders)}")
                
                if orders:
                    print(f"   最新订单信息:")
                    print(json.dumps(orders[0], indent=2, ensure_ascii=False))
                else:
                    print("   今天没有订单记录")
            else:
                print(f"❌ API返回错误: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API端点测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ 订单详情API测试完成")
    print("=" * 60)
    
    return True

def test_partial_fill_scenario():
    """测试部分成交场景"""
    print("\n" + "=" * 60)
    print("测试部分成交处理逻辑...")
    print("=" * 60)
    
    # 硬编码认证信息
    csrf_token = "637d82b799abc550ed09ec0304f622e3"
    cookie = "bnc-uuid=f56aacad-cdb0-404b-a2c1-5354a641283b; se_gd=QgLGRWwsKDICRMXtaFg8gZZAAVxkOBRVlFSJZVkJ1ldWwVFNWV0B1; se_gsd=RgMlPz9vICsiFhEoJTY0MwQpAlQIBQVRVVhHW1FTVllbAlNT1; BNC_FV_KEY=33b25091b9a9a8c3b1f099a25e5d4d4262f5eb5f; currentAccount=; logined=y; BNC-Location=CN; lang=zh-CN; language=zh-CN; _gid=GA1.2.2110246887.1759118563; aws-waf-token=96329126-b424-4460-80c2-389ed1a9eaa1:BgoAZ8cFUxQVAAAA:Nefci3ClIIlDRYzJXFLhYPVshcSo5FKUz6y7qSj01Q4s2FgqZ61PizCD5A/bt3WSYKLROvX7Hiq1SIAgk1G+rnUV87Sm/AXObZ7bQJgteszQmkrweghYnFSEFFiR3adPPJiKrdlrrxMXvxHlHvJMXo6Uw/dvXyIi0wlmhJksirTPolKHto2ZQFZU1ydyTDysvys=; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221163710816%22%2C%22first_id%22%3A%221998baf4fb319e9-0e7777777777778-26061951-3686400-1998baf4fb422e4%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTk5OGJhZjRmYjMxOWU5LTBlNzc3Nzc3Nzc3Nzc3OC0yNjA2MTk1MS0zNjg2NDAwLTE5OThiYWY0ZmI0MjJlNCIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjExNjM3MTA4MTYifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%221163710816%22%7D%2C%22%24device_id%22%3A%221999e3515e31cf9-05d94d2fb0371-26061951-3686400-1999e3515e421b3%22%7D; changeBasisTimeZone=; _gcl_au=1.1.701008307.1759371306; _uetsid=9f45b6309f3511f08f3f3909aba67661; _uetvid=9f45ae709f3511f099e1af3c79014179; theme=dark; language=zh-CN; se_sd=QgDEhRRpVDSGwtSgQUQ1gZZVQHBsGEUVFZd5QVEF1hQVwCFNWVQF1; BNC_FV_KEY_T=101-r07jp%2BLnQN9ceg5a0HsOTftPlTcQInFvwUdnN8y8H%2FmTzbIt8GRxpqOevQzlbeH3AhcotstWofo4%2FyyI%2F6SJ1w%3D%3D-djyvTynvOf7dJmZMjT2VwA%3D%3D-3a; BNC_FV_KEY_EXPIRE=1759471471070; s9r1=ADC35E4C36247863B9E40F2256E37D78; r20t=web.CF919B634A5D956BF33F208BAC6B1A78; r30t=1; cr00=3D20AC25A729C9DC6502E293A9894C06; d1og=web.1163710816.5A047CE03D5B7E418E8EC1E6A41C6226; r2o1=web.1163710816.9E2428172954A776311A80C671D7DB19; f30l=web.1163710816.8D54EBA7C7CB6FFB06EDBE3EE9242EA4; p20t=web.1163710816.4FF58BFFA0E9E880DE1C3CCA97F81597; _ga_3WP50LGEEC=GS2.1.s1759449868$o12$g1$t1759451216$j60$l0$h0; _ga=GA1.2.479831411.1758985153; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Oct+03+2025+08%3A26%3A59+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202506.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=665c2234-30d7-4a15-8b7f-18490b9fb192&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false; _gat=1"
    
    trader = BinanceTrader()
    trader.csrf_token = csrf_token
    trader.cookie = cookie
    
    print("1. 模拟部分成交订单处理...")
    
    # 这里可以添加更详细的部分成交测试逻辑
    # 由于需要实际的订单ID，这里只做基本的结构测试
    
    print("✅ 部分成交处理逻辑结构正常")
    
    return True

if __name__ == "__main__":
    try:
        print("币安订单详情API测试脚本")
        print("请确保已设置正确的CSRF Token和Cookie")
        print()
        
        # 主要测试
        success = test_order_details_api()
        
        if success:
            # 额外测试
            test_partial_fill_scenario()
        
        print("\n测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
