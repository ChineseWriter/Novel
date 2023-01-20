#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :log.py
# @Time      :03/09/2022 11:50
# @Author    :Amundsen Severus Rubeus Bjaaland
"""为整个项目提供日志支持"""


# 导入标准库logging，用于记录日志
import logging


class Logger(object):
	"""包装日志记录器，使其易于使用"""
	def __init__(self, logger_name: str, file_name: str = "info"):
		"""日志记录器初始化方法
		
		:param logger_name: 日志记录器的层级名称
		:param file_name: 日志文件名称
		"""
		# 获取标准库中的记录器
		self.__logger = logging.getLogger(logger_name)
		# 设置日志记录器级别为DEBUG
		self.__logger.setLevel(logging.DEBUG)
		# 使子记录器的日志不向父记录器传递
		self.__logger.propagate = False
		
		# 设置日志记录的格式
		self.__formatter = logging.Formatter(
			"[%(asctime)s](%(levelname)s){%(name)s: %(filename)s, %(funcName)s, %(lineno)d} %(message)s"
		)
		# 创建命令行日志显示器
		self.__stream_handler = logging.StreamHandler()
		# 创建日志文件写入器
		self.__file_handler = logging.FileHandler(f"data/log/{file_name}.log", encoding="UTF-8")
		# 设置命令行日志显示器的日志级别
		self.__stream_handler.setLevel(logging.INFO)
		# 设置日志文件写入器的日志级别
		self.__file_handler.setLevel(logging.WARNING)
		# 设置日志处理器的日志格式
		self.__stream_handler.setFormatter(self.__formatter)
		self.__file_handler.setFormatter(self.__formatter)
		
		# 向日志记录器添加定义好的日志处理器
		self.__logger.addHandler(self.__stream_handler)
		self.__logger.addHandler(self.__file_handler)
		# TODO 使同一条日志不会被记录多次
	
	@property
	def object(self):
		"""获取日志记录器对象以便进行日志相关操作"""
		return self.__logger
