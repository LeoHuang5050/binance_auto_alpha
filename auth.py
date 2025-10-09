#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证管理模块
Authentication Module for Binance Auto Trade System
"""

import sys
import uuid
import hashlib
import tkinter as tk


class AuthManager:
    """认证管理类 - 负责MAC地址校验等权限验证"""
    
    def __init__(self, allowed_mac_hashes=None):
        """
        初始化认证管理器
        
        Args:
            allowed_mac_hashes: 允许的MAC地址哈希值列表
        """
        # 默认允许的MAC地址哈希值列表
        self.allowed_mac_hashes = allowed_mac_hashes or [
            "3a36b385f3a6953d8c732bea92e3ca2a",  # 当前电脑的MAC地址哈希
            "188a66fe2f45fb0dc42d8b67d9abdc3a",  # 新增MAC地址1
            "c99cfed938c7e379ed5f73cb2f14ad61",  # 新增MAC地址2
            "68c3110ad7fc78479caf1442f11faf84",  # 新增MAC地址3
            # 可以添加更多允许的MAC地址哈希值
        ]
    
    def add_allowed_mac_hash(self, mac_hash):
        """
        添加允许的MAC地址哈希值
        
        Args:
            mac_hash: MAC地址的MD5哈希值
        """
        if mac_hash not in self.allowed_mac_hashes:
            self.allowed_mac_hashes.append(mac_hash)
    
    def remove_allowed_mac_hash(self, mac_hash):
        """
        移除允许的MAC地址哈希值
        
        Args:
            mac_hash: MAC地址的MD5哈希值
        """
        if mac_hash in self.allowed_mac_hashes:
            self.allowed_mac_hashes.remove(mac_hash)
    
    def get_mac_address(self):
        """
        获取当前电脑的MAC地址
        
        Returns:
            str: MAC地址字符串（格式：XX:XX:XX:XX:XX:XX），失败返回None
        """
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
        """
        获取MAC地址的MD5哈希值
        
        Returns:
            str: MAC地址的MD5哈希值，失败返回None
        """
        mac = self.get_mac_address()
        if mac:
            return hashlib.md5(mac.encode()).hexdigest()
        return None
    
    def check_mac_permission(self):
        """
        检查MAC地址权限
        
        Returns:
            bool: 权限验证通过返回True，否则返回False
        """
        current_mac_hash = self.get_mac_hash()
        if not current_mac_hash:
            self.show_permission_error("无法获取设备信息")
            return False
        
        if current_mac_hash not in self.allowed_mac_hashes:
            self.show_permission_error(f"设备未授权\n当前设备哈希: {current_mac_hash}")
            return False
        
        print(f"MAC地址校验通过: {current_mac_hash}")
        return True
    
    def show_permission_error(self, message):
        """
        显示权限错误对话框
        
        Args:
            message: 错误信息
        """
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
        
        # 运行对话框
        error_dialog.mainloop()


# 创建全局认证实例（可选）
_global_auth = None


def get_auth_manager(allowed_mac_hashes=None):
    """
    获取全局认证管理器实例（单例模式）
    
    Args:
        allowed_mac_hashes: 允许的MAC地址哈希值列表
        
    Returns:
        AuthManager: 认证管理器实例
    """
    global _global_auth
    if _global_auth is None:
        _global_auth = AuthManager(allowed_mac_hashes)
    return _global_auth


def set_global_auth_manager(auth_manager):
    """
    设置全局认证管理器实例
    
    Args:
        auth_manager: AuthManager实例
    """
    global _global_auth
    _global_auth = auth_manager

