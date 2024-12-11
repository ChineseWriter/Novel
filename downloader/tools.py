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


class SQLManager(object):
    def __init__(self, db_path: str):
        self.__db_path = db_path
        self.__connection = None
        self.__cursor = None
        self.__lock = Lock()
    
    def __enter__(self):
        self.__lock.acquire()
        assert isinstance(self.__connection, type(None))
        assert isinstance(self.__cursor, type(None))
        self.__connection = sqlite3.connect(self.__db_path)
        self.__cursor = self.__connection.cursor()
        return self.__cursor
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        assert isinstance(self.__cursor, sqlite3.Cursor)
        assert isinstance(self.__connection, sqlite3.Connection)
        self.__cursor.close()
        self.__connection.commit()
        self.__connection.close()
        self.__cursor = None
        self.__connection = None
        self.__lock.release()
        return None