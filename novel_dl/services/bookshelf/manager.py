#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: manager.py
# @Time: 13/03/2025 21:42
# @Author: Amundsen Severus Rubeus Bjaaland


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from novel_dl.core.books import Book, Chapter
from novel_dl.core import Settings
from novel_dl.core.settings import Settings

from .model import Chapters, Books, Base, BookCovers, Attechments


class Bookshelf(object):
    def __init__(self):
        self.__engine = create_engine(
            f"sqlite:///{Settings().BOOKS_DB_PATH}",
            connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(self.__engine, checkfirst=True)
    
    def save_book_info(self, book: Book):
        with sessionmaker(bind=self.__engine)() as session:
            book_record = session.query(Books) \
                .filter_by(things_hash=book.hash).first()
            if (book_record is None) or Settings().FORCE_RELOAD:
                session.add(Books.from_book(book))
                [session.add(i) for i in BookCovers.from_book(book)]
            if book_record is not None:
                book_record.sources = list(
                    set(book_record.sources + list(book.sources))
                )
                session.add(book_record)
            session.commit()
    
    def save_chapter_info(self, chapter: Chapter, book_hash: bytes):
        with sessionmaker(bind=self.__engine)() as session:
            chapter_record = session.query(Chapters) \
                .filter_by(things_hash=chapter.hash).first()
            if (chapter_record is None) or Settings().FORCE_RELOAD:
                session.add(Chapters.from_chapter(chapter, book_hash))
                [
                    session.add(i) for i in
                    Attechments.from_chapter(chapter)
                ]
            if chapter_record is not None:
                chapter_record.sources = list(
                    set(chapter_record.sources + list(chapter.sources))
                )
                session.add(chapter_record)
            session.commit()
    
    def complete_book(self, book: Book):
        with sessionmaker(bind=self.__engine)() as session:
            chapters = session.query(Chapters) \
                .filter_by(book_hash=book.hash).all()
            for i in chapters:
                book.append(i.to_chapter())
        return book