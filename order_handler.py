#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
订单处理模块
Order Handler Module for Binance Auto Trade System
"""

import time
import random


class OrderHandler:
    """订单处理类 - 负责订单状态检查、重试等业务逻辑"""
    
    def __init__(self, trader):
        """
        初始化订单处理器
        
        Args:
            trader: BinanceTrader实例
        """
        self.trader = trader
        # 直接引用API实例，避免跨模块调用
        self.api = trader.api
    
    def handle_order_status(self, symbol, order_id, display_name, side, check_count=0, max_checks=5):
        """
        递归检查订单状态
        
        Args:
            symbol: 交易对符号
            order_id: 订单ID
            display_name: 显示名称
            side: 订单方向（"BUY" 或 "SELL"）
            check_count: 当前检查次数
            max_checks: 最大检查次数
            
        Returns:
            bool: 订单成交返回True，否则返回False
        """
        # 检查自动交易状态
        if not self.trader.auto_trading.get(symbol, False):
            self.trader.log_message(f"{display_name} 自动交易已停止")
            return False

        # 等待随机时间
        time.sleep(random.uniform(1, 2))

        # 检查订单状态
        try:
            order_status = self.api.check_single_order_filled(order_id)
            self.trader.log_message(f"{display_name} 检查{side}单状态: {order_status}, 检查次数: {check_count + 1}")
        except Exception as e:
            self.trader.log_message(f"{display_name} 检查{side}单状态失败: {e}")
            time.sleep(random.uniform(0, 1))
            return False

        if order_status == "FILLED":
            self.trader.log_message(f"{display_name} {side}单已成交")
            # 获取订单详情
            order_details = self.api.get_order_details()
            if order_details:
                # 买单成交时保存份额和成交额
                if side == "BUY" and symbol in self.trader.tokens:
                    executed_qty = float(order_details.get('executedQty', 0))
                    cum_quote = float(order_details.get('cumQuote', '0'))
                    
                    # 保存买单份额
                    current_quantity = self.trader.tokens[symbol].get('last_buy_quantity', 0.0)
                    new_total_quantity = current_quantity + executed_qty
                    self.trader.tokens[symbol]['last_buy_quantity'] = new_total_quantity
                    
                    # 保存买单成交额
                    current_buy_amount = self.trader.tokens[symbol].get('last_buy_amount', 0.0)
                    new_total_amount = current_buy_amount + cum_quote
                    self.trader.tokens[symbol]['last_buy_amount'] = new_total_amount
                    
                    self.trader.log_message(f"买单成交，保存份额: {current_quantity} + {executed_qty} = {new_total_quantity}，保存成交额: {current_buy_amount:.2f} + {cum_quote:.2f} = {new_total_amount:.2f} USDT")
                # 卖单成交时累加成交额
                elif side == "SELL" and symbol in self.trader.tokens:
                    cum_quote = float(order_details.get('cumQuote', '0'))
                    formatted_amount = f"{cum_quote:.2f}"
                    
                    # 累计卖单成交额（统计到token数据中）
                    current_sell_amount = self.trader.tokens[symbol].get('last_sell_amount', 0.0)
                    new_total_sell_amount = current_sell_amount + cum_quote
                    self.trader.tokens[symbol]['last_sell_amount'] = new_total_sell_amount
                    
                    # 同时累计到全局变量（用于兼容性）
                    self.trader.current_sell_amount += cum_quote
                    
                    self.trader.log_message(f"卖单成交，保存成交额: {current_sell_amount:.2f} + {cum_quote:.2f} = {new_total_sell_amount:.2f} USDT")
            else:
                self.trader.log_message(f"无法获取订单详情，跳过保存{side}单信息")
            return True
        elif order_status == "PARTIALLY_FILLED":
            self.trader.log_message(f"{display_name} {side}单部分成交，开始处理剩余份额")
            try:
                # 先查询5次，每次间隔1-2秒
                for i in range(5):
                    self.trader.log_message(f"{display_name} 第{i+1}次查询部分成交状态...")
                    time.sleep(random.uniform(1, 2))
                    
                    # 重新检查订单状态
                    new_status = self.api.check_single_order_filled(order_id)
                    if new_status == "FILLED":
                        self.trader.log_message(f"{display_name} 第{i+1}次查询：{side}单已完全成交")
                        return True
                    elif new_status != "PARTIALLY_FILLED":
                        self.trader.log_message(f"{display_name} 第{i+1}次查询：{side}单状态变为 {new_status}")
                        # 如果不是部分成交，按其他状态处理
                        if new_status == "CANCELED":
                            return self.handle_canceled_order(symbol, side, display_name, order_id)
                        else:
                            result = self.retry_order_with_new_price(order_id, symbol, side, display_name)
                            if side == "BUY":
                                return result
                            return result
                
                # 5次查询后仍然是部分成交，取消订单
                self.trader.log_message(f"{display_name} 5次查询后仍为部分成交，取消订单")
                self.api.cancel_all_orders()
                time.sleep(2)  # 等待取消生效
                
                # Double check订单状态
                final_status = self.api.check_single_order_filled(order_id)
                self.trader.log_message(f"{display_name} Double check: {side}单状态为 {final_status}")
                
                if final_status == "FILLED":
                    self.trader.log_message(f"{display_name} 取消后{side}单已完全成交")
                    return True
                elif final_status == "CANCELED":
                    # 获取已取消订单的份额信息
                    canceled_order_info = self.api.get_order_details()
                    if canceled_order_info:
                        orig_qty = float(canceled_order_info.get('origQty', 0))
                        executed_qty = float(canceled_order_info.get('executedQty', 0))
                        remaining_qty = orig_qty - executed_qty
                        
                        self.trader.log_message(f"{display_name} 已取消订单详情:")
                        self.trader.log_message(f"  - 原始数量: {orig_qty}")
                        self.trader.log_message(f"  - 已成交数量: {executed_qty}")
                        self.trader.log_message(f"  - 剩余数量: {remaining_qty}")
                        
                        if remaining_qty > 0:
                            # 只有部分成交才累计已成交的份额和成交额
                            if side == "BUY" and symbol in self.trader.tokens:
                                # 累计买单份额
                                current_quantity = self.trader.tokens[symbol].get('last_buy_quantity', 0.0)
                                new_total_quantity = current_quantity + executed_qty
                                self.trader.tokens[symbol]['last_buy_quantity'] = new_total_quantity
                                
                                # 累计买单成交额
                                cum_quote = float(canceled_order_info.get('cumQuote', '0'))
                                current_buy_amount = self.trader.tokens[symbol].get('last_buy_amount', 0.0)
                                new_total_amount = current_buy_amount + cum_quote
                                self.trader.tokens[symbol]['last_buy_amount'] = new_total_amount
                                
                                self.trader.log_message(f"累计部分成交份额: {current_quantity} + {executed_qty} = {new_total_quantity}，累计买单成交额: {current_buy_amount:.2f} + {cum_quote:.2f} = {new_total_amount:.2f} USDT")
                            
                            return self.retry_order_with_remaining_qty(symbol, side, display_name, remaining_qty)
                        else:
                            self.trader.log_message(f"{display_name} 没有剩余份额需要处理")
                            return True
                    else:
                        self.trader.log_message(f"{display_name} 无法获取已取消订单详情")
                        result = self.retry_order_with_new_price(order_id, symbol, side, display_name)
                        if side == "BUY":
                            return result
                        return result
                else:
                    self.trader.log_message(f"{display_name} 取消后{side}单状态异常: {final_status}")
                    result = self.retry_order_with_new_price(order_id, symbol, side, display_name)
                    if side == "BUY":
                        return result
                    return result
                    
            except Exception as e:
                self.trader.log_message(f"{display_name} 处理部分成交失败: {e}")
                result = self.retry_order_with_new_price(order_id, symbol, side, display_name)
                if side == "BUY":
                    return result
                return result
        else:
            # 未成交，检查次数是否达到上限
            if check_count + 1 < max_checks:
                self.trader.log_message(f"{display_name} {side}单尚未成交，2秒后继续检查")
                return self.handle_order_status(symbol, order_id, display_name, side, check_count + 1, max_checks)
            else:
                self.trader.log_message(f"{display_name} {side}单约10秒未成交，取消订单")
                try:
                    self.api.cancel_all_orders()
                    # 取消后等待2秒，然后双重检查订单状态
                    time.sleep(2)
                    self.trader.log_message(f"{display_name} 取消后双重检查订单状态")
                    final_status = self.api.check_single_order_filled(order_id)
                    
                    if final_status == 'FILLED':
                        self.trader.log_message(f"{display_name} Double check: {side}单已成交，继续流程")
                        return True
                    else:
                        # 买单5次查询后仍未成交，退出当前交易循环
                        if side == "BUY":
                            self.trader.log_message(f"{display_name} Double check: 买单状态为 {final_status}，5次查询后仍未成交，退出当前交易循环")
                            return False
                        # 卖单继续重试
                        self.trader.log_message(f"{display_name} Double check: 卖单状态为 {final_status}，继续重试")
                        
                except Exception as e:
                    self.trader.log_message(f"{display_name} 取消{side}单失败: {e}")
                    result = self.retry_order_with_new_price(order_id, symbol, side, display_name)
                    # 如果是买单且切换了代币，根据返回值决定是否继续
                    if side == "BUY":
                        self.trader.log_message(f"{display_name} 买单取消失败，退出当前交易循环")
                        return False
                    # 卖单继续重试
                    return self.retry_order_with_new_price(order_id, symbol, side, display_name)
                
                # 卖单：如果双重检查没有发现成交，继续重试
                return self.retry_order_with_new_price(order_id, symbol, side, display_name)

    def retry_order_with_new_price(self, order_id, symbol, side, display_name):
        """
        重新获取最新价格并下单，如果失败则尝试更换代币（仅限买单）
        
        Args:
            order_id: 原订单ID
            symbol: 交易对符号
            side: 订单方向
            display_name: 显示名称
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        try:
            # 获取最新价格
            price_data = self.trader.get_token_price(symbol)
            if not price_data or 'price' not in price_data:
                if side == "BUY":
                    # 检查是否有部分成交的份额，如果有则不切换代币
                    if symbol in self.trader.tokens:
                        current_quantity = self.trader.tokens[symbol].get('last_buy_quantity', 0.0)
                        if current_quantity > 0:
                            self.trader.log_message(f"{display_name} 检测到部分成交份额 {current_quantity}，不切换代币")
                            return False  # 不切换代币，返回False表示重试失败但不切换
                    
                    self.trader.log_message(f"{display_name} 无法获取最新价格，尝试更换代币")
                    return self.switch_to_better_token(symbol, display_name)
                else:
                    self.trader.log_message(f"{display_name} 无法获取最新价格，卖单重试失败")
                    return False
            
            latest_price = float(price_data['price'])
            
            # 根据订单方向调整价格以提高撮合优先级
            if side == "BUY":
                price_data['price'] = latest_price + 0.00000001  # 买单价格提高0.00000001
                self.trader.log_message(f"{display_name} 获取最新价格: {latest_price}，买单调整后价格: {price_data['price']}")
            else:  # SELL
                price_data['price'] = latest_price - 0.00000001  # 卖单价格降低0.00000001
                self.trader.log_message(f"{display_name} 获取最新价格: {latest_price}，卖单调整后价格: {price_data['price']}")
            
            # 重新下单
            new_order_id = self.trader.trading_engine.place_single_order(symbol, price_data['price'], side)
            if new_order_id:
                # 递归检查新订单状态
                return self.handle_order_status(symbol, new_order_id, display_name, side)
            else:
                if side == "BUY":
                    # 检查是否有部分成交的份额，如果有则不切换代币
                    if symbol in self.trader.tokens:
                        current_quantity = self.trader.tokens[symbol].get('last_buy_quantity', 0.0)
                        if current_quantity > 0:
                            self.trader.log_message(f"{display_name} 检测到部分成交份额 {current_quantity}，不切换代币")
                            return False  # 不切换代币，返回False表示重试失败但不切换
                    
                    self.trader.log_message(f"{display_name} 重新下单失败，尝试更换代币")
                    return self.switch_to_better_token(symbol, display_name)
                else:
                    self.trader.log_message(f"{display_name} 重新下单失败，卖单重试失败")
                    return False
                
        except Exception as e:
            if side == "BUY":
                # 检查是否有部分成交的份额，如果有则不切换代币
                if symbol in self.trader.tokens:
                    current_quantity = self.trader.tokens[symbol].get('last_buy_quantity', 0.0)
                    if current_quantity > 0:
                        self.trader.log_message(f"{display_name} 检测到部分成交份额 {current_quantity}，不切换代币")
                        return False  # 不切换代币，返回False表示重试失败但不切换
                
                self.trader.log_message(f"重新下单失败: {str(e)}，尝试更换代币")
                return self.switch_to_better_token(symbol, display_name)
            else:
                self.trader.log_message(f"重新下单失败: {str(e)}，卖单重试失败")
                return False

    def switch_to_better_token(self, current_symbol, current_display_name):
        """
        当前代币交易困难时，退出当前代币交易循环
        
        Args:
            current_symbol: 当前代币符号
            current_display_name: 当前代币显示名称
            
        Returns:
            bool: 返回False表示当前交易失败
        """
        try:
            self.trader.log_message(f"尝试买单失败，代币可能当前不稳定，重新开始流程")
            
            # 停止当前代币的自动交易
            self.trader.auto_trading[current_symbol] = False
            if current_symbol in self.trader.tokens:
                self.trader.tokens[current_symbol]['auto_trading'] = False
            
            self.trader.log_message(f"{current_display_name} 已停止交易，将在下一次循环中重新获取新代币")
            
            return False  # 返回False表示当前交易失败，但不会影响整体交易流程
            
        except Exception as e:
            self.trader.log_message(f"停止当前代币交易失败: {str(e)}")
            return False

    def retry_order_with_remaining_qty(self, symbol, side, display_name, remaining_qty):
        """
        使用剩余份额重新下单
        
        Args:
            symbol: 交易对符号
            side: 订单方向
            display_name: 显示名称
            remaining_qty: 剩余份额
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        try:
            # 获取最新价格
            price_data = self.trader.get_token_price(symbol)
            if not price_data or 'price' not in price_data:
                self.trader.log_message(f"{display_name} 无法获取最新价格，取消交易")
                return False
            
            latest_price = float(price_data['price'])
            
            # 根据订单方向调整价格以提高撮合优先级
            if side == "BUY":
                adjusted_price = latest_price + 0.00000001  # 买单价格提高0.00000001
                self.trader.log_message(f"{display_name} 获取最新价格: {latest_price}，买单调整后价格: {adjusted_price}")
            else:  # SELL
                adjusted_price = latest_price - 0.00000001  # 卖单价格降低0.00000001
                self.trader.log_message(f"{display_name} 获取最新价格: {latest_price}，卖单调整后价格: {adjusted_price}")
            
            # 使用剩余份额重新下单
            new_order_id = self.trader.trading_engine.place_single_order(symbol, adjusted_price, side, custom_quantity=remaining_qty)
            if new_order_id:
                # 递归检查新订单状态
                return self.handle_order_status(symbol, new_order_id, display_name, side)
            else:
                return False
                
        except Exception as e:
            self.trader.log_message(f"使用剩余份额重新下单失败: {str(e)}")
            return False

    def handle_canceled_order(self, symbol, side, display_name, order_id):
        """
        处理已取消的订单
        
        Args:
            symbol: 交易对符号
            side: 订单方向
            display_name: 显示名称
            order_id: 订单ID
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        try:
            # 获取已取消订单的份额信息
            canceled_order_info = self.api.get_order_details()
            if canceled_order_info:
                orig_qty = float(canceled_order_info.get('origQty', 0))
                executed_qty = float(canceled_order_info.get('executedQty', 0))
                remaining_qty = orig_qty - executed_qty
                
                self.trader.log_message(f"{display_name} 已取消订单详情:")
                self.trader.log_message(f"  - 原始数量: {orig_qty}")
                self.trader.log_message(f"  - 已成交数量: {executed_qty}")
                self.trader.log_message(f"  - 剩余数量: {remaining_qty}")
                
                if remaining_qty > 0:
                    return self.retry_order_with_remaining_qty(symbol, side, display_name, remaining_qty)
                else:
                    self.trader.log_message(f"{display_name} 没有剩余份额需要处理")
                    return True
            else:
                self.trader.log_message(f"{display_name} 无法获取已取消订单详情")
                result = self.retry_order_with_new_price(order_id, symbol, side, display_name)
                if side == "BUY":
                    return result
                return result
        except Exception as e:
            self.trader.log_message(f"{display_name} 处理已取消订单失败: {e}")
            result = self.retry_order_with_new_price(order_id, symbol, side, display_name)
            if side == "BUY":
                return result
            return result

