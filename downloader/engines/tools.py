#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: tools.py
# @Time: 03/04/2024 17:33
# @Author: Amundsen Severus Rubeus Bjaaland


from abc import ABCMeta
from typing import List

from bs4 import Tag

from ..books import Book


class BookWeb(metaclass=ABCMeta):
    name: str = ""
    domains: List[str] = []
    book_url_pattern: str = ""
    chapter_url_pattern: str = ""
    section_url_pattern: str = ""
    encoding: str = "UTF-8"
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self):
        return f"<WebConfig name={self.name} encoding={self.encoding}>"
    
    def get_book_info(self, book_html: Tag) -> Book:
        """获取书籍的基本信息"""
        return Book("", "", Book.State.END, "", "", b"")
    
    def get_chapter_url(self, book_html: Tag) -> List[str]:
        """获取书籍的章节来源"""
        return []
    
    def get_chapter_text(self, chapter_html: Tag) -> List[str]:
        """获取章节的内容"""
        return []
    
    def is_protected(self, response: Network) -> bool:
        """判断是否为网站的访问保护"""
        return False
