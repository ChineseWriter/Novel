#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :manually_download.py
# @Time      :12/09/2022 11:29
# @Author    :Amundsen Severus Rubeus Bjaaland


from novel import BookConfig, ManDown


if __name__ == "__main__":
	DOWNLOAD_TYPE = ManDown.DOWNLOAD_TYPE
	download_server = ManDown()
	download_server.append(BookConfig("https://fanqienovel.com/page/7108317482728819726", DOWNLOAD_TYPE.TXT_ONE_FILE, False, "小山河"))
	download_server.append(BookConfig("https://www.xddxs.cc/read/18314/", DOWNLOAD_TYPE.TXT_ONE_FILE, False, "仙武神煌"))
	download_server.append(BookConfig("https://www.tatajk.net/book/6748/", DOWNLOAD_TYPE.TXT_ONE_FILE, False, "仙魔同修"))
	download_server.append(BookConfig("https://www.bequwx.com/3/3803/", DOWNLOAD_TYPE.TXT_ONE_FILE, False, "魔门败类"))
	download_server.append(BookConfig("https://www.qb5.la/book_23116/", DOWNLOAD_TYPE.TXT_ONE_FILE, False, "仙韵传"))
	download_server.append(BookConfig("https://www.81zw.com/book/127131/", DOWNLOAD_TYPE.TXT_ONE_FILE, False, "斗破之无上之境"))
	download_server.append(BookConfig("https://www.bequge.cc/book/291/", DOWNLOAD_TYPE.TXT_ONE_FILE, False, "霸天龙帝"))
	download_server.append(BookConfig("https://www.1718k.com/files/article/html/155/155487/", DOWNLOAD_TYPE.TXT_ONE_FILE, True, "暴力丹尊"))
	download_server.download()
	b = 0
