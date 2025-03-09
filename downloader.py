#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: main.py
# @Time: 23/02/2024 19:31
# @Author: Amundsen Severus Rubeus Bjaaland
"""程序主要功能的入口文件, 用于连接主要支持库与命令行."""


# 导入标准库
import os
import sys

# 导入第三方库
import fire

# 导入自定义库
import novel_dl
from novel_dl.core.books import SaveMethod, Saver
from novel_dl.services.download import WebManager


class Pipeline(object):
    def test_cmd(self):
        print("命令行可正常使用。")

    def run_test(self):
        import pytest
        pytest.main(["-s", "tests"])
    
    def download_novel(self, url: str, save_method: int = 1):
        method = SaveMethod.to_obj(save_method)
        manager = WebManager()
        
        def test(chapter):
            print(chapter.name)
            return chapter
        
        book = manager.download(url, chapter_middle_ware=test)
        if book is not None:
            Saver(book, method).save()
    
    def download_novels(self, save_method: int = 1):
        BOOK_URLS_FILE = "book_urls.txt"
        # 将数字表示的保存方式改为保存方式常量
        method = novel_dl.Book.SaveMethod.transform(save_method)
        # 获取网站引擎管理类
        manager = novel_dl.WebManager()
        # 确保书籍网址文件存在, 不存在则自动创建
        if not os.path.exists(BOOK_URLS_FILE):
            print(f"未找到书籍 URL 配置文件({BOOK_URLS_FILE}), 将自动创建. ")
            open(BOOK_URLS_FILE, "w", encoding="UTF-8").close()
            return None
        # 读取书籍网址文件, 并按行将其转换为列表
        with open(BOOK_URLS_FILE, "r", encoding="UTF-8") as book_urls_file:
            urls = [i.strip("\n") for i in book_urls_file.readlines()]
        for one_url in urls:
            # 下载指定的书籍并保存
            book = manager.download(one_url)
            if book != novel_dl.Book.empty_book():
                book.save(method)
        # 退出程序
        return None
    
    # TODO 在 README 文件中给这个命令添加说明
    def download_novel_by_name(
        self, save_method: int = 1
    ):
        # 获取书籍引擎管理类
        manager = novel_dl.WebManager()
        # 获取书架
        bookshelf = novel_dl.BookShelf()
        
        # 获取书籍名称
        name = input("请输入要搜索的书籍名称: ")
        # 搜索书籍
        print("查找书籍中 . . .", end="")
        # TODO 限制获取上限
        books = list(bookshelf.search_books_by_name(name))
        if len(books) == 0:
            print("未找到符合条件的书籍. 程序即将退出.")
            return None
        print("查找完成!\n结果如下: ")
        for i, (one_book, sources) in enumerate(books):
            print(f"{i + 1}.{one_book.author} - {one_book.name}")
        # 选择书籍
        try:
            index = int(input("请输入要下载的书籍序号: "))
            assert 0 < index <= len(books)
        except (ValueError, AssertionError):
            print("输入的序号不合法!")
            return None
        one_book, sources = books[index - 1]
        
        # 展示书籍来源
        if len(sources) != 1:
            for i, source in enumerate(sources):
                print(
                    f"{i + 1}." \
                    f"[{manager.get_engine(source).name}]" \
                    f"{source}"
                )
            # 选择书籍来源
            try:
                index = int(input("请输入要下载的书籍来源序号: "))
                assert 0 < index <= len(sources)
            except (ValueError, AssertionError):
                print("输入的序号不合法!")
                return None
            source = sources[index - 1]
        else:
            print("仅有一个来源, 将自动选择.")
            source = sources[0]

        # 下载书籍
        print(f"开始下载书籍({one_book.name})的内容. . .\n\n")
        self.download_novel(source, save_method)
        print("\n书籍下载完成!")
        # 退出程序
        return None


if __name__ == "__main__":
    # 添加工作目录, 工作目录为该文件所在目录
    sys.path.append(os.getcwd())
    # 进入程序
    if len(sys.argv) == 1:
        # TODO 撰写可用的 GUI 界面
        print("该程序暂时不支持默认运行(GUI 界面)哦!")
    else:
        fire.Fire(Pipeline)
    # 程序正常退出
    sys.exit(0)