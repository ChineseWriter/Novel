#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :engines.py
# @Time      :04/09/2022 12:04
# @Author    :Amundsen Severus Rubeus Bjaaland


import re
import copy

from bs4 import BeautifulSoup as bs

from ..object import Book, BookData, ChapterData
from .object import WebConfig, Web, WebMap
from ..tools import Network, get_response


class Config_1(WebConfig):
	main_url = "www.fanqienovel.com"
	name = "番茄小说"
	book_url_pattern = "^\/page\/\d+$"
	chapter_url_pattern = "^\/reader\/\d+$"
	encoding = "UTF-8"
	
	def get_book_info(self, response: Network):
		book_name = response.BS.find("h1").text
		author_name = response.BS.find("div", attrs={"class": "author-name"}).text
		state_text = response.BS.find("div", attrs={"class": "info-label"}).find("span").text
		state = Book.BookState.END if state_text == "已完结" else Book.BookState.SERIALIZING
		desc = response.BS.find("div", attrs={"class": "page-abstract-content"}).text
		chapters = response.BS.find_all("a", attrs={"class": "chapter-item-title"})
		chapter_list = []
		for index, one_chapter in enumerate(chapters):
			chapter_list.append((response.get_next_url(one_chapter["href"]), one_chapter.text))
		return BookData(book_name, author_name, state, desc, response.response.url, chapter_list)
	
	def get_chapter_text(self, response: Network, index: int):
		text_div = response.BS.find("div", attrs={"class": "muye-reader-content noselect"})
		text_list = text_div.find_all("p")
		text_list = [text.text for text in text_list]
		text_list = list(filter(lambda x: True if x else False, text_list))
		text = "\t" + "\n\t".join(text_list)
		return ChapterData(index, text)


class Config_2(WebConfig):
	main_url = "www.xddxs.cc"
	name = "新顶点小说"
	book_url_pattern = "^\/read\/\d+\/$"
	chapter_url_pattern = "^\/read\/\d+\/\d+\.html$"
	encoding = "GBK"
	
	def get_book_info(self, response: Network) -> BookData:
		book_name = response.BS.find("h1").text
		info_block = response.BS.find("div", attrs={"id": "info"}).find_all("p")
		author_name, state_text = info_block[0].text.split("：")[1], info_block[1].text.split("：")[1]
		state = Book.BookState.END if state_text == "完结" else Book.BookState.SERIALIZING
		desc = response.BS.find("div", attrs={"id": "intro"}).find("p").text.rstrip("\n").lstrip(" ")
		chapters = response.BS.find("div", attrs={"class": "listmain"}).find_all("a")[6:]
		chapter_list = []
		for index, one_chapter in enumerate(chapters):
			chapter_list.append((response.get_next_url(one_chapter["href"]), one_chapter.text))
		return BookData(book_name, author_name, state, desc, response.response.url, chapter_list)
	
	def get_chapter_text(self, response: Network, index: int) -> ChapterData:
		div = response.BS.find("div", attrs={"id": "content"})
		str_div = str(div)
		str_content = str_div[34:-6]
		content = str_content.replace(" ", "\t").replace("\r", "\n").replace("<br/>", "").replace(" ", "")
		text = "\t" + "\n\t".join(content.split("\n\t")[:-1])
		return ChapterData(index, text)


class Config_3(WebConfig):
	main_url = "www.tatajk.net"
	name = "笔趣阁小说"
	book_url_pattern = "^\/book\/\d+\/$"
	chapter_url_pattern = "^\/book\/\d+\/\d+\.html$"
	encoding = "UTF-8"
	
	def get_book_info(self, response: Network) -> BookData:
		book_name = response.BS.find("h1").text
		info_block = response.BS.find("div", attrs={"id": "info"}).find_all("p")
		author_name, state_text = info_block[0].text.split("：")[1], info_block[1].text.split("：")[1].split(" ")[0]
		state = Book.BookState.END if state_text == "全本" else Book.BookState.SERIALIZING
		desc = response.BS.find("div", attrs={"id": "intro"}).text.split("【")[0].lstrip("\n")
		chapter_list = []
		bs_object = response.BS
		while True:
			chapters = bs_object.find("div", attrs={"id": "list"}).find("dl")
			chapter_text = re.split("<dt>.*?<\/dt>", str(chapters).replace("\n", ""))[2]
			chapters = bs(chapter_text, "lxml").find_all("a")
			for one_chapter in chapters:
				chapter_list.append((response.get_next_url(one_chapter["href"]), one_chapter["title"]))
			flag = response.get_next_url(
				bs_object.find(
					"div", attrs={"class": "page chapter_page clearfix"}
				).find(
					"a", attrs={"class": "next"}
				)["href"]
			)
			if flag != response.response.url:
				bs_object = get_response(response.get_next_url(flag)).BS
			else:
				break
		return BookData(book_name, author_name, state, desc, response.response.url, chapter_list)
	
	def get_chapter_text(self, response: Network, index: int) -> ChapterData:
		div_tag = response.BS.find("div", attrs={"id": "content"})
		text = "\t" + "\n\t".join([p_tag.text.replace("\n", "") for p_tag in div_tag.find_all("p")])
		return ChapterData(index, text)


class Config_4(WebConfig):
	main_url = "www.bequwx.com"
	name = "笔趣阁小说"
	book_url_pattern = "^\/\d+\/\d+\/$"
	chapter_url_pattern = "^\/\d+\/\d+\/\d+\.html$"
	encoding = "UTF-8"
	
	def get_book_info(self, response: Network) -> BookData:
		book_name = response.BS.find("h1").text
		author_name = response.BS.find("div", attrs={"id": "info"}).find("p").text.split("：")[1]
		state = Book.BookState.SERIALIZING
		desc = response.BS.find("div", attrs={"id": "intro"}).text
		desc = desc.replace("\r", "").replace("\n", "").replace(" ", "").replace(" ", "")
		chapters = response.BS.find("div", attrs={"id": "list"}).find("dl")
		chapter_text = re.split("<dt>.*?<\/dt>", str(chapters).replace("\n", ""))[2]
		chapters = bs(chapter_text, "lxml").find_all("a")
		chapter_list = []
		for one_chapter in chapters:
			chapter_list.append((response.get_next_url(one_chapter["href"]), one_chapter.text))
		return BookData(book_name, author_name, state, desc, response.response.url, chapter_list)
	
	def get_chapter_text(self, response: Network, index: int) -> ChapterData:
		div_tag = response.BS.find("div", attrs={"id": "content"})
		content_list = re.split(
			"<div.*?>.*?</div>",
			re.split(
				"<p>.*?</p>", str(div_tag)[27:-6].replace("\n", "").replace("\r", "").replace(" ", "").replace(" ", "")
			)[1]
		)[0].split("<br/>")
		content_list = filter(lambda x: True if x else False, content_list)
		text = "\t" + "\n\t".join(content_list)
		return ChapterData(index, text)


class Config_5(WebConfig):
	main_url = "www.qb5.la"
	name = "全本小说网"
	book_url_pattern = "^\/book\_\d+\/$"
	chapter_url_pattern = "^\/book\_\d+\/\d+\.html$"
	encoding = "GBK"
	
	def get_book_info(self, response: Network) -> BookData:
		h1_tag = response.BS.find("h1").text.replace(" ", "").split("/")
		book_name, author_name = h1_tag[0], h1_tag[1]
		state_text = response.BS.find("p", attrs={"class": "booktag"}).find_all("span")[1].text
		state = Book.BookState.END if state_text == "已完成" else Book.BookState.SERIALIZING
		desc = response.BS.find("div", attrs={"id": "intro"}).text.lstrip(" ")
		chapters = response.BS.find("dl", attrs={"class": "zjlist"}).find_all("a")
		chapter_list = []
		for one_chapter in chapters:
			chapter_list.append((response.get_next_url(one_chapter["href"]), one_chapter.text))
		return BookData(book_name, author_name, state, desc, response.response.url, chapter_list)
	
	def get_chapter_text(self, response: Network, index: int) -> ChapterData:
		str_div = str(response.BS.find("div", attrs={"id": "content"})).replace("\xa0", "").replace(" ", "")
		content_list = list(filter(lambda x: True if x else False, str_div.split("<br/>")[1:]))
		content_list[-1] = content_list[-1].rstrip("</div>")
		text = "\t" + "\n\t".join(content_list)
		return ChapterData(index, text)


class Config_6(WebConfig):
	main_url = "www.81zw.com"
	name = "81中文网"
	book_url_pattern = "^\/book\/\d+\/$"
	chapter_url_pattern = "^\/book\/\d+\/\d+\.html$"
	encoding = "UTF-8"
	
	def get_book_info(self, response: Network) -> BookData:
		book_name = response.BS.find("h1").text
		info_block = response.BS.find("div", attrs={"id": "info"}).find_all("p")
		author_name = info_block[0].text.split("：")[1].replace(" ", "")
		state_text = info_block[1].text.split("：")[1].split(",")[0].replace("\n", "")
		state = Book.BookState.END if state_text == "完本" else Book.BookState.SERIALIZING
		desc = response.BS.find("div", attrs={"id": "intro"}).find("p").text.replace("\n", "")
		chapters = response.BS.find("div", attrs={"id": "list"}).find_all("a")
		chapter_list = []
		for one_chapter in chapters:
			chapter_list.append((response.get_next_url(one_chapter["href"]), one_chapter.text))
		return BookData(book_name, author_name, state, desc, response.response.url, chapter_list)
	
	def get_chapter_text(self, response: Network, index: int) -> ChapterData:
		div_tag = response.BS.find("div", attrs={"id": "content"})
		str_div = str(div_tag)[18:-6]
		content_list = list(
			filter(
				lambda x: True if x else False,
				str_div.replace("\n", "").replace(" ", "").replace("\u3000", "").split("<br/>")
			)
		)
		content_buffer = []
		for i in content_list:
			if i == "网页版章节内容慢，请下载爱阅小说app阅读最新内容":
				break
			else:
				content_buffer.append(i.replace("www.八壹zw.ćőm", "").replace("m.81ZW.ćőm", "").replace("八壹中文網", ""))
		text = "\t" + "\n\t".join(content_buffer)
		return ChapterData(index, text)
	
	def is_protected(self, response: Network, text: str) -> bool:
		if response.response.status_code != 200:
			return True


class Config_7(WebConfig):
	main_url = "www.bequge.cc"
	name = "新笔趣阁"
	book_url_pattern = "^\/book\/\d+\/$"
	chapter_url_pattern = "^\/book\/\d+\/\d+\.html$"
	encoding = "UTF-8"
	
	Pattern_1 = re.compile("\n\n.*?\r")
	
	def get_book_info(self, response: Network) -> BookData:
		book_name = response.BS.find("h1").text
		info_block = response.BS.find("p", attrs={"class": "booktag"})
		author_name = info_block.find_all("a")[0].text
		if author_name in book_name:
			book_name = book_name.strip(author_name)
		state_text = info_block.find_all("span")[1].text
		state = Book.BookState.END if state_text == "完本" else Book.BookState.SERIALIZING
		desc = response.BS.find("div", attrs={"class": "row"}).find_all("p")[-1].text
		chapters = response.BS.find("div", attrs={"id": "list-chapterAll"}).find_all("a")
		chapter_list = []
		for one_chapter in chapters:
			chapter_list.append((response.get_next_url(one_chapter["href"]), one_chapter.get("title")))
		return BookData(book_name, author_name, state, desc, response.response.url, chapter_list)
	
	def get_chapter_text(self, response: Network, index: int) -> ChapterData:
		text_list = response.BS.find("div", attrs={"id": "htmlContent"}).find_all("p")
		text_list = [self.Pattern_1.sub("", i.text.replace(" ", "").strip("\n")) for i in text_list]
		text_list = list(filter(lambda x: True if x else False, text_list))
		text = "\t" + "\n\t".join(text_list)
		return ChapterData(index, text)


class Config_8(WebConfig):
	main_url = "www.1718k.com"
	name = "1718K文学"
	book_url_pattern = "^\/files\/article\/html\/\d+\/\d+\/$"
	chapter_url_pattern = "^\/files\/article\/html\/\d+\/\d+\/\d+\.html$"
	encoding = "UTF-8"
	
	def get_book_info(self, response: Network) -> BookData:
		book_name = response.BS.find("div", attrs={"id": "bookinfo"}).find("h1").text
		author_name = response.BS.find("span", attrs={"class": "p_author"}).find("a").text
		state_text = response.BS.find("div", attrs={"id": "count"}).find_all("span")[2].text
		state = Book.BookState.END if state_text == "全本" else Book.BookState.SERIALIZING
		try:
			desc = response.BS.find("div", attrs={"id": "bookintro"}).find("p").text
		except AttributeError:
			desc = "书籍简介缺失"
		chapters = response.BS.find("ul", attrs={"id": "chapterList"}).find_all("a")
		chapter_list = []
		for one_chapter in chapters:
			chapter_list.append((response.get_next_url(one_chapter["href"]), one_chapter.text))
		return BookData(book_name, author_name, state, desc, response.response.url, chapter_list)
	
	def get_chapter_text(self, response: Network, index: int) -> ChapterData:
		present_bs_object = response.BS
		content_buffer = []
		while True:
			next_url_a_tag = present_bs_object.find("a", attrs={"id": "next_url"})
			content_buffer.append([i.text for i in present_bs_object.find("div", attrs={"id": "TextContent"}).find_all("p")])
			flag_text = next_url_a_tag.text.strip(" ")
			if flag_text != "下一章":
				present_bs_object = get_response(response.get_next_url(next_url_a_tag.get("href"))).BS
			else:
				break
		text_list = []
		for i in content_buffer:
			for ii in i:
				text_list.append(ii.replace("\r", ""))
		text = "\t" + "\n\t".join(text_list)
		return ChapterData(index, text)


MAP = WebMap(lambda a, b, c, d, e: None, lambda a, b, c, d, e: None, lambda a, b: None)
MAP.append(Config_1())
MAP.append(Config_2())
MAP.append(Config_3())
MAP.append(Config_4())
MAP.append(Config_5())
MAP.append(Config_6())
MAP.append(Config_7())
MAP.append(Config_8())
