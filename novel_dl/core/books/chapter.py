#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: chapter.py
# @Time: 27/01/2025 22:55
# @Author: Amundsen Severus Rubeus Bjaaland
"""chapter.py
这是一个用于处理小说章节内容缓存和管理的模块。
模块包含以下类:
- CacheMethod: 枚举类，定义章节内容的缓存方式（内存或磁盘）。
- CacheList: 类，管理章节内容的缓存列表。
- Chapter: 类，表示小说的一个章节。
模块依赖的标准库:
- os: 提供操作系统相关功能。
- copy: 提供浅拷贝和深拷贝操作。
- json: 提供 JSON 编码和解码功能。
- time: 提供时间相关功能。
- hashlib: 提供哈希算法。
- enum: 提供枚举支持。
- typing: 提供类型提示支持。
模块依赖的自定义库:
- novel_dl.utils.options: 提供 mkdir 和 sanitize_filename 函数。
- novel_dl.core.settings: 提供 Settings 类。
- .line: 提供 Line 类。
类:
- CacheMethod: 枚举类，定义章节内容的缓存方式（内存或磁盘）。
- CacheList: 类，管理章节内容的缓存列表。
- Chapter: 类，表示小说的一个章节。
CacheMethod 类:
- Memory: 内存缓存方式。
- Disk: 磁盘缓存方式。
- to_obj: 类方法，将常量的 ID 或名称转换为常量对象。
- __int__: 返回常量的 ID。
- __str__: 返回常量的名称。
CacheList 类:
- __init__: 初始化缓存列表。
- __del__: 删除缓存文件。
- __iter__: 创建迭代器。
- __next__: 获取下一行内容。
- to_list: 将缓存内容转换为列表。
- append: 向缓存文件中添加一行内容。
- clear: 清空缓存列表。
- index: 获取行对象在缓存列表中的索引。
- insert: 在缓存列表中的指定位置插入一行内容。
- pop: 删除缓存列表中的指定位置的行对象。
- remove: 删除缓存列表中的指定行对象。
- sort: 对缓存列表进行排序。
- __len__: 返回缓存列表的长度。
- path: 返回缓存文件的路径。
Chapter 类:
- __init__: 初始化章节对象。
- __len__: 返回章节内容的长度。
- __str__: 返回章节的字符串表示。
- __repr__: 返回章节的表示形式。
- __hash__: 返回章节的哈希值。
- __eq__: 判断两个章节是否相等。
- __iter__: 返回章节内容的迭代器。
- append: 向章节内容中添加一行内容。
- add_source: 向章节来源中添加一个来源。
- index: 返回章节索引。
- str_index: 返回章节索引的字符串形式。
- name: 返回章节名称。
- sources: 返回章节来源列表。
- update_time: 返回章节更新时间。
- book_name: 返回书籍名称。
- cache_method: 返回缓存方式。
- other_info: 返回其他信息。
- content: 返回章节内容的生成器。
"""


# 导入标准库
import os
import copy
import json
import time
import hashlib
from enum import Enum
from typing import Iterable, Generator, List, Dict

# 导入自定义库
from novel_dl.utils.options import mkdir, sanitize_filename
from novel_dl.core.settings import Settings
from .line import Line


class CacheMethod(Enum):
    """章节内容缓存方式枚举类
    
    常量中, 第一个参数是ID, 第二个参数是名称
    """
    Memory = (1, "内存")
    Disk = (2, "磁盘")
    
    @classmethod
    def to_obj(cls, value: int | str) -> "CacheMethod":
        """将常量的ID或名称转换为常量对象
        
        :param value: 常量的ID或名称
        :type value: int | str
        :return: 常量对象
        
        Example:
            >>> CacheMethod.to_obj(1)
            >>> CacheMethod.to_obj("内存")
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
        return cls.Memory
    
    def __int__(self):
        return self.value[0]
    
    def __str__(self):
        return self.value[1]
    

class CacheList(object):
    def __init__(
        self, book_name: str, chapter_index: int,
        chapter_name: str, lines: Iterable[Line] = ()
    ):
        """章节内容缓存列表类
        
        :param book_name: 书籍名称
        :type book_name: str
        :param chapter_index: 章节索引
        :type chapter_index: int
        :param chapter_name: 章节名称
        :type chapter_name: str
        :param lines: 章节内容
        :type lines: Iterable[Line]
        
        Example:
            >>> CacheList(
            >>>     "book_name", 1, "chapter_name", [Line.default(),]
            >>> )
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(book_name, str)
        assert isinstance(chapter_index, int)
        assert isinstance(chapter_name, str)
        assert isinstance(lines, Iterable)
        for i in lines:
            assert isinstance(i, Line)
        # 创建运行时必要的目录
        mkdir(Settings().DATA_DIR)
        mkdir(Settings().BOOKS_DIR)
        mkdir(Settings().BOOKS_CACHE_DIR)
        mkdir(os.path.join(Settings().BOOKS_CACHE_DIR, book_name))
        # 设置缓存文件的路径
        self.__path = os.path.join(
            Settings().BOOKS_CACHE_DIR,
            f"{book_name}/{str(chapter_index).zfill(5)}" \
            f"-{chapter_name}.cache"
        )
        # 如果缓存文件存在, 则清空
        if os.path.exists(self.__path):
            self.clear()
        # 将章节内容写入缓存文件
        for i in lines:
            self.append(i)
    
    def __del__(self):
        # 删除缓存文件
        try: os.remove(self.__path)
        except OSError: pass
    
    def __iter__(self):
        # 创建迭代器: 设置索引为0
        self.__index = 0
        return self
    
    def __next__(self):
        # 创建内容缓存变量
        data = ""
        # 打开缓存文件, 读取至索引位置
        with open(self.__path, "r") as cache_file:
            for _ in range(self.__index + 1):
                data = cache_file.readline()
        # 如果读取到的内容为空, 则抛出 StopIteration 异常
        if not data:
            raise StopIteration
        # 如果读取到的内容不为空, 则返回 Line 对象
        else:
            # 索引自增
            self.__index += 1
            # 尝试将读取到的内容转换为字典
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                # TODO 这里 Json 解析失败时应该记录日志
                return Line.default()
            else:
                return Line.from_dict(data)
    
    def to_list(self) -> List[Line]:
        """将缓存内容转换为列表
        
        :return: 缓存内容列表
        """
        return [i for i in self]
    
    def append(self, line: Line) -> None:
        """向缓存文件中添加一行内容
        
        :param line: 行对象
        :type line: Line
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(line, Line)
        # 打开缓存文件, 追加写入一行内容
        with open(self.__path, "a") as cache_file:
            # 将行对象转换为字典, 再转换为 Json 字符串, 写入缓存文件
            cache_file.write(json.dumps(line.to_dict()))
            cache_file.write("\n")
    
    def clear(self) -> None:
        """清空缓存列表"""
        # 清空缓存文件
        with open(self.__path, "w") as cache_file:
            cache_file.write("")
    
    def index(self, line: Line) -> int:
        """获取行对象在缓存列表中的索引
        
        :param line: 行对象
        :type line: Line
        :return: 行对象在缓存列表中的索引
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(line, Line)
        # 设置索引为0
        index = 0
        # 遍历缓存内容, 获取行对象在缓存列表中的索引
        for one_line in self:
            if one_line == line:
                return index
            index += 1
        # 如果行对象不在缓存列表中, 则返回 -1
        return -1
    
    def insert(self, index: int, line: Line) -> None:
        """在缓存列表中的指定位置插入一行内容
        
        :param index: 索引
        :type index: int
        :param line: 行对象
        :type line: Line
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(index, int)
        assert isinstance(line, Line)
        # 如果索引小于0, 则设置索引为0
        if index < 0:
            index = 0
        # 如果索引大于等于缓存列表的长度, 则追加写入一行内容
        if index >= len(self):
            self.append(line)
            return
        # 创建缓存文件的临时文件
        with open(f"{self.__path}-cache", "w") as cache_file:
            # 打开缓存文件, 读取至索引位置, 将内容写入临时文件
            with open(self.__path, "r") as old_cache_file:
                # 创建计数器
                counter = 0
                # 遍历缓存内容
                while True:
                    # 读取一行内容
                    old_line = old_cache_file.readline()
                    # 如果读取到的内容为空, 则退出循环
                    if not old_line:
                        break
                    # 如果计数器等于索引, 则将行对象转换为字典, 写入临时文件
                    if counter == index:
                        cache_file.write(json.dumps(line.to_dict()))
                        cache_file.write("\n")
                    # 将读取到的内容写入临时文件
                    cache_file.write(old_line)
                    # 计数器自增
                    counter += 1
        # 删除缓存文件, 重命名临时文件为缓存文件
        try:
            os.remove(self.__path)
            os.rename(f"{self.__path}-cache", self.__path)
        except OSError: pass
    
    def pop(self, index: int = -1) -> None:
        """删除缓存列表中的指定位置的行对象
        
        :param index: 索引
        :type index: int
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(index, int)
        # 如果索引为 -1, 则设置索引为缓存列表的长度减1， 即删除最后一行内容
        if index == -1:
            index = len(self) - 1
        # 如果索引小于0, 则抛出 IndexError 异常
        if index < 0:
            raise IndexError
        # 如果索引大于等于缓存列表的长度, 则抛出 IndexError 异常
        if index >= len(self):
            raise IndexError
        # 创建缓存文件的临时文件
        with open(f"{self.__path}-cache", "w") as cache_file:
            # 打开缓存文件, 读取至索引位置, 将内容写入临时文件
            with open(self.__path, "r") as old_cache_file:
                # 创建计数器
                counter = 0
                # 遍历缓存内容
                while True:
                    # 读取一行内容
                    old_line = old_cache_file.readline()
                    # 如果读取到的内容为空, 则退出循环
                    if not old_line:
                        break
                    # 如果计数器不等于索引, 则将读取到的内容写入临时文件
                    if counter != index:
                        cache_file.write(old_line)
                    # 计数器自增
                    counter += 1
        # 删除缓存文件, 重命名临时文件为缓存文件
        try:
            os.remove(self.__path)
            os.rename(f"{self.__path}-cache", self.__path)
        except OSError:
            pass
    
    def remove(self, line: Line) -> None:
        """删除缓存列表中的指定行对象
        
        :param line: 行对象
        :type line: Line
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(line, Line)
        # 获取行对象在缓存列表中的索引
        index = self.index(line)
        # 如果行对象不在缓存列表中, 则直接退出函数
        if index == -1:
            return
        # 删除缓存列表中的指定位置的行对象
        self.pop(index)
    
    def sort(self, reverse=False) -> None:
        """对缓存列表进行排序
        
        :param reverse: 是否降序排序, 若为 True, 则降序排序, 否则升序排序
        :type reverse: bool
        """
        # 将缓存内容转换为列表
        data_list = self.to_list()
        # 对列表进行排序
        data_list = sorted(
            data_list, key=lambda x: x.index, reverse=reverse
        )
        # 清空缓存列表
        self.clear()
        # 将排序后的列表写入缓存文件
        for i in data_list:
            self.append(i)
                    
    def __len__(self):
        counter = 0
        for _ in self:
            counter += 1
        return counter
    
    @property
    def path(self) -> str:
        return self.__path


class Chapter(object):
    def __init__(
        self, index: int, name: str, sources: Iterable[str],
        update_time: float, book_name: str,
        content: Iterable[Line] = (),
        cache_method: CacheMethod = CacheMethod.Memory,
        **other_info: Dict[str, str]
    ):
        """章节类
        
        :param index: 章节索引
        :type index: int
        :param name: 章节名称
        :type name: str
        :param sources: 章节来源
        :type sources: Iterable[str]
        :param update_time: 更新时间
        :type update_time: float
        :param book_name: 书籍名称
        :type book_name: str
        :param content: 章节内容
        :type content: Iterable[Line]
        :param cache_method: 缓存方式
        :type cache_method: CacheMethod
        :param other_info: 其他信息
        :type other_info: Dict[str, str]
        
        Example:
            >>> Chapter(
            >>>     1, "chapter_name",
            >>>     ["https://example.com/1", "https://example.com/2"],
            >>>     1643328000.0, "book_name", [Line.default(),],
            >>>     CacheMethod.Disk, key1="value1", key2="value2"
            >>> )
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(index, int)
        assert isinstance(name, str)
        assert isinstance(sources, Iterable)
        assert isinstance(update_time, float)
        assert isinstance(book_name, str)
        assert isinstance(content, Iterable)
        assert isinstance(cache_method, CacheMethod)
        for i in sources:
            assert isinstance(i, str)
        for i in content:
            assert isinstance(i, Line)
        for k, v in other_info.items():
            assert isinstance(k, str)
            assert isinstance(v, str)
        # 初始化数据, 其中 name 和 book_name 需要进行文件名清洗
        self.__index = index
        self.__name = sanitize_filename(name)
        self.__sources = list(sources)
        self.__update_time = update_time
        self.__book_name = sanitize_filename(book_name)
        self.__cache_method = cache_method
        self.__other_info = other_info
        # 根据缓存方式初始化章节内容
        if cache_method == CacheMethod.Memory:
            self.__content = list(content)
        else:
            self.__content = CacheList(
                self.__book_name, self.__index,
                self.__name, content
            )
    
    def __len__(self):
        return len(self.__content)
    
    def __str__(self):
        # 将章节内容转换为字符串
        content = "\t" + "\n\t".join([str(i) for i in self.__content])
        # 将更新时间转换为字符串
        update_time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(self.__update_time)
        )
        # 返回章节的字符串表示, 该表示默认是 TXT 文件的输出格式
        return f"第{self.__index}章 {self.__name}\n" \
            f"\t更新时间: {update_time}\n" \
            f"{content}"
    
    def __repr__(self):
        return f"<Chapter book_name={self.__book_name} " \
            f"index={self.__index} name={self.__name}" \
            f"len={len(self)} cache_method={str(self.__cache_method)}>"
    
    def __hash__(self):
        # 拼接参与计算哈希值的字符串
        hash_str = f"{self.str_index}{self.__name}" \
            f"{self.__book_name}"
        # 计算哈希值
        sha256 = hashlib.sha256()
        sha256.update(hash_str.encode())
        # 返回哈希值
        return int(sha256.hexdigest(), 16)
    
    def __eq__(self, value: "Chapter"):
        if not isinstance(value, Chapter):
            return False
        return hash(self) == hash(value)
    
    def __iter__(self):
        # 注意: 这里的迭代器是对章节内容的迭代器
        return self.__content
    
    def append(self, line: Line) -> None:
        """向章节内容中添加一行内容
        
        :param line: 行对象
        :type line: Line
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(line, Line)
        # 向章节内容中添加一行内容
        self.__content.append(line)
    
    def add_source(self, source: str) -> None:
        """向章节来源中添加一个来源
        
        :param source: 来源
        :type source: str
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(source, str)
        # 向章节来源中添加一个来源
        self.__sources.append(source)
    
    @property
    def index(self) -> int:
        return self.__index
    
    @property
    def str_index(self) -> str:
        return str(self.__index).zfill(5)
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def sources(self) -> List[str]:
        return copy.deepcopy(self.__sources)
    
    @property
    def update_time(self) -> float:
        return self.__update_time
    
    @property
    def book_name(self) -> str:
        return self.__book_name
    
    @property
    def cache_method(self) -> CacheMethod:
        return self.__cache_method
    
    @property
    def other_info(self) -> dict:
        return copy.deepcopy(self.__other_info)
    
    @property
    def content(self) -> Generator[Line, None, None]:
        for i in self.__content:
            yield i