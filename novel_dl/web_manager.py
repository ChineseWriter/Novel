#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: web_manager.py
# @Time: 26/10/2024 16:29
# @Author: Amundsen Severus Rubeus Bjaaland
"""书籍下载网站引擎的使用与管理"""


# 导入标准库
import re
import hashlib
import traceback
from threading import Lock
from urllib.parse import urlparse
from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Union, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

# 导入第三方库
from tqdm import tqdm

#导入自定义库
from .logs import Logger
from .network import Network
from .settings import Settings
from .tools import try_callback
from .books import Book, Chapter


def default_callback():
    """生成默认的回调函数, 用于指示书籍下载情况和进度"""
    # 创建几个函数需要共用的用于保存下载进度的变量
    bar: Union[None, tqdm] = None
    
    def book_info_callback(book: Book, all_chapters: int, need_chapters: int):
        """指示书籍基本信息的回调函数, 同时创建一个进度条"""
        nonlocal bar
        # 如果需要下载的章节数为0, 则直接输出提示即可
        if need_chapters == 0:
            return None
        Logger().set_scheme("tqdm")
        # 创建进度条, 并设置总长度(需要下载的章节数)和书籍名称
        bar = tqdm(total=need_chapters)
        bar.set_description(f"《{book.name}》")
        
    def chapter_info_callback(chapter: Chapter):
        """更新章节的基本信息, 并更新进度条"""
        nonlocal bar
        # 更新进度条的进度
        if bar is not None:
            bar.update()
    
    def error_callback(exception: Exception):
        """出现错误时显示它们, 来排查程序执行过程中的问题"""
        pass
    
    def close_bar():
        """书籍下载完毕后关闭进度条, 防止出现进度条未更新完但书籍已经下载完的情况"""
        nonlocal bar
        # 确保在书籍下载完毕后进度条被关闭
        if bar is not None:
            bar.close()
            Logger().set_scheme("default")
            bar = None
    
    return (book_info_callback, chapter_info_callback, error_callback, close_bar)


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
            "默认书籍", "默认作者", "https://example.com/",
            Book.State.END, "默认描述", b""
        )
    
    @abstractmethod
    def get_chapter_url(self, response: Network) -> List[str]:
        """获取书籍的章节来源"""
        return []
    
    @abstractmethod
    def get_chapter(self, response: Network) -> Chapter:
        """获取章节的内容"""
        return Chapter("默认章节", 1, "https://example.com/", "默认书籍")
    
    @abstractmethod
    def is_protected(
        self, response: Union[Network, None],
        network_error: Union[Exception, None],
        analyze_error: Union[Exception, None]
    ) -> bool:
        """判断是否为网站的访问保护"""
        return False
    
    @abstractmethod
    def prevent_protected(self, *param):
        """反爬操作"""
        return None


class WebManager(object):
    """书籍网站管理"""
    def __init__(self):
         # 初始化日志记录器
        self.__logger = Logger()
        # 初始化引擎列表
        self.__engine_list: List[BookWeb] = []
        # 为了防止出现循环导入错误，这里将其放在函数内进行导入
        from .web_engines import ENGINE_LIST
        # 逐个导入预置的引擎
        [self.append_engine(i) for i in ENGINE_LIST]
    
    @property
    def engine_list(self):
        for one_engine in self.__engine_list:
            yield one_engine
    
    def get_engine(self, url: str) -> Union[BookWeb, None]:
        """依据给定的 URL 寻找支持的引擎
        
        :param url: 指定的 URL
        :type url: str
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(url, str)
        # 从给定的 URL 中解析出 domain
        domain = urlparse(url).netloc.split(":")[0]
        # 查找是否存在匹配的 domain
        for one_engine in self.__engine_list:
            if domain in one_engine.domains:
                self.__logger.debug(f"为该 URL ({url})找到匹配的引擎({str(one_engine)}).")
                return one_engine
        self.__logger.warning(f"没有为该 URL ({url})找到匹配的引擎.")
        # 没有找到则返回 None
        return None
    
    def append_engine(self, engine: BookWeb) -> bool:
        """添加一个自定义引擎
        
        :param engine: 自定义的网络引擎
        :type engine: BookWeb
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(engine, BookWeb)
        # 确认该引擎是否在引擎列表里
        if engine not in self.__engine_list:
            # 确认引擎是否可用
            if engine.workable:
                # 添加引擎到引擎列表里
                self.__engine_list.append(engine)
                self.__logger.debug(f"添加一个引擎({str(engine)})到引擎列表中.")
            else:
                self.__logger.debug(f"该引擎({str(engine)})处于不可用状态, 不会添加到引擎列表.")
            # 成功添加则返回 True
            return True
        self.__logger.debug(f"加入的引擎({str(engine)})已存在, 不会重复添加.")
        # 如果已存在则不做任何操作并返回 False
        return False
    
    def download(self, url: str) -> Book:
        """下载书籍
        
        :param url: 书籍信息页面的地址
        :type url: str
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(url, str)
        # 获取对应的引擎
        engine = self.get_engine(url)
        # 检查是否存在支持该网址的引擎
        if engine is None:
            return Book.empty_book()
        self.__logger.info(f"开始下载该 URL ({url})下的书籍")
        # 返回下载的结果
        return DownloadManager(url, engine, *default_callback()).download()


class DownloadManager(object):
    def __init__(
        self, url: str, engine: BookWeb,
        book_info_callback: Callable[[Book, int, int], None],
        chapter_info_callback: Callable[[Chapter], None],
        error_callback: Callable[[Exception], None],
        stop_callback: Callable[[], None]
    ) -> None:
        """书籍下载管理器
        
        :param url: 书籍的源网址
        :type url: str
        :param engine: 书籍对应的引擎
        :type engine: BookWeb
        :param book_info_callback:书籍信息回调函数, 要求输入为 Book 对象、总章节数和要下载的章节数
        :type book_info_callback: Callable[[Book, int], None]
        :param chapter_info_callback: 章节信息回调函数, 要求输入为 Chapter 对象
        :type chapter_info_callback: Callable[[Chapter], None]
        :param error_callback: 错误信息回调函数, 要求输入为一个错误类型
        :type error_callback: Callable[[Exception], None]
        :param stop_callback: 停止信息回调函数, 没有输入
        :type stop_callback: Callable[[], None]
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(url, str)
        assert isinstance(engine, BookWeb)
         # 初始化日志记录器
        self.__logger = Logger()
        # 设置下载书籍的基本信息
        self.__url = url
        self.__engine = engine
        # 设置所有需要用到的回调函数
        self.__book_info_callback = try_callback(book_info_callback)
        self.__chapter_info_callback = try_callback(chapter_info_callback)
        self.__error_callback = try_callback(error_callback)
        self.__stop_callback = try_callback(stop_callback)
        # 为了防止出现循环导入错误，这里将其放在函数内进行导入
        from .bookshelf import BookShelf
        # 启用书架, 以保存下载过的数据
        self.__book_shelf = BookShelf()
    
    def download(self, only_info: bool = False) -> Book:
        """下载书籍
        
        :param only_info: 是否要只下载书籍信息, 而不是整本书籍, 为 True 则只下载信息
        :type only_info: bool
        """
        # 获取基本书籍信息
        book_obj, chapter_list = self.__download_book_info()
        # 若只下载书籍信息则直接返回结果
        if only_info:
            return book_obj
        # 下载章节内容
        book = self.__download_chapters_content(book_obj, chapter_list)
        # 调用停止下载回调函数, 防止出现进度条等组件未正确退出的情况
        self.__stop_callback()
        if book == Book.empty_book():
            self.__logger.error("下载书籍失败.")
        # 返回整本书籍
        return book
    
    def __operate(
        self, url: str, operate_func: Callable, engine: BookWeb
    ) -> Tuple[bool, Any]:
        """执行指定的函数
        
        :param url: 需要操作的 URL
        :type url: str
        :param operate_func: 需要的操作
        :type operate_func: Callable
        :param engine: 执行操作的引擎
        :type engine: BookWeb
        """
        while True:
            # 尝试从指定的 URL 获取内容
            try:
                network_obj = Network.get(url, engine.encoding)
            except Exception as network_error:
                if engine.is_protected(None, network_error, None):
                    self.__logger.info(f"下载时遭遇反爬机制. 错误: {type(network_error)}")
                    engine.prevent_protected()
                    continue
                error_info = traceback.format_exc().replace("\n", "\n\t\t")
                self.__logger.warning(f"下载时发生无法处理的错误:\n\t\t{error_info}")
                self.__error_callback(network_error)
                return False, None
            # 尝试使用给定的函数解析内容
            try:
                result = operate_func(network_obj)
            except Exception as analyze_error:
                if engine.is_protected(network_obj, None, analyze_error):
                    self.__logger.info(f"下载时遭遇反爬机制. 错误: {type(analyze_error)}")
                    engine.prevent_protected()
                    continue
                error_info = traceback.format_exc().replace("\n", "\n\t\t")
                self.__logger.warning(f"下载时发生无法处理的错误:\n\t\t{error_info}")
                self.__error_callback(analyze_error)
                return False, None
            return True, result
    
    def __download_book_info(self) -> Tuple[Book, List[str]]:
        # 检查引擎对应的书籍 URL 模式是否与传入的 URL 匹配
        if not re.match(self.__engine.book_url_pattern, urlparse(self.__url).path):
            self.__logger.error(
                f"引擎对应书籍 URL 模式({self.__engine.book_url_pattern})" \
                    f"与传入 URL ({self.__url})不匹配."
            )
            return Book.empty_book(), []
        # 获取书籍的基本信息
        result_book_info: Tuple[bool, Book] = \
            self.__operate(self.__url, self.__engine.get_book_info, self.__engine)
        if not result_book_info[0]:
            return Book.empty_book(), []
        book = result_book_info[1]
        # 获取书籍的所有章节的网址
        result_chapter_urls: Tuple[bool, List[str]] = \
            self.__operate(self.__url, self.__engine.get_chapter_url, self.__engine)
        if not result_chapter_urls[0]:
            return Book.empty_book(), []
        # 过滤与引擎对应的章节 URL 模式不匹配的章节 URL
        chapter_url_list: List[str] = []
        for chapter_url in result_chapter_urls[1]:
            if re.match(self.__engine.chapter_url_pattern, urlparse(chapter_url).path):
                chapter_url_list.append(chapter_url)
            else:
                self.__logger.warning(
                    f"引擎对应章节 URL 模式({self.__engine.chapter_url_pattern})" \
                    f"与获取到的 URL ({chapter_url})不匹配."
                )
        # 使用本地副本将已下载的章节补充入书籍中
        if not Settings.FORCE_RELOAD:
            self.__logger.debug(f"已使用本地副本预填充书籍({book.name}).")
            book = self.__book_shelf.complete_book(book)
        # 触发书籍信息获取回调函数
        self.__book_info_callback(
            book, len(chapter_url_list), len(chapter_url_list) - len(book)
        )
        add_info = "已下载过书籍, 将采用本地缓存." \
            if not len(chapter_url_list) - len(book) else ""
        self.__logger.info(f"成功获取书籍({book.name})的基本信息. {add_info}")
        # 将书籍添加到书架上
        self.__book_shelf.add_books([(book, hash(self.__engine))], Settings.FORCE_RELOAD)
        # 返回最终的下载结果
        return book, chapter_url_list
    
    def __download_chapters_content(
        self, book: Book, chapter_url_list: List[str]
    ) -> Book:
        # 如果指定多线程且该网站的引擎允许多线程, 则将使用多线程进行下载
        if Settings.MULTI_THREAD and self.__engine.multi_thread:
            self.__logger.debug(f"将使用多线程下载书籍({book.name}).")
            # 使用多线程下载章节
            with ThreadPoolExecutor(thread_name_prefix=f"书籍《{book.name}》下载线程") as executor:
                future_to_url = {
                    executor.submit(
                        self.__download_chapter_content, chapter_url, index + 1, book
                    ): chapter_url
                    for index, chapter_url in enumerate(chapter_url_list)
                }
                # 等待所有线程执行完毕
                as_completed(future_to_url)
            # 返回下载好的书籍对象
            return book
        # 不使用多线程则按照列表顺序逐个下载章节
        for index, chapter_url in enumerate(chapter_url_list):
            self.__download_chapter_content(chapter_url, index + 1, book)
        # 返回下载好的书籍对象
        return book
    
    def __download_chapter_content(self, chapter_url: str, index: int, book: Book) -> bool:
        # 确认章节是否已经存在于书籍中, 若存在则直接退出下载
        for one_chapter in book.chapter_list:
            # 判断是否存在主要基于章节的 index
            if index == one_chapter.index:
                self.__logger.debug(
                    f"该章节(序号: {index})已存在于该书籍({book.name})中, 将不会再次下载."
                )
                return True
        # 获取章节内容
        result_chapter_content: Tuple[bool, Chapter] = \
            self.__operate(chapter_url, self.__engine.get_chapter, self.__engine)
        if not result_chapter_content[0]:
            return False
        #设置章节数据
        chapter = result_chapter_content[1]
        chapter.index = index
        chapter.book_name = book.name
        # 检查章节的内容是否过短
        if chapter.word_count <= 200:
            self.__logger.warning(
                f"该章节({chapter.name})内容过短: {chapter.text[:20].replace('\n', '')}..."
            )
            self.__error_callback(Exception(f"章节内容过短: {chapter.text[:20]}..."))
        # 向书籍中加入章节
        book.append(chapter)
        # 触发章节信息回调函数
        self.__chapter_info_callback(chapter)
        self.__logger.info(f"为书籍({book.name})下载了一个章节({chapter.name}).")
        # 向书架添加章节
        self.__book_shelf.add_chapters([(chapter, book)], Settings.FORCE_RELOAD)
        # 返回下载结果
        return True