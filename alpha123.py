#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alpha123稳定度数据模块
Alpha123 Stability Data Module for Binance Auto Trade System
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logger import Logger


class Alpha123Client:
    """Alpha123客户端类 - 负责获取稳定度看板数据"""
    
    def __init__(self, logger=None, alpha_id_map=None):
        """
        初始化Alpha123客户端
        
        Args:
            logger: Logger实例，用于记录日志
            alpha_id_map: ALPHA代币ID映射字典
        """
        self.logger = logger or Logger()
        self.alpha_id_map = alpha_id_map or {}
    
    def set_alpha_id_map(self, alpha_id_map):
        """
        设置ALPHA代币ID映射
        
        Args:
            alpha_id_map: ALPHA代币ID映射字典
        """
        self.alpha_id_map = alpha_id_map
    
    def fetch_stability_data(self):
        """
        获取稳定度看板数据（尝试多种方式）
        
        Returns:
            list: 稳定度数据列表，失败返回空列表
        """
        try:
            # 首先尝试模拟浏览器请求
            return self.fetch_stability_data_requests()
        except Exception as e:
            self.logger.log_message(f"模拟请求失败，尝试Selenium: {str(e)}")
            try:
                return self.fetch_stability_data_selenium()
            except Exception as e2:
                self.logger.log_message(f"Selenium也失败，尝试API: {str(e2)}")
                return self.fetch_stability_data_api()
    
    def fetch_stability_data_requests(self):
        """
        使用requests直接调用API获取稳定度数据
        
        Returns:
            list: 稳定度数据列表
        """
        try:
            # 直接调用API接口
            api_url = "https://alpha123.uk/stability/stability_feed_v2.json"
            
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
            
            # 根据新的JSON结构解析数据
            if isinstance(api_data, dict) and 'items' in api_data:
                items = api_data['items']
                self.logger.log_message(f"找到 {len(items)} 个项目")
                
                for item in items:
                    if isinstance(item, dict):
                        # 从n字段提取项目名称（去掉/USDT后缀）
                        project_name = item.get('n', '')
                        project = project_name.replace('/USDT', '') if project_name else ''
                        
                        # 获取最新价格
                        last_price = item.get('p', 0)
                        
                        # 获取稳定度状态
                        stability_text = item.get('st', 'unknown')
                        
                        # 转换稳定度为中文
                        stability_map = {
                            'green:stable': '稳定',
                            'yellow:general': '一般',
                            'yellow:moderate': '一般',
                            'red:unstable': '不稳定',
                            'stable': '稳定',
                            'unstable': '不稳定',
                            'general': '一般',
                            'moderate': '一般',
                            'unknown': '未知'
                        }
                        stability = stability_map.get(stability_text.lower(), '未知')
                        
                        # 获取4倍剩余天数
                        multiplier_days = item.get('md', 0)
                        
                        # 获取价差基点（越小越稳定）
                        spread = item.get('spr', 0)
                        
                        # 过滤条件：排除KOGE，且4倍天数必须大于0
                        if project.upper() == 'KOGE':
                            # KOGE始终添加（用于显示）
                            parsed_item = {
                                'project': project,
                                'stability': stability,
                                'stability_status': stability_text,  # 保存原始st值
                                'price': str(last_price),
                                'remaining_days': str(multiplier_days),
                                'spread': str(spread)
                            }
                            stability_data.append(parsed_item)
                        elif multiplier_days > 0:
                            # 其他代币：4倍天数必须大于0
                            parsed_item = {
                                'project': project,
                                'stability': stability,
                                'stability_status': stability_text,  # 保存原始st值
                                'price': str(last_price),
                                'remaining_days': str(multiplier_days),
                                'spread': str(spread)
                            }
                            stability_data.append(parsed_item)
            
            # 如果API返回的是数组格式（保持向后兼容）
            elif isinstance(api_data, list):
                for item in api_data:
                    if isinstance(item, dict):
                        # 检查是否为新格式
                        if 'n' in item and 'p' in item and 'st' in item:
                            # 新格式解析
                            project_name = item.get('n', '')
                            project = project_name.replace('/USDT', '') if project_name else ''
                            
                            last_price = item.get('p', 0)
                            stability_text = item.get('st', 'unknown')
                            
                            stability_map = {
                                'green:stable': '稳定',
                                'yellow:general': '一般',
                                'yellow:moderate': '一般',
                                'red:unstable': '不稳定',
                                'stable': '稳定',
                                'unstable': '不稳定',
                                'general': '一般',
                                'moderate': '一般',
                                'unknown': '未知'
                            }
                            stability = stability_map.get(stability_text.lower(), '未知')
                            
                            multiplier_days = item.get('md', 0)
                            spread = item.get('spr', 0)
                            
                            # 过滤条件：排除KOGE，且4倍天数必须大于0
                            if project.upper() == 'KOGE':
                                stability_data.append({
                                    'project': project,
                                    'stability': stability,
                                    'stability_status': stability_text,  # 保存原始st值
                                    'price': str(last_price),
                                    'remaining_days': str(multiplier_days),
                                    'spread': str(spread)
                                })
                            elif multiplier_days > 0:
                                stability_data.append({
                                    'project': project,
                                    'stability': stability,
                                    'stability_status': stability_text,  # 保存原始st值
                                    'price': str(last_price),
                                    'remaining_days': str(multiplier_days),
                                    'spread': str(spread)
                                })
                        else:
                            # 旧格式解析（向后兼容）
                            display = item.get('display', '')
                            project = display.replace('/USDT', '') if display else item.get('key', '')
                            
                            metrics = item.get('metrics', {})
                            last_price = metrics.get('lastPrice', 0)
                            
                            status = item.get('status', {})
                            status_text = status.get('text', 'unknown')
                            
                            stability_map = {
                                'stable': '稳定',
                                'unstable': '不稳定',
                                'general': '一般',
                                'moderate': '一般',
                                'unknown': '未知'
                            }
                            stability = stability_map.get(status_text.lower(), '未知')
                            
                            multiplier_days = item.get('multiplier_days', 0)
                            spread = item.get('spread', 999999)  # 旧格式可能没有spread字段
                            
                            # 过滤条件：排除KOGE，且4倍天数必须大于0
                            if project.upper() == 'KOGE':
                                stability_data.append({
                                    'project': project,
                                    'stability': stability,
                                    'stability_status': status_text,  # 保存原始status值
                                    'price': str(last_price),
                                    'remaining_days': str(multiplier_days),
                                    'spread': str(spread)
                                })
                            elif multiplier_days > 0:
                                stability_data.append({
                                    'project': project,
                                    'stability': stability,
                                    'stability_status': status_text,  # 保存原始status值
                                    'price': str(last_price),
                                    'remaining_days': str(multiplier_days),
                                    'spread': str(spread)
                                })
            
            # 对数据进行排序：KOGE固定排第一位，其他按价差基点（spr）升序排序
            def sort_key(item):
                project = item['project']
                spread_str = item.get('spread', '999999')
                
                # KOGE固定排第一位
                if project.upper() == 'KOGE':
                    return (0, 0)
                
                # 其他按价差基点排序：spr越小越稳定，排在前面
                try:
                    spread = float(spread_str)
                except (ValueError, TypeError):
                    spread = 999999  # 如果无法转换，设为一个很大的值排在后面
                
                return (1, spread)
            
            stability_data.sort(key=sort_key)
            
            self.logger.log_message(f"从API获取到 {len(stability_data)} 个稳定度项目")
            return stability_data
            
        except Exception as e:
            self.logger.log_message(f"API调用失败: {str(e)}")
            # 不使用备用数据，返回空列表
            return []
    
    def fetch_stability_data_selenium(self):
        """
        使用Selenium获取稳定度数据
        
        Returns:
            list: 稳定度数据列表
        """
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
                self.logger.log_message("等待数据加载超时")
            
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
            
            self.logger.log_message(f"通过Selenium获取了 {len(stability_data)} 个稳定度项目")
            return stability_data
            
        except Exception as e:
            self.logger.log_message(f"Selenium获取稳定度数据失败: {str(e)}")
            return []
        finally:
            if driver:
                driver.quit()
    
    def fetch_stability_data_api(self):
        """
        尝试通过API获取稳定度数据
        
        Returns:
            list: 稳定度数据列表
        """
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
                        self.logger.log_message(f"通过API获取了 {len(stability_data)} 个稳定度项目")
                        return stability_data
                except:
                    continue
            
            # 如果API都失败，返回空数据
            self.logger.log_message("所有API接口都无法访问")
            return []
            
        except Exception as e:
            self.logger.log_message(f"API获取稳定度数据失败: {str(e)}")
            return []
    
    def get_top_stability_token(self):
        """
        获取除KOGE外价差基点最小的代币（最稳定）
        
        过滤条件：
        - 排除KOGE
        - 4倍天数(md)必须大于0
        - 稳定度状态(st)必须为 "green:stable"
        - 价差基点(spr)必须 < 1
        - 按价差基点(spr)升序排序，取最小值
        
        Returns:
            dict: 代币信息字典，包含symbol、display_name、price、stability、spread，失败返回None
        """
        try:
            stability_data = self.fetch_stability_data()
            if not stability_data:
                self.logger.log_message("未获取到稳定度数据")
                return None
            
            # 数据已经按spr排序（越小越稳定），过滤掉KOGE，找到第一个符合条件的代币
            for item in stability_data:
                project = item.get('project', '')
                if project and project.upper() != 'KOGE':
                    # 获取稳定度状态
                    stability_status = item.get('stability_status', '').lower()
                    
                    # 条件1：st必须为 green:stable
                    if stability_status != 'green:stable':
                        self.logger.log_message(f"代币 {project} 稳定度状态 {stability_status} != green:stable，不符合条件")
                        continue
                    
                    # 获取价差基点
                    spread_str = item.get('spread', 'N/A')
                    
                    # 条件2：spr必须 < 1
                    try:
                        spread_value = float(spread_str)
                    except (ValueError, TypeError):
                        self.logger.log_message(f"代币 {project} 价差基点无效: {spread_str}")
                        continue
                    
                    if spread_value >= 1:
                        self.logger.log_message(f"代币 {project} 价差基点 {spread_value} >= 1，不符合稳定条件")
                        continue
                    
                    # 两个条件都满足，检查alpha_id
                    alpha_id = self.alpha_id_map.get(project)
                    if alpha_id:
                        # 安全解析价格
                        try:
                            price_value = item.get('price', 0)
                            price = float(price_value) if price_value else 0.0
                        except (ValueError, TypeError):
                            price = 0.0
                        
                        # 获取稳定度信息（用于显示）
                        stability_info = item.get('stability', '未知')
                        
                        self.logger.log_message(f"[OK] 选中最稳定代币: {project}, st={stability_status}, spr={spread_value}<1")
                        
                        return {
                            'symbol': f"{alpha_id}USDT",
                            'display_name': project,
                            'price': price,
                            'stability': stability_info,
                            'spread': spread_str
                        }
            
            self.logger.log_message("没有找到符合条件的稳定代币（st=green:stable 且 spr<1）")
            return None
            
        except Exception as e:
            self.logger.log_message(f"获取最稳定代币失败: {str(e)}")
            return None


# 创建全局Alpha123客户端实例（可选）
_global_alpha123_client = None


def get_alpha123_client(logger=None, alpha_id_map=None):
    """
    获取全局Alpha123客户端实例（单例模式）
    
    Args:
        logger: Logger实例
        alpha_id_map: ALPHA代币ID映射字典
        
    Returns:
        Alpha123Client: Alpha123客户端实例
    """
    global _global_alpha123_client
    if _global_alpha123_client is None:
        _global_alpha123_client = Alpha123Client(logger, alpha_id_map)
    return _global_alpha123_client


def set_global_alpha123_client(client):
    """
    设置全局Alpha123客户端实例
    
    Args:
        client: Alpha123Client实例
    """
    global _global_alpha123_client
    _global_alpha123_client = client

