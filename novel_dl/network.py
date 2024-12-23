#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: network.py
# @Time: 26/10/2024 16:23
# @Author: Amundsen Severus Rubeus Bjaaland
"""网络相关工具, 简化了一些网络操作, 主要为 Network 类."""


# 导入标准库
from typing import Dict
from urllib.parse import urljoin, urlparse

# 导入第三方库
import requests
from fake_useragent import UserAgent  # 该库是否可以开箱即用暂时存疑
from bs4 import BeautifulSoup as bs


class Network(object):
    # 将 requests 库内置到模块中, 以减少其他模块使用该库时的代码行数
    requests = requests
    # 所有 Network 类共享这一个自动 UserAgent 创建池
    user_agent_pool = UserAgent()
    # URL 支持的协议
    SUPPORTED_PROTOCOLS = ["http", "https"]
    
    def __init__(self, response: requests.Response, encoding: str = "UTF-8"):
        """网络对象,
        提供网络相关的基本操作
        
        :param response: 获取的网页的结果
        :type response: requests.Response
        :param encoding: 网页所使用的编码
        :type encoding: str
        
        Example:
            >>> Network(requests.get("https://example.com/"), "GBK")
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(response, requests.Response)
        assert isinstance(encoding, str)
        # 记录这些参数
        self.__response = response
        self.__encoding = encoding
    
    def get_next_url(self, href: str, lock: bool = False) -> str:
        """获取下一个 URL
        依据自身的 URL 和指定的 a 标签 href 属性进行合理拼接
        
        :param href: 指定的 a 标签 href 属性
        :type href: str
        :param lock: 是否要求下一个网址仍然为该网站的网址
        :type lock: bool
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(href, str)
        # 确认 href 不为 JavaScript 代码
        if href.startswith("javascript:"):
            return ""
        # 确认 href 不为网站主页面
        if href.startswith("www"):
            return ""
        # 确认 href 不为网站的主机名
        if href == urlparse(self.__response.url).netloc:
            return ""
        # 获取下一个 URL
        next_url = urljoin(self.__response.url, href)
        # 确认该 URL 的协议受该程序支持
        if urlparse(next_url).scheme not in self.SUPPORTED_PROTOCOLS:
            return ""
        # 如果要求下一个 URL 为该网站的 URL, 但不满足该条件, 则返回空字符串
        if (lock and (
            urlparse(next_url).netloc != 
            urlparse(self.__response.url).netloc
        )):
            return ""
        # 返回获取的结果
        return next_url
    
    def save_debug_file(self):
        """保存该 URL 获取到的页面, 以支持开发人员进行调试"""
        with open("debug.html", "w", encoding=self.__encoding) as debug_file:
            debug_file.write(self.__response.text)
    
    @classmethod
    def get(
        cls, url: str, encoding: str = "UTF-8",
        redirect: bool = True, **other_headers
    ):
        """使用 GET 方法获取 Web 页面
        该方法主要将 requests.get 函数进行包装
        
        :param url: 要获取的页面的 URL
        :type url: str
        :param encoding: 要获取页面的编码
        :type encoding: str
        :param redirect: 是否允许重定向
        :type redirect: bool
        :param other_headers: 其它的要带在 headers 中的参数,
            若未指定 User_Agent, 则使用随机 Firefox 的 UA
        """
        # 确认传入的参数的类型是否正确
        buffer: Dict[str, str] = {}
        for key, item in other_headers.items():
            if isinstance(item, str):
                buffer[key] = item
        # 给最终的 headers 添加 User-Agent 值
        if "User_Agent" not in buffer:
            # 若未指定 UA 则使用默认的随机 UA
            ua_ = cls.user_agent_pool.firefox
            buffer["User-Agent"] = ua_ if isinstance(ua_, str) else \
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"
        else:
            # 若指定了 UA 则将键的名称改为合法的
            buffer["User-Agent"] = buffer["User_Agent"]
            buffer.pop("User_Agent")
        # 获取页面并返回
        return Network(
            requests.get(url, allow_redirects=redirect, headers=buffer),
               encoding
        )
    
    @property
    def response(self):
        return self.__response
    
    @property
    def encoding(self):
        return self.__encoding
    
    @property
    def text(self):
        self.__response.encoding = self.__encoding
        return self.__response.text
    
    @property
    def content(self):
        return self.__response.content
    
    @property
    def bs(self):
        return bs(self.text.replace("\xa0", ""), "lxml")
    
    @property
    def h1(self):
        result = bs(self.text, "lxml").find("h1")
        if result:
            return result.text
        else:
            return ""