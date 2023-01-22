#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# @FileName  :search.py
# @Time      :2023/1/22 13:13
# @Author    :Amundsen Severus Rubeus Bjaaland


from novel import UrlGetter, WebMap, ENGINE_LIST


if __name__ == "__main__":
    map = WebMap(
        lambda a, b, c, d, e: None,
        lambda a, b, c, d, e: None,
        lambda a, b: None
    )
    map.append(ENGINE_LIST)
    manager = UrlGetter(map)
    manager.pause()
    book_list = manager.search("修")
    a = 0
