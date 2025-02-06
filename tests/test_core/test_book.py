#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: test_book.py
# @Time: 31/01/2025 18:25
# @Author: Amundsen Severus Rubeus Bjaaland


import os
import sys
import time
import copy

from novel_dl import Settings
from novel_dl import ContentType, Line
from novel_dl.core.books.chapter import CacheList
from novel_dl import CacheMethod, Chapter


class TestLine:
    def test_content_type(self):
        assert ContentType.to_obj(1) == ContentType.Text
        assert ContentType.to_obj("文本") == ContentType.Text
        assert int(ContentType.Text) == 1
        assert str(ContentType.Text) == "文本"
        assert ContentType.Text.is_bytes() == False
        assert ContentType.Text.html_tag() == "p"

        assert ContentType.to_obj(2) == ContentType.Image
        assert ContentType.to_obj("图片") == ContentType.Image
        assert int(ContentType.Image) == 2
        assert str(ContentType.Image) == "图片"
        assert ContentType.Image.is_bytes() == True
        assert ContentType.Image.html_tag() == "img"

        assert ContentType.to_obj(3) == ContentType.Audio
        assert ContentType.to_obj("音频") == ContentType.Audio
        assert int(ContentType.Audio) == 3
        assert str(ContentType.Audio) == "音频"
        assert ContentType.Audio.is_bytes() == True
        assert ContentType.Audio.html_tag() == "audio"

        assert ContentType.to_obj(4) == ContentType.Video
        assert ContentType.to_obj("视频") == ContentType.Video
        assert int(ContentType.Video) == 4
        assert str(ContentType.Video) == "视频"
        assert ContentType.Video.is_bytes() == True
        assert ContentType.Video.html_tag() == "video"

        assert ContentType.to_obj(5) == ContentType.CSS
        assert ContentType.to_obj("层叠式设计样表") == ContentType.CSS
        assert int(ContentType.CSS) == 5
        assert str(ContentType.CSS) == "层叠式设计样表"
        assert ContentType.CSS.is_bytes() == False
        assert ContentType.CSS.html_tag() == "link"

        assert ContentType.to_obj(6) == ContentType.JS
        assert ContentType.to_obj("JavaScript") == ContentType.JS
        assert int(ContentType.JS) == 6
        assert str(ContentType.JS) == "JavaScript"
        assert ContentType.JS.is_bytes() == False
        assert ContentType.JS.html_tag() == "script"
        
        assert ContentType.to_obj(7) == ContentType.Text
        assert ContentType.to_obj("未知") == ContentType.Text


    def test_line(self):
        line_1 = Line(0, "Hello, World!", ContentType.Text)
        
        assert line_1.encode() == "SGVsbG8sIFdvcmxkIQ=="
        assert line_1.content == "Hello, World!"
        assert line_1.content_type == ContentType.Text
        assert line_1.attrs == {}
        
        assert line_1.to_dict() == {
            "index": 0, "attrs": {},
            "content": "SGVsbG8sIFdvcmxkIQ==",
            "content_type": int(ContentType.Text)
        }
        assert line_1 == Line.from_dict(
            {
                "content": "SGVsbG8sIFdvcmxkIQ==", "attrs": {},
                "content_type": int(ContentType.Text), "index": 0
            }
        )
        
        assert Line.default() == Line(0, "默认的 Line 对象.", ContentType.Text)

class TestChapter:
    def test_cache_method(self):
        assert CacheMethod.to_obj(1) == CacheMethod.Memory
        assert CacheMethod.to_obj("内存") == CacheMethod.Memory
        assert int(CacheMethod.Memory) == 1
        assert str(CacheMethod.Memory) == "内存"
        
        assert CacheMethod.to_obj(2) == CacheMethod.Disk
        assert CacheMethod.to_obj("磁盘") == CacheMethod.Disk
        assert int(CacheMethod.Disk) == 2
        assert str(CacheMethod.Disk) == "磁盘"
        
        assert CacheMethod.to_obj(3) == CacheMethod.Memory
        assert CacheMethod.to_obj("未知") == CacheMethod.Memory
    
    def test_cache_list(self):
        line_1 = Line(0, "Hello, World!", ContentType.Text)
        line_2 = Line(1, "你好, 世界!", ContentType.Text)
        line_3 = Line(2, "Bonjour le monde!", ContentType.Text)
        
        cache_list = CacheList(
            "测试书籍名_1", 1, "测试章节名_1", [line_1, line_2, line_3]
        )
        
        assert cache_list.path == os.path.join(
            Settings().BOOKS_CACHE_DIR,
            "测试书籍名_1/00001-测试章节名_1.cache"
        )
        assert cache_list.to_list() == [line_1, line_2, line_3]
        assert len(cache_list) == 3
        assert os.path.exists(cache_list.path)
        assert cache_list.index(line_1) == 0
        
        line_4 = Line(3, "Hola, Mundo!", ContentType.Text)
        cache_list.append(line_4)
        assert cache_list.to_list() == [line_1, line_2, line_3, line_4]
        
        line_5 = Line(4, "Hallo, Welt!", ContentType.Text)
        cache_list.insert(1, line_5)
        assert cache_list.to_list() == [
            line_1, line_5, line_2, line_3, line_4
        ]
        
        cache_list.remove(line_5)
        assert cache_list.to_list() == [line_1, line_2, line_3, line_4]
        
        cache_list.pop(1)
        assert cache_list.to_list() == [line_1, line_3, line_4]
        
        cache_list.sort(True)
        assert cache_list.to_list() == [line_4, line_3, line_1]
        
        cache_list.clear()
        assert cache_list.to_list() == []
        
        # path = copy.deepcopy(cache_list.path)
        # WARN 当有1个变量保存了对象的引用时，此对象的引用计数就会加1
        # 当使用del删除变量指向的对象时，如果对象的引用计数不会1，比如3，
        # 那么此时只会让这个引用计数减1，即变为2，
        # 当再次调用del时，变为1，如果再调用1次del，此时会真的把对象进行删除
        # a = sys.getrefcount(cache_list)
        # del cache_list
        # assert not os.path.exists(path)
    
    def test_chapter(self):
        create_time = time.time()
        chapter_1 = Chapter(
            1, "测试章节名_1", ("https://example.com/1",),
            create_time, "测试书籍名_1", (),
            CacheMethod.Memory
        )
        
        assert chapter_1.index == 1
        assert chapter_1.str_index == "00001"
        assert chapter_1.name == "测试章节名_1"
        assert chapter_1.sources == ["https://example.com/1",]
        assert chapter_1.update_time == create_time
        assert chapter_1.book_name == "测试书籍名_1"
        assert list(chapter_1.content) == []
        assert chapter_1.cache_method == CacheMethod.Memory
        assert len(chapter_1) == 0
        
        line_1 = Line(0, "Hello, World!", ContentType.Text)
        line_2 = Line(1, "你好, 世界!", ContentType.Text)
        line_3 = Line(2, "Bonjour le monde!", ContentType.Text)
        
        chapter_1.append(line_1)
        chapter_1.append(line_2)
        chapter_1.append(line_3)
        
        assert list(chapter_1.content) == [line_1, line_2, line_3]
        assert len(chapter_1) == 3
        
        chapter_1.add_source("https://example.com/2")
        assert chapter_1.sources == [
            "https://example.com/1", "https://example.com/2"
        ]
        
        chapter_2 = Chapter(
            1, "测试章节名_1", ("https://example.com/",),
            create_time, "测试书籍名_1", (line_1, line_2, line_3),
            CacheMethod.Disk
        )
        
        assert os.path.exists(
            os.path.join(
                Settings().BOOKS_CACHE_DIR,
                "测试书籍名_1/00001-测试章节名_1.cache"
            )
        )
        
        assert chapter_1 == chapter_2