#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: settings.py
# @Time: 05/04/2024 12:20
# @Author: Amundsen Severus Rubeus Bjaaland


import os
from typing import Literal


class Settings(object):
    DEBUG: Literal[True, False] = False
    DATA_DIR: str = os.path.abspath("data")
    
    MULTI_THREAD: Literal[True, False] = True
    FORCE_RELOAD: Literal[True, False] = False
    
    LOG_DIR: str = os.path.join(DATA_DIR, "logs")
    LOG_MAX_FILE_NUMBER: int = 30
    LOG_FORMAT: str = "[%(asctime)s](%(levelname)s)%(filename)s-%(lineno)s, in %(funcName)s:\n\t%(message)s"
    
    URLS_DIR: str = os.path.join(DATA_DIR, "urls")

    BOOKS_DIR: str = os.path.join(DATA_DIR, "books")
    BOOKS_CACHE_DIR: str = os.path.join(BOOKS_DIR, "cache")
    BOOKS_DB_PATH: str = os.path.join(BOOKS_DIR, "bookshelf.db")
    BOOKS_STORAGE_DIR: str = os.path.join(BOOKS_DIR, "storage")