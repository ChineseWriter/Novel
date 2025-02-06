#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: line.py
# @Time: 27/01/2025 19:51
# @Author: Amundsen Severus Rubeus Bjaaland
"""line.py
这是一个用于处理书籍中每行内容的模块. 
模块中定义了两个主要类: ContentType 和 Line. 
类:
    ContentType: 枚举类, 表示书籍中每行内容的类型. 
    Line: 表示书籍中每行内容的类. 
ContentType 类:
    枚举类, 表示书籍中每行内容的类型. 
    常量:
        Text: 文本类型, ID 为 1, 名称为 "文本", 非二进制, HTML 标签名为 "p". 
        Image: 图片类型, ID 为 2, 名称为 "图片", 二进制, HTML 标签名为 "img". 
        Audio: 音频类型, ID 为 3, 名称为 "音频", 二进制, HTML 标签名为 "audio". 
        Video: 视频类型, ID 为 4, 名称为 "视频", 二进制, HTML 标签名为 "video". 
        CSS: 层叠式设计样表类型, ID 为 5, 名称为 "层叠式设计样表", 非二进制, HTML 标签名为 "link". 
        JS: JavaScript 类型, ID 为 6, 名称为 "JavaScript", 非二进制, HTML 标签名为 "script". 
    方法:
        to_obj(value: int | str): 将常量的 ID 或名称转换为常量对象. 
        __int__(): 返回常量的 ID. 
        __str__(): 返回常量的名称. 
        is_bytes() -> bytes: 判断内容是否为二进制. 
        html_tag() -> str: 获取内容对应的 HTML 标签名. 
Line 类:
    表示书籍中每行内容的类. 
    属性:
        index: 索引, 表示内容的编号. 
        content: 内容, 可以是字符串或二进制数据. 
        content_type: 内容类型, 表示内容的类型. 
        attrs: 属性, 键与值都要求为字符串类型. 
    方法:
        __init__(
            index: int, content: str | bytes,
            content_type: ContentType, **attrs
        ): 初始化 Line 对象. 
        __repr__(): 返回 Line 对象的字符串表示. 
        __str__(): 返回 Line 对象的内容. 
        __hash__(): 返回 Line 对象的哈希值. 
        __eq__(other: "Line"): 判断两个 Line 对象是否相等. 
        default() -> "Line": 创建默认的 Line 对象. 
        to_dict() -> dict: 将 Line 对象转换为字典. 
        from_dict(data: dict) -> "Line": 从字典数据中创建 Line 对象. 
        encode() -> str: 将内容编码为 base64 编码. 
        decode(
            value: str, is_bytes: bool = False
        ) -> str | bytes: 将 base64 编码的内容解码. 
"""


# 导入标准库
import copy
import base64
import hashlib
from enum import Enum


class ContentType(Enum):
    """书籍中每行的内容类型枚举类
    
    常量中, 第一个参数是ID, 第二个参数是名称, 
    第三个参数是是否为二进制, 第四个参数是 HTML 标签名
    """
    Text = (1, "文本", False, "p")
    Image = (2, "图片", True, "img")
    Audio = (3, "音频", True, "audio")
    Video = (4, "视频", True, "video")
    CSS = (5, "层叠式设计样表", False, "link")
    JS = (6, "JavaScript", False, "script")
    
    @classmethod
    def to_obj(cls, value: int | str) -> "ContentType":
        """将常量的 ID 或名称转换为常量对象
        
        注意: 如果 value 的值不在常量中, 则返回 Text 类型
        
        :param value: 常量的ID或名称
        :type value: int | str
        :return: 常量对象
        
        Example:
            >>> ContentType.to_obj(1)
            >>> ContentType.to_obj("文本")
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
        # 如果 value 的值不在常量中, 则返回 Text 类型
        return cls.Text
    
    def __int__(self):
        return self.value[0]
    
    def __str__(self):
        return self.value[1]
    
    def is_bytes(self) -> bool:
        """判断内容是否为二进制"""
        return self.value[2]
    
    def html_tag(self) -> str:
        """获取内容对应的 HTML 标签名"""
        return self.value[3]


class Line(object):
    def __init__(
        self, index: int, content: str | bytes,
        content_type: ContentType, **attrs
    ):
        """书籍的每行内容
        
        每行内容包括内容编号, 内容, 内容类型和属性,
        所有数据最终都以服务于呈现 HTML 标签为目的.
        注意: 若内容为 str 类型, 则必须是 UTF-8 编码
        
        :param index: 索引
        :type index: int
        :param content: 内容
        :type content: str | bytes
        :param content_type: 内容类型
        :type content_type: ContentType
        :param attrs: 属性, 键与值都要求为字符串类型
        
        Example:
            >>> Line(
               >>>		0, "Hello, World!", ContentType.Text, 
               >>>		style="color: red;"
            >>> )
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(index, int)
        assert isinstance(content, str) or isinstance(content, bytes)
        assert len(content) > 0
        assert isinstance(content_type, ContentType)
        assert isinstance(content, bytes) == content_type.is_bytes()
        for k, v in attrs.items():
            assert isinstance(k, str)
            assert isinstance(v, str)
        # 初始化数据
        self.__index = index
        self.__content = content
        self.__content_type = content_type
        self.__attrs = attrs
    
    def __repr__(self):
        return f"<Line index={self.__index} " \
            f"content={self.__content[:10]}...>"
    
    def __str__(self):
        if self.__content_type.is_bytes():
            alt = self.__attrs.get("alt", "")
            return alt if alt else ""
        else:
            return self.__content
    
    def __hash__(self):
        hash_str = f"{self.__index}{self.__content}" \
            f"{self.__content_type}{self.__attrs}"
        sha256 = hashlib.sha256()
        sha256.update(hash_str.encode())
        return int(sha256.hexdigest(), 16)
    
    def __eq__(self, other: "Line"):
        if not isinstance(other, Line):
            return False
        return hash(self) == hash(other)
    
    @staticmethod
    def default() -> "Line":
        """创建默认的 Line 对象
        
        :return: Line 对象
        """
        return Line(0, "默认的 Line 对象.", ContentType.Text)
    
    def to_dict(self) -> dict:
        return {
            "index": self.__index,
            "content": self.encode(),
            "content_type": int(self.__content_type),
            "attrs": self.__attrs
        }
    
    @staticmethod
    def from_dict(data: dict) -> "Line":
        """从字典数据中创建 Line 对象
        
        :param data: 字典数据
        :type data: dict
        :return: Line 对象
        """
        # 确认传入的参数的数据类型是否正确
        assert isinstance(data, dict)
        # 获取内容, 内容类型和属性
        index = data.get("index", 0)
        content = data.get("content", "")
        content_type = data.get("content_type", 0)
        attrs = data.get("attrs", {})
        # 确认内容和内容类型的数据类型是否正确
        # # 确认索引的数据类型为 int
        if not isinstance(index, int):
            return Line.default()
        # # 确认内容的数据类型为 str, 并且内容长度大于 0
        if (not isinstance(content, str)) or len(content) == 0:
            return Line.default()
        # # 确认内容类型的数据类型为 int, 并且内容类型在 1-6 之间
        if (not isinstance(content_type, int)) or \
            (content_type not in range(1, 7)):
            return Line.default()
        else:
            content_type = ContentType.to_obj(content_type)
        # # 确认属性的数据类型为 dict, 并且属性的键和值都是字符串
        if not isinstance(attrs, dict):
            return Line.default()
        else:
            for k, v in attrs.items():
                if (not isinstance(k, str)) or (not isinstance(v, str)):
                    return Line.default()
        # 创建 Line 对象
        return Line(
            index, Line.decode(content, content_type.is_bytes()),
            content_type, **attrs
        )
    
    def encode(self) -> str:
        """将内容编码为 base64 编码
        
        :return: base64 编码的内容
        """
        # 获取内容的拷贝
        value = copy.deepcopy(self.__content)
        # 如果内容不是二进制, 则将内容转换为二进制
        if not self.__content_type.is_bytes():
            value = value.encode()
        # 将二进制内容转换为 base64 编码
        value = base64.b64encode(value)
        # 将 base64 编码的内容转换为字符串
        return value.decode()
    
    @staticmethod
    def decode(value: str, is_bytes: bool = False) -> str | bytes:
        """将 base64 编码的内容解码
        
        :param value: base64 编码的内容
        :type value: str
        :param is_bytes: 是否返回二进制内容, 默认为 False
        :type is_bytes: bool
        :return: 解码后的内容
        """
        # 确认传入的参数的数据类型是否正确
        assert isinstance(value, str)
        assert isinstance(is_bytes, bool)
        # 将 base64 编码的内容转换为二进制
        value = value.encode()
        # 将二进制内容解码
        value = base64.b64decode(value)
        # 返回解码后的内容, 如果 is_bytes 为 False, 则将内容转换为字符串
        # 如果 is_bytes 为 True, 则返回二进制内容
        return value if is_bytes else value.decode()
    
    @property
    def index(self) -> int:
        return self.__index
    
    @property
    def content(self) -> str | bytes:
        return self.__content
    
    @property
    def content_type(self) -> ContentType:
        return self.__content_type
    
    @property
    def attrs(self) -> dict:
        return self.__attrs