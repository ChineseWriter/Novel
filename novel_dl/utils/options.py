#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: options.py
# @Time: 31/01/2025 21:02
# @Author: Amundsen Severus Rubeus Bjaaland


# 导入标准库
import os
import threading


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
