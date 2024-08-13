#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: settings.py
# @Time: 05/04/2024 12:20
# @Author: Amundsen Severus Rubeus Bjaaland


import os


class Settings(object):
    DATA_DIR = ".\\data"
    DEBUG = True

    LOG_DIR = os.path.join(DATA_DIR, "logs")
    LOG_FORMAT = "[%(asctime)s]{%(levelname)s} %(name)s (%(filename)s - %(lineno)s):\n%(message)s"

    BOOKS_DIR = os.path.join(DATA_DIR, "books")
    BOOKS_CACHE_DIR = os.path.join(BOOKS_DIR, "cache")
    BOOKS_STORAGE_DIR = os.path.join(BOOKS_DIR, "storage")

