#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# @FileName  :tools.py
# @Time      :2023/1/14 12:17
# @Author    :Amundsen Severus Rubeus Bjaaland
"""必要的工具，包括本地空间管理工具，文件保存工具，网络工具等"""


# 导入Python标准库
import os
import time
import socket
import traceback

import urllib3.exceptions
from urllib.parse import urlparse, urljoin

# 导入第三方库
import requests
from bs4 import BeautifulSoup

# 导入自定义库
from .log import Logger
from .object import Book


class DiskTools(object):
	"""所有和操作系统直接相关的工具"""
	
	@classmethod
	def mkdir(cls, path: str) -> bool:
		"""创建目录
	
		:param path: 目录创建位置
		:return: 创建成功或已存在则返回True，创建失败则返回False
		"""
		# 检查目录是否存在
		if os.path.exists(path):
			return True
		# 创建目录
		try:
			os.mkdir(path)
		except OSError:
			return False
		else:
			return True


# 创建项目必要的路径
DiskTools.mkdir("./data")
DiskTools.mkdir("./data/log")
DiskTools.mkdir("./data/book")


class StorageServer(object):
	"""书籍保存工具"""
	# 初始化日志记录器
	__logger = Logger("Novel.StorageServer", "disk")
	
	class StorageMethod(object):
		"""书籍保存形式常量"""
		# 保存为一个txt文件
		TXT_ONE_FILE = ("单个Txt文件", 1)
		# 保存为多个txt文件
		TXT_MANY_FILE = ("多个Txt文件", 2)
		# 保存为epub文件
		EPUB = ("Epub文件", 3)
		
		# 所有保存形式
		ALL = [TXT_ONE_FILE, TXT_MANY_FILE, EPUB]

		@classmethod
		def get(cls, index: int) -> tuple:
			result = cls.TXT_ONE_FILE
			for i in cls.ALL:
				if i[1] == index:
					result = i
			return result
	
	def __init__(self, book: Book, method: tuple):
		# 类型检查
		assert isinstance(book, Book)
		assert method in self.StorageMethod.ALL
		# 保存为类属性
		self.__book = book
		self.__method = method
	
	def save(self, path: str = "./data/book") -> int:
		"""保存该书籍
		
		:param path: 保存的路径
		:return: 保存的文件大小，以字节为单位
		"""
		# 确保指定的目录存在
		if not os.path.exists(path):
			self.__logger.object.warning(f"指定的书籍保存路径({path})不存在。")
			return 0
		# 按照指定的方式保存书籍
		if self.__method == self.StorageMethod.TXT_ONE_FILE:
			file_size = self.__txt_one_file(path)
		elif self.__method == self.StorageMethod.TXT_MANY_FILE:
			file_size = self.__txt_many_file(path)
		elif self.__method == self.StorageMethod.EPUB:
			# TODO 支持EPUB格式保存
			file_size = 0
		else:
			file_size = self.__txt_one_file(path)
		# 记录该次保存操作
		self.__logger.object.info(
			f"以{self.__method[0]}方式保存书籍{self.__book.book_name}，文件总大小{file_size / 1024 ** 2}MB。"
		)
		# 返回保存的文件总大小
		return file_size
	
	def __txt_one_file(self, path: str) -> int:
		"""以单个txt文件的形式保存该书籍
		
		:param path: 保存的路径
		:return: 保存的文件大小，以字节为单位
		"""
		# 生成书籍的文件名
		book_file_name = f"{self.__book.author} - {self.__book.book_name}.txt"
		# 生成书籍文件的路径
		book_file_path = os.path.join(path, book_file_name)
		# 书籍的内容
		book_content = str(self.__book)
		# 打开文件并保存书籍内容，若文件存在则先清空文件
		with open(book_file_path, "w", encoding="UTF-8") as book_file:
			book_file.write(book_content)
		# 返回文件的大小
		return os.path.getsize(book_file_path)
	
	def __txt_many_file(self, path: str) -> int:
		"""一多个txt文件的形式保存该书籍
		
		:param path: 保存的路径
		:return: 保存的文件大小，以字节为单位
		"""
		# 生成书籍文件夹的路径
		book_dir_path = os.path.join(path, f"{self.__book.author} - {self.__book.book_name}")
		# 创建书籍文件夹
		DiskTools.mkdir(book_dir_path)
		# 书籍文件编号
		counter_file = 1
		# 章节编号
		counter_chapter = 0
		# 每十章保存为一个书籍文件
		for i in self.__book.chapter_list:
			# 生成书籍文件名
			book_file_name = f"第{str(counter_file).rjust(5, '0')}批.txt"
			# 生成书籍文件路径
			book_file_path = os.path.join(book_dir_path, book_file_name)
			# 打开文件并保存书籍内容，若文件存在则不会清空文件
			with open(book_file_path, "a+", encoding="UTF-8") as File:
				File.write(f"{i.chapter_name}\n{i.text}\n")
			# 将章节编号加一
			counter_chapter += 1
			# 检测该文件内保存了多少章节
			if counter_chapter == 10:
				# 若保存了十章，则改变书籍文件编号
				counter_file += 1
				counter_chapter = 0
		# 获取文件夹内每个文件的大小
		file_size_list = [
			os.path.getsize(os.path.join(book_dir_path, one_file_name)) for one_file_name in os.listdir(book_dir_path)
		]
		# 返回文件的大小
		return sum(file_size_list)


class Network(object):
	"""网络请求相关类"""
	# 预定义请求头
	__header = {
		"User-Agent":
			"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
			"(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33",
	}
	# 初始化日志记录器
	__logger = Logger("Novel.Network", "network")
	illegal_character = ["\"", "'", "<", ">", "&", "(", ")", ";", "+", "[", "]", "{", "}"]
	
	def __init__(self, url: str):
		# 保存为类属性
		self.__url = url
		self.__response = requests.Response()
		# 发出请求获取数据
		try:
			self.__response = requests.get(self.__url, headers=self.__header, timeout=21)
		except Exception:
			pass
		if self.__response.status_code is None:
			self.__logger.object.error(f"请求{self.__url}失败")
	
	@staticmethod
	def get_response(url: str) -> "Network":
		"""发出网络请求并将数据保存于该类中
		
		:param url: 目标网址
		:return: 请求的数据，该数据保存于该类中
		"""
		return Network(url)
	
	@staticmethod
	def check_url(url: str) -> bool:  # TODO 优化URL检查函数
		"""检查传入的网址是否合法
		
		:param url: 网址
		:return: 合法返回True，不合法返回False
		"""
		# 检查传入的网址是否为保存为str类型
		if not isinstance(url, str):
			return False
		# 检查网址的长度是否小于12
		if len(url) <= 12:
			return False
		# 检查网址是否以http或https开头
		if url[:4] != "http" and url[:5] != "https":
			return False
		# 检查网址是否包含非法字符
		for i in Network.illegal_character:
			if i in url:
				return False
		# 通过检查则该网址合法
		return True
			
	@property
	def response(self):
		"""获取requests.Response对象，即该次请求的原始相关数据"""
		return self.__response
	
	@property
	def bs(self):
		"""获取请求的网页对象"""
		text = self.__response.text.replace("\xa0", " ").replace("\r", "").replace("\n", "")
		return BeautifulSoup(text, "lxml")
	
	def get_next_url(self, href: str):
		"""通过传入的url获得下一页的url
		
		:param href: url
		:return: 下一页的url
		"""
		# 检查传入的参数是否为str类型
		if not isinstance(href, str):
			return self.__url
		# 检查传入的参数是否为空
		if not href:
			# 为空则返回该网站的主网址
			main_url = urlparse(self.__url)
			return f"{main_url.scheme}://{main_url.netloc}/"
		# 检查该网址是否包含非法字符
		for i in self.illegal_character:
			if i in href:
				main_url = urlparse(self.__url)
				return f"{main_url.scheme}://{main_url.netloc}/"
		# 解析该请求中的网址
		main_url = urlparse(self.__url)
		# 解析传入的网址
		next_url = urlparse(href)
		# 如果开头是反斜杠，则可以认定该参数是一个网址且为绝对路径，直接拼接即可
		if href[0] == "/":
			return f"{main_url.scheme}://{main_url.netloc}{next_url.path}"
		# 如果传入的网址的网站存在且与该次请求的网站不符
		if next_url.netloc and (main_url.netloc != next_url.netloc):
			return self.__url
		# 如果都不是，则该网址为相对路径，直接拼接即可
		return urljoin(self.__url, href)
