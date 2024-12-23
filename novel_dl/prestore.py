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
from typing import List, Callable, Iterable
from urllib.parse import urlparse, urlunparse

from .books import Book
from .logs import Logger
from .network import Network
from .settings import Settings
from .bookshelf import BookShelf
from .tools import SQLManager, str_hash, mkdir, try_callback
from .web_manager import DownloadManager, BookWeb


class URLFilter(object):
    # 定义将会使用的 SQL 语句
    # 用于查询数据库中的所有表, 确认是否已经创建了需要的表
    SQL_SELECT_TABLE = "SELECT name FROM sqlite_master WHERE type = 'table'"
    # 用于创建数据库中的 URLS 表
    SQL_CREATE_TABLE = """CREATE TABLE URLS(
        HASH       BLOB    NOT NULL PRIMARY KEY,
        VISITED    TINYINT NOT NULL DEFAULT 0 CHECK (VISITED=0 OR VISITED=1),
        IS_404     TINYINT NOT NULL DEFAULT 0 CHECK (IS_404=0 OR IS_404=1),
        IS_BOOK    TINYINT NOT NULL DEFAULT 0 CHECK (IS_BOOK=0 OR IS_BOOK=1),
        IS_CHAPTER TINYINT NOT NULL DEFAULT 0 CHECK (IS_CHAPTER=0 OR IS_CHAPTER=1)
    )"""
    # 用于查询数据库中是否存在某个已被访问过的 URL
    SQL_SELECT_URL = "SELECT * FROM URLS WHERE HASH=? AND VISITED=1"
    # 用于插入新的 URL 到数据库中
    SQL_INSERT_URL = """INSERT INTO URLS (HASH,VISITED,IS_404,IS_BOOK,IS_CHAPTER) 
        SELECT ?,0,0,0,0 WHERE NOT EXISTS
        (SELECT * FROM URLS WHERE HASH=?)"""
    # 用于更新数据库中的 URL 信息
    SQL_UPDATE_URL = "UPDATE URLS SET VISITED=?,IS_404=?,IS_BOOK=?,IS_CHAPTER=? WHERE HASH=?"
    
    def __init__(self, engine: BookWeb):
        """URL 过滤器, 用于管理 URL 的访问状态
        
        :param engine: 书籍引擎
        :type engine: BookWeb
        """
        # 创建数据存储目录
        mkdir(Settings.DATA_DIR)
        mkdir(Settings.URLS_DIR)
        # 创建日志记录器
        self.__logger = Logger()
        # 拼接获得数据库文件的路径
        db_path = os.path.join(Settings.URLS_DIR, f"{hash(engine)}.db")
        # 创建数据库管理器并创建表
        self.__sql_manager = SQLManager(db_path, False)
        self.__create_table()
    
    def __create_table(self):
        with self.__sql_manager as cursor:
            # 查询数据库中的所有表
            table = cursor.execute(self.SQL_SELECT_TABLE).fetchall()
            # 确认是否已经创建了 URLS 表
            if not table:
                # 若不存在则创建 URLS 表
                cursor.execute(self.SQL_CREATE_TABLE)
        # 返回 None
        return None
    
    def append_urls(self, urls: List[str]) -> None:
        """将 URL 添加到数据库中
        注意: URL仅需要路径部分
        
        :param urls: URL 列表
        :type urls: List[str]
        """
        with self.__sql_manager as cursor:
            # 依次插入 URL 到数据库中
            for i in urls:
                # 计算 URL 的哈希值
                url_hash = str_hash(i)
                # 插入 URL 到数据库中
                cursor.execute(
                    self.SQL_INSERT_URL, [url_hash, url_hash]
                )
        # 记录日志: 加入的 URL 数量
        self.__logger.debug(f"已添加 {len(urls)} 个 URL.")
        # 返回 None
        return None
    
    def drop_visited_urls(self, urls: List[str]) -> List[str]:
        """从给定的 URL 列表中删除已经访问过的 URL
        注意: URL 仅需要路径部分
        
        :param urls: URL 列表
        :type urls: List[str]
        :return: 未访问过的 URL 列表
        :rtype: List[str]
        """
        with self.__sql_manager as cursor:
            # 创建一个缓冲区
            buffer = []
            # 依次查询数据库中的 URL 是否已经被访问过
            for i in urls:
                # 计算 URL 的哈希值
                url_hash = str_hash(i)
                # 查询数据库中的 URL 是否已经被访问过
                result = cursor.execute(
                    self.SQL_SELECT_URL, [url_hash,]
                ).fetchall()
                # 若没有被访问过则添加到缓冲区中
                if not result:
                    buffer.append(i)
        # 记录日志: 删除的 URL 数量
        self.__logger.debug(
            f"已删除 {len(urls) - len(buffer)} 个已访问过的 URL."
        )
        # 返回缓冲区
        return buffer
    
    def update_url(
        self, url: str, is_404: bool, is_book: bool, is_chapter: bool
    ) -> None:
        """更新 URL 的相关信息
        
        :param url: URL 的路径部分
        :type url: str
        :param is_404: 是否为 404
        :type is_404: bool
        :param is_book: 是否为书籍 URL
        :type is_book: bool
        :param is_chapter: 是否为章节 URL
        :type is_chapter: bool
        """
        with self.__sql_manager as cursor:
            # 更新数据库中的 URL 信息
            cursor.execute(
                self.SQL_UPDATE_URL,
                [
                    1, 1 if is_404 else 0, 1 if is_book else 0,
                    1 if is_chapter else 0, str_hash(url)
                ]
            )
        # 记录日志: 更新的 URL 信息
        self.__logger.debug(f"已更新 URL: {url}")
        # 返回 None
        return None


class PreStore(object):    
    def __init__(
        self, engines: Iterable[BookWeb],
        url_info_callback: Callable[[str, BookWeb], None],
        book_info_callback: Callable[[Book, BookWeb], None],
        error_callback: Callable[[Exception, BookWeb], None],
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
        # 确认传入的参数的类型是否正确, 并确认引擎是否可以被预寻找书籍 URL
        buffer = []
        for i in engines:
            assert isinstance(i, BookWeb)
            if i.prestore_book_urls:
                buffer.append(i)

        # 创建数据存储目录
        mkdir(Settings.DATA_DIR)
        mkdir(Settings.URLS_DIR)
        # 创建日志记录器
        self.__logger = Logger()
        # 创建书架
        self.__bookshelf = BookShelf()
        
        # 初始化引擎列表
        self.__engines: List[BookWeb] = buffer
        # 初始化各个回调函数
        self.__url_info_callback = try_callback(url_info_callback)
        self.__book_info_callback = try_callback(book_info_callback)
        self.__error_callback = try_callback(error_callback)
        
        self.__url_filters = {hash(i): URLFilter(i) for i in self.__engines}
        
        # 初始化该类需要使用的线程池
        self.__thread_pool = {hash(i): [] for i in self.__engines}
        # 初始化线程运行时标志
        self.__stop_flag = False
        self.__pause_flag = False
        # 启动预下载线程
        self.__start()
    
    def stop(self):
        """停止预下载线程"""
        # 将停止标志设置为 True
        self.__stop_flag = True
        # 记录日志: 正在停止预下载线程
        self.__logger.info("正在停止预下载线程...")
    
    def pause(self):
        """暂停预下载线程"""
        # 将暂停标志设置为 True
        self.__pause_flag = True
        # 记录日志: 正在暂停预下载线程
        self.__logger.info("正在暂停预下载线程...")
    
    def resume(self):
        """恢复预下载线程"""
        # 将暂停标志设置为 False
        self.__pause_flag = False
        # 记录日志: 正在恢复预下载线程
        self.__logger.info("正在恢复预下载线程...")
    
    def join(self):
        """等待所有线程结束"""
        # 等待所有线程结束
        for one_thread_list in self.__thread_pool.values():
            for one_thread in one_thread_list:
                one_thread.join()
        # 记录日志: 所有预下载线程已经结束
        self.__logger.info("所有预下载线程已经结束.")
    
    def __start(self):
        # 依次处理每一个引擎
        for one_engine in self.__engines:
            # 确认该引擎是否支持多线程以及设置中是否使用多线程
            if one_engine.multi_thread and Settings.MULTI_THREAD:
                # 按照 Python 官方文档中线程池的默认方法获取最大线程数
                max_workers = min(32, os.cpu_count() + 4)
                # 依次创建线程并启动
                for ii in range(max_workers):
                    # 创建线程并启动
                    one_thread = threading.Thread(
                        target=self.__run, args=(one_engine,),
                        name=f"网站({hash(one_engine)})预下载线程-{ii + 1}"
                    )
                    one_thread.start()
                    # 将线程添加到线程池中
                    self.__thread_pool[hash(one_engine)].append(one_thread)
            # 任意一个条件不满足则只创建一个线程
            else:
                # 创建线程并添加到线程池中
                self.__thread_pool[hash(one_engine)].append(
                    threading.Thread(
                        target=self.__run, args=(one_engine,),
                        name=f"网站({hash(one_engine)})预下载线程"
                    )
                )
                # 启动线程
                self.__thread_pool[hash(one_engine)][-1].start()
    
    def __run(self, engine: BookWeb):
        # 初始化第一个 URL, 默认为整个网站引擎支持的域名列表中的最后一个域名
        next_url = f"https://{engine.domains[-1]}/"
        # 进入循环, 每次循环都会尝试获取一个新的 URL 并处理
        while True:
            # 确认是否需要退出循环
            if self.__stop_flag:
                break
            # 确认是否需要暂停循环
            if self.__pause_flag:
                time.sleep(1)
                continue
            # 若都不需要, 则即将获取一个 URL, 在此打印信息
            self.__logger.info(f"正在预寻找书籍: {next_url}")
            # 尝试获取 URL, 注意: 获取时会禁止重定向
            try:
                response = Network.get(
                    next_url, engine.encoding, False
                )
            # 如果出现网络错误, 则打印错误信息并等待 5 秒
            except Exception as network_error:
                self.__logger.warning(
                    traceback.format_exc().replace("\n", "\n\t")
                )
                self.__error_callback(network_error, engine)
                time.sleep(5)
            # 如果没有出现网络错误, 则处理获取到的 URL
            else:
                next_url = self.__deal_url(response, engine)
                # 调用 URL 信息回调函数
                self.__url_info_callback(next_url, engine)
            
    
    def __deal_url(self, response: Network, engine: BookWeb) -> str:
        # 确认状态码是否为 200
        if not self.__check_status_code(response, engine):
            # 如果状态码不为 200, 则直接返回网站的最后一个域名
            return f"https://{engine.domains[-1]}/"
        
        # 获取网页上所有的 URL
        urls = self.__get_urls(response, engine)
        # 从网页上所有的 URL 中抽取一个作为下一个要访问的 URL
        next_url = self.__get_next_url(urls, engine)
        
        # 获取当前 URL 的路径部分
        path = urlparse(response.response.url).path
        # 如果当前 URL 是书籍 URL, 则下载书籍的基本信息, 
        # 并将当前 URL 标记为书籍 URL 和已访问, 并返回下一个 URL
        if re.match(engine.book_url_pattern, path):
            # 下载书籍的基本信息
            book = DownloadManager(
                response.response.url, engine,
                book_info_callback=lambda x, y, z: None,
                chapter_info_callback=lambda x: None,
                error_callback=lambda x: None,
                stop_callback=lambda: None
            ).download(True)
            # 将书籍添加到书架中
            self.__bookshelf.add_books([(book, hash(engine)),])
            # 调用书籍信息回调函数
            self.__book_info_callback(book, engine)
            # 将当前 URL 标记为书籍 URL 和已访问
            self.__url_filters[hash(engine)] \
                .update_url(path, False, True, False)
            # 返回下一个 URL
            return next_url
        # 如果当前 URL 是章节 URL, 则
        # 将当前 URL 标记为章节 URL 和已访问, 并返回下一个 URL
        if re.match(engine.chapter_url_pattern, path):
            # 将当前 URL 标记为章节 URL 和已访问
            self.__url_filters[hash(engine)] \
                .update_url(path, False, False, True)
            # 返回下一个 URL
            return next_url
        # 如果不是书籍 URL 或者章节 URL, 则仅将当前 URL 标记为已访问,
        self.__url_filters[hash(engine)] \
            .update_url(path, False, False, False)
        # 并直接返回下一个 URL
        return next_url
    
    def __check_status_code(
        self, response: Network, engine: BookWeb
    ) -> bool:
        # 如果状态码不为 200, 则将当前 URL 标记为 404, 并返回 False
        if response.response.status_code != 200:
            # 确认是否为重定向
            if 299 < response.response.status_code < 400:
                self.__logger.info(
                    f"{response.response.url} 重定向到\n\t" \
                    f"{response.response.headers['Location']}"
                )
            self.__url_filters[hash(engine)].update_url(
                urlparse(response.response.url).path, True, False, False
            )
            return False
        # 如果状态码为 200, 则返回 True
        return True
    
    def __get_urls(self, response: Network, engine: BookWeb) -> List[str]:
        # 如果没有获取到网页内容, 则返回空列表
        if not response.text:
            return []
        # 获取网页上所有的 a 标签
        a_tags = response.bs.find_all("a")
        # 获取 a 标签中的 href 属性
        hrefs = [i.get("href") for i in a_tags]
        # 过滤掉 None 值以及空字符串
        hrefs = list(filter(lambda x: True if x else False, hrefs))
        # 依据 href 内容转换得到对应的 URL, 同时过滤掉不是该引擎支持的域名的 URL
        urls = [response.get_next_url(i, True) for i in hrefs]
        # 过滤掉空字符串
        urls = list(filter(lambda x: True if x else False, urls))
        # 仅保留 URL 的路径部分
        urls = [urlparse(i).path for i in urls]
        # 将 URL 添加到 URL 过滤器中
        self.__url_filters[hash(engine)].append_urls(urls)
        # 返回 URL 列表
        return urls
    
    def __get_next_url(self, urls: List[str], engine: BookWeb) -> str:
        # 依靠 URL 过滤器去除已访问过的 URL
        not_visited_urls = self.__url_filters[hash(engine)] \
            .drop_visited_urls(urls)
        # 从未访问过的 URL 中随机选择一个作为下一个 URL
        if not_visited_urls:
            next_url = random.choice(not_visited_urls)
        # 如果没有未访问过的 URL, 则从已访问过的 URL 中随机选择一个作为下一个 URL
        else:
            # 从已访问过的 URL 中随机选择一个作为下一个 URL
            if urls:
                next_url = random.choice(urls)
            # 如果没有已访问过的 URL, 则直接返回网站的最后一个域名
            else:
                return f"https://{engine.domains[-1]}/"
        # 将仅有路径的 URL 转换为完整的 URL 并返回
        return urlunparse(["https", engine.domains[-1], next_url, "", "", ""])