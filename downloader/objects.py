#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: objects.py
# @Time: 03/04/2024 17:29
# @Author: Amundsen Severus Rubeus Bjaaland


from typing import List
from collections import Counter

from bs4 import BeautifulSoup as bs
from bs4.element import Tag

import jieba


class Chapter(object):
	def __init__(
			self, book_name: str, index: int, chapter_name: str,
			source: str, content: str = ""
		):
		self.__book_name = book_name
		self.__index = index
		self.__chapter_name = chapter_name
		self.__source = source
		self.__content = bs(content, "lxml")
	
	def __str__(self) -> str:
		para_list: List[str] = []
		p_tag_list: List[Tag] = self.__content.find_all("p")
		for p_tag in p_tag_list:
			para_list.append("\t" + p_tag.text)
		text = self.__chapter_name + "\r\n" + \
			"\r\n".join(para_list) + "\r\n"
		return text
	
	def __len__(self) -> int: return len(str(self))

	def __repr__(self) -> str:
		return f"<Chapter book_name={self.__book_name} index={self.__index}" \
				f" chapter_name={self.__chapter_name} length={len(self)}>"
	
	@property
	def book_name(self) -> str: return self.__book_name
	@property
	def index(self) -> int: return self.__index
	@property
	def chapter_name(self) -> str: return self.__chapter_name
	@property
	def source(self) -> str: return self.__source
	@property
	def content(self) -> str: return str(self.__content.find("body"))[6:-7]

	@property
	def word_count(self) -> Counter:
		words = "".join([i.text for i in self.__content.find_all("p")])
		words = jieba.lcut(words)
		word_counter = Counter()
		word_counter.update(words)
		return word_counter
