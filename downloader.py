#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: main.py
# @Time: 23/02/2024 19:31
# @Author: Amundsen Severus Rubeus Bjaaland


# 导入标准库
import os
import sys

# 导入第三方库
import fire

# 导入自定义库
import downloader


class Pipeline(object):
    SAVE_METHOD = downloader.Book.SaveMethod
    
    def __init__(self, debug: bool = False):
        self.__settings = downloader.Settings
        self.__settings.DEBUG = debug # type: ignore

    def test_cmd(self):
        print("命令行可正常使用。")

    def run_test(self):
        import pytest
        pytest.main(["-s", "tests"])
    
    def download_novel(self, url: str, multi_thread: int = 1, save_method: int = 1):
        # 将数字表示的保存方式改为保存方式常量
        method = downloader.Book.SaveMethod.transform(save_method)
        # 获取网站引擎管理类
        manager = downloader.WebManager()
        manager.append_default_engine()
        
        # 下载指定的书籍
        book = manager.download(url, True if multi_thread else False)
        # 保存书籍后退出程序
        if book != downloader.EMPTY_BOOK:
            book.save(method)
        return None
    
    def download_novels(self, multi_thread: int = 1, save_method: int = 1):
        BOOK_URLS_FILE = "book_urls.txt"
        # 将数字表示的保存方式改为保存方式常量
        method = downloader.Book.SaveMethod.transform(save_method)
        # 将数字表示的多线程标志转换为标准标志
        multi_thread_flag = True if multi_thread else False
        # 获取网站引擎管理类
        manager = downloader.WebManager()
        manager.append_default_engine()
        
        if not os.path.exists(BOOK_URLS_FILE):
            print(f"未找到书籍 URL 配置文件({BOOK_URLS_FILE}), 将自动创建. ")
            with open(BOOK_URLS_FILE, "w", encoding="UTF-8"):
                pass
            return None
        
        with open(BOOK_URLS_FILE, "r", encoding="UTF-8") as book_urls_file:
            urls = [i.strip("\n") for i in book_urls_file.readlines()]
        
        # TODO 修复部分网站不支持多线程下载的问题
        # if multi_thread_flag:
        #     from concurrent.futures import ThreadPoolExecutor, as_completed
            
        #     def download(one_url: str, multi_thread_flag: bool) -> bool:
        #         # 下载指定的书籍
        #         book = manager.download(one_url, multi_thread_flag)
        #         # 保存书籍后退出程序
        #         if book != downloader.EMPTY_BOOK:
        #             book.save(method)
        #             return True
        #         return False
            
        #     with ThreadPoolExecutor(5, thread_name_prefix="书籍下载线程") as executor:
        #         future_to_url = {
        #             executor.submit(
        #                 download, one_url, multi_thread_flag
        #             ): one_url
        #             for one_url in urls
        #         }
        #         as_completed(future_to_url)
            
        #     return None
        
        for one_url in urls:
            # 下载指定的书籍
            book = manager.download(one_url, multi_thread_flag)
            # 保存书籍后退出程序
            if book != downloader.EMPTY_BOOK:
                book.save(method)
        return None


if __name__ == "__main__":
    # 添加工作目录
    sys.path.append(os.getcwd())
    if len(sys.argv) == 1:
        # TODO 撰写可用的 GUI 界面
        print("该程序暂时不支持默认运行(GUI 界面)哦!")
    else:
        fire.Fire(Pipeline)
