#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理模块
Logger Module for Binance Auto Trade System
"""

import os
import json
from datetime import datetime
import tkinter as tk


class Logger:
    """日志管理类 - 负责系统运行日志和交易详情日志的记录"""
    
    def __init__(self, log_dir="log", log_widget=None):
        """
        初始化日志管理器
        
        Args:
            log_dir: 日志文件存储目录，默认为 "log"
            log_widget: tkinter的文本控件（可选），用于在GUI界面显示日志
        """
        self.log_dir = log_dir
        self.log_widget = log_widget
        
        # 创建日志目录
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def set_log_widget(self, log_widget):
        """
        设置日志显示控件
        
        Args:
            log_widget: tkinter的scrolledtext.ScrolledText控件
        """
        self.log_widget = log_widget
    
    def log_message(self, message):
        """
        添加日志消息 - 同时记录到控制台、GUI界面和文件
        
        Args:
            message: 要记录的日志消息
        """
        now = datetime.now()
        timestamp = now.strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}\n"
        
        # 1. 显示到GUI界面
        if self.log_widget:
            try:
                self.log_widget.insert(tk.END, log_msg)
                self.log_widget.see(tk.END)
                
                # 限制日志行数，避免内存占用过大
                lines = self.log_widget.get("1.0", tk.END).count('\n')
                if lines > 100:
                    self.log_widget.delete("1.0", "10.0")
            except Exception as e:
                print(f"GUI日志显示失败: {str(e)}")
        else:
            # 如果没有GUI控件，打印到控制台
            print(log_msg.strip())
        
        # 2. 写入到日志文件
        try:
            # 创建日期目录
            date_str = now.strftime("%Y-%m-%d")
            date_dir = os.path.join(self.log_dir, date_str)
            if not os.path.exists(date_dir):
                os.makedirs(date_dir)
            
            # 日志文件路径
            log_file = os.path.join(date_dir, "system_running_log.txt")
            
            # 追加模式写入日志
            with open(log_file, 'a', encoding='utf-8') as f:
                full_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{full_timestamp}] {message}\n")
        except Exception as e:
            # 如果写入文件失败，只打印到控制台，不影响程序运行
            print(f"日志文件写入失败: {str(e)}")
    
    def log_trade_detail(self, trade_detail):
        """
        记录交易详情到文件
        
        Args:
            trade_detail: 交易详情字典，包含以下字段：
                - timestamp: 交易时间
                - symbol: 代币符号
                - side: 交易方向 (BUY/SELL)
                - price: 交易价格
                - status: 订单状态
                - custom_quantity: 自定义数量（可选）
                - order_id: 订单ID（可选）
                - error: 错误信息（可选）
                - request_params: 请求参数（可选）
                - response: 响应信息（可选）
        """
        try:
            # 创建日期目录
            date_str = datetime.now().strftime('%Y-%m-%d')
            date_dir = os.path.join(self.log_dir, date_str)
            if not os.path.exists(date_dir):
                os.makedirs(date_dir)
            
            # 交易详情日志文件路径
            trade_log_file = os.path.join(date_dir, "trade_detail_log.txt")
            
            with open(trade_log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'=' * 80}\n")
                f.write(f"时间: {trade_detail.get('timestamp', 'N/A')}\n")
                f.write(f"代币: {trade_detail.get('symbol', 'N/A')}\n")
                f.write(f"方向: {trade_detail.get('side', 'N/A')}\n")
                f.write(f"价格: {trade_detail.get('price', 'N/A')}\n")
                f.write(f"自定义数量: {trade_detail.get('custom_quantity', 'None')}\n")
                f.write(f"状态: {trade_detail.get('status', 'N/A')}\n")
                
                if 'order_id' in trade_detail:
                    f.write(f"订单ID: {trade_detail['order_id']}\n")
                
                if 'error' in trade_detail:
                    f.write(f"错误信息: {trade_detail['error']}\n")
                
                if 'request_params' in trade_detail:
                    f.write(f"请求参数:\n")
                    f.write(f"  URL: {trade_detail['request_params'].get('url', 'N/A')}\n")
                    if 'payload' in trade_detail['request_params']:
                        f.write(f"  Payload: {json.dumps(trade_detail['request_params']['payload'], indent=2, ensure_ascii=False)}\n")
                
                if 'response' in trade_detail:
                    f.write(f"响应信息:\n")
                    f.write(f"  状态码: {trade_detail['response'].get('status_code', 'N/A')}\n")
                    if 'json' in trade_detail['response']:
                        f.write(f"  响应数据: {json.dumps(trade_detail['response']['json'], indent=2, ensure_ascii=False)}\n")
                    elif 'text' in trade_detail['response']:
                        f.write(f"  响应文本: {trade_detail['response']['text']}\n")
                
                f.write(f"{'=' * 80}\n")
                
        except Exception as e:
            print(f"写入交易详情失败: {e}")
    
    def log_error(self, error_message):
        """
        记录错误信息到错误日志文件
        
        Args:
            error_message: 错误消息
        """
        try:
            # 同时记录到系统日志
            self.log_message(f"[ERROR] {error_message}")
            
            # 创建日期目录
            date_str = datetime.now().strftime('%Y-%m-%d')
            date_dir = os.path.join(self.log_dir, date_str)
            if not os.path.exists(date_dir):
                os.makedirs(date_dir)
            
            # 错误日志文件路径
            error_log_file = os.path.join(date_dir, "error_log.txt")
            
            with open(error_log_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {error_message}\n")
                
        except Exception as e:
            print(f"写入错误日志失败: {e}")


# 创建全局日志实例（可选）
_global_logger = None


def get_logger(log_dir="log", log_widget=None):
    """
    获取全局日志实例（单例模式）
    
    Args:
        log_dir: 日志目录
        log_widget: GUI日志控件
        
    Returns:
        Logger: 日志实例
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = Logger(log_dir, log_widget)
    return _global_logger


def set_global_logger(logger):
    """
    设置全局日志实例
    
    Args:
        logger: Logger实例
    """
    global _global_logger
    _global_logger = logger

