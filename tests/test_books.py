#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: test_books.py
# @Time: 19/06/2024 10:55
# @Author: Amundsen Severus Rubeus Bjaaland


import os

from downloader.books import Chapter, Book


class TestConstant:
    def test_book_state(self):
        assert Book.BookState.transform(1) == Book.BookState.END
        assert Book.BookState.transform(2) == Book.BookState.SERIALIZING
        assert Book.BookState.transform(3) == Book.BookState.FORECAST
        assert Book.BookState.transform(4) == Book.BookState.BREAK
        assert Book.BookState.transform(5) == Book.BookState.SERIALIZING
        assert Book.BookState.END == ("完结", 1)
        assert Book.BookState.SERIALIZING == ("连载中", 2)
        assert Book.BookState.FORECAST == ("预告", 3)
        assert Book.BookState.BREAK == ("断更", 4)
        assert Book.BookState.STATE_LIST == (
            Book.BookState.END,
            Book.BookState.SERIALIZING,
            Book.BookState.FORECAST,
            Book.BookState.BREAK
        )

    def test_storage_method(self):
        assert Chapter.StorageMethod.transform(1) == \
            Chapter.StorageMethod.MEMORY
        assert Chapter.StorageMethod.transform(2) == \
            Chapter.StorageMethod.DISK
        assert Chapter.StorageMethod.transform(3) == \
            Chapter.StorageMethod.MEMORY
        assert Chapter.StorageMethod.MEMORY == ("内存", 1)
        assert Chapter.StorageMethod.DISK == ("磁盘", 2)
        assert Chapter.StorageMethod.METHOD_LIST == (
            Chapter.StorageMethod.MEMORY,
            Chapter.StorageMethod.DISK
        )


class TestObject:
    def test_chapter(self):
        test_chapter_1 = Chapter(
            "TestChapter1", 1, "http://example.com/", "TestBook",
            ("This is the first line.", "This is the second line.")
        )
        test_chapter_2 = Chapter(
            "TestChapter2", 2, "http://example.com/", "TestBook",
            ("This is the first line.", "This is the second line."),
            Chapter.StorageMethod.MEMORY
        )
        test_chapter_3 = Chapter(
            "TestChapter1", 1, "http://example.com/", "TestBook",
            ("This is the first line.", "This is the second line."),
            Chapter.StorageMethod.MEMORY
        )
        assert test_chapter_1.text == \
            "\tThis is the first line.\n\tThis is the second line."
        assert len(test_chapter_1) == 50
        assert str(test_chapter_1) == "第0001章 TestChapter1\n\t" \
            "This is the first line.\n\tThis is the second line.\n\n"
        assert test_chapter_1 == test_chapter_3
