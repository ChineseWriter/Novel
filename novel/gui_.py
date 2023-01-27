#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :gui.py
# @Time      :01/26/2023 18:25
# @Author    :Amundsen Severus Rubeus Bjaaland


import time
import tkinter
import threading
from tkinter import messagebox

from .tools import StorageServer
from .config import WebMap
from .engines import ENGINE_LIST


class BookInfoCollectFrame(tkinter.Frame):
	def __init__(self, book_info_callback, master=None):
		super(BookInfoCollectFrame, self).__init__(master)
		self.__book_info_callback = book_info_callback
		self.__setup_ui()
		self.pack()
	
	def __setup_ui(self):
		self.__url_marked_words = tkinter.Label(self, text="书籍网址：")
		self.__url_marked_words.pack(side=tkinter.LEFT)
		self.__url_text = tkinter.StringVar()
		self.__url_entry = tkinter.Entry(self, textvariable=self.__url_text)
		self.__url_entry.pack(side=tkinter.LEFT)
		self.__download_button = tkinter.Button(self, text="下载", command=self.__book_info_callback)
		self.__download_button.pack(side=tkinter.LEFT)
		self.pack()
	
	@property
	def book_info(self):
		book_url = self.__url_entry.get()
		self.__url_entry.delete(0, tkinter.END)
		return book_url


class ProgressInfoFrame(tkinter.Frame):
	def __init__(self, master=None):
		super(ProgressInfoFrame, self).__init__(master)
		self.__setup_ui()
		self.pack()
	
	def __setup_ui(self):
		self.__info_table = tkinter.ttk.Treeview(
			self, show='headings', height=50
			)
		self.__info_table["columns"] = (
			"书籍名", "作者名", "书籍状态", "章节总数",
			"已下载章节数", "当前章节名", "下载速度", "起始下载时间", "数据量"
		)
		self.__info_table["displaycolumns"] = (
			"书籍名", "作者名", "书籍状态", "章节总数",
			"已下载章节数", "当前章节名", "下载速度"
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
		self.__info_table.pack()
	
	@property
	def info_table(self):
		return self.__info_table


class DownloadFrame(tkinter.Frame):
	def __init__(self, master=None):
		super(DownloadFrame, self).__init__(master)
		self.__download_thread_list = []
		self.__map = WebMap(
			self.__book_info_callback,
			self.__chapter_info_callback,
			lambda a, b: None
		)
		self.__map.append(ENGINE_LIST)

		self.__generate_menu()
		self.__setup_ui()
		self.pack()
	
	def __generate_menu(self):
		self.__main_menu = tkinter.Menu(self)

		self.__download_options_menu = tkinter.Menu(self.__main_menu, tearoff=False)
		self.__download_type_flag = tkinter.IntVar()
		self.__download_type_flag.set(1)
		for type in StorageServer.StorageMethod.ALL:
			self.__download_options_menu.add_radiobutton(
				label=f"保存为{type[0]}", variable=self.__download_type_flag,
				value=type[1]
			)
		
		
		self.__main_menu.add_command (label="文件")
		self.__main_menu.add_cascade(label="下载选项", menu=self.__download_options_menu)
	
	def __setup_ui(self):
		self.__book_info_collect_frame = BookInfoCollectFrame(
			self.__download_button_callback, self
		)
		self.__progress_info_frame = ProgressInfoFrame(
			self
		)
	
	@property
	def thread_list(self):
		return self.__download_thread_list
	
	@property
	def web_map(self):
		return self.__map
	
	@property
	def main_menu(self):
		return self.__main_menu
	
	@property
	def book_info_collect_frame(self):
		return self.__book_info_collect_frame
	
	@property
	def download_thread_list(self):
		return self.__download_thread_list
	
	def __download(self, book_url: str):
		StorageServer(
			self.__map.download(book_url), 
			StorageServer.StorageMethod.get(
				self.__download_type_flag
			)
		).save()
	
	def __download_button_callback(self):
		self.__download_thread_list = list(
			filter(
				lambda x: x.is_alive(),
				self.__download_thread_list
			)
		)
		download_thread = threading.Thread(
			target=self.__download,
			args=(self.__book_info_collect_frame.book_info,)
		)
		self.__download_thread_list.append(download_thread)
		download_thread.start()
		return None
	
	def __book_info_callback(
		self, name: str, author: str, state: str, desc: str, chapter_number: int
	):
		for column_index in self.__progress_info_frame.info_table.get_children():
			column = self.__progress_info_frame.info_table.item(column_index)
			data = column["values"]
			if data[0] == name and data[1] == author:
				messagebox.showwarning(
					title="警告", 
					message=f"书籍({author} - {name})已在您的下载列表中，重复下载将会导致信息显示冲突。"
				)
				break
		else:
			self.__progress_info_frame.info_table.insert(
				"", tkinter.END, values=(
					name, author, state, str(chapter_number), "0",
					"(空)", "0 Bytes/s", str(time.time()), "0"
				)
			)

	
	def __chapter_info_callback(
		self, book_name: str, author: str, chapter_name: str,
		chapter_text: str, chapter_index: int
	):
		for column_index in self.__progress_info_frame.info_table.get_children():
			column = self.__progress_info_frame.info_table.item(column_index)
			data = column["values"]
			if data[0] == book_name and data[1] == author:
				download_time = time.time() - float(data[7])
				data_volume = int(data[8]) + len(chapter_text.encode("UTF-8"))
				self.__progress_info_frame.info_table.item(
					column_index,
					value=(
						data[0], data[1], data[2], data[3], str(chapter_index), chapter_name,
						str(int(data_volume / download_time)) + " Bytes/s", data[7], data_volume
					)
				)
				return None
