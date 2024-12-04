#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: building.py
# @Time: 25/11/2024 22:42
# @Author: Amundsen Severus Rubeus Bjaaland


from downloader.web_engines import Engine3


if __name__ == "__main__":
    engine = Engine3()
    cookie = engine.get_cookie()
    a = 0