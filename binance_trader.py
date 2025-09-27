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

class BinanceTrader:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Binance Auto Trade - 币安量化交易系统")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # 居中显示主窗口
        self.center_window(self.root, 1000, 700)
        
        # 进行MAC地址校验
        if not self.check_mac_permission():
            return  # 权限校验失败，不继续初始化
        
        # 币安ALPHA API基础URL
        self.base_url = "https://www.binance.com/bapi/defi/v1/public/alpha-trade"
        
        # 存储代币数据
        self.tokens = {}
        
        # 稳定度看板数据
        self.stability_data = []
        
        # 用户设置的CSRF token和Cookie
        self.csrf_token = None
        self.cookie = None
        
        # 配置文件路径
        self.config_file = "config.json"
        
        # 加载配置
        self.load_config()
        
        # 自动交易状态
        self.auto_trading = {}  # 存储每个代币的自动交易状态
        self.trading_threads = {}  # 存储交易线程
        
        # 存储输入框和按钮的引用
        
        # 加载ALPHA代币ID映射
        self.alpha_id_map = self.load_alpha_id_map()
        
        # 创建界面
        self.create_widgets()
        
        # 添加常驻的KOGE代币
        self.add_koge_token()
    
    def get_mac_address(self):
        """获取当前电脑的MAC地址"""
        try:
            # 获取MAC地址
            mac = uuid.getnode()
            # 转换为十六进制字符串
            mac_str = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
            return mac_str
        except Exception as e:
            print(f"获取MAC地址失败: {e}")
            return None
    
    def get_mac_hash(self):
        """获取MAC地址的MD5哈希值"""
        mac = self.get_mac_address()
        if mac:
            return hashlib.md5(mac.encode()).hexdigest()
        return None
    
    def check_mac_permission(self):
        """检查MAC地址权限"""
        # 允许的MAC地址哈希值列表
        allowed_mac_hashes = [
            "3a36b385f3a6953d8c732bea92e3ca2a",  # 当前电脑的MAC地址哈希
            "188a66fe2f45fb0dc42d8b67d9abdc3a",  # 新增MAC地址1
            "c99cfed938c7e379ed5f73cb2f14ad61",  # 新增MAC地址2
            "68c3110ad7fc78479caf1442f11faf84",  # 新增MAC地址3
            # 可以添加更多允许的MAC地址哈希值
        ]
        
        current_mac_hash = self.get_mac_hash()
        if not current_mac_hash:
            self.show_permission_error("无法获取设备信息")
            return False
        
        if current_mac_hash not in allowed_mac_hashes:
            self.show_permission_error(f"设备未授权\n当前设备哈希: {current_mac_hash}")
            return False
        
        print(f"MAC地址校验通过: {current_mac_hash}")
        return True
    
    def show_permission_error(self, message):
        """显示权限错误对话框"""
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        # 创建错误对话框
        error_dialog = tk.Toplevel(root)
        error_dialog.title("权限验证失败")
        error_dialog.geometry("400x200")
        error_dialog.configure(bg='#f0f0f0')
        error_dialog.resizable(False, False)
        
        # 居中显示
        screen_width = error_dialog.winfo_screenwidth()
        screen_height = error_dialog.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 200) // 2
        error_dialog.geometry(f"400x200+{x}+{y}")
        
        # 设置窗口置顶
        error_dialog.attributes('-topmost', True)
        
        # 创建内容
        frame = tk.Frame(error_dialog, bg='#f0f0f0')
        frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # 错误图标和标题
        title_label = tk.Label(
            frame, 
            text="❌ 无权限使用该软件", 
            font=('Arial', 14, 'bold'),
            fg='#e74c3c',
            bg='#f0f0f0'
        )
        title_label.pack(pady=(0, 10))
        
        # 错误信息
        message_label = tk.Label(
            frame,
            text=message,
            font=('Arial', 10),
            fg='#333333',
            bg='#f0f0f0',
            wraplength=350,
            justify='center'
        )
        message_label.pack(pady=(0, 20))
        
        # 确定按钮
        ok_button = tk.Button(
            frame,
            text="确定",
            font=('Arial', 10, 'bold'),
            bg='#e74c3c',
            fg='white',
            width=10,
            height=2,
            command=lambda: [error_dialog.destroy(), root.destroy(), sys.exit()]
        )
        ok_button.pack()
        
        # 绑定关闭事件
        error_dialog.protocol("WM_DELETE_WINDOW", lambda: [error_dialog.destroy(), root.destroy(), sys.exit()])
        
        # 显示对话框
        error_dialog.mainloop()
        
        # 自动交易状态
        self.auto_trading = {}  # 存储每个代币的自动交易状态
        self.trading_threads = {}  # 存储交易线程
        
        # 存储输入框和按钮的引用
        
        # 加载ALPHA代币ID映射
        self.alpha_id_map = self.load_alpha_id_map()
        
        # 创建界面
        self.create_widgets()
        
        # 添加常驻的KOGE代币
        self.add_koge_token()
    
    def load_alpha_id_map(self):
        """加载ALPHA代币ID映射"""
        try:
            with open('alphaIdMap.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("未找到alphaIdMap.json文件，将使用默认映射")
            return {"KOGE": "ALPHA_22"}
        except Exception as e:
            print(f"加载alphaIdMap.json失败: {e}")
            return {"KOGE": "ALPHA_22"}
    
    def add_koge_token(self):
        """添加常驻的KOGE代币"""
        koge_symbol = "ALPHA_22USDT"  # KOGE的ALPHA ID
        self.tokens[koge_symbol] = {
            'price': 0.0,
            'last_update': datetime.now(),
            'display_name': 'KOGE'
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
        
        # 状态标签
        self.status_label = tk.Label(
            input_frame, 
            text="就绪", 
            font=('Arial', 10),
            fg='green',
            bg='#f0f0f0'
        )
        self.status_label.pack(side='right', padx=10)
        
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
        
        # 设置Token按钮
        token_btn = tk.Button(
            control_frame,
            text="设置Token",
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
    
    def show_token_dialog(self):
        """显示Token设置对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("设置认证信息")
        dialog.geometry("600x520")
        dialog.configure(bg='#2c3e50')
        dialog.resizable(False, False)
        
        # 使对话框居中
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示对话框
        self.center_window(dialog, 600, 520)
        
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
            height=6,
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
5. 找到API请求，查看Request Headers中的：
   - csrftoken字段（第一行）
   - Cookie字段（第二行）
6. 复制这些值并粘贴到下方输入框"""
        
        info_text.config(state='normal')
        info_text.insert('1.0', info_content)
        info_text.config(state='disabled')
        
        # 输入框区域
        input_frame = tk.Frame(dialog, bg='#2c3e50')
        input_frame.pack(fill='x', padx=20, pady=10)
        
        # CSRF Token输入框
        csrf_frame = tk.Frame(input_frame, bg='#2c3e50')
        csrf_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            csrf_frame,
            text="CSRF Token:",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#2c3e50'
        ).pack(anchor='w', pady=(0, 5))
        
        csrf_entry = tk.Entry(
            csrf_frame,
            font=('Consolas', 11),
            width=70
        )
        csrf_entry.pack(fill='x', pady=(0, 5))
        
        # 如果已有token，显示完整token
        if self.csrf_token:
            csrf_entry.insert(0, self.csrf_token)
        
        # Cookie输入框
        cookie_frame = tk.Frame(input_frame, bg='#2c3e50')
        cookie_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            cookie_frame,
            text="Cookie:",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#2c3e50'
        ).pack(anchor='w', pady=(0, 5))
        
        cookie_text = tk.Text(
            cookie_frame,
            height=6,
            font=('Consolas', 10),
            wrap='word'
        )
        cookie_text.pack(fill='x', pady=(0, 5))
        
        # 如果已有cookie，显示完整cookie
        if self.cookie:
            cookie_text.insert('1.0', self.cookie)
        
        # 按钮区域
        button_frame = tk.Frame(dialog, bg='#2c3e50')
        button_frame.pack(fill='x', padx=20, pady=(10, 20))
        
        def save_tokens():
            csrf_token = csrf_entry.get().strip()
            cookie = cookie_text.get('1.0', 'end-1c').strip()
            
            if not csrf_token:
                messagebox.showwarning("警告", "请输入CSRF Token")
                return
            
            if not cookie:
                messagebox.showwarning("警告", "请输入Cookie")
                return
            
            self.csrf_token = csrf_token
            self.cookie = cookie
            self.save_config()  # 保存到配置文件
            self.log_message("认证信息设置成功并已保存")
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
            text="确认",
            command=save_tokens,
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15
        )
        confirm_btn.pack(side='right')
        
        # 绑定回车键
        csrf_entry.bind('<Return>', lambda e: save_tokens())
        csrf_entry.focus()
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}\n"
        
        # 检查log_text是否已创建
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, log_msg)
            self.log_text.see(tk.END)
            
            # 限制日志行数
            lines = self.log_text.get("1.0", tk.END).count('\n')
            if lines > 100:
                self.log_text.delete("1.0", "10.0")
        else:
            # 如果log_text还未创建，先打印到控制台
            print(log_msg.strip())
    
    def update_status(self, message, color='green'):
        """更新状态标签"""
        self.status_label.config(text=message, fg=color)
        self.root.update_idletasks()
    
    def get_token_price(self, symbol):
        """获取代币价格（使用K线接口）"""
        try:
            url = f"{self.base_url}/klines"
            params = {
                'symbol': symbol,
                'interval': '1s',  # 1秒间隔获取最新价格
                'limit': 1  # 只获取1条K线数据
            }
            
            # 价格获取使用公开接口，不需要认证信息
            
            # 使用公开接口的请求头
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Baggage': 'sentry-environment=prod,sentry-release=20250924-d1d0004c-2900,sentry-public_key=9445af76b2ba747e7b574485f2c998f7,sentry-trace_id=847f639347bc49be967b6777b03a413c,sentry-sample_rate=0.01,sentry-transaction=%2Falpha%2F%24chainSymbol%2F%24contractAddress,sentry-sampled=false',
                'Bnc-Uuid': 'e420e928-1b68-4ea2-991d-016cf1dc6f8b',
                'Clienttype': 'web',
                'Content-Type': 'application/json',
                'Cookie': self.cookie,
                'device-info': 'eyJzY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsImF2YWlsYWJsZV9zY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsInN5c3RlbV92ZXJzaW9uIjoiV2luZG93cyAxMCIsImJyYW5kX21vZGVsIjoidW5rbm93biIsInN5c3RlbV9sYW5nIjoiemgtQ04iLCJ0aW1lem9uZSI6IkdNVCswODowMCIsInRpbWV6b25lT2Zmc2V0IjotNDgwLCJ1c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0MC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwibGlzdF9wbHVnaW4iOiJQREYgVmlld2VyLENocm9tZSBQREYgVmlld2VyLENocm9taXVtIFBERiBWaWV3ZXIsTWljcm9zb2Z0IEVkZ2UgUERGIFZpZXdlcixXZWJLaXQgYnVpbHQtaW4gUERGIiwiY2FudmFzX2NvZGUiOiI2NjAzODQzMyIsIndlYmdsX3ZlbmRvciI6Ikdvb2dsZSBJbmMuIChOVklESUEpIiwid2ViZ2xfcmVuZGVyZXIiOiJBTkdMRSAoTlZJRElBLCBOVklESUEgR2VGb3JjZSBSVFggMzA3MCAoMHgwMDAwMjQ4OCkgRGlyZWN0M0QxMSB2c181XzAgcHNfNV8wLCBEM0QxMSkiLCJhdWRpbyI6IjEyNC4wNDM0NzUyNzUxNjA3NCIsInBsYXRmb3JtIjoiV2luMzIiLCJ3ZWJfdGltZXpvbmUiOiJBc2lhL1NoYW5naGFpIiwiZGV2aWNlX25hbWUiOiJDaHJvbWUgVjE0MC4wLjAuMCAoV2luZG93cykiLCJmaW5nZXJwcmludCI6ImI0NzNmZjVhODA0ODU4YWQ2ZmYxYTdhNmQ2YzY0NjIzIiwiZGV2aWNlX2lkIjoiIiwicmVsYXRlZF9kZXZpY2VfaWRzIjoiIn0=',
                'fvideo-id': '33ea495bf3a5a79b884c5845faf9ca5e77e32ab5',
                'lang': 'zh-CN',
                'Priority': 'u=1, i',
                'Referer': 'https://www.binance.com/zh-CN/alpha/bsc/0xe6df05ce8c8301223373cf5b969afcb1498c5528',
                'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'Sentry-Trace': '847f639347bc49be967b6777b03a413c-ac242fc8bf0e51e2-0',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
                'X-Passthrough-Token': '',
                'X-Trace-Id': '000f2190-8b35-4cb1-aa27-d62a5017a918',
                'X-Ui-Request-Trace': '000f2190-8b35-4cb1-aa27-d62a5017a918'
            }
            
            # 设置cookies
            cookies = {
                'theme': 'dark',
                'bnc-uuid': 'e420e928-1b68-4ea2-991d-016cf1dc6f8b',
                '_gid': 'GA1.2.951612344.1758819202',
                'BNC_FV_KEY': '33ea495bf3a5a79b884c5845faf9ca5e77e32ab5',
                'ref': 'FEQE7YL0',
                'lang': 'zh-CN',
                'language': 'zh-CN',
                'se_sd': 'AQPAhWVkMHTCRVWMRBgVgZZDBDA9TEQUlsN5aVEd1lcUgVVNWV4A1',
                'se_gd': 'QZaVlDhAHQRA1IaRXUBMgZZAFVQcUBQUlpc5aVEd1lcUgG1NWVAP1',
                'se_gsd': 'YDo2XDtWNTAgCSMrNAgnMzkECQIaBQYaV11BUl1QVllaJ1NT1',
                'currentAccount': '',
                'logined': 'y',
                'BNC-Location': 'CN',
                'aws-waf-token': '6a2e990f-c746-49ff-9096-b327596dd9d8:BgoAZZh3lccKAAAA:frs4tlGhn0srGqMVNdKjOUR6E1AopfP/a3uZHcPKLSFBKkQjYpgbOsjbsL/PuL7PzWy1a6xg+L7J/Hnb9L5xAb88hAOBFBDOL358HxuVvNgpN41Rqv/RGGnERAcxnm6cSRWMXbe+yCluzdyiGMFLc5oMXF4CTn0fUmdeBrXbkaCX0HYuT8/3xnMjVTs2E0cbasI=',
                '_gcl_au': '1.1.1119987010.1758819849',
                'changeBasisTimeZone': '',
                'userPreferredCurrency': 'USD_USD',
                'BNC_FV_KEY_T': '101-ya6ZGxeFJ63HG8vatAZthWy4Sjc5qu1P2aV50Sb2TEtgnS4ZbkrDqmNQWTQ6cP%2FyOPWacDiBfIZ8GRjL8bGDig%3D%3D-dPwS3iTPmfQHOxcm1JrBNQ%3D%3D-0e',
                'BNC_FV_KEY_EXPIRE': '1758929057818',
                '_uetsid': 'a955dd009a3111f08ea99b841f36689a',
                '_uetvid': 'a955d8909a3111f08c0c25e413aeab0c',
                's9r1': 'CA65B5057A146BFF9C192E8BD726E97A',
                'r20t': 'web.AD47E59A1520E690EFDD909400E9E08E',
                'r30t': '1',
                'cr00': 'F92A672B1280C3A02CAF0E64D3756059',
                'd1og': 'web.1162735228.F4F8D3766A63F34B04DA0A322745A3C8',
                'r2o1': 'web.1162735228.56CD4DF4A52B7CA2AA5BE433C63EABB1',
                'f30l': 'web.1162735228.75764A4A9618F09433B203557F3AE012',
                'p20t': 'web.1162735228.EBF4B2B5DB6916330942ED764FAEE65E',
                '_ga_3WP50LGEEC': 'GS2.1.s1758904316$o4$g1$t1758912362$j36$l0$h0',
                'OptanonConsent': 'isGpcEnabled=0&datestamp=Sat+Sep+27+2025+02%3A46%3A04+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202506.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=7e0430b4-07eb-4780-a2e2-48b9be3dd13c&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1&AwaitingReconsent=false',
                '_gat_UA-162512367-1': '1',
                '_ga': 'GA1.2.1952928982.1758819202',
                'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%221162735228%22%2C%22first_id%22%3A%2219981cb2b079d5-0702e12ae9987a-26061951-3686400-19981cb2b08181c%22%2C%22props%22%3A%7B%22aws_waf_referrer%22%3A%22%7B%5C%22referrer%5C%22%3A%5C%22https%3A%2F%2Falpha123.uk%2F%5C%22%7D%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTk5ODFjYjJiMDc5ZDUtMDcwMmUxMmFlOTk4N2EtMjYwNjE5NTEtMzY4NjQwMC0xOTk4MWNiMmIwODE4MWMiLCIkaWRlbnRpdHlfbG9naW5faWQiOiIxMTYyNzM1MjI4In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%221162735228%22%7D%2C%22%24device_id%22%3A%2219981dc7d84bdb-0b69a1775381dc8-26061951-3686400-19981dc7d851c20%22%7D',
                '_gat': '1'
            }
            
            # 创建session并设置cookies
            session = requests.Session()
            session.cookies.update(cookies)
            
            response = session.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') == '000000' and data.get('success') == True:
                kline_data = data.get('data', [])
                if kline_data and len(kline_data) > 0:
                    # 解析K线数据，返回格式化的价格数据
                    kline = kline_data[0]
                    return {
                        'price': kline[4],  # 收盘价（最新价格）
                        'open': kline[1],   # 开盘价
                        'high': kline[2],   # 最高价
                        'low': kline[3],    # 最低价
                        'volume': kline[5], # 成交量
                        'timestamp': kline[6]  # 收盘时间戳
                    }
                else:
                    return None
            else:
                self.log_message(f"API调用失败: {data.get('message', '未知错误')}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.log_message(f"获取 {symbol} 价格失败: {str(e)}")
            return None
    
    def get_token_24h_stats(self, symbol):
        """获取代币24小时统计（ALPHA接口暂不支持，返回None）"""
        # ALPHA接口暂不支持24小时统计，返回None
        return None
    
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
            messagebox.showerror("错误", f"未找到代币 {symbol} 的ALPHA ID，请检查代币名称")
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
                    'auto_trading': False  # 默认不自动交易
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
        self.toggle_auto_trading(symbol)
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
        self.root.after(100, lambda: self.toggle_auto_trading(symbol))
    
    
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
        """清空所有代币（保留KOGE）"""
        if messagebox.askyesno("确认", "确定要清空所有代币吗？（KOGE将保留）"):
            # 保留KOGE代币
            koge_token = self.tokens.get("ALPHA_22USDT")
            
            # 清理所有相关组件
            # 先清理所有嵌入的组件
            for symbol, data in self.tokens.items():
                if 'widgets' in data:
                    widgets = data['widgets']
                    for widget in widgets.values():
                        if widget.winfo_exists():
                            widget.destroy()
            
            self.auto_trading.clear()
            self.trading_threads.clear()
            
            self.tokens.clear()
            if koge_token:
                # 移除change_24h字段，添加交易相关字段
                koge_token = {
                    'price': koge_token['price'],
                    'last_update': koge_token['last_update'],
                    'display_name': koge_token['display_name'],
                    'trade_count': 1,
                    'trade_amount': 0.0,
                    'auto_trading': False
                }
                self.tokens["ALPHA_22USDT"] = koge_token
            self.update_tree_view()
            self.log_message("已清空所有代币（KOGE已保留）")
    
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
    
    def fetch_stability_data(self):
        """获取稳定度看板数据"""
        try:
            # 首先尝试模拟浏览器请求
            return self.fetch_stability_data_requests()
        except Exception as e:
            self.log_message(f"模拟请求失败，尝试Selenium: {str(e)}")
            try:
                return self.fetch_stability_data_selenium()
            except Exception as e2:
                self.log_message(f"Selenium也失败，尝试API: {str(e2)}")
                return self.fetch_stability_data_api()
    
    def fetch_stability_data_requests(self):
        """使用requests直接调用API获取稳定度数据"""
        try:
            # 直接调用API接口
            api_url = "https://alpha123.uk/stability_feed.json"
            
            # 简化的请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://alpha123.uk/zh/stability.html'
            }
            
            response = requests.get(api_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # 解析JSON数据
            api_data = response.json()
            stability_data = []
            
            # 根据您提供的JSON结构解析数据
            if isinstance(api_data, dict) and 'items' in api_data:
                items = api_data['items']
                
                for item in items:
                    if isinstance(item, dict):
                        # 从display字段提取项目名称（去掉/USDT后缀）
                        display = item.get('display', '')
                        project = display.replace('/USDT', '') if display else item.get('key', '')
                        
                        # 获取最新价格
                        metrics = item.get('metrics', {})
                        last_price = metrics.get('lastPrice', 0)
                        
                        # 获取稳定度状态
                        status = item.get('status', {})
                        status_text = status.get('text', 'unknown')
                        
                        # 转换稳定度为中文
                        stability_map = {
                            'stable': '稳定',
                            'unstable': '不稳定',
                            'general': '一般',
                            'moderate': '一般',
                            'unknown': '未知'
                        }
                        stability = stability_map.get(status_text.lower(), '未知')
                        
                        # 获取4倍剩余天数
                        multiplier_days = item.get('multiplier_days', 0)
                        
                        stability_data.append({
                            'project': project,
                            'stability': stability,
                            'price': str(last_price),
                            'remaining_days': str(multiplier_days)
                        })
            
            # 如果API返回的是数组格式
            elif isinstance(api_data, list):
                for item in api_data:
                    if isinstance(item, dict):
                        display = item.get('display', '')
                        project = display.replace('/USDT', '') if display else item.get('key', '')
                        
                        # 获取最新价格
                        metrics = item.get('metrics', {})
                        last_price = metrics.get('lastPrice', 0)
                        
                        # 获取稳定度状态
                        status = item.get('status', {})
                        status_text = status.get('text', 'unknown')
                        
                        # 转换稳定度为中文
                        stability_map = {
                            'stable': '稳定',
                            'unstable': '不稳定',
                            'general': '一般',
                            'moderate': '一般',
                            'unknown': '未知'
                        }
                        stability = stability_map.get(status_text.lower(), '未知')
                        
                        # 获取4倍剩余天数
                        multiplier_days = item.get('multiplier_days', 0)
                        
                        stability_data.append({
                            'project': project,
                            'stability': stability,
                            'price': str(last_price),
                            'remaining_days': str(multiplier_days)
                        })
            
            # 对数据进行排序：KOGE固定排第一位，其他按稳定度排序
            def sort_key(item):
                project = item['project']
                stability = item['stability']
                
                # KOGE固定排第一位
                if project == 'KOGE':
                    return (0, 0)
                
                # 其他按稳定度排序：稳定 > 一般 > 不稳定
                stability_order = {
                    '稳定': 1,
                    '一般': 2,
                    'moderate': 2,  # 处理英文状态
                    '不稳定': 3,
                    'unstable': 3,  # 处理英文状态
                    '未知': 4
                }
                
                return (1, stability_order.get(stability, 4))
            
            stability_data.sort(key=sort_key)
            
            self.log_message(f"从API获取到 {len(stability_data)} 个稳定度项目")
            return stability_data
            
        except Exception as e:
            self.log_message(f"API调用失败: {str(e)}")
            # 如果API失败，尝试备用方法
            return self.fetch_stability_data_fallback()
    
    def fetch_stability_data_fallback(self):
        """备用方法：使用模拟数据"""
        try:
            # 基于您之前提供的图片数据
            stability_data = [
                {
                    'project': 'AOP',
                    'stability': '稳定',
                    'price': '0.06210104',
                    'remaining_days': '23'
                },
                {
                    'project': 'KOGE',
                    'stability': '稳定',
                    'price': '48.00171117',
                    'remaining_days': '0'
                },
                {
                    'project': 'MCH',
                    'stability': '稳定',
                    'price': '0.02252917',
                    'remaining_days': '7'
                },
                {
                    'project': 'WOD',
                    'stability': '稳定',
                    'price': '0.11043909',
                    'remaining_days': '4'
                },
                {
                    'project': 'ZEUS',
                    'stability': '一般',
                    'price': '0.11610119',
                    'remaining_days': '17'
                },
                {
                    'project': 'ALEO',
                    'stability': '不稳定',
                    'price': '0.21285',
                    'remaining_days': '18'
                },
                {
                    'project': 'FROGGIE',
                    'stability': '不稳定',
                    'price': '0.03525713',
                    'remaining_days': '24'
                },
                {
                    'project': 'POP',
                    'stability': '不稳定',
                    'price': '0.00861099',
                    'remaining_days': '14'
                }
            ]
            
            # 对备用数据也进行排序
            def sort_key(item):
                project = item['project']
                stability = item['stability']
                
                if project == 'KOGE':
                    return (0, 0)
                
                stability_order = {
                    '稳定': 1,
                    '一般': 2,
                    '不稳定': 3,
                    '未知': 4
                }
                
                return (1, stability_order.get(stability, 4))
            
            stability_data.sort(key=sort_key)
            
            self.log_message(f"使用备用数据: {len(stability_data)} 个项目")
            return stability_data
            
        except Exception as e:
            self.log_message(f"requests获取稳定度数据失败: {str(e)}")
            return self.fetch_stability_data_fallback()
    
    def fetch_stability_data_selenium(self):
        """使用Selenium获取稳定度数据"""
        driver = None
        try:
            # 配置Chrome选项
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # 启动浏览器
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("https://alpha123.uk/zh/stability.html")
            
            # 等待页面加载完成
            wait = WebDriverWait(driver, 10)
            
            # 等待表格数据加载完成
            try:
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
                # 等待数据加载（不是"加载中..."）
                wait.until(lambda driver: "加载中" not in driver.page_source)
            except:
                self.log_message("等待数据加载超时")
            
            # 获取页面源码
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 解析表格数据
            stability_data = []
            table = soup.find('table')
            
            if table:
                rows = table.find_all('tr')[1:]  # 跳过表头
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        project = cells[0].get_text(strip=True)
                        stability_text = cells[1].get_text(strip=True)
                        latest_price = cells[2].get_text(strip=True)
                        remaining_days = cells[3].get_text(strip=True)
                        
                        # 跳过"加载中..."行
                        if project == "加载中..." or not project:
                            continue
                        
                        # 确定稳定度状态
                        stability_status = "未知"
                        if "稳定" in stability_text:
                            stability_status = "稳定"
                        elif "一般" in stability_text:
                            stability_status = "一般"
                        elif "不稳定" in stability_text:
                            stability_status = "不稳定"
                        
                        stability_data.append({
                            'project': project,
                            'stability': stability_status,
                            'price': latest_price,
                            'remaining_days': remaining_days
                        })
            
            self.log_message(f"通过Selenium获取了 {len(stability_data)} 个稳定度项目")
            return stability_data
            
        except Exception as e:
            self.log_message(f"Selenium获取稳定度数据失败: {str(e)}")
            return []
        finally:
            if driver:
                driver.quit()
    
    def fetch_stability_data_api(self):
        """尝试通过API获取稳定度数据"""
        try:
            # 尝试查找可能的API接口
            api_urls = [
                "https://alpha123.uk/api/stability",
                "https://alpha123.uk/api/zh/stability",
                "https://alpha123.uk/api/data/stability"
            ]
            
            for api_url in api_urls:
                try:
                    response = requests.get(api_url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        # 解析API数据
                        stability_data = []
                        for item in data:
                            stability_data.append({
                                'project': item.get('project', ''),
                                'stability': item.get('stability', '未知'),
                                'price': str(item.get('price', '')),
                                'remaining_days': str(item.get('remaining_days', ''))
                            })
                        self.log_message(f"通过API获取了 {len(stability_data)} 个稳定度项目")
                        return stability_data
                except:
                    continue
            
            # 如果API都失败，返回空数据
            self.log_message("所有API接口都无法访问")
            return []
            
        except Exception as e:
            self.log_message(f"API获取稳定度数据失败: {str(e)}")
            return []
    
    def show_stability_dashboard(self):
        """显示稳定度看板窗口"""
        # 创建新窗口
        stability_window = tk.Toplevel(self.root)
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
        
        # 初始加载数据
        self.refresh_stability_data(stability_window)
    
    def refresh_stability_data(self, window):
        """刷新稳定度数据"""
        def fetch_data():
            window.status_label.config(text="正在获取数据...", fg='orange')
            
            data = self.fetch_stability_data()
            
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
            
            # 根据稳定度设置颜色标签
            stability_display = stability
            if stability == "稳定":
                stability_display = "🟢 稳定"
            elif stability == "一般":
                stability_display = "🟡 一般"
            elif stability == "不稳定":
                stability_display = "🔴 不稳定"
            
            window.tree.insert('', 'end', values=(
                project,
                stability_display,
                price,
                remaining_days,
                "添加"
            ))
        
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
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.csrf_token = config.get('csrf_token')
                    self.cookie = config.get('cookie')
                    if self.csrf_token and self.cookie:
                        print(f"已加载配置: CSRF Token: {self.csrf_token[:10]}..., Cookie: {self.cookie[:50]}...")
        except Exception as e:
            print(f"加载配置文件失败: {e}")
    
    def save_config(self):
        """保存配置文件"""
        try:
            config = {
                'csrf_token': self.csrf_token,
                'cookie': self.cookie
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print("配置已保存")
        except Exception as e:
            print(f"保存配置文件失败: {e}")

    def run(self):
        """运行应用"""
        self.log_message("币安量化交易系统启动")
        self.root.mainloop()
    
    
    def toggle_auto_trading(self, symbol):
        """切换自动交易状态"""
        display_name = self.tokens[symbol].get('display_name', symbol)
        
        # 添加调试信息
        current_status = self.auto_trading.get(symbol, False)
        self.log_message(f"[DEBUG] {display_name} toggle_auto_trading 被调用，当前状态: {current_status}")
        
        if symbol in self.auto_trading and self.auto_trading[symbol]:
            # 停止自动交易
            self.auto_trading[symbol] = False
            self.tokens[symbol]['auto_trading'] = False
            if symbol in self.trading_threads:
                # 这里可以添加停止线程的逻辑
                pass
            self.log_message(f"{display_name} 自动交易已停止")
            
            # 更新表格显示
            self.update_tree_view()
        else:
            # 开始自动交易
            if not self.csrf_token or not self.cookie:
                messagebox.showerror("错误", "请先设置认证信息")
                return
            
            self.auto_trading[symbol] = True
            self.tokens[symbol]['auto_trading'] = True
            
            # 启动自动交易线程
            thread = threading.Thread(target=self.auto_trade_worker, args=(symbol,), daemon=True)
            self.trading_threads[symbol] = thread
            thread.start()
            
            self.log_message(f"{display_name} 自动交易已开始")
            
            # 更新表格显示
            self.update_tree_view()
    
    def auto_trade_worker(self, symbol):
        """自动交易工作线程 - 单向交易模式"""
        trade_count = self.tokens[symbol].get('trade_count', 1)
        completed_trades = 0
        display_name = self.tokens[symbol].get('display_name', symbol)
        
        self.log_message(f"{display_name} 开始自动交易，目标次数: {trade_count}")
        
        # 开始自动交易
        
        while self.auto_trading.get(symbol, False) and completed_trades < trade_count:
            try:
                # 添加调试信息
                self.log_message(f"[DEBUG] {display_name} 进入交易循环，auto_trading状态: {self.auto_trading.get(symbol, False)}")
                
                # 1. 获取价格
                price_data = self.get_token_price(symbol)
                if not price_data:
                    self.log_message(f"{display_name} 获取价格失败，等待5秒后重试")
                    time.sleep(5)
                    continue
                
                current_price = float(price_data['price'])
                
                # 2. 下买单（重试机制）
                buy_order_id = None
                while self.auto_trading.get(symbol, False) and not buy_order_id:
                    buy_order_id = self.place_single_order(symbol, current_price, "BUY")
                    if not buy_order_id:
                        self.log_message(f"{display_name} 买单下单失败，等待5秒后重试")
                        time.sleep(5)
                        # 重新获取价格
                        price_data = self.get_token_price(symbol)
                        if price_data:
                            current_price = float(price_data['price'])
                
                # 如果自动交易被停止，跳出外层循环
                if not self.auto_trading.get(symbol, False):
                    break
                
                self.log_message(f"{display_name} 买单下单成功，价格为: {current_price}")
                
                # 3. 等待买单成交（最多6次检查，30秒）
                buy_filled = False
                check_count = 0
                max_checks = 6
                self.log_message(f"[DEBUG] {display_name} 开始等待买单成交，auto_trading状态: {self.auto_trading.get(symbol, False)}")
                
                while self.auto_trading.get(symbol, False) and not buy_filled and check_count < max_checks:
                    time.sleep(5)  # 等待5秒
                    check_count += 1
                    
                    if self.check_single_order_filled(buy_order_id):
                        buy_filled = True
                    else:
                        if check_count < max_checks:
                            self.log_message(f"{display_name} 买单尚未成交，5秒后继续检查委托状态")
                        else:
                            # 6次检查后仍未成交，取消委托并重新下单
                            self.log_message(f"{display_name} 委托已半分钟没有成交，取消委托")
                            self.cancel_all_orders()
                            
                            # 重新获取价格并下单
                            price_data = self.get_token_price(symbol)
                            if price_data:
                                current_price = float(price_data['price'])
                                buy_order_id = self.place_single_order(symbol, current_price, "BUY")
                                if buy_order_id:
                                    self.log_message(f"{display_name} 重新下单成功，价格为: {current_price}")
                                    check_count = 0  # 重置检查计数
                                else:
                                    self.log_message(f"{display_name} 重新下单失败，等待5秒后重试")
                                    time.sleep(5)
                                    continue  # 继续重试，不退出循环
                            else:
                                self.log_message(f"{display_name} 重新获取价格失败，等待5秒后重试")
                                time.sleep(5)
                                continue  # 继续重试，不退出循环
                
                # 如果自动交易被停止，跳出外层循环
                if not self.auto_trading.get(symbol, False):
                    break
                
                # 4. 获取最新价格
                price_data = self.get_token_price(symbol)
                if not price_data:
                    self.log_message(f"{display_name} 获取最新价格失败，等待5秒后重试")
                    time.sleep(5)
                    continue
                
                sell_price = float(price_data['price'])
                
                # 5. 下卖单（重试机制）
                sell_order_id = None
                while self.auto_trading.get(symbol, False) and not sell_order_id:
                    sell_order_id = self.place_single_order(symbol, sell_price, "SELL")
                    if not sell_order_id:
                        self.log_message(f"{display_name} 卖单下单失败，等待5秒后重试")
                        time.sleep(5)
                        # 重新获取价格
                        price_data = self.get_token_price(symbol)
                        if price_data:
                            sell_price = float(price_data['price'])
                
                # 如果自动交易被停止，跳出外层循环
                if not self.auto_trading.get(symbol, False):
                    break
                
                self.log_message(f"{display_name} 卖单下单成功，价格为: {sell_price}")
                
                # 6. 等待卖单成交（最多6次检查，30秒）
                sell_filled = False
                check_count = 0
                max_checks = 6
                
                while self.auto_trading.get(symbol, False) and not sell_filled and check_count < max_checks:
                    time.sleep(5)  # 等待5秒
                    check_count += 1
                    
                    if self.check_single_order_filled(sell_order_id):
                        sell_filled = True
                    else:
                        if check_count < max_checks:
                            self.log_message(f"{display_name} 卖单尚未成交，5秒后继续检查委托状态")
                        else:
                            # 6次检查后仍未成交，取消委托并重新下单
                            self.log_message(f"{display_name} 委托已半分钟没有成交，取消委托")
                            self.cancel_all_orders()
                            
                            # 重新获取价格并下单
                            price_data = self.get_token_price(symbol)
                            if price_data:
                                sell_price = float(price_data['price'])
                                sell_order_id = self.place_single_order(symbol, sell_price, "SELL")
                                if sell_order_id:
                                    self.log_message(f"{display_name} 重新下单成功，价格为: {sell_price}")
                                    check_count = 0  # 重置检查计数
                                else:
                                    self.log_message(f"{display_name} 重新下单失败，等待5秒后重试")
                                    time.sleep(5)
                                    continue  # 继续重试，不退出循环
                            else:
                                self.log_message(f"{display_name} 重新获取价格失败，等待5秒后重试")
                                time.sleep(5)
                                continue  # 继续重试，不退出循环
                
                # 如果自动交易被停止，跳出外层循环
                if not self.auto_trading.get(symbol, False):
                    break
                
                # 一次买卖完成
                completed_trades += 1
                self.log_message(f"{display_name} 第 {completed_trades} 次买卖完成")
                
                # 更新成交额
                self.update_trade_amount(symbol, sell_price)
                
            except Exception as e:
                self.log_message(f"{display_name} 自动交易出错: {str(e)}")
                time.sleep(5)
        
        # 交易完成
        self.auto_trading[symbol] = False
        self.tokens[symbol]['auto_trading'] = False
        
        # 更新表格显示
        self.root.after(0, lambda: self.update_tree_view())
        
        self.log_message(f"{display_name} 自动交易完成，共完成 {completed_trades} 次交易")
    
    
    def place_dual_order(self, symbol, price):
        """同时创建买单和卖单"""
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
                    self.log_message(f"下单失败 - 错误代码: {error_code}, 错误信息: {error_msg}")
            else:
                self.log_message(f"下单失败 - HTTP状态码: {response.status_code}")
            
            return None, None
        except Exception as e:
            self.log_message(f"下单异常: {str(e)}")
            return None, None
    
    def place_single_order(self, symbol, price, side):
        """创建单向订单（买单或卖单）"""
        try:
            url = "https://www.binance.com/bapi/defi/v1/private/alpha-trade/order/place"
            
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Baggage': 'sentry-environment=prod,sentry-release=20250924-d1d0004c-2900,sentry-public_key=9445af76b2ba747e7b574485f2c998f7,sentry-trace_id=847f639347bc49be967b6777b03a413c,sentry-sample_rate=0.01,sentry-transaction=%2Falpha%2F%24chainSymbol%2F%24contractAddress,sentry-sampled=false',
                'Bnc-Uuid': 'e420e928-1b68-4ea2-991d-016cf1dc6f8b',
                'Clienttype': 'web',
                'Content-Type': 'application/json',
                'Cookie': self.cookie,
                'csrftoken': self.csrf_token,
                'device-info': 'eyJzY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsImF2YWlsYWJsZV9zY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsInN5c3RlbV92ZXJzaW9uIjoiV2luZG93cyAxMCIsImJyYW5kX21vZGVsIjoidW5rbm93biIsInN5c3RlbV9sYW5nIjoiemgtQ04iLCJ0aW1lem9uZSI6IkdNVCswODowMCIsInRpbWV6b25lT2Zmc2V0IjotNDgwLCJ1c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0MC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwibGlzdF9wbHVnaW4iOiJQREYgVmlld2VyLENocm9tZSBQREYgVmlld2VyLENocm9taXVtIFBERiBWaWV3ZXIsTWljcm9zb2Z0IEVkZ2UgUERGIFZpZXdlcixXZWJLaXQgYnVpbHQtaW4gUERGIiwiY2FudmFzX2NvZGUiOiI2NjAzODQzMyIsIndlYmdsX3ZlbmRvciI6Ikdvb2dsZSBJbmMuIChOVklESUEpIiwid2ViZ2xfcmVuZGVyZXIiOiJBTkdMRSAoTlZJRElBLCBOVklESUEgR2VGb3JjZSBSVFggMzA3MCAoMHgwMDAwMjQ4OCkgRGlyZWN0M0QxMSB2c181XzAgcHNfNV8wLCBEM0QxMSkiLCJhdWRpbyI6IjEyNC4wNDM0NzUyNzUxNjA3NCIsInBsYXRmb3JtIjoiV2luMzIiLCJ3ZWJfdGltZXpvbmUiOiJBc2lhL1NoYW5naGFpIiwiZGV2aWNlX25hbWUiOiJDaHJvbWUgVjE0MC4wLjAuMCAoV2luZG93cykiLCJmaW5nZXJwcmludCI6ImI0NzNmZjVhODA0ODU4YWQ2ZmYxYTdhNmQ2YzY0NjIzIiwiZGV2aWNlX2lkIjoiIiwicmVsYXRlZF9kZXZpY2VfaWRzIjoiIn0=',
                'fvideo-id': '33ea495bf3a5a79b884c5845faf9ca5e77e32ab5',
                'lang': 'zh-CN',
                'Priority': 'u=1, i',
                'Referer': 'https://www.binance.com/zh-CN/alpha/bsc/0xe6df05ce8c8301223373cf5b969afcb1498c5528',
                'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'Sentry-Trace': '847f639347bc49be967b6777b03a413c-ac242fc8bf0e51e2-0',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
                'X-Passthrough-Token': '',
                'X-Trace-Id': '000f2190-8b35-4cb1-aa27-d62a5017a918',
                'X-Ui-Request-Trace': '000f2190-8b35-4cb1-aa27-d62a5017a918'
            }
            
            # 计算数量
            base_amount = 1025
            working_quantity = base_amount / price
            working_quantity_formatted = int(working_quantity * 10000) / 10000  # 截断到4位小数
            
            # 计算支付金额
            if side == "BUY":
                payment_amount = working_quantity_formatted * price
                payment_amount_formatted = int(payment_amount * 100000000) / 100000000  # 截断到8位小数
                payment_wallet_type = "CARD"
            else:  # SELL
                # 卖单动态计算手续费（0.01%），避免余额不足
                fee_rate = 0.0001  # 0.01%
                fee_amount = working_quantity_formatted * fee_rate
                working_quantity_formatted = max(0, working_quantity_formatted - fee_amount)
                working_quantity_formatted = int(working_quantity_formatted * 10000) / 10000  # 截断到4位小数
                payment_amount_formatted = working_quantity_formatted
                payment_wallet_type = "ALPHA"
            
            # 构建请求数据
            payload = {
                "baseAsset": symbol.replace('USDT', ''),
                "quoteAsset": "USDT",
                "side": side,
                "price": price,
                "quantity": working_quantity_formatted,
                "paymentDetails": [{"amount": str(payment_amount_formatted), "paymentWalletType": payment_wallet_type}]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '000000' and 'data' in data:
                    return data['data']  # 直接返回订单ID
                else:
                    # 打印错误信息
                    error_code = data.get('code', 'unknown')
                    error_message = data.get('message', '未知错误')
                    self.log_message(f"{side}单下单失败 - 错误代码: {error_code}, 错误信息: {error_message}")
                    return None
            else:
                self.log_message(f"{side}单下单请求失败 - HTTP状态码: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_message(f"{side}单下单异常: {str(e)}")
            return None
    
    def cancel_all_orders(self):
        """取消所有委托"""
        try:
            if not self.csrf_token or not self.cookie:
                self.log_message("请先设置认证信息")
                return False
                
            url = "https://www.binance.com/bapi/defi/v1/private/alpha-trade/order/cancel-all"
            payload = {}
            
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Baggage': 'sentry-environment=prod,sentry-release=20250924-d1d0004c-2900,sentry-public_key=9445af76b2ba747e7b574485f2c998f7,sentry-trace_id=847f639347bc49be967b6777b03a413c,sentry-sample_rate=0.01,sentry-transaction=%2Falpha%2F%24chainSymbol%2F%24contractAddress,sentry-sampled=false',
                'Bnc-Uuid': 'e420e928-1b68-4ea2-991d-016cf1dc6f8b',
                'Clienttype': 'web',
                'Content-Type': 'application/json',
                'Cookie': self.cookie,
                'csrftoken': self.csrf_token,
                'device-info': 'eyJzY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsImF2YWlsYWJsZV9zY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsInN5c3RlbV92ZXJzaW9uIjoiV2luZG93cyAxMCIsImJyYW5kX21vZGVsIjoidW5rbm93biIsInN5c3RlbV9sYW5nIjoiemgtQ04iLCJ0aW1lem9uZSI6IkdNVCswODowMCIsInRpbWV6b25lT2Zmc2V0IjotNDgwLCJ1c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0MC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwibGlzdF9wbHVnaW4iOiJQREYgVmlld2VyLENocm9tZSBQREYgVmlld2VyLENocm9taXVtIFBERiBWaWV3ZXIsTWljcm9zb2Z0IEVkZ2UgUERGIFZpZXdlcixXZWJLaXQgYnVpbHQtaW4gUERGIiwiY2FudmFzX2NvZGUiOiI2NjAzODQyMyIsIndlYmdsX3ZlbmRvciI6Ikdvb2dsZSBJbmMuIChOVklESUEpIiwid2ViZ2xfcmVuZGVyZXIiOiJBTkdMRSAoTlZJRElBLCBOVklESUEgR2VGb3JjZSBSVFggMzA3MCAoMHgwMDAwMjQ4OCkgRGlyZWN0M0QxMSB2c181XzAgcHNfNV8wLCBEM0QxMSkiLCJhdWRpbyI6IjEyNC4wNDM0NzUyNzUxNjA3NCIsInBsYXRmb3JtIjoiV2luMzIiLCJ3ZWJfdGltZXpvbmUiOiJBc2lhL1NoYW5naGFpIiwiZGV2aWNlX25hbWUiOiJDaHJvbWUgVjE0MC4wLjAuMCAoV2luZG93cykiLCJmaW5nZXJwcmludCI6ImI0NzNmZjVhODA0ODU4YWQ2ZmYxYTdhNmQ2YzY0NjIzIiwiZGV2aWNlX2lkIjoiIiwicmVsYXRlZF9kZXZpY2VfaWRzIjoiIn0=',
                'fvideo-id': '33ea495bf3a5a79b884c5845faf9ca5e77e32ab5',
                'lang': 'zh-CN',
                'Priority': 'u=1, i',
                'Referer': 'https://www.binance.com/zh-CN/alpha/bsc/0xe6df05ce8c8301223373cf5b969afcb1498c5528',
                'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'Sentry-Trace': '847f639347bc49be967b6777b03a413c-ac242fc8bf0e51e2-0',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
                'X-Passthrough-Token': '',
                'X-Trace-Id': '000f2190-8b35-4cb1-aa27-d62a5017a918',
                'X-Ui-Request-Trace': '000f2190-8b35-4cb1-aa27-d62a5017a918'
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '000000' and data.get('success') == True:
                    self.log_message("取消所有委托成功")
                    return True
                else:
                    self.log_message(f"取消委托失败 - 错误代码: {data.get('code')}, 错误信息: {data.get('message')}")
                    return False
            else:
                self.log_message(f"取消委托请求失败 - HTTP状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_message(f"取消委托异常: {str(e)}")
            return False

    def check_single_order_filled(self, order_id):
        """检查单个订单是否已成交"""
        try:
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
                'orderStatus': 'FILLED',
                'startTime': start_time,
                'endTime': end_time
            }
            
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Bnc-Level': '0',
                'Bnc-Location': 'CN',
                'Bnc-Time-Zone': 'Asia/Shanghai',
                'Bnc-Uuid': 'e420e928-1b68-4ea2-991d-016cf1dc6f8b',
                'Clienttype': 'web',
                'Content-Type': 'application/json',
                'Cookie': self.cookie,
                'csrftoken': self.csrf_token,
                'device-info': 'eyJzY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsImF2YWlsYWJsZV9zY3JlZW5fcmVzb2x1dGlvbiI6IjI1NjAsMTQ0MCIsInN5c3RlbV92ZXJzaW9uIjoiV2luZG93cyAxMCIsImJyYW5kX21vZGVsIjoidW5rbm93biIsInN5c3RlbV9sYW5nIjoiemgtQ04iLCJ0aW1lem9uZSI6IkdNVCswODowMCIsInRpbWV6b25lT2Zmc2V0IjotNDgwLCJ1c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0MC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwibGlzdF9wbHVnaW4iOiJQREYgVmlld2VyLENocm9tZSBQREYgVmlld2VyLENocm9taXVtIFBERiBWaWV3ZXIsTWljcm9zb2Z0IEVkZ2UgUERGIFZpZXdlcixXZWJLaXQgYnVpbHQtaW4gUERGIiwiY2FudmFzX2NvZGUiOiI2NjAzODQyMyIsIndlYmdsX3ZlbmRvciI6Ikdvb2dsZSBJbmMuIChOVklESUEpIiwid2ViZ2xfcmVuZGVyZXIiOiJBTkdMRSAoTlZJRElBLCBOVklESUEgR2VGb3JjZSBSVFggMzA3MCAoMHgwMDAwMjQ4OCkgRGlyZWN0M0QxMSB2c181XzAgcHNfNV8wLCBEM0QxMSkiLCJhdWRpbyI6IjEyNC4wNDM0NzUyNzUxNjA3NCIsInBsYXRmb3JtIjoiV2luMzIiLCJ3ZWJfdGltZXpvbmUiOiJBc2lhL1NoYW5naGFpIiwiZGV2aWNlX25hbWUiOiJDaHJvbWUgVjE0MC4wLjAuMCAoV2luZG93cykiLCJmaW5nZXJwcmludCI6ImI0NzNmZjVhODA0ODU4YWQ2ZmYxYTdhNmQ2YzY0NjIzIiwiZGV2aWNlX2lkIjoiIiwicmVsYXRlZF9kZXZpY2VfaWRzIjoiIn0=',
                'fvideo-id': '33ea495bf3a5a79b884c5845faf9ca5e77e32ab5',
                'fvideo-token': 'r4R1qH50iUiBSvkPxnk29hGEzOdVdsdK1PoVlT6ffvZ/MjoWsgdF2PVAMzhjjqaaYN8uQUjZfwbLIYLnvjaK+0JsjNR4eNpSUmddjCkrKVAbcD6VKcogkjBEGbgOoQrBIbaKP1/QYanSSqlXpTal5hQExJnFU0EwVWLUSs0Zr8PYXnzgfSaRTxbPy91QYSeYo=3b',
                'If-None-Match': 'W/"0fc5ed125198498515f07cb35f0655bb7"',
                'lang': 'zh-CN',
                'Priority': 'u=1, i',
                'Referer': 'https://www.binance.com/zh-CN/my/wallet/alpha',
                'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
                'X-Passthrough-Token': '',
                'X-Trace-Id': '14b00354-0504-4a31-a7c9-6206fcbda5cb',
                'X-Ui-Request-Trace': '14b00354-0504-4a31-a7c9-6206fcbda5cb'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '000000' and 'data' in data:
                    orders = data['data']
                    if orders and len(orders) > 0:
                        # 检查最新订单是否匹配
                        latest_order = orders[0]
                        if str(latest_order.get('orderId')) == str(order_id):
                            # 打印成交额信息
                            cum_quote = latest_order.get('cumQuote', '0')
                            side = latest_order.get('side', '')
                            
                            # 根据订单方向格式化成交额
                            if side == 'SELL':
                                # 卖单截取两位小数
                                formatted_amount = f"{float(cum_quote):.2f}"
                            else:
                                # 买单保持原精度
                                formatted_amount = cum_quote
                            
                            self.log_message(f"订单 {order_id} 成交，成交额: {formatted_amount} USDT")
                            return True
                return False
            else:
                self.log_message(f"查询订单历史失败 - HTTP状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_message(f"查询订单历史异常: {str(e)}")
            return False

    def check_orders_filled(self, buy_order_id, sell_order_id):
        """检查订单是否已成交"""
        try:
            # 获取今天和明天的时间戳
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow_start = today_start + timedelta(days=1)
            
            start_time = int(today_start.timestamp() * 1000)
            end_time = int(tomorrow_start.timestamp() * 1000)
            
            url = "https://www.binance.com/bapi/defi/v1/private/alpha-trade/order/get-order-history-web"
            params = {
                'page': 1,
                'rows': 50,
                'orderStatus': 'FILLED',
                'startTime': start_time,
                'endTime': end_time
            }
            
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Content-Type': 'application/json',
                'csrftoken': self.csrf_token,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '000000' and 'data' in data:
                    orders = data['data']
                    buy_filled = any(order.get('orderId') == buy_order_id for order in orders)
                    sell_filled = any(order.get('orderId') == sell_order_id for order in orders)
                    return buy_filled and sell_filled
            
            return False
        except Exception as e:
            self.log_message(f"查询订单状态失败: {str(e)}")
            return False
    
    def update_trade_amount(self, symbol, price):
        """更新成交额"""
        try:
            # 每次交易固定增加1025 USDT
            current_amount = self.tokens[symbol].get('trade_amount', 0.0)
            new_amount = current_amount + 1025.0
            
            self.tokens[symbol]['trade_amount'] = new_amount
            self.root.after(0, self.update_tree_view)
            
            display_name = self.tokens[symbol].get('display_name', symbol)
            self.log_message(f"{display_name} 成交额更新: {current_amount:.2f} -> {new_amount:.2f} USDT")
        except Exception as e:
            self.log_message(f"更新成交额失败: {str(e)}")

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
