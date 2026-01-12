#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
币安量化交易系统
Binance Auto Trade System
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import threading
import time
import random
from datetime import datetime, timedelta
import sys
import os
import uuid
import hashlib
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 导入日志模块
from logger import Logger
# 导入币安API模块
from binance_api import BinanceAPI
# 导入认证模块
from auth import AuthManager
# 导入Alpha123稳定度数据模块
from alpha123 import Alpha123Client
# 导入订单处理模块
from order_handler import OrderHandler
# 导入配置管理模块
from config_manager import ConfigManager
# 导入交易引擎模块
from trading_engine import TradingEngine

class BinanceTrader:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Binance Auto Trade - 币安量化交易系统")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # 居中显示主窗口
        self.center_window(self.root, 1400, 800)
        
        # 初始化认证管理器
        self.auth_manager = AuthManager()
        
        # 进行MAC地址校验
        if not self.auth_manager.check_mac_permission():
            return  # 权限校验失败，不继续初始化
        
        # 创建log文件夹并初始化日志管理器
        self.log_dir = "log"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # 初始化日志管理器（GUI控件稍后设置）
        self.logger = Logger(log_dir=self.log_dir)
        
        # 初始化配置管理器（先加载配置以获取认证信息）
        self.config_manager = ConfigManager(config_file="config.json", logger=self.logger)
        self.config_manager.load_config()
        
        # 从配置管理器获取认证信息（保留本地引用以便快速访问）
        self.csrf_token = self.config_manager.csrf_token
        self.cookie = self.config_manager.cookie
        
        # 币安ALPHA API基础URL
        self.base_url = "https://www.binance.com/bapi/defi/v1/public/alpha-trade"
        
        # 初始化币安API接口（直接传入认证信息）
        self.api = BinanceAPI(
            base_url=self.base_url, 
            csrf_token=self.csrf_token,
            cookie=self.cookie,
            logger=self.logger,
            extra_headers=self.config_manager.extra_headers
        )
        
        # 存储代币数据
        self.tokens = {}
        
        # 稳定度看板数据
        self.stability_data = []
        self.stability_window = None  # 稳定度看板窗口引用
        
        # 从配置管理器获取统计数据（保留本地引用以便快速访问）
        self.daily_total_amount = self.config_manager.daily_total_amount
        self.daily_trade_loss = self.config_manager.daily_trade_loss
        self.daily_completed_trades = self.config_manager.daily_completed_trades
        self.last_trade_date = self.config_manager.last_trade_date
        
        # 当前买卖交易跟踪
        self.current_sell_amount = 0.0  # 当前买卖交易中卖单的总成交额
        
        # 自动交易状态
        self.auto_trading = {}  # 存储每个代币的自动交易状态
        self.trading_threads = {}  # 存储交易线程
        
        # 4倍自动交易状态
        self.trading_4x_active = False  # 4倍自动交易是否激活
        self.trading_4x_thread = None  # 4倍自动交易线程
        
        # 定时交易状态
        self.scheduled_trading_enabled = False  # 定时交易是否启用
        self.scheduled_trading_thread = None  # 定时交易检查线程
        self.last_scheduled_date = None  # 上次执行定时交易的日期
        
        # 今日交易次数统计
        # daily_completed_trades 现在由 config_manager 管理
        self.alarm_played_today = False  # 今日是否已播放过闹钟
        
        # 闹钟播放状态
        self.alarm_is_playing = False  # 闹钟是否正在播放
        
        # 交易成功标识
        self.trade_success_flag = True  # 标识当前交易是否成功
        
        # 存储输入框和按钮的引用
        
        # 创建界面
        self.create_widgets()
        
        # 加载ALPHA代币ID映射（在GUI日志控件设置之后）
        self.alpha_id_map = self.load_alpha_id_map()
        
        # 初始化Alpha123稳定度数据客户端
        self.alpha123_client = Alpha123Client(logger=self.logger, alpha_id_map=self.alpha_id_map)
        
        # 初始化订单处理器
        self.order_handler = OrderHandler(self)
        
        # 初始化交易引擎
        self.trading_engine = TradingEngine(self)
        
        # 从稳定度看板添加常驻代币
        self.add_permanent_tokens_from_stability()
        
        # 延迟更新统计数据显示，确保界面已完全创建
        self.root.after(100, self.update_daily_total_display)
        self.root.after(100, self.update_daily_loss_display)
        self.root.after(100, self.update_daily_trade_count_display)
        self.root.after(100, self.update_daily_initial_balance_display)
        self.root.after(100, self.update_daily_end_balance_display)
        
        # 延迟获取当天初始资金（确保认证信息已设置）
        self.root.after(500, self.init_daily_balance)
    
    def load_alpha_id_map(self):
        """加载ALPHA代币ID映射，每天只更新一次，如果当天已更新则直接读取文件"""
        from datetime import datetime
        
        # 检查是否需要更新（每天一次）
        need_update = False
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 检查alphaIdMap.json是否存在
        if not os.path.exists('alphaIdMap.json'):
            need_update = True
            print("未找到alphaIdMap.json文件，需要从API获取...")
            self.logger.log_message("未找到alphaIdMap.json文件，需要从API获取...")
        else:
            # 检查文件修改时间是否为今天
            try:
                file_mtime = datetime.fromtimestamp(os.path.getmtime('alphaIdMap.json'))
                file_date = file_mtime.strftime('%Y-%m-%d')
                
                if file_date != today:
                    need_update = True
                    print(f"Alpha ID映射文件不是今天的（文件日期: {file_date}），需要更新...")
                    self.logger.log_message(f"Alpha ID映射文件不是今天的（文件日期: {file_date}），需要更新...")
                else:
                    print("Alpha ID映射文件是今天的，直接加载...")
                    self.logger.log_message("Alpha ID映射文件是今天的，直接加载...")
            except Exception as e:
                print(f"检查文件时间失败: {e}，尝试从API获取...")
                self.logger.log_message(f"检查文件时间失败: {e}，尝试从API获取...")
                need_update = True
        
        # 如果需要更新，从API获取最新数据
        if need_update:
            try:
                print("正在从币安API获取最新代币列表...")
                self.logger.log_message("正在从币安API获取最新代币列表...")
                token_data = self.api.get_binance_token_list()
                alpha_id_map = self.api.create_alpha_id_map(token_data)
                
                # 保存映射到文件
                with open('alphaIdMap.json', 'w', encoding='utf-8') as f:
                    json.dump(alpha_id_map, f, indent=2, ensure_ascii=False)
                
                success_msg = f"✅ 成功从API获取并保存Alpha ID映射，包含 {len(alpha_id_map)} 个代币"
                print(success_msg)
                self.logger.log_message(success_msg)
                return alpha_id_map
                
            except Exception as e:
                error_msg = f"从API获取代币列表失败: {e}"
                print(error_msg)
                self.logger.log_message(error_msg)
                print("尝试加载现有文件作为备用...")
                self.logger.log_message("尝试加载现有文件作为备用...")
                
                # 如果API调用失败，尝试加载现有文件
                if os.path.exists('alphaIdMap.json'):
                    try:
                        with open('alphaIdMap.json', 'r', encoding='utf-8') as f:
                            existing_map = json.load(f)
                            backup_msg = f"已加载现有Alpha ID映射作为备用，包含 {len(existing_map)} 个代币"
                            print(backup_msg)
                            self.logger.log_message(backup_msg)
                            return existing_map
                    except Exception as file_e:
                        print(f"加载现有文件失败: {file_e}")
                        self.logger.log_message(f"加载现有文件失败: {file_e}")
                        print("使用默认映射")
                        self.logger.log_message("使用默认映射")
                        return {"KOGE": "ALPHA_22"}
                else:
                    print("未找到现有文件，使用默认映射")
                    self.logger.log_message("未找到现有文件，使用默认映射")
                    return {"KOGE": "ALPHA_22"}
        else:
            # 直接加载现有文件
            try:
                with open('alphaIdMap.json', 'r', encoding='utf-8') as f:
                    existing_map = json.load(f)
                    load_msg = f"✅ 已加载现有Alpha ID映射，包含 {len(existing_map)} 个代币"
                    print(load_msg)
                    self.logger.log_message(load_msg)
                    return existing_map
            except Exception as e:
                error_msg = f"加载现有文件失败: {e}"
                print(error_msg)
                self.logger.log_message(error_msg)
                print("使用默认映射")
                self.logger.log_message("使用默认映射")
                return {"KOGE": "ALPHA_22"}
    
    def add_permanent_tokens_from_stability(self):
        """从稳定度看板添加常驻代币"""
        try:
            # 获取稳定度看板数据
            stability_data = self.alpha123_client.fetch_stability_data()
            if not stability_data:
                self.log_message("无法获取稳定度看板数据，将只添加KOGE代币")
                self.add_koge_token()
                return
            
            added_count = 0
            for item in stability_data:
                project = item.get('project', '')
                if not project:
                    continue
                
                # 查找对应的ALPHA ID
                alpha_id = self.alpha_id_map.get(project)
                if not alpha_id:
                    continue
                
                alpha_symbol = f"{alpha_id}USDT"
                
                # 检查代币是否已在监控列表中
                if alpha_symbol in self.tokens:
                    continue
                
                # 获取稳定度看板返回的价格
                stability_price = float(item.get('price', 0))
                
                # 添加代币到监控列表，直接使用稳定度看板的价格
                self.tokens[alpha_symbol] = {
                    'price': stability_price,
                    'last_update': datetime.now(),
                    'display_name': project,
                    'trade_count': 1,
                    'trade_amount': 0.0,
                    'auto_trading': False,
                    'change_24h': 0.0,  # 稳定度看板没有24h变化数据，设为0
                    'last_buy_quantity': 0.0,  # 存储上一个买单的份额
                    'last_buy_amount': 0.0,  # 存储上一个买单的成交额
                    'last_sell_amount': 0.0  # 存储上一个卖单的成交额
                }
                added_count += 1
            
            # 更新表格显示
            self.update_tree_view()
            
            # 记录日志
            if hasattr(self, 'log_text'):
                self.log_message(f"已从稳定度看板添加 {added_count} 个常驻代币")
            else:
                print(f"已从稳定度看板添加 {added_count} 个常驻代币")
            
        except Exception as e:
            self.log_message(f"从稳定度看板添加常驻代币失败: {str(e)}")
            # 如果失败，至少添加KOGE代币
            self.add_koge_token()
    
    def add_koge_token(self):
        """添加常驻的KOGE代币（备用方法）"""
        koge_symbol = "ALPHA_22USDT"  # KOGE的ALPHA ID
        self.tokens[koge_symbol] = {
            'price': 0.0,
            'last_update': datetime.now(),
            'display_name': 'KOGE',
            'trade_count': 1,
            'trade_amount': 0.0,
            'auto_trading': False,
            'last_buy_quantity': 0.0,  # 存储上一个买单的份额
            'last_buy_amount': 0.0,  # 存储上一个买单的成交额
            'last_sell_amount': 0.0  # 存储上一个卖单的成交额
        }
        # 更新表格显示
        self.update_tree_view()
        # 检查log_text是否已创建
        if hasattr(self, 'log_text'):
            self.log_message("已添加常驻代币: KOGE (ALPHA_22USDT)")
        else:
            print("已添加常驻代币: KOGE (ALPHA_22USDT)")
        
        # 立即获取KOGE的价格数据
        self.fetch_koge_price()
    
    
    def fetch_koge_price(self):
        """获取KOGE代币的价格数据"""
        def fetch_data():
            koge_symbol = "ALPHA_22USDT"
            price_data = self.get_token_price(koge_symbol)
            if price_data:
                stats_data = self.get_token_24h_stats(koge_symbol)
                self.root.after(0, lambda: self.update_token_data(koge_symbol, price_data, stats_data, 'KOGE'))
            else:
                self.root.after(0, lambda: self.log_message("获取KOGE价格失败（请先设置认证信息）"))
        
        threading.Thread(target=fetch_data, daemon=True).start()
    
    def create_widgets(self):
        """创建GUI界面组件"""
        # 主标题
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x', padx=10, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="🚀 Binance Auto Trade - 币安量化交易系统", 
            font=('Arial', 18, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(expand=True)
        
        # 输入区域
        input_frame = tk.Frame(self.root, bg='#f0f0f0')
        input_frame.pack(fill='x', padx=10, pady=10)
        
        # 代币输入
        tk.Label(input_frame, text="代币名称:", font=('Arial', 12), bg='#f0f0f0').pack(side='left', padx=5)
        
        self.token_entry = tk.Entry(input_frame, font=('Arial', 12), width=20)
        self.token_entry.pack(side='left', padx=5)
        self.token_entry.bind('<Return>', lambda e: self.add_token())
        
        add_btn = tk.Button(
            input_frame, 
            text="添加代币", 
            command=self.add_token,
            bg='#3498db',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20
        )
        add_btn.pack(side='left', padx=10)
        
        # 统计数据显示区域（原定时交易位置）
        stats_frame = tk.Frame(input_frame, bg='#f0f0f0')
        stats_frame.pack(side='left', padx=(20, 0))
        
        # 今日初始余额
        tk.Label(stats_frame, text="今日初始余额:", font=('Arial', 10, 'bold'), bg='#f0f0f0', fg='#2c3e50').pack(side='left', padx=(0, 5))
        self.daily_initial_balance_label = tk.Label(
            stats_frame,
            text="-- USDT",
            font=('Arial', 10, 'bold'),
            bg='#e3f2fd',
            fg='#1976d2',
            relief='raised',
            bd=1,
            padx=8,
            pady=2
        )
        self.daily_initial_balance_label.pack(side='left', padx=2)
        
        # 今日结束余额
        tk.Label(stats_frame, text="今日结束余额:", font=('Arial', 10, 'bold'), bg='#f0f0f0', fg='#2c3e50').pack(side='left', padx=(10, 5))
        self.daily_end_balance_label = tk.Label(
            stats_frame,
            text="-- USDT",
            font=('Arial', 10, 'bold'),
            bg='#e3f2fd',
            fg='#1976d2',
            relief='raised',
            bd=1,
            padx=8,
            pady=2
        )
        self.daily_end_balance_label.pack(side='left', padx=2)
        
        # 今日交易总额
        tk.Label(stats_frame, text="今日总额:", font=('Arial', 10, 'bold'), bg='#f0f0f0', fg='#2c3e50').pack(side='left', padx=(10, 5))
        self.daily_total_label = tk.Label(
            stats_frame,
            text="0.00 USDT",
            font=('Arial', 10, 'bold'),
            bg='#e8f5e8',
            fg='#27ae60',
            relief='raised',
            bd=1,
            padx=8,
            pady=2
        )
        self.daily_total_label.pack(side='left', padx=2)
        
        # 今日损耗
        tk.Label(stats_frame, text="今日损耗:", font=('Arial', 10, 'bold'), bg='#f0f0f0', fg='#2c3e50').pack(side='left', padx=(10, 5))
        self.daily_loss_label = tk.Label(
            stats_frame,
            text="0.00 USDT",
            font=('Arial', 10, 'bold'),
            bg='#ffe8e8',
            fg='#e74c3c',
            relief='raised',
            bd=1,
            padx=8,
            pady=2
        )
        self.daily_loss_label.pack(side='left', padx=2)
        
        # 今日交易次数
        tk.Label(stats_frame, text="交易次数:", font=('Arial', 10, 'bold'), bg='#f0f0f0', fg='#2c3e50').pack(side='left', padx=(10, 5))
        self.daily_trade_count_label = tk.Label(
            stats_frame,
            text="0",
            font=('Arial', 10, 'bold'),
            bg='#fff3cd',
            fg='#856404',
            relief='raised',
            bd=1,
            padx=8,
            pady=2
        )
        self.daily_trade_count_label.pack(side='left', padx=2)
        
        # 代币列表区域
        list_frame = tk.Frame(self.root, bg='#f0f0f0')
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 创建自定义表格
        self.create_custom_table(list_frame)
        
        # 右键菜单
        self.create_context_menu()
        
        # 控制按钮区域
        control_frame = tk.Frame(self.root, bg='#f0f0f0')
        control_frame.pack(fill='x', padx=10, pady=10)
        
        # 设置认证信息按钮
        token_btn = tk.Button(
            control_frame,
            text="设置认证信息",
            command=self.show_token_dialog,
            bg='#8e44ad',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20
        )
        token_btn.pack(side='left', padx=5)
        
        # 清空列表按钮
        clear_btn = tk.Button(
            control_frame,
            text="清空列表",
            command=self.clear_tokens,
            bg='#f39c12',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20
        )
        clear_btn.pack(side='left', padx=5)
        
        # 稳定度看板按钮
        stability_btn = tk.Button(
            control_frame,
            text="稳定度看板",
            command=self.show_stability_dashboard,
            bg='#9b59b6',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20
        )
        stability_btn.pack(side='left', padx=5)
        
        # 取消所有订单按钮
        cancel_orders_btn = tk.Button(
            control_frame,
            text="取消所有订单",
            command=self.cancel_all_orders,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20
        )
        cancel_orders_btn.pack(side='left', padx=5)
        
        # 认证信息过期显示（单独一行）
        auth_info_frame = tk.Frame(self.root, bg='#f0f0f0')
        auth_info_frame.pack(fill='x', padx=10, pady=(0, 5))
        
        self.auth_expiry_label = tk.Label(
            auth_info_frame,
            text="正在检查认证信息...",
            bg='#f0f0f0',
            fg='#666666',
            font=('Arial', 10)
        )
        self.auth_expiry_label.pack(anchor='w')
        
        # 4倍自动交易控制行
        trading_4x_control_frame = tk.Frame(self.root, bg='#f0f0f0')
        trading_4x_control_frame.pack(fill='x', padx=10, pady=5)
        
        # 4倍自动交易相关控件
        trading_4x_frame = tk.Frame(trading_4x_control_frame, bg='#f0f0f0')
        trading_4x_frame.pack(side='left')
        
        # 交易次数输入框
        tk.Label(
            trading_4x_frame,
            text="交易次数:",
            font=('Arial', 10),
            bg='#f0f0f0'
        ).pack(side='left', padx=(0, 5))
        
        self.trading_count_var = tk.StringVar(value="16")
        trading_count_entry = tk.Entry(
            trading_4x_frame,
            textvariable=self.trading_count_var,
            width=8,
            font=('Arial', 10)
        )
        trading_count_entry.pack(side='left', padx=(0, 10))
        
        # 4倍自动交易按钮
        self.trading_4x_btn = tk.Button(
            trading_4x_frame,
            text="4倍自动交易",
            command=self.start_4x_trading,
            bg='#27ae60',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=15
        )
        self.trading_4x_btn.pack(side='left', padx=5)
        
        # 系统日志区域
        log_frame = tk.Frame(self.root, bg='#f0f0f0')
        log_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(log_frame, text="系统日志:", font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w')
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=6, 
            font=('Consolas', 9),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        self.log_text.pack(fill='x', pady=5)
        
        # 将日志控件设置到logger中
        self.logger.set_log_widget(self.log_text)
        
        # 状态栏
        status_frame = tk.Frame(self.root, bg='#2c3e50', height=30)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="就绪",
            font=('Arial', 10),
            fg='#ecf0f1',
            bg='#2c3e50',
            anchor='w',
            padx=10
        )
        self.status_label.pack(fill='both', expand=True)
    
    def create_custom_table(self, parent):
        """创建自定义表格"""
        # 创建表头
        header_frame = tk.Frame(parent, bg='#e0e0e0', height=30)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # 表头标签
        headers = ['代币', '最新价格 (USDT)', '更新时间', '交易次数', '成交额 (USDT)', '自动交易']
        widths = [120, 200, 120, 100, 120, 100]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = tk.Label(header_frame, text=header, bg='#e0e0e0', font=('Arial', 10, 'bold'))
            label.place(x=sum(widths[:i]), y=0, width=width, height=30)
        
        # 创建表格内容区域
        self.table_content_frame = tk.Frame(parent, bg='white')
        self.table_content_frame.pack(fill='both', expand=True)
        
        # 添加滚动条
        self.scrollbar = ttk.Scrollbar(self.table_content_frame, orient='vertical')
        self.scrollbar.pack(side='right', fill='y')
        
        # 创建画布用于滚动
        self.canvas = tk.Canvas(self.table_content_frame, yscrollcommand=self.scrollbar.set, bg='white')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.config(command=self.canvas.yview)
        
        # 创建表格内容框架
        self.table_items_frame = tk.Frame(self.canvas, bg='white')
        self.canvas.create_window((0, 0), window=self.table_items_frame, anchor='nw')
        
        # 绑定滚动事件
        self.table_items_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # 存储表格行
        self.table_rows = []
        
        # 兼容性：创建虚拟的tree对象
        class VirtualTree:
            def __init__(self, table):
                self.table = table
                self.selection = []
            
            def get_children(self):
                return [f"row_{i}" for i in range(len(self.table.table_rows))]
            
            def delete(self, item):
                if item.startswith("row_"):
                    index = int(item.split("_")[1])
                    if 0 <= index < len(self.table.table_rows):
                        self.table.table_rows[index].destroy()
                        del self.table.table_rows[index]
            
            def selection_remove(self, item):
                if item in self.selection:
                    self.selection.remove(item)
            
            def bind(self, event, handler):
                """绑定事件 - 虚拟方法，不做任何操作"""
                pass
            
            def update_idletasks(self):
                """更新空闲任务 - 虚拟方法，不做任何操作"""
                pass
        
        self.tree = VirtualTree(self)
    
    def on_frame_configure(self, event):
        """表格框架大小变化时更新滚动区域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """画布大小变化时调整内容框架宽度"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas.find_all()[0], width=canvas_width)
    
    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="删除代币", command=self.delete_selected_token)
        self.context_menu.add_command(label="刷新价格", command=self.refresh_selected_token)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def on_click(self, event):
        """处理单击事件 - 自定义表格不需要此方法"""
        pass
    
    def center_window(self, window, width, height):
        """将窗口居中显示"""
        # 获取屏幕尺寸
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # 计算窗口位置
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # 设置窗口位置
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    @staticmethod
    def parse_request_headers(headers_text):
        """
        解析浏览器复制的 Request Headers 或 cURL 命令
        
        Args:
            headers_text: 完整的 Request Headers 文本或 cURL 命令
            
        Returns:
            dict: 解析后的headers字典，包含 cookie, csrftoken 等字段
        """
        headers_dict = {}
        
        # 检查是否是 cURL 格式
        if headers_text.strip().startswith('curl'):
            return BinanceTrader.parse_curl_command(headers_text)
        else:
            return BinanceTrader.parse_headers_format(headers_text)
    
    @staticmethod
    def parse_curl_command(curl_text):
        """
        解析 cURL 命令格式
        
        Args:
            curl_text: cURL 命令文本
            
        Returns:
            dict: 解析后的headers字典
        """
        headers_dict = {}
        lines = curl_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 跳过空行和 curl 命令本身
            if not line or line.startswith('curl'):
                continue
            
            # 解析 -H 'header: value' 格式
            if line.startswith("-H '") and line.endswith("' \\"):
                # 移除开头的 -H ' 和结尾的 ' \
                header_line = line[4:-3]
                if ':' in header_line:
                    parts = header_line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip().lower()
                        value = parts[1].strip()
                        headers_dict[key] = value
            
            # 解析 -b 'cookie' 格式
            elif line.startswith("-b '") and line.endswith("' \\"):
                # 移除开头的 -b ' 和结尾的 ' \
                cookie_value = line[4:-3]
                headers_dict['cookie'] = cookie_value
            
            # 处理最后一行（没有 \ 结尾）
            elif line.startswith("-H '") and line.endswith("'"):
                header_line = line[4:-1]
                if ':' in header_line:
                    parts = header_line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip().lower()
                        value = parts[1].strip()
                        headers_dict[key] = value
            
            elif line.startswith("-b '") and line.endswith("'"):
                cookie_value = line[4:-1]
                headers_dict['cookie'] = cookie_value
        
        return headers_dict
    
    @staticmethod
    def parse_headers_format(headers_text):
        """
        解析传统的 Request Headers 格式（冒号分隔或两行格式）
        
        Args:
            headers_text: Request Headers 文本
            
        Returns:
            dict: 解析后的headers字典
        """
        headers_dict = {}
        lines = headers_text.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 跳过空行和以:开头的伪头部
            if not line or line.startswith(':'):
                i += 1
                continue
            
            # 处理两种格式：
            # 1. 冒号分隔格式: "header-name: value"
            # 2. 两行格式: "header-name" + "\n" + "value"
            
            if ':' in line:
                # 冒号分隔格式
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower()
                    value = parts[1].strip()
                    
                    # 处理多行值（cookie特别长可能换行）
                    while i + 1 < len(lines) and not ':' in lines[i + 1] and not lines[i + 1].startswith(':'):
                        i += 1
                        value += lines[i].strip()
                    
                    headers_dict[key] = value
            else:
                # 两行格式：当前行是header名称，下一行是值
                key = line.lower()
                if i + 1 < len(lines):
                    i += 1
                    value = lines[i].strip()
                    headers_dict[key] = value
            
            i += 1
        
        return headers_dict
    
    def show_token_dialog(self):
        """显示认证信息设置对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("设置认证信息")
        dialog.geometry("700x650")
        dialog.configure(bg='#2c3e50')
        dialog.resizable(False, False)
        
        # 使对话框居中
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示对话框
        self.center_window(dialog, 700, 650)
        
        # 标题
        title_frame = tk.Frame(dialog, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', padx=20, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🔑 设置认证信息",
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(expand=True)
        
        # 说明文本
        info_frame = tk.Frame(dialog, bg='#2c3e50')
        info_frame.pack(fill='x', padx=20, pady=10)
        
        info_text = tk.Text(
            info_frame,
            height=7,
            font=('Arial', 10),
            bg='#34495e',
            fg='#ecf0f1',
            wrap='word',
            state='disabled'
        )
        info_text.pack(fill='x')
        
        info_content = """获取认证信息的方法：
                        1. 在浏览器中登录币安
                        2. 按F12打开开发者工具
                        3. 切换到Network标签页
                        4. 在币安页面进行任何操作
                        5. 找到任意API请求（如：/bapi/...），右键点击
                        6. 选择"Copy" -> "Copy as cURL (bash)"（推荐）
                        或选择"Copy Request Headers"
                        7. 将复制的内容粘贴到下方文本框中
                        8. 点击"保存"按钮

                        支持的格式：
                        • cURL命令格式（推荐）
                        • Request Headers格式（冒号分隔）
                        • 两行格式（header名称 + header值）"""
        
        info_text.config(state='normal')
        info_text.insert('1.0', info_content)
        info_text.config(state='disabled')
        
        # Request Headers输入框区域
        input_frame = tk.Frame(dialog, bg='#2c3e50')
        input_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        tk.Label(
            input_frame,
            text="Request Headers（直接粘贴完整内容）:",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#2c3e50'
        ).pack(anchor='w', pady=(0, 5))
        
        # 创建带滚动条的文本框
        text_frame = tk.Frame(input_frame, bg='#2c3e50')
        text_frame.pack(fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        
        headers_text = tk.Text(
            text_frame,
            height=20,
            font=('Consolas', 9),
            wrap='none',
            yscrollcommand=scrollbar.set
        )
        headers_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=headers_text.yview)
        
        # 提示文本
        placeholder = "请粘贴完整的 Request Headers...\n例如：\naccept: */*\ncookie: bnc-uuid=xxx...\ncsrftoken: xxx..."
        headers_text.insert('1.0', placeholder)
        headers_text.config(fg='gray')
        
        def on_focus_in(event):
            if headers_text.get('1.0', 'end-1c') == placeholder:
                headers_text.delete('1.0', 'end')
                headers_text.config(fg='black')
        
        def on_focus_out(event):
            if not headers_text.get('1.0', 'end-1c').strip():
                headers_text.insert('1.0', placeholder)
                headers_text.config(fg='gray')
        
        headers_text.bind('<FocusIn>', on_focus_in)
        headers_text.bind('<FocusOut>', on_focus_out)
        
        # 按钮区域
        button_frame = tk.Frame(dialog, bg='#2c3e50')
        button_frame.pack(fill='x', padx=20, pady=(10, 20))
        
        def save_headers():
            headers_content = headers_text.get('1.0', 'end-1c').strip()
            
            if not headers_content or headers_content == placeholder:
                messagebox.showwarning("警告", "请粘贴 Request Headers")
                return
            
            # 解析 headers
            parsed_headers = self.parse_request_headers(headers_content)
            
            # 提取必需的字段
            cookie = parsed_headers.get('cookie', '')
            csrf_token = parsed_headers.get('csrftoken', '')
            
            if not cookie:
                messagebox.showerror("错误", "未找到 cookie 字段，请检查粘贴的内容")
                return
            
            if not csrf_token:
                messagebox.showerror("错误", "未找到 csrftoken 字段，请检查粘贴的内容")
                return
            
            # 提取额外的有用字段
            extra_headers = {
                'device-info': parsed_headers.get('device-info', ''),
                'fvideo-id': parsed_headers.get('fvideo-id', ''),
                'fvideo-token': parsed_headers.get('fvideo-token', ''),
                'bnc-uuid': parsed_headers.get('bnc-uuid', ''),
                'user-agent': parsed_headers.get('user-agent', ''),
            }
            
            # 使用config_manager设置认证信息
            self.config_manager.set_credentials(csrf_token, cookie, extra_headers)
            
            # 更新本地认证信息
            self.csrf_token = csrf_token
            self.cookie = cookie
            self.config_manager.extra_headers = extra_headers
            
            # 重新创建API实例（使用新的认证信息）
            self.api = BinanceAPI(
                base_url=self.base_url,
                csrf_token=self.csrf_token,
                cookie=self.cookie,
                logger=self.logger,
                extra_headers=extra_headers
            )
            
            # 更新依赖组件的API引用
            if hasattr(self, 'trading_engine'):
                self.trading_engine.api = self.api
            if hasattr(self, 'order_handler'):
                self.order_handler.api = self.api
            
            self.log_message("认证信息设置成功并已保存")
            self.log_message(f"已提取: cookie, csrftoken, device-info, fvideo-id, bnc-uuid 等字段")
            
            # 更新认证信息过期显示
            self.update_auth_expiry_display()
            
            dialog.destroy()
        
        # 取消按钮
        cancel_btn = tk.Button(
            button_frame,
            text="取消",
            command=dialog.destroy,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15
        )
        cancel_btn.pack(side='right', padx=(10, 0))
        
        # 确认按钮
        confirm_btn = tk.Button(
            button_frame,
            text="设置",
            command=save_headers,
            bg='#27ae60',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20
        )
        confirm_btn.pack(side='right')
        
        # 聚焦到文本框
        headers_text.focus()
    
    def log_message(self, message):
        """添加日志消息 - 调用logger模块记录日志"""
        self.logger.log_message(message)
    
    def update_status(self, message, color='green'):
        """更新状态标签"""
        self.status_label.config(text=message, fg=color)
        self.root.update_idletasks()
    
    def get_token_price(self, symbol, max_retries=5):
        """
        获取代币价格 - 调用API模块，带重试机制
        
        Args:
            symbol: 代币符号，如 "ALPHA_1USDT"
            max_retries: 最大重试次数，默认5次
            
        Returns:
            dict: 包含价格和交易信息的字典，失败返回None
        """
        import time
        import random
        
        for attempt in range(max_retries):
            result = self.api.get_token_price(symbol)
            if result:
                return result
            
            # 如果获取失败且还有重试机会
            if attempt < max_retries - 1:
                self.log_message(f"获取 {symbol} 价格失败，第{attempt + 1}次重试")
                time.sleep(random.uniform(0.5, 1.5))
        
        # 所有重试都失败
        self.log_message(f"获取 {symbol} 价格失败，已重试{max_retries}次")
        return None
    
    def get_token_24h_stats(self, symbol):
        """获取代币24小时统计 - 调用API模块"""
        return self.api.get_token_24h_stats(symbol)
    
    def add_token(self):
        """添加代币"""
        if not self.csrf_token or not self.cookie:
            messagebox.showwarning("警告", "请先设置认证信息")
            return
        
        symbol = self.token_entry.get().strip().upper()
        
        if not symbol:
            messagebox.showwarning("警告", "请输入代币名称")
            return
        
        # 查找对应的ALPHA ID
        alpha_id = self.alpha_id_map.get(symbol)
        if not alpha_id:
            # 如果找不到代币，尝试更新Alpha ID映射
            print(f"未找到代币 {symbol} 的ALPHA ID，尝试更新代币列表...")
            self.logger.log_message(f"未找到代币 {symbol} 的ALPHA ID，尝试更新代币列表...")
            
            try:
                # 强制更新Alpha ID映射
                token_data = self.api.get_binance_token_list()
                updated_alpha_id_map = self.api.create_alpha_id_map(token_data)
                
                # 更新内存中的映射
                self.alpha_id_map = updated_alpha_id_map
                
                # 保存到文件
                with open('alphaIdMap.json', 'w', encoding='utf-8') as f:
                    json.dump(updated_alpha_id_map, f, indent=2, ensure_ascii=False)
                
                update_msg = f"✅ 已更新Alpha ID映射，包含 {len(updated_alpha_id_map)} 个代币"
                print(update_msg)
                self.logger.log_message(update_msg)
                
                # 再次查找代币
                alpha_id = self.alpha_id_map.get(symbol)
                if not alpha_id:
                    messagebox.showerror("错误", f"更新后仍未找到代币 {symbol} 的ALPHA ID，请检查代币名称是否正确")
                    return
                else:
                    print(f"更新后找到代币 {symbol} 的ALPHA ID: {alpha_id}")
                    self.logger.log_message(f"更新后找到代币 {symbol} 的ALPHA ID: {alpha_id}")
                    
            except Exception as e:
                error_msg = f"更新Alpha ID映射失败: {e}"
                print(error_msg)
                self.logger.log_message(error_msg)
                messagebox.showerror("错误", f"未找到代币 {symbol} 的ALPHA ID，且更新失败: {e}")
                return
        
        alpha_symbol = f"{alpha_id}USDT"
        
        if alpha_symbol in self.tokens:
            messagebox.showwarning("警告", f"代币 {symbol} ({alpha_symbol}) 已存在")
            return
        
        self.update_status("正在获取代币信息...", 'orange')
        self.log_message(f"正在添加代币: {symbol} -> {alpha_symbol}")
        
        # 在新线程中获取价格
        def fetch_data():
            price_data = self.get_token_price(alpha_symbol)
            if price_data:
                stats_data = self.get_token_24h_stats(alpha_symbol)
                
                # 在主线程中更新UI
                self.root.after(0, lambda: self.update_token_data(alpha_symbol, price_data, stats_data, symbol))
            else:
                self.root.after(0, lambda: self.handle_add_token_error(symbol))
        
        threading.Thread(target=fetch_data, daemon=True).start()
    
    def update_token_data(self, symbol, price_data, stats_data, display_name=None):
        """更新代币数据"""
        try:
            price = float(price_data['price'])
            
            # 如果是新代币，初始化交易相关数据
            if symbol not in self.tokens:
                self.tokens[symbol] = {
                    'trade_count': 1,  # 默认交易次数
                    'trade_amount': 0.0,  # 默认成交额
                    'auto_trading': False,  # 默认不自动交易
                    'last_buy_quantity': 0.0,  # 存储上一个买单的份额
                    'last_buy_amount': 0.0,  # 存储上一个买单的成交额
                    'last_sell_amount': 0.0  # 存储上一个卖单的成交额
                }
            
            self.tokens[symbol]['price'] = price
            self.tokens[symbol]['last_update'] = datetime.now()
            self.tokens[symbol]['display_name'] = display_name or symbol
            
            self.update_tree_view()
            display = display_name or symbol
            self.update_status(f"成功添加代币: {display}", 'green')
            self.log_message(f"代币 {display} ({symbol}) 更新成功，价格: ${price:.8f}")
            
        except (ValueError, KeyError) as e:
            self.log_message(f"解析 {symbol} 数据失败: {str(e)}")
            self.update_status("数据解析失败", 'red')
    
    def handle_add_token_error(self, symbol):
        """处理添加代币错误"""
        self.update_status("添加代币失败", 'red')
        messagebox.showerror("错误", f"无法获取代币 {symbol} 的信息，请检查代币名称是否正确")
    
    def update_tree_view(self):
        """更新表格显示"""
        # 清空现有数据
        for row in self.table_rows:
            row.destroy()
        self.table_rows.clear()
        
        # 添加代币数据
        for symbol, data in self.tokens.items():
            price = data['price']
            last_update = data['last_update'].strftime("%H:%M:%S")
            display_name = data.get('display_name', symbol)
            
            # 在价格文本后添加可点击的刷新标识
            price_text = f"${price:.8f} 🔄"
            
            # 获取交易相关数据
            trade_count = data.get('trade_count', 1)
            trade_amount = data.get('trade_amount', 0.0)
            auto_trading = data.get('auto_trading', False)
            
            # 创建表格行
            row_frame = self.create_table_row(symbol, display_name, price_text, last_update, trade_count, trade_amount, auto_trading)
            self.table_rows.append(row_frame)
            
            # 存储行引用
            if 'row_ref' not in self.tokens[symbol]:
                self.tokens[symbol]['row_ref'] = {}
            self.tokens[symbol]['row_ref'] = row_frame
    
    def create_table_row(self, symbol, display_name, price_text, last_update, trade_count, trade_amount, auto_trading):
        """创建表格行"""
        # 创建行框架
        row_frame = tk.Frame(self.table_items_frame, bg='white', height=30)
        row_frame.pack(fill='x')
        row_frame.pack_propagate(False)
        
        # 列宽度
        widths = [120, 200, 120, 100, 120, 100]
        
        # 代币名称
        token_label = tk.Label(row_frame, text=display_name, bg='white', font=('Arial', 9))
        token_label.place(x=0, y=0, width=widths[0], height=30)
        
        # 价格（可点击）
        price_label = tk.Label(row_frame, text=price_text, bg='white', font=('Arial', 9), cursor='hand2')
        price_label.place(x=widths[0], y=0, width=widths[1], height=30)
        price_label.bind('<Button-1>', lambda e: self.refresh_single_token(symbol))
        
        # 更新时间
        time_label = tk.Label(row_frame, text=last_update, bg='white', font=('Arial', 9))
        time_label.place(x=widths[0]+widths[1], y=0, width=widths[2], height=30)
        
        # 交易次数输入框
        count_entry = tk.Entry(row_frame, width=8, font=('Arial', 9), justify='center')
        count_entry.insert(0, str(trade_count))
        count_entry.place(x=widths[0]+widths[1]+widths[2], y=2, width=widths[3]-4, height=26)
        count_entry.bind('<Return>', lambda e: self.update_trade_count_from_entry(symbol, count_entry.get()))
        count_entry.bind('<FocusOut>', lambda e: self.update_trade_count_from_entry(symbol, count_entry.get()))
        
        # 成交额输入框
        amount_entry = tk.Entry(row_frame, width=10, font=('Arial', 9), justify='center')
        amount_entry.insert(0, f"{trade_amount:.2f}")
        amount_entry.place(x=widths[0]+widths[1]+widths[2]+widths[3], y=2, width=widths[4]-4, height=26)
        amount_entry.bind('<Return>', lambda e: self.update_trade_amount_from_entry(symbol, amount_entry.get()))
        amount_entry.bind('<FocusOut>', lambda e: self.update_trade_amount_from_entry(symbol, amount_entry.get()))
        
        # 自动交易按钮
        if auto_trading:
            button_text = "停止"
            button_color = '#e74c3c'
        else:
            button_text = "开始"
            button_color = '#27ae60'
        
        auto_button = tk.Button(
            row_frame, 
            text=button_text, 
            width=6, 
            font=('Arial', 9, 'bold'),
            bg=button_color,
            fg='white',
            relief='raised',
            bd=2
        )
        auto_button.place(x=widths[0]+widths[1]+widths[2]+widths[3]+widths[4], y=2, width=widths[5]-4, height=26)
        
        # 添加按钮按下效果
        auto_button.bind('<Button-1>', lambda e: self.on_button_press(auto_button))
        auto_button.bind('<ButtonRelease-1>', lambda e: self.on_button_release(auto_button, symbol))
        
        # 存储组件引用
        if 'widgets' not in self.tokens[symbol]:
            self.tokens[symbol]['widgets'] = {}
        self.tokens[symbol]['widgets'] = {
            'count_entry': count_entry,
            'amount_entry': amount_entry,
            'auto_button': auto_button
        }
        
        return row_frame
    
    
    
    def update_trade_count_from_entry(self, symbol, value):
        """从输入框更新交易次数"""
        try:
            count = int(value)
            if count > 0:
                self.tokens[symbol]['trade_count'] = count
                self.log_message(f"{symbol} 交易次数设置为: {count}")
                # 更新表格显示
                self.update_tree_view()
            else:
                messagebox.showerror("错误", "交易次数必须大于0")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    
    def update_trade_amount_from_entry(self, symbol, value):
        """从输入框更新成交额"""
        try:
            amount = float(value)
            if amount >= 0:
                self.tokens[symbol]['trade_amount'] = amount
                display_name = self.tokens[symbol].get('display_name', symbol)
                self.log_message(f"{display_name} 成交额设置为: {amount} USDT")
                # 更新表格显示
                self.update_tree_view()
            else:
                messagebox.showerror("错误", "成交额不能为负数")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    
    def show_trade_settings_dialog(self, symbol):
        """显示交易设置对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"交易设置 - {symbol}")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"400x300+{x}+{y}")
        
        # 获取当前数据
        data = self.tokens.get(symbol, {})
        current_count = data.get('trade_count', 1)
        current_amount = data.get('trade_amount', 0.0)
        current_trading = data.get('auto_trading', False)
        
        # 创建输入框
        tk.Label(dialog, text="交易次数:", font=('Arial', 12)).pack(pady=10)
        count_var = tk.StringVar(value=str(current_count))
        count_entry = tk.Entry(dialog, textvariable=count_var, font=('Arial', 12), width=20)
        count_entry.pack(pady=5)
        
        tk.Label(dialog, text="成交额 (USDT):", font=('Arial', 12)).pack(pady=10)
        amount_var = tk.StringVar(value=f"{current_amount:.2f}")
        amount_entry = tk.Entry(dialog, textvariable=amount_var, font=('Arial', 12), width=20)
        amount_entry.pack(pady=5)
        
        # 自动交易按钮
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        button_text = "停止自动交易" if current_trading else "开始自动交易"
        button_color = '#e74c3c' if current_trading else '#27ae60'
        
        auto_button = tk.Button(
            button_frame,
            text=button_text,
            font=('Arial', 12, 'bold'),
            bg=button_color,
            fg='white',
            width=15,
            height=2,
            command=lambda: self.toggle_auto_trading_from_dialog(symbol, dialog)
        )
        auto_button.pack()
        
        # 保存按钮
        save_button = tk.Button(
            dialog,
            text="保存设置",
            font=('Arial', 12),
            bg='#3498db',
            fg='white',
            width=15,
            command=lambda: self.save_trade_settings(symbol, count_var.get(), amount_var.get(), dialog)
        )
        save_button.pack(pady=10)
        
        # 关闭按钮
        close_button = tk.Button(
            dialog,
            text="关闭",
            font=('Arial', 12),
            bg='#95a5a6',
            fg='white',
            width=15,
            command=dialog.destroy
        )
        close_button.pack(pady=5)
    
    def toggle_auto_trading_from_dialog(self, symbol, dialog):
        """从对话框切换自动交易状态"""
        self.trading_engine.toggle_auto_trading(symbol)
        dialog.destroy()
    
    def save_trade_settings(self, symbol, count_str, amount_str, dialog):
        """保存交易设置"""
        try:
            # 验证并更新交易次数
            count = int(count_str)
            if count <= 0:
                raise ValueError("交易次数必须大于0")
            self.tokens[symbol]['trade_count'] = count
            self.log_message(f"{symbol} 交易次数设置为:{count}")
            
            # 验证并更新成交额
            amount = float(amount_str)
            if amount < 0:
                raise ValueError("成交额不能为负数")
            self.tokens[symbol]['trade_amount'] = amount
            display_name = self.tokens[symbol].get('display_name', symbol)
            self.log_message(f"{display_name} 成交额设置为:{amount:.2f} USDT")
            
            # 更新表格显示
            self.update_tree_view()
            dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
    
    def on_button_press(self, button):
        """按钮按下效果"""
        button.configure(relief='sunken')
    
    def on_button_release(self, button, symbol):
        """按钮松开效果"""
        button.configure(relief='raised')
        # 延迟执行实际功能，让用户看到按下效果
        self.root.after(100, lambda: self.trading_engine.toggle_auto_trading(symbol))
    
    
    def delete_selected_token(self):
        """删除选中的代币"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的代币")
            return
        
        item = self.tree.item(selection[0])
        display_name = item['values'][0]
        
        # 查找对应的symbol
        symbol_to_delete = None
        for symbol, data in self.tokens.items():
            if data.get('display_name', symbol) == display_name:
                symbol_to_delete = symbol
                break
        
        if symbol_to_delete is None:
            messagebox.showerror("错误", "未找到对应的代币")
            return
        
        if messagebox.askyesno("确认", f"确定要删除代币 {display_name} 吗？"):
            if symbol_to_delete in self.auto_trading:
                del self.auto_trading[symbol_to_delete]
            if symbol_to_delete in self.trading_threads:
                del self.trading_threads[symbol_to_delete]
            
            # 清理嵌入的组件
            if symbol_to_delete in self.tokens and 'widgets' in self.tokens[symbol_to_delete]:
                widgets = self.tokens[symbol_to_delete]['widgets']
                for widget in widgets.values():
                    if widget.winfo_exists():
                        widget.destroy()
            
            del self.tokens[symbol_to_delete]
            self.update_tree_view()
            self.log_message(f"已删除代币: {display_name}")
    
    def refresh_selected_token(self):
        """刷新选中代币的价格"""
        if not self.csrf_token or not self.cookie:
            messagebox.showwarning("警告", "请先设置认证信息")
            return
        
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要刷新的代币")
            return
        
        item = self.tree.item(selection[0])
        display_name = item['values'][0]
        
        # 查找对应的symbol
        symbol_to_refresh = None
        for symbol, data in self.tokens.items():
            if data.get('display_name', symbol) == display_name:
                symbol_to_refresh = symbol
                break
        
        if symbol_to_refresh is None:
            messagebox.showerror("错误", "未找到对应的代币")
            return
        
        self.log_message(f"正在刷新代币: {display_name}")
        
        def refresh_data():
            price_data = self.get_token_price(symbol_to_refresh)
            if price_data:
                stats_data = self.get_token_24h_stats(symbol_to_refresh)
                display_name = self.tokens[symbol_to_refresh].get('display_name', symbol_to_refresh)
                self.root.after(0, lambda: self.update_token_data(symbol_to_refresh, price_data, stats_data, display_name))
            else:
                self.root.after(0, lambda: self.log_message(f"刷新 {display_name} 失败"))
        
        threading.Thread(target=refresh_data, daemon=True).start()
    
    def clear_tokens(self):
        """清空所有代币（保留稳定度看板中的代币）"""
        if messagebox.askyesno("确认", "确定要清空所有代币吗？（稳定度看板中的代币将保留）"):
            # 获取稳定度看板中的代币列表和价格
            stability_tokens = {}
            try:
                stability_data = self.fetch_stability_data()
                if stability_data:
                    for item in stability_data:
                        project = item.get('project', '')
                        if project:
                            alpha_id = self.alpha_id_map.get(project)
                            if alpha_id:
                                alpha_symbol = f"{alpha_id}USDT"
                                stability_price = float(item.get('price', 0))
                                stability_tokens[alpha_symbol] = {
                                    'price': stability_price,
                                    'display_name': project,
                                    'change_24h': 0.0
                                }
            except Exception as e:
                self.log_message(f"获取稳定度看板代币列表失败: {str(e)}")
                # 如果失败，至少保留KOGE
                stability_tokens["ALPHA_22USDT"] = {
                    'price': 0.0,
                    'display_name': 'KOGE',
                    'change_24h': 0.0
                }
            
            # 保留稳定度看板中的代币，使用稳定度看板的价格
            permanent_tokens = {}
            for symbol, stability_data in stability_tokens.items():
                if symbol in self.tokens:
                    token_data = self.tokens[symbol]
                    permanent_tokens[symbol] = {
                        'price': stability_data.get('price', token_data.get('price', 0.0)),
                        'last_update': token_data.get('last_update', datetime.now()),
                        'display_name': stability_data.get('display_name', token_data.get('display_name', '')),
                        'trade_count': 1,
                        'trade_amount': 0.0,
                        'auto_trading': False,
                        'change_24h': stability_data.get('change_24h', 0.0),
                        'last_buy_quantity': token_data.get('last_buy_quantity', 0.0),  # 保留上一个买单份额
                        'last_buy_amount': token_data.get('last_buy_amount', 0.0),  # 保留上一个买单成交额
                        'last_sell_amount': token_data.get('last_sell_amount', 0.0)  # 保留上一个卖单成交额
                    }
            
            # 清理所有相关组件
            for symbol, data in self.tokens.items():
                if 'widgets' in data:
                    widgets = data['widgets']
                    for widget in widgets.values():
                        if widget.winfo_exists():
                            widget.destroy()
            
            self.auto_trading.clear()
            self.trading_threads.clear()
            
            self.tokens.clear()
            self.tokens.update(permanent_tokens)
            
            self.update_tree_view()
            self.log_message(f"已清空所有代币（保留了 {len(permanent_tokens)} 个稳定度看板代币）")
    
    def cancel_all_orders(self):
        """取消所有订单并清理持仓"""
        if not self.csrf_token or not self.cookie:
            messagebox.showwarning("警告", "请先设置认证信息")
            return
        
        # 确认对话框
        result = messagebox.askyesno(
            "确认操作", 
            "此操作将:\n1. 取消所有未成交订单\n2. 卖出所有持有的代币\n\n确定要继续吗？",
            icon='warning'
        )
        
        if not result:
            return
        
        self.log_message("开始执行取消所有订单并清理持仓...")
        
        # 在新线程中执行，避免阻塞UI
        def cleanup_all():
            try:
                # 1. 取消所有未成交订单
                self.log_message("正在取消所有未成交订单...")
                cancel_success = self.api.cancel_all_orders()
                if cancel_success:
                    self.log_message("✅ 已取消所有未成交订单")
                else:
                    self.log_message("❌ 取消订单失败，继续执行清理...")
                
                # 等待一下，确保订单取消生效
                time.sleep(2)
                
                # 2. 清理所有持仓
                tokens_with_holdings = []
                for symbol, token_data in self.tokens.items():
                    last_buy_quantity = token_data.get('last_buy_quantity', 0)
                    if last_buy_quantity > 0:
                        tokens_with_holdings.append((symbol, token_data, last_buy_quantity))
                
                if tokens_with_holdings:
                    self.log_message(f"发现 {len(tokens_with_holdings)} 个代币有持仓，开始清仓...")
                    
                    for symbol, token_data, quantity in tokens_with_holdings:
                        display_name = token_data.get('display_name', symbol)
                        self.log_message(f"{display_name} 检测到持有份额: {quantity}，正在清仓卖出...")
                        
                        # 使用交易引擎的清仓卖单逻辑（全局清理模式）
                        self.trading_engine.execute_cleanup_sell_order(symbol, display_name, quantity, is_global_cleanup=True)
                        
                        # 每个代币之间稍微等待一下
                        time.sleep(1)
                else:
                    self.log_message("✅ 无持仓代币，无需清仓")
                
                # 3. 停止所有自动交易
                active_trading = []
                for symbol in list(self.auto_trading.keys()):
                    if self.auto_trading.get(symbol, False):
                        active_trading.append(symbol)
                
                if active_trading:
                    self.log_message(f"停止 {len(active_trading)} 个代币的自动交易...")
                    for symbol in active_trading:
                        self.auto_trading[symbol] = False
                        if symbol in self.tokens:
                            self.tokens[symbol]['auto_trading'] = False
                    
                    # 更新UI
                    self.root.after(0, self.update_tree_view)
                
                self.log_message("✅ 取消所有订单并清理持仓完成")
                
            except Exception as e:
                self.log_message(f"❌ 清理过程中出现异常: {str(e)}")
        
        # 启动清理线程
        threading.Thread(target=cleanup_all, daemon=True).start()
    
    def refresh_single_token(self, symbol):
        """刷新单个代币价格"""
        if not self.csrf_token or not self.cookie:
            messagebox.showwarning("警告", "请先设置认证信息")
            return
        
        if symbol not in self.tokens:
            self.log_message(f"代币 {symbol} 不存在")
            return
        
        display_name = self.tokens[symbol].get('display_name', symbol)
        self.log_message(f"正在刷新代币: {display_name}")
        self.update_status(f"正在刷新 {display_name}...", 'orange')
        
        def refresh_data():
            price_data = self.get_token_price(symbol)
            if price_data:
                stats_data = self.get_token_24h_stats(symbol)
                self.root.after(0, lambda: self.update_token_data(symbol, price_data, stats_data, display_name))
            else:
                self.root.after(0, lambda: self.log_message(f"刷新 {display_name} 失败"))
                self.root.after(0, lambda: self.update_status("刷新失败", 'red'))
        
        threading.Thread(target=refresh_data, daemon=True).start()
    
    def start_4x_trading(self):
        """开始4倍自动交易"""
        if self.trading_4x_active:
            # 停止4倍自动交易
            self.trading_4x_active = False
            self.trading_4x_btn.config(text="4倍自动交易", bg='#27ae60')
            self.log_message("4倍自动交易已停止")
        else:
            # 开始4倍自动交易
            try:
                trading_count = int(self.trading_count_var.get())
                if trading_count <= 0:
                    self.log_message("交易次数必须大于0")
                    return
                
                self.trading_4x_active = True
                self.trading_4x_btn.config(text="停止4倍交易", bg='#e74c3c')
                self.log_message(f"开始4倍自动交易，计划交易 {trading_count} 次")
                
                # 启动4倍自动交易线程
                self.trading_4x_thread = threading.Thread(target=self.trading_engine.run_4x_trading, args=(trading_count,), daemon=True)
                self.trading_4x_thread.start()
                
            except ValueError:
                self.log_message("请输入有效的交易次数")
    
    def on_scheduled_trading_toggle(self):
        """定时交易复选框状态改变时的处理"""
        if self.scheduled_trading_var.get():
            # 启用定时交易
            self.scheduled_trading_enabled = True
            self.log_message("定时交易已启用")
            self.start_scheduled_trading_checker()
        else:
            # 禁用定时交易
            self.scheduled_trading_enabled = False
            self.log_message("定时交易已禁用")
            if self.scheduled_trading_thread and self.scheduled_trading_thread.is_alive():
                # 注意：线程无法强制停止，只能设置标志位让它自然结束
                pass
    
    def start_scheduled_trading_checker(self):
        """启动定时交易检查线程"""
        if self.scheduled_trading_thread and self.scheduled_trading_thread.is_alive():
            return  # 如果已经在运行，不重复启动
        
        self.scheduled_trading_thread = threading.Thread(
            target=self.scheduled_trading_worker, 
            daemon=True
        )
        self.scheduled_trading_thread.start()
    
    def scheduled_trading_worker(self):
        """定时交易检查工作线程"""
        while self.scheduled_trading_enabled:
            try:
                current_time = datetime.now()
                current_date = current_time.date()
                current_hour = current_time.hour
                current_minute = current_time.minute
                
                # 获取设定的时间
                try:
                    scheduled_hour = int(self.scheduled_hour_var.get())
                    scheduled_minute = int(self.scheduled_minute_var.get())
                except ValueError:
                    self.log_message("定时交易时间格式错误，请检查输入")
                    time.sleep(60)  # 等待1分钟后重试
                    continue
                
                # 检查是否到达设定时间
                if (current_hour == scheduled_hour and 
                    current_minute == scheduled_minute and 
                    self.last_scheduled_date != current_date and
                    not self.trading_4x_active):
                    
                    # 执行定时交易
                    self.last_scheduled_date = current_date
                    self.log_message(f"到达定时交易时间 {scheduled_hour:02d}:{scheduled_minute:02d}，开始执行4倍自动交易")
                    
                    # 获取默认交易次数
                    try:
                        trading_count = int(self.trading_count_var.get())
                    except ValueError:
                        trading_count = 8  # 默认8次
                    
                    # 在GUI线程中执行交易
                    self.root.after(0, lambda: self.execute_scheduled_trading(trading_count))
                
                # 检查超时提醒（超过设定时间30分钟）
                self.check_timeout_alarm(current_hour, current_minute, scheduled_hour, scheduled_minute, current_date)
                
                # 每分钟检查一次
                time.sleep(60)
                
            except Exception as e:
                self.log_message(f"定时交易检查出错: {str(e)}")
                time.sleep(60)  # 出错后等待1分钟再重试
    
    def execute_scheduled_trading(self, trading_count):
        """执行定时交易"""
        try:
            if trading_count <= 0:
                self.log_message("交易次数必须大于0")
                return
            
            self.trading_4x_active = True
            self.trading_4x_btn.config(text="停止4倍交易", bg='#e74c3c')
            self.log_message(f"定时交易启动，计划交易 {trading_count} 次")
            
            # 启动4倍自动交易线程
            self.trading_4x_thread = threading.Thread(
                target=self.trading_engine.run_4x_trading, 
                args=(trading_count,), 
                daemon=True
            )
            self.trading_4x_thread.start()
                    
        except Exception as e:
            self.log_message(f"定时交易执行失败: {str(e)}")
    
    def check_timeout_alarm(self, current_hour, current_minute, scheduled_hour, scheduled_minute, current_date):
        """检查超时提醒"""
        try:
            # 计算当前时间与设定时间的差值（分钟）
            current_time_minutes = current_hour * 60 + current_minute
            scheduled_time_minutes = scheduled_hour * 60 + scheduled_minute
            
            # 如果当前时间超过设定时间30分钟，但不超过1小时
            if scheduled_time_minutes + 30 <= current_time_minutes < scheduled_time_minutes + 60:
                # 检查今日是否已播放过闹钟
                if not self.alarm_played_today:
                    # 获取设定的交易次数
                    try:
                        expected_count = int(self.trading_count_var.get())
                    except ValueError:
                        expected_count = 8
                    
                    # 如果实际交易次数不等于设定次数，且启用了闹钟，播放闹钟
                    enable_alarm = hasattr(self, 'enable_alarm_var') and self.enable_alarm_var.get()
                    if self.daily_completed_trades != expected_count and enable_alarm:
                        self.play_alarm()
                        self.alarm_played_today = True
                        self.log_message(f"⚠️ 超时警告：设定时间 {scheduled_hour:02d}:{scheduled_minute:02d} 已过30分钟，今日交易次数 {self.daily_completed_trades} 不等于设定次数 {expected_count}，播放闹钟提醒！")
                    elif self.daily_completed_trades != expected_count and not enable_alarm:
                        self.log_message(f"⚠️ 超时警告：设定时间 {scheduled_hour:02d}:{scheduled_minute:02d} 已过30分钟，今日交易次数 {self.daily_completed_trades} 不等于设定次数 {expected_count}，但闹钟未启用")
                    else:
                        self.log_message(f"今日交易次数已达到设定目标 {expected_count} 次，无需播放闹钟")
            elif current_time_minutes >= scheduled_time_minutes + 60:
                # 如果超过设定时间1小时，不再播放闹钟
                if not self.alarm_played_today:
                    try:
                        expected_count = int(self.trading_count_var.get())
                    except ValueError:
                        expected_count = 8
                    
                    if self.daily_completed_trades != expected_count:
                        self.log_message(f"⚠️ 超时警告：设定时间 {scheduled_hour:02d}:{scheduled_minute:02d} 已过1小时，今日交易次数 {self.daily_completed_trades} 不等于设定次数 {expected_count}，但已超过闹钟提醒时限")
                        self.alarm_played_today = True  # 标记为已处理，避免重复提醒
                        
        except Exception as e:
            self.log_message(f"超时检查出错: {str(e)}")
    
    def play_alarm(self):
        """播放闹钟音频"""
        try:
            import os
            import subprocess
            
            # 检查alarm.mp3文件是否存在
            if not os.path.exists("alarm.mp3"):
                self.log_message("警告：alarm.mp3文件不存在，无法播放闹钟")
                return
            
            # 获取文件绝对路径
            alarm_path = os.path.abspath("alarm.mp3")
            
            # 设置闹钟播放状态
            self.alarm_is_playing = True
            
            # 更新按钮颜色为红色（播放中）
            self.root.after(0, self.update_alarm_button_color)
            
            self.log_message("🔔 闹钟已播放，将循环播放15分钟")
            
            # 启动循环播放线程
            def alarm_worker():
                try:
                    # 计算需要播放的次数（15分钟 = 900秒，每次播放7秒+等待3秒=10秒）
                    total_cycles = 90  # 900 / 10 = 90次
                    
                    for i in range(total_cycles):
                        if not self.alarm_is_playing:
                            break
                        
                        # 使用Windows默认播放器打开MP3文件
                        # /min表示最小化窗口，避免弹出太多窗口
                        subprocess.Popen(
                            f'start /min "" "{alarm_path}"',
                            shell=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        
                        self.log_message(f"闹钟播放进度: 第{i+1}/{total_cycles}次播放")
                        
                        # 等待7秒让音频播放
                        time.sleep(7)
                        
                        # 等待3秒后继续下一次播放
                        time.sleep(3)
                    
                    # 播放结束，更新状态
                    self.alarm_is_playing = False
                    self.root.after(0, self.update_alarm_button_color)
                    self.log_message("🔔 闹钟播放已结束（15分钟）")
                    
                except Exception as e:
                    self.log_message(f"闹钟播放过程出错: {str(e)}")
                    self.alarm_is_playing = False
                    self.root.after(0, self.update_alarm_button_color)
            
            # 启动播放线程
            alarm_thread = threading.Thread(target=alarm_worker, daemon=True)
            alarm_thread.start()
            
        except Exception as e:
            self.log_message(f"播放闹钟失败: {str(e)}")
    
    def stop_alarm_manually(self):
        """手动停止闹钟"""
        try:
            # 设置闹钟播放状态为停止
            self.alarm_is_playing = False
            
            # 更新按钮颜色为绿色（停止状态）
            self.update_alarm_button_color()
            
            self.log_message("🔔 闹钟已手动停止")
        except Exception as e:
            self.log_message(f"停止闹钟失败: {str(e)}")
    
    def update_alarm_button_color(self):
        """更新闹钟按钮颜色"""
        try:
            if hasattr(self, 'stop_alarm_btn') and self.stop_alarm_btn:
                if self.alarm_is_playing:
                    # 播放中：红色
                    self.stop_alarm_btn.config(bg='#e74c3c')
                else:
                    # 停止状态：绿色
                    self.stop_alarm_btn.config(bg='#27ae60')
        except Exception as e:
            self.log_message(f"更新闹钟按钮颜色失败: {str(e)}")
    
    def reset_daily_alarm_flag(self):
        """重置每日闹钟标志（在每日重置时调用）"""
        self.alarm_played_today = False
        self.config_manager.daily_completed_trades = 0
        self.daily_completed_trades = 0
        self.log_message("每日闹钟标志已重置")
    
    
    def show_stability_dashboard(self):
        """显示稳定度看板窗口"""
        # 检查是否已经存在稳定度看板窗口
        if self.stability_window is not None and self.stability_window.winfo_exists():
            # 如果窗口已存在，则将其提到前台并恢复显示
            self.stability_window.lift()
            self.stability_window.focus_force()
            # 如果窗口被最小化，则恢复显示
            if self.stability_window.state() == 'iconic':
                self.stability_window.state('normal')
            return
        
        # 创建新窗口
        stability_window = tk.Toplevel(self.root)
        self.stability_window = stability_window  # 保存窗口引用
        stability_window.title("稳定度看板 - Stability Dashboard")
        stability_window.geometry("800x600")
        stability_window.configure(bg='#2c3e50')
        
        # 标题
        title_frame = tk.Frame(stability_window, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', padx=10, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="📊 稳定度看板 - Stability Dashboard",
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(expand=True)
        
        # 控制按钮
        control_frame = tk.Frame(stability_window, bg='#2c3e50')
        control_frame.pack(fill='x', padx=10, pady=5)
        
        refresh_btn = tk.Button(
            control_frame,
            text="🔄 刷新数据",
            command=lambda: self.refresh_stability_data(stability_window),
            bg='#3498db',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20
        )
        refresh_btn.pack(side='left', padx=5)
        
        # 状态标签
        status_label = tk.Label(
            control_frame,
            text="点击刷新获取最新数据",
            font=('Arial', 10),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        status_label.pack(side='right', padx=10)
        
        # 表格框架
        table_frame = tk.Frame(stability_window, bg='#2c3e50')
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 创建表格
        columns = ('项目', '稳定度', '最新价', '4倍剩余天数', '操作')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # 配置标签样式
        style = ttk.Style()
        
        # 稳定状态 - 绿色
        style.configure("stable.Treeview", foreground="#2ecc71")
        style.configure("stable.Treeview.Item", foreground="#2ecc71")
        
        # 一般状态 - 橙色
        style.configure("moderate.Treeview", foreground="#f39c12")
        style.configure("moderate.Treeview.Item", foreground="#f39c12")
        
        # 不稳定状态 - 红色
        style.configure("unstable.Treeview", foreground="#e74c3c")
        style.configure("unstable.Treeview.Item", foreground="#e74c3c")
        
        # 未知状态 - 灰色
        style.configure("unknown.Treeview", foreground="#95a5a6")
        style.configure("unknown.Treeview.Item", foreground="#95a5a6")
        
        # 设置列标题和宽度
        tree.heading('项目', text='项目')
        tree.heading('稳定度', text='稳定度')
        tree.heading('最新价', text='最新价')
        tree.heading('4倍剩余天数', text='4倍剩余天数')
        tree.heading('操作', text='操作')
        
        tree.column('项目', width=120, anchor='center')
        tree.column('稳定度', width=100, anchor='center')
        tree.column('最新价', width=120, anchor='center')
        tree.column('4倍剩余天数', width=120, anchor='center')
        tree.column('操作', width=100, anchor='center')
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 存储引用
        stability_window.tree = tree
        stability_window.status_label = status_label
        
        # 添加窗口关闭事件处理
        def on_window_close():
            stability_window.destroy()  # 销毁窗口
            self.stability_window = None  # 清空窗口引用
        
        stability_window.protocol("WM_DELETE_WINDOW", on_window_close)
        
        # 初始加载数据
        self.refresh_stability_data(stability_window)
    
    def refresh_stability_data(self, window):
        """刷新稳定度数据"""
        def fetch_data():
            window.status_label.config(text="正在获取数据...", fg='orange')
            
            data = self.alpha123_client.fetch_stability_data()
            
            # 在主线程中更新UI
            window.after(0, lambda: self.update_stability_table(window, data))
        
        threading.Thread(target=fetch_data, daemon=True).start()
    
    def update_stability_table(self, window, data):
        """更新稳定度表格"""
        # 清空现有数据
        for item in window.tree.get_children():
            window.tree.delete(item)
        
        if not data:
            window.status_label.config(text="获取数据失败", fg='red')
            return
        
        # 添加数据
        for item in data:
            project = item['project']
            stability = item['stability']
            price = item['price']
            remaining_days = item['remaining_days']
            
            # 根据稳定度设置颜色标签和样式
            stability_display = stability
            tag_name = "unknown"  # 默认标签
            
            if stability == "稳定":
                stability_display = "🟢 稳定"  # 绿色圆点
                tag_name = "stable"
            elif stability == "一般":
                stability_display = "🟡 一般"  # 橙色圆点
                tag_name = "moderate"
            elif stability == "不稳定":
                stability_display = "🔴 不稳定"  # 红色圆点
                tag_name = "unstable"
            
            # 插入数据并应用标签样式
            item_id = window.tree.insert('', 'end', values=(
                project,
                stability_display,
                price,
                remaining_days,
                "添加"
            ), tags=(tag_name,))
        
        window.status_label.config(text=f"已加载 {len(data)} 个项目", fg='green')
        
        # 绑定添加按钮事件
        window.tree.bind('<Button-1>', lambda e: self.on_stability_item_click(e, window))
    
    def on_stability_item_click(self, event, window):
        """处理稳定度表格点击事件"""
        item = window.tree.identify_row(event.y)
        column = window.tree.identify_column(event.x)
        
        if item and column == '#5':  # 点击的是操作列
            values = window.tree.item(item, 'values')
            project = values[0]
            
            # 尝试添加代币到监控列表
            self.add_token_from_stability(project)
    
    def add_token_from_stability(self, project):
        """从稳定度看板添加代币到监控列表"""
        # 查找对应的ALPHA ID
        alpha_id = self.alpha_id_map.get(project)
        if not alpha_id:
            messagebox.showerror("错误", f"未找到代币 {project} 的ALPHA ID")
            return
        
        alpha_symbol = f"{alpha_id}USDT"
        
        # 检查代币是否已在监控列表中
        if alpha_symbol in self.tokens:
            messagebox.showinfo("提示", f"代币 {project} ({alpha_symbol}) 已在监控列表中")
            return
        
        try:
            # 检查代币是否存在
            price_data = self.get_token_price(alpha_symbol)
            if price_data:
                # 代币存在，添加到监控列表
                stats_data = self.get_token_24h_stats(alpha_symbol)
                self.update_token_data(alpha_symbol, price_data, stats_data, project)
                self.log_message(f"从稳定度看板添加代币: {project} -> {alpha_symbol}")
                messagebox.showinfo("成功", f"代币 {project} 已添加到监控列表")
            else:
                messagebox.showwarning("警告", f"无法获取代币 {project} 的价格数据")
        except Exception as e:
            self.log_message(f"添加代币 {project} 失败: {str(e)}")
            messagebox.showerror("错误", f"添加代币 {project} 失败: {str(e)}")

    def load_config(self):
        """加载配置文件 - 配置已在__init__中加载"""
        # 配置在初始化时已通过config_manager.load_config()加载
        # 此方法保留用于接口兼容性
        pass
    
    def save_config(self):
        """保存配置文件 - 调用配置管理器"""
        # 同步本地数据到配置管理器
        self.config_manager.csrf_token = self.csrf_token
        self.config_manager.cookie = self.cookie
        self.config_manager.daily_total_amount = self.daily_total_amount
        self.config_manager.daily_trade_loss = self.daily_trade_loss
        self.config_manager.daily_completed_trades = self.daily_completed_trades
        self.config_manager.last_trade_date = self.last_trade_date
        
        # 保存配置
        self.config_manager.save_config()
    
    def init_daily_balance(self):
        """初始化当天初始资金"""
        if not self.csrf_token or not self.cookie:
            self.log_message("认证信息未设置，跳过获取初始资金")
            return
        
        # 检查是否已经设置过当天的初始资金
        today = datetime.now().strftime('%Y-%m-%d')
        if (self.config_manager.daily_initial_balance is not None and 
            self.config_manager.last_trade_date == today):
            self.log_message(f"当天初始资金已设置: {self.config_manager.daily_initial_balance} USDT")
            return
        
        # 在新线程中获取初始资金，避免阻塞UI
        def fetch_initial_balance():
            try:
                self.log_message("正在获取当天初始资金...")
                balance = self.api.get_funding_balance()
                
                if balance is not None:
                    self.config_manager.set_daily_initial_balance(balance)
                    self.log_message(f"✅ 当天初始资金已设置: {balance} USDT")
                    # 更新显示
                    self.root.after(0, self.update_daily_initial_balance_display)
                else:
                    self.log_message("⚠️ 获取初始资金失败，请稍后重试")
            except Exception as e:
                self.log_message(f"获取初始资金异常: {str(e)}")
        
        threading.Thread(target=fetch_initial_balance, daemon=True).start()
    
    def update_daily_total_display(self):
        """更新今日交易总额显示"""
        try:
            if hasattr(self, 'daily_total_label') and self.daily_total_label:
                self.daily_total_label.config(text=f"{self.daily_total_amount:.2f} USDT")
                self.log_message(f"今日交易总额显示已更新: {self.daily_total_amount:.2f} USDT")
            else:
                self.log_message("今日交易总额标签尚未创建，将在界面完全加载后重试")
                # 如果标签还没创建，延迟100ms后重试
                self.root.after(100, self.update_daily_total_display)
        except Exception as e:
            self.log_message(f"更新今日交易总额显示失败: {str(e)}")

    def run(self):
        """运行应用"""
        self.log_message("币安量化交易系统启动")
        
        # 初始化认证信息过期显示
        self.root.after(1000, self.update_auth_expiry_display)
        
        self.root.mainloop()
    

    def update_trade_amount(self, symbol, price):
        """更新成交额"""
        try:
            # 根据代币类型设置交易金额：KOGE使用1025，其他代币使用1030
            trade_amount = 1025.0 if symbol == "ALPHA_22USDT" else 4120.0
            # trade_amount = 1.0  # 测试模式：统一使用1 USDT
            current_amount = self.tokens[symbol].get('trade_amount', 0.0)
            new_amount = current_amount + trade_amount
            
            # 更新单个代币成交额
            self.tokens[symbol]['trade_amount'] = new_amount
            
            # 更新今日交易总额
            self.daily_total_amount += trade_amount
            self.last_trade_date = datetime.now().strftime('%Y-%m-%d')
            
            # 保存配置
            self.save_config()
            
            # 更新界面
            self.root.after(0, self.update_tree_view)
            self.root.after(0, self.update_daily_total_display)
            self.root.after(0, self.update_daily_loss_display)
            
            display_name = self.tokens[symbol].get('display_name', symbol)
            self.log_message(f"{display_name} 成交额更新: {current_amount:.2f} -> {new_amount:.2f} USDT，今日总额: {self.daily_total_amount:.2f} USDT")
        except Exception as e:
            self.log_message(f"更新成交额失败: {str(e)}")

    def update_daily_loss_display(self):
        """更新今日损耗显示"""
        try:
            if hasattr(self, 'daily_loss_label') and self.daily_loss_label:
                self.daily_loss_label.config(text=f"{self.daily_trade_loss:.2f} USDT")
                self.log_message(f"今日损耗显示已更新: {self.daily_trade_loss:.2f} USDT")
            else:
                self.log_message("今日损耗标签尚未创建，将在界面完全加载后重试")
                # 如果标签还没创建，延迟100ms后重试
                self.root.after(100, self.update_daily_loss_display)
        except Exception as e:
            self.log_message(f"更新今日损耗显示失败: {str(e)}")
    
    def update_daily_trade_count_display(self):
        """更新今日交易次数显示"""
        try:
            if hasattr(self, 'daily_trade_count_label') and self.daily_trade_count_label:
                self.daily_trade_count_label.config(text=f"{self.daily_completed_trades}")
                self.log_message(f"今日交易次数显示已更新: {self.daily_completed_trades}")
            else:
                self.log_message("今日交易次数标签尚未创建，将在界面完全加载后重试")
                # 如果标签还没创建，延迟100ms后重试
                self.root.after(100, self.update_daily_trade_count_display)
        except Exception as e:
            self.log_message(f"更新今日交易次数显示失败: {str(e)}")
            
    def increment_daily_trade_count(self):
        """增加今日交易次数"""
        self.daily_completed_trades = self.config_manager.increment_trade_count()
        self.root.after(0, self.update_daily_trade_count_display)
        self.log_message(f"今日已完成交易次数: {self.daily_completed_trades}")
    
    def update_daily_initial_balance_display(self):
        """更新今日初始余额显示"""
        try:
            if hasattr(self, 'daily_initial_balance_label') and self.daily_initial_balance_label:
                initial_balance = self.config_manager.daily_initial_balance
                if initial_balance is not None:
                    self.daily_initial_balance_label.config(text=f"{initial_balance:.2f} USDT")
                else:
                    self.daily_initial_balance_label.config(text="-- USDT")
            else:
                # 如果标签还没创建，延迟100ms后重试
                self.root.after(100, self.update_daily_initial_balance_display)
        except Exception as e:
            self.log_message(f"更新今日初始余额显示失败: {str(e)}")
    
    def update_daily_end_balance_display(self):
        """更新今日结束余额显示"""
        try:
            if hasattr(self, 'daily_end_balance_label') and self.daily_end_balance_label:
                end_balance = self.config_manager.daily_end_balance
                if end_balance is not None:
                    self.daily_end_balance_label.config(text=f"{end_balance:.2f} USDT")
                else:
                    self.daily_end_balance_label.config(text="-- USDT")
            else:
                # 如果标签还没创建，延迟100ms后重试
                self.root.after(100, self.update_daily_end_balance_display)
        except Exception as e:
            self.log_message(f"更新今日结束余额显示失败: {str(e)}")
    
    def update_auth_expiry_display(self):
        """更新认证信息过期显示"""
        try:
            if hasattr(self, 'auth_expiry_label') and self.auth_expiry_label:
                expiry_info = self.config_manager.get_auth_expiry_info()
                
                # 根据状态设置颜色
                if expiry_info['status'] == 'no_auth':
                    color = '#e74c3c'  # 红色
                elif expiry_info['status'] == 'warning':
                    color = '#f39c12'  # 橙色
                elif expiry_info['status'] == 'expired':
                    color = '#e74c3c'  # 红色
                elif expiry_info['status'] == 'ok':
                    color = '#27ae60'  # 绿色
                else:
                    color = '#e74c3c'  # 红色
                
                self.auth_expiry_label.config(
                    text=expiry_info['message'],
                    fg=color
                )
            else:
                # 如果标签还没创建，延迟100ms后重试
                self.root.after(100, self.update_auth_expiry_display)
        except Exception as e:
            self.log_message(f"更新认证信息过期显示失败: {str(e)}")

def main():
    """主函数"""
    try:
        app = BinanceTrader()
        app.run()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
