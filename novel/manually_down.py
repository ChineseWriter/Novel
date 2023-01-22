#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :manually_down.py
# @Time      :09/10/2022 10:26
# @Author    :Amundsen Severus Rubeus Bjaaland
"""为在Python程序中手动下载小说提供支持"""


# 导入Python标准库
import copy
from typing import List, Tuple

# 导入自定义库
from .config import WebMap
from .engines import ENGINE_LIST
from .tools import StorageServer


class BookConfig(object):
	"""书籍信息配置"""
	DOWNLOAD_TYPE = StorageServer.StorageMethod

	def __init__(self, book_url: str, down_type: Tuple[str, int], flag: bool = True, book_name: str = "") -> None:
		"""初始化该类
		
		:param book_url: 书籍的源URL
		:param down_type: 书籍的下载方式
		:param flag: 书籍是否要被下载
		:param book_name: 书籍的名称，便于记录书籍名
		"""
		# 书籍的源URL
		self.__book_url = book_url
		# 书籍的下载方式
		self.__down_type = down_type
		# 书籍下载标识
		self.__flag = flag
		# 书籍名称
		self.__book_name = book_name
	
	def __str__(self):
		return f"{self.__book_url} - {self.__down_type} - {'下载' if self.__flag else '不下载'}"
	
	def __repr__(self):
		return f"<BookConfig flag={self.__flag} down_type={self.__down_type} name={self.__book_name} url={self.__book_url}>"
	
	@property
	def book_url(self):
		"""获取该书籍的源URL"""
		return self.__book_url
	
	@property
	def down_type(self):
		"""获取该书籍的下载方式"""
		return self.__down_type
	
	@property
	def flag(self):
		"""标示该书籍是否要下载"""
		return self.__flag


class Callback(object):
	"""命令行内使用的回调函数集"""
	@staticmethod
	def book_info(name: str, author: str, state: str, desc: str, chapter_number: int):
		print(f"以下是书籍信息:\n\t名称 - {name}\n\t作者 - {author}\n\t状态 - {state}\n\t章节数 - {chapter_number}\n\t描述 - {desc}")
	
	@staticmethod
	def chapter_info(book_name: str, author: str, chapter_name: str, content: str, index: int):
		print(f"{book_name} - {author}: {index}.{chapter_name} 长度：{len(content)}")
	
	@staticmethod
	def book_finish(name: str, author: str):
		print(f"{name} - {author}: 下载完毕!")


class ManDown(object):
	"""手动小说下载管理器"""
	DOWNLOAD_TYPE = StorageServer.StorageMethod

	def __init__(self):
		# 书籍配置列表
		self.__book_configs: List[BookConfig] = []
		# 初始化一个新的Map对象
		self.__map = WebMap(
			Callback.book_info,
			Callback.chapter_info,
			Callback.book_finish
		)
		self.__map.append(ENGINE_LIST)  # engine可以被复用
	
	def append(self, book_config: BookConfig) -> bool:
		"""添加书籍配置
		
		:param book_config: 书籍的配置
		:return: True
		"""
		self.__book_configs.append(book_config)
		return True
	
	def download(self):
		"""下载书籍列表，flag为False的书籍不会被下载"""
		for book_config in self.__book_configs:
			if not book_config.flag:
				continue
			if book_config.down_type in self.DOWNLOAD_TYPE.ALL:
				StorageServer(self.__map.download(book_config.book_url), book_config.down_type).save()
				continue
			data = self.__map.download(book_config.book_url)
			for i in BookConfig.DownType.ALL_TYPE:
				StorageServer(data, i).save()
