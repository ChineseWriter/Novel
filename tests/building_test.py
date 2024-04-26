#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: building_test.py
# @Time: 26/04/2024 21:08
# @Author: Amundsen Severus Rubeus Bjaaland

import os
import sys

work_folder = os.path.abspath(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)
sys.path.append(work_folder)

import downloader


if __name__ == "__main__":
    manager = downloader.Manager()
    chapter = manager.create_chapter(
        "测试书籍名", 0, "测试章节名", "https://example.com/", 
        "<p>这是测试内容第一段。</p><p>这是测试内容第二段。</p>"
    )