#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: building.py
# @Time: 25/11/2024 22:42
# @Author: Amundsen Severus Rubeus Bjaaland


from downloader import Book
from downloader.prestore import PreStore
from downloader.web_engines import Engine2


def callback(book: Book):
    print(
        f"找到了一本书书籍, 以下是它的基本信息:\n\t书籍名: 《{book.name}》\n" \
		f"\t作者名: {book.author}\n\t状态: {book.state.value[0]}\n" \
		f"\t简介: {book.desc.replace('\n', '\n\t')}\n"
    )


if __name__ == "__main__":
    pre_store = PreStore(Engine2(), callback)
    pre_store.join()
    a = 0