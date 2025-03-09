#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: manager.py
# @Time: 18/02/2025 18:16
# @Author: Amundsen Severus Rubeus Bjaaland


from urllib.parse import urlparse
from typing import List, Generator, Tuple, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from .engines import ENGINE_LIST
from .config import Operations, BookWeb
from novel_dl.utils.network import Network
from novel_dl.core import Settings, Book, Chapter


class WebManager(object):
    def __init__(self):
        self.__web_list: List[BookWeb] = []
        for i in ENGINE_LIST:
            self.append(i)
    
    def append(self, web: BookWeb) -> bool:
        assert isinstance(web, BookWeb)
        if (web.workable is False) or (web in self.__web_list):
            return False
        self.__web_list.append(web)
        return True
    
    def engines(self) -> Generator[BookWeb, None, None]:
        for web in self.__web_list:
            yield web
    
    def get_engine_by_name(self, name: str) -> BookWeb | None:
        for web in self.__web_list:
            if web.name == name:
                return web
        return None
    
    def get_engine_by_url(self, url: str) -> BookWeb | None:
        for web in self.__web_list:
            if urlparse(url).netloc in web.domains:
                return web
        return None
    
    def __operate(
        self, engine: BookWeb, url: str, operation: Operations, **kwargs
    ) -> Tuple[bool, Book | List[str] | Chapter | None]:
        assert isinstance(engine, BookWeb)
        assert isinstance(url, str)
        assert isinstance(operation, Operations)
        while True:
            try:
                network_obj = Network.get(url, engine.encoding)
            except Exception as network_error:
                if engine.is_protected(None, network_error, None):
                    engine.prevent_protected()
                    continue
                return False, None
            try:
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
                if engine.is_protected(
                    network_obj, None, analyze_error
                ):
                    engine.prevent_protected()
                    continue
                return False, None
            return True, result
    
    def __download_book_info(
        self, engine: BookWeb, url: str, book_middle_ware: \
        Callable[[Book], Book] = lambda x: x, chapters_middle_ware: \
        Callable[[List[Chapter]], List[Chapter]] = lambda x: x
    ) -> Tuple[Book, List[str]] | None:
        assert isinstance(engine, BookWeb)
        assert isinstance(url, str)
        book = self.__operate(engine, url, Operations.INFO)
        if book[0] == False:
            return None
        book = book[1]
        book = book_middle_ware(book)
        chapter_list = self.__operate(engine, url, Operations.URLS)
        if chapter_list[0] == False:
            return None
        chapter_list = chapter_list[1]
        if not Settings().FORCE_RELOAD:
            for i in book.chapters:
                for ii in i.sources:
                    chapter_list.remove(ii)
        chapter_list = chapters_middle_ware(chapter_list)
        
        return (book, chapter_list)
    
    def __download_chapter(
        self, engine: BookWeb, url: str, book: Book,
        chapter_list: List[str],
        chapter_middle_ware: Callable[[Chapter], Chapter] = lambda x: x
    ) -> Book:
        assert isinstance(engine, BookWeb)
        assert isinstance(url, str)
        assert isinstance(book, Book)
        assert isinstance(chapter_list, List)
        
        if Settings().MULTI_THREAD and engine.multi_thread:
            with ThreadPoolExecutor() as executor:
                future_to_url = {
                    executor.submit(
                        self.__operate, engine, chapter_url,
                        Operations.CHAPTER, index=index + 1,
                        book_name=book.name
                    ): chapter_url
                    for index, chapter_url in enumerate(chapter_list)
                }
                for future in as_completed(future_to_url):
                    chapter = future.result()
                    if chapter[0] == False:
                        continue
                    chapter = chapter[1]
                    chapter = chapter_middle_ware(chapter)
                    book.append(chapter)
        else:
            for index, chapter_url in enumerate(chapter_list):
                chapter = self.__operate(
                    engine, chapter_url, Operations.CHAPTER,
                    index=index + 1, book_name=book.name
                )
                if chapter[0] == False:
                    continue
                chapter = chapter[1]
                chapter = chapter_middle_ware(chapter)
                book.append(chapter)
        
        book.sort()
        return book
    
    def download(
        self, url: str, book_middle_ware: Callable[[Book], Book] = \
        lambda x: x, chapters_middle_ware: \
        Callable[[List[Chapter]], List[Chapter]] = lambda x: x,
        chapter_middle_ware: Callable[[Chapter], Chapter] = lambda x: x
    ) -> Book | None:
        assert isinstance(url, str)
        
        engine = self.get_engine_by_url(url)
        if engine is None:
            return None
        
        result = self.__download_book_info(
            engine, url, book_middle_ware, chapters_middle_ware
        )
        if result is None:
            return None
        book = result[0]
        chapter_list = result[1]
        
        return self.__download_chapter(
            engine, url, book, chapter_list, chapter_middle_ware
        )