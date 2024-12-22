#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: prestore.py
# @Time: 10/12/2024 17:51
# @Author: Amundsen Severus Rubeus Bjaaland


import os
import re
import time
import random
import traceback
import threading
from typing import List, Callable
from urllib.parse import urlparse, urlunparse

from .books import Book
from .logs import Logger
from .network import Network
from .settings import Settings
from .bookshelf import BookShelf
from .tools import SQLManager, str_hash, mkdir, try_callback
from .web_manager import DownloadManager, BookWeb


class PreStore(object):
    # 创建一个书籍书架
    BOOKSHELF = BookShelf()
    
    # 定义预下载模块中的 SQL 语句
    # 用于查询数据库中的所有表, 确认是否已经创建了需要的表
    SELECT_TABLE = "SELECT name FROM sqlite_master WHERE type = 'table'"
    # 用于创建数据库中的 URLS 表
    CREATE_TABLE = """CREATE TABLE URLS(
        HASH       BLOB    NOT NULL PRIMARY KEY,
        VISITED    TINYINT NOT NULL DEFAULT 0 CHECK (VISITED=0 OR VISITED=1),
        IS_404     TINYINT NOT NULL DEFAULT 0 CHECK (IS_404=0 OR IS_404=1),
        IS_BOOK    TINYINT NOT NULL DEFAULT 0 CHECK (IS_BOOK=0 OR IS_BOOK=1),
        IS_CHAPTER TINYINT NOT NULL DEFAULT 0 CHECK (IS_CHAPTER=0 OR IS_CHAPTER=1)
    )"""
    # 用于查询数据库中是否存在某个已被访问过的 URL
    SELECT_URL = "SELECT * FROM URLS WHERE HASH=? AND VISITED=1"
    # 用于插入新的 URL 到数据库中
    INSERT_URL = """INSERT INTO URLS (HASH,VISITED,IS_404,IS_BOOK,IS_CHAPTER) 
        SELECT ?,0,0,0,0 WHERE NOT EXISTS
        (SELECT * FROM URLS WHERE HASH=?)"""
    # 用于更新数据库中的 URL 信息
    UPDATE_URL = "UPDATE URLS SET VISITED=?,IS_404=?,IS_BOOK=?,IS_CHAPTER=? WHERE HASH=?"
    
    def __init__(
        self, engine: BookWeb,
        url_info_callback: Callable[[str], None],
        book_info_callback: Callable[[Book], None],
        error_callback: Callable[[Exception], None],
    ):
        """书籍预下载模块
        
        :param engine: 书籍引擎
        :type engine: BookWeb
        :param url_info_callback: URL 信息回调函数
        :type url_info_callback: Callable[[str], None]
        :param book_info_callback: 书籍信息回调函数
        :type book_info_callback: Callable[[Book], None]
        :type error_callback: 错误信息回调函数
        :type error_callback: Callable[[Exception], None]
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(engine, BookWeb)
        # 创建数据存储目录
        mkdir(Settings.DATA_DIR)
        mkdir(Settings.URLS_DIR)
        # 创建日志记录器
        self.__logger = Logger()
        # 初始化数据
        self.__engine = engine
        self.__url_info_callback = try_callback(url_info_callback)
        self.__book_info_callback = try_callback(book_info_callback)
        self.__error_callback = try_callback(error_callback)
        # 拼接获得数据库文件的路径
        db_path = os.path.join(Settings.URLS_DIR, str(hash(engine)))
        # 创建数据库管理器并创建表
        self.__sql_manager = SQLManager(db_path, False)
        self.__create_table()
        # 初始化停机标志
        self.__stop_flag = False
        # 依据是否支持及使用多线程来创建线程池或线程
        if engine.multi_thread and Settings.MULTI_THREAD:
            # 创建线程列表
            self.__thread_pool = []
            # 依据 Python 官方的线程池的默认实现创建指定数量的线程
            for i in range(min(32, os.cpu_count() + 4)):
                # 创建并启动线程
                one_thread = threading.Thread(
                    target=self.__run,
                    name=f"网站({self.__engine.name})书籍预寻找线程-{i + 1}"
                )
                one_thread.start()
                # 将线程添加到线程列表中
                self.__thread_pool.append(one_thread)
        else:
            # 创建并启动线程
            self.__sub_thread = threading.Thread(
                target=self.__run, name=f"网站({self.__engine.name})书籍预寻找线程"
            )
            self.__sub_thread.start()
    
    def stop(self):
        """停止预下载模块, 将内部停止标志设置为 True"""
        # 将停止标志设置为 True
        self.__stop_flag = True
    
    def join(self):
        """等待预下载模块的线程结束"""
        # 依次调用每个线程的 join 方法
        if self.__engine.multi_thread and Settings.MULTI_THREAD:
            for i in self.__thread_pool:
                i.join()
        else:
            self.__sub_thread.join()
    
    def __create_table(self):
        with self.__sql_manager as cursor:
            # 查询数据库中的所有表
            table = cursor.execute(self.SELECT_TABLE).fetchall()
            # 确认是否已经创建了 URLS 表
            if not table:
                # 若不存在则创建 URLS 表
                cursor.execute(self.CREATE_TABLE)
        # 返回 None
        return None
    
    def __append_urls(self, urls: List[str]):
        with self.__sql_manager as cursor:
            # 依次插入 URL 到数据库中
            for i in urls:
                # 计算 URL 的哈希值
                url_hash = str_hash(i)
                # 插入 URL 到数据库中
                cursor.execute(self.INSERT_URL, [url_hash, url_hash])
        # 返回 None
        return None
    
    def __drop_visited_urls(self, urls: List[str]) -> List[str]:
        with self.__sql_manager as cursor:
            # 创建一个缓冲区
            buffer = []
            # 依次查询数据库中的 URL 是否已经被访问过
            for i in urls:
                # 计算 URL 的哈希值
                url_hash = str_hash(i)
                # 查询数据库中的 URL 是否已经被访问过
                result = cursor.execute(self.SELECT_URL, [url_hash,]).fetchall()
                # 若没有被访问过则添加到缓冲区中
                if not result:
                    buffer.append(i)
        # 返回缓冲区
        return buffer
    
    def __update_url(
        self, url: str, is_404: bool, is_book: bool,
        is_chapter: bool, visited: bool = True
    ):
        with self.__sql_manager as cursor:
            # 更新数据库中的 URL 信息
            cursor.execute(
                self.UPDATE_URL,
                [
                    1 if visited else 0, 1 if is_404 else 0,
                    1 if is_book else 0, 1 if is_chapter else 0,
                    str_hash(url)
                ]
            )
    
    def __deal_url(self, response: Network) -> str:
        path = urlparse(response.response.url).path
        if response.response.status_code != 200:
            self.__update_url(path, True, False, False)
            return f"https://{self.__engine.domains[-1]}/"
        
        a_tags = response.bs.find_all("a")
        hrefs = [i.get("href") for i in a_tags]
        hrefs = list(filter(lambda x: True if x else False, hrefs))
        urls = [response.get_next_url(i, True) for i in hrefs]
        hrefs = list(filter(lambda x: True if x else False, hrefs))
        urls = [urlparse(i).path for i in urls]
        self.__append_urls(urls)
        not_visited_urls = self.__drop_visited_urls(urls)
        if not_visited_urls:
            next_url = random.choice(not_visited_urls)
        else:
            if urls:
                next_url = random.choice(urls)
            else:
                return f"https://{self.__engine.domains[-1]}/"
        next_url = urlunparse(["https", self.__engine.domains[-1], next_url, "", "", ""])
        
        if re.match(self.__engine.book_url_pattern, path):
            self.__update_url(path, False, True, False)
            book = DownloadManager(
                response.response.url, self.__engine,
                book_info_callback=lambda x, y, z: None,
                chapter_info_callback=lambda x: None,
                error_callback=lambda x: None,
                stop_callback=lambda: None
            ).download(True)
            self.BOOKSHELF.add_books([(book, hash(self.__engine)),])
            self.__book_info_callback(book)
            return next_url
        if re.match(self.__engine.chapter_url_pattern, path):
            self.__update_url(path, False, False, True)
            return next_url
        self.__update_url(path, False, False, False)
        return next_url
    
    def __run(self):
        next_url = f"https://{self.__engine.domains[-1]}/"
        while (not self.__stop_flag):
            try:
                self.__logger.info(f"正在预寻找书籍: {next_url}")
                response = Network.get(next_url, self.__engine.encoding)
            except Exception as Error:
                self.__logger.warning(traceback.format_exc())
                time.sleep(5)
            else:
                next_url = self.__deal_url(response)