#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易引擎模块
Trading Engine Module for Binance Auto Trade System
"""

import time
import random
import threading
from datetime import datetime
from tkinter import messagebox


class TradingEngine:
    """交易引擎类 - 负责自动交易逻辑"""
    
    def __init__(self, trader):
        """
        初始化交易引擎
        
        Args:
            trader: BinanceTrader实例
        """
        self.trader = trader
        # 直接引用API实例，避免跨模块调用
        self.api = trader.api
    
    def place_single_order(self, symbol, price, side, custom_quantity=None):
        """
        创建单向订单（买单或卖单）
        
        Args:
            symbol: 交易对符号
            price: 价格
            side: 交易方向 (BUY/SELL)
            custom_quantity: 自定义数量（可选）
            
        Returns:
            str: 订单ID，失败返回None
        """
        # 获取上一个买单份额（用于卖单）
        last_buy_quantity = 0
        if side == "SELL" and symbol in self.trader.tokens:
            last_buy_quantity = self.trader.tokens[symbol].get('last_buy_quantity', 0)
        
        # 直接调用API模块下单
        return self.api.place_single_order(symbol, price, side, custom_quantity, last_buy_quantity)
    
    def run_4x_trading(self, trading_count):
        """
        运行4倍自动交易
        
        Args:
            trading_count: 交易次数
        """
        completed_trades = 0
        
        while self.trader.trading_4x_active and completed_trades < trading_count:
            try:
                # 获取稳定度排名第一的代币
                top_token = self.trader.alpha123_client.get_top_stability_token()
                
                if not top_token:
                    self.trader.log_message("当前没有稳定高倍代币，等待15秒")
                    time.sleep(15)
                    continue
                
                symbol = top_token['symbol']
                display_name = top_token['display_name']
                price = top_token['price']
                stability = top_token['stability']
                
                self.trader.log_message(f"选择代币: {display_name} ({symbol})，稳定度: {stability}，价格: ${price}")
                
                # 执行一次买卖交易 - 直接调用toggle_auto_trading方法
                # 临时设置代币到tokens中
                if symbol not in self.trader.tokens:
                    self.trader.tokens[symbol] = {
                        'price': price,
                        'last_update': datetime.now(),
                        'display_name': display_name,
                        'trade_count': 1,
                        'trade_amount': 0.0,
                        'auto_trading': False,
                        'change_24h': 0.0,
                        'last_buy_quantity': 0.0,  # 存储上一个买单的份额
                        'last_buy_amount': 0.0,  # 存储上一个买单的成交额
                        'last_sell_amount': 0.0  # 存储上一个卖单的成交额
                    }
                
                # 调用toggle_auto_trading开始单次交易
                self.toggle_auto_trading(symbol, single_trade=True)
                
                # 等待单次交易完成
                self.wait_for_single_trade_completion(symbol)
                
                # 只有交易成功才计数
                if self.trader.trade_success_flag:
                    completed_trades += 1
                    self.trader.log_message(f"4倍交易完成 {completed_trades}/{trading_count}")
                    
                    # 增加今日交易次数统计
                    self.trader.increment_daily_trade_count()
                    
                    # 计算本次买卖的损耗（买单成交额 - 卖单成交额）
                    if symbol in self.trader.tokens:
                        last_buy_amount = self.trader.tokens[symbol].get('last_buy_amount', 0.0)
                        last_sell_amount = self.trader.tokens[symbol].get('last_sell_amount', 0.0)
                        
                        if last_buy_amount > 0 and last_sell_amount > 0:
                            trade_loss = last_buy_amount - last_sell_amount
                            self.trader.daily_trade_loss += trade_loss
                            self.trader.log_message(f"4倍交易损耗: 买入 {last_buy_amount:.2f} USDT - 卖出 {last_sell_amount:.2f} USDT = 损耗 {trade_loss:.2f} USDT，累计损耗: {self.trader.daily_trade_loss:.2f} USDT")
                            
                            # 保存配置并更新损耗显示
                            self.trader.save_config()
                            self.trader.root.after(0, self.trader.update_daily_loss_display)
                    
                    # 重置当前卖单成交额
                    self.trader.current_sell_amount = 0.0
                else:
                    self.trader.log_message(f"4倍交易失败，不计入完成次数")
                
                # 重置交易成功标识
                self.trader.trade_success_flag = True
                
                # 交易间隔 - 每次交易完成后都等待10-15秒
                wait_time = random.uniform(10, 15)
                if completed_trades < trading_count:
                    self.trader.log_message(f"等待 {wait_time:.1f} 秒后获取下一个稳定高倍代币...")
                time.sleep(wait_time)
                    
            except Exception as e:
                self.trader.log_message(f"4倍自动交易异常: {str(e)}")
                time.sleep(5)
        
        # 交易完成
        self.trader.trading_4x_active = False
        self.trader.root.after(0, lambda: self.trader.trading_4x_btn.config(text="4倍自动交易", bg='#27ae60'))
        self.trader.log_message(f"4倍自动交易完成，共完成 {completed_trades} 次交易")
    
    def wait_for_single_trade_completion(self, symbol):
        """
        等待单次交易完成
        
        Args:
            symbol: 交易对符号
        """
        # 等待自动交易状态变为False（表示交易完成）
        while self.trader.auto_trading.get(symbol, False):
            time.sleep(1)
    
    def toggle_auto_trading(self, symbol, single_trade=False):
        """
        切换自动交易状态
        
        Args:
            symbol: 交易对符号
            single_trade: 是否单次交易
        """
        display_name = self.trader.tokens[symbol].get('display_name', symbol)
        
        # 添加调试信息
        current_status = self.trader.auto_trading.get(symbol, False)
        self.trader.log_message(f"[DEBUG] {display_name} toggle_auto_trading 被调用，当前状态: {current_status}，单次交易: {single_trade}")
        
        if symbol in self.trader.auto_trading and self.trader.auto_trading[symbol]:
            # 停止自动交易
            self.trader.auto_trading[symbol] = False
            self.trader.tokens[symbol]['auto_trading'] = False
            if symbol in self.trader.trading_threads:
                # 这里可以添加停止线程的逻辑
                pass
            
            self.trader.log_message(f"{display_name} 自动交易停止中，正在清理持仓...")
            
            # 执行停止清理逻辑
            self.stop_trading_cleanup(symbol, display_name)
            
            self.trader.log_message(f"{display_name} 自动交易已停止")
            
            # 更新表格显示
            self.trader.update_tree_view()
        else:
            # 开始自动交易
            if not self.trader.csrf_token or not self.trader.cookie:
                messagebox.showerror("错误", "请先设置认证信息")
                return
            
            self.trader.auto_trading[symbol] = True
            self.trader.tokens[symbol]['auto_trading'] = True
            
            # 如果是单次交易，设置trade_count为1
            if single_trade:
                self.trader.tokens[symbol]['trade_count'] = 1
            
            # 启动自动交易线程
            thread = threading.Thread(target=self.auto_trade_worker, args=(symbol,), daemon=True)
            self.trader.trading_threads[symbol] = thread
            thread.start()
            
            self.trader.log_message(f"{display_name} 自动交易已开始")
            
            # 更新表格显示
            self.trader.update_tree_view()
    
    def stop_trading_cleanup(self, symbol, display_name):
        """
        停止交易时的清理逻辑
        
        Args:
            symbol: 交易对符号
            display_name: 显示名称
        """
        try:
            # 1. 取消所有未成交的订单
            self.trader.log_message(f"{display_name} 正在取消所有未成交订单...")
            cancel_success = self.api.cancel_all_orders()
            if cancel_success:
                self.trader.log_message(f"{display_name} 已取消所有未成交订单")
            else:
                self.trader.log_message(f"{display_name} 取消订单失败，继续执行清理...")
            
            # 等待一下，确保订单取消生效
            time.sleep(1)
            
            # 2. 检查是否持有代币，如果有则卖出
            last_buy_quantity = self.trader.tokens[symbol].get('last_buy_quantity', 0)
            if last_buy_quantity > 0:
                self.trader.log_message(f"{display_name} 检测到持有份额: {last_buy_quantity}，正在清仓卖出...")
                
                # 使用和正常交易一样的卖单逻辑
                self.execute_cleanup_sell_order(symbol, display_name, last_buy_quantity)
            else:
                self.trader.log_message(f"{display_name} 无持仓，无需清仓")
                
        except Exception as e:
            self.trader.log_message(f"{display_name} 停止清理过程中出现异常: {str(e)}")
    
    def execute_cleanup_sell_order(self, symbol, display_name, quantity, is_global_cleanup=False):
        """
        执行清仓卖单，使用和正常交易一样的逻辑
        
        Args:
            symbol: 交易对符号
            display_name: 显示名称
            quantity: 卖出数量
            is_global_cleanup: 是否为全局清理（不检查自动交易状态）
        """
        try:
            # 获取当前价格
            price_data = self.api.get_token_price(symbol)
            if not price_data or not price_data.get('price'):
                self.trader.log_message(f"{display_name} 无法获取当前价格，跳过清仓")
                return
            
            sell_price = float(price_data['price'])
            self.trader.log_message(f"{display_name} 获取到当前价格: {sell_price}")
            
            # 卖单重试逻辑（和正常交易一样）
            max_sell_retries = 5
            sell_retry_count = 0
            sell_order_id = None
            use_wallet_balance = False
            
            while sell_retry_count < max_sell_retries and not sell_order_id:
                sell_price_adjusted = sell_price - (0.0000001 * sell_retry_count)  # 每次重试降低价格
                
                # 如果是重试且之前失败过，使用钱包接口获取实际余额
                if sell_retry_count > 0 and not use_wallet_balance:
                    self.trader.log_message(f"{display_name} 清仓卖单失败，尝试从钱包接口获取实际持有份额")
                    
                    # 从symbol中提取代币符号（例如 "ALPHA_195USDT" -> "ALPHA_195"）
                    token_symbol = symbol.replace('USDT', '')
                    wallet_balance = self.api.get_token_balance(token_symbol)
                    
                    if wallet_balance > 0:
                        # 更新数量为钱包实际余额
                        old_quantity = quantity
                        quantity = wallet_balance
                        self.trader.tokens[symbol]['last_buy_quantity'] = wallet_balance
                        self.trader.log_message(f"{display_name} 更新清仓数量: {old_quantity} -> {wallet_balance}（来自钱包接口）")
                        use_wallet_balance = True
                    else:
                        self.trader.log_message(f"{display_name} 无法从钱包获取余额，继续使用系统计算的份额")
                
                self.trader.log_message(f"{display_name} 尝试清仓卖单，价格: {sell_price_adjusted}，数量: {quantity}")
                sell_order_id = self.api.place_single_order(symbol, sell_price_adjusted, "SELL", None, quantity)
                
                if not sell_order_id:
                    sell_retry_count += 1
                    self.trader.log_message(f"{display_name} 清仓卖单下单失败（{sell_retry_count}/{max_sell_retries}），等待1秒后重试")
                    
                    if sell_retry_count >= max_sell_retries:
                        self.trader.log_message(f"{display_name} 清仓卖单下单失败{max_sell_retries}次，停止清仓")
                        return
                    
                    time.sleep(random.uniform(0, 1))
                    # 重新获取最新价格
                    price_data = self.api.get_token_price(symbol)
                    if price_data and price_data.get('price'):
                        sell_price = float(price_data['price'])
                        self.trader.log_message(f"{display_name} 重新获取价格: {sell_price}")
                    else:
                        self.trader.log_message(f"{display_name} 重新获取价格失败，使用原价格")
            
            if sell_order_id:
                self.trader.log_message(f"{display_name} 清仓卖单下单成功，order_id: {sell_order_id}，价格: {sell_price_adjusted}")
                
                # 根据是否为全局清理选择不同的订单状态检查逻辑
                if is_global_cleanup:
                    # 全局清理：使用简化的状态检查（不检查自动交易状态）
                    sell_filled = self.check_cleanup_order_status(sell_order_id, display_name, "SELL")
                else:
                    # 单个代币停止：使用正常的订单状态检查逻辑
                    sell_filled = self.trader.order_handler.handle_order_status(symbol, sell_order_id, display_name, "SELL")
                
                if sell_filled:
                    # 清零持有份额
                    self.trader.tokens[symbol]['last_buy_quantity'] = 0
                    self.trader.tokens[symbol]['last_buy_amount'] = 0
                    self.trader.log_message(f"{display_name} 清仓完成，已清零持有份额")
                else:
                    self.trader.log_message(f"{display_name} 清仓卖单未成交或被取消")
            
        except Exception as e:
            self.trader.log_message(f"{display_name} 执行清仓卖单异常: {str(e)}")
    
    def check_cleanup_order_status(self, order_id, display_name, side, check_count=0, max_checks=5):
        """
        检查清仓订单状态（简化版，不检查自动交易状态）
        
        Args:
            order_id: 订单ID
            display_name: 显示名称
            side: 订单方向
            check_count: 当前检查次数
            max_checks: 最大检查次数
            
        Returns:
            bool: 订单成交返回True，否则返回False
        """
        try:
            # 等待随机时间（和正常流程一样）
            time.sleep(random.uniform(1, 2))
            
            # 检查订单状态
            order_status = self.api.check_single_order_filled(order_id)
            self.trader.log_message(f"{display_name} 检查清仓{side}单状态: {order_status}, 检查次数: {check_count + 1}")
            
            if order_status == "FILLED":
                self.trader.log_message(f"{display_name} 清仓{side}单已成交")
                return True
            elif order_status == "PARTIALLY_FILLED":
                self.trader.log_message(f"{display_name} 清仓{side}单部分成交")
                return True  # 部分成交也算成功
            elif order_status in ["CANCELED", "REJECTED", "EXPIRED"]:
                self.trader.log_message(f"{display_name} 清仓{side}单失败，状态: {order_status}")
                return False
            else:
                # 未成交，检查次数是否达到上限
                if check_count + 1 < max_checks:
                    self.trader.log_message(f"{display_name} 清仓{side}单尚未成交，2秒后继续检查")
                    return self.check_cleanup_order_status(order_id, display_name, side, check_count + 1, max_checks)
                else:
                    self.trader.log_message(f"{display_name} 清仓{side}单约10秒未成交，取消订单")
                    try:
                        self.api.cancel_all_orders()
                        # 取消后等待2秒，然后双重检查订单状态
                        time.sleep(2)
                        self.trader.log_message(f"{display_name} 取消后双重检查清仓订单状态")
                        final_status = self.api.check_single_order_filled(order_id)
                        
                        if final_status in ["FILLED", "PARTIALLY_FILLED"]:
                            self.trader.log_message(f"{display_name} 清仓订单在取消前已成交，状态: {final_status}")
                            return True
                        else:
                            self.trader.log_message(f"{display_name} 清仓订单确认未成交，状态: {final_status}")
                            return False
                    except Exception as e:
                        self.trader.log_message(f"{display_name} 取消清仓订单异常: {str(e)}")
                        return False
                        
        except Exception as e:
            self.trader.log_message(f"{display_name} 检查清仓订单状态异常: {str(e)}")
            return False
    
    def auto_trade_worker(self, symbol):
        """
        自动交易工作线程 - 单向交易模式
        
        Args:
            symbol: 交易对符号
        """
        trade_count = self.trader.tokens[symbol].get('trade_count', 1)
        initial_trade_count = trade_count  # 保存初始计划的交易次数
        completed_trades = 0
        display_name = self.trader.tokens[symbol].get('display_name', symbol)
        
        self.trader.log_message(f"{display_name} 开始自动交易，目标次数: {trade_count}")
        
        # 开始自动交易
        while self.trader.auto_trading.get(symbol, False) and completed_trades < trade_count:
            try:
                # 添加调试信息
                self.trader.log_message(f"[DEBUG] {display_name} 进入交易循环，auto_trading状态: {self.trader.auto_trading.get(symbol, False)}")
                
                # 1. 获取价格（已内置重试机制）
                price_data = self.trader.get_token_price(symbol)
                if not price_data:
                    self.trader.log_message(f"{display_name} 获取价格失败，跳过当前交易")
                    continue
                
                current_price = float(price_data['price'])
                time.sleep(random.uniform(1, 2))
                # 2. 下买单（重试机制，最多5次）- 使用最新价格+0.00000001提高撮合优先级
                buy_order_id = None
                buy_retry_count = 0
                max_buy_retries = 5
                
                while self.trader.auto_trading.get(symbol, False) and not buy_order_id and buy_retry_count < max_buy_retries:
                    buy_price = current_price + 0.0000001  # 买单价格提高0.00000001
                    buy_order_id = self.place_single_order(symbol, buy_price, "BUY")
                    # buy_order_id = None
                    
                    if not buy_order_id:
                        buy_retry_count += 1
                        self.trader.log_message(f"{display_name} 买单下单失败（{buy_retry_count}/{max_buy_retries}），等待1秒后重试")
                        
                        if buy_retry_count >= max_buy_retries:
                            self.trader.log_message(f"{display_name} 买单下单失败{max_buy_retries}次，退出当前交易循环")
                            self.trader.trade_success_flag = False
                            break
                        
                        time.sleep(random.uniform(0, 1))
                        # 重新获取价格
                        price_data = self.trader.get_token_price(symbol)
                        if price_data:
                            current_price = float(price_data['price'])
                
                # 如果买单下单失败，跳出外层循环
                if not buy_order_id:
                    break
                
                # 如果自动交易被停止，跳出外层循环
                if not self.trader.auto_trading.get(symbol, False):
                    break
                
                self.trader.log_message(f"{display_name} 买单下单成功，order_id: {buy_order_id}，价格为: {buy_price}")
                
                # 3. 等待买单成交（使用递归方法处理）
                self.trader.log_message(f"[DEBUG] {display_name} 开始等待买单成交，auto_trading状态: {self.trader.auto_trading.get(symbol, False)}")
                buy_filled = self.trader.order_handler.handle_order_status(symbol, buy_order_id, display_name, "BUY")
                
                # 如果自动交易被停止，跳出外层循环
                if not self.trader.auto_trading.get(symbol, False):
                    self.trader.log_message(f"{display_name} 自动交易已停止，退出交易循环")
                    break
                
                # 如果买单失败，跳出外层循环
                if not buy_filled:
                    self.trader.trade_success_flag = False  # 设置交易失败标识
                    self.trader.log_message(f"{display_name} 买单失败，退出交易循环")
                    break
                
                # 4. 获取最新价格（已内置重试机制）
                price_data = self.trader.get_token_price(symbol)
                if not price_data:
                    # 卖单时如果获取不到价格，使用买单价格
                    self.trader.log_message(f"{display_name} 获取最新价格失败，使用买单价格作为卖单价格")
                    sell_price = buy_price
                else:
                    sell_price = float(price_data['price'])
                
                # 5. 下卖单（最多重试5次）- 使用最新价格-0.00000001提高撮合优先级
                # 重要：买单已成交，必须确保卖出，否则资金被占用无法进行下一次交易
                sell_order_id = None
                sell_retry_count = 0
                max_sell_retries = 5
                use_wallet_balance = False  # 标记是否使用钱包接口获取的余额
                time.sleep(random.uniform(1, 2))
                
                while self.trader.auto_trading.get(symbol, False) and not sell_order_id and sell_retry_count < max_sell_retries:
                    sell_price_adjusted = sell_price - 0.0000001  # 卖单价格降低0.00000001
                    
                    # 如果是重试且之前失败过，使用钱包接口获取实际余额
                    if sell_retry_count > 0 and not use_wallet_balance:
                        self.trader.log_message(f"{display_name} 卖单失败，尝试从钱包接口获取实际持有份额")
                        
                        # 从symbol中提取代币符号（例如 "ALPHA_195USDT" -> "ALPHA_195"）
                        token_symbol = symbol.replace('USDT', '')
                        wallet_balance = self.api.get_token_balance(token_symbol)
                        
                        if wallet_balance > 0:
                            # 更新 last_buy_quantity 为钱包实际余额
                            old_quantity = self.trader.tokens[symbol].get('last_buy_quantity', 0)
                            self.trader.tokens[symbol]['last_buy_quantity'] = wallet_balance
                            self.trader.log_message(f"{display_name} 更新持有份额: {old_quantity} -> {wallet_balance}（来自钱包接口）")
                            use_wallet_balance = True
                        else:
                            self.trader.log_message(f"{display_name} 无法从钱包获取余额，继续使用系统计算的份额")
                    
                    sell_order_id = self.place_single_order(symbol, sell_price_adjusted, "SELL")
                    
                    if not sell_order_id:
                        sell_retry_count += 1
                        self.trader.log_message(f"{display_name} 卖单下单失败（{sell_retry_count}/{max_sell_retries}），等待1秒后重试")
                        
                        if sell_retry_count >= max_sell_retries:
                            self.trader.log_message(f"{display_name} 卖单下单失败{max_sell_retries}次，触发闹钟提醒，退出当前交易循环")
                            self.trader.trade_success_flag = False
                            # 触发闹钟
                            self.trader.root.after(0, self.trader.play_alarm)
                            break
                        
                        time.sleep(random.uniform(0, 1))
                        # 重新获取最新价格（已内置重试机制）
                        price_data = self.trader.get_token_price(symbol)
                        if price_data:
                            sell_price = float(price_data['price'])
                        else:
                            # 如果无法获取价格，使用买单价格
                            self.trader.log_message(f"{display_name} 重新获取价格失败，使用买单价格")
                            sell_price = buy_price
                
                # 如果自动交易被停止，跳出外层循环
                if not self.trader.auto_trading.get(symbol, False):
                    break
                
                # 如果卖单下单失败，跳出外层循环
                if not sell_order_id:
                    break
                
                self.trader.log_message(f"{display_name} 卖单下单成功，order_id: {sell_order_id}，价格为: {sell_price_adjusted}")
                
                # 6. 等待卖单成交（使用递归方法处理）
                sell_filled = self.trader.order_handler.handle_order_status(symbol, sell_order_id, display_name, "SELL")
                
                # 如果自动交易被停止，跳出外层循环
                if not self.trader.auto_trading.get(symbol, False):
                    break
                
                # 一次买卖完成
                completed_trades += 1
                self.trader.log_message(f"{display_name} 第 {completed_trades} 次买卖完成")
                time.sleep(random.uniform(2, 3))
                
                # 计算损耗（在清空数据之前）
                if symbol in self.trader.tokens:
                    previous_buy_amount = self.trader.tokens[symbol].get('last_buy_amount', 0.0)
                    previous_sell_amount = self.trader.tokens[symbol].get('last_sell_amount', 0.0)
                    
                    # 计算本次交易损耗
                    if previous_buy_amount > 0 and previous_sell_amount > 0:
                        trade_loss = previous_buy_amount - previous_sell_amount
                        # 使用config_manager更新损耗
                        total_loss = self.trader.config_manager.update_trade_loss(trade_loss)
                        self.trader.daily_trade_loss = total_loss  # 同步到trader对象
                        self.trader.log_message(f"计算损耗: 买单成交额 {previous_buy_amount:.2f} - 卖单成交额 {previous_sell_amount:.2f} = {trade_loss:.2f} USDT")
                        self.trader.log_message(f"累计损耗: {total_loss:.2f} USDT")
                        
                        # 更新损耗显示
                        self.trader.root.after(0, self.trader.update_daily_loss_display)
                
                # 清空累计的买单和卖单数据（买卖完成一轮后重置）
                if symbol in self.trader.tokens:
                    previous_quantity = self.trader.tokens[symbol].get('last_buy_quantity', 0.0)
                    previous_buy_amount = self.trader.tokens[symbol].get('last_buy_amount', 0.0)
                    previous_sell_amount = self.trader.tokens[symbol].get('last_sell_amount', 0.0)
                    
                    self.trader.tokens[symbol]['last_buy_quantity'] = 0.0
                    self.trader.tokens[symbol]['last_buy_amount'] = 0.0
                    self.trader.tokens[symbol]['last_sell_amount'] = 0.0
                    
                    self.trader.log_message(f"清空累计交易数据: 买单份额 {previous_quantity} -> 0.0, 买单成交额 {previous_buy_amount:.2f} -> 0.0 USDT, 卖单成交额 {previous_sell_amount:.2f} -> 0.0 USDT")
                
                # 更新成交额
                self.trader.update_trade_amount(symbol, sell_price_adjusted)
                
            except Exception as e:
                self.trader.log_message(f"{display_name} 自动交易出错: {str(e)}")
                time.sleep(random.uniform(0, 1))
        
        # 交易完成
        self.trader.auto_trading[symbol] = False
        self.trader.tokens[symbol]['auto_trading'] = False
        
        # 检查是否提前退出（未完成所有计划的交易）
        if completed_trades < initial_trade_count:
            remaining_trades = initial_trade_count - completed_trades
            self.trader.tokens[symbol]['trade_count'] = remaining_trades
            self.trader.log_message(f"{display_name} 自动交易中途退出，已完成 {completed_trades}/{initial_trade_count} 次，剩余交易次数已更新为 {remaining_trades}")
        else:
            self.trader.log_message(f"{display_name} 自动交易完成，共完成 {completed_trades} 次交易")
        
        # 更新表格显示
        self.trader.root.after(0, lambda: self.trader.update_tree_view())

