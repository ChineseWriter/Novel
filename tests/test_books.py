#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: test_books.py
# @Time: 19/06/2024 10:55
# @Author: Amundsen Severus Rubeus Bjaaland


import os

from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup as bs

from downloader import books


class TestConstant:
    def test_book_state(self):
        assert books.BookState.transform(1) == books.BookState.END
        assert books.BookState.transform(2) == books.BookState.SERIALIZING
        assert books.BookState.transform(3) == books.BookState.FORECAST
        assert books.BookState.transform(4) == books.BookState.BREAK
        assert books.BookState.transform(5) == books.BookState.SERIALIZING
        assert books.BookState.END == ("完结", 1)
        assert books.BookState.SERIALIZING == ("连载中", 2)
        assert books.BookState.FORECAST == ("预告", 3)
        assert books.BookState.BREAK == ("断更", 4)
    
    def test_caching_method(self):
        assert books.CachingMethod.transform(1) == books.CachingMethod.M_MEMORY
        assert books.CachingMethod.transform(2) == books.CachingMethod.M_DISK
        assert books.CachingMethod.transform(3) == books.CachingMethod.M_DISK
        assert books.CachingMethod.M_MEMORY == ("内存", 1)
        assert books.CachingMethod.M_DISK == ("磁盘", 2)
    
    def test_storage_method(self):
        assert books.StorageMethod.transform(1) == books.StorageMethod.M_TXT
        assert books.StorageMethod.transform(2) == books.StorageMethod.M_EPUB
        assert books.StorageMethod.transform(3) == books.StorageMethod.M_PDF
        assert books.StorageMethod.transform(4) == books.StorageMethod.M_EPUB
        assert books.StorageMethod.M_TXT == ("TXT", 1)
        assert books.StorageMethod.M_EPUB == ("EPUB", 2)
        assert books.StorageMethod.M_PDF == ("PDF", 3)


class TestChapter:
    def test_novel_chapter(self):
        chapter_1 = books.NovelChapter(
            "测试书籍名", 1, "测试章节名_1", "https://example.com/",
            ["这是测试内容第一段。", "这是测试内容第二段。"]
        )
        chapter_2 = books.NovelChapter(
            "测试书籍名", 2, "测试章节名_2", "https://example.com/",
            ["这是测试内容第一段。", "这是测试内容第二段。"],
            books.CachingMethod.M_MEMORY
        )
        chapter_3 = books.NovelChapter(
            "测试书籍名", 1, "测试章节名_1", "https://example.com/",
            ["这是测试内容第一段。", "这是测试内容第二段。"],
            books.CachingMethod.M_MEMORY
        )
        
        assert str(chapter_1) == "第00001章 测试章节名_1\n\t这是测试内容第一段。\n\t这是测试内容第二段。\n"
        assert len(chapter_1) == 40
        assert chapter_1.para_list == ["这是测试内容第一段。", "这是测试内容第二段。"]
        assert chapter_1.word_count == {'这是': 2, '测试': 2, '内容': 2, '。': 2, '第一段': 1, '第二段': 1}
        assert hash(chapter_1) == 1873465245797862365
        assert chapter_1 == chapter_3
        assert chapter_1.html_content.content == "<p>这是测试内容第一段。</p><p>这是测试内容第二段。</p>"
        assert chapter_1.html_content.bs == bs("<p>这是测试内容第一段。</p><p>这是测试内容第二段。</p>", "lxml")
        assert chapter_1.html_content.content == chapter_2.html_content.content
        assert chapter_1.html_content.bs == chapter_2.html_content.bs
        
        assert os.path.exists("./data/books/cache/测试书籍名/00001 - 测试章节名_1/测试章节名_1.html")
        os.remove("./data/books/cache/测试书籍名/00001 - 测试章节名_1/测试章节名_1.html")
        assert str(chapter_1) == "第00001章 测试章节名_1\n\t该章节缓存过程中出现问题。\n"
        assert chapter_1.html_content.content == "<p>该章节缓存过程中出现问题。</p>"
    
    def test_cartoon_chapter(self):
        with open("./building/test.jpg", "rb") as pic_file:
            pic = pic_file.read()
        dealt_pic = BytesIO()
        image = Image.open(BytesIO(pic))
        image.save(dealt_pic, image.format)
        dealt_pic.seek(0)
        dealt_pic = dealt_pic.read()
            
        chapter_1 = books.CartoonChapter(
            "测试书籍名", 1, "测试章节名_1", "https://example.com/",
            ["https://q1.itc.cn/images01/20240619/a18d6730f77c4c1bb5e0a583eb21dd5a.jpeg"],
            [pic]
        )
        chapter_2 = books.CartoonChapter(
            "测试书籍名", 1, "测试章节名_1", "https://example.com/",
            ["https://q1.itc.cn/images01/20240619/a18d6730f77c4c1bb5e0a583eb21dd5a.jpeg"],
            [pic],
            books.CachingMethod.M_MEMORY
        )
        
        assert str(chapter_1) == "第00001章 测试章节名_1\n\t这是第1张图片。\n"
        assert len(chapter_1) == 1
        assert chapter_1.img_url_list == \
            ["https://q1.itc.cn/images01/20240619/a18d6730f77c4c1bb5e0a583eb21dd5a.jpeg"]
        assert list(chapter_1.img_list) == [dealt_pic]
        assert hash(chapter_1) == 1873465245797862365
        assert chapter_1 == chapter_2
        assert chapter_1.html_content.content == \
            '<p>这是第1张图片。<br/>' \
            '<img src="https://q1.itc.cn/images01/20240619/a18d6730f77c4c1bb5e0a583eb21dd5a.jpeg"/></p>'
        assert chapter_1.html_content.bs == bs(
            '<p>这是第1张图片。<br/>' \
            '<img src="https://q1.itc.cn/images01/20240619/a18d6730f77c4c1bb5e0a583eb21dd5a.jpeg"/></p>',
            "lxml"
        )
        assert list(chapter_1.image_object_list)[0].content == dealt_pic
        assert chapter_1.html_content.content == chapter_2.html_content.content
        assert chapter_1.html_content.bs == chapter_2.html_content.bs
        assert list(chapter_1.image_object_list)[0].content == \
            list(chapter_2.image_object_list)[0].content
        
        assert os.path.exists("./data/books/cache/测试书籍名/00001 - 测试章节名_1/测试章节名_1.JPEG")
        os.remove("./data/books/cache/测试书籍名/00001 - 测试章节名_1/测试章节名_1.JPEG")
        assert list(chapter_1.image_object_list)[0].image == Image.new("RGB", (600, 600), (255, 255, 255))


class TestBook:
    def test_book(self):
        with open("./building/test.jpg", "rb") as pic_file:
            pic = pic_file.read()
        
        book_1 = books.Book(
            "测试书籍名", "测试作者名",
            books.BookState.END, "http://example.com/",
            "测试简介", pic
        )
        book_2 = books.Book(
            "测试书籍名", "测试作者名",
            books.BookState.SERIALIZING, "http://example.com/",
            "测试简介", pic
        )
        book_3 = books.Book(
            "测试书籍名_1", "测试作者名",
            books.BookState.SERIALIZING, "http://example.com/",
            "测试简介", pic
        )
        chapter_1 = books.NovelChapter(
            "测试书籍名", 1, "测试章节名_1", "https://example.com/",
            ["这是测试内容第一段。", "这是测试内容第二段。"]
        )
        chapter_2 = books.NovelChapter(
            "测试书籍名", 2, "测试章节名_2", "https://example.com/",
            ["这是测试内容第一段。", "这是测试内容第二段。"],
            books.CachingMethod.M_MEMORY
        )
        chapter_3 = books.CartoonChapter(
            "测试书籍名", 1, "测试章节名_3", "https://example.com/",
            ["https://q1.itc.cn/images01/20240619/a18d6730f77c4c1bb5e0a583eb21dd5a.jpeg"],
            [pic]
        )
        chapter_4 = books.CartoonChapter(
            "测试书籍名", 2, "测试章节名_4", "https://example.com/",
            ["https://q1.itc.cn/images01/20240619/a18d6730f77c4c1bb5e0a583eb21dd5a.jpeg"],
            [pic],
            books.CachingMethod.M_MEMORY
        )
        
        book_1.append(chapter_1, "测试分卷")
        book_1.append(chapter_2, "测试分卷")
        book_3.append(chapter_3, "测试分卷")
        book_3.append(chapter_4, "测试分卷")
        
        assert len(book_1) == 2
        print(str(book_1))
        assert str(book_1) == "测试书籍名 By:测试作者名 (完结)\n\n" \
            "简介:\n\t测试简介\n\n" \
            "第000卷 测试分卷\n\n" \
            "第00001章 测试章节名_1\n\t这是测试内容第一段。\n\t这是测试内容第二段。\n\n" \
            "第00002章 测试章节名_2\n\t这是测试内容第一段。\n\t这是测试内容第二段。\n"
        assert book_1 == book_2
        
        assert [
            (volume_name, list(chapter_list)) 
            for (volume_name, chapter_list) in book_1.chapter_list
            ] == [("测试分卷", [chapter_1, chapter_2])]
        book_1.save()
        book_3.save()
        book_1.save(books.StorageMethod.M_TXT)
        
        
