#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: options.py
# @Time: 31/01/2025 21:02
# @Author: Amundsen Severus Rubeus Bjaaland


# 导入标准库
import os
import threading


# Windows 路径中所有非法字符及其替代方案
_ILLEGAL_CHARS = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
_ILLEGAL_CHARS_REP = ['＜', '＞', '：', '＂', '／', '＼', '｜', '？', '＊']


def singleton(cls):
    """单例模式装饰器
    
    该单例模式装饰器是线程安全的.
    
    :param cls: 类
    :type cls: class
    :return: 类的实例
    """
    # 用于存储类的实例
    instances = {}
    # 创建锁对象
    lock = threading.Lock()
    
    def wrapper(*args, **kwargs):
        """装饰器函数"""
        # 将 instances 声明为外部变量
        nonlocal instances
		# 检查类是否在实例缓存区中
        if cls not in instances:
			# 加锁
            with lock:
                # 双重检查锁定, 检查类是否在实例缓存区中
                if cls not in instances:
                    # 如果类不在实例缓存区中, 则创建类的实例
                    instances[cls] = cls(*args, **kwargs)
        # 返回类的实例
        return instances[cls]
    
    # 返回装饰器函数
    return wrapper

def mkdir(path: str) -> None:
    """创建文件夹，若文件夹已存在则不进行任何操作
    
    :param path: 要创建的文件的路径
    """
    # 确保 path 是 str 类型
    assert isinstance(path, str)
    # 创建文件夹
    try:
        os.makedirs(path)
    except FileExistsError:
        pass


def sanitize_filename(text: str) -> str:
	"""替换非法字符
	
	:param text: 将要检查的字符串
	:type text: str
	
	Example:
		>>> sanitize_filename("测试字符串")
	"""
	# 检查每一个非法字符的存在情况, 如果存在则替换掉
	for char, char_rep in zip(_ILLEGAL_CHARS, _ILLEGAL_CHARS_REP):
		text = text.replace(char, char_rep)
	# 返回替换以后的字符串
	return text
