#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: bookshelf.py
# @Time: 25/11/2024 17:38
# @Author: Amundsen Severus Rubeus Bjaaland
"""书架模块, 用于管理下载过的书籍和预载入信息的书籍"""


# 导入标准库
import os
import json
import logging
import sqlite3
from functools import reduce
from typing import Iterable, Iterator, List, Tuple

# 导入第三方库
import jieba

# 导入自定义库
from .settings import Settings
from .books import Book, Chapter
from .tools import mkdir, str_hash, SQLManager

# 防止 jieba 库输出调试信息到控制台中
jieba.setLogLevel(logging.INFO)

# 提取必要的设置作为模块的全局设置
_DATA_DIR = Settings.DATA_DIR
_BOOKS_DIR = Settings.BOOKS_DIR
_BOOKS_DB_PATH = Settings.BOOKS_DB_PATH
# 尝试创建所有需要的文件夹
REQUIRED_DIRS = [_DATA_DIR, _BOOKS_DIR]
[mkdir(i) for i in REQUIRED_DIRS]


class BookShelf(object):
    BOOKS = "Books"
    CHAPTERS = "Chapters"
    SOURCES = "Sources"
    TOKENS = "Tokens"
    
    DB_PATH: str = os.path.join(_BOOKS_DIR, "bookshelf.db")
    
    SELECT_TABLE = "SELECT name FROM sqlite_master WHERE type = 'table'"
    SELECT_SOURCE = "SELECT SOURCE FROM SOURCES WHERE BOOK_HASH=?"
    CREATE_TABLES = {
        CHAPTERS: """CREATE TABLE CHAPTERS(
        HASH              INTEGER NOT NULL PRIMARY KEY,
        BOOK_HASH         INTEGER NOT NULL,
        NAME              TEXT    NOT NULL,
        CHAPTER_INDEX     INTEGER NOT NULL,
        CONTENT           TEXT    NOT NULL)""",
        BOOKS: """CREATE TABLE BOOKS(
        HASH   INTEGER NOT NULL PRIMARY KEY,
        NAME   TEXT    NOT NULL,
        AUTHOR TEXT    NOT NULL,
        STATE  INTEGER NOT NULL,
        DESC   TEXT    NOT NULL,
        COVER  BLOB    NOT NULL,
        OTHER  TEXT    NOT NULL)""",
        SOURCES: """CREATE TABLE SOURCES(
        WEB_HASH  INTEGER NOT NULL,
        BOOK_HASH INTEGER NOT NULL,
        SOURCE    TEXT    NOT NULL UNIQUE,
        PRIMARY KEY(WEB_HASH,BOOK_HASH))""",
        TOKENS: """CREATE TABLE TOKENS(
        HASH      BLOB    NOT NULL,
        BOOK_HASH INTEGER NOT NULL,
        PRIMARY KEY(HASH,BOOK_HASH))"""
    }
    INSERT_TABLES = {
        CHAPTERS: """INSERT INTO CHAPTERS (HASH,BOOK_HASH,NAME,CHAPTER_INDEX,CONTENT) 
        SELECT ?,?,?,?,? WHERE NOT EXISTS 
        (SELECT * FROM CHAPTERS WHERE HASH=?)""",
        BOOKS: """INSERT INTO BOOKS (HASH,NAME,AUTHOR,STATE,DESC,COVER,OTHER) 
        SELECT ?,?,?,?,?,?,? WHERE NOT EXISTS
        (SELECT * FROM BOOKS WHERE HASH=?)""",
        SOURCES: """INSERT INTO SOURCES (WEB_HASH,BOOK_HASH,SOURCE) 
        SELECT ?,?,? WHERE NOT EXISTS
        (SELECT * FROM SOURCES WHERE WEB_HASH=? AND BOOK_HASH=?)""",
        TOKENS: """INSERT INTO TOKENS (HASH,BOOK_HASH) 
        SELECT ?,? WHERE NOT EXISTS
        (SELECT * FROM TOKENS WHERE HASH=? AND BOOK_HASH=?)"""
    }
    
    def __init__(self):
        self.__sql_manager = SQLManager(_BOOKS_DB_PATH)
        self.__create_tables()
    
    def __create_tables(self) -> None:
        with self.__sql_manager as cursor:
            result = cursor.execute(self.SELECT_TABLE).fetchall()
            result = [i[0] for i in result]
            for key, item in self.CREATE_TABLES.items():
                if key.upper() not in result:
                    cursor.execute(item)
        return None
    
    def __transform_books(self, cursor: sqlite3.Cursor) -> Iterator[Book]:
        while True:
            data = cursor.fetchone()
            if data is None:
                break
            book = Book(data[1], data[2], "", Book.State.transform(data[3]), data[4], data[5])
            for key, item in json.loads(data[6]).items():
                book.set_other_data(key, item)
            yield book
    
    def add_books(self, data: Iterable[Tuple[Book, int]]):
        with self.__sql_manager as cursor:
            for one_book, web_hash in data:
                book_hash = hash(one_book)
                cursor.execute(
                    self.INSERT_TABLES[self.BOOKS],
                    [
                        book_hash, one_book.name, one_book.author,
                        one_book.state.value[1], one_book.desc,
                        one_book.cover_image, json.dumps(one_book.other_data), book_hash
                    ]
                )
                cursor.execute(
                    self.INSERT_TABLES[self.SOURCES],
                    [web_hash, book_hash, one_book.source, web_hash, book_hash]
                )
                
                token_list = jieba.lcut_for_search(one_book.name)
                for one_token in token_list:
                    token_hash = str_hash(one_token)
                    cursor.execute(
                        self.INSERT_TABLES[self.TOKENS],
                          [token_hash, book_hash, token_hash, book_hash]
                    )
    
    def search_books_by_name(self, name: str) -> Iterator[Tuple[Book, List[str]]]:
        with self.__sql_manager as cursor:
            token_list = jieba.lcut_for_search(name)
            buffer: List[set] = []
            for one_token in token_list:
                token_hash = str_hash(one_token)
                result = cursor.execute(
                    "SELECT BOOK_HASH FROM TOKENS WHERE HASH=?", [token_hash]
                ).fetchall()
                result = [i[0] for i in result]
                buffer.append(set(result))
            book_hash_list = list(reduce(lambda x, y: x & y, buffer))
            for one_book_hash in book_hash_list:
                result = cursor.execute("SELECT * FROM BOOKS WHERE HASH=?", [one_book_hash])
                for i in self.__transform_books(result):
                    cursor.execute(self.SELECT_SOURCE, [hash(i)])
                    book_sources = [i[0] for i in cursor.fetchall()]
                    yield (i, book_sources)
    
    def search_books_by_author(self, author: str) -> Iterator[Tuple[Book, List[str]]]:
        with self.__sql_manager as cursor:
            result = cursor.execute("SELECT * FROM BOOKS WHERE AUTHOR=?", [author])
            for i in self.__transform_books(result):
                cursor.execute(self.SELECT_SOURCE, [hash(i)])
                book_sources = [i[0] for i in cursor.fetchall()]
                yield (i, book_sources)
    
    def search_books_by_web(self, web_hash: int) -> Iterator[Tuple[Book, List[str]]]:
        with self.__sql_manager as cursor:
            result = cursor.execute(
                """SELECT * FROM BOOKS WHERE HASH IN 
                (SELECT BOOK_HASH FROM SOURCES WHERE WEB_HASH=?)""",
                [web_hash]
            )
            for i in self.__transform_books(result):
                cursor.execute(self.SELECT_SOURCE, [hash(i)])
                book_sources = [i[0] for i in cursor.fetchall()]
                yield (i, book_sources)
    
    def add_chapters(self, chapters: Iterable[Tuple[Chapter, Book]]):
        with self.__sql_manager as cursor:
            for one_chapter, one_book in chapters:
                if one_book.name != one_chapter.book_name:
                    continue
                cursor.execute(
                    self.INSERT_TABLES[self.CHAPTERS],
                    [
                        hash(one_chapter), hash(one_book), 
                        one_chapter.name, one_chapter.index, 
                        "\n\t".join(one_chapter.content), hash(one_chapter)
                    ]
                )
    
    def complete_book(self, book: Book) -> Book:
        with self.__sql_manager as cursor:
            result = cursor.execute(
                "SELECT * FROM CHAPTERS WHERE BOOK_HASH=?", [hash(book)]
            ).fetchall()
            for data in result:
                book.append(
                    Chapter(
                        data[2], data[3], "", book.name, data[4].split("\n\t")
                    )
                )
        return book