#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# @FileName  :cache.py
# @Time      :2023/1/21 20:34
# @Author    :Amundsen Severus Rubeus Bjaaland


import signal, sys


from novel import UrlGetter,  WebMap, ENGINE_LIST


if __name__ == "__main__":
    m = WebMap(
        lambda a, b, c, d, e: None,
        lambda a, b, c, d, e: None,
        lambda a, b: None
    )
    m.append(ENGINE_LIST)
    
    u = UrlGetter(m)


    def exit(sig, frame):
        print("即将退出程序。")
        u.finish()
        sys.exit(0)
    

    signal.signal(signal.SIGHUP, exit)
    signal.signal(signal.SIGINT, exit)
    signal.signal(signal.SIGQUIT, exit)
    # signal.signal(signal.SIGKILL, exit)
    signal.signal(signal.SIGALRM, exit)
    signal.signal(signal.SIGTERM, exit)

    u.join()
