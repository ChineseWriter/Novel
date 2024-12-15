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
     	"Ver": "1.0.0", "Time": "2024-12-04",
		"Changes": [
			"可以下载小说，并可以指定多个 URL 一次性下载.",
			"加入了三个网站的引擎, 包括笔趣阁下的两个网站和番茄小说的支持, " \
       			"笔趣阁支持多线程下载, 番茄小说暂时不支持.",
			"下载过的书籍及其章节将会被记录下来, 之后再次下载时将使用本地的副本."
		]
    },
 	{
		"Ver": "1.0.1", "Time": "2024-12-11",
		"Changes": [
			"加强了程序的稳定性, 更新模块主要包括 Book 和 Network.",
   			"给 Network, Web 模块编写了注释.",
			"修复了番茄小说引擎在获取书籍信息时被反爬的情况.",
			"修复了笔趣阁引擎在获取到某种UA时页面结构改变的问题.",
			"优化了默认下载信息回调函数的信息显示.",
			"完善 Network 模块中的获取下一个 URL 方法.",
			"初步编写预下载模块, 其暂时不能投入使用.",
			"删去了文件内版本指示.",
			"使设置模块可以正常工作."
		]
    },
]