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

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG if Settings.DEBUG else logging.INFO)
        stream_handler.setFormatter(logging.Formatter(Settings.LOG_FORMAT))
        self.__root.addHandler(stream_handler)

        self.__init_logger()
    
    def __init_logger(self):
        for one_logger_name in self.LOGGER_LIST:
            file_handler = logging.FileHandler(
                os.path.join(Settings.LOG_DIR, f"{one_logger_name}.dlog")
                )
            file_handler.setLevel(logging.WARNING)
            file_handler.setFormatter(logging.Formatter(Settings.LOG_FORMAT))
            
            logger = logging.getLogger(f"{self.ROOT_NAME}.{one_logger_name}")
            logger.addHandler(file_handler)
    
    def __getattr__(self, name: str):
        if name not in self.LOGGER_LIST: raise AttributeError
        return logging.getLogger(f"{self.ROOT_NAME}.{name}")
    
    @property
    def root(self): return self.__root


