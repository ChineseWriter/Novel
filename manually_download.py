#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :manually_download.py
# @Time      :12/09/2022 11:29
# @Author    :Amundsen Severus Rubeus Bjaaland


from novel import ManDown, BookConfig


if __name__ == "__main__":
	d = ManDown()
	t = BookConfig.DownType
	d.download()
