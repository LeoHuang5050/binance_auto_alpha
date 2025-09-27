#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取当前电脑的MAC地址哈希值
用于配置软件权限
"""

import uuid
import hashlib

def get_mac_address():
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

def get_mac_hash():
    """获取MAC地址的MD5哈希值"""
    mac = get_mac_address()
    if mac:
        return hashlib.md5(mac.encode()).hexdigest()
    return None

def main():
    """主函数"""
    print("=" * 50)
    print("MAC地址权限配置工具")
    print("=" * 50)
    
    mac_address = get_mac_address()
    mac_hash = get_mac_hash()
    
    if mac_address and mac_hash:
        print(f"当前电脑MAC地址: {mac_address}")
        print(f"MAC地址哈希值: {mac_hash}")
        print("\n请将以下哈希值添加到 binance_trader.py 的 allowed_mac_hashes 列表中:")
        print(f'"{mac_hash}",')
    else:
        print("❌ 无法获取MAC地址信息")

if __name__ == "__main__":
    main()
