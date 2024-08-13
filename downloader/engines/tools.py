#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: tools.py
# @Time: 03/04/2024 17:33
# @Author: Amundsen Severus Rubeus Bjaaland


from abc import ABCMeta
from typing import List
from bs4 import Tag
from urllib.parse import urlparse, ParseResult

from ..books import Book, BookState


class URL(object):
    def __init__(self, url: str):
        self.__url = url
        self.__parse_result = urlparse(url)
    
    @property
    def parse_result(self) -> ParseResult: return self.__parse_result
    
    @property
    def url(self) -> str: return self.__url
    
    def __str__(self) -> str: return self.__url


class BookWeb(metaclass=ABCMeta):
    domains: List[URL] = []
    name: str = ""
    book_url_pattern: str = ""
    chapter_url_pattern: str = ""
    section_url_pattern: str = ""
    # TODO 测试功能
    # author_url_pattern: str = ""
    encoding: str = "UTF-8"
    
    def __str__(self) -> str: return self.name
    
    def __repr__(self):
        return f"<WebConfig name={self.name} encoding={self.encoding}>"
    
    def get_book_info(self, book_html: Tag) -> Book:
        """获取书籍的基本信息"""
        return Book("", "", BookState.END, "", "", b"")
    
    def get_chapter_text(self, chapter_html: Tag, index: int) -> ChapterData:
        """获取章节的内容"""
        response.response.encoding = self.encoding
        return ChapterData(index + 1, "")
    
    def is_protected(self, response: Network) -> bool:
        """判断是否为网站的访问保护"""
        response.response.encoding = self.encoding
        return False
