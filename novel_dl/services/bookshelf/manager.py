#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: manager.py
# @Time: 13/03/2025 21:42
# @Author: Amundsen Severus Rubeus Bjaaland
"""manager.py
==========
该模块提供了 `Bookshelf` 类，用于管理书籍和章节的缓存信息，并与 SQLite 数据库交互。
类
---
Bookshelf
    书架对象，用于缓存已经下载过的书籍和章节信息，并提供保存和完善书籍信息的功能。
依赖
----
- 第三方库:
    - sqlalchemy: 用于数据库连接和 ORM 操作。
- 自定义库:
    - novel_dl.core.books: 提供 `Book` 和 `Chapter` 类。
    - novel_dl.core: 提供全局设置。
    - novel_dl.core.settings: 提供 `Settings` 类。
    - .model: 提供数据库模型类 `Chapters`, `Books`, `Base`, `BookCovers`, `Attechments`。
功能
----
- 初始化数据库连接并创建表。
- 保存书籍信息到数据库。
- 保存章节信息到数据库。
- 从数据库中完善书籍信息。
注意事项
--------
- 数据库路径由 `Settings().BOOKS_DB_PATH` 指定。
- 如果 `Settings().FORCE_RELOAD` 为 True, 则会强制重新加载书籍或章节信息。
"""


# 导入第三方库
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 导入自定义库
from novel_dl.core.books import Book, Chapter
from novel_dl.core import Settings
from novel_dl.core.settings import Settings
from .model import Chapters, Books, Base, BookCovers, Attechments


class Bookshelf(object):
    def __init__(self):
        """书架对象
        用于缓存已经下载过的书籍信息
        """
        # 初始化数据库连接
        self.__engine = create_engine(
            f"sqlite:///{Settings().BOOKS_DB_PATH}",
            connect_args={"check_same_thread": False}
        )
        # 创建表
        Base.metadata.create_all(self.__engine, checkfirst=True)
    
    def save_book_info(self, book: Book) -> None:
        """保存书籍信息
        
        :param book: 书籍对象
        :type book: Book
        """
        # 创建数据库会话
        with sessionmaker(bind=self.__engine)() as session:
            # 查询数据库中是否已经存在该书籍
            book_record = session.query(Books) \
                .filter_by(things_hash=book.hash).first()
            # 如果书籍不存在或者强制重新加载
            if (book_record is None) or Settings().FORCE_RELOAD:
                # 添加书籍信息以及封面信息
                session.add(Books.from_book(book))
                [session.add(i) for i in BookCovers.from_book(book)]
            # 如果书籍存在
            if book_record is not None:
                # 将该书籍的来源信息与数据库中已经存在的信息合并
                book_record.sources = list(
                    set(book_record.sources + list(book.sources))
                )
                # 更新数据库中的信息
                session.add(book_record)
            # 保存更改
            session.commit()
    
    def save_chapter_info(
        self, chapter: Chapter, book_hash: bytes
    ) -> None:
        """保存章节信息
        
        :param chapter: 章节对象
        :type chapter: Chapter
        :param book_hash: 书籍的hash值
        :type book_hash: bytes
        """
        # 创建数据库会话
        with sessionmaker(bind=self.__engine)() as session:
            # 查询数据库中是否已经存在该章节
            chapter_record = session.query(Chapters) \
                .filter_by(things_hash=chapter.hash).first()
            # 如果章节不存在或者强制重新加载
            if (chapter_record is None) or Settings().FORCE_RELOAD:
                # 添加章节信息以及附件信息
                session.add(Chapters.from_chapter(chapter, book_hash))
                [
                    session.add(i) for i in
                    Attechments.from_chapter(chapter)
                ]
            # 如果章节存在
            if chapter_record is not None:
                # 将该章节的来源信息与数据库中已经存在的信息合并
                chapter_record.sources = list(
                    set(chapter_record.sources + list(chapter.sources))
                )
                # 更新数据库中的信息
                session.add(chapter_record)
            # 保存更改
            session.commit()
    
    def complete_book(self, book: Book) -> Book:
        """完善书籍信息
        
        :param book: 书籍对象
        :type book: Book
        :return: 完善后的书籍对象
        :rtype: Book
        """
        # 创建数据库会话
        with sessionmaker(bind=self.__engine)() as session:
            # 获取数据库中该书籍的所有章节
            chapters = session.query(Chapters) \
                .filter_by(book_hash=book.hash).all()
            # 将数据库中的章节信息转换为章节对象并添加到书籍对象中
            for i in chapters:
                book.append(i.to_chapter())
        # 返回完善后的书籍对象
        return book