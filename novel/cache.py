#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# @FileName  :cache.py
# @Time      :2023/1/14 12:44
# @Author    :Amundsen Severus Rubeus Bjaaland


import time
import copy
import sqlite3
import threading
import traceback
from typing import List, Callable
from urllib.parse import urlparse

from .log import Logger
from .tools import Network
from .config import WebConfig, WebMap
from .object import Book, BookData


class WebUrlManager(object):
	"""网站的所有URL的数据库管理器"""
	
	class UrlState(object):
		"""网站的URL的访问状态"""
		# URL未被下载
		NOT_DOWNLOADED = ("未下载", 1)
		# 网络问题
		NETWORK_ERROR = ("网络错误", 2)
		# URL格式不正确
		FORMAT_ERROR = ("格式不正确", 3)
		# 返回数据不正确
		DATA_ERROR = ("返回的数据不正确", 4)
		# 解析数据出错
		ANALYZE_ERROR = ("数据解析出错", 5)
		# URL已被成功下载
		DOWNLOADED = ("下载成功", 6)
		
		# 所有的状态列表
		STATE_LIST = [NOT_DOWNLOADED, NETWORK_ERROR, FORMAT_ERROR, DATA_ERROR, ANALYZE_ERROR, DOWNLOADED]
	
	# 创建表的SQL语句
	CREATE_TABLE_SENTENCE_1 = """CREATE TABLE URLS(
		ID             INTEGER PRIMARY KEY AUTOINCREMENT,
		URL_PATH       TEXT    NOT NULL UNIQUE,
		STATE          INTEGER NOT NULL DEFAULT 1 CHECK(1 <= STATE <= 6),
		IS_BOOK_URL    INTEGER NOT NULL DEFAULT 0 CHECK(IS_BOOK_URL=0 OR IS_BOOK_URL=1),
		IS_CHAPTER_URL INTEGER NOT NULL DEFAULT 0 CHECK(IS_CHAPTER_URL=0 OR IS_CHAPTER_URL=1)
	)"""
	CREATE_TABLE_SENTENCE_2 = """CREATE TABLE BOOKS(
		ID     INTEGER PRIMARY KEY AUTOINCREMENT,
		NAME   TEXT    NOT NULL,
		AUTHOR TEXT    NOT NULL,
		STATE  INTEGER NOT NULL,
		SOURCE TEXT    NOT NULL,
		DESC   TEXT    NOT NULL
	)"""
	
	def __init__(self, web_config: WebConfig, db_object, lock: threading.Lock):
		"""初始化网站URL管理器对象"""
		# 创建或连接到网站对应的数据库
		self.__db_file = db_object
		# 保存网站设置
		self.__web_config = web_config
		# 创建表名，包括网址表和书籍表
		prefix = f"A{web_config.main_url.split('.')[1]}"
		self.__url_table_name = f"{prefix}_URLS".upper()
		self.__book_info_table_name = f"{prefix}_BOOKS".upper()
		# 创建日志记录器对象
		self.__logger = Logger("Novel.Web.DBManager.WebUrlManager", "engine")
		# 创建线程锁，防止数据库被多线程访问
		self.__lock = lock
		# 创建URL存储表格
		self.__create_table()
	
	def __del__(self):
		self.__db_file.close()
	
	@property
	def config(self):
		return self.__web_config
	
	def __create_table(self):
		self.__lock.acquire()
		cursor = self.__db_file.cursor()
		try:
			result = cursor.execute(
				f"""SELECT * FROM sqlite_master WHERE type='table' AND name='{self.__url_table_name}'"""
			).fetchall()
			if not result:
				cursor.execute(self.CREATE_TABLE_SENTENCE_1.replace("URLS", self.__url_table_name))
				self.__db_file.commit()
			result = cursor.execute(
				f"""SELECT * FROM sqlite_master WHERE type='table' AND name='{self.__book_info_table_name}'"""
			).fetchall()
			if not result:
				cursor.execute(self.CREATE_TABLE_SENTENCE_2.replace("BOOKS", self.__book_info_table_name))
				self.__db_file.commit()
		except Exception:
			self.__db_file.rollback()
			self.__logger.object.critical(f"初始化URL数据库失败:\n{traceback.format_exc()}")
		finally:
			cursor.close()
			self.__lock.release()
	
	def append_urls(self, urls: List[str]):
		self.__lock.acquire()
		cursor = self.__db_file.cursor()
		try:
			for one_url in urls:
				url_path = urlparse(one_url).path
				if not url_path:
					continue
				result = cursor.execute(
					f"""SELECT * FROM {self.__url_table_name} WHERE URL_PATH=?""",
					(url_path,)
				).fetchall()
				if not result:
					book_flag = 1 if self.__web_config.book_url_pattern.match(url_path) else 0
					chapter_flag = 1 if self.__web_config.chapter_url_pattern.match(url_path) else 0
					download_flag = 6 if chapter_flag else 1
					cursor.execute(
						f"""INSERT INTO {self.__url_table_name} VALUES (?,?,?,?,?)""",
						(None, url_path, download_flag, book_flag, chapter_flag)
					)
			self.__db_file.commit()
		except Exception:
			self.__db_file.rollback()
			self.__logger.object.warning(f"添加URL失败:\n{traceback.format_exc()}")
		finally:
			cursor.close()
			self.__lock.release()
	
	def append_book(self, book: BookData):
		cursor = self.__db_file.cursor()
		self.__lock.acquire()
		try:
			cursor.execute(
				f"""INSERT INTO {self.__book_info_table_name} VALUES (?,?,?,?,?,?)""",
				(None, book.name, book.author, book.state[1], book.source, book.desc)
			)
			self.__db_file.commit()
		except Exception:
			self.__db_file.rollback()
			self.__logger.object.warning(f"添加书籍失败:\n{traceback.format_exc()}")
		finally:
			cursor.close()
			self.__lock.release()
	
	def get_url(self):
		self.__lock.acquire()
		cursor = self.__db_file.cursor()
		new_url = ""
		try:
			result = cursor.execute(
				f"""SELECT ID, URL_PATH FROM {self.__url_table_name} WHERE STATE=1 AND IS_CHAPTER_URL=0"""
			).fetchone()
			if result is not None:
				new_url = result[1]
		except Exception:
			self.__db_file.rollback()
			self.__logger.object.warning(f"获取URL数据失败:\n{traceback.format_exc()}")
		finally:
			cursor.close()
			self.__lock.release()
		return new_url
	
	def get_books(self):
		self.__lock.acquire()
		cursor = self.__db_file.cursor()
		book_list = []
		try:
			data_list = cursor.execute(f"""SELECT * FROM {self.__book_info_table_name}""").fetchall()
			book_list = [Book(i[1], i[2], Book.BookState.transform(i[3]), i[4], i[5]) for i in data_list]
		except Exception:
			self.__db_file.rollback()
			self.__logger.object.warning(f"添加书籍失败:\n{traceback.format_exc()}")
		finally:
			cursor.close()
			self.__lock.release()
		return book_list
	
	def search_books(self, name: str = ""):
		self.__lock.acquire()
		cursor = self.__db_file.cursor()
		book_list = []
		try:
			data_list = cursor.execute(
				f"""SELECT * FROM {self.__book_info_table_name} WHERE NAME LIKE ?""", 
				("%" + "%".join([i for i in name]) + "%",)
			).fetchall()
			book_list = [Book(i[1], i[2], Book.BookState.transform(i[3]), i[4], i[5]) for i in data_list]
		except Exception:
			self.__db_file.rollback()
			self.__logger.object.warning(f"添加书籍失败:\n{traceback.format_exc()}")
		finally:
			cursor.close()
			self.__lock.release()
		return book_list
	
	def sign_url(self, url: str, state: tuple):
		if state not in self.UrlState.STATE_LIST:
			return None
		self.__lock.acquire()
		cursor = self.__db_file.cursor()
		try:
			cursor.execute(f"""UPDATE {self.__url_table_name} SET STATE=? WHERE URL_PATH=?""", (state[1], urlparse(url).path))
			self.__db_file.commit()
			cursor.close()
		except Exception:
			self.__db_file.rollback()
			self.__logger.object.error(f"无法将该URL({url})标记为{state[0]}:\n{traceback.format_exc()}")
		finally:
			cursor.close()
			self.__lock.release()
	
	def transform_url(self):
		self.__lock.acquire()
		cursor = self.__db_file.cursor()
		try:
			cursor.execute(f"""UPDATE {self.__url_table_name} SET STATE=1 WHERE STATE=2""")
			self.__db_file.commit()
			cursor.close()
		except Exception:
			self.__db_file.rollback()
			self.__logger.object.error(f"无法将网络错误的URL转换为未下载:\n{traceback.format_exc()}")
		finally:
			cursor.close()
			self.__lock.release()
	
	def count(self):
		self.__lock.acquire()
		cursor = self.__db_file.cursor()
		all_number = 0
		downloaded_number = 0
		book_number = 0
		try:
			all_number = cursor.execute(f"""SELECT COUNT(*) FROM {self.__url_table_name}""").fetchall()[0][0]
			downloaded_number = cursor.execute(f"""SELECT COUNT(*) FROM {self.__url_table_name} WHERE STATE=6""").fetchall()[0][0]
			book_number = cursor.execute(f"""SELECT COUNT(*) FROM {self.__url_table_name} WHERE IS_BOOK_URL=1""").fetchall()[0][0]
		except Exception:
			self.__db_file.rollback()
			self.__logger.object.critical(f"获取URL数目数据失败:\n{traceback.format_exc()}")
		finally:
			cursor.close()
			self.__lock.release()
		return all_number, downloaded_number, book_number


class UrlGetter(object):
	def __init__(
			self, map: WebMap, db_path: str = "./data/book_info.db",
			db_state_callback: Callable[[WebConfig, int, int, int], None] =
			lambda a, b, c, d: print(f"{a.name}: 已找到{b}个网址，已下载{c}个网址，找到书籍网址{d}个。"),
			url_state_callback: Callable[[WebConfig, str, str], None] =
			lambda a, b, c: print(f"{a.name}: {b} {c}!"),
	):
		# 连接到数据库
		self.__db = sqlite3.connect(db_path, check_same_thread=False)
		# 全局同步机制
		self.__lock = threading.Lock()
		# 将Map对象添加入属性
		self.__map = map
		self.__manager_list = [WebUrlManager(i.config, self.__db, self.__lock) for i in self.__map.web_list]
		# 设置回调函数
		self.__db_state_callback = db_state_callback
		self.__url_state_callback = url_state_callback
		# 初始化线程容器
		self.__thread_list = []
		# 初始化状态控制标志
		self.__finished_flag = False
		self.__pause_flag = False
		# 启动下载线程并加入线程容器
		for i in self.__manager_list:
			# 加入线程容器
			get_url_thread = threading.Thread(target=self.__get_urls, args=(i,), name=f"Thread-{i.config.name}")
			self.__thread_list.append(get_url_thread)
	
	def start(self):
		for get_url_thread in self.__thread_list:
			get_url_thread.start()

	def pause(self):
		self.__pause_flag = True
	
	def unpause(self):
		self.__pause_flag = False
	
	def join(self):
		for i in self.__thread_list:
			i.join()
	
	def finish(self):
		self.__finished_flag = True
		for i in self.__thread_list:
			i.join()
		del self
	
	def search(self, book_name: str):
		book_buffer = []
		for i in self.__manager_list:
			book_list = i.search_books(book_name)
			for ii in book_list:
				book_buffer.append(ii)
		return book_buffer
	
	def db_info(self):
		info_buffer = []
		for i in self.__manager_list:
			info_buffer.append({"Name": i.config.name, "Info": i.count()})
		return info_buffer
	
	def __get_urls(self, db_manager: WebUrlManager):
		"""获取网站的所有URL"""
		config = db_manager.config
		# 向数据库添加网站的主网址
		db_manager.append_urls([f"http://{config.main_url}/"])
		# 反复进行URL获取动作
		while True:
			# 检测是否需要退出
			if self.__finished_flag:
				break
			# 检测是否需要暂停
			if self.__pause_flag:
				time.sleep(1)
				continue
			# 从数据库中取出第一个可被下载的URL
			current_url = db_manager.get_url()
			# 若未获取到数据则说明网站的所有URL均被访问过，该函数将退出
			if not current_url:
				db_manager.transform_url()
				current_url = db_manager.get_url()
				if not current_url:
					break
			current_url = f"http://{config.main_url}{current_url}"
			# 检查该URL是否合法
			if not Network.check_url(current_url):
				db_manager.sign_url(current_url, db_manager.UrlState.FORMAT_ERROR)
				self.__url_state_callback(
					copy.deepcopy(config), current_url, db_manager.UrlState.FORMAT_ERROR[0]
				)
				continue
			# 从网站中获取数据
			data_got_flag = True
			while data_got_flag:
				response = Network.get_response(current_url)
				if bool(response.response.text):
					response.response.encoding = config.encoding
					break
				if not config.is_protected(response):
					db_manager.sign_url(current_url, db_manager.UrlState.NETWORK_ERROR)
					self.__url_state_callback(
						copy.deepcopy(config), current_url, db_manager.UrlState.NETWORK_ERROR[0]
					)
					data_got_flag = False
				time.sleep(config.wait_time)
			if not data_got_flag:
				continue
			data = response.bs.find_all("a")
			if data is None:
				data = []
			# 获取页面的所有URL
			urls = [response.get_next_url(a_tag.get("href")) for a_tag in data]
			urls = list(filter(lambda x: True if x else False, urls))
			# 将获取的URL添加到数据库中
			db_manager.append_urls(urls)
			if not config.book_url_pattern.match(urlparse(current_url).path):
				db_manager.sign_url(current_url, db_manager.UrlState.DOWNLOADED)
				# self.__url_state_callback(
				# 	copy.deepcopy(config), current_url, db_manager.UrlState.DOWNLOADED[0]
				# )
				self.__db_state_callback(copy.deepcopy(config), *db_manager.count())
				continue
			flag = True
			while flag:
				try:
					response = Network.get_response(current_url)
					book_info = config.get_book_info(response)
				except Exception:
					if not config.is_protected(response):
						db_manager.sign_url(current_url, db_manager.UrlState.ANALYZE_ERROR)
						self.__url_state_callback(
							copy.deepcopy(config), current_url, db_manager.UrlState.ANALYZE_ERROR[0]
						)
						flag = False
				else:
					db_manager.append_book(book_info)
					# 将已访问过的URL进行标记
					db_manager.sign_url(current_url, db_manager.UrlState.DOWNLOADED)
					# self.__url_state_callback(
					# 	copy.deepcopy(config), current_url, db_manager.UrlState.DOWNLOADED[0]
					# )
					self.__db_state_callback(copy.deepcopy(config), *db_manager.count())
					flag = False
