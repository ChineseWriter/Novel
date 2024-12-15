#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: logs.py
# @Time: 02/11/2024 10:21
# @Author: Amundsen Severus Rubeus Bjaaland
"""为整个项目提供日志支持"""


# 导入标准库
import os
import copy
import logging
import threading
from typing import Dict, List

# 导入自定义库
from .settings import Settings

# 导入第三方库
import tqdm


def synchronized(func):
    func.__lock__ = threading.Lock()

    def lock_func(*args, **kwargs):
        with func.__lock__:
            return func(*args, **kwargs)

    return lock_func


class Singleton(object):
    __instance = None
    
    @synchronized
    def __new__(cls):
        if not cls.__instance:
            cls.__instance = super(Singleton, cls).__new__(cls)
        return cls.__instance


class TqdmHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            message = self.format(record)
            tqdm.write(message)
        except Exception:
            self.handleError(record)


class Logger(Singleton):
    def __init__(self):
        """整个包所使用的日志记录器"""
        # 获取标准库中的记录器
        self.__logger = logging.getLogger("novel_dl")
        # 设置日志记录器级别为DEBUG
        self.__logger.setLevel(logging.DEBUG if Settings.DEBUG else logging.WARNING)
        # 使子记录器的日志不向父记录器传递
        self.__logger.propagate = False
        # 设置日志记录的格式
        self.__formatter = logging.Formatter(Settings.LOG_FORMAT)
        
        # 创建处理器列表并初始化
        self.__handlers: Dict[str, logging.Handler] = {}
        self.__add_default_handlers()
        # 创建配置方案列表并初始化
        self.__scheme: Dict[str, List[str]] = {}
        self.add_scheme("default", ["stream_handler", "file_handler"])
        self.add_scheme("tqdm", ["tqdm_handler", "file_handler"])
        # 设置默认的配置方案
        self.__now_scheme: str = "default"
        self.set_scheme(self.__now_scheme)
    
    def __call__(self):
        return self.__logger
    
    def __add_default_handlers(self) -> Dict[str, logging.Handler]:
        # 创建命令行日志显示器
        stream_handler = logging.StreamHandler()
        # 设置命令行日志显示器的日志级别
        stream_handler.setLevel(logging.DEBUG if Settings.DEBUG else logging.INFO)
        # 设置日志处理器的日志格式
        stream_handler.setFormatter(self.__formatter)
        # 添加命令行日志处理器到日志处理器列表
        self.add_handler("stream_handler", stream_handler)
        
        # 创建日志文件写入器
        file_handler = logging.FileHandler(
              os.path.join(Settings.LOG_DIR, f"{Settings.LOG_FILE_NAME}.log"), encoding="UTF-8"
        )
        # 设置日志文件写入器的日志级别
        file_handler.setLevel(logging.WARNING)
        # 设置日志处理器的日志格式
        file_handler.setFormatter(self.__formatter)
        # 添加日志文件写入器到日志处理器列表
        self.add_handler("file_handler", file_handler)
        
        # 创建进度条日志显示器
        tqdm_handler = TqdmHandler()
        # 设置进度条日志显示器的日志级别
        tqdm_handler.setLevel(logging.DEBUG if Settings.DEBUG else logging.INFO)
        # 设置进度条日志显示器的日志格式
        tqdm_handler.setFormatter(self.__formatter)
        # 添加进度条日志显示器到日志处理器列表
        self.add_handler("tqdm_handler", tqdm_handler)
    
    def add_handler(self, name: str, handler: logging.Handler):
        assert isinstance(name, str)
        assert isinstance(handler, logging.Handler)
        self.__handlers["name"] = copy.deepcopy(handler)
    
    def add_scheme(self, name: str, scheme: List[str]):
        assert isinstance(name, str)
        for i in scheme:
            assert isinstance(i, str)
            assert i in self.__handlers()
        self.__scheme[name] = copy.deepcopy(scheme)
    
    def set_scheme(self, name: str):
        if name not in self.__scheme:
            return None
        for i in self.__scheme[self.__now_scheme]:
            self.__logger.removeHandler(self.__handlers[i])
        for i in self.__scheme[name]:
            self.__logger.addHandler(self.__handlers[i])
        self.__now_scheme = name
        return None
    
    @property
    def object(self):
        return self.__logger
        