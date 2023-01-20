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
from typing import List, Callable, Tuple
from urllib.parse import urlparse

# 导入第三方库
import requests

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
	
	def is_protected(self, response: Network, text: str) -> bool:
		"""判断是否为网站的访问保护"""
		response.response.encoding = self.encoding
		text.split(" ")
		return False


class Web(object):
	"""网站对象"""
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
		result = WebDownloadTools.check_book_pattern(url, self.__config)
		if not result[0]:
			self.__logger.object.warning(result[1])
			return Book("", "", Book.BookState.SERIALIZING, "")
		
		result = WebDownloadTools.get_book_info(url, self.__config)
		if not result[0]:
			self.__logger.object.warning(result[1])
			return Book("", "", Book.BookState.SERIALIZING, "")
		else:
			book, book_data = result[2], result[3]
		# # 调用书籍信息回调函数
		try:
			self.__book_info_callback(
				book.book_name, book.author, book.state[0], book.desc, len(book_data.chapter_list)
			)
		except Exception:
			self.__logger.object.warning("书籍信息回调函数执行出错。")
		
		# 获取章节内容
		for index, one_chapter_info in enumerate(book_data.chapter_list):
			if not self.__config.re_chapter_url_pattern.match(urlparse(one_chapter_info[0]).path):
				self.__logger.object.warning("返回的章节URL与指定的章节URL不匹配。")
			flag = True
			one_chapter_data = ChapterData(index + 1, "")
			while flag:
				result = WebDownloadTools.get_chapter_content(one_chapter_info, book, self.__config, index)
				if not result[0]:
					self.__logger.object.warning(result[1])
					continue
				one_chapter_data, chapter_response = result[2], result[3]
				# 检查章节内容长度是否合规
				if len(one_chapter_data.text) > 1000:
					flag = False
				if self.__config.is_protected(chapter_response, one_chapter_data.text):
					time.sleep(30)
					self.__logger.object.warning(
						f"下载书籍({book.book_name})的章节({one_chapter_info[1]})时遭遇网站反爬机制。"
					)
				else:
					self.__logger.object.warning(
						f"书籍({book.book_name})的章节({one_chapter_info[1]})数据可能存在问题(长度小于或等于1000)。"
						f"章节网址：{one_chapter_info[0]}"
					)
					flag = False
			# 调用章节信息回调函数
			try:
				self.__chapter_info_callback(
					book.book_name, book.author, one_chapter_info[1], one_chapter_data.text, index + 1
				)
			except Exception as error:
				self.__logger.object.warning(f"章节信息回调函数执行出错：{repr(error)}")
			# 创建章节对象
			one_chapter = Chapter(
				book_data.name, one_chapter_data.index,
				one_chapter_info[1], one_chapter_info[0], one_chapter_data.text
			)
			book.append(one_chapter)  # 向书籍中添加章节
		
		# 调用书籍下载完成回调函数
		try:
			self.__book_finish_callback(book.book_name, book.author)
		except Exception:
			self.__logger.object.warning("书籍下载完成回调函数执行出错。")
		# 记录日志并返回数据
		self.__logger.object.info(f"书籍({book.book_name})下载完毕。")
		return book


class WebDownloadTools(object):
	"""书籍下载工具"""
	@staticmethod
	def check_book_pattern(url: str, config: WebConfig) -> Tuple[bool, str]:
		"""检查传入的网址是否受传入的引擎支持"""
		# 检查该书籍URL的域名与该网站是否匹配
		if urlparse(url).netloc != config.main_url:
			return False, f"指定URL({url})的域名与该网站({config.main_url})不匹配。"
		# 检查该书籍URL与该网站的书籍URL固定模式是否匹配
		if not re.match(config.book_url_pattern, urlparse(url).path):
			return False, f"指定URL({url})不为该网站({config.main_url})的书籍URL。"
		return True, ""
	
	@staticmethod
	def get_book_info(url: str, config: WebConfig) -> Tuple[bool, str, Book, BookData]:
		# 获取书籍信息
		# # 获取网络数据
		book_response = get_response(url)
		book_response.response.encoding = config.encoding
		book_data = BookData("", "", Book.BookState.SERIALIZING, "", "", [])
		# # 解析数据
		try:
			book_data = config.get_book_info(book_response)
		except Exception as Error:
			return False, f"解析书籍数据失败：{repr(Error)}", Book("", "", Book.BookState.SERIALIZING, ""), book_data
		return True, "", Book(book_data.name, book_data.author, book_data.state, book_data.source,
		                      book_data.desc), book_data
	
	@staticmethod
	def get_chapter_content(
			one_chapter_info: Tuple[str, str], book_info: Book, config: WebConfig, index: int
	) -> Tuple[bool, str, ChapterData, Network]:
		# 获取网络数据
		chapter_response = get_response(one_chapter_info[0])
		chapter_response.response.encoding = config.encoding
		flag = True
		message = ""
		one_chapter_data = ChapterData(index + 1, "")
		# 解析数据
		try:
			one_chapter_data = config.get_chapter_text(chapter_response, index + 1)
		except Exception as Error:
			flag = False
			message = f"解析书籍({book_info.book_name})的章节数据失败: {repr(Error)}"
		return flag, message, one_chapter_data, chapter_response


class WebMap(object):
	"""支持的网站列表管理"""
	
	def __init__(
			self, book_info_callback: Callable[[str, str, str, str, int], None],
			chapter_info_callback: Callable[[str, str, str, str, int], None],
			finish_callback: Callable[[str, str], None]
	):
		"""初始化网站管理对象"""
		# 创建钩子函数，以满足下载时显示进度的需要
		# # 书籍信息回调函数，参数分别为书籍名，作者名，书籍状态，书籍描述，章节总数
		self.__book_info_callback: Callable[[str, str, str, str, int], None] = book_info_callback
		# # 章节信息回调函数，参数分别为书籍名，作者名，章节名称，章节内容，章节序号
		self.__chapter_info_callback: Callable[[str, str, str, str, int], None] = chapter_info_callback
		# # 书籍下载完成回调函数，参数分别为书籍名，作者名
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
		# 获取传入的URL的域名
		netloc = url.netloc
		# 检查域名长度
		if len(url.netloc.split(".")) == 3:
			# 若为3，则无任何操作
			pass
		elif len(url.netloc.split(".")) == 2:
			# 若为2，则用默认前缀("www.")补全URL
			netloc = "www." + url.netloc
		else:
			# 若不为2或3，则发出警告，并返回空网站对象
			self.__logger.object.warning(f"解析传入的URL({one_url})出错。")
			return Web(WebConfig(), self.__book_info_callback, self.__chapter_info_callback, self.__finish_callback)
		# 在网站列表中查找域名匹配的网站并返回第一个匹配项
		for one_web in self.__web_list:
			if netloc == one_web.config.main_url:
				return one_web
		# 若未找到则返回空网站对象
		return Web(WebConfig(), self.__book_info_callback, self.__chapter_info_callback, self.__finish_callback)
	
	def download(self, book_url: str):
		"""下载书籍

		:param book_url: 书籍目录的URL
		"""
		# 通过书籍目录URL查找网站引擎
		web = self.get_web_by_url(book_url)
		# 检查查找是否成功
		if web.config.name == "默认":
			# 若未成功则发出警告并返回空网站对象
			self.__logger.object.warning(f"未为{book_url}找到指定的网站引擎。")
			return Book("", "", Book.BookState.SERIALIZING, "")  # TODO BookState应加上Error
		self.__logger.object.info(f"为{book_url}查找到网站({web.config.name})引擎。")
		# 下载书籍至内存
		book = web.download_book(book_url)
		# 返回书籍对象
		return book
