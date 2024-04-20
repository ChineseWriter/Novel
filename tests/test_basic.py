#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: basic.py
# @Time: 20/04/2024 18:09
# @Author: Amundsen Severus Rubeus Bjaaland


import downloader


class TestManager:
    def test_manager_duplicate(self):
        manager_1 = downloader.Manager()
        manager_2 = downloader.Manager()
        assert id(manager_1) == id(manager_2)
    
class TestObjects:
    def test_chapter(self):
        manager = downloader.Manager()
        chapter = manager.create_chapter(
            "测试书籍名", 0, "测试章节名", "https://example.com/", 
            "<p>这是测试内容第一段。</p><p>这是测试内容第二段。</p>"
        )
        assert chapter.book_name == "测试书籍名"
        assert chapter.index == 0
        assert chapter.source == "https://example.com/"
        assert str(chapter) == "测试章节名\r\n\t这是测试内容第一段。" \
            "\r\n\t这是测试内容第二段。\r\n"
        assert chapter.content == "<p>这是测试内容第一段。</p>" \
            "<p>这是测试内容第二段。</p>"
        assert chapter.word_count == \
            {'这是': 2, '测试': 2, '内容': 2, '。': 2, '第一段': 1, '第二段': 1}

