#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: objects.py
# @Time: 03/04/2024 17:29
# @Author: Amundsen Severus Rubeus Bjaaland
"""书籍相关的工具，包括书籍对象，章节对象，以及用于内容保存的对象等"""


import os
import hashlib
from typing import List, Tuple, Union

try:
    from .tools import mkdir
    from .settings import Settings
except ImportError:
    settings_flag = False
    required_dirs = [
        "./data", "./data/books", "./data/books/cache", "./data/books/storage"
    ]
    def mkdir(path: str) -> None:
        """创建文件夹，若文件夹已存在则不进行任何操作
        
        :param path: 要创建的文件的路径
        """
        try: os.makedirs(path)
        except FileExistsError: pass
else:
    settings_flag = True
    required_dirs = [
        Settings.DATA_DIR, Settings.BOOKS_DIR,
        Settings.BOOKS_CACHE_DIR, Settings.BOOKS_STORAGE_DIR
    ]
finally:
    for i in required_dirs: mkdir(i)


class Chapter(object):
    class StorageMethod(object):
        MEMORY = ("内存", 1)
        DISK = ("硬盘", 2)
        
        METHOD_LIST = (MEMORY, DISK)
        
        @classmethod
        def transform(cls, number: int):
            for i in cls.METHOD_LIST:
                if number == i[1]:
                    return i
            return cls.MEMORY
    
    def __init__(
        self, name: str, index: int, source: str,
        book_name: str, text: Tuple = (),
        storage_method: tuple = StorageMethod.MEMORY
    ):
        self.__name: str = name
        self.__index: int = index
        self.__source: str = source
        self.__book_name: str = book_name
        self.__storage_method = storage_method
        self.__content: Union[None, str, List[str]] = None
        match self.__storage_method:
            case self.StorageMethod.MEMORY:
                self.__content = list(text)
            case self.StorageMethod.DISK:
                if settings_flag:
                    self.__file_path = os.path.join(Settings.BOOKS_CACHE_DIR, f"{book_name}\\{name}.txt")
                else:
                    self.__file_path = f"./data/books/cache/{book_name}/{name}.txt"
                with open(self.__file_path, "w", encoding="UTF-8") as txt_file:
                    txt_file.write("\n".join(text))
            case _:
                self.__content = list(text)
                self.__storage_method = self.StorageMethod.MEMORY
    
    def __len__(self): return len(self.text)
    
    def __str__(self):
        return f"第{str(self.__index).rjust(4, '0')}章 {self.__name}\n{self.text}\n\n"
    
    def __repr__(self):
        return f"<Chapter index={self.__index} name={self.__name} book_name={self.__book_name}>"
    
    def __hash__(self):
        text = f"{str(self.__index).rjust(4, '0')}{self.name}{self.book_name}".encode()
        sha256_hash = hashlib.sha256(text)
        hash_value = sha256_hash.hexdigest()
        return int(hash_value, 16)
    
    def __eq__(self, other: "Chapter"):
        if isinstance(other, Chapter) and \
            hash(self) == hash(other):
            return True
        return False
    
    @property
    def name(self): return self.__name
    @property
    def index(self): return self.__index
    @property
    def source(self): return self.__source
    @property
    def book_name(self): return self.__book_name
    
    @property
    def text(self) -> str:
        match self.__storage_method:
            case self.StorageMethod.MEMORY:
                assert isinstance(self.__content, list) 
                return "\n\t".join(self.__content)
            case self.StorageMethod.DISK:
                with open(self.__file_path, "r", encoding="UTF-8") as txt_file:
                    content = txt_file.readlines()
                return "\n\t".join([i.strip("\n") for i in content])
            case _: return ""
    
    @text.setter
    def text(self, text: Union[Tuple[str], List[str]]):
        match self.__storage_method:
            case self.StorageMethod.MEMORY:
                self.__content = list(text)
            case self.StorageMethod.DISK:
                with open(self.__file_path, "w", encoding="UTF-8") as txt_file:
                    txt_file.write("\n".join(text))
        


class Book(object):
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
    
    def __init__(self, name: str, author: str, state: tuple, source: str, desc: str = ""):
        self.__name: str = name
        self.__author: str = author
        self.__state: tuple = state
        self.__source: str = source
        self.__desc: str = desc
        self.__chapter_list: List[Chapter] = []
        
    def __len__(self):
        return len(self.__chapter_list)
    
    def __repr__(self):
        return f"<Book name={self.__name} author={self.__author}>"
    
    def __hash__(self):
        text = f"{self.name}{self.author}{self.state[0]}".encode()
        sha256_hash = hashlib.sha256(text)
        hash_value = sha256_hash.hexdigest()
        return int(hash_value, 16)
    
    def __eq__(self, other: "Book"):
        if isinstance(other, Book) and \
            hash(self) == hash(other):
            return True
        return False
    
    @property
    def name(self): return self.__name
    @property
    def author(self): return self.__author
    @property
    def state(self): return self.__state
    @property
    def source(self): return self.__source
    @property
    def desc(self): return self.__desc
    
    def __index_list(self) -> List[int]:
        index_list = [i.index for i in self.__chapter_list]
        index_list.sort()
        return index_list
    
    def append(self, chapter: Chapter) -> bool:
        if (chapter.book_name != self.name) or \
            (chapter.index in self.__index_list()):
            return False
        self.__chapter_list.append(chapter)
        self.__chapter_list = sorted(self.__chapter_list, key=lambda x: x.index)
        return True


class Saver(object):
    class SaveMethod(object):
        ONE_TXT_FILE = ("一个txt文件", 1)
        MANY_TXT_FILE = ("多个txt文件", 2)
        EPUB = ("epub文件", 3)
        PDF = ("pdf文件", 4)
        
        METHOD_LIST = (ONE_TXT_FILE, MANY_TXT_FILE, EPUB, PDF)
        
        @classmethod
        def transform(cls, number: int):
            for i in cls.METHOD_LIST:
                if number == i[1]:
                    return i
            return cls.EPUB
    
    def __init__(self, ):
        pass
