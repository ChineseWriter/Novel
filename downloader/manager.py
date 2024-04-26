#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: manager.py
# @Time: 03/04/2024 17:29
# @Author: Amundsen Severus Rubeus Bjaaland


import threading

from .logs import Logger
from .objects import Chapter


def singleton(cls):
    thread_lock = threading.Lock()
    manager = {}

    def _singleton(*args, **kwargs):
        with thread_lock:
            if cls not in manager:
                manager[cls] = cls(*args, **kwargs)
        return manager[cls]
    
    return _singleton


@singleton
class Manager(object):
    def __init__(self):
        self.__logger = Logger()
    
    def create_chapter(
        self, book_name: str, index: int, chapter_name: str,
        source: str, content: str = ""
    ):
        self.__logger.books.debug(f"创建了名为{chapter_name}的章节。")
        return Chapter(book_name, index, chapter_name, source, content)
