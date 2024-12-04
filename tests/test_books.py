#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: test_books.py
# @Time: 19/06/2024 10:55
# @Author: Amundsen Severus Rubeus Bjaaland


import os

from downloader.books import Chapter, Book


class TestConstant:
    def test_book_state(self):
        assert Book.State.transform(1) == Book.State.END
        assert Book.State.transform(2) == Book.State.SERIALIZING
        assert Book.State.transform(3) == Book.State.FORECAST
        assert Book.State.transform(4) == Book.State.BREAK
        assert Book.State.transform(5) == Book.State.SERIALIZING
        assert Book.State.END == ("完结", 1)
        assert Book.State.SERIALIZING == ("连载中", 2)
        assert Book.State.FORECAST == ("预告", 3)
        assert Book.State.BREAK == ("断更", 4)
        assert Book.State.STATE_LIST == (
            Book.State.END,
            Book.State.SERIALIZING,
            Book.State.FORECAST,
            Book.State.BREAK
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

    def test_save_method(self):
        assert Book.SaveMethod.transform(1) == \
            Book.SaveMethod.TXT
        assert Book.SaveMethod.transform(2) == \
            Book.SaveMethod.EPUB
        assert Book.SaveMethod.transform(3) == \
            Book.SaveMethod.PDF
        assert Book.SaveMethod.TXT == ("txt文件", 1, "txt")
        assert Book.SaveMethod.EPUB == ("epub文件", 2, "epub")
        assert Book.SaveMethod.PDF == ("pdf文件", 3, "pdf")
        assert Book.SaveMethod.METHOD_LIST == (
            Book.SaveMethod.TXT,
            Book.SaveMethod.EPUB,
            Book.SaveMethod.PDF,
        )


class TestObject:
    def test_chapter(self):
        test_chapter_1 = Chapter(
            "TestChapter1", 1, "http://example.com/", "TestBook",
            ("This is the first line.", "This is the second line.")
        )
        test_chapter_3 = Chapter(
            "TestChapter1", 1, "http://example.com/", "TestBook",
            ("This is the first line.", "This is the second line."),
            Chapter.StorageMethod.DISK
        )

        assert test_chapter_1.content == \
            "\tThis is the first line.\n\tThis is the second line."
        assert len(test_chapter_1) == 50
        assert str(test_chapter_1) == "第0001章 TestChapter1\n\t" \
            "This is the first line.\n\tThis is the second line.\n\n"
        assert test_chapter_1 == test_chapter_3

        test_chapter_1.content = [
            "This is the first line.", "This is the second line.",
            "This is the third line."
        ]
        test_chapter_3.content = [
            "This is the first line.", "This is the second line.",
            "This is the third line."
        ]
        assert len(test_chapter_1) == 75
        assert len(test_chapter_3) == 75

    def test_book(self):
        test_chapter_1 = Chapter(
            "TestChapter1", 1, "http://example.com/", "TestBook",
            ("This is the first line.", "This is the second line.")
        )
        test_chapter_2 = Chapter(
            "TestChapter2", 2, "http://example.com/", "TestBook",
            ("This is the first line.", "This is the second line."),
            Chapter.StorageMethod.DISK
        )
        test_book_1 = Book(
            "TestBook", "TestAuthor", Book.State.END,
            "https://example.com/1/", "TestDescription_1"
        )
        test_book_2 = Book(
            "TestBook", "TestAuthor", Book.State.SERIALIZING,
            "https://example.com/2/", "TestDescription_2"
        )
        test_book_1.append(test_chapter_1)
        test_book_1.append(test_chapter_2)

        assert len(test_book_1) == 2
        assert len(test_book_2) == 0
        assert test_book_1 == test_book_2
        assert test_book_1.index_list == [1, 2]
        assert list(test_book_1.chapter_list) == \
            [test_chapter_1, test_chapter_2]

    def test_book_save(self):
        with open("./tests/book.jpg", "rb") as pic_file:
            pic = pic_file.read()

        test_book_1 = Book(
            "TestBook", "TestAuthor", Book.State.END,
            "https://example.com/1/", "TestDescription_1", pic
        )
        test_chapter_1 = Chapter(
            "TestChapter1", 1, "http://example.com/", "TestBook",
            ("This is the first line.", "This is the second line.")
        )
        test_chapter_2 = Chapter(
            "TestChapter2", 2, "http://example.com/", "TestBook",
            ("This is the first line.", "This is the second line."),
            Chapter.StorageMethod.DISK
        )
        test_book_1.append(test_chapter_1)
        test_book_1.append(test_chapter_2)

        test_book_1.save(Book.SaveMethod.TXT)
        test_book_1.save(Book.SaveMethod.EPUB)
