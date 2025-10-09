#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试 place_single_order 方法的返回值
模拟特定的响应数据
"""

import json
from datetime import datetime
from unittest.mock import patch, MagicMock

class MockBinanceTrader:
    def __init__(self):
        self.tokens = {}
        self.cookie = "test_cookie"
        self.csrf_token = "test_csrf_token"
        
    def log_message(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def log_trade_detail(self, trade_detail):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 交易详情记录:")
        print(f"  状态: {trade_detail['status']}")
        if 'order_id' in trade_detail:
            print(f"  订单ID: {trade_detail['order_id']}")
        if 'error' in trade_detail:
            print(f"  错误: {trade_detail['error']}")

    def place_single_order(self, symbol, price, side, custom_quantity=None):
        """创建单向订单（买单或卖单）"""
        # 记录交易详情
        trade_detail = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': symbol,
            'side': side,
            'price': price,
            'custom_quantity': custom_quantity,
            'status': 'started'
        }
        
        try:
            url = "https://www.binance.com/bapi/defi/v1/private/alpha-trade/order/place"
            
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Content-Type': 'application/json',
                'Cookie': self.cookie,
                'csrftoken': self.csrf_token,
            }
            
            # 计算数量：KOGE使用1025，其他代币使用1030
            base_amount = 1025 if symbol == "ALPHA_22USDT" else 1030
            
            if custom_quantity is not None:
                # 使用自定义数量
                working_quantity = custom_quantity
            else:
                # 使用基础金额计算
                working_quantity = base_amount / price
            
            # KOGE代币截取到4位小数，其他代币截取到2位小数
            if symbol == "ALPHA_22USDT":
                working_quantity_formatted = int(working_quantity * 10000) / 10000  # 截断到4位小数
            else:
                working_quantity_formatted = int(working_quantity * 100) / 100  # 截断到2位小数
            
            # 计算支付金额
            if side == "BUY":
                payment_amount = working_quantity_formatted * price
                # 只有当小数位数超过8位时才截取
                if len(str(payment_amount).split('.')[-1]) > 8:
                    payment_amount_formatted = int(payment_amount * 100000000) / 100000000  # 截断到8位小数
                else:
                    payment_amount_formatted = payment_amount
                payment_wallet_type = "CARD"

            else:  # SELL
                # 卖单直接使用上一个买单的份额，但需要考虑手续费
                if symbol in self.tokens and self.tokens[symbol].get('last_buy_quantity', 0) > 0:
                    # 获取上一个买单的份额
                    last_buy_quantity = self.tokens[symbol]['last_buy_quantity']
                    
                    # 计算手续费（0.01%）
                    fee_rate = 0.0001  # 0.01%
                    fee_amount = last_buy_quantity * fee_rate
                    
                    # 扣除手续费后的实际可卖份额
                    working_quantity_formatted = max(0, last_buy_quantity - fee_amount)
                    
                    # 按照代币类型截断到正确的小数位数
                    if symbol == "ALPHA_22USDT":
                        working_quantity_formatted = int(working_quantity_formatted * 10000) / 10000  # 截断到4位小数
                    else:
                        working_quantity_formatted = int(working_quantity_formatted * 100) / 100  # 截断到2位小数
                    
                    self.log_message(f"代币份额: {working_quantity_formatted}")
                else:
                    # 如果没有上一个买单份额，则使用当前计算的份额并扣除手续费
                    fee_rate = 0.0001  # 0.01%
                    fee_amount = working_quantity_formatted * fee_rate
                    working_quantity_formatted = max(0, working_quantity_formatted - fee_amount)
                    
                    # 按照代币类型截断到正确的小数位数
                    if symbol == "ALPHA_22USDT":
                        working_quantity_formatted = int(working_quantity_formatted * 10000) / 10000  # 截断到4位小数
                    else:
                        working_quantity_formatted = int(working_quantity_formatted * 100) / 100  # 截断到2位小数
                    
                    self.log_message(f"没有找到上一个买单份额，使用当前计算份额并扣除手续费: {working_quantity_formatted}")
                
                # 卖单的支付金额就是代币数量
                payment_amount = working_quantity_formatted
                payment_amount_formatted = working_quantity_formatted
                payment_wallet_type = "ALPHA"
            
            # 构建请求数据
            # 确保支付金额使用正确的精度（8位小数）
            if side == "BUY":
                amount_str = f"{payment_amount_formatted:.8f}"
            else:
                amount_str = str(payment_amount_formatted)
            
            payload = {
                "baseAsset": symbol.replace('USDT', ''),
                "quoteAsset": "USDT",
                "side": side,
                "price": price,
                "quantity": working_quantity_formatted,
                "paymentDetails": [{"amount": amount_str, "paymentWalletType": payment_wallet_type}]
            }
            
            # 记录请求参数
            trade_detail['request_params'] = {
                'url': url,
                'headers': headers,
                'payload': payload
            }
            
            # 模拟响应数据
            response_data = {
                "code": "000002",
                "message": "price*quantity must be the same as sum(paymentDetail.amount)",
                "messageDetail": None,
                "data": None,
                "success": False
            }
            
            # 记录响应信息
            trade_detail['response'] = {
                'status_code': 200,
                'headers': {},
                'text': json.dumps(response_data),
                'json': response_data
            }
            
            print(f"模拟响应数据: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            if 200 == 200:  # 模拟HTTP 200状态码
                data = response_data
                
                if data.get('code') == '000000' and 'data' in data:
                    # 记录成功信息
                    trade_detail['status'] = 'success'
                    trade_detail['order_id'] = data['data']
                    
                    # 买单成功后立即保存份额
                    if side == "BUY" and symbol in self.tokens:
                        self.tokens[symbol]['last_buy_quantity'] = working_quantity_formatted
                        self.log_message(f"已保存买单份额: {working_quantity_formatted}")

                    # 记录交易详情到文件
                    self.log_trade_detail(trade_detail)
                    
                    return data['data']  # 直接返回订单ID
                else:
                    # 记录失败信息
                    trade_detail['status'] = 'failed'
                    trade_detail['error'] = {
                        'code': data.get('code', 'unknown'),
                        'message': data.get('message', '未知错误')
                    }
                    
                    # 打印错误信息
                    error_code = data.get('code', 'unknown')
                    error_message = data.get('message', '未知错误')
                    self.log_message(f"{side}单下单失败 - 错误代码: {error_code}, 错误信息: {error_message}")
                    
                    # 记录交易详情到文件
                    self.log_trade_detail(trade_detail)
                    
                    # 控制台打印下单失败信息，方便排查
                    error_info = f"""
                                    === {side}单下单失败 ===
                                    代币: {symbol}
                                    价格: {price}
                                    数量: {working_quantity_formatted}
                                    支付金额: {payment_amount_formatted}
                                    错误代码: {error_code}
                                    错误信息: {error_message}
                                    请求数据:
                                    {json.dumps(payload, indent=2, ensure_ascii=False)}
                                    {'=' * 50}
                                """
                    print(error_info)
                    
                    return None
            else:
                # 记录HTTP错误
                trade_detail['status'] = 'http_error'
                trade_detail['error'] = {
                    'status_code': 200,
                    'message': f"HTTP状态码: 200"
                }
                
                error_msg = f"{side}单下单请求失败 - HTTP状态码: 200"
                self.log_message(error_msg)
                
                # 记录交易详情到文件
                self.log_trade_detail(trade_detail)
                
                return None
                
        except Exception as e:
            # 记录异常错误
            trade_detail['status'] = 'exception'
            trade_detail['error'] = {
                'message': str(e),
                'type': type(e).__name__
            }
            
            error_msg = f"{side}单下单异常: {str(e)}"
            self.log_message(error_msg)
            
            # 记录交易详情到文件
            self.log_trade_detail(trade_detail)
            
            return None

def test_place_single_order_response():
    """测试 place_single_order 方法的返回值"""
    print("=" * 60)
    print("测试 place_single_order 方法返回值")
    print("=" * 60)
    
    trader = MockBinanceTrader()
    
    # 测试参数
    symbol = "ALPHA_373USDT"
    price = 0.2236
    side = "BUY"
    
    print(f"\n测试参数:")
    print(f"  代币: {symbol}")
    print(f"  价格: {price}")
    print(f"  方向: {side}")
    print(f"  基础金额: {1025 if symbol == 'ALPHA_22USDT' else 1030}")
    
    # 计算预期值
    base_amount = 1025 if symbol == "ALPHA_22USDT" else 1030
    working_quantity = base_amount / price
    working_quantity_formatted = int(working_quantity * 100) / 100  # 截断到2位小数
    payment_amount = working_quantity_formatted * price
    
    print(f"\n计算值:")
    print(f"  工作数量: {working_quantity}")
    print(f"  格式化数量: {working_quantity_formatted}")
    print(f"  支付金额: {payment_amount}")
    
    # 调用方法
    print(f"\n调用 place_single_order 方法...")
    result = trader.place_single_order(symbol, price, side)
    
    # 检查返回值
    print(f"\n返回值检查:")
    print(f"  返回值: {result}")
    print(f"  返回值类型: {type(result)}")
    print(f"  是否为 None: {result is None}")
    
    if result is None:
        print("✅ 测试通过：方法正确返回 None")
    else:
        print("❌ 测试失败：方法应该返回 None 但返回了其他值")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_place_single_order_response()
