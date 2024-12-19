#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: test_books.py
# @Time: 19/06/2024 10:55
# @Author: Amundsen Severus Rubeus Bjaaland


import os

from novel_dl.books import Chapter, Book


class TestConstant:
    def test_storage_method(self):
        assert Chapter.StorageMethod.MEMORY.value == ("内存", 1)
        assert Chapter.StorageMethod.DISK.value == ("磁盘", 2)
        assert Chapter.StorageMethod.transform(1) == \
            Chapter.StorageMethod.MEMORY
        assert Chapter.StorageMethod.transform(2) == \
            Chapter.StorageMethod.DISK
        assert Chapter.StorageMethod.transform(3) == \
            Chapter.StorageMethod.MEMORY
        assert tuple(Chapter.StorageMethod) == (
            Chapter.StorageMethod.MEMORY,
            Chapter.StorageMethod.DISK
        )
        
    def test_book_state(self):
        assert Book.State.END.value == ("完结", 1)
        assert Book.State.SERIALIZING.value == ("连载中", 2)
        assert Book.State.BREAK.value == ("断更", 3)
        assert Book.State.transform(1) == Book.State.END
        assert Book.State.transform(2) == Book.State.SERIALIZING
        assert Book.State.transform(3) == Book.State.BREAK
        assert Book.State.transform(4) == Book.State.SERIALIZING
        assert tuple(Book.State) == (
            Book.State.END,
            Book.State.SERIALIZING,
            Book.State.BREAK
        )

    def test_save_method(self):
        assert Book.SaveMethod.EPUB.value == ("epub文件", 1, "epub")
        assert Book.SaveMethod.TXT.value == ("txt文件", 2, "txt")
        assert Book.SaveMethod.PDF.value == ("pdf文件", 3, "pdf")
        assert Book.SaveMethod.transform(1) == \
            Book.SaveMethod.EPUB
        assert Book.SaveMethod.transform(2) == \
            Book.SaveMethod.TXT
        assert Book.SaveMethod.transform(3) == \
            Book.SaveMethod.PDF
        assert Book.SaveMethod.transform(4) == \
            Book.SaveMethod.EPUB
        assert tuple(Book.SaveMethod) == (
            Book.SaveMethod.EPUB,
            Book.SaveMethod.TXT,
            Book.SaveMethod.PDF
        )


class TestObject:
    def test_chapter(self):
        test_chapter_1 = Chapter(
            "TestChapter1", 1, "http://example.com/", "TestBook",
            ("This is the first line.", "This is the second line.")
        )
        test_chapter_2 = Chapter(
            "TestChapter1", 1, "http://example.com/", "TestBook",
            ("This is the first line.", "This is the second line."),
            Chapter.StorageMethod.DISK
        )

        assert test_chapter_1.name == "TestChapter1"
        assert test_chapter_1.index == 1
        assert test_chapter_1.source == "http://example.com/"
        assert test_chapter_1.book_name == "TestBook"
        assert test_chapter_1.content == \
            ("This is the first line.", "This is the second line.")
        assert test_chapter_1.word_count == 47
        assert test_chapter_1.str_index == "00001"
        assert test_chapter_1.text == "\tThis is the first line.\n\tThis is the second line."
        assert str(test_chapter_1) == "第00001章 TestChapter1\n\t" \
            "This is the first line.\n\tThis is the second line.\n\n"
        assert len(test_chapter_1) == 50
        assert test_chapter_1 == test_chapter_2

        test_chapter_1.content = [
            "This is the first line.", "This is the second line.",
            "This is the third line."
        ]
        test_chapter_2.content = [
            "This is the first line.", "This is the second line.",
            "This is the third line."
        ]
        assert len(test_chapter_1) == 75
        assert len(test_chapter_2) == 75

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
            "TestBook", "TestAuthor", "https://example.com/1/", Book.State.END,
            "TestDescription_1"
        )
        test_book_2 = Book(
            "TestBook", "TestAuthor", "https://example.com/2/", Book.State.SERIALIZING,
            "TestDescription_2"
        )
        empty_book = Book.empty_book()
        test_book_1.append(test_chapter_1)
        test_book_1.append(test_chapter_2)

        assert test_book_1.name == "TestBook"
        assert test_book_1.author == "TestAuthor"
        assert test_book_1.source == "https://example.com/1/"
        assert test_book_1.state == Book.State.END
        assert test_book_1.desc == "TestDescription_1"
        assert test_book_1.cover_image == b""
        assert test_book_1.other_data == {}
        
        assert len(test_book_1) == 2
        assert len(test_book_2) == 0
        assert not empty_book
        assert test_book_1 == test_book_2
        assert test_book_1.index_list == [1, 2]
        assert list(test_book_1.chapter_list) == \
            [test_chapter_1, test_chapter_2]

    def test_book_save(self):
        with open("./tests/book.jpg", "rb") as pic_file:
            pic = pic_file.read()

        test_book_1 = Book(
            "TestBook", "TestAuthor", 
            "https://example.com/1/", 
            Book.State.END,
            "TestDescription_1", pic
        )
        test_chapter_1 = Chapter(
            "TestChapter1", 1, "http://example.com/", "TestBook",
            ("This is the first line.", "This is the second line.")
        )
        test_book_1.append(test_chapter_1)
        
        test_book_1.save(Book.SaveMethod.TXT)
        test_book_1.save(Book.SaveMethod.EPUB)
        test_book_1.save(Book.SaveMethod.PDF)

        assert os.path.exists("./tests/test_book_save.txt")
        assert os.path.exists("./tests/test_book_save.epub")
        assert os.path.exists("./tests/test_book_save.pdf")

        os.remove("./tests/test_book_save.txt")
        os.remove("./tests/test_book_save.epub")
        os.remove("./tests/test_book_save.pdf")