#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :gui.py
# @Time      :09/11/2022 09:12
# @Author    :Amundsen Severus Rubeus Bjaaland


import time
import tkinter
import threading
import tkinter.ttk
from typing import List
from urllib.parse import urlparse

from .config import WebMap
from .engines import ENGINE_LIST
from .tools import StorageServer


class InfoFrame(tkinter.Frame):
	def __init__(self, map: WebMap):
		super(InfoFrame, self).__init__()
		self.__map = map
		self.__map.chapter_info_callback = self.__chapter_info_callback
		
		self.__info_table = tkinter.ttk.Treeview(self, show='headings')
		self.__info_table["columns"] = (
			"书籍名", "作者名", "书籍状态", "章节总数", "已下载章节数", "当前章节名", "下载速度", "起始下载时间", "数据量"
		)
		self.__info_table["displaycolumns"] = (
			"书籍名", "作者名", "书籍状态", "章节总数", "已下载章节数", "当前章节名", "下载速度"
		)
		self.__info_table.heading("书籍名", text="书籍名")
		self.__info_table.heading("作者名", text="作者名")
		self.__info_table.heading("书籍状态", text="书籍状态")
		self.__info_table.heading("章节总数", text="章节总数")
		self.__info_table.heading("已下载章节数", text="已下载章节数")
		self.__info_table.heading("当前章节名", text="当前章节名")
		self.__info_table.heading("下载速度", text="下载速度")
		self.__info_table.heading("起始下载时间", text="起始下载时间")
		self.__info_table.heading("数据量", text="数据量")
		self.__info_table.column("书籍名", width=300, anchor=tkinter.CENTER)
		self.__info_table.column("作者名", width=150, anchor=tkinter.CENTER)
		self.__info_table.column("书籍状态", width=75, anchor=tkinter.CENTER)
		self.__info_table.column("章节总数", width=75, anchor=tkinter.CENTER)
		self.__info_table.column("已下载章节数", width=100, anchor=tkinter.CENTER)
		self.__info_table.column("当前章节名", width=300, anchor=tkinter.CENTER)
		self.__info_table.column("下载速度", width=150, anchor=tkinter.CENTER)
		self.__info_table.column("起始下载时间", anchor=tkinter.CENTER)
		self.__info_table.column("数据量", anchor=tkinter.CENTER)
		self.__info_table.pack(side=tkinter.TOP)
		
		self.pack(side=tkinter.BOTTOM)
	
	@property
	def info_table(self):
		return self.__info_table
	
	def __chapter_info_callback(
			self, book_name: str, author: str, chapter_name: str, chapter_text: str, chapter_index: int
	):
		for index in self.__info_table.get_children():
			item = self.__info_table.item(index)
			data = item["values"]
			if data[0] == book_name and data[1] == author:
				download_time = time.time() - float(data[7])
				data_volume = int(data[8]) + len(chapter_text.encode("UTF-8"))
				self.__info_table.item(
					index,
					value=(
						data[0], data[1], data[2], data[3], str(chapter_index), chapter_name,
						str(int(data_volume / download_time)) + " Bytes/s", data[7], data_volume
					)
				)
				return None


class SettingsFrame(tkinter.Frame):
	def __init__(self, info_table, map: WebMap, master = None):
		super(SettingsFrame, self).__init__(master)
		self.__master: InfoFrame = master
		self.__info_table = info_table
		self.__map = map
		self.__map.book_info_callback = self.__book_info_callback
		
		self.__url_input_frame = tkinter.Frame(self)
		self.__url_marked_words = tkinter.Label(self.__url_input_frame, text="书籍网址：")
		self.__url_marked_words.pack(side=tkinter.LEFT)
		self.__url_text = tkinter.StringVar()
		self.__url_entry = tkinter.Entry(self.__url_input_frame, textvariable=self.__url_text)
		self.__url_entry.pack(side=tkinter.LEFT)
		self.__download_button = tkinter.Button(self.__url_input_frame, text="下载", command=self.__download_button_func)
		self.__download_button.pack(side=tkinter.LEFT)
		self.__url_input_frame.pack(side=tkinter.TOP)
		
		self.__mode_frame = tkinter.Frame(self)
		self.__mode_marked_words = tkinter.Label(self.__mode_frame, text="下载模式：")
		self.__mode_marked_words.pack(side=tkinter.LEFT)
		self.__mode_flag = tkinter.IntVar()
		self.__mode_flag.set(1)
		self.__mode_button_list = []
		for index, method_flag in enumerate(StorageServer.StorageMethod.ALL):
			radio_button = tkinter.ttk.Radiobutton(
				self.__mode_frame, value=index + 1, text=method_flag[0], variable=self.__mode_flag
			)
			radio_button.pack(side=tkinter.LEFT)
			self.__mode_button_list.append(radio_button)
		radio_button = tkinter.ttk.Radiobutton(
			self.__mode_frame, value=len(StorageServer.StorageMethod.ALL)+1, text="所有格式", variable=self.__mode_flag
		)
		radio_button.pack(side=tkinter.LEFT)
		self.__mode_button_list.append(radio_button)
		self.__mode_frame.pack(side=tkinter.TOP)
		
		self.pack(side=tkinter.BOTTOM)
	
	def __download_button_func(self):
		book_url = self.__url_entry.get()
		if not book_url:
			return None
		thread_buffer = []
		for one_thread in self.__master.thread_list:
			if one_thread.is_alive():
				thread_buffer.append(one_thread)
		self.__thread_list = thread_buffer
		self.__url_entry.delete(0, tkinter.END)
		download_thread = threading.Thread(target=self.__download, args=(book_url,))
		self.__thread_list.append(download_thread)
		download_thread.start()
		return None
	
	def __download(self, book_url, path="./data/book"):
		save_method = StorageServer.StorageMethod.ALL
		for i in StorageServer.StorageMethod.ALL:
			if self.__mode_flag.get() == i[1]:
				save_method = i
				break
		web = self.__map.get_web_by_url(book_url)
		if web.config.name == "默认":
			return None
		if len(urlparse(book_url).netloc.split(".")) == 2:
			book_url = book_url.replace("//", "//www.")
		book = web.download_book(book_url)
		StorageServer(book, save_method).save()
	
	def __book_info_callback(self, name: str, author: str, state: str, desc: str, chapter_numbers: int):
		for index in self.__info_table.get_children():
			item = self.__info_table.item(index)
			data = item["values"]
			if data[0] == name and data[1] == author:
				tkinter.messagebox.showwarning(title='警告', message=f'《{name}》已经在您的下载列表中。')
				break
		else:
			self.__info_table.insert(
				"", tkinter.END,
				values=(name, author, state, str(chapter_numbers), "0", "（空）", "0 Bytes/s", str(time.time()), "0")
			)


class DownloadFrame(tkinter.Frame):
	def __init__(self, master=None):
		super(DownloadFrame, self).__init__(master)
		self.__thread_list: List[threading.Thread] = []
		self.__map = WebMap(lambda a, b, c, d, e: None, lambda a, b, c, d, e: None, lambda a, b: None)
		self.__map.append(ENGINE_LIST)
		
		self.__info_frame = InfoFrame(self.__map)
		self.__settings_frame = SettingsFrame(self.__info_frame.info_table, self.__map, self)
		
		self.pack()
	
	@property
	def info_frame(self):
		return self.__info_frame
	
	@property
	def settings_frame(self):
		return self.__settings_frame
	
	@property
	def thread_list(self):
		return self.__thread_list
