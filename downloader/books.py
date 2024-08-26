#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: objects.py
# @Time: 03/04/2024 17:29
# @Author: Amundsen Severus Rubeus Bjaaland
"""书籍相关的工具，包括书籍对象，章节对象，以及用于内容保存的对象等"""


import os
import copy
import hashlib
from typing import List, Tuple, Union

import yaml
from ebooklib import epub

try:
    from .tools import mkdir
    from .settings import Settings
except ImportError:
    class Settings:
        DATA_DIR = os.path.abspath("./data")
        BOOKS_DIR = os.path.abspath("./data/books")
        BOOKS_CACHE_DIR = os.path.abspath("./data/books/cache")
        BOOKS_STORAGE_DIR = os.path.abspath("./data/books/storage")

    def mkdir(path: str) -> None:
        """创建文件夹，若文件夹已存在则不进行任何操作

        :param path: 要创建的文件的路径
        """
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
finally:
    required_dirs = [
        Settings.DATA_DIR, Settings.BOOKS_DIR,
        Settings.BOOKS_CACHE_DIR, Settings.BOOKS_STORAGE_DIR
    ]
    for i in required_dirs:
        mkdir(i)


class Chapter(object):
    class StorageMethod(object):
        MEMORY = ("内存", 1)
        DISK = ("磁盘", 2)

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
                self.__dir_path = \
                    os.path.join(
                        Settings.BOOKS_CACHE_DIR,
                        book_name
                    )
                mkdir(self.__dir_path)
                self.__file_path = os.path.join(self.__dir_path, f"{name}.txt")
                with open(self.__file_path, "w", encoding="UTF-8") as txt_file:
                    txt_file.write("\n".join(text))
            case _:
                self.__content = list(text)
                self.__storage_method = self.StorageMethod.MEMORY

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return f"第{self.str_index}章" \
            f" {self.__name}\n{self.text}\n\n"

    def __repr__(self):
        return f"<Chapter index={self.__index} " \
            f"name={self.__name} book_name={self.__book_name}>"

    def __hash__(self):
        text = f"{self.str_index}" \
            f"{self.name}{self.book_name}".encode()
        sha256_hash = hashlib.sha256(text)
        hash_value = sha256_hash.hexdigest()
        return int(hash_value, 16)

    def __eq__(self, other: "Chapter"):
        if (isinstance(other, Chapter) and
            (hash(self) == hash(other))):
            return True
        return False

    @property
    def name(self):
        return self.__name

    @property
    def index(self):
        return self.__index
    
    @property
    def str_index(self):
        return str(self.__index).rjust(4, '0')

    @property
    def source(self):
        return self.__source

    @property
    def book_name(self):
        return self.__book_name

    @property
    def text(self) -> str:
        match self.__storage_method:
            case self.StorageMethod.MEMORY:
                assert isinstance(self.__content, list)
                return "\t" + "\n\t".join(self.__content)
            case self.StorageMethod.DISK:
                with open(
                    self.__file_path, "r", encoding="UTF-8"
                ) as txt_file:
                    content = txt_file.readlines()
                return "\t" + "\n\t".join(
                    [i.strip("\n") for i in content]
                )
            case _: return ""

    @text.setter
    def text(self, text: Union[Tuple[str], List[str]]):
        match self.__storage_method:
            case self.StorageMethod.MEMORY:
                self.__content = list(text)
            case self.StorageMethod.DISK:
                with open(
                    self.__file_path, "w", encoding="UTF-8"
                ) as txt_file:
                    txt_file.write("\n".join(text))


class Book(object):
    class State(object):
        """书籍的状态常量"""
        END = ("完结", 1)  # 已完结状态常量
        SERIALIZING = ("连载中", 2)  # 连载中状态常量
        FORECAST = ("预告", 3)  # 预告状态常量
        BREAK = ("断更", 4)

        STATE_LIST = (END, SERIALIZING, FORECAST, BREAK)

        @classmethod
        def transform(cls, number: int):
            for i in cls.STATE_LIST:
                if number == i[1]:
                    return i
            return cls.SERIALIZING
    
    class SaveMethod(object):
        TXT = ("txt文件", 1, "txt")
        EPUB = ("epub文件", 2, "epub")
        PDF = ("pdf文件", 3, "pdf")

        METHOD_LIST = (TXT, EPUB, PDF)

        @classmethod
        def transform(cls, number: int):
            for i in cls.METHOD_LIST:
                if number == i[1]:
                    return i
            return cls.EPUB

    def __init__(
            self, name: str, author: str, state: tuple,
            source: str, desc: str = "", cover_image: bytes = b"",
            **other_data
        ):
        self.__name: str = name
        self.__author: str = author
        self.__state: tuple = state
        self.__source: str = source
        self.__desc: str = desc
        self.__cover_image: bytes = cover_image
        try:
            self.__other_data = other_data
        except NameError:
            self.__other_data = {}
        self.__chapter_list: List[Chapter] = []

    def __len__(self):
        return len(self.__chapter_list)

    def __repr__(self):
        return f"<Book name={self.__name} " \
            f"author={self.__author}>"

    def __hash__(self):
        text = f"{self.name}{self.author}".encode()
        sha256_hash = hashlib.sha256(text)
        hash_value = sha256_hash.hexdigest()
        return int(hash_value, 16)

    def __eq__(self, other: "Book"):
        if (isinstance(other, Book) and
            (hash(self) == hash(other))):
            return True
        return False

    @property
    def index_list(self) -> List[int]:
        index_list = [
            i.index for i in self.__chapter_list
        ]
        index_list.sort()
        return index_list
    
    @property
    def chapter_list(self):
        for i in self.__chapter_list:
            yield i

    def append(self, chapter: Chapter) -> bool:
        if ((chapter.book_name != self.name) or
            (chapter.index in self.index_list)):
            return False
        self.__chapter_list.append(chapter)
        self.__chapter_list = \
            sorted(
                self.__chapter_list, key=lambda x: x.index
            )
        return True
    
    def save(self, method: tuple = SaveMethod.EPUB) -> int:
        saver = Saver(self, method)
        return saver.save()
    
    @property
    def name(self):
        return self.__name

    @property
    def author(self):
        return self.__author

    @property
    def state(self):
        return self.__state

    @property
    def source(self):
        return self.__source

    @property
    def desc(self):
        return self.__desc
    
    @property
    def cover_image(self):
        return self.__cover_image
    
    @property
    def other_data(self):
        return copy.deepcopy(self.__other_data)


class Saver(object):
    def __init__(
        self, book: Book, method: tuple = Book.SaveMethod.EPUB
    ):
        self.__book = book
        self.__method = method
        self.__path = os.path.join(
            Settings.BOOKS_STORAGE_DIR,
            f"{book.name}.{method[2]}"
        )

    def save(self) -> int:
        match self.__method:
            case Book.SaveMethod.TXT:
                return self.__txt_file()
            case Book.SaveMethod.EPUB:
                return self.__epub_file()
            case Book.SaveMethod.PDF:
                # TODO 完成该分支方法，使保存方式支持PDF文件
                return 0
            case _:
                return 0
    
    def __txt_file(self):
        with open(self.__path, "w", encoding="UTF-8") as txt_file:
            txt_file.write(f"{self.__book.name} - {self.__book.author}\n\n")
            txt_file.write(f"书籍简介:\n\t{self.__book.desc}\n\n")
            for one_chapter in self.__book.chapter_list:
                txt_file.write(str(one_chapter))
        return os.path.getsize(self.__path)
    
    def __epub_file(self):
        book = epub.EpubBook()
        
        book.set_title(self.__book.name)
        book.set_language('zh-CN')
        book.add_author(self.__book.author)
        book.set_cover("image.jpg", self.__book.cover_image)
        book.add_metadata('DC', 'description', self.__book.desc)
        
        if self.__book.other_data:
            yaml_item = epub.EpubItem(
                uid='yaml', file_name='metadata.yaml',
                media_type='application/octet-stream',
                content=yaml.dump(self.__book.other_data)
            )
            book.add_item(yaml_item)
        
        intro_e = epub.EpubHtml(
            title='Introduction', file_name='intro.xhtml', lang='hr'
        )
        intro_e.content = (
            f'<img src="image.jpg" alt="Cover Image"/>'
            f'<h1>{self.__book.name}</h1>'
            f'<p>{self.__book.desc}</p>'
        )
        book.add_item(intro_e)
        
        book.spine = ['nav', intro_e]
        
        for one_chapter in self.__book.chapter_list:
            chapter_text_list = one_chapter.text.strip("\t").split("\n\t")
            text = epub.EpubHtml(
                title=one_chapter.name,
                file_name=f'chapter_{one_chapter.str_index}.xhtml'
            )
            text.content = \
                f'<h2 class="titlecss">{one_chapter.name}</h2>' + \
                ''.join([f"<p>{i}</p>" for i in chapter_text_list])
            book.spine.append(text)
            book.add_item(text)
        
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        epub.write_epub(self.__path, book, {})
        
        return os.path.getsize(self.__path)
        
        
        
