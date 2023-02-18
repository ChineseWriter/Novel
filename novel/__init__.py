#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :__init__.py.py
# @Time      :03/09/2022 11:42
# @Author    :Amundsen Severus Rubeus Bjaaland


from .object import Book, Chapter
from .tools import StorageServer
from .config import WebMap, WebConfig
from .engines import ENGINE_LIST, MAP
from .manually_down import BookConfig, ManDown
from .cache import UrlGetter, WebUrlManager
from .gui import DownloadFrame


VERSION_HISTORY = [
	{
		"Version": "1.0.0",
		"Changes": "可用下载番茄小说网和新顶点小说网的小说并提供GUI界面。"
	},
	{
		"Version": "1.0.1",
		"Changes": "添加了笔趣阁小说、全本小说、81中文、新笔趣阁、1718K文学的引擎。修复了全本小说网有反爬机制的问题。"
	},
	{
		"Version": "1.0.2",
		"Changes": "完成了项目文件的初步重构。建立了反爬处理机制。"
	},
	{
		"Version": "1.0.3",
		"Changes": "完成了项目文件的重构，初步建立新的GUI。"
	},
]


VERSION = VERSION_HISTORY[-1]["Version"]
AUTHOR = "Amundsen Severus Rubeus Bjaaland"
