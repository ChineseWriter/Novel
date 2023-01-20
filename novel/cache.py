#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# @FileName  :cache.py
# @Time      :2023/1/14 12:44
# @Author    :Amundsen Severus Rubeus Bjaaland
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
		HASH           INTEGER NOT NULL UNIQUE,
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
	
	def __init__(self, web_config: WebConfig, db_path: str):
		"""初始化网站URL管理器对象"""
		# 创建或连接到网站对应的数据库
		self.__db_file = sqlite3.connect(db_path, check_same_thread=False)
		# 保存网站设置
		self.__web_config = web_config
		# 创建日志记录器对象
		self.__logger = Logger("Novel.Web.DBManager.WebUrlManager", "engine")
		# 创建线程锁，防止数据库被多线程访问
		self.__lock = threading.Lock()
		# 创建URL存储表格
		self.__create_table()
	
	def __del__(self):
		self.__db_file.close()
	
	def __create_table(self):
		cursor = self.__db_file.cursor()
		self.__lock.acquire()
		try:
			result = cursor.execute("""SELECT * FROM sqlite_master WHERE type='table' AND name='URLS'""").fetchall()
			if not result:
				cursor.execute(self.CREATE_TABLE_SENTENCE_1)
				self.__db_file.commit()
			result = cursor.execute("""SELECT * FROM sqlite_master WHERE type='table' AND name='BOOKS'""").fetchall()
			if not result:
				cursor.execute(self.CREATE_TABLE_SENTENCE_2)
				self.__db_file.commit()
			cursor.close()
		except Exception:
			self.__db_file.rollback()
			cursor.close()
			self.__logger.object.critical(f"初始化URL数据库失败:\n{traceback.format_exc()}")
			raise  # TODO 定义需要的错误类型
		finally:
			self.__lock.release()
			return None
	
	def append_urls(self, urls: List[str]):
		cursor = self.__db_file.cursor()
		self.__lock.acquire()
		try:
			for one_url in urls:
				url_path = urlparse(one_url).path
				url_hash = hash(url_path)
				result = cursor.execute("""SELECT * FROM URLS WHERE HASH=?""", (url_hash,)).fetchall()
				if not result:
					book_flag = 1 if self.__web_config.re_book_url_pattern.match(url_path) else 0
					chapter_flag = 1 if self.__web_config.re_chapter_url_pattern.match(url_path) else 0
					download_flag = 6 if chapter_flag else 1
					cursor.execute(
						"""INSERT INTO URLS VALUES (?,?,?,?,?,?)""",
						(None, url_path, url_hash, download_flag, book_flag, chapter_flag)
					)
			self.__db_file.commit()
			cursor.close()
		except Exception:
			self.__db_file.rollback()
			self.__logger.object.warning(f"添加URL失败:\n{traceback.format_exc()}")
		finally:
			cursor.close()
			self.__lock.release()
			return None
	
	def append_book(self, book: BookData):
		cursor = self.__db_file.cursor()
		self.__lock.acquire()
		try:
			cursor.execute(
				"""INSERT INTO BOOKS VALUES (?,?,?,?,?,?)""",
				(None, book.name, book.author, book.state[1], book.source, book.desc)
			)
			self.__db_file.commit()
			cursor.close()
		except Exception:
			self.__db_file.rollback()
			self.__logger.object.warning(f"添加书籍失败:\n{traceback.format_exc()}")
		finally:
			cursor.close()
			self.__lock.release()
			return None
	
	def get_url(self):
		cursor = self.__db_file.cursor()
		self.__lock.acquire()
		new_url = ""
		try:
			while True:
				result = cursor.execute(
					"""SELECT ID, URL_PATH FROM URLS WHERE STATE=1 AND IS_CHAPTER_URL=0"""
				).fetchone()
				if result is None:
					break
				if not result[1]:
					cursor.execute("""UPDATE URLS SET STATE=3 WHERE ID=?""", (result[0],))
					self.__db_file.commit()
				if result:
					new_url = result[1]
					break
			cursor.close()
		except Exception:
			self.__db_file.rollback()
			self.__logger.object.warning(f"获取URL数据失败:\n{traceback.format_exc()}")
		finally:
			cursor.close()
			self.__lock.release()
			return new_url
	
	def get_books(self):
		cursor = self.__db_file.cursor()
		self.__lock.acquire()
		book_list = []
		try:
			data_list = cursor.execute("""SELECT * FROM BOOKS""").fetchall()
			book_list = [Book(i[1], i[2], Book.BookState.transform(i[3]), i[4], i[5]) for i in data_list]
			cursor.close()
		except Exception:
			self.__db_file.rollback()
			self.__logger.object.warning(f"添加书籍失败:\n{traceback.format_exc()}")
		finally:
			cursor.close()
			self.__lock.release()
			return book_list
	
	def search_books(self, name: str = ""):
		cursor = self.__db_file.cursor()
		self.__lock.acquire()
		book_list = []
		try:
			data_list = cursor.execute("""SELECT * FROM BOOKS WHERE NAME LIKE ?""", (name + "%",)).fetchall()
			book_list = [Book(i[1], i[2], Book.BookState.transform(i[3]), i[4], i[5]) for i in data_list]
			cursor.close()
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
		cursor = self.__db_file.cursor()
		self.__lock.acquire()
		try:
			cursor.execute("""UPDATE URLS SET STATE=? WHERE HASH=?""", (state[1], hash(urlparse(url).path)))
			self.__db_file.commit()
			cursor.close()
		except Exception:
			self.__db_file.rollback()
			self.__logger.object.error(f"无法将该URL({url})标记为{state[0]}:\n{traceback.format_exc()}")
		finally:
			cursor.close()
			self.__lock.release()
			return None
	
	def transform_url(self):
		cursor = self.__db_file.cursor()
		self.__lock.acquire()
		try:
			cursor.execute("""UPDATE URLS SET STATE=1 WHERE STATE=2""")
			self.__db_file.commit()
			cursor.close()
		except Exception:
			self.__db_file.rollback()
			self.__logger.object.error(f"无法将网络错误的URL转换为未下载:\n{traceback.format_exc()}")
		finally:
			cursor.close()
			self.__lock.release()
			return None
	
	def count(self):
		cursor = self.__db_file.cursor()
		self.__lock.acquire()
		all_number = 0
		downloaded_number = 0
		book_number = 0
		try:
			all_number = cursor.execute("""SELECT COUNT(*) FROM URLS""").fetchall()[0][0]
			downloaded_number = cursor.execute("""SELECT COUNT(*) FROM URLS WHERE STATE=6""").fetchall()[0][0]
			book_number = cursor.execute("""SELECT COUNT(*) FROM URLS WHERE IS_BOOK_URL=1""").fetchall()[0][0]
			cursor.close()
		except Exception:
			self.__db_file.rollback()
			self.__logger.object.critical(f"获取URL数目数据失败:\n{traceback.format_exc()}")
		finally:
			cursor.close()
			self.__lock.release()
			return all_number, downloaded_number, book_number


class UrlGetter(object):
	def __init__(
			self, web_config: WebConfig,
			db_state_callback: Callable[[WebConfig, int, int, int], None] =
			lambda a, b, c, d: print(f"{a.name}: 已找到{b}个网址，已下载{c}个网址，找到书籍网址{d}个。"),
			url_state_callback: Callable[[WebConfig, str, str], None] =
			lambda a, b, c: print(f"{a.name}: {b} {c}!"),
	):
		self.__web_config = web_config
		self.__book_url_pattern = re.compile(web_config.book_url_pattern)
		self.__url_state_callback = url_state_callback
		self.__db_state_callback = db_state_callback
		self.__db_manager = WebUrlManager(self.__web_config, f"./data/book_info/{web_config.name}.db")
		self.__pause_flag = True
		self.__finished_flag = False
		self.__url_get_thread = None
	
	def start(self):
		if self.__url_get_thread is None:
			self.__url_get_thread = threading.Thread(target=self.get_urls, name=f"{self.__web_config.name} URL检索线程")
			self.__url_get_thread.start()
		self.__pause_flag = False
	
	def pause(self):
		self.__pause_flag = True
	
	def unpause(self):
		self.__pause_flag = False
	
	def wait(self):
		self.__url_get_thread.join()
	
	def finish(self):
		self.__finished_flag = True
	
	def get_books(self):
		return self.__db_manager.get_books()
	
	def search_books(self, name):
		return self.__db_manager.search_books(name)
	
	def get_urls(self):
		"""获取网站的所有URL"""
		# 向数据库添加网站的主网址
		self.__db_manager.append_urls([f"http://{self.__web_config.main_url}/"])
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
			current_url = self.__db_manager.get_url()
			# 若未获取到数据则说明网站的所有URL均被访问过，该函数将退出
			if not current_url:
				self.__db_manager.transform_url()
				current_url = self.__db_manager.get_url()
				if not current_url:
					break
				else:
					continue
			current_url = f"http://{self.__web_config.main_url}{current_url}"
			# 检查该URL是否合法
			if not check_url(current_url):
				self.__db_manager.sign_url(current_url, self.__db_manager.UrlState.FORMAT_ERROR)
				self.__url_state_callback(
					copy.deepcopy(self.__web_config), current_url, self.__db_manager.UrlState.FORMAT_ERROR[0]
				)
				continue
			# 从网站中获取数据
			try:
				response = get_response(current_url)
				response.response.encoding = self.__web_config.encoding
			except Exception:
				self.__db_manager.sign_url(current_url, self.__db_manager.UrlState.NETWORK_ERROR)
				self.__url_state_callback(
					copy.deepcopy(self.__web_config), current_url, self.__db_manager.UrlState.NETWORK_ERROR[0]
				)
				continue
			# 检查数据获取是否成功或数据是否为HTML
			if not response.response.status_code:
				self.__db_manager.sign_url(current_url, self.__db_manager.UrlState.DATA_ERROR)
				self.__url_state_callback(
					copy.deepcopy(self.__web_config), current_url, self.__db_manager.UrlState.DATA_ERROR[0]
				)
				continue
			# 获取页面的所有URL
			urls = [response.get_next_url(a_tag.get("href")) for a_tag in response.BS.find_all("a")]
			# 将获取的URL添加到数据库中
			self.__db_manager.append_urls(urls)
			if self.__book_url_pattern.match(urlparse(current_url).path):
				self.__db_manager.append_book(self.__web_config.get_book_info(response))
			# 将已访问过的URL进行标记
			self.__db_manager.sign_url(current_url, self.__db_manager.UrlState.DOWNLOADED)
			self.__url_state_callback(
				copy.deepcopy(self.__web_config), current_url, self.__db_manager.UrlState.DOWNLOADED[0]
			)
			self.__db_state_callback(copy.deepcopy(self.__web_config), *self.__db_manager.count())