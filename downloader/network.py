#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: network.py
# @Time: 26/10/2024 16:23
# @Author: Amundsen Severus Rubeus Bjaaland


from typing import Dict
from urllib.parse import urljoin

import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup as bs


class Network:
    requests = requests
    user_agent_pool = UserAgent()
    
    def __init__(self, response: requests.Response, encoding: str = "UTF-8"):
        self.__response = response
        self.__encoding = encoding
    
    def get_next_url(self, href: str):
        # TODO 完成传入HREF属性检查避免运行出错
        return urljoin(self.__response.url, href)
    
    def save_debug_file(self):
        with open("debug.html", "w", encoding=self.__encoding) as debug_file:
            debug_file.write(self.__response.text)
    
    @classmethod
    def get(cls, url: str, encoding: str = "UTF-8", **other_headers):
        buffer: Dict[str, str] = {}
        for key, item in other_headers:
            if isinstance(item, str):
                buffer[key] = item
        ua_ = cls.user_agent_pool.random
        ua = ua_ if isinstance(ua_, str) else \
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0"
        return Network(
			requests.get(
       			url, headers={"User-Agent": ua, **buffer}
          	),
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


if __name__ == "__main__":
	VERSION = "0.1.0"