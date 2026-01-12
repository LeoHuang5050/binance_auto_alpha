#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
Config Manager Module for Binance Auto Trade System
"""

import os
import json
from datetime import datetime


class ConfigManager:
    """配置管理类 - 负责配置文件的加载、保存和统计数据管理"""
    
    def __init__(self, config_file='config.json', logger=None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
            logger: Logger实例
        """
        self.config_file = config_file
        self.logger = logger
        
        # 认证信息
        self.csrf_token = None
        self.cookie = None
        self.csrf_token_updated_time = None  # CSRF token更新时间
        self.extra_headers = {}  # 额外的 header 字段
        
        # 统计数据
        self.daily_total_amount = 0.0  # 今日交易总额
        self.daily_trade_loss = 0.0    # 今日交易损耗
        self.daily_completed_trades = 0  # 今日已完成交易次数
        self.last_trade_date = None    # 最后交易日期
        
        # 资金账户余额相关
        self.daily_initial_balance = None  # 当天初始资金（USDT）
        self.daily_end_balance = None     # 当天结束资金（USDT）
    
    def load_config(self):
        """
        加载配置文件
        
        Returns:
            dict: 配置字典，失败返回空字典
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                    # 加载认证信息
                    self.csrf_token = config.get('csrf_token')
                    self.cookie = config.get('cookie')
                    self.csrf_token_updated_time = config.get('csrf_token_updated_time')
                    self.extra_headers = config.get('extra_headers', {})
                    
                    # 加载统计数据
                    self.daily_total_amount = config.get('daily_total_amount', 0.0)
                    self.daily_trade_loss = config.get('daily_trade_loss', 0.0)
                    self.daily_completed_trades = config.get('daily_completed_trades', 0)
                    self.last_trade_date = config.get('last_trade_date')
                    
                    # 加载资金账户余额
                    self.daily_initial_balance = config.get('daily_initial_balance')
                    self.daily_end_balance = config.get('daily_end_balance')
                    
                    print(f"已加载今日交易总额: {self.daily_total_amount:.2f} USDT")
                    print(f"已加载今日交易损耗: {self.daily_trade_loss:.2f} USDT")
                    print(f"已加载今日完成交易次数: {self.daily_completed_trades}")
                    print(f"最后交易日期: {self.last_trade_date}")
                    
                    # 检查是否需要每日归零
                    self.check_daily_reset()
                    
                    if self.csrf_token and self.cookie:
                        print(f"已加载配置: CSRF Token: {self.csrf_token[:10]}..., Cookie: {self.cookie[:50]}...")
                    
                    return config
            else:
                print(f"配置文件 {self.config_file} 不存在，使用默认配置")
                return {}
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            if self.logger:
                self.logger.log_error(f"加载配置文件失败: {e}")
            return {}
    
    def save_config(self):
        """
        保存配置文件
        
        Returns:
            bool: 成功返回True，失败返回False
        """
        try:
            config = {
                'csrf_token': self.csrf_token,
                'cookie': self.cookie,
                'csrf_token_updated_time': self.csrf_token_updated_time,
                'extra_headers': self.extra_headers,
                'daily_total_amount': self.daily_total_amount,
                'daily_trade_loss': self.daily_trade_loss,
                'daily_completed_trades': self.daily_completed_trades,
                'last_trade_date': self.last_trade_date,
                'daily_initial_balance': self.daily_initial_balance,
                'daily_end_balance': self.daily_end_balance
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print("配置已保存")
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            if self.logger:
                self.logger.log_error(f"保存配置文件失败: {e}")
            return False
    
    def check_daily_reset(self):
        """
        检查是否需要每日归零
        
        Returns:
            bool: 如果执行了归零返回True，否则返回False
        """
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            if self.last_trade_date != today:
                # 日期不同，需要归零
                if self.last_trade_date:
                    message = f"检测到日期变化: {self.last_trade_date} -> {today}，今日交易总额和损耗已归零"
                    print(message)
                    if self.logger:
                        self.logger.log_message(message)
                
                self.daily_total_amount = 0.0
                self.daily_trade_loss = 0.0
                self.daily_completed_trades = 0
                self.last_trade_date = today
                self.daily_initial_balance = None
                self.daily_end_balance = None
                self.save_config()
                return True
            return False
        except Exception as e:
            error_msg = f"检查每日归零失败: {str(e)}"
            print(error_msg)
            if self.logger:
                self.logger.log_message(error_msg)
            return False
    
    def update_trade_amount(self, trade_amount):
        """
        更新今日交易总额
        
        Args:
            trade_amount: 交易金额
            
        Returns:
            float: 更新后的总额
        """
        self.daily_total_amount += trade_amount
        self.last_trade_date = datetime.now().strftime('%Y-%m-%d')
        self.save_config()
        return self.daily_total_amount
    
    def update_trade_loss(self, loss_amount):
        """
        更新今日交易损耗（旧方法，保留兼容性）
        
        Args:
            loss_amount: 损耗金额
            
        Returns:
            float: 更新后的损耗
        """
        self.daily_trade_loss += loss_amount
        self.save_config()
        return self.daily_trade_loss
    
    def set_daily_initial_balance(self, balance):
        """
        设置当天初始资金
        
        Args:
            balance: 初始资金余额（USDT）
        """
        self.daily_initial_balance = balance
        self.last_trade_date = datetime.now().strftime('%Y-%m-%d')
        self.save_config()
        if self.logger:
            self.logger.log_message(f"设置当天初始资金: {balance} USDT")
    
    def update_loss_from_balance(self, current_balance):
        """
        根据当前余额更新损耗
        
        Args:
            current_balance: 当前资金账户余额（USDT）
            
        Returns:
            float: 计算后的损耗，如果初始余额不存在则返回None
        """
        if self.daily_initial_balance is None:
            if self.logger:
                self.logger.log_message("未设置初始资金，无法计算损耗")
            return None
        
        # 计算损耗：初始资金 - 当前余额
        loss = self.daily_initial_balance - current_balance
        self.daily_trade_loss = loss
        self.daily_end_balance = current_balance
        self.last_trade_date = datetime.now().strftime('%Y-%m-%d')
        self.save_config()
        
        if self.logger:
            self.logger.log_message(f"更新损耗: 初始资金={self.daily_initial_balance} USDT, 当前余额={current_balance} USDT, 损耗={loss:.2f} USDT")
        
        return loss
    
    def increment_trade_count(self):
        """
        增加交易次数
        
        Returns:
            int: 更新后的交易次数
        """
        self.daily_completed_trades += 1
        self.save_config()
        return self.daily_completed_trades
    
    def set_credentials(self, csrf_token, cookie, extra_headers=None):
        """
        设置认证信息
        
        Args:
            csrf_token: CSRF令牌
            cookie: Cookie字符串
            extra_headers: 额外的 header 字段字典
        """
        self.csrf_token = csrf_token
        self.cookie = cookie
        self.csrf_token_updated_time = datetime.now().isoformat()  # 记录更新时间
        if extra_headers:
            self.extra_headers = extra_headers
        self.save_config()
    
    def get_auth_expiry_info(self):
        """
        获取认证信息过期信息
        
        Returns:
            dict: 包含剩余天数和状态信息的字典
        """
        if not self.csrf_token_updated_time:
            return {'days_remaining': 0, 'status': 'no_auth', 'message': '未设置认证信息'}
        
        try:
            # 解析更新时间
            updated_time = datetime.fromisoformat(self.csrf_token_updated_time)
            current_time = datetime.now()
            
            # 计算天数差
            days_passed = (current_time - updated_time).days
            days_remaining = max(0, 5 - days_passed)  # 假设5天过期
            
            if days_remaining > 2:
                status = 'ok'
                message = f'认证信息还有{days_remaining}天过期'
            elif days_remaining > 0:
                status = 'warning'
                message = f'认证信息还有{days_remaining}天过期，请更新认证信息'
            else:
                status = 'expired'
                message = '认证信息已过期，请立即更新认证信息'
            
            return {
                'days_remaining': days_remaining,
                'status': status,
                'message': message,
                'updated_time': updated_time
            }
        except Exception as e:
            return {'days_remaining': 0, 'status': 'error', 'message': f'计算过期时间失败: {str(e)}'}
    
    def get_credentials(self):
        """
        获取认证信息
        
        Returns:
            tuple: (csrf_token, cookie)
        """
        return self.csrf_token, self.cookie
    
    def get_statistics(self):
        """
        获取统计数据
        
        Returns:
            dict: 统计数据字典
        """
        return {
            'daily_total_amount': self.daily_total_amount,
            'daily_trade_loss': self.daily_trade_loss,
            'last_trade_date': self.last_trade_date
        }
    
    def reset_statistics(self):
        """
        手动重置统计数据
        """
        self.daily_total_amount = 0.0
        self.daily_trade_loss = 0.0
        self.last_trade_date = datetime.now().strftime('%Y-%m-%d')
        self.save_config()
        
        message = "统计数据已手动重置"
        print(message)
        if self.logger:
            self.logger.log_message(message)

