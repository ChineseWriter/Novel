#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: objects.py
# @Time: 03/04/2024 17:29
# @Author: Amundsen Severus Rubeus Bjaaland
"""书籍相关的工具，包括书籍对象，章节对象，以及用于内容保存的对象等"""



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


class Book(object):
    pass
