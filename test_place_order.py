#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 place_single_order 接口
检查缺失的请求头字段
"""

import requests
import json
import uuid
from binance_api import BinanceAPI
from logger import Logger

def compare_headers():
    """对比当前代码生成的headers和网页端完整的headers"""
    
    # 从配置或环境变量读取认证信息（需要手动设置）
    csrf_token = "YOUR_CSRF_TOKEN_HERE"  # 替换为实际的 csrf_token
    cookie = "YOUR_COOKIE_HERE"  # 替换为实际的 cookie
    
    # 网页端完整的 headers（用户提供的）
    web_headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'zh-CN,zh;q=0.9',
        'baggage': 'sentry-environment=prod,sentry-release=20251022-1b018171-3173,sentry-public_key=9445af76b2ba747e7b574485f2c998f7,sentry-trace_id=154e4e965e014b0698c50922665cb44f,sentry-sample_rate=0.01,sentry-transaction=%2Falpha%2F%24chainSymbol%2F%24contractAddress,sentry-sampled=false',
        'bnc-uuid': '63c297dc-98e7-47d8-9c22-69cf63b0a5eb',
        'clienttype': 'web',
        'content-type': 'application/json',
        'cookie': cookie,
        'csrftoken': csrf_token,
        'device-info': 'eyJzY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsImF2YWlsYWJsZV9zY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsInN5c3RlbV92ZXJzaW9uIjoiV2luZG93cyAxMCIsImJyYW5kX21vZGVsIjoidW5rbm93biIsInN5c3RlbV9sYW5nIjoiemgtQ04iLCJ0aW1lem9uZSI6IkdNVCswODowMCIsInRpbWV6b25lT2Zmc2V0IjotNDgwLCJ1c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0MS4wLjAuMCBTYWZhcmkvNTM3LjM2IiwibGlzdF9wbHVnaW4iOiJQREYgVmlld2VyLENocm9tZSBQREYgVmlld2VyLENocm9taXVtIFBERiBWaWV3ZXIsTWljcm9zb2Z0IEVkZ2UgUERGIFZpZXdlcixXZWJLaXQgYnVpbHQtaW4gUERGIiwiY2FudmFzX2NvZGUiOiI2NjAzODQyMyIsIndlYmdsX3ZlbmRvciI6Ikdvb2dsZSBJbmMuIChOVklESUEpIiwid2ViZ2xfcmVuZGVyZXIiOiJBTkdMRSAoTlZJRElBLCBOVklESUEgR2VGb3JjZSBSVFggMzA3MCAoMHgwMDAwMjQ4OCkgRGlyZWN0M0QxMSB2c181XzAgcHNfNV8wLCBEM0QxMSkiLCJhdWRpbyI6IjEyNC4wNDM0NzUyNzUxNjA3NCIsInBsYXRmb3JtIjoiV2luMzIiLCJ3ZWJfdGltZXpvbmUiOiJBc2lhL1NoYW5naGFpIiwiZGV2aWNlX25hbWUiOiJDaHJvbWUgVjE0MS4wLjAuMCAoV2luZG93cykiLCJmaW5nZXJwcmludCI6Ijg3MDY5NDc2M2YwN2I2M2MxODJkNDQzZjZiNzJlZDk5IiwiZGV2aWNlX2lkIjoiIiwicmVsYXRlZF9kZXZpY2VfaWRzIjoiIn0=',
        'fvideo-id': '33e38051d12bae91a1efbd0a56d2dc425f21a646',
        'lang': 'zh-CN',
        'origin': 'https://www.binance.com',  # ⚠️ 缺失的字段
        'priority': 'u=1, i',
        'referer': 'https://www.binance.com/zh-CN/alpha/bsc/0x81a7da4074b8e0ed51bea40f9dcbdf4d9d4832b4',
        'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sentry-trace': '154e4e965e014b0698c50922665cb44f-aaecb1a608e42c8b-0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'x-passthrough-token': '',  # ⚠️ 注意：空字符串
        'x-trace-id': '5fb7b1a4-1b7f-468a-881b-c1cc9fc7e49e',  # ⚠️ 缺失的字段
        'x-ui-request-trace': '5fb7b1a4-1b7f-468a-881b-c1cc9fc7e49e',  # ⚠️ 缺失的字段
    }
    
    # 使用代码生成的 headers
    extra_headers = {
        'device-info': web_headers['device-info'],
        'fvideo-id': web_headers['fvideo-id'],
        'bnc-uuid': web_headers['bnc-uuid'],
        'user-agent': web_headers['user-agent'],
        'baggage': web_headers['baggage'],
        'sentry-trace': web_headers['sentry-trace'],
    }
    
    logger = Logger()
    api = BinanceAPI(
        csrf_token=csrf_token,
        cookie=cookie,
        logger=logger,
        extra_headers=extra_headers
    )
    
    # 获取代码生成的 headers
    code_headers = BinanceAPI.build_request_headers(csrf_token, cookie, extra_headers)
    
    print("=" * 80)
    print("对比分析：代码生成的 headers vs 网页端完整的 headers")
    print("=" * 80)
    print("\n1. 缺失的关键字段：")
    print("-" * 80)
    
    missing_fields = []
    if 'origin' not in code_headers:
        missing_fields.append('origin')
        print("❌ origin: https://www.binance.com")
    
    if 'x-trace-id' not in code_headers:
        missing_fields.append('x-trace-id')
        print("❌ x-trace-id: (需要动态生成)")
    
    if 'x-ui-request-trace' not in code_headers:
        missing_fields.append('x-ui-request-trace')
        print("❌ x-ui-request-trace: (需要动态生成)")
    
    print("\n2. 字段名称大小写差异：")
    print("-" * 80)
    if 'Bnc-Uuid' in code_headers:
        print(f"⚠️  代码使用: 'Bnc-Uuid' = {code_headers.get('Bnc-Uuid', 'N/A')}")
        print(f"   网页使用: 'bnc-uuid' = {web_headers.get('bnc-uuid', 'N/A')}")
    
    print("\n3. 字段值差异：")
    print("-" * 80)
    
    # 检查 Referer 是否更具体
    if code_headers.get('Referer') != web_headers.get('referer'):
        print(f"⚠️  Referer 差异：")
        print(f"   代码: {code_headers.get('Referer', 'N/A')}")
        print(f"   网页: {web_headers.get('referer', 'N/A')}")
    
    # 检查 Sec-Ch-Ua 版本
    if code_headers.get('Sec-Ch-Ua') != web_headers.get('sec-ch-ua'):
        print(f"⚠️  Sec-Ch-Ua 版本差异：")
        print(f"   代码: {code_headers.get('Sec-Ch-Ua', 'N/A')}")
        print(f"   网页: {web_headers.get('sec-ch-ua', 'N/A')}")
    
    print("\n4. URL 路径检查：")
    print("-" * 80)
    code_url = "https://www.binance.com/bapi/asset/v1/private/alpha-trade/order/place"
    web_url = "https://www.binance.com/bapi/asset/v1/private/alpha-trade/order/place"
    print(f"✓  代码使用: {code_url}")
    print(f"  网页使用: {web_url}")
    if code_url == web_url:
        print("  ✅ URL 路径匹配")
    
    print("\n" + "=" * 80)
    print("总结：导致 'invalid token' 错误的可能原因")
    print("=" * 80)
    print("根据分析，以下字段缺失可能导致认证失败：")
    print("")
    print("🔴 关键缺失字段（最可能导致 invalid token）：")
    print("   1. 'Origin: https://www.binance.com' - CORS 验证需要")
    print("   2. 'X-Trace-Id' - 请求追踪ID（可能是安全验证的一部分）")
    print("   3. 'X-Ui-Request-Trace' - UI请求追踪ID")
    print("")
    print("🟡 次要问题：")
    print("   4. 'bnc-uuid' 字段大小写：代码使用 'Bnc-Uuid'，网页使用 'bnc-uuid'")
    print("   5. Sec-Ch-Ua 版本：代码是 Chrome 140，网页是 Chrome 141")
    print("   6. Referer 路径：代码是通用路径，网页是具体代币页面")
    print("")
    print("建议修复优先级：")
    print("   ✅ 高优先级：添加 Origin、X-Trace-Id、X-Ui-Request-Trace")
    print("   ⚠️  中优先级：统一 bnc-uuid 大小写")
    print("   ⚪ 低优先级：更新 Chrome 版本号")
    
    return missing_fields, code_url != web_url


def test_place_order_with_full_headers():
    """使用完整的headers测试下单接口"""
    
    # ⚠️ 需要手动设置这些值
    csrf_token = "YOUR_CSRF_TOKEN_HERE"
    cookie = "YOUR_COOKIE_HERE"
    
    if csrf_token == "YOUR_CSRF_TOKEN_HERE" or cookie == "YOUR_COOKIE_HERE":
        print("⚠️  请先设置 csrf_token 和 cookie！")
        return
    
    # 生成 trace ID
    trace_id = str(uuid.uuid4())
    
    # 完整的 headers（基于网页端）
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Clienttype': 'web',
        'Content-Type': 'application/json',
        'Cookie': cookie,
        'csrftoken': csrf_token,
        'lang': 'zh-CN',
        'Origin': 'https://www.binance.com',  # ⚠️ 关键字段
        'Priority': 'u=1, i',
        'Referer': 'https://www.binance.com/zh-CN/alpha',
        'Sec-Ch-Ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'X-Passthrough-Token': '',
        'X-Trace-Id': trace_id,  # ⚠️ 关键字段
        'X-Ui-Request-Trace': trace_id,  # ⚠️ 关键字段
    }
    
    # 添加额外的字段（如果有）
    extra_headers_dict = {
        'baggage': '',
        'bnc-uuid': '',
        'device-info': '',
        'fvideo-id': '',
        'sentry-trace': '',
    }
    
    for key, value in extra_headers_dict.items():
        if value:
            headers[key] = value
    
    # 使用新的 URL 路径
    url = "https://www.binance.com/bapi/asset/v1/private/alpha-trade/order/place"  # ⚠️ 注意路径
    
    # 测试 payload（示例）
    payload = {
        "baseAsset": "ALPHA_304",
        "quoteAsset": "USDT",
        "side": "BUY",
        "price": "1.0",
        "quantity": "100",
        "paymentDetails": [{
            "amount": "100.0",
            "paymentWalletType": "CARD"
        }]
    }
    
    print("=" * 80)
    print("测试下单接口（使用完整headers）")
    print("=" * 80)
    print(f"\nURL: {url}")
    print(f"\nHeaders (关键字段):")
    print(f"  Origin: {headers.get('Origin')}")
    print(f"  X-Trace-Id: {headers.get('X-Trace-Id')}")
    print(f"  X-Ui-Request-Trace: {headers.get('X-Ui-Request-Trace')}")
    print(f"\nPayload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '000000':
                print("\n✅ 请求成功！")
            else:
                print(f"\n❌ API错误: {data.get('message', '未知错误')}")
        else:
            print(f"\n❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ 请求异常: {str(e)}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Binance API place_single_order 接口测试工具")
    print("=" * 80)
    
    # 1. 对比分析
    print("\n[步骤 1] 对比 headers")
    missing_fields, url_mismatch = compare_headers()
    
    # 2. 测试接口（需要手动设置认证信息）
    print("\n[步骤 2] 测试接口（需要先设置认证信息）")
    print("⚠️  请编辑脚本设置 csrf_token 和 cookie 后再运行测试")
    # test_place_order_with_full_headers()
    
    print("\n" + "=" * 80)
    print("分析完成")
    print("=" * 80)

