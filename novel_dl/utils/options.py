#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: options.py
# @Time: 31/01/2025 21:02
# @Author: Amundsen Severus Rubeus Bjaaland


# 导入标准库
import io
import hashlib
import threading

# 导入 PIL 库
from PIL import Image


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


def hash(value: bytes | str, format: str = "BYTES") -> bytes | str:
    """计算 SHA256 哈希值
    可选的格式有 "BYTES" 和 "HEX"
    
    :param value: 要计算哈希值的字符串或字节
    :type value: bytes | str
    :param format: 返回的哈希值的格式, 默认为 "BYTES"
    :type format: str
    :return: SHA256 哈希值
    
    Example:
        >>> hash("测试字符串")
    """
    # 创建 SHA256 对象
    sha256 = hashlib.sha256()
    # 如果 value 是 str 类型, 则将其编码为字节
    if isinstance(value, str):
        value = value.encode("utf-8")
    # 更新哈希值
    sha256.update(value)
    # 根据 format 的值返回不同的格式
    match format:
        case "BYTES":
            return sha256.digest()
        case "HEX":
            return sha256.hexdigest().encode("utf-8")
        case _:
            return sha256.digest()


def convert_image(image: bytes, format: str = "JPEG") -> bytes:
    """将图像转换为指定格式
    
    :param image: 要转换的图像
    :type image: bytes
    :param format: 要转换的格式, 默认为 "JPEG"
    :type format: str
    :return: 转换后的图像
    
    Example:
        >>> convert_image(image)
    """
    # 创建 BytesIO 对象
    image = Image.open(io.BytesIO(image))
    # 创建 BytesIO 对象
    output = io.BytesIO()
    # 保存图像
    image.save(output, format=format)
    # 返回转换后的图像
    return output.getvalue()