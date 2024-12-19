#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: objects.py
# @Time: 03/04/2024 17:29
# @Author: Amundsen Severus Rubeus Bjaaland
"""书籍相关的工具, 包括书籍对象, 章节对象, 以及用于内容保存的对象等"""


# 导入标准库
import os
import io
import copy
import hashlib
from enum import Enum
from threading import Lock
from typing import List, Tuple, Any, Iterable

# 导入第三方库
import yaml  # 该库用 pip 安装时的名称为 pyyaml
from ebooklib import epub
from PIL import Image

# 导入自定义库
from .tools import mkdir
from .logs import Logger
from .settings import Settings


# 初始化程序常量和必要函数
_EMPTY_TIP = "段落内容为空"


# Windows 路径中所有非法字符及其替代方案
ILLEGAL_CHARS = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
ILLEGAL_CHARS_REP = ['＜', '＞', '：', '＂', '／', '＼', '｜', '？', '＊']


def _replace_illegal_chars(text: str) -> str:
    """替换非法字符
    
    :param text: 将要检查的字符串
    :type text: str
    
    Example:
        >>> _replace_illegal_chars("测试字符串")
    """
    # 检查每一个非法字符的存在情况, 如果存在则替换掉
    for char, char_rep in zip(ILLEGAL_CHARS, ILLEGAL_CHARS_REP):
        text = text.replace(char, char_rep)
    # 返回替换以后的字符串
    return text


class Chapter(object):
    class StorageMethod(Enum):
        """章节的存储方式常量"""
        # 设置必要的存储常量
        MEMORY = ("内存", 1)
        DISK = ("磁盘", 2)

        @classmethod
        def transform(cls, number: int):
            """将常量的 id 转换为常量
            若常量 id 不存在, 则使用默认值, 存储在内存中
            
            :param number: 常量 id
            :type number: int
            
            Example:
                >>> Chapter.StorageMethod.transform(1)
                >>> Chapter.StorageMethod.transform(2)
                >>> Chapter.StorageMethod.transform(3)
            """
            # 尝试查找匹配的常量
            for i in list(cls):
                if number == i.value[1]:
                    return i
            # 若没有常量的结果和参数匹配, 则返回默认值
            return cls.MEMORY

    def __init__(
        self, name: str, index: int, source: str,
        book_name: str, content: Iterable[str] = (_EMPTY_TIP, ),
        storage_method: StorageMethod = StorageMethod.MEMORY
    ):
        """书籍的章节对象
        
        :param name: 章节的名称
        :type name: str
        :param index: 章节的序号
        :type index: int
        :param source: 章节的源网址
        :type source: str
        :param book_name: 章节所属的书籍名
        :type book_name: str
        :param content: 章节的内容, 要求每段为一个 str , 所有段落的 str 组成一个 tuple
        :type content: Iterable[str]
        :param storage_method: 章节的存储方式
        :type storage_method: tuple
        
        Example:
            >>> Chapter("测试章节", 1, "https://example.com/", "测试书籍")
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(name, str)
        assert isinstance(index, int)
        assert isinstance(source, str)
        assert isinstance(book_name, str)
        assert isinstance(storage_method, self.StorageMethod)
        buffer = []
        for i in content:
            if isinstance(i, str):
                buffer.append(i)
        # 初始化日志记录器
        self.__logger = Logger()
        # 初始化数据
        self.__name: str = _replace_illegal_chars(name)
        self.__index: int = index
        self.__source: str = source
        self.__book_name: str = _replace_illegal_chars(book_name)
        self.__storage_method = storage_method
        # 初始化章节内容存储变量
        self.__content: List[str] = []
        self.__dir_path = ""
        self.__file_path = ""
        # 为每种存储方式设置对应的内容存储变量
        match self.__storage_method:
            # 使用内存存储则将段落内容数据转换为 list 即可, 便于内容的增改
            case self.StorageMethod.MEMORY:
                self.__content = buffer
            # 使用磁盘存储则进行以下一系列操作
            case self.StorageMethod.DISK:
                # 依据书籍名创建章节缓存目录, 即所有数据按照书籍名分区
                self.__dir_path = \
                    os.path.join(Settings.BOOKS_CACHE_DIR, book_name)
                mkdir(self.__dir_path)
                # 在对应书籍缓存目录下创建该章节的缓存文件, 并将章节内容写入
                self.__file_path = os.path.join(self.__dir_path, f"{name}.txt")
                with open(self.__file_path, "w", encoding="UTF-8") as txt_file:
                    txt_file.write("\n".join(buffer))
        self.__logger.debug(
            f"使用{self.__storage_method.value[0]}存储方式保存了章节({self.__name})内容."
        )
        self.__logger.debug(f"创建了名为'{self.__name}'的章节.")
    
    def __len__(self):
        return len(self.text)

    def __str__(self):
        return f"第{self.str_index}章 " \
            f"{self.__name}\n{self.text}\n\n"

    def __repr__(self):
        return f"<Chapter index={self.__index} name={self.__name} " \
            f"len={len(self)} book_name={self.__book_name}>"

    def __hash__(self):
        text = f"{self.str_index}" \
            f"{self.name}{self.book_name}".encode()
        sha256_hash = hashlib.sha256(text)
        hash_value = sha256_hash.hexdigest()
        return int(hash_value, 16)

    def __eq__(self, other: "Chapter"):
        if (isinstance(other, Chapter) and (hash(self) == hash(other))):
            return True
        return False
    
    @property
    def text(self):
        return "\t" + "\n\t".join(self.content)
    
    @property
    def str_index(self):
        return str(self.__index).rjust(5, '0')
    
    @property
    def word_count(self):
        return sum([len(i) for i in self.content])
    
    @property
    def content(self) -> Tuple[str, ...]:
        # 为每种存储方式设置对应提取内容方式
        match self.__storage_method:
            # 若为内存存储则直接将内容输出即可
            case self.StorageMethod.MEMORY:
                return tuple(self.__content)
            # 若为磁盘存储则从文件中提取内容输出
            case self.StorageMethod.DISK:
                try:
                    with open(
                        self.__file_path, "r", encoding="UTF-8"
                    ) as txt_file:
                        content = [i.rstrip("\n") for i in txt_file.readlines()]
                except OSError:
                    content = (_EMPTY_TIP, "原因可能为缓存文件被移动或删除")
                    self.__logger.warning("读取缓存文件时出现了一个错误.")
                return tuple(content)

    @content.setter
    def content(self, text: Iterable[str]):
        # 确认传入的参数的类型是否正确
        buffer = []
        for i in text:
            if isinstance(i, str):
                buffer.append(i)
            else:
                self.__logger.warning("传入的文本列表中存在非 str 对象.")
        # 为每种存储方式设置对应的内容存储变量
        match self.__storage_method:
            # 使用内存存储则将段落内容数据转换为 list 即可, 便于内容的增改
            case self.StorageMethod.MEMORY:
                self.__content = buffer
            # 使用磁盘存储则进行以下一系列操作
            case self.StorageMethod.DISK:
                with open(
                    self.__file_path, "w", encoding="UTF-8"
                ) as txt_file:
                    txt_file.write("\n".join(buffer))
        self.__logger.debug(
            f"使用{self.__storage_method.value[0]}存储方式保存了章节({self.__name})内容."
        )

    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, name: str):
        assert isinstance(name, str)
        self.__name = _replace_illegal_chars(name)

    @property
    def index(self):
        return self.__index
    
    @index.setter
    def index(self, index: int):
        assert isinstance(index, int)
        self.__index = index

    @property
    def source(self):
        return self.__source
    
    @source.setter
    def source(self, source: str):
        assert isinstance(source, str)
        self.__source = source

    @property
    def book_name(self):
        return self.__book_name
    
    @book_name.setter
    def book_name(self, book_name: str):
        assert isinstance(book_name, str)
        self.__book_name = _replace_illegal_chars(book_name)


class Book(object):
    class State(Enum):
        """书籍的状态常量"""
        # 设置必要的状态常量
        END = ("完结", 1)
        SERIALIZING = ("连载中", 2)
        FORECAST = ("预告", 3)
        BREAK = ("断更", 4)

        @classmethod
        def transform(cls, number: int):
            """将常量的 id 转换为常量
            若常量 id 不存在, 则使用默认值, 书籍状态连载中
            
            :param number: 常量 id
            :type number: int
            
            Example: 
                >>> Book.State.transform(1)
                >>> Book.State.transform(2)
                >>> Book.State.transform(3)
                >>> Book.State.transform(4)
                >>> Book.State.transform(5)
            """
            # 尝试查找匹配的常量
            for i in list(cls):
                if number == i.value[1]:
                    return i
            # 若没有常量的结果和参数匹配, 则返回默认值
            return cls.SERIALIZING
    
    class SaveMethod(Enum):
        """书籍的保存方式常量"""
        # 设置必要的保存常量
        EPUB = ("epub文件", 1, "epub")
        TXT = ("txt文件", 2, "txt")
        PDF = ("pdf文件", 3, "pdf")

        @classmethod
        def transform(cls, number: int):
            """将常量的 id 转换为常量
            若常量 id 不存在, 则使用默认值, 存储为 EPUB 文件
            
            :param number: 常量 id
            :type number: int
            
            Example:
                >>> Book.SaveMethod.transform(1)
                >>> Book.SaveMethod.transform(2)
                >>> Book.SaveMethod.transform(3)
                >>> Book.SaveMethod.transform(4)
            """
            # 尝试查找匹配的常量
            for i in list(cls):
                if number == i.value[1]:
                    return i
            # 若没有常量的结果和参数匹配, 则返回默认值
            return cls.EPUB

    def __init__(
            self, name: str, author: str,
            source: str, state: State = State.SERIALIZING,
            desc: str = "", cover_image: bytes = b"", **other_data
        ):
        """书籍对象
        
        :param name: 书籍的名称
        :type name: str
        :param author: 书籍的作者
        :type author: str
        :param state: 书籍的状态
        :type state: tuple
        :param source: 书籍的源网址
        :type source: str
        :param desc: 书籍的简介或描述
        :type desc: str
        :param cover_image: 书籍的封面图片
        :type cover_image: bytes
        :param other_data: 书籍的其它信息
        :type other_data: dict
        
        Example:
            >>> Book("测试书籍", "测试作者", "https://example.com/")
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(name, str)
        assert isinstance(author, str)
        assert isinstance(source, str)
        assert isinstance(state, self.State)
        assert isinstance(desc, str)
        assert isinstance(cover_image, bytes)
        # 初始化日志记录器
        self.__logger = Logger()
        # 初始化数据
        self.__name = _replace_illegal_chars(name)
        self.__author = _replace_illegal_chars(author)
        self.__state = state
        self.__source = source
        self.__desc = desc
        self.__cover_image = cover_image
        self.__other_data = other_data
        # 初始化书籍的章节列表
        self.__chapter_list: List[Chapter] = []
        # 为了适应多线程时使用该对象, 特别是添加章节时, 需要在此设置线程锁保证数据安全
        self.__lock = Lock()
        self.__logger.debug(f"创建了名为'{self.__name}'的书籍.")
    
    def __len__(self):
        return len(self.__chapter_list)
    
    def __bool__(self):
        if hash(self) == hash(self.empty_book()):
            return False
        return True

    def __repr__(self):
        return f"<Book name={self.__name} " \
            f"author={self.__author} len={len(self)}>"

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

    def append(self, chapter: Chapter) -> bool:
        """向书籍对象中添加章节
        
        :param chapter: 章节对象
        :type chapter: Chapter
        """
        # 检查传入的参数是否正确
        if not isinstance(chapter, Chapter):
            self.__logger.warning("向书籍的章节列表中添加的不为章节对象.")
            return False
        # 获取线程锁以确保线程安全
        with self.__lock:
            # 确定书籍的名称匹配且章节还未加入该书籍的章节列表
            if ((chapter.book_name != self.name) or
                (chapter.index in self.index_list)):
                return False
            # 添加章节进入章节列表, 并按照章节 index 排序
            self.__chapter_list.append(chapter)
            self.__chapter_list = sorted(
                self.__chapter_list, key=lambda x: x.index
            )
        self.__logger.debug(f"向书籍({self.__name})中添加了一个章节({chapter.name}).")
        return True
    
    def save(self, method: SaveMethod = SaveMethod.EPUB) -> int:
        """按照指定方式存储书籍, 并返回存储后文件的大小
        
        :param method: 书籍的保存方式
        :type method: SaveMethod
        """
        # 确认传入的参数是否正确
        assert isinstance(method, self.SaveMethod)
        # 保存书籍
        book_size = Saver(self, method).save()
        self.__logger.info(
            f"保存了一本书籍({self.__name}), 占用磁盘空间约为%.5fMB." % (book_size / (1024 * 1024))
        )
        return book_size
    
    @property
    def index_list(self) -> List[int]:
        # 获取所有章节的 index
        index_list = [i.index for i in self.__chapter_list]
        return index_list
    
    @property
    def chapter_list(self):
        for i in self.__chapter_list:
            yield i
    
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
    
    @staticmethod
    def empty_book():
        return Book(
            "默认书籍", "默认作者", "https://example.com/",
            Book.State.END, "默认描述", b""
        )
    
    def set_other_data(self, key: str, item: Any):
        """设置书籍的其它数据
        
        :param key: 书籍的数据名
        :type key: str
        :param item: 对应的数据, 要求为 Json 格式支持的数据类型
        :type item: Any
        """
        # 确保数据名的数据类型为 str
        assert isinstance(key, str)
        # 设置数据
        self.__other_data[key] = item


# 可能常用的常量
global EMPTY_BOOK
EMPTY_BOOK = Book(
    "默认书籍", "默认作者", "https://example.com/",
    Book.State.END, "默认描述", b""
)


class Saver(object):
    def __init__(
        self, book: Book, method: Book.SaveMethod = Book.SaveMethod.EPUB
    ):
        """书籍保存 API
        
        :param book: 书籍对象
        :type book: Book
        :param method: 保存方式
        :type method: Book.SaveMethod
        """
        # 检查传入的参数是否正确
        assert isinstance(book, Book)
        assert isinstance(method, Book.SaveMethod)
        # 初始化数据
        self.__book = book
        self.__method = method
        # 生成保存路径
        self.__path = os.path.join(
            Settings.BOOKS_STORAGE_DIR, f"{book.author} - {book.name}.{method.value[2]}"
        )

    def save(self) -> int:
        # 依据给定的方法保存书籍
        match self.__method:
            case Book.SaveMethod.TXT:
                return self.__txt_file()
            case Book.SaveMethod.EPUB:
                return self.__epub_file()
            case Book.SaveMethod.PDF:
                # TODO 完成该分支方法，使保存方式支持PDF文件
                return 0
    
    def __txt_file(self):
        # 依据指定的路径创建或打开文件, 文件存在则清空文件
        with open(self.__path, "w", encoding="UTF-8") as txt_file:
            # 向文件中写入书籍的基本信息
            txt_file.write(f"{self.__book.name} - {self.__book.author}\n\n")
            txt_file.write(f"书籍简介:\n\t{self.__book.desc}\n\n")
            # 向文件中写入每一个章节
            for one_chapter in self.__book.chapter_list:
                txt_file.write(str(one_chapter))
        # 获取最终的文件大小并返回
        return os.path.getsize(self.__path)
    
    def __epub_file(self):
        # 创建一个 Epub 书籍对象
        book = epub.EpubBook()
        
        # 设置书籍的基本信息
        # 包括 书籍名称、语言(为默认的中文)、书籍作者名、书籍简介
        book.set_title(self.__book.name)
        book.set_language('zh-CN')
        book.add_author(self.__book.author)
        book.add_metadata('DC', 'description', self.__book.desc)
        
        # 设置书籍的封面图片
        if self.__book.cover_image:
            # 将封面图片用 PIL 库统一转换成 JPEG 格式
            image = io.BytesIO()
            Image.open(io.BytesIO(self.__book.cover_image)) \
                .convert("RGB").save(image, format="jpeg")
            # 从头读取图片内容并设置图片
            image.seek(0)
            book.set_cover("image.jpg", image.read())
        
        # 设置书籍的其它信息
        if self.__book.other_data:
            # 设置前将数据转换为 YAML 格式
            yaml_item = epub.EpubItem(
                uid='yaml', file_name='metadata.yaml',
                media_type='application/octet-stream',
                content=yaml.dump(self.__book.other_data).encode()
            )
            book.add_item(yaml_item)
        
        # 设置书籍的基本信息展示页面
        intro_e = epub.EpubHtml(
            title='Introduction', file_name='intro.xhtml', lang='hr'
        )
        intro_e.content = (
            f'<img src="image.jpg" alt="Cover Image" ' \
            f'style="width:100%;height:100%;object-fit:cover;"/>'
            f'<h1>{self.__book.name}</h1>'
            f'<p>{self.__book.desc.replace("\n", "</p><p>")}</p>'
        )
        book.add_item(intro_e)
        
        # 设置书籍内容的排序, 基本信息展示在最前面, 其次是书籍的目录
        book.spine = [intro_e, "nav"]
        # 初始化书籍目录缓存变量
        toc = []
        # 创建章节的页面并加入书籍目录以及书籍内容排序
        for one_chapter in self.__book.chapter_list:
            # 获取章节内容元组
            chapter_text_list = one_chapter.content
            # 创建章节内容页面, 展示章节基本信息
            text = epub.EpubHtml(
                title=f"第{one_chapter.index}章 {one_chapter.name}",
                file_name=f'chapter_{one_chapter.str_index}.xhtml'
            )
            # 填充章节内容
            text.content = \
                f'<h2 class="titlecss"><span>第{one_chapter.index}章</span> ' \
                f'<span>{one_chapter.name}</span></h2>' + \
                ''.join([f"<p>{i}</p>" for i in chapter_text_list])
            # 向书籍对象、内容排序、目录中添加章节页面
            book.add_item(text)
            toc.append(text)
            book.spine.append(text)
        
        # 给书籍添加目录
        book.toc = toc
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        # 保存书籍
        epub.write_epub(self.__path, book, {})
        # 获取最终的文件大小并返回
        return os.path.getsize(self.__path)


if __name__ == "__main__":
    VERSION = "0.1.0"