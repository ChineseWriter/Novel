#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: manager.py
# @Time: 17/03/2025 16:59
# @Author: Amundsen Severus Rubeus Bjaaland


import re
import os
import time
import random
from threading import Thread
from urllib.parse import urlparse, urlunparse
from typing import Iterable, Generator, Callable, List, Dict

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from novel_dl.core.books import Book
from novel_dl.utils.network import Network
from novel_dl.core.settings import Settings
from novel_dl.services.bookshelf import Bookshelf
from novel_dl.services.download import BookWeb
from novel_dl.services.download import WebManager
from novel_dl.utils.options import hash as _hash

from .model import URL, Base


class URLFilter(object):
    def __init__(self, engine: BookWeb):
        db_path = os.path.join(
            Settings().URLS_DIR, f'{engine.domains[0]}.db'
        )
        
        self.__book_engine = engine
        self.__sql_engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False}
        )
    
    def add_urls(self, urls: Iterable[str]) -> None:
        with sessionmaker(bind=self.__sql_engine)() as session:
            for one_url in urls:
                url_record = session.query(URL) \
                    .filter_by(thing_hash=_hash(one_url)).first()
                if not url_record:
                    is_book = False
                    is_chapter = False
                    if re.match(
                        self.__book_engine.book_url_pattern, one_url
                    ):
                        is_book = True
                    if re.match(
                        self.__book_engine.chapter_url_pattern, one_url
                    ):
                        is_chapter = True
                    session.add(
                        URL(
                            thing_hash=_hash(one_url),
                            is_book=is_book, is_chapter=is_chapter
                        )
                    )
            session.commit()
    
    def mark_url(self, url: str, is_404: bool = False) -> None:
        with sessionmaker(bind=self.__sql_engine)() as session:
            url_record = session.query(URL) \
                .filter_by(thing_hash=_hash(url)).first()
            if url_record:
                url_record.visited = 1
                url_record.is_404 = 1 if is_404 else 0
            session.commit()
    
    def rm_urls(
        self, urls: Iterable[str]
    ) -> Generator[str, None, None]:
        with sessionmaker(bind=self.__sql_engine)() as session:
            for one_url in urls:
                url_record = session.query(URL) \
                    .filter_by(thing_hash=_hash(one_url)).first()
                if url_record:
                    if url_record.visited:
                        continue
                    else:
                        yield one_url


class PreStore(object):
    def __init__(
        self, engines: Iterable[BookWeb],
        url_info_callback: Callable[[str, BookWeb], None],
        book_info_callback: Callable[[Book, BookWeb], None],
        error_callback: Callable[[Exception, BookWeb], None],
    ):
        for i in engines:
            assert isinstance(i, BookWeb)
        self.__engines = {i: URLFilter(i) for i in engines}
        
        self.__book_shelf = Bookshelf()
        
        self.__url_info_callback = url_info_callback
        self.__book_info_callback = book_info_callback
        self.__error_callback = error_callback
        
        self.__stop_flag = False
        self.__pause_flag = False
        
        self.__thread_pool: Dict[BookWeb, Thread] = {}
        for i in engines:
            one_thread = Thread(
                target=self.__run, args=(i,),
                name=f"网站{i.name}预下载线程"
            )
            one_thread.start()
            self.__thread_pool[i] = one_thread
    
    def stop(self) -> None:
        self.__stop_flag = True
    
    def pause(self) -> None:
        self.__pause_flag = True
    
    def resume(self) -> None:
        self.__pause_flag = False
    
    def join(self) -> None:
        for i in self.__thread_pool.values():
            i.join()
    
    def __run(self, engine: BookWeb) -> None:
        next_url = f"https://{engine.domains[-1]}/"
        while True:
            if self.__stop_flag:
                break
            if self.__pause_flag:
                time.sleep(1)
                continue
            try:
                response = Network.get(
                    next_url, engine.encoding, False
                )
            except Exception as network_error:
                self.__error_callback(network_error, engine)
                time.sleep(5)
            else:
                next_url = self.__deal_url(response, engine)
                self.__url_info_callback(next_url, engine)
    
    def __deal_url(self, response: Network, engine: BookWeb) -> str:
        if not self.__check_status_code(response, engine):
            return f"https://{engine.domains[-1]}/"
        urls = self.__get_urls(response, engine)
        next_url = self.__get_next_url(urls, engine)
        path = urlparse(response.response.url).path
        self.__engines[engine].mark_url(response.response.url)
        if re.match(engine.book_url_pattern, path):
            book = WebManager().download(response.response.url, True)
            self.__book_shelf.save_book_info(book)
            self.__book_info_callback(book, engine)
        return next_url

    def __get_urls(
        self, response: Network, engine: BookWeb
    ) -> List[str]:
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
        self.__url_filters[engine].add_urls(urls)
        # 返回 URL 列表
        return urls

    def __get_next_url(self, urls: List[str], engine: BookWeb) -> str:
        if not urls:
            return f"https://{engine.domains[-1]}/"
        not_visited_urls = list(
            self.__url_filters[engine].rm_urls(urls)
        )
        if not_visited_urls:
            next_url = random.choice(not_visited_urls)
        else:
            next_url = random.choice(urls)
        return urlunparse(
            ["https", engine.domains[-1], next_url, "", "", ""]
        )