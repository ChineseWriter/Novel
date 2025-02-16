#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: settings.py
# @Time: 30/01/2025 19:48
# @Author: Amundsen Severus Rubeus Bjaaland


# 导入标准库
import os
from typing import Literal

# 导入自定义库
from novel_dl.utils.options import singleton


@singleton
class Settings(object):
    def __init__(self):
        """模块的全局设置
        
        该类用于存储该模块的设置信息. 所有的设置项以及说明如下:
        1. DEBUG: 是否开启调试模式, 默认为 False.
        2. TIME_FORMAT: 时间格式, 默认为 "%Y-%m-%d %H:%M:%S".
        3. DATA_DIR: 数据目录, 默认为 "data".
        4. MULTI_THREAD: 是否开启多线程, 默认为 True.
        5. FORCE_RELOAD: 是否强制重新下载, 默认为 False.
        6. LOG_DIR: 日志目录, 默认为 "data/logs".
        7. LOG_MAX_FILE_NUMBER: 日志文件最大数量, 默认为 30.
        8. LOG_FORMAT: 日志格式, 默认为 "\[%(asctime)s\]\(%(levelname\)s)%(filename)s-%(lineno)s, in %(funcName)s:\\n\\t%(message)s".
        9. URLS_DIR: URL 目录, 默认为 "data/urls".
        10. BOOKS_DIR: 书籍目录, 默认为 "data/books".
        11. BOOKS_CACHE_DIR: 书籍缓存目录, 默认为 "data/books/cache".
        12. BOOKS_DB_PATH: 书籍数据库路径, 默认为 "data/books/bookshelf.db".
        13. BOOKS_STORAGE_DIR: 书籍存储目录, 默认为 "data/books/storage".
        
        TODO 添加新的设置项时应当:
        1. 在初始化函数中添加默认值.
        2. 在类属性中添加 getter 和 setter 方法.
        3. 在类初始化方法的说明中添加新的设置项说明
        """
        self.__debug: Literal[True, False] = False
        
        self.__time_format: str = "%Y-%m-%d %H:%M:%S"
        
        self.__multi_thread: Literal[True, False] = True
        self.__force_reload: Literal[True, False] = False
        
        self.__log_dir: str = os.path.join(self.__data_dir, "logs")
        self.__log_max_file_number: int = 30
        self.__log_format: str = "[%(asctime)s](%(levelname)s)" \
            "%(filename)s-%(lineno)s, in %(funcName)s:\n\t%(message)s"
        
        self.__data_dir: str = os.path.abspath("data")
        self.__urls_dir: str = os.path.join(self.__data_dir, "urls")
        self.__books_dir: str = os.path.join(self.__data_dir, "books")
        self.__books_cache_dir: str = os.path.join(
            self.__books_dir, "cache"
        )
        self.__books_db_path: str = os.path.join(
            self.__books_dir, "bookshelf.db"
        )
        self.__books_storage_dir: str = os.path.join(
            self.__books_dir, "storage"
        )
    
    @property
    def DEBUG(self) -> bool:
        """是否开启调试模式"""
        return self.__debug
    
    @DEBUG.setter
    def DEBUG(self, value: bool):
        """设置是否开启调试模式"""
        # 确保 value 是 bool 类型
        assert isinstance(value, bool)
        self.__debug = value
    
    @property
    def TIME_FORMAT(self) -> str:
        """时间格式"""
        return self.__time_format
    
    @TIME_FORMAT.setter
    def TIME_FORMAT(self, value: str):
        """设置时间格式"""
        # 确保 value 是 str 类型
        assert isinstance(value, str)
        self.__time_format = value
    
    @property
    def DATA_DIR(self) -> str:
        """数据目录"""
        return self.__data_dir
    
    @DATA_DIR.setter
    def DATA_DIR(self, value: str):
        """设置数据目录"""
        # 确保 value 是 str 类型
        assert isinstance(value, str)
        self.__data_dir = value
        
        self.__log_dir = os.path.join(self.__data_dir, "logs")
        self.__urls_dir = os.path.join(self.__data_dir, "urls")
        self.__books_dir = os.path.join(self.__data_dir, "books")
        self.__books_cache_dir = os.path.join(
            self.__books_dir, "cache"
        )
        self.__books_db_path = os.path.join(
            self.__books_dir, "bookshelf.db"
        )
        self.__books_storage_dir = os.path.join(
            self.__books_dir, "storage"
        )    
    
    @property
    def MULTI_THREAD(self) -> bool:
        """是否开启多线程"""
        return self.__multi_thread
    
    @MULTI_THREAD.setter
    def MULTI_THREAD(self, value: bool):
        """设置是否开启多线程"""
        # 确保 value 是 bool 类型
        assert isinstance(value, bool)
        self.__multi_thread = value
    
    @property
    def FORCE_RELOAD(self) -> bool:
        """是否强制重新下载"""
        return self.__force_reload
    
    @FORCE_RELOAD.setter
    def FORCE_RELOAD(self, value: bool):
        """设置是否强制重新下载"""
        # 确保 value 是 bool 类型
        assert isinstance(value, bool)
        self.__force_reload = value
    
    @property
    def LOG_DIR(self) -> str:
        """日志目录"""
        return self.__log_dir
    
    @property
    def LOG_MAX_FILE_NUMBER(self) -> int:
        """日志文件最大数量"""
        return self.__log_max_file_number
    
    @LOG_MAX_FILE_NUMBER.setter
    def LOG_MAX_FILE_NUMBER(self, value: int):
        """设置日志文件最大数量"""
        # 确保 value 是 int 类型
        assert isinstance(value, int)
        self.__log_max_file_number = value
    
    @property
    def LOG_FORMAT(self) -> str:
        """日志格式"""
        return self.__log_format
    
    @LOG_FORMAT.setter
    def LOG_FORMAT(self, value: str):
        """设置日志格式"""
        # 确保 value 是 str 类型
        assert isinstance(value, str)
        self.__log_format = value
    
    @property
    def URLS_DIR(self) -> str:
        """URL 目录"""
        return self.__urls_dir
    
    @property
    def BOOKS_DIR(self) -> str:
        """书籍目录"""
        return self.__books_dir
    
    @property
    def BOOKS_CACHE_DIR(self) -> str:
        """书籍缓存目录"""
        return self.__books_cache_dir
    
    @property
    def BOOKS_DB_PATH(self) -> str:
        """书籍数据库路径"""
        return self.__books_db_path
    
    @property
    def BOOKS_STORAGE_DIR(self) -> str:
        """书籍存储目录"""
        return self.__books_storage_dir