#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: logs.py
# @Time: 02/11/2024 10:21
# @Author: Amundsen Severus Rubeus Bjaaland
"""为整个项目提供日志支持"""


# 导入标准库
import logging.handlers
import os
import copy
import logging
import threading
from typing import Dict, List

# 导入第三方库
from tqdm import tqdm

# 导入自定义库
from .tools import mkdir
from .settings import Settings


def singleton(cls):
    instances = {}
    lock = threading.Lock()
    
    def wrapper(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:  # 双重检查锁定
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return wrapper


class TqdmHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            message = self.format(record)
            tqdm.write(message)
        except Exception:
            self.handleError(record)


@singleton
class Logger(object):
    def __init__(self):
        """整个包所使用的日志记录器"""
        # 创建必要的目录
        mkdir(Settings.DATA_DIR)
        mkdir(Settings.LOG_DIR)
        # 获取标准库中的记录器
        self.__logger = logging.getLogger("novel_dl")
        # 设置日志记录器级别为DEBUG
        self.__logger.setLevel(logging.DEBUG)
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
    
    def __add_default_handlers(self):
        # 创建命令行日志显示器
        stream_handler = logging.StreamHandler()
        # 设置命令行日志显示器的日志级别
        stream_handler.setLevel(logging.DEBUG if Settings.DEBUG else logging.INFO)
        # 设置日志处理器的日志格式
        stream_handler.setFormatter(self.__formatter)
        # 添加命令行日志处理器到日志处理器列表
        self.add_handler("stream_handler", stream_handler)
        
        # 创建日志文件写入器
        file_handler = logging.handlers.TimedRotatingFileHandler(
			filename=os.path.join(Settings.LOG_DIR, "novel_dl_logs"),
   			when="MIDNIGHT", interval=1, encoding="UTF-8",
      		backupCount=Settings.LOG_MAX_FILE_NUMBER
		)
        # 设置文件后缀
        file_handler.suffix = "%Y-%m-%d.log"
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
        self.__handlers[name] = handler
    
    def add_scheme(self, name: str, scheme: List[str]):
        assert isinstance(name, str)
        for i in scheme:
            assert isinstance(i, str)
            assert i in self.__handlers
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
    
    @property
    def debug(self):
        return self.__logger.debug
    
    @property
    def info(self):
        return self.__logger.info
    
    @property
    def warning(self):
        return self.__logger.warning
    
    @property
    def error(self):
        return self.__logger.error
    
    @property
    def critical(self):
        return self.__logger.critical