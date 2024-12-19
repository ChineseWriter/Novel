#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: tools.py
# @Time: 13/06/2024 17:45
# @Author: Amundsen Severus Rubeus Bjaaland


#导入标准库
import os
import hashlib
import sqlite3
from threading import Lock
from typing import Callable


def mkdir(path: str) -> None:
    """创建文件夹，若文件夹已存在则不进行任何操作
    
    :param path: 要创建的文件的路径
    """
    try: os.makedirs(path)
    except FileExistsError: pass


def str_hash(text: str) -> bytes:
	sha256_hash = hashlib.sha256(text.encode())
	hash_value = sha256_hash.hexdigest()
	return bytes.fromhex(hash_value)


def try_callback(callback: Callable):
    def wrapper(*args, **kwargs):
        try:
            result = callback(*args, **kwargs)
        except Exception:
            result = None
        return result
    return wrapper


class SQLManager(object):
    def __init__(self, db_path: str, check_same_thread: bool = True):
        self.__db_path = db_path
        self.__connection: sqlite3.Connection = sqlite3.connect(
            self.__db_path, check_same_thread=check_same_thread
        )
        self.__cursor = None
        self.__lock = Lock()
    
    def __enter__(self):
        self.__lock.acquire()
        assert isinstance(self.__cursor, type(None))
        self.__cursor = self.__connection.cursor()
        return self.__cursor
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        assert isinstance(self.__cursor, sqlite3.Cursor)
        self.__cursor.close()
        self.__connection.commit()
        self.__cursor = None
        self.__lock.release()
        return None
    
    def __del__(self):
        self.__connection.close()