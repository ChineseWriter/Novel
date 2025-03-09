#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: config.py
# @Time: 18/02/2025 18:01
# @Author: Amundsen Severus Rubeus Bjaaland


# 导入标准库
import time
import hashlib
from enum import Enum
from typing import List
from abc import ABCMeta, abstractmethod

# 导入自定义库
from novel_dl.utils.network import Network
from novel_dl.core.books import Book, Chapter, State


class Operations(Enum):
    """可选的操作类型常量"""
    INFO = (1, "获取书籍信息")
    URLS = (2, "获取书籍的所有章节 URL")
    CHAPTER = (3, "获取章节的信息及内容")
    
    @classmethod
    def to_obj(cls, value: int) -> "Operations":
        """将常量的ID转换为常量对象
        
        :param value: 常量的ID
        :type value: int
        :return: 常量对象
        
        Example:
            >>> State.to_obj(1)
        """
        # 确保 value 是 int类型
        assert isinstance(value, int)
        # 遍历所有常量
        for i in list(cls):
            # 如果常量的 ID 等于 value
            if i.value[0] == value:
                # 返回常量对象
                return i
        # 如果 value 的值不在常量中, 则返回 INFO 类型
        return cls.INFO
    
    def __int__(self):
        return self.value[0]
    
    def __str__(self):
        return self.value[1]


class BookWeb(metaclass=ABCMeta):
    """通用引擎模版, 一个基本的网站引擎应当包含这些信息"""
    # 网站的名字
    name: str = "默认网站"
    # 网站可能的网址列表
    domains: List[str] = ["www.example.com",]
    # 引擎是否可用
    workable: bool = True
    # 网站书籍 URL 的固定模式
    book_url_pattern: str = r"/book/\d+/"
    # 网站章节 URL 的固定模式
    chapter_url_pattern: str = r"/chapter/\d+/"
    # 网站所使用的编码
    encoding: str = "UTF-8"
    # 是否可以提前寻找网站内所有书籍
    prestore_book_urls: bool = False
    # 该网站是否支持多线程下载
    multi_thread: bool = True
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self):
        return f"<WebConfig name={self.name} encoding={self.encoding}>"
    
    def __hash__(self):
        text = self.name + "".join(self.domains)
        sha256_hash = hashlib.sha256(text.encode())
        hash_value = sha256_hash.hexdigest()
        return int(hash_value, 16)

    def __eq__(self, other: "BookWeb"):
        if (isinstance(other, BookWeb) and (hash(self) == hash(other))):
            return True
        return False
    
    @abstractmethod
    def get_book_info(self, response: Network) -> Book:
        """获取书籍的基本信息"""
        return Book(
            "默认书籍", "默认作者", State.END, "默认描述",
            ["https://example.com/",]
        )
    
    @abstractmethod
    def get_chapter_url(self, response: Network) -> List[str]:
        """获取书籍的章节来源"""
        return []
    
    @abstractmethod
    def get_chapter(
        self, response: Network, index: int, book_name: str
    ) -> Chapter:
        """获取章节的内容"""
        return Chapter(
            1, "默认章节", ["https://example.com/",], 
            time.time(), "默认书籍"
        )
    
    @abstractmethod
    def is_protected(
        self, response: Network | None,
        network_error: Exception | None,
        analyze_error: Exception | None
    ) -> bool:
        """判断是否为网站的访问保护"""
        return False
    
    @abstractmethod
    def prevent_protected(self, *param):
        """反爬操作"""
        return None