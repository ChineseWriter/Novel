#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :gui.py
# @Time      :01/26/2023 18:25
# @Author    :Amundsen Severus Rubeus Bjaaland


import time
import tkinter
import tkinter.ttk
import threading
from tkinter import messagebox

from .object import Book
from .tools import StorageServer
from .config import WebMap
from .engines import ENGINE_LIST
from .cache import UrlGetter


class BookInfoCollectFrame(tkinter.Frame):
	def __init__(self, book_info_callback, master=None):
		super(BookInfoCollectFrame, self).__init__(master)
		self.__book_info_callback = book_info_callback
		self.__setup_ui()
		self.pack()
	
	def __setup_ui(self):
		self.__url_text = tkinter.StringVar()

		self.__url_marked_words = tkinter.Label(self, text="书籍网址：")
		self.__url_entry = tkinter.Entry(self, textvariable=self.__url_text)
		self.__download_button = tkinter.Button(self, text="下载", command=self.__book_info_callback)

		self.__url_marked_words.pack(side=tkinter.LEFT)
		self.__url_entry.pack(side=tkinter.LEFT)
		self.__download_button.pack(side=tkinter.LEFT)
	
	@property
	def book_info(self):
		book_url = self.__url_entry.get()
		self.__url_entry.delete(0, tkinter.END)
		return book_url


class ProgressInfoFrame(tkinter.Frame):
	def __init__(self, master=None):
		super(ProgressInfoFrame, self).__init__(master)
		self.__lock = threading.Lock()
		self.__setup_ui()
		self.pack()
	
	def __setup_ui(self):
		self.__info_table = tkinter.ttk.Treeview(
			self, show='headings', height=10
		)
		self.__cache_info = tkinter.Label(self, text="", width=143)

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
		self.__cache_info.pack()
	
	@property
	def info_table(self):
		return self.__info_table
	
	def set_cacheinfo(self, web_config, all_number, downloaded_number, book_number, downloaded_book_number):
		self.__lock.acquire()
		try:
			self.__cache_info["text"] = \
				f"{web_config.name}: 已找到{all_number}个网址，" \
				f"已下载{downloaded_number}个网址，找到书籍网址{book_number}个，" \
				f"已下载{downloaded_book_number}本书籍信息。"
		except Exception:
			pass
		self.__lock.release()


class BookSearchFrame(tkinter.Frame):
	def __init__(self, download_callback, url_getter: UrlGetter, master: "DownloadFrame" = None):
		super(BookSearchFrame, self).__init__(master)
		self.__data_buffer = []
		self.__url_getter = url_getter
		self.__download_callback = download_callback
		self.__setup_ui()
		self.pack()

		self.__update_thread = threading.Thread(target=self.__list_update)
		self.__update_thread.start()
	
	def __setup_ui(self):
		self.__book_name_text = tkinter.StringVar()

		self.__book_name_marked_words = tkinter.Label(self, text="书籍名：")
		self.__book_name_entry = tkinter.Entry(self, textvariable=self.__book_name_text)
		self.__download_button = tkinter.Button(self, text="查找", command=self.__list_update)
		self.__list_view = tkinter.Listbox(self, width=50)
		self.__desc_info = tkinter.Message(self, text="", width=400)

		self.__list_view.bind('<Double-Button-1>', self.__download_book)
		self.__list_view.bind('<ButtonRelease-1>', self.__info_viewer)
		
		self.__book_name_marked_words.grid(column=0, row=0)
		self.__book_name_entry.grid(column=1, row=0, columnspan=3)
		self.__download_button.grid(column=4, row=0)
		self.__list_view.grid(column=0, row=1, columnspan=5, padx=5, pady=5)
		self.__desc_info.grid(column=0, row=2, columnspan=5, padx=5, pady=5)
	
	def __list_update(self):
		self.__list_view.delete(0, tkinter.END)
		data = self.__book_name_entry.get()
		if not data:
			return None
		self.__data_buffer = self.__url_getter.search(data)
		for one_book in self.__data_buffer:
			one_book: Book
			self.__list_view.insert(tkinter.END, f"{one_book.author} - {one_book.book_name}")
		
	def __info_viewer(self, event):
		book: Book = self.__data_buffer[self.__list_view.curselection()[0]]
		self.__desc_info["text"] = f"名称：{book.book_name}\n作者：{book.author}\n简介：{book.desc}"
	
	def __download_book(self, event):
		data = self.__data_buffer[self.__list_view.curselection()[0]].source
		self.__download_callback(data)


class DownloadFrame(tkinter.Frame):
	def __init__(self, master=None):
		super(DownloadFrame, self).__init__(master)
		self.__master = master
		self.__download_thread_list = []
		self.__url_getter = None
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
		
		self.__file_options_menu = tkinter.Menu(self.__main_menu, tearoff=False)
		self.__file_options_menu.add_command(
			label="查找书籍", command=self.__book_search_callback, accelerator="Ctrl+F"
		)
		self.__master.bind("<Control-F>", self.__book_search_callback)
		
		self.__main_menu.add_cascade(label="文件", menu=self.__file_options_menu)
		self.__main_menu.add_cascade(label="下载选项", menu=self.__download_options_menu)
	
	def __setup_ui(self):
		self.__book_info_collect_frame = BookInfoCollectFrame(
			self.__download_button_callback, self
		)
		self.__progress_info_frame = ProgressInfoFrame(self)
	
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

	@property
	def url_getter(self):
		return self.__url_getter
	
	@url_getter.setter
	def url_getter(self, url_getter: UrlGetter):
		self.__url_getter = url_getter
		self.__url_getter.db_state_callback = self.__progress_info_frame.set_cacheinfo
	
	def __download(self, book_url: str):
		StorageServer(
			self.__map.download(book_url), 
			StorageServer.StorageMethod.get(
				self.__download_type_flag.get()
			)
		).save()
	
	def __start_download_thread(self, book_url: str):
		self.__download_thread_list = list(
			filter(
				lambda x: x.is_alive(),
				self.__download_thread_list
			)
		)
		download_thread = threading.Thread(
			target=self.__download,
			args=(book_url,)
		)
		self.__download_thread_list.append(download_thread)
		download_thread.start()
		return None
	
	def __download_button_callback(self):
		book_url = self.__book_info_collect_frame.book_info
		self.__start_download_thread(book_url)
	
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
	
	def __book_search_callback(self):
		root_window = tkinter.Tk()
		root_window.title("搜索书籍")
		app = BookSearchFrame(self.__start_download_thread, self.__url_getter, root_window)
		root_window.resizable(0, 0)
		root_window.mainloop()
		app.finish()

