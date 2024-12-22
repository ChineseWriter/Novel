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
    BOOK_SHELF = BookShelf()
    
    SELECT_TABLE = "SELECT name FROM sqlite_master WHERE type = 'table'"
    CREATE_TABLE = """CREATE TABLE URLS(
        HASH       BLOB    NOT NULL PRIMARY KEY,
        VISITED    TINYINT NOT NULL DEFAULT 0 CHECK (VISITED=0 OR VISITED=1),
        IS_404     TINYINT NOT NULL DEFAULT 0 CHECK (IS_404=0 OR IS_404=1),
        IS_BOOK    TINYINT NOT NULL DEFAULT 0 CHECK (IS_BOOK=0 OR IS_BOOK=1),
        IS_CHAPTER TINYINT NOT NULL DEFAULT 0 CHECK (IS_CHAPTER=0 OR IS_CHAPTER=1)
    )"""
    SELECT_URL = "SELECT * FROM URLS WHERE HASH=? AND VISITED=1"
    INSERT_URL = """INSERT INTO URLS (HASH,VISITED,IS_404,IS_BOOK,IS_CHAPTER) 
        SELECT ?,0,0,0,0 WHERE NOT EXISTS
        (SELECT * FROM URLS WHERE HASH=?)"""
    UPDATE_URL = "UPDATE URLS SET VISITED=?,IS_404=?,IS_BOOK=?,IS_CHAPTER=? WHERE HASH=?"
    
    def __init__(self, engine: BookWeb, book_info_callback: Callable[[Book], None]):
        mkdir(Settings.DATA_DIR)
        mkdir(Settings.URLS_DIR)
        self.__logger = Logger()
        self.__engine = engine
        self.__book_info_callback = try_callback(book_info_callback)
        db_path = os.path.join(Settings.URLS_DIR, str(hash(engine)))
        self.__sql_manager = SQLManager(db_path, False)
        self.__create_table()
        
        self.__stop_flag = False
        
        self.__sub_thread = threading.Thread(
            target=self.__run, name=f"{self.__engine.name}-书籍预寻找线程"
        )
        self.__sub_thread.start()
    
    def stop(self):
        self.__stop_flag = True
    
    def join(self):
        self.__sub_thread.join()
    
    def __create_table(self):
        with self.__sql_manager as cursor:
            table = cursor.execute(self.SELECT_TABLE).fetchall()
            if not table:
                cursor.execute(self.CREATE_TABLE)
        return None
    
    def __append_urls(self, urls: List[str]):
        with self.__sql_manager as cursor:
            for i in urls:
                url_hash = str_hash(i)
                cursor.execute(self.INSERT_URL, [url_hash, url_hash])
        return None
    
    def __drop_visited_urls(self, urls: List[str]) -> List[str]:
        with self.__sql_manager as cursor:
            buffer = []
            for i in urls:
                url_hash = str_hash(i)
                result = cursor.execute(self.SELECT_URL, [url_hash,]).fetchall()
                if not result:
                    buffer.append(i)
        return buffer
    
    def __update_url(
        self, url: str, is_404: bool, is_book: bool,
        is_chapter: bool, visited: bool = True
    ):
        with self.__sql_manager as cursor:
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
            next_url = random.choice(urls)
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
            self.BOOK_SHELF.add_books([(book, hash(self.__engine)),])
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