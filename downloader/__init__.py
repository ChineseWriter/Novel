#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: __init__.py
# @Time: 03/04/2024 17:35
# @Author: Amundsen Severus Rubeus Bjaaland


# 预导入自定义函数(类)
from .logs import Logger
from .settings import Settings
from .bookshelf import BookShelf
from .web_manager import WebManager
from .books import Chapter, Book, EMPTY_BOOK

# 更新说明
VERSION = [
	{
     	"Ver": "0.0.1",
		"Changes": [
			"可以下载小说，并可以指定多个 URL 一次性下载.",
			"加入了三个网站的引擎, 包括笔趣阁下的两个网站和番茄小说的支持, " \
       			"笔趣阁支持多线程下载, 番茄小说暂时不支持.",
			"下载过的书籍及其章节将会被记录下来, 之后再次下载时将使用本地的副本."
		]
    }
]