#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :manually_down.py
# @Time      :09/10/2022 10:26
# @Author    :Amundsen Severus Rubeus Bjaaland
"""为在Python程序中手动下载小说提供支持"""


# 导入Python标准库
from typing import List

# 导入自定义库
from .engines import MAP
from .tools import Memorizer


class BookConfig(object):
	"""书籍信息配置"""
	class DownType(object):
		"""下载方式常量"""
		# 下载为多个Txt文件
		TXT_MANY_FILE = Memorizer.StorageMethod.TXT_MANY_FILE
		# 下载为单个Txt文件
		TXT_ONE_FILE = Memorizer.StorageMethod.TXT_ONE_FILE
		
		# 所有受支持的下载方式
		ALL_TYPE = [TXT_MANY_FILE, TXT_ONE_FILE]
		
	def __init__(self, book_url: str, down_type: str, flag: bool = True, book_name: str = "") -> None:
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
		return f"<BookConfig flag={self.__flag} down_type={self.__down_type} url={self.__book_url}>"
	
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


class ManDown(object):
	"""手动小说下载管理器"""
	def __init__(self):
		# 书籍配置列表
		self.__book_configs: List[BookConfig] = []
	
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
			if book_config.flag:
				if book_config.down_type == BookConfig.DownType.ALL_TYPE:
					data = MAP.download(book_config.book_url)
					for i in BookConfig.DownType.ALL_TYPE:
						Memorizer(data, i).save()
				else:
					Memorizer(MAP.download(book_config.book_url), book_config.down_type).save()
		
