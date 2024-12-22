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
from .logs import Logger
from .settings import Settings
from .books import Book, Chapter
from .tools import mkdir, str_hash, SQLManager

# 防止 jieba 库输出调试信息到控制台中
jieba.setLogLevel(logging.INFO)


class BookShelf(object):
    # 使用枚举形式定义可操作的数据库表, 实际的表名是字符串变量内容的大写形式
    BOOKS = "Books"  # 书籍表
    SOURCES = "Sources"  # 来源表(只包括书籍的来源)
    TOKENS = "Tokens"  # 书籍名称的分词表
    CHAPTERS = "Chapters"  # 章节表
    
    # 定义书架对象中的 SQL 语句
    # 用于查询数据库中的所有表, 确认是否已经创建了需要的表
    SELECT_TABLE = "SELECT name FROM sqlite_master WHERE type = 'table'"
    # 用于查询书籍的来源, 一本书籍可能有多个来源
    SELECT_SOURCE = "SELECT SOURCE FROM SOURCES WHERE BOOK_HASH=?"
    # 用于创建数据库中的表
    CREATE_TABLES = {
        BOOKS: """CREATE TABLE BOOKS(
            HASH   INTEGER NOT NULL PRIMARY KEY,
            NAME   TEXT    NOT NULL,
            AUTHOR TEXT    NOT NULL,
            STATE  INTEGER NOT NULL CHECK (STATE=1 OR STATE=2 OR STATE=3 OR STATE=4),
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
            PRIMARY KEY(HASH,BOOK_HASH))""",
        CHAPTERS: """CREATE TABLE CHAPTERS(
            HASH              INTEGER NOT NULL PRIMARY KEY,
            BOOK_HASH         INTEGER NOT NULL,
            NAME              TEXT    NOT NULL,
            CHAPTER_INDEX     INTEGER NOT NULL,
            CONTENT           TEXT    NOT NULL)"""
    }
    # 用于查询数据库中的相关数据
    SELECT_TABLES = {
        BOOKS: "SELECT * FROM BOOKS WHERE HASH=?",
        SOURCES: "SELECT * FROM SOURCES WHERE WEB_HASH=? AND BOOK_HASH=?",
        TOKENS: "SELECT * FROM TOKENS WHERE HASH=? AND BOOK_HASH=?",
        CHAPTERS: "SELECT * FROM CHAPTERS WHERE HASH=?"
    }
    # 用于向数据库中插入数据
    INSERT_TABLES = {
        BOOKS: "INSERT INTO BOOKS VALUES (?,?,?,?,?,?,?)",
        SOURCES: """INSERT INTO SOURCES VALUES (?,?,?)""",
        TOKENS: """INSERT INTO TOKENS VALUES (?,?)""",
        CHAPTERS: "INSERT INTO CHAPTERS VALUES (?,?,?,?,?)"
    }
    # 用于更新数据库中的数据
    UPDATE_TABLES = {
        BOOKS: """UPDATE BOOKS SET
            HASH=?,NAME=?,AUTHOR=?,STATE=?,DESC=?,COVER=?,OTHER=? WHERE HASH=?""",
        SOURCES: """UPDATE SOURCES SET
            WEB_HASH=?,BOOK_HASH=?,SOURCE=? WHERE WEB_HASH=? AND BOOK_HASH=?""",
        TOKENS: """UPDATE TOKENS SET
            HASH=?,BOOK_HASH=? WHERE HASH=? AND BOOK_HASH=?""",
        CHAPTERS: """UPDATE CHAPTERS SET
            HASH=?,BOOK_HASH=?,NAME=?,CHAPTER_INDEX=?,CONTENT=? WHERE HASH=?""",
    }
    
    def __init__(self):
        """书架对象, 用于管理下载过的书籍和预载入信息的书籍
        
        Example:
			>>> bs = BookShelf()
        """
        # 尝试创建所有需要的文件夹
        mkdir(Settings.DATA_DIR)
        mkdir(Settings.BOOKS_DIR)
        # 创建日志记录器
        self.__logger = Logger()
        # 依据程序设置合成数据库文件的路径
        self.DB_PATH: str = os.path.join(Settings.BOOKS_DIR, "bookshelf.db")
        # 创建数据库管理器
        self.__sql_manager = SQLManager(Settings.BOOKS_DB_PATH, False)
        # 创建数据库中的表
        self.__create_tables()
    
    def __create_tables(self) -> None:
        with self.__sql_manager as cursor:
            # 查询数据库中的所有表
            result = cursor.execute(self.SELECT_TABLE).fetchall()
            # 将查询结果转换为列表, 原结果中的元素为一个只有一个元素的元组
            result = [i[0] for i in result]
            # 检查是否已经创建了需要的表, 若没有则创建
            for key, item in self.CREATE_TABLES.items():
                if key.upper() not in result:  # 注意应该使用大写形式进行比较
                    cursor.execute(item)
        # 函数返回 None
        return None
    
    def __transform_books(self, cursor: sqlite3.Cursor) -> Iterator[Book]:
        while True:
            # 从数据库中获取一条数据
            data = cursor.fetchone()
            # 若数据为空则退出函数
            if data is None:
                break
            # 使用数据创建一个书籍对象, 注意书籍对象中不包含额外信息
            book = Book(
                data[1], data[2], "",
                Book.State.transform(data[3]),
                data[4], data[5]
            )
            # 将额外信息加入书籍对象中, 额外信息使用 JSON 格式存储
            for key, item in json.loads(data[6]).items():
                book.set_other_data(key, item)
            # 返回书籍对象
            yield book
    
    def __add(
        self, target: str, select_conditions: tuple,
        data: tuple, force_reload: bool = False
    ):
        with self.__sql_manager as cursor:
            # 查询数据库中是否已经存在了需要添加的数据
            result = cursor.execute(
                self.SELECT_TABLES[target], select_conditions
            ).fetchall()
            # 若数据库中不存在需要添加的数据则添加
            if not result:
                cursor.execute(self.INSERT_TABLES[target], data)
            # 若数据库中存在需要添加的数据且需要强制覆盖则覆盖
            if result and force_reload:
                cursor.execute(
                    self.UPDATE_TABLES[target],
                    (*data, *select_conditions)
                )
    
    def add_books(
        self, data: Iterable[Tuple[Book, int]],
        force_reload: bool = False
    ):
        """将书籍添加到书架中
        
        :param data: 一个可迭代对象, 其中的元素为一个元组,
        	元组中的第一个元素为书籍对象, 第二个元素为书籍对应引擎的 hash 值
        :type data: Iterable[Tuple[Book, int]]
        :param force_reload: 是否强制覆盖已存在的书籍
        :type force_reload: bool
        """
        # 依次处理所有书籍
        for one_book, web_hash in data:
            # 计算书籍的哈希值
            book_hash = hash(one_book)
            # 将书籍添加到数据库中
            self.__add(
                self.BOOKS, (book_hash,),
                (
                    book_hash, one_book.name, one_book.author,
                    one_book.state.value[1], one_book.desc,
                    one_book.cover_image, json.dumps(one_book.other_data)
                ),
                force_reload
            )
            # 将书籍的来源添加到数据库中
            self.__add(
                self.SOURCES, (web_hash, book_hash),
                (web_hash, book_hash, one_book.source),
                force_reload
            )
            # 将书籍的名称进行分词
            token_list = jieba.lcut_for_search(one_book.name)
            # 一次处理每一个词
            for one_token in token_list:
                # 计算词的哈希值
                token_hash = str_hash(one_token)
                # 将词添加到数据库中
                self.__add(
                    self.TOKENS, (token_hash, book_hash),
                    (token_hash, book_hash), force_reload
                )
            # 记录日志
            self.__logger.info(
                f"成功将书籍({one_book.name})添加到书架中." \
                f"(若已存在则{'' if force_reload else '不'}覆盖)"
            )
            # FIXME 日志打印了两次
    
    def search_books_by_name(
        self, name: str
    ) -> Iterator[Tuple[Book, List[str]]]:
        """通过书籍名称搜索书籍
        
        :param name: 书籍名称
        :type name: str
        :return: 一个迭代器, 其中的元素为一个元组, 元组的第一个元素为书籍对象,
        	第二个元素为书籍的来源, 是一个包含字符串的列表.
        """
        with self.__sql_manager as cursor:
            # 将书籍名称进行分词
            token_list = jieba.lcut_for_search(name)
            # 创建一个缓冲区, 用于存储查询结果
            buffer: List[set] = []
            # 依次处理每一个词
            for one_token in token_list:
                # 计算词的哈希值
                token_hash = str_hash(one_token)
                # 依据词的哈希值查询名称中含有该词的书籍的 hash 值
                result = cursor.execute(
                    "SELECT BOOK_HASH FROM TOKENS WHERE HASH=?", [token_hash]
                ).fetchall()
                # 将查询结果转换为列表
                # 注意这里的每一个查询结果是一个只有一个元素的元组
                result = [i[0] for i in result]
                # 将查询结果添加到缓冲区中
                buffer.append(set(result))
            # 将缓冲区中的查询结果取交集, 得到最终的查询结果
            book_hash_list = list(reduce(lambda x, y: x & y, buffer))
            # 若查询结果为空则返回空列表
            if not book_hash_list:
                # 查询结果为空时应当发出警告
                self.__logger.warning(f"未找到匹配的书籍({name})")
                return []
            # 依次处理每一个查询结果
            for one_book_hash in book_hash_list:
                # 依据书籍的哈希值查询书籍的详细信息
                result = cursor.execute(
                    "SELECT * FROM BOOKS WHERE HASH=?", [one_book_hash]
                )
                # 依据查询结果创建书籍对象
                for i in self.__transform_books(result):
                    # 依据书籍的哈希值查询书籍的来源
                    cursor.execute(self.SELECT_SOURCE, [hash(i)])
                    # 将查询结果转换为列表
                    book_sources = [i[0] for i in cursor.fetchall()]
                    # 返回书籍对象和书籍的来源
                    yield (i, book_sources)
    
    def search_books_by_author(
        self, author: str
    ) -> Iterator[Tuple[Book, List[str]]]:
        """通过作者搜索书籍
        
        :param author: 作者
        :type author: str
        :return: 一个迭代器, 其中的元素为一个元组, 元组的第一个元素为书籍对象,
			第二个元素为书籍的来源, 是一个包含字符串的列表.
        """
        with self.__sql_manager as cursor:
            # 依据作者查询书籍的详细信息
            result = cursor.execute(
                "SELECT * FROM BOOKS WHERE AUTHOR=?", [author]
            )
            # 依据查询结果创建书籍对象
            for i in self.__transform_books(result):
                # 依据书籍的哈希值查询书籍的来源
                cursor.execute(self.SELECT_SOURCE, [hash(i)])
                # 将查询结果转换为列表
                # 注意这里的每一个查询结果是一个只有一个元素的元组
                book_sources = [i[0] for i in cursor.fetchall()]
                # 返回书籍对象和书籍的来源
                yield (i, book_sources)
    
    def search_books_by_web(
        self, web_hash: int
    ) -> Iterator[Tuple[Book, List[str]]]:
        """查询书籍引擎下的所有书籍
        
        :param web_hash: 书籍引擎的哈希值
        :type web_hash: int
        :return: 一个迭代器, 其中的元素为一个元组, 元组的第一个元素为书籍对象,
			第二个元素为书籍的来源, 是一个包含字符串的列表.
        """
        with self.__sql_manager as cursor:
            # 依据书籍引擎的哈希值查询书籍的详细信息
            result = cursor.execute(
                """SELECT * FROM BOOKS WHERE HASH IN 
                (SELECT BOOK_HASH FROM SOURCES WHERE WEB_HASH=?)""",
                [web_hash]
            )
            # 依据查询结果创建书籍对象
            for i in self.__transform_books(result):
                # 依据书籍的哈希值查询书籍的来源
                cursor.execute(self.SELECT_SOURCE, [hash(i)])
				# 将查询结果转换为列表
				# 注意这里的每一个查询结果是一个只有一个元素的元组
                book_sources = [i[0] for i in cursor.fetchall()]
                # 返回书籍对象和书籍的来源
                yield (i, book_sources)
    
    def add_chapters(
        self, chapters: Iterable[Tuple[Chapter, Book]],
        force_reload: bool = False
    ) -> None:
        """将章节添加到书籍中
        
        :param chapters: 一个可迭代对象, 其中的元素为一个元组,
			元组中的第一个元素为章节对象, 第二个元素为对应的书籍对象.
		:type chapters: Iterable[Tuple[Chapter, Book]]
		:param force_reload: 是否强制覆盖已存在的章节
		:type force_reload: bool
        """
        # 依次处理所有章节
        for one_chapter, one_book in chapters:
            # 确认章节所属的书籍名和书籍对象的名字相同
            if one_book.name != one_chapter.book_name:
                continue
            # 将章节添加到数据库中
            self.__add(
                self.CHAPTERS, (hash(one_chapter),),
                (
                    hash(one_chapter), hash(one_book), 
                    one_chapter.name, one_chapter.index, 
                    "\n\t".join(one_chapter.content)
                ),
                force_reload
            )
            # 记录日志
            self.__logger.info(
				f"成功将章节({one_chapter.name})添加到书籍({one_book.name})中." \
        		f"(若已存在则{'' if force_reload else '不'}覆盖)"
			)
    
    def complete_book(self, book: Book) -> Book:
        """将书籍的章节添加到书籍对象中
        
        :param book: 书籍对象
        :type book: Book
        :return: 完整的书籍对象
        """
        with self.__sql_manager as cursor:
			# 依据书籍的哈希值查询书籍的章节
            result = cursor.execute(
                "SELECT * FROM CHAPTERS WHERE BOOK_HASH=?", [hash(book)]
            ).fetchall()
            # 创建一个计数器, 用于记录添加的章节数
            counter = 0
            # 依据查询结果创建章节对象
            for data in result:
                # 将章节对象添加到书籍对象中
                book.append(
                    Chapter(
                        data[2], data[3], "", book.name, data[4].split("\n\t")
                    )
                )
                # 计数器加一
                counter += 1
        self.__logger.info(
            f"成功将书籍({book.name})的章节添加到书籍对象中, 共添加了{counter}章."
        )
        # 返回完整的书籍对象
        return book