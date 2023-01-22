#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# @FileName  :cache.py
# @Time      :2023/1/21 20:34
# @Author    :Amundsen Severus Rubeus Bjaaland


from novel import UrlGetter,  WebMap, ENGINE_LIST


if __name__ == "__main__":
    m = WebMap(
        lambda a, b, c, d, e: None,
        lambda a, b, c, d, e: None,
        lambda a, b: None
    )
    m.append([ENGINE_LIST[5]])
    u = UrlGetter(m)
    u.join()
