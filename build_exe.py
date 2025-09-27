#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包成exe文件的脚本
使用PyInstaller将币安量化交易系统打包成可执行文件
"""

import os
import sys
import subprocess

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ PyInstaller安装失败: {e}")
        return False

def build_exe():
    """构建exe文件"""
    print("开始构建exe文件...")
    
    # PyInstaller命令参数
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成单个exe文件
        "--windowed",                   # 不显示控制台窗口
        "--name=BinanceAutoTrade",      # exe文件名
        "--icon=icon.ico",              # 图标文件（如果存在）
        "--add-data=requirements.txt;.", # 包含requirements.txt
        "binance_trader.py"             # 主程序文件
    ]
    
    # 如果没有图标文件，移除图标参数
    if not os.path.exists("icon.ico"):
        cmd.remove("--icon=icon.ico")
    
    try:
        subprocess.check_call(cmd)
        print("✓ exe文件构建成功！")
        print("可执行文件位置: dist/BinanceAutoTrade.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ exe文件构建失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("币安量化交易系统 - exe打包工具")
    print("=" * 50)
    
    # 检查主程序文件是否存在
    if not os.path.exists("binance_trader.py"):
        print("✗ 找不到主程序文件 binance_trader.py")
        return
    
    # 安装PyInstaller
    if not install_pyinstaller():
        return
    
    # 构建exe文件
    if build_exe():
        print("\n" + "=" * 50)
        print("打包完成！")
        print("可执行文件: dist/BinanceAutoTrade.exe")
        print("您可以将整个dist文件夹分发给其他用户")
        print("=" * 50)
    else:
        print("\n打包失败，请检查错误信息")

if __name__ == "__main__":
    main()
