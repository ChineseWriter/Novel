#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: settings.py
# @Time: 05/04/2024 12:20
# @Author: Amundsen Severus Rubeus Bjaaland


import os


class Settings(object):
    DEBUG = False
    DATA_DIR = os.path.abspath(".\\data")
    
    LOG_DIR = os.path.join(DATA_DIR, "logs")
    LOG_FILE_NAME = "logs"
    LOG_FORMAT = "[%(asctime)s]{%(levelname)s} %(name)s (%(filename)s - %(lineno)s):\n\t%(message)s"

    BOOKS_DIR = os.path.join(DATA_DIR, "books")
    BOOKS_DB_PATH = os.path.join(BOOKS_DIR, "bookshelf")
    BOOKS_CACHE_DIR = os.path.join(BOOKS_DIR, "cache")
    BOOKS_STORAGE_DIR = os.path.join(BOOKS_DIR, "storage")

