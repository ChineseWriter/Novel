#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# @FileName  :search.py
# @Time      :2023/1/22 13:13
# @Author    :Amundsen Severus Rubeus Bjaaland


from novel import WebUrlManager, ENGINE_LIST


if __name__ == "__main__":
    manager = WebUrlManager(ENGINE_LIST[5])
    book_list = manager.search_books("修")
    a = 0
