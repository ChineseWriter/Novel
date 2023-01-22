#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :main.py
# @Time      :03/09/2022 11:41
# @Author    :Amundsen Severus Rubeus Bjaaland


import tkinter
import tkinter.messagebox

from novel import VERSION
from novel import DownloadFrame


if __name__ == "__main__":
	main_window = tkinter.Tk()
	main_window.title(f"书籍下载器  版本：{VERSION}")
	app = DownloadFrame(main_window)
	app.pack()
	
	
	def app_exit():
		"""检查退出的时候是否所有线程均退出"""
		for one_thread in app.thread_list:
			if one_thread.is_alive():
				tkinter.messagebox.showwarning(title='警告', message='有下载线程未执行完毕。')
				break
		else:
			main_window.destroy()
	
	
	main_window.protocol("WM_DELETE_WINDOW", app_exit)
	main_window.mainloop()
