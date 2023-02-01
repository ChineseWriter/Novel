#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :gui.py
# @Time      :01/26/2023 19:05
# @Author    :Amundsen Severus Rubeus Bjaaland


import tkinter
import tkinter.messagebox

from novel import VERSION, UrlGetter
from novel import DownloadFrame


if __name__ == "__main__":
	main_window = tkinter.Tk()
	main_window.title(f"书籍下载器  版本：{VERSION}")
	app = DownloadFrame(main_window)
	main_window.config(menu=app.main_menu)
	app.pack()
	url_getter = UrlGetter(app.web_map)
	app.url_getter = url_getter
	url_getter.start()
	
	
	def app_exit():
		"""检查退出的时候是否所有线程均退出"""
		for one_thread in app.thread_list:
			if one_thread.is_alive():
				tkinter.messagebox.showwarning(
					title="警告", message="有下载线程未执行完毕"
				)
				break
		else:
			main_window.destroy()
			url_getter.finish()
	
	
	main_window.protocol("WM_DELETE_WINDOW", app_exit)
	main_window.resizable(0, 0)
	main_window.mainloop()