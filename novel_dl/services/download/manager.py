#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: manager.py
# @Time: 18/02/2025 18:16
# @Author: Amundsen Severus Rubeus Bjaaland
"""书籍网站引擎管理器模块
该模块提供了 WebManager 类，用于管理书籍网站引擎并执行相关操作。
类:
    WebManager: 书籍网站引擎管理器类，提供添加引擎、获取引擎、
                执行引擎操作、下载书籍信息和章节等功能。
方法:
    __init__(self):
        初始化 WebManager 实例，添加默认的引擎。
    append(self, web: BookWeb) -> bool:
        添加引擎。如果引擎不可用或者已经添加过则返回 False。
    engines(self) -> Generator[BookWeb, None, None]:
        返回一个引擎生成器，包含所有引擎对象。
    get_engine_by_name(self, name: str) -> BookWeb | None:
        通过引擎名获取引擎对象。如果没有找到则返回 None。
    get_engine_by_url(self, url: str) -> BookWeb | None:
        通过 URL 获取引擎对象。如果没有找到则返回 None。
    __operate(
        执行引擎操作。如果操作失败则返回 False, None。
        如果操作成功则返回 True, 结果。
    __download_book_info(
        下载书籍信息。如果下载失败则返回 None。
        返回书籍信息和章节列表。
    __download_chapter(
        下载章节。返回书籍对象。
    download(
        下载书籍。如果下载失败则返回 None。
        返回书籍对象。
"""


# 导入标准库
from urllib.parse import urlparse
from typing import List, Generator, Tuple, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

# 导入自定义库
from .engines import ENGINE_LIST
from .config import Operations, BookWeb
from novel_dl.utils.network import Network
from novel_dl.core import Settings, Book, Chapter


class WebManager(object):
    def __init__(self):
        """书籍网站引擎管理器"""
        # 初始化引擎列表
        self.__web_list: List[BookWeb] = []
        # 添加默认的引擎
        for i in ENGINE_LIST:
            self.append(i)
    
    def append(self, web: BookWeb) -> bool:
        """添加引擎
        如果引擎不可用或者已经添加过则返回 False
        
        :param web: 引擎对象
        :type web: BookWeb
        :return: 添加是否成功
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(web, BookWeb)
        # 如果引擎不可用或者已经添加过则返回 False
        if (web.workable is False) or (web in self.__web_list):
            return False
        # 添加引擎至引擎列表
        self.__web_list.append(web)
        # 返回添加成功
        return True
    
    def engines(self) -> Generator[BookWeb, None, None]:
        """返回一个引擎生成器, 包含所有引擎对象"""
        for web in self.__web_list:
            yield web
    
    def get_engine_by_name(self, name: str) -> BookWeb | None:
        """通过引擎名获取引擎对象
        如果有多个同名引擎则返回第一个  
        如果没有找到则返回 None  
        
        :param name: 引擎名
        :type name: str
        :return: 引擎对象或者 None
        """
        for web in self.__web_list:
            if web.name == name:
                return web
        return None
    
    def get_engine_by_url(self, url: str) -> BookWeb | None:
        """通过 URL 获取引擎对象
        如果有多个引擎支持该 URL 则返回第一个
        如果没有找到则返回 None
        
        :param url: URL
        :type url: str
        :return: 引擎对象或者 None
        """
        for web in self.__web_list:
            if urlparse(url).netloc in web.domains:
                return web
        return None
    
    def __operate(
        self, engine: BookWeb, url: str, operation: Operations, **kwargs
    ) -> Tuple[bool, Book | List[str] | Chapter | None]:
        """执行引擎操作
        如果操作失败则返回 False, None
        如果操作成功则返回 True, 结果
        
        :param engine: 引擎对象
        :type engine: BookWeb
        :param url: URL
        :type url: str
        :param operation: 操作类型
        :type operation: Operations
        :param kwargs: 其他参数
        :return: 操作是否成功, 结果
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(engine, BookWeb)
        assert isinstance(url, str)
        assert isinstance(operation, Operations)
        # 循环直到操作成功
        while True:
            # 尝试获取网络对象
            try:
                network_obj = Network.get(url, engine.encoding)
            except Exception as network_error:
                # 如果网络对象获取失败则判断是否存在保护机制
                if engine.is_protected(None, network_error, None):
                    # 如果存在保护机制则反制保护机制
                    engine.prevent_protected()
                    continue
                # 如果不存在保护机制则返回 False, None
                return False, None
            # 尝试执行操作
            try:
                # 根据操作类型执行不同的操作
                match operation:
                    case Operations.INFO:
                        result = engine.get_book_info(network_obj)
                    case Operations.URLS:
                        result = engine.get_chapter_url(
                            network_obj
                        )
                    case Operations.CHAPTER:
                        result = engine.get_chapter(
                            network_obj, **kwargs
                        )
            except Exception as analyze_error:
                # 如果操作失败则判断是否存在保护机制
                if engine.is_protected(
                    network_obj, None, analyze_error
                ):
                    # 如果存在保护机制则反制保护机制
                    engine.prevent_protected()
                    continue
                # 如果不存在保护机制则返回 False, None
                return False, None
            # 如果操作成功则返回 True, 结果
            return True, result
    
    def __download_book_info(
        self, engine: BookWeb, url: str,
        book_middle_ware: Callable[[Book], Book] = lambda x: x,
        chapters_middle_ware: \
        Callable[[List[Chapter]], List[Chapter]] = lambda x: x,
    ) -> Tuple[Book, List[str]] | None:
        """下载书籍信息
        如果下载失败则返回 None  
        注意: 如果书籍中间件返回的书籍对象中的章节
        含有与章节列表中的章节重复的章节来源, 且强制重载为 False,
        则章节列表中的章节来源会被移除
        
        :param engine: 引擎对象
        :type engine: BookWeb
        :param url: URL
        :type url: str
        :param book_middle_ware: 书籍中间件, 用于处理书籍信息
        :type book_middle_ware: Callable[[Book], Book]
        :param chapters_middle_ware: 章节列表中间件, 用于处理章节列表
        :type chapters_middle_ware: 
        Callable[[List[Chapter]], List[Chapter]]
        :return: 书籍信息和章节列表
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(engine, BookWeb)
        assert isinstance(url, str)
        # 获取书籍信息
        book = self.__operate(engine, url, Operations.INFO)
        # 如果获取失败则返回 None
        if book[0] == False:
            return None
        # 从结果中提取书籍信息
        book = book[1]
        # 使用书籍中间件处理书籍信息
        book = book_middle_ware(book)
        # 获取章节列表
        chapter_list = self.__operate(engine, url, Operations.URLS)
        # 如果获取失败则返回 None
        if chapter_list[0] == False:
            return None
        # 从结果中提取章节列表
        chapter_list = chapter_list[1]
        # 如果不强制重新加载则从章节列表中移除已经下载的章节
        if not Settings().FORCE_RELOAD:
            for i in book.chapters:
                for ii in i.sources:
                    chapter_list.remove(ii)
        # 使用章节列表中间件处理章节列表
        chapter_list = chapters_middle_ware(chapter_list)
        # 返回书籍信息和章节列表
        return (book, chapter_list)
    
    def __download_chapter(
        self, engine: BookWeb, url: str, book: Book,
        chapter_list: List[str],
        chapter_middle_ware: Callable[[Chapter, Book], Chapter] = \
        lambda x: x
    ) -> Book:
        """下载章节
        
        :param engine: 引擎对象
        :type engine: BookWeb
        :param url: URL
        :type url: str
        :param book: 书籍对象
        :type book: Book
        :param chapter_list: 章节列表
        :type chapter_list: List[str]
        :param chapter_middle_ware: 章节中间件, 用于处理章节信息
        :type chapter_middle_ware: Callable[[Chapter], Chapter]
        :return: 书籍对象
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(engine, BookWeb)
        assert isinstance(url, str)
        assert isinstance(book, Book)
        assert isinstance(chapter_list, List)
        # 如果启用多线程则使用多线程下载
        if Settings().MULTI_THREAD and engine.multi_thread:
            # 使用线程池下载章节
            with ThreadPoolExecutor() as executor:
                # 提交任务到线程池
                future_to_url = {
                    executor.submit(
                        self.__operate, engine, chapter_url,
                        Operations.CHAPTER, index=index + 1,
                        book_name=book.name
                    ): chapter_url
                    for index, chapter_url in enumerate(chapter_list)
                }
                # 当所有任务完成时, 获取结果
                for future in as_completed(future_to_url):
                    # 获取结果
                    chapter = future.result()
                    # 如果获取失败则跳过
                    if chapter[0] == False:
                        continue
                    # 从结果中提取章节
                    chapter = chapter[1]
                    # 使用章节中间件处理章节
                    chapter = chapter_middle_ware(chapter, book)
                    # 添加章节到书籍对象
                    book.append(chapter)
        # 如果不启用多线程则使用单线程下载
        else:
            for index, chapter_url in enumerate(chapter_list):
                # 下载章节
                chapter = self.__operate(
                    engine, chapter_url, Operations.CHAPTER,
                    index=index + 1, book_name=book.name
                )
                # 如果下载失败则跳过
                if chapter[0] == False:
                    continue
                # 从结果中提取章节
                chapter = chapter[1]
                # 使用章节中间件处理章节
                chapter = chapter_middle_ware(chapter, book)
                # 添加章节到书籍对象
                book.append(chapter)
        # 将书籍对象中的章节排序
        book.sort()
        # 返回书籍对象
        return book
    
    def download(
        self, url: str, book_middle_ware: Callable[[Book], Book] = \
        lambda x: x, chapters_middle_ware: \
        Callable[[List[Chapter]], List[Chapter]] = lambda x: x,
        chapter_middle_ware: Callable[[Chapter, Book], Chapter] = \
        lambda x: x
    ) -> Book | None:
        """下载书籍
        如果下载失败则返回 None
        
        :param url: URL
        :type url: str
        :param book_middle_ware: 书籍中间件, 用于处理书籍信息
        :type book_middle_ware: Callable[[Book], Book]
        :param chapters_middle_ware: 章节列表中间件, 用于处理章节列表
        :type chapters_middle_ware:
        Callable[[List[Chapter]], List[Chapter]]
        :param chapter_middle_ware: 章节中间件, 用于处理章节信息
        :type chapter_middle_ware: Callable[[Chapter, Book], Chapter]
        :return: 书籍对象或者 None
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(url, str)
        # 根据 URL 获取引擎对象
        engine = self.get_engine_by_url(url)
        # 如果引擎对象不存在则返回 None
        if engine is None:
            return None
        # 下载书籍信息
        result = self.__download_book_info(
            engine, url, book_middle_ware, chapters_middle_ware
        )
        # 如果下载失败则返回 None
        if result is None:
            return None
        # 从结果中提取书籍信息和章节列表
        book = result[0]
        chapter_list = result[1]
        # 下载章节
        book = self.__download_chapter(
            engine, url, book, chapter_list, chapter_middle_ware
        )
        # 返回书籍对象
        return book