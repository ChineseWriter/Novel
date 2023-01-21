#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# @FileName  :config.py
# @Time      :2023/1/14 12:41
# @Author    :Amundsen Severus Rubeus Bjaaland
"""网站配置文件"""


# 导入Python标准库
import re
import copy
import time
import traceback
from typing import Callable, Tuple, List
from urllib.parse import urlparse

# 导入自定义库
from .log import Logger
from .tools import Network
from .object import Book, Chapter, BookData, ChapterData


class WebConfig(object):
	"""网站的相关信息及下载时的预定行为"""
	# 网站的网址，注意应有两个"."，即分为三节
	main_url = "www.example.com"
	# 网站的名字
	name = "默认"
	# 网站书籍URL的固定模式
	book_url_pattern = re.compile(r"/book/\d+/")
	# 网站章节URL的固定模式
	chapter_url_pattern = re.compile(r"/chapter/\d+/")
	# 网站所使用的编码
	encoding = "UTF-8"
	# 遭遇反爬机制等待的时长
	wait_time = 30
	
	def __str__(self):
		return f"{self.name} - {self.main_url}"
	
	def __repr__(self):
		return f"<WebConfig name={self.name} main_url={self.main_url} encoding={self.encoding}>"
	
	def get_book_info(self, response: Network) -> BookData:
		"""获取书籍的基本信息"""
		response.response.encoding = self.encoding
		return BookData("", "", Book.BookState.SERIALIZING, "", "", [])
	
	def get_chapter_text(self, response: Network, index: int) -> ChapterData:
		"""获取章节的内容"""
		response.response.encoding = self.encoding
		return ChapterData(index + 1, "")
	
	def is_protected(self, response: Network) -> bool:
		"""判断是否为网站的访问保护"""
		response.response.encoding = self.encoding
		return False


class Web(object):
	"""网站对象"""
	class WebDownloadTools(object):
		"""书籍下载工具"""
		@staticmethod
		def check_book_pattern(url: str, config: WebConfig, logger: Logger) -> bool:
			"""检查传入的网址是否受传入的引擎支持"""
			# 检查该书籍URL的域名与该网站是否匹配
			if urlparse(url).netloc != config.main_url:
				logger.object.warning(f"指定URL({url})的域名与该网站({config.main_url})不匹配。")
				return False
			# 检查该书籍URL与该网站的书籍URL固定模式是否匹配
			if not re.match(config.book_url_pattern, urlparse(url).path):
				logger.object.warning(f"指定URL({url})不为该网站({config.main_url})的书籍URL。")
				return False
			# 检查完毕
			return True
		
		@staticmethod
		def get_book_info(url: str, config: WebConfig, logger: Logger) -> BookData:
			"""获取指定URL下的书籍信息

			:param url: 书籍目录的URL
			"""
			while True:
				# 获取网络数据
				book_response = Network.get_response(url)
				# 设置适用于该网站的编码
				book_response.response.encoding = config.encoding
				# 初始化书籍数据容器
				book_data = BookData("", "", Book.BookState.SERIALIZING, "", "", [])
				# 解析数据
				try:
					book_data = config.get_book_info(book_response)
				except Exception:
					# 检查是否为网站的反爬机制
					if config.is_protected(book_response):
						time.sleep(config.wait_time)
						continue
					# 若不是反爬机制，则解析函数存在问题，该次解析失败
					logger.object.warning(
						f"解析书籍数据失败：\n{traceback.format_exc()}"
					)
				return book_data
		
		@staticmethod
		def get_chapter_content(
				one_chapter_info: Tuple[str, str], book_info: Book,
				config: WebConfig, index: int, logger: Logger
		) -> ChapterData:
			while True:
				# 获取网络数据
				chapter_response = Network.get_response(one_chapter_info[0])
				# 设置适用于该网站的编码
				chapter_response.response.encoding = config.encoding
				# 初始化章节数据容器
				one_chapter_data = ChapterData(index + 1, "")
				# 解析数据
				try:
					one_chapter_data = config.get_chapter_text(chapter_response, index + 1)
				except Exception:
					# 检查是否为网站的反爬机制
					if config.is_protected(chapter_response):
						time.sleep(config.wait_time)
						continue
					# 若不是反爬机制，则解析函数存在问题，该次解析失败
					logger.object.warning(
						f"解析书籍({book_info.book_name})的章节数据失败: \n{traceback.format_exc()}"
					)
					return one_chapter_data
				# 检查该章节的数据是否过小
				if len(one_chapter_data.text) <= 1000:
					# 检查是否为网站的反爬机制
					if config.is_protected(chapter_response):
						time.sleep(config.wait_time)
						continue
				return one_chapter_data

	def __init__(
		self, config: WebConfig,
		book_info_callback: Callable[[str, str, str, str, int], None],
		chapter_info_callback: Callable[[str, str, str, str, int], None],
		book_finish_callback: Callable[[str, str], None]
	):
		"""初始化网站对象

		:param config: 网站的相关信息及下载时的预定行为
		:param book_info_callback: 获取到书籍信息后将会调用该回调函数，参数分别为书籍名，作者名，书籍状态，书籍描述，章节总数
		:param chapter_info_callback: 获取章节内容后将会调用该回调函数，书籍名，作者名，章节名称，章节内容，章节序号
		:param book_finish_callback: 书籍下载完毕后将会调用该回调函数，参数分别为书籍名，作者名
		"""
		# 创建一个config参数的拷贝，防止被意外更改
		self.__config = copy.deepcopy(config)
		# 创建日志记录器对象
		self.__logger = Logger(f"Novel.Web.{self.__config.main_url.split('.')[1]}", "engine")
		# 创建钩子函数，以满足下载时显示进度的需要
		self.__book_info_callback = book_info_callback
		self.__chapter_info_callback = chapter_info_callback
		self.__book_finish_callback = book_finish_callback
	
	def __repr__(self):
		return f"<Web name={self.__config.name} main_url={self.__config.main_url}>"
	
	@property
	def book_info_callback(self):
		"""获取书籍信息回调函数"""
		return self.__book_info_callback
	
	@book_info_callback.setter
	def book_info_callback(self, cn_func: Callable[[str, str, str, str, int], None]):
		self.__book_info_callback = cn_func
	
	@property
	def chapter_info_callback(self):
		"""获取章节信息回调函数"""
		return self.__chapter_info_callback
	
	@chapter_info_callback.setter
	def chapter_info_callback(self, cn_func: Callable[[str, str, str, str, int], None]):
		self.__chapter_info_callback = cn_func
	
	@property
	def book_finish_callback(self):
		"""获取书籍下载完成回调函数"""
		return self.__book_finish_callback
	
	@book_finish_callback.setter
	def book_finish_callback(self, cn_func: Callable[[str, str], None]):
		self.__book_finish_callback = cn_func
	
	@property
	def config(self):
		"""获取该网站的相关信息及下载时的预定行为"""
		return copy.deepcopy(self.__config)
	
	def download_book(self, url: str) -> Book:
		"""下载指定URL下的书籍

		:param url: 书籍目录的URL
		"""
		# 检查该网址是否符合该网站的书籍网址模式
		if not self.WebDownloadTools.check_book_pattern(url, self.__config, self.__logger):
			return Book("", "", Book.BookState.SERIALIZING, "")
		
		# 获取该书籍的相关信息
		book_data = self.WebDownloadTools.get_book_info(url, self.__config, self.__logger)
		if not book_data.name:
			return Book("", "", Book.BookState.SERIALIZING, "")
		else:
			book = Book.from_book_data(book_data)
		
		# 调用书籍信息回调函数
		try:
			self.__book_info_callback(
				book.book_name, book.author, book.state[0], book.desc, len(book_data.chapter_list)
			)
		except Exception:
			self.__logger.object.warning(f"书籍信息回调函数执行出错：\n{traceback.format_exc()}")
		
		# 获取章节内容
		for index, one_chapter_info in enumerate(book_data.chapter_list):
			# 检查该网址是否符合该网站的章节网址模式
			if not self.__config.chapter_url_pattern.match(urlparse(one_chapter_info[0]).path):
				self.__logger.object.warning("返回的章节URL与指定的章节URL不匹配。")
			# 获取该章节的相关内容
			one_chapter_data = self.WebDownloadTools.get_chapter_content(
				one_chapter_info, book, self.__config, index, self.__logger
			)
			# 调用章节信息回调函数
			try:
				self.__chapter_info_callback(
					book.book_name, book.author, one_chapter_info[1], one_chapter_data.text, index + 1
				)
			except Exception:
				self.__logger.object.warning(f"章节信息回调函数执行出错：\n{traceback.format_exc()}")
			# 创建章节对象
			one_chapter = Chapter(
				book_data.name, one_chapter_data.index,
				one_chapter_info[1], one_chapter_info[0], one_chapter_data.text
			)
			# 向书籍中添加章节
			book.append(one_chapter)
		
		# 调用书籍下载完成回调函数
		try:
			self.__book_finish_callback(book.book_name, book.author)
		except Exception:
			self.__logger.object.warning(f"书籍下载完成回调函数执行出错：\n{traceback.format_exc()}")
		# 记录日志并返回数据
		self.__logger.object.info(f"书籍({book.book_name})下载完毕。")
		return book


class WebMap(object):
	"""支持的网站列表管理"""
	def __init__(
			self, book_info_callback: Callable[[str, str, str, str, int], None],
			chapter_info_callback: Callable[[str, str, str, str, int], None],
			finish_callback: Callable[[str, str], None]
	):
		"""初始化网站管理对象
		
		:param book_info_callback: 书籍信息回调函数，参数分别为书籍名，作者名，书籍状态，书籍描述，章节总数
		:param chapter_info_callback: 章节信息回调函数，参数分别为书籍名，作者名，章节名称，章节内容，章节序号
		:param finish_callback: 书籍下载完成回调函数，参数分别为书籍名，作者名
		"""
		# 创建钩子函数，以满足下载时显示进度的需要
		self.__book_info_callback: Callable[[str, str, str, str, int], None] = book_info_callback
		self.__chapter_info_callback: Callable[[str, str, str, str, int], None] = chapter_info_callback
		self.__finish_callback = finish_callback
		# 创建网站列表对象
		self.__web_list: List[Web] = []
		# 创建日志记录器对象
		self.__logger = Logger("Novel.BookMap", "map")
	
	def __repr__(self):
		return f"<WebMap web_number={len(self.__web_list)}>"
	
	@property
	def book_info_callback(self):
		"""获取书籍信息回调函数，参数分别为书籍名，作者名，书籍状态，书籍描述，章节总数"""
		return self.__book_info_callback
	
	@book_info_callback.setter
	def book_info_callback(self, cn_func: Callable[[str, str, str, str, int], None]):
		self.__book_info_callback = cn_func
		for i in self.__web_list:
			i.book_info_callback = cn_func
	
	@property
	def chapter_info_callback(self):
		"""获取章节信息回调函数，参数分别为书籍名，作者名，章节名称，章节序号"""
		return self.__chapter_info_callback
	
	@chapter_info_callback.setter
	def chapter_info_callback(self, cn_func: Callable[[str, str, str, str, int], None]):
		self.__chapter_info_callback = cn_func
		for i in self.__web_list:
			i.chapter_info_callback = cn_func
	
	@property
	def finish_callback(self):
		"""书籍下载完成回调函数，参数分别为书籍名，作者名"""
		return self.__finish_callback
	
	@finish_callback.setter
	def finish_callback(self, cn_func: Callable[[str, str], None]):
		self.__finish_callback = cn_func
		for i in self.__web_list:
			i.book_finish_callback = cn_func
	
	def append(self, web_config: WebConfig) -> bool:
		"""添加一个新网站配置

		:param web_config: 网站配置
		"""
		self.__web_list.append(Web(
			copy.deepcopy(web_config),  # 防止网站配置文件被更改
			self.__book_info_callback, self.__chapter_info_callback, self.__finish_callback
		))
		self.__logger.object.info(f"添加了一个网站({web_config.name})的配置。")
		return True
	
	def get_web_by_url(self, one_url: str) -> Web:
		"""通过URL获取对应网站

		:param one_url: 任意URL
		"""
		# 解析传入的URL
		url = urlparse(one_url)
		netloc = url.netloc
		# 检查域名长度
		if len(netloc.split(".")) == 3:
			# 若为3，则无任何操作
			pass
		elif len(netloc.split(".")) == 2:
			# 若为2，则用默认前缀("www.")补全URL
			netloc = "www." + url.netloc
		else:
			# 若不为2或3，则发出警告，并返回空网站对象
			self.__logger.object.warning(f"传入的URL({one_url})的域名不合法：应为2或3节。")
			return Web(
				WebConfig(), self.__book_info_callback,
				self.__chapter_info_callback, self.__finish_callback
			)
		# 在网站列表中查找域名匹配的网站并返回第一个匹配项
		for one_web in self.__web_list:
			if netloc == one_web.config.main_url:
				return one_web
		# 若未找到则返回空网站对象并示警
		self.__logger.object.warning(f"未为{one_url}找到指定的网站引擎。")
		return Web(
			WebConfig(), self.__book_info_callback,
			self.__chapter_info_callback, self.__finish_callback
		)
	
	def download(self, book_url: str):
		"""下载书籍
		
		:param book_url: 书籍目录的URL
		"""
		# 通过书籍目录URL查找网站引擎
		web = self.get_web_by_url(book_url)
		# 检查查找是否成功
		if web.config.name == "默认":
			return Book("", "", Book.BookState.SERIALIZING, "")
		# 规范化网址，将域名补齐
		if len(urlparse(book_url).netloc.split(".")) == 2:
			book_url = book_url.replace("//", "//www.")
		# 找到引擎的信息
		self.__logger.object.info(f"为{book_url}查找到网站({web.config.name})引擎。")
		# 下载书籍至内存并返回书籍对象
		return web.download_book(book_url)
