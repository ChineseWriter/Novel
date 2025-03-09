#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: book.py
# @Time: 06/02/2025 11:03
# @Author: Amundsen Severus Rubeus Bjaaland
"""书籍模块
这个模块定义了书籍相关的类和常量，包括书籍状态、标签和书籍类。
类:
    State: 枚举类，表示书籍的状态。
    Tag: 枚举类，表示书籍的标签。
    Book: 书籍类，表示一本书籍。
State 类:
    枚举常量:
        END: 表示书籍已完结。
        SERIALIZING: 表示书籍正在连载。
        BREAK: 表示书籍断更。
    方法:
        to_obj(value: int | str) -> "State": 将常量的ID或名称转换为常量对象。
        __int__() -> int: 返回常量的ID。
        __str__() -> str: 返回常量的名称。
Tag 类:
    枚举常量:
        FANTASY: 表示书籍的标签为玄幻。
        ROMANCE: 表示书籍的标签为言情。
    方法:
        to_obj(value: int | str) -> "Tag": 将常量的ID或名称转换为常量对象。
        __int__() -> int: 返回常量的ID。
        __str__() -> str: 返回常量的名称。
Book 类:
    属性:
        name: 书籍的名称。
        author: 书籍的作者。
        state: 书籍的状态。
        desc: 书籍的描述。
        sources: 书籍的来源。
        cover_images: 书籍的封面图片。
        tags: 书籍的标签。
        other_info: 书籍的其他信息。
        chapters: 书籍的章节列表。
    方法:
        __init__(name: str, author: str, state: State, desc: str, sources: Iterable[str], cover_images: Iterable[bytes] = (), tags: Iterable[Tag] = (), **other_info: Dict[str, str]): 初始化书籍对象。
        __len__() -> int: 返回书籍的章节数量。
        __hash__() -> int: 返回书籍的哈希值。
        __eq__(value: "Book") -> bool: 判断两个书籍对象是否相等。
        __bool__() -> bool: 判断书籍对象是否有效。
        __getitem__(index: int) -> Chapter: 获取指定索引的章节对象。
        __setitem__(index: int, value: Chapter) -> None: 设置指定索引的章节对象。
        __delitem__(index: int) -> None: 删除指定索引的章节对象。
        default() -> "Book": 获取默认的书籍对象。
        append(value: Chapter) -> bool: 添加章节对象。
        sort(reverse: bool = False) -> None: 对章节列表进行排序。
        add_source(source: str) -> None: 添加来源。
        add_cover_image(cover_image: bytes) -> None: 添加封面图片。
        add_tag(tag: Tag) -> None: 添加标签。
        set_other_info(key: str, value: str) -> None: 设置其他信息。
"""


# 导入标准库
import time
import copy
import hashlib
from enum import Enum
from threading import Lock
from typing import Iterable, Generator, Dict, List
# 导入自定义库
from .chapter import Chapter
from novel_dl.utils.fs import sanitize_filename


class State(Enum):
    """书籍的状态常量"""
    END = (1, "完结")
    SERIALIZING = (2, "连载")
    BREAK = (3, "断更")
    
    @classmethod
    def to_obj(cls, value: int | str) -> "State":
        """将常量的ID或名称转换为常量对象
        
        :param value: 常量的ID或名称
        :type value: int | str
        :return: 常量对象
        
        Example:
            >>> State.to_obj(1)
            >>> State.to_obj("完结")
        """
        # 确保 value 是 int 或 str 类型
        assert isinstance(value, int) or isinstance(value, str)
        # 如果 value 是 int 类型
        if isinstance(value, int):
            # 遍历所有常量
            for i in list(cls):
                # 如果常量的 ID 等于 value
                if i.value[0] == value:
                    # 返回常量对象
                    return i
        # 如果 value 是 str 类型
        else:
            # 遍历所有常量
            for i in list(cls):
                # 如果常量的名称等于 value
                if i.value[1] == value:
                    # 返回常量对象
                    return i
        # 如果 value 的值不在常量中, 则返回 END 类型
        return cls.END
    
    def __int__(self):
        return self.value[0]
    
    def __str__(self):
        return self.value[1]


class Tag(Enum):
    """书籍的标签常量"""
    # TODO 添加更多标签, 添加时应同步书写测试用例以及程序文档
    FANTASY = (1, "玄幻")
    ROMANCE = (2, "言情")
    
    @classmethod
    def to_obj(cls, value: int | str) -> "Tag":
        """将常量的ID或名称转换为常量对象
        
        :param value: 常量的ID或名称
        :type value: int | str
        :return: 常量对象
        
        Example:
            >>> Tag.to_obj(1)
            >>> Tag.to_obj("奇幻")
        """
        # 确保 value 是 int 或 str 类型
        assert isinstance(value, int) or isinstance(value, str)
        # 如果 value 是 int 类型
        if isinstance(value, int):
            # 遍历所有常量
            for i in list(cls):
                # 如果常量的 ID 等于 value
                if i.value[0] == value:
                    # 返回常量对象
                    return i
        # 如果 value 是 str 类型
        else:
            # 遍历所有常量
            for i in list(cls):
                # 如果常量的名称等于 value
                if i.value[1] == value:
                    # 返回常量对象
                    return i
        # 如果 value 的值不在常量中, 则返回 Memory 类型
        return cls.FANTASY
    
    def __int__(self):
        return self.value[0]
    
    def __str__(self):
        return self.value[1]


class Book(object):
    def __init__(
        self, name: str, author: str, state: State, desc: str,
        sources: Iterable[str], cover_images: Iterable[bytes] = (),
        tags: Iterable[Tag] = (), **other_info: Dict[str, str]
    ):
        """书籍类
        注意: 书籍类是线程安全的.  
        注意: 书籍类中的其它信息不能以"id"作为键名, 因为"id"是保留关键字.
        该关键字将作为该书籍在数据库中的唯一索引值.  
        
        :param name: 书籍的名称
        :type name: str
        :param author: 书籍的作者
        :type author: str
        :param state: 书籍的状态
        :type state: State
        :param desc: 书籍的描述
        :type desc: str
        :param sources: 书籍的来源
        :type sources: Iterable[str]
        :param cover_images: 书籍的封面图片
        :type cover_images: Iterable[bytes]
        :param tags: 书籍的标签
        :type tags: Iterable[Tag]
        :param other_info: 书籍的其他信息
        :type other_info: Dict[str, str]
        
        Example:
            >>> book = Book(
            >>>     "书名", "作者", State.END, "描述", ["来源1", "来源2"]
            >>> )
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(name, str)
        assert isinstance(author, str)
        assert isinstance(state, State)
        assert isinstance(desc, str)
        assert isinstance(sources, Iterable)
        assert isinstance(cover_images, Iterable)
        assert isinstance(tags, Iterable)
        assert isinstance(other_info, Dict)
        for i in sources:
            assert isinstance(i, str)
        for i in cover_images:
            assert isinstance(i, bytes)
        for i in tags:
            assert isinstance(i, Tag)
        for k, v in other_info.items():
            assert isinstance(k, str)
            assert isinstance(v, str)
        # 初始化数据, 其中 name 和 author 会被转换为合法文件名
        self.__name = sanitize_filename(name)
        self.__author = sanitize_filename(author)
        self.__state = state
        self.__desc = desc
        self.__sources = [i for i in sources]
        self.__cover_images = [i for i in cover_images]
        self.__tags = [i for i in tags]
        self.__other_info = other_info
        # 初始化章节列表和锁对象
        self.__chapter_list: List[Chapter] = []
        self.__lock = Lock()
    
    def __repr__(self):
        return f"<Book name={self.__name} " \
            f"author={self.__author} " \
            f"state={int(self.__state)} " \
            f"len={len(self.__chapter_list)}>"
    
    def __len__(self) -> int:
        with self.__lock:
            return len(self.__chapter_list)
    
    def __hash__(self) -> int:
        # 拼接参与计算哈希值的字符串
        hash_str = f"{self.__name}{self.__author}{self.__state}"
        # 计算哈希值
        sha256 = hashlib.sha256()
        sha256.update(hash_str.encode())
        # 返回哈希值
        return int(sha256.hexdigest(), 16)
    
    def __eq__(self, value: "Book") -> bool:
        if not isinstance(value, Book):
            return False
        return hash(self) == hash(value)
    
    def __bool__(self) -> bool:
        return hash(self) != hash(Book.default())
    
    def __iter__(self) -> Iterable[Chapter]:
        return self.__chapter_list
    
    def __getitem__(self, index: int) -> Chapter:
        # 确保 index 是 int 类型
        assert isinstance(index, int)
        # 加锁
        with self.__lock:
            # 返回章节对象
            return self.__chapter_list[index]
    
    def __setitem__(self, index: int, value: Chapter) -> None:
        # 确保 index 是 int 类型
        assert isinstance(index, int)
        # 确保 value 是 Chapter 类型
        assert isinstance(value, Chapter)
        # 加锁
        with self.__lock:
            # 设置章节对象
            self.__chapter_list[index] = value
    
    def __delitem__(self, index: int) -> None:
        # 确保 index 是 int 类型
        assert isinstance(index, int)
        # 加锁
        with self.__lock:
            # 删除章节对象
            del self.__chapter_list[index]
    
    @staticmethod
    def default() -> "Book":
        """获取默认的书籍对象"""
        return Book("", "", State.END, "", [])
    
    def append(self, value: Chapter) -> bool:
        """添加章节对象
        
        :param value: 章节对象
        :type value: Chapter
        :return: 添加是否成功
        :rtype: bool
        """
        # 确保 value 是 Chapter 类型
        assert isinstance(value, Chapter)
        # 如果 value 已经在章节列表中,
        # 或者 value 是默认章节对象,
        # 或者 value 的书名不是当前书籍的名称
        # 则返回 False
        if (value in self.__chapter_list) or \
            (value == Chapter.default()) or \
            (value.book_name != self.__name):
            return False
        # 加锁
        with self.__lock:
            # 添加章节对象
            self.__chapter_list.append(value)
        # 返回 True
        return True
    
    def sort(self, reverse: bool = False) -> None:
        """对章节列表进行排序
        
        :param reverse: 是否降序排序, 默认为 False, 即升序排序
        :type reverse: bool
        """
        # 确保 reverse 是 bool 类型
        assert isinstance(reverse, bool)
        # 加锁
        with self.__lock:
            # 对章节列表进行排序
            self.__chapter_list.sort(
                key=lambda x: x.index,
                reverse=reverse
            )
    
    def add_source(self, source: str) -> None:
        """添加来源
        
        :param source: 来源
        :type source: str
        """
        # 确保 source 是 str 类型
        assert isinstance(source, str)
        # 加锁
        with self.__lock:
            # 添加来源
            self.__sources.append(source)
    
    def add_cover_image(self, cover_image: bytes) -> None:
        """添加封面图片
        
        :param cover_image: 封面图片
        :type cover_image: bytes
        """
        # 确保 cover_image 是 bytes 类型
        assert isinstance(cover_image, bytes)
        # 加锁
        with self.__lock:
            # 添加封面图片
            self.__cover_images.append(cover_image)
    
    def add_tag(self, tag: Tag) -> None:
        """添加标签
        
        :param tag: 标签
        :type tag: Tag
        """
        # 确保 tag 是 Tag 类型
        assert isinstance(tag, Tag)
        # 加锁
        with self.__lock:
            # 添加标签
            self.__tags.append(tag)
    
    def set_other_info(self, key: str, value: str) -> None:
        """设置其他信息
        
        :param key: 键
        :type key: str
        :param value: 值
        :type value: str
        """
        # 确保 key 和 value 是 str 类型
        assert isinstance(key, str)
        assert isinstance(value, str)
        # 加锁
        with self.__lock:
            # 设置其他信息
            self.__other_info[key] = value
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def author(self) -> str:
        return self.__author
    
    @property
    def state(self) -> State:
        return self.__state
    
    @property
    def desc(self) -> str:
        return self.__desc
    
    @property
    def update_time(self) -> float:
        time_list = [i.update_time for i in self.__chapter_list]
        return max(time_list) if time_list else time.time()
    
    @property
    def sources(self) -> Generator[str, None, None]:
        for i in self.__sources:
            yield i
    
    @property
    def cover_images(self) -> Generator[bytes, None, None]:
        for i in self.__cover_images:
            yield i
    
    @property
    def tags(self) -> Generator[Tag, None, None]:
        for i in self.__tags:
            yield i
    
    @property
    def other_info(self) -> Dict[str, str]:
        return copy.deepcopy(self.__other_info)
    
    @property
    def chapters(self) -> Generator[Chapter, None, None]:
        for i in self.__chapter_list:
            yield i