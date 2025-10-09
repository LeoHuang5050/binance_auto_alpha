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
        
        # 统计数据
        self.daily_total_amount = 0.0  # 今日交易总额
        self.daily_trade_loss = 0.0    # 今日交易损耗
        self.last_trade_date = None    # 最后交易日期
    
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
                    
                    # 加载统计数据
                    self.daily_total_amount = config.get('daily_total_amount', 0.0)
                    self.daily_trade_loss = config.get('daily_trade_loss', 0.0)
                    self.last_trade_date = config.get('last_trade_date')
                    
                    print(f"已加载今日交易总额: {self.daily_total_amount:.2f} USDT")
                    print(f"已加载今日交易损耗: {self.daily_trade_loss:.2f} USDT")
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
                'daily_total_amount': self.daily_total_amount,
                'daily_trade_loss': self.daily_trade_loss,
                'last_trade_date': self.last_trade_date
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
                self.last_trade_date = today
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
        更新今日交易损耗
        
        Args:
            loss_amount: 损耗金额
            
        Returns:
            float: 更新后的损耗
        """
        self.daily_trade_loss += loss_amount
        self.save_config()
        return self.daily_trade_loss
    
    def set_credentials(self, csrf_token, cookie):
        """
        设置认证信息
        
        Args:
            csrf_token: CSRF令牌
            cookie: Cookie字符串
        """
        self.csrf_token = csrf_token
        self.cookie = cookie
        self.save_config()
    
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

