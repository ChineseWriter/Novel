#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: logs.py
# @Time: 03/04/2024 17:32
# @Author: Amundsen Severus Rubeus Bjaaland


import os
import logging
from re import DEBUG

from .settings import Settings


try: os.mkdir(Settings.DATA_DIR)
except FileExistsError: pass
try: os.mkdir(Settings.LOG_DIR)
except FileExistsError: pass


class Logger(object):
    ROOT_NAME = "downloader"
    LOGGER_LIST = ("test", "books")

    def __init__(self):
        self.__root = logging.getLogger(self.ROOT_NAME)
        self.__root.setLevel(logging.DEBUG)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG if Settings.DEBUG else logging.INFO)
        stream_handler.setFormatter(logging.Formatter(Settings.LOG_FORMAT))
        self.__root.addHandler(stream_handler)
        self.__root.addHandler(self.__generate_file_handler(self.ROOT_NAME))

        self.__init_logger()
    
    def __generate_file_handler(self, name: str):
        file_handler = logging.FileHandler(
            os.path.join(Settings.LOG_DIR, f"{name}.dlog"), encoding="UTF-8"
        )
        file_handler.setLevel(logging.DEBUG if Settings.DEBUG else logging.WARNING)
        file_handler.setFormatter(logging.Formatter(Settings.LOG_FORMAT))
        return file_handler
    
    def __init_logger(self):
        for one_logger_name in self.LOGGER_LIST:
            file_handler = self.__generate_file_handler(one_logger_name)
            logger = logging.getLogger(f"{self.ROOT_NAME}.{one_logger_name}")
            logger.addHandler(file_handler)
    
    def __getattr__(self, name: str):
        if name not in self.LOGGER_LIST: raise AttributeError
        return logging.getLogger(f"{self.ROOT_NAME}.{name}")
    
    @property
    def root(self): return self.__root


