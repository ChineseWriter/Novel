#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :build.py
# @Time      :03/09/2022 11:42
# @Author    :Amundsen Severus Rubeus Bjaaland


from novel import BookConfig, ManDown


if __name__ == "__main__":
	DOWNLOAD_TYPE = ManDown.DOWNLOAD_TYPE
	download_server = ManDown()
	download_server.append(BookConfig("https://fanqienovel.com/page/7108317482728819726", DOWNLOAD_TYPE.TXT_ONE_FILE, True, "小山河"))
	download_server.append(BookConfig("https://www.xddxs.cc/read/89259/", DOWNLOAD_TYPE.TXT_ONE_FILE, True, "医婿"))
	download_server.append(BookConfig("https://www.tatajk.net/book/39600/", DOWNLOAD_TYPE.TXT_ONE_FILE, True, "惹哭"))
	download_server.append(BookConfig("https://www.bequwx.com/167/167515/", DOWNLOAD_TYPE.TXT_ONE_FILE, True, "她曾热情似火"))
	download_server.append(BookConfig("https://www.qb5.la/book_109623/", DOWNLOAD_TYPE.TXT_ONE_FILE, True, "男神撩妻：魔眼小神医"))
	download_server.append(BookConfig("https://www.81zw.com/book/113940/", DOWNLOAD_TYPE.TXT_ONE_FILE, True, "快穿万人迷：男主你们不要在打了"))
	download_server.append(BookConfig("https://www.bequge.cc/book/32456/", DOWNLOAD_TYPE.TXT_ONE_FILE, True, "将军，夫人喊你种田了"))
	download_server.append(BookConfig("https://www.1718k.com/files/article/html/230/230574/", DOWNLOAD_TYPE.TXT_ONE_FILE, True, "重回九零她靠科研暴富了"))
	download_server.download()
	b = 0

