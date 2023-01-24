#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# @FileName  :novel_cmd.py
# @Time      :2023/1/23 12:46
# @Author    :Amundsen Severus Rubeus Bjaaland


import sys, signal

from novel import UrlGetter,  WebMap, ENGINE_LIST


if __name__ == "__main__":
    map = WebMap(
        lambda a, b, c, d, e: None,
        lambda a, b, c, d, e: None,
        lambda a, b: None
    )
    map.append([ENGINE_LIST[1]])
    
    url_getter = UrlGetter(map)


    def exit(sig, frame):
        print("即将退出程序。")
        url_getter.finish()
        sys.exit(0)
    

    signal.signal(signal.SIGINT, exit)
    url_getter.start()

    while True:
        input_text = str(input())
        data = input_text.split(" ")
        match data[0]:
            case "exit":
                url_getter.finish()
                sys.exit(0)
            case "db_info":
                for i in url_getter.db_info():
                    print(
                        f"{i['Name']}: 网址共有{i['Info'][0]}个, "
                        f"已下载网址共有{i['Info'][0]}个, 书籍共有{i['Info'][0]}本"
                    )
            case "search":
                for i in url_getter.search(data[1]):
                    print(i)

