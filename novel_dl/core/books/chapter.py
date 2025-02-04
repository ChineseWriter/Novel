#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: chapter.py
# @Time: 27/01/2025 22:55
# @Author: Amundsen Severus Rubeus Bjaaland


# 导入标准库
import os
import json
from enum import Enum
from typing import Iterable

# 导入自定义库
from novel_dl.core.settings import Settings
from .line import ContentType, Line


class CacheMethod(Enum):
    """章节内容缓存方式枚举类
    
    常量中, 第一个参数是ID, 第二个参数是名称
    """
    Memory = (1, "内存")
    Disk = (2, "磁盘")
    
    @classmethod
    def to_obj(cls, value: int | str):
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
    
    def __int__(self):
        return self.value[0]
    
    def __str__(self):
        return self.value[1]
    

class CacheList(object):
    def __init__(self, path: str, lines: Iterable[Line] = ()):
        assert isinstance(path, str)
        assert isinstance(lines, Iterable)
        for i in lines:
            assert isinstance(i, Line)
        self.__path = path
    
    def append(self, line: Line):
        assert isinstance(line, Line)
        with open(self.__path, "a") as cache_file:
            cache_file.write(json.dumps(line.to_dict()))
            cache_file.write("\n")
    
    def clear(self):
        with open(self.__path, "w") as cache_file:
            cache_file.write("")
    
    def index(self, line: Line):
        assert isinstance(line, Line)
        index = 0
        for one_line in self:
            if one_line == line:
                return index
            index += 1
        return -1
    
    def insert(self, index: int, line: Line):
        assert isinstance(index, int)
        assert isinstance(line, Line)
        if index < 0:
            index = 0
        if index >= len(self):
            self.append(line)
            return
        with open(f"{self.__path}-cache", "w") as cache_file:
            with open(self.__path, "r") as old_cache_file:
                counter = 0
                while True:
                    old_line = old_cache_file.readline()
                    if not old_line:
                        break
                    if counter == index:
                        cache_file.write(json.dumps(line.to_dict()))
                        cache_file.write("\n")
                    cache_file.write(old_line)
                    counter += 1
        try:
            os.remove(self.__path)
            os.rename(f"{self.__path}-cache", self.__path)
        except OSError:
            pass
    
    def pop(self, index: int = -1):
        assert isinstance(index, int)
        if index == -1:
            index = len(self) - 1
        if index < 0:
            raise IndexError
        if index >= len(self):
            raise IndexError
        with open(f"{self.__path}-cache", "w") as cache_file:
            with open(self.__path, "r") as old_cache_file:
                counter = 0
                while True:
                    old_line = old_cache_file.readline()
                    if not old_line:
                        break
                    if counter != index:
                        cache_file.write(old_line)
                    counter += 1
        try:
            os.remove(self.__path)
            os.rename(f"{self.__path}-cache", self.__path)
        except OSError:
            pass
    
    def remove(self, line: Line):
        assert isinstance(line, Line)
        index = self.index(line)
        if index == -1:
            return
        self.pop(index)
    
    def sort(self, reverse=False):
        data_list = list(self)
        data_list = 
                    
    def __len__(self):
        counter = 0
        for _ in self:
            counter += 1
        return counter
    
    def __iter__(self):
        return self  
    
    def __next__(self):
        with open(self.__path, "r") as cache_file:
            while True:
                line = cache_file.readline()
                if not line:
                    break
                try:
                    data = Line.from_dict(json.loads(line))
                except json.JSONDecodeError:
                    # TODO 这里执行失败时应该有 WARNING
                    continue
                else:
                    yield data
        raise StopIteration
        


class Chapter(object):
    def __init__(
        self, index: int, name: str, source: str,
        update_time: float, book_name: str,
        content: Iterable[Line] = (),
        cache_method: CacheMethod = CacheMethod.Memory,
        **other_info
    ):
        pass