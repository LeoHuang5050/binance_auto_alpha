import time
import random

class TradingBot:
    def __init__(self):
        self.auto_trading = {}  # 自动交易状态字典
        self.tokens = {}  # 交易对配置字典
        self.root = None  # 假设的UI根对象
        # 其他初始化代码...

    def auto_trade_worker(self, symbol):
        """自动交易工作线程 - 单向交易模式"""
        trade_count = self.tokens[symbol].get('trade_count', 1)
        completed_trades = 0
        display_name = self.tokens[symbol].get('display_name', symbol)
        
        self.log_message(f"{display_name} 开始自动交易，目标次数: {trade_count}")
        
        while self.auto_trading.get(symbol, False) and completed_trades < trade_count:
            try:
                self.log_message(f"[DEBUG] {display_name} 进入交易循环，auto_trading状态: {self.auto_trading.get(symbol, False)}")
                
                # 1. 获取价格
                price_data = self.get_token_price(symbol)
                if not price_data:
                    self.log_message(f"{display_name} 获取价格失败，等待1秒后重试")
                    time.sleep(random.uniform(0, 1))
                    continue
                
                current_price = float(price_data['price'])
                
                # 2. 下买单（重试机制）
                buy_order_id = None
                while self.auto_trading.get(symbol, False) and not buy_order_id:
                    buy_order_id = self.place_single_order(symbol, current_price, "BUY")
                    if not buy_order_id:
                        self.log_message(f"{display_name} 买单下单失败，等待1秒后重试")
                        time.sleep(random.uniform(0, 1))
                        price_data = self.get_token_price(symbol)
                        if price_data:
                            current_price = float(price_data['price'])
                
                if not self.auto_trading.get(symbol, False):
                    break
                
                self.log_message(f"{display_name} 买单下单成功，价格为: {current_price}")
                
                # 3. 等待买单成交（递归检查）
                buy_filled = self.handle_order_status(symbol, buy_order_id, display_name, "BUY")
                if not self.auto_trading.get(symbol, False) or not buy_filled:
                    break
                
                # 4. 获取最新价格
                price_data = self.get_token_price(symbol)
                if not price_data:
                    self.log_message(f"{display_name} 获取最新价格失败，等待1秒后重试")
                    time.sleep(random.uniform(0, 1))
                    continue
                
                sell_price = float(price_data['price'])
                
                # 5. 下卖单（重试机制）
                sell_order_id = None
                while self.auto_trading.get(symbol, False) and not sell_order_id:
                    sell_order_id = self.place_single_order(symbol, sell_price, "SELL")
                    if not sell_order_id:
                        self.log_message(f"{display_name} 卖单下单失败，等待1秒后重试")
                        time.sleep(random.uniform(0, 1))
                        price_data = self.get_token_price(symbol)
                        if price_data:
                            sell_price = float(price_data['price'])
                
                if not self.auto_trading.get(symbol, False):
                    break
                
                self.log_message(f"{display_name} 卖单下单成功，价格为: {sell_price}")
                
                # 6. 等待卖单成交（递归检查）
                sell_filled = self.handle_order_status(symbol, sell_order_id, display_name, "SELL")
                if not self.auto_trading.get(symbol, False) or not sell_filled:
                    break
                
                # 7. 一次买卖完成
                completed_trades += 1
                self.log_message(f"{display_name} 第 {completed_trades} 次买卖完成")
                
                # 更新成交额
                self.update_trade_amount(symbol, sell_price)
                
            except Exception as e:
                self.log_message(f"{display_name} 自动交易出错: {str(e)}")
                time.sleep(random.uniform(0, 1))
        
        # 交易完成
        self.auto_trading[symbol] = False
        self.tokens[symbol]['auto_trading'] = False
        self.root.after(0, lambda: self.update_tree_view())
        self.log_message(f"{display_name} 自动交易完成，共完成 {completed_trades} 次交易")

    def handle_order_status(self, symbol, order_id, display_name, side, check_count=0, max_checks=6):
        """
        递归检查订单状态
        :param symbol: 交易对符号
        :param order_id: 订单ID
        :param display_name: 显示名称
        :param side: 订单方向（"BUY" 或 "SELL"）
        :param check_count: 当前检查次数
        :param max_checks: 最大检查次数
        :return: True if order is filled, False otherwise
        """
        # 检查自动交易状态
        if not self.auto_trading.get(symbol, False):
            self.log_message(f"[INFO] {display_name} 自动交易已停止")
            return False

        # 等待随机时间
        time.sleep(random.uniform(1, 2))

        # 检查订单状态
        try:
            order_status = self.check_single_order_filled(order_id)
            self.log_message(f"[DEBUG] {display_name} 检查{side}单状态: {order_status}, 检查次数: {check_count + 1}")
        except Exception as e:
            self.log_message(f"[ERROR] {display_name} 检查{side}单状态失败: {e}")
            time.sleep(random.uniform(0, 1))
            return False

        if order_status == "FILLED":
            self.log_message(f"[INFO] {display_name} {side}单已成交")
            return True
        elif order_status == "PARTIALLY_FILLED":
            self.log_message(f"[INFO] {display_name} {side}单部分成交，开始处理剩余份额")
            try:
                # 获取部分成交订单的详细信息
                partial_order_info = self.get_order_details(order_id)
                if not partial_order_info:
                    self.log_message(f"[ERROR] {display_name} 无法获取{side}单详细信息")
                    return self._retry_place_order(symbol, display_name, side)
                
                # 计算剩余份额
                orig_qty = float(partial_order_info.get('origQty', 0))
                executed_qty = float(partial_order_info.get('executedQty', 0))
                remaining_qty = orig_qty - executed_qty
                
                self.log_message(f"[INFO] {display_name} {side}单部分成交详情:")
                self.log_message(f"  - 原始数量: {orig_qty}")
                self.log_message(f"  - 已成交数量: {executed_qty}")
                self.log_message(f"  - 剩余数量: {remaining_qty}")
                
                # 发送取消请求
                self.cancel_all_orders()
                time.sleep(2)  # 等待取消生效
                
                # 重新检查订单状态
                new_status = self.check_single_order_filled(order_id)
                if new_status == "FILLED":
                    self.log_message(f"[INFO] {display_name} 取消后{side}单已完全成交")
                    return True
                elif new_status == "CANCELED":
                    self.log_message(f"[INFO] {display_name} 订单已取消，使用剩余份额重新下单")
                    return self._retry_place_order_with_remaining_qty(symbol, display_name, side, remaining_qty)
                else:
                    self.log_message(f"[INFO] {display_name} {side}单状态异常: {new_status}，重新下单")
                    return self._retry_place_order(symbol, display_name, side)
            except Exception as e:
                self.log_message(f"[ERROR] {display_name} 取消{side}单或检查状态失败: {e}")
                return self._retry_place_order(symbol, display_name, side)
        else:
            # 未成交，检查次数是否达到上限
            if check_count + 1 < max_checks:
                self.log_message(f"[INFO] {display_name} {side}单尚未成交，2秒后继续检查")
                return self.handle_order_status(symbol, order_id, display_name, side, check_count + 1, max_checks)
            else:
                self.log_message(f"[INFO] {display_name} {side}单约10秒未成交，取消订单")
                try:
                    self.cancel_all_orders()
                except Exception as e:
                    self.log_message(f"[ERROR] {display_name} 取消{side}单失败: {e}")
                return self._retry_place_order(symbol, display_name, side)

    def _retry_place_order(self, symbol, display_name, side):
        """辅助方法：重新获取价格并下单"""
        try:
            price_data = self.get_token_price(symbol)
            if not price_data:
                self.log_message(f"[ERROR] {display_name} 获取{side}单价格失败，等待1秒后重试")
                time.sleep(random.uniform(0, 1))
                return False
            
            current_price = float(price_data['price'])
            order_id = self.place_single_order(symbol, current_price, side)
            if not order_id:
                self.log_message(f"[ERROR] {display_name} {side}单下单失败，等待1秒后重试")
                time.sleep(random.uniform(0, 1))
                return False
            
            self.log_message(f"[INFO] {display_name} {side}单重新下单成功，价格为: {current_price}")
            return self.handle_order_status(symbol, order_id, display_name, side)
        except Exception as e:
            self.log_message(f"[ERROR] {display_name} 重新下{side}单出错: {e}")
            time.sleep(random.uniform(0, 1))
            return False

    def _retry_place_order_with_remaining_qty(self, symbol, display_name, side, remaining_qty):
        """辅助方法：使用剩余份额重新下单"""
        try:
            price_data = self.get_token_price(symbol)
            if not price_data:
                self.log_message(f"[ERROR] {display_name} 获取{side}单价格失败，等待1秒后重试")
                time.sleep(random.uniform(0, 1))
                return False
            
            current_price = float(price_data['price'])
            
            # 根据订单方向计算下单数量
            if side == "BUY":
                # 买单：使用剩余份额直接下单
                order_qty = remaining_qty
                self.log_message(f"[INFO] {display_name} 买单剩余份额下单: {order_qty}")
            else:
                # 卖单：需要计算多次成交的买单份额之和减去手续费
                total_bought_qty = self.calculate_total_bought_quantity(symbol)
                if total_bought_qty <= 0:
                    self.log_message(f"[ERROR] {display_name} 无法计算已买入总份额")
                    return False
                
                # 计算手续费 (0.01%)
                fee_rate = 0.0001
                fee_amount = total_bought_qty * fee_rate
                order_qty = total_bought_qty - fee_amount
                
                self.log_message(f"[INFO] {display_name} 卖单计算:")
                self.log_message(f"  - 总买入份额: {total_bought_qty}")
                self.log_message(f"  - 手续费: {fee_amount}")
                self.log_message(f"  - 可卖份额: {order_qty}")
            
            # 使用自定义数量下单
            order_id = self.place_single_order_with_qty(symbol, current_price, side, order_qty)
            if not order_id:
                self.log_message(f"[ERROR] {display_name} {side}单下单失败，等待1秒后重试")
                time.sleep(random.uniform(0, 1))
                return False
            
            self.log_message(f"[INFO] {display_name} {side}单重新下单成功，价格为: {current_price}, 数量: {order_qty}")
            return self.handle_order_status(symbol, order_id, display_name, side)
        except Exception as e:
            self.log_message(f"[ERROR] {display_name} 重新下{side}单出错: {e}")
            time.sleep(random.uniform(0, 1))
            return False

    # 假设的其他方法（需要你实现实际逻辑）
    def check_single_order_filled(self, order_id):
        # 模拟检查订单状态
        # 第一次调用返回部分成交，第二次调用返回已取消
        if not hasattr(self, '_order_check_count'):
            self._order_check_count = 0
        self._order_check_count += 1
        
        if self._order_check_count == 1:
            return "PARTIALLY_FILLED"  # 第一次检查：部分成交
        else:
            return "CANCELED"  # 第二次检查：已取消

    def get_order_details(self, order_id):
        """获取订单详细信息"""
        # 模拟获取订单详情，返回您提供的部分成交订单示例
        return {
            "orderId": "150950331",
            "symbol": "ALPHA_347USDT",
            "status": "PARTIALLY_FILLED",
            "clientOrderId": "web_28ba0979d6a149ee802d4cffddbba653",
            "price": "0.10395706",
            "avgPrice": "0.10395706",
            "origQty": "9907.93",
            "executedQty": "4775.28",
            "cumQuote": "496.42406947",
            "timeInForce": "GTC",
            "type": "LIMIT",
            "side": "BUY",
            "stopPrice": "0",
            "origType": "LIMIT",
            "time": 1759060002169,
            "updateTime": 1759060014276,
            "orderListId": "-1",
            "pageId": "12563616204",
            "baseAsset": "ALPHA_347",
            "quoteAsset": "USDT",
            "contingencyType": None,
            "otoOrderPosition": None
        }
    
    def get_canceled_order_details(self, order_id):
        """获取取消后的订单详细信息"""
        # 模拟获取取消后的订单详情
        return {
            "orderId": "150950331",
            "symbol": "ALPHA_347USDT",
            "status": "CANCELED",
            "clientOrderId": "web_28ba0979d6a149ee802d4cffddbba653",
            "price": "0.10395706",
            "avgPrice": "0.10395706",
            "origQty": "9907.93",
            "executedQty": "4775.28",
            "cumQuote": "496.42406947",
            "timeInForce": "GTC",
            "type": "LIMIT",
            "side": "BUY",
            "stopPrice": "0",
            "origType": "LIMIT",
            "time": 1759060002169,
            "updateTime": 1759060014276,
            "orderListId": "-1",
            "pageId": "12563616204",
            "baseAsset": "ALPHA_347",
            "quoteAsset": "USDT",
            "contingencyType": None,
            "otoOrderPosition": None
        }

    def calculate_total_bought_quantity(self, symbol):
        """计算已买入的总份额"""
        # 模拟计算已买入总份额
        # 实际实现中应该查询所有已成交的买单并求和
        return 10000.0  # 示例返回值

    def cancel_all_orders(self):
        # 模拟取消订单
        self.log_message("Canceling all orders")

    def get_token_price(self, symbol):
        # 模拟获取价格
        return {"price": 100.0}  # 示例返回值

    def place_single_order(self, symbol, price, side):
        # 模拟下单
        self.log_message(f"Placing {side} order for {symbol} at price {price}")
        return "new_order_id"  # 示例订单ID

    def place_single_order_with_qty(self, symbol, price, side, quantity):
        """使用自定义数量下单"""
        # 模拟使用自定义数量下单
        self.log_message(f"Placing {side} order for {symbol} at price {price} with quantity {quantity}")
        return "new_order_id_with_qty"  # 示例订单ID

    def update_trade_amount(self, symbol, price):
        # 模拟更新成交额
        self.log_message(f"Updating trade amount for {symbol} at price {price}")

    def log_message(self, message):
        # 模拟日志记录
        print(message)

    def update_tree_view(self):
        # 模拟更新UI
        self.log_message("Updating tree view")

# 测试代码
if __name__ == "__main__":
    bot = TradingBot()
    bot.auto_trading["BTCUSDT"] = True
    bot.tokens["BTCUSDT"] = {"display_name": "BTC Trading", "trade_count": 1, "auto_trading": True}
    bot.auto_trade_worker("BTCUSDT")