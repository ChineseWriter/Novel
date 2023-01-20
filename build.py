#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :build.py
# @Time      :03/09/2022 11:42
# @Author    :Amundsen Severus Rubeus Bjaaland


# from novel import ManDown, BookConfig
from novel import MAP


if __name__ == "__main__":
	# d = ManDown()
	# t = BookConfig.DownType
	# d.append(BookConfig("https://www.1718k.com/files/article/html/396/396555/", t.TXT_ONE_FILE, True, "逆天丹帝"))
	# d.download()
	MAP.start_get_url()
	MAP.wait_get_url()
	# a = MAP.books
	# a = [i.book_name for i in a]
	# a = MAP.search_books("天龙狱主")
	b = 0

