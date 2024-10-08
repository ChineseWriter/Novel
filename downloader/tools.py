#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: tools.py
# @Time: 13/06/2024 17:45
# @Author: Amundsen Severus Rubeus Bjaaland


#导入标准库
import os


def mkdir(path: str) -> None:
    """创建文件夹，若文件夹已存在则不进行任何操作
    
    :param path: 要创建的文件的路径
    """
    try: os.makedirs(path)
    except FileExistsError: pass