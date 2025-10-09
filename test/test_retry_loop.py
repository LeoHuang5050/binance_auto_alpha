#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试当 place_single_order 返回 None 时重试循环的执行情况
"""

import time
import random
from datetime import datetime

class MockBinanceTrader:
    def __init__(self):
        self.auto_trading = {}
        self.tokens = {}
        self.log_messages = []
        
    def log_message(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        self.log_messages.append(log_msg)
        
    def place_single_order(self, symbol, price, side, custom_quantity=None):
        """模拟 place_single_order 方法，总是返回 None"""
        self.log_message(f"place_single_order 被调用: {symbol}, {price}, {side}")
        self.log_message(f"模拟下单失败，返回 None")
        return None
        
    def get_token_price(self, symbol):
        """模拟获取价格，返回递增的价格"""
        if not hasattr(self, '_price_counter'):
            self._price_counter = {}
        if symbol not in self._price_counter:
            self._price_counter[symbol] = 0.2236
            
        # 每次调用价格递增 0.0001
        self._price_counter[symbol] += 0.0001
        price = self._price_counter[symbol]
        
        self.log_message(f"get_token_price 被调用: {symbol}, 返回价格: {price}")
        return {'price': str(price)}

def test_retry_loop():
    """测试重试循环的执行情况"""
    print("=" * 60)
    print("测试重试循环执行情况")
    print("=" * 60)
    
    trader = MockBinanceTrader()
    
    # 设置测试参数
    symbol = "ALPHA_373USDT"
    display_name = "ALEO"
    current_price = 0.2236
    
    # 设置自动交易状态
    trader.auto_trading[symbol] = True
    
    print(f"\n测试参数:")
    print(f"  代币: {symbol}")
    print(f"  显示名称: {display_name}")
    print(f"  初始价格: {current_price}")
    print(f"  自动交易状态: {trader.auto_trading.get(symbol, False)}")
    
    print(f"\n开始测试重试循环...")
    print("-" * 40)
    
    # 模拟重试循环（限制次数避免无限循环）
    buy_order_id = None
    loop_count = 0
    max_loops = 5  # 限制循环次数用于测试
    
    while trader.auto_trading.get(symbol, False) and not buy_order_id and loop_count < max_loops:
        loop_count += 1
        trader.log_message(f"=== 循环第 {loop_count} 次 ===")
        trader.log_message(f"循环条件检查:")
        trader.log_message(f"  auto_trading.get(symbol, False): {trader.auto_trading.get(symbol, False)}")
        trader.log_message(f"  not buy_order_id: {not buy_order_id}")
        trader.log_message(f"  buy_order_id 当前值: {buy_order_id}")
        
        buy_order_id = trader.place_single_order(symbol, current_price, "BUY")
        trader.log_message(f"place_single_order 返回值: {buy_order_id}")
        
        if not buy_order_id:
            trader.log_message(f"{display_name} 买单下单失败，等待1秒后重试")
            time.sleep(0.1)  # 测试时缩短等待时间
            # 重新获取价格
            price_data = trader.get_token_price(symbol)
            if price_data:
                current_price = float(price_data['price'])
                trader.log_message(f"更新价格: {current_price}")
            else:
                trader.log_message(f"获取价格失败")
        else:
            trader.log_message(f"买单下单成功，order_id: {buy_order_id}")
        
        trader.log_message(f"循环结束，buy_order_id: {buy_order_id}")
        print("-" * 40)
    
    # 检查循环退出原因
    print(f"\n循环退出分析:")
    print(f"  总循环次数: {loop_count}")
    print(f"  最终 buy_order_id: {buy_order_id}")
    print(f"  自动交易状态: {trader.auto_trading.get(symbol, False)}")
    
    if loop_count >= max_loops:
        print(f"  退出原因: 达到最大循环次数限制 ({max_loops})")
    elif not trader.auto_trading.get(symbol, False):
        print(f"  退出原因: 自动交易被停止")
    elif buy_order_id:
        print(f"  退出原因: 买单成功")
    else:
        print(f"  退出原因: 未知")
    
    print(f"\n日志记录:")
    for i, log in enumerate(trader.log_messages, 1):
        print(f"  {i:2d}. {log}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

def test_retry_loop_with_auto_trading_stop():
    """测试当自动交易被停止时的循环行为"""
    print("\n" + "=" * 60)
    print("测试自动交易停止时的循环行为")
    print("=" * 60)
    
    trader = MockBinanceTrader()
    
    # 设置测试参数
    symbol = "ALPHA_373USDT"
    display_name = "ALEO"
    current_price = 0.2236
    
    # 设置自动交易状态
    trader.auto_trading[symbol] = True
    
    print(f"\n开始测试，3秒后停止自动交易...")
    
    # 启动一个线程在3秒后停止自动交易
    import threading
    def stop_trading():
        time.sleep(3)
        trader.auto_trading[symbol] = False
        trader.log_message("自动交易已停止")
    
    stop_thread = threading.Thread(target=stop_trading)
    stop_thread.start()
    
    # 模拟重试循环
    buy_order_id = None
    loop_count = 0
    
    while trader.auto_trading.get(symbol, False) and not buy_order_id:
        loop_count += 1
        trader.log_message(f"=== 循环第 {loop_count} 次 ===")
        
        buy_order_id = trader.place_single_order(symbol, current_price, "BUY")
        
        if not buy_order_id:
            trader.log_message(f"{display_name} 买单下单失败，等待1秒后重试")
            time.sleep(0.5)  # 测试时缩短等待时间
            # 重新获取价格
            price_data = trader.get_token_price(symbol)
            if price_data:
                current_price = float(price_data['price'])
        else:
            trader.log_message(f"买单下单成功，order_id: {buy_order_id}")
    
    # 等待停止线程完成
    stop_thread.join()
    
    print(f"\n循环退出分析:")
    print(f"  总循环次数: {loop_count}")
    print(f"  最终 buy_order_id: {buy_order_id}")
    print(f"  自动交易状态: {trader.auto_trading.get(symbol, False)}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_retry_loop()
    test_retry_loop_with_auto_trading_stop()
