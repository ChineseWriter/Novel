#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: fs.py
# @Time: 18/02/2025 18:02
# @Author: Amundsen Severus Rubeus Bjaaland


import os


# Windows 路径中所有非法字符及其替代方案
_ILLEGAL_CHARS = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
_ILLEGAL_CHARS_REP = ['＜', '＞', '：', '＂', '／', '＼', '｜', '？', '＊']


def mkdir(path: str) -> None:
    """创建文件夹，若文件夹已存在则不进行任何操作
    
    :param path: 要创建的文件的路径
    """
    # 确保 path 是 str 类型
    assert isinstance(path, str)
    # 创建文件夹
    try:
        os.makedirs(path)
    except FileExistsError:
        pass


def sanitize_filename(text: str) -> str:
	"""替换非法字符
	
	:param text: 将要检查的字符串
	:type text: str
	
	Example:
		>>> sanitize_filename("测试字符串")
	"""
	# 检查每一个非法字符的存在情况, 如果存在则替换掉
	for char, char_rep in zip(_ILLEGAL_CHARS, _ILLEGAL_CHARS_REP):
		text = text.replace(char, char_rep)
	# 返回替换以后的字符串
	return text