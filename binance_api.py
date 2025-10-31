#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
币安API接口模块
Binance API Module for Binance Auto Trade System
"""

import requests
import json
from decimal import Decimal, ROUND_DOWN
from logger import Logger


class BinanceAPI:
    """币安API接口类 - 负责与币安API进行交互"""
    
    def __init__(self, base_url=None, csrf_token=None, cookie=None, logger=None, extra_headers=None):
        """
        初始化币安API接口
        
        Args:
            base_url: API基础URL
            csrf_token: CSRF令牌
            cookie: Cookie字符串
            logger: Logger实例，用于记录日志
            extra_headers: 额外的 header 字段（device-info, fvideo-id 等）
        """
        self.base_url = base_url or "https://www.binance.com/bapi/defi/v1/public/alpha-trade"
        self.csrf_token = csrf_token
        self.cookie = cookie
        self.logger = logger or Logger()
        self.extra_headers = extra_headers or {}
    
    def get_token_price(self, symbol):
        """
        获取代币价格（使用聚合成交数据接口）
        
        Args:
            symbol: 代币符号，如 "ALPHA_1USDT"
            
        Returns:
            dict: 包含价格和交易信息的字典，失败返回None
                {
                    'price': str,  # 最新成交价格
                    'quantity': str,  # 成交数量
                    'timestamp': int,  # 成交时间戳
                    'trade_id': int,  # 聚合交易ID
                    'is_buyer_maker': bool  # 是否为买方主动
                }
        """
        try:
            url = "https://www.binance.com/bapi/defi/v1/public/alpha-trade/agg-trades"
            params = {
                'symbol': symbol,
                'limit': 1  # 只获取1条最新交易记录
            }
            
            # 使用公开接口的请求头
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '000000':
                trades = data.get('data', [])
                if trades and len(trades) > 0:
                    # 解析聚合成交数据，返回格式化的价格数据
                    trade = trades[0]
                    return {
                        'price': trade.get('p'),  # 最新成交价格
                        'quantity': trade.get('q'),  # 成交数量
                        'timestamp': trade.get('T'),  # 成交时间戳
                        'trade_id': trade.get('a'),  # 聚合交易ID
                        'is_buyer_maker': trade.get('m')  # 是否为买方主动
                    }
                else:
                    return None
            else:
                self.logger.log_message(f"API调用失败: {data.get('message', '未知错误')}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.log_message(f"获取 {symbol} 价格失败: {str(e)}")
            return None
    
    def get_token_24h_stats(self, symbol):
        """
        获取代币24小时统计（ALPHA接口暂不支持，返回None）
        
        Args:
            symbol: 代币符号
            
        Returns:
            None: ALPHA接口暂不支持24小时统计
        """
        # ALPHA接口暂不支持24小时统计，返回None
        return None
    
    # ==================== 订单辅助方法 ====================
    
    @staticmethod
    def calculate_order_quantity(symbol, price, side, custom_quantity=None, last_buy_quantity=0):
        """
        计算订单数量
        
        Args:
            symbol: 交易对符号
            price: 价格
            side: 交易方向 (BUY/SELL)
            custom_quantity: 自定义数量（可选）
            last_buy_quantity: 上一个买单的份额（用于卖单）
            
        Returns:
            float: 计算后的数量
        """
        if custom_quantity is not None:
            # 使用自定义数量
            return custom_quantity
        
        if side == "BUY":
            # 买单：根据基础金额计算
            base_amount = 1025 if symbol == "ALPHA_22USDT" else 1030
            return base_amount / price
        else:
            # 卖单：使用上一个买单的份额，扣除手续费
            if last_buy_quantity > 0:
                # 计算手续费（0.01%）
                fee_rate = 0.0001
                fee_amount = last_buy_quantity * fee_rate
                return max(0, last_buy_quantity - fee_amount)
            else:
                # 如果没有上一个买单份额，使用基础金额计算并扣除手续费
                base_amount = 1025 if symbol == "ALPHA_22USDT" else 1030
                quantity = base_amount / price
                fee_rate = 0.0001
                fee_amount = quantity * fee_rate
                return max(0, quantity - fee_amount)
    
    @staticmethod
    def format_quantity(symbol, quantity):
        """
        格式化订单数量
        
        Args:
            symbol: 交易对符号
            quantity: 原始数量
            
        Returns:
            float: 格式化后的数量
        """
        # KOGE代币截取到4位小数，其他代币截取到2位小数
        if symbol == "ALPHA_22USDT":
            return int(quantity * 10000) / 10000  # 截断到4位小数
        else:
            return int(quantity * 100) / 100  # 截断到2位小数
    
    @staticmethod
    def format_price(price):
        """
        格式化价格（8位小数）
        
        Args:
            price: 原始价格
            
        Returns:
            float: 格式化后的价格
        """
        return int(price * 100000000) / 100000000
    
    @staticmethod
    def calculate_payment_amount(side, quantity, price):
        """
        计算支付金额
        
        Args:
            side: 交易方向 (BUY/SELL)
            quantity: 数量
            price: 价格
            
        Returns:
            tuple: (payment_amount, payment_wallet_type)
        """
        if side == "BUY":
            # 使用 Decimal 进行精确计算，避免浮点数精度问题
            dec_quantity = Decimal(str(quantity))
            dec_price = Decimal(str(price))
            dec_amount = dec_quantity * dec_price
            
            # 检查小数位数，如果超过8位则截取（向下取整）
            # 获取小数部分的位数
            amount_str = str(dec_amount)
            if '.' in amount_str:
                decimal_places = len(amount_str.split('.')[1])
                if decimal_places > 8:
                    dec_amount = dec_amount.quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)
            
            # 转换回 float
            payment_amount = float(dec_amount)
            return payment_amount, "CARD"
        else:
            # 卖单的支付金额就是代币数量
            return quantity, "ALPHA"
    
    @staticmethod
    def format_amount_string(side, amount):
        """
        格式化金额字符串
        
        Args:
            side: 交易方向
            amount: 金额
            
        Returns:
            str: 格式化后的金额字符串
        """
        if side == "BUY":
            # 使用 Decimal 确保精确的字符串格式化
            if isinstance(amount, float):
                dec_amount = Decimal(str(amount))
            else:
                dec_amount = Decimal(amount)
            # 格式化为8位小数的字符串
            return format(dec_amount, '.8f')
        else:
            return str(amount)
    
    @staticmethod
    def build_order_payload(symbol, side, price, quantity, payment_amount, payment_wallet_type):
        """
        构建订单payload
        
        Args:
            symbol: 交易对符号
            side: 交易方向
            price: 格式化后的价格
            quantity: 格式化后的数量
            payment_amount: 支付金额
            payment_wallet_type: 支付钱包类型
            
        Returns:
            dict: 订单payload
        """
        amount_str = BinanceAPI.format_amount_string(side, payment_amount)
        
        return {
            "baseAsset": symbol.replace('USDT', ''),
            "quoteAsset": "USDT",
            "side": side,
            "price": price,
            "quantity": quantity,
            "paymentDetails": [{
                "amount": amount_str,
                "paymentWalletType": payment_wallet_type
            }]
        }
    
    @staticmethod
    def build_request_headers(csrf_token, cookie, extra_headers=None):
        """
        构建请求头
        
        Args:
            csrf_token: CSRF令牌
            cookie: Cookie字符串
            extra_headers: 额外的 header 字段字典（可覆盖默认值）
            
        Returns:
            dict: 请求头字典
        """
        extra_headers = extra_headers or {}
        
        # 默认headers
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Clienttype': 'web',
            'Content-Type': 'application/json',
            'Cookie': cookie,
            'csrftoken': csrf_token,
            'lang': 'zh-CN',
            'Priority': 'u=1, i',
            'Referer': 'https://www.binance.com/zh-CN/alpha',
            'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'X-Passthrough-Token': '',
        }
        
        # 从 extra_headers 中添加/覆盖关键字段
        if 'device-info' in extra_headers and extra_headers['device-info']:
            headers['device-info'] = extra_headers['device-info']
        
        if 'fvideo-id' in extra_headers and extra_headers['fvideo-id']:
            headers['fvideo-id'] = extra_headers['fvideo-id']
        
        if 'fvideo-token' in extra_headers and extra_headers['fvideo-token']:
            headers['fvideo-token'] = extra_headers['fvideo-token']
        
        if 'bnc-uuid' in extra_headers and extra_headers['bnc-uuid']:
            headers['Bnc-Uuid'] = extra_headers['bnc-uuid']
        
        if 'user-agent' in extra_headers and extra_headers['user-agent']:
            headers['User-Agent'] = extra_headers['user-agent']
        
        # 添加其他动态生成的字段
        if 'baggage' in extra_headers and extra_headers['baggage']:
            headers['Baggage'] = extra_headers['baggage']
        
        if 'sentry-trace' in extra_headers and extra_headers['sentry-trace']:
            headers['Sentry-Trace'] = extra_headers['sentry-trace']
        
        return headers
    
    # ==================== 订单API方法 ====================
    
    def place_dual_order(self, symbol, price):
        """
        同时创建买单和卖单（双向订单）- 保留方法，暂未使用
        
        Args:
            symbol: 交易对符号
            price: 价格
            
        Returns:
            tuple: (working_order_id, pending_order_id)，失败返回(None, None)
        """
        try:
            url = "https://www.binance.com/bapi/defi/v1/private/alpha-trade/order/place"
            
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Content-Type': 'application/json',
                'csrftoken': self.csrf_token,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
            }
            
            # 构建请求数据
            payload = {
                "baseAsset": symbol.replace('USDT', ''),
                "quoteAsset": "USDT",
                "workingSide": "BUY",
                "workingPrice": price,
                "workingQuantity": 0.1,
                "pendingPrice": price * 100,
                "paymentDetails": [{"amount": "1025", "paymentWalletType": "CARD"}]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '000000' and 'data' in data:
                    return data['data'].get('workingOrderId'), data['data'].get('pendingOrderId')
                else:
                    # 打印错误信息
                    error_code = data.get('code', 'unknown')
                    error_msg = data.get('message', 'unknown error')
                    self.logger.log_message(f"下单失败 - 错误代码: {error_code}, 错误信息: {error_msg}")
            else:
                self.logger.log_message(f"下单失败 - HTTP状态码: {response.status_code}")
            
            return None, None
        except Exception as e:
            self.logger.log_message(f"下单异常: {str(e)}")
            return None, None
    
    def place_single_order(self, symbol, price, side, custom_quantity=None, last_buy_quantity=0):
        """
        创建单向订单（买单或卖单）
        
        Args:
            symbol: 交易对符号
            price: 价格
            side: 交易方向 (BUY/SELL)
            custom_quantity: 自定义数量（可选）
            last_buy_quantity: 上一个买单的份额（用于卖单）
            
        Returns:
            str: 订单ID，失败返回None
        """
        from datetime import datetime
        import json
        
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
            # 1. 记录买单份额信息（用于卖单）
            if side == "SELL" and last_buy_quantity > 0:
                self.logger.log_message(f"代币份额: {last_buy_quantity}")
            
            # 2. 计算订单数量
            quantity = BinanceAPI.calculate_order_quantity(
                symbol, price, side, custom_quantity, last_buy_quantity
            )
            
            # 3. 格式化数量和价格
            quantity_formatted = BinanceAPI.format_quantity(symbol, quantity)
            price_formatted = BinanceAPI.format_price(price)
            
            # 4. 计算支付金额
            payment_amount, payment_wallet_type = BinanceAPI.calculate_payment_amount(
                side, quantity_formatted, price_formatted
            )
            
            # 5. 构建请求头和payload
            url = "https://www.binance.com/bapi/defi/v1/private/alpha-trade/order/place"
            headers = BinanceAPI.build_request_headers(self.csrf_token, self.cookie, self.extra_headers)
            payload = BinanceAPI.build_order_payload(
                symbol, side, price_formatted, quantity_formatted, 
                payment_amount, payment_wallet_type
            )
            
            # 6. 记录请求参数
            trade_detail['request_params'] = {
                'url': url,
                'headers': headers,
                'payload': payload
            }
            
            # 7. 发送请求
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            # 8. 记录响应信息
            trade_detail['response'] = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'text': response.text
            }
            
            if response.status_code == 200:
                data = response.json()
                trade_detail['response']['json'] = data
                
                if data.get('code') == '000000' and 'data' in data:
                    # 记录成功信息
                    trade_detail['status'] = 'success'
                    trade_detail['order_id'] = data['data']
                    
                    # 记录交易详情到文件
                    self.logger.log_trade_detail(trade_detail)
                    
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
                    self.logger.log_message(f"{side}单下单失败 - 错误代码: {error_code}, 错误信息: {error_message}")
                    
                    # 记录交易详情到文件
                    self.logger.log_trade_detail(trade_detail)
                    
                    # 使用logger记录错误信息
                    if side == "BUY":
                        error_info = f"""{side}单下单失败 - 代币: {symbol}, 价格: {price}, 数量: {quantity_formatted}, 支付金额: {payment_amount} USDT, 错误代码: {error_code}, 错误信息: {error_message}"""
                    else:  # SELL
                        error_info = f"""{side}单下单失败 - 代币: {symbol}, 价格: {price}, 数量: {quantity_formatted}, 支付代币数量: {payment_amount}, 错误代码: {error_code}, 错误信息: {error_message}"""
                    self.logger.log_error(error_info)
                    
                    # 控制台打印详细信息，方便排查
                    print(f"\n{'=' * 50}")
                    print(f"=== {side}单下单失败 ===")
                    print(f"代币: {symbol}")
                    print(f"价格: {price}")
                    print(f"数量: {quantity_formatted}")
                    print(f"支付金额: {payment_amount}")
                    print(f"错误代码: {error_code}")
                    print(f"错误信息: {error_message}")
                    print(f"请求数据:\n{json.dumps(payload, indent=2, ensure_ascii=False)}")
                    print(f"{'=' * 50}\n")
                    
                    return None
            else:
                # 记录HTTP错误
                trade_detail['status'] = 'http_error'
                trade_detail['error'] = {
                    'status_code': response.status_code,
                    'message': f"HTTP状态码: {response.status_code}"
                }
                
                error_msg = f"{side}单下单请求失败 - HTTP状态码: {response.status_code}"
                self.logger.log_message(error_msg)
                
                # 记录交易详情到文件
                self.logger.log_trade_detail(trade_detail)
                
                return None
                
        except Exception as e:
            # 记录异常错误
            trade_detail['status'] = 'exception'
            trade_detail['error'] = {
                'message': str(e),
                'type': type(e).__name__
            }
            
            error_msg = f"{side}单下单异常: {str(e)}"
            self.logger.log_message(error_msg)
            
            # 记录交易详情到文件
            self.logger.log_trade_detail(trade_detail)
            
            return None
    
    def cancel_all_orders(self):
        """
        取消所有委托
        
        Returns:
            bool: 成功返回True，失败返回False
        """
        try:
            if not self.csrf_token or not self.cookie:
                self.logger.log_message("请先设置认证信息")
                return False
                
            url = "https://www.binance.com/bapi/defi/v1/private/alpha-trade/order/cancel-all"
            payload = {}
            
            headers = BinanceAPI.build_request_headers(self.csrf_token, self.cookie, self.extra_headers)
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '000000' and data.get('success') == True:
                    self.logger.log_message("取消所有委托成功")
                    return True
                else:
                    self.logger.log_message(f"取消委托失败 - 错误代码: {data.get('code')}, 错误信息: {data.get('message')}")
                    return False
            else:
                self.logger.log_message(f"取消委托请求失败 - HTTP状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.log_message(f"取消委托异常: {str(e)}")
            return False
    
    def check_single_order_filled(self, order_id):
        """
        检查单个订单状态
        
        Args:
            order_id: 订单ID
            
        Returns:
            str: 订单状态（FILLED/PARTIALLY_FILLED等），失败返回None
        """
        try:
            from datetime import datetime, timedelta
            
            # 获取今天和明天的时间戳
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow_start = today_start + timedelta(days=1)
            
            start_time = int(today_start.timestamp() * 1000)
            end_time = int(tomorrow_start.timestamp() * 1000)
            
            url = "https://www.binance.com/bapi/defi/v1/private/alpha-trade/order/get-order-history-web"
            params = {
                'page': 1,
                'rows': 1,  # 只获取最新1条订单
                'orderStatus': 'FILLED,PARTIALLY_FILLED,EXPIRED,CANCELED,REJECTED',
                'startTime': start_time,
                'endTime': end_time
            }
            
            headers = BinanceAPI.build_request_headers(self.csrf_token, self.cookie, self.extra_headers)
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '000000' and 'data' in data:
                    orders = data['data']
                    
                    if orders and len(orders) > 0:
                        # 检查最新订单是否匹配
                        latest_order = orders[0]
                        if str(latest_order.get('orderId')) == str(order_id):
                            # 检查订单状态
                            order_status = latest_order.get('status', '')
                            if order_status in ['FILLED', 'PARTIALLY_FILLED']:
                                # 打印成交额信息
                                cum_quote = latest_order.get('cumQuote', '0')
                                side = latest_order.get('side', '')
                                
                                # 根据订单方向格式化成交额
                                if side == 'SELL':
                                    formatted_amount = f"{float(cum_quote):.2f}"
                                    self.logger.log_message(f"订单 {order_id} 成交，成交额: {formatted_amount} USDT")
                                else:
                                    formatted_amount = cum_quote
                                    self.logger.log_message(f"订单 {order_id} 成交，成交额: {formatted_amount} USDT")
                                
                                return order_status
                            else:
                                return order_status
                return None
            else:
                self.logger.log_message(f"查询订单历史失败 - HTTP状态码: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.log_message(f"查询订单历史异常: {str(e)}")
            return None
    
    def get_order_details(self, order_id=None):
        """
        获取订单详细信息（获取最新一条订单）
        
        Args:
            order_id: 订单ID（可选，未使用）
            
        Returns:
            dict: 订单详情字典，失败返回None
        """
        try:
            from datetime import datetime, timedelta
            
            # 获取今天的时间范围
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow_start = today + timedelta(days=1)
            
            start_time = int(today.timestamp() * 1000)
            end_time = int(tomorrow_start.timestamp() * 1000)
            
            url = "https://www.binance.com/bapi/defi/v1/private/alpha-trade/order/get-order-history-web"
            params = {
                'page': 1,
                'rows': 1,  # 只获取最新1条订单
                'orderStatus': 'FILLED,PARTIALLY_FILLED,EXPIRED,CANCELED,REJECTED',
                'startTime': start_time,
                'endTime': end_time
            }
            
            headers = BinanceAPI.build_request_headers(self.csrf_token, self.cookie, self.extra_headers)
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == '000000' and data.get('data') and len(data['data']) > 0:
                return data['data'][0]
            else:
                self.logger.log_message(f"获取订单详情失败: {data.get('message', '未知错误')}")
                self.logger.log_message(f"响应数据: {data}")
                return None
                
        except Exception as e:
            self.logger.log_message(f"获取订单详情异常: {str(e)}")
            # 添加响应数据日志
            try:
                if 'response' in locals():
                    self.logger.log_message(f"响应状态码: {response.status_code}")
                    self.logger.log_message(f"响应内容: {response.text}")
            except:
                pass
            return None
    
    def get_token_balance(self, symbol):
        """
        获取指定代币的钱包余额（新资产接口）
        
        Args:
            symbol: 原始代币符号（例如 "MERL"）。
                   若传入类似 "ALPHA_195"，将尝试从 alphaIdMap.json 反查为原始符号。
        
        Returns:
            float: 代币数量，未找到或失败返回0
        """
        try:
            # 若传入的是 ALPHA_###，尝试反查为原始代币名（如 MERL）
            search_asset = symbol
            try:
                if isinstance(symbol, str) and symbol.startswith("ALPHA_"):
                    with open('alphaIdMap.json', 'r', encoding='utf-8') as f:
                        alpha_map = json.load(f)
                    # 反向映射
                    for k, v in alpha_map.items():
                        if v == symbol:
                            search_asset = k
                            break
            except Exception:
                # 反查失败时忽略，按原值查询
                pass

            url = "https://www.binance.com/bapi/asset/v2/private/asset-service/wallet/asset"
            params = {
                "needAlphaAsset": "true",
                "needEuFuture": "true",
                "needPnl": "true",
            }
            headers = BinanceAPI.build_request_headers(self.csrf_token, self.cookie, self.extra_headers)
            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code != 200:
                self.logger.log_message(f"获取钱包余额请求失败: HTTP {response.status_code}")
                return 0

            data = response.json()
            assets = data.get('data') or []

            # 遍历资产列表，按 asset 字段匹配（例如 MERL）
            for item in assets:
                if item.get('asset') == search_asset:
                    amount_str = item.get('amount', '0') or '0'
                    try:
                        amount = float(amount_str)
                    except (ValueError, TypeError):
                        amount = 0.0
                    self.logger.log_message(f"从钱包接口获取 {search_asset} 余额: {amount}")
                    return amount

            self.logger.log_message(f"钱包中未找到代币: {search_asset}")
            return 0

        except Exception as e:
            self.logger.log_message(f"获取钱包余额异常: {str(e)}")
            return 0

    def get_binance_token_list(self):
        """
        获取币安Alpha交易代币列表
        
        Returns:
            dict: API响应数据，包含代币列表信息
        """
        url = "https://www.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/cex/alpha/all/token/list"
        
        # 添加请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Origin': 'https://www.binance.com',
            'Referer': 'https://www.binance.com/'
        }
        
        try:
            # 发送GET请求，添加超时和SSL验证
            response = requests.get(url, headers=headers, timeout=10, verify=True)
            
            # 检查响应状态
            if response.status_code != 200:
                raise Exception(f"API请求失败，状态码: {response.status_code}")
            
            # 解析JSON响应
            data = response.json()
            
            # 检查API响应是否成功
            if not data.get('success'):
                raise Exception(f"API返回错误: {data.get('message', '未知错误')}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求错误: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"JSON解析错误: {e}")
        except Exception as e:
            raise Exception(f"获取代币列表失败: {e}")

    def create_alpha_id_map(self, token_list_data=None):
        """
        从代币列表数据创建Alpha ID映射
        
        Args:
            token_list_data (dict, optional): 代币列表数据，如果为None则调用API获取
        
        Returns:
            dict: Symbol到Alpha ID的映射
        """
        if token_list_data is None:
            token_list_data = self.get_binance_token_list()
        
        if not token_list_data.get('data'):
            raise Exception("代币列表数据为空")
        
        token_list = token_list_data['data']
        alpha_id_map = {}
        
        for token in token_list:
            symbol = token.get('symbol')
            alpha_id = token.get('alphaId')
            if symbol and alpha_id:
                alpha_id_map[symbol] = alpha_id
        
        return alpha_id_map


# 创建全局API实例（可选）
_global_api = None


def get_api(base_url=None, csrf_token=None, cookie=None, logger=None):
    """
    获取全局API实例（单例模式）
    
    Args:
        base_url: API基础URL
        csrf_token: CSRF令牌
        cookie: Cookie字符串
        logger: Logger实例
        
    Returns:
        BinanceAPI: API实例
    """
    global _global_api
    if _global_api is None:
        _global_api = BinanceAPI(base_url, csrf_token, cookie, logger)
    return _global_api


def set_global_api(api):
    """
    设置全局API实例
    
    Args:
        api: BinanceAPI实例
    """
    global _global_api
    _global_api = api

