#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建程序图标
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    def create_icon():
        """创建程序图标"""
        # 创建64x64的图像
        size = 64
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制圆形背景
        draw.ellipse([4, 4, size-4, size-4], fill=(52, 152, 219, 255), outline=(41, 128, 185, 255), width=2)
        
        # 绘制币安风格的B字母
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("arial.ttf", 32)
        except:
            # 使用默认字体
            font = ImageFont.load_default()
        
        # 绘制B字母
        text = "B"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - 2
        
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        
        # 保存为ICO文件
        img.save('icon.ico', format='ICO', sizes=[(64, 64), (32, 32), (16, 16)])
        print("✓ 图标文件创建成功: icon.ico")
        return True
        
    except ImportError:
        print("PIL库未安装，跳过图标创建")
        print("如需创建图标，请运行: pip install Pillow")
        return False
    except Exception as e:
        print(f"创建图标失败: {e}")
        return False

if __name__ == "__main__":
    create_icon()
