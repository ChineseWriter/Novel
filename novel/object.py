#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :object.py
# @Time      :04/09/2022 12:18
# @Author    :Amundsen Severus Rubeus Bjaaland


# 导入Python标准库
import copy
from typing import List

# 导入自定义库
from .log import Logger


class Chapter(object):
	"""书籍的章节对象"""
	
	def __init__(self, book_name: str, index: int, chapter_name: str, source: str, text: str = ""):
		"""初始化章节对象
		
		:param book_name: 该章节所属书籍名称
		:param index: 章节在书中的位置，即第几个
		:param chapter_name: 该章节名称
		:param source: 该章节的源
		:param text: 章节的内容
		"""
		# 强制类型检查
		assert isinstance(book_name, str)
		assert isinstance(index, int)
		assert isinstance(chapter_name, str)
		assert isinstance(source, str)
		assert isinstance(text, str)
		# 添加属性
		self.__book_name = book_name
		self.__index = index
		self.__chapter_name = chapter_name
		self.__source = source
		self.__text = text
	
	def __len__(self):
		return len(self.__text)
	
	def __str__(self):
		return self.__text
	
	def __repr__(self):
		return f"<Chapter book_name={self.__book_name} index={self.__index}" \
				f" chapter_name={self.__chapter_name} length={self.word_count}>"
	
	@property
	def book_name(self):
		"""该章节所属书籍的名称"""
		return self.__book_name
	
	@property
	def index(self):
		"""章节在书中的位置"""
		return self.__index
	
	@property
	def chapter_name(self):
		"""该章节的名称"""
		return self.__chapter_name
	
	@property
	def source(self):
		"""该章节的源"""
		return self.__source
	
	@property
	def text(self):
		"""该章节的内容"""
		return self.__text
	
	@text.setter
	def text(self, string: str):
		# 强制类型检查
		assert isinstance(string, str)
		# 重设属性
		self.__text = string
	
	@property
	def word_count(self):
		"""该章节的字数"""
		return len(self.__text.replace(" ", "").replace("\n", "").replace("\t", ""))


class Book(object):
	"""书籍的书本对象"""
	class BookState(object):
		"""书籍的状态常量"""
		END = ("完结", 1)  # 已完结状态常量
		SERIALIZING = ("连载中", 2)  # 连载中状态常量
		FORECAST = ("预告", 3)  # 预告状态常量
		
		STATE_LIST = (END, SERIALIZING, FORECAST)
		
		@classmethod
		def transform(cls, number: int):
			for i in cls.STATE_LIST:
				if number == i[1]:
					return i
			return cls.SERIALIZING
	
	def __init__(self, book_name: str, author: str, state: tuple, source: str, desc: str = ""):
		"""初始化书本对象
		
		:param book_name: 书籍的名称
		:param author: 书籍的作者
		:param state: 书籍的状态
		:param source: 书籍的源
		:param desc: 书籍的简介
		"""
		# 强制类型检查
		assert isinstance(book_name, str)
		assert isinstance(author, str)
		assert state in self.BookState.STATE_LIST
		assert isinstance(source, str)
		assert isinstance(desc, str)
		# 添加属性
		self.__book_name = book_name
		self.__author = author
		self.__state = state
		self.__source = source
		self.__desc = desc
		# 创建日志记录器对象
		self.__logger = Logger(f"Novel.Object.Book.{book_name}", "book")
		# 创建章节列表对象
		self.__chapter_list: List[Chapter] = []
	
	@staticmethod
	def from_book_data(book_data: "BookData"):
		return Book(
			book_name=book_data.name,
			author=book_data.author,
			state=book_data.state,
			source=book_data.source,
            desc=book_data.desc
		)
	
	def __len__(self):
		return len(self.__chapter_list)
	
	def __str__(self):
		return f"简介\n\t{self.__desc}\n\n" + \
			"".join([f"{one_chapter.chapter_name}\n{one_chapter.text}\n" for one_chapter in self.__chapter_list])
	
	def __repr__(self):
		return f"<Book book_name={self.__book_name} author={self.__author} chapter_number={len(self.__chapter_list)}>"
	
	def __hash__(self):
		return hash((self.__book_name, self.__author))
	
	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return other.__hash__() == self.__hash__()
		return False
	
	def append(self, chapter: Chapter) -> bool:
		"""向书中添加章节"""
		# 强制类型检查
		assert isinstance(chapter, Chapter)
		# 检查章节所属名称是否与书籍名对应
		if chapter.book_name != self.__book_name:
			self.__logger.object.warning(f"章节所属书籍名称({chapter.book_name})与书籍名称({self.__book_name})不匹配。")
			return False
		# 检查指定章节编号是否已存在
		if chapter.index in [i.index for i in self.__chapter_list]:
			self.__logger.object.warning(f"章节的编号({chapter.index})已经存在。")
			return False
		# 添加章节至章节列表
		self.__chapter_list.append(chapter)
		self.__logger.object.debug(f"向书籍({self.__book_name})添加章节({chapter.chapter_name})成功。")
		return True
	
	@property
	def chapter_list(self):
		"""书籍的章节列表"""
		for one_chapter in self.__chapter_list:
			# 返回章节对象的拷贝，防止被意外更改
			yield copy.deepcopy(one_chapter)
	
	@property
	def book_name(self):
		"""书籍名称"""
		return self.__book_name
	
	@property
	def author(self):
		"""书籍的作者"""
		return self.__author
	
	@property
	def state(self):
		"""书籍的状态常量"""
		return self.__state
	
	@property
	def source(self):
		"""书籍的源"""
		return self.__source
	
	@property
	def desc(self):
		"""书籍的简介"""
		return self.__desc


class BookData(object):
	"""解析完毕后的书籍数据"""
	def __init__(self, name: str, author: str, state: tuple, desc: str, source: str, chapter_list: List[tuple]):
		# 强制类型检查
		assert isinstance(name, str)
		assert isinstance(author, str)
		assert state in Book.BookState.STATE_LIST
		assert isinstance(desc, str)
		assert isinstance(source, str)
		assert isinstance(chapter_list, list)
		for one_chapter_info in chapter_list:
			assert isinstance(one_chapter_info, tuple)
		# 添加属性
		self.name = name
		self.author = author
		self.state = state
		self.desc = desc
		self.source = source
		self.chapter_list = chapter_list  # tuple的两项，第一项是网址，第二项是名称
		

class ChapterData(object):
	"""解析完毕后的章节数据"""
	def __init__(self, index: int, text: str):
		# 强制类型检查
		assert isinstance(index, int)
		assert isinstance(text, str)
		# 添加属性
		self.index = index
		self.text = text
