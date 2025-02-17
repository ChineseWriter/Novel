#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: saver.py
# @Time: 15/02/2025 11:41
# @Author: Amundsen Severus Rubeus Bjaaland


import io
import os
import time
from enum import Enum

import yaml
from PIL import Image
from ebooklib import epub

from novel_dl.core.settings import Settings
from .line import ContentType
from .book import Book


INTRODUCE_CSS = """body {
    line-height: 1.6;
    margin: 20px;
}
.container {
    max-width: 800px;
    margin: auto;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}
h1 {
    color: #333;
    border-bottom: 2px solid #333;
    padding-bottom: 10px;
}
p {
    margin: 10px 0;
}
.info-title {
    font-weight: bold;
}
.cover {
    text-align: center;
    margin-bottom: 20px;
}
.cover img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
}
.tags {
    display: flex;
    flex-wrap: wrap;
    list-style-type: none;
    padding: 0;
}
.tags li {
    margin-right: 10px;
}
.sources {
    list-style-type: disc;
    padding-left: 20px;
}"""
CHAPTER_CSS = """body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 20px;
    background-color: #f4f4f4;
}
.container {
    max-width: 800px;
    margin: auto;
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}
h1 {
    color: #333;
    border-bottom: 2px solid #333;
    padding-bottom: 10px;
}
p {
    margin: 10px 0;
}
.info-title {
    font-weight: bold;
}
.hidden {
    display: none;
}"""


class SaveMethod(Enum):
    EPUB = (1, "EPUB")
    PDF = (2, "PDF")
    TXT = (3, "TXT")
    
    @classmethod
    def to_obj(cls, value: int | str) -> "SaveMethod":
        """将常量的ID或名称转换为常量对象
        
        :param value: 常量的ID或名称
        :type value: int | str
        :return: 常量对象
        
        Example:
            >>> State.to_obj(1)
            >>> State.to_obj("EPUB")
        """
        # 确保 value 是 int 或 str 类型
        assert isinstance(value, int) or isinstance(value, str)
        # 如果 value 是 int 类型
        if isinstance(value, int):
            # 遍历所有常量
            for i in list(cls):
                # 如果常量的 ID 等于 value
                if i.value[0] == value:
                    # 返回常量对象
                    return i
        # 如果 value 是 str 类型
        else:
            # 遍历所有常量
            for i in list(cls):
                # 如果常量的名称等于 value
                if i.value[1] == value:
                    # 返回常量对象
                    return i
        # 如果 value 的值不在常量中, 则返回 EPUB 类型
        return cls.EPUB
    
    def __int__(self):
        return self.value[0]
    
    def __str__(self):
        return self.value[1]


class Saver(object):
    def __init__(self, book: Book, save_method: SaveMethod):
        assert isinstance(book, Book)
        assert isinstance(save_method, SaveMethod)
        self.__book = book
        self.__save_method = save_method
    
    def save(self) -> int:
        match self.__save_method:
            case SaveMethod.EPUB:
                return self.__save_epub()
            case SaveMethod.PDF:
                return self.__save_pdf()
            case SaveMethod.TXT:
                return self.__save_txt()
    
    def __save_epub(self):
        book = epub.EpubBook()
        
        if self.__book.other_info.get("id"):
            book.set_identifier(self.__book.url)
        book.set_title(self.__book.title)
        book.add_author(self.__book.author)
        book.set_language("zh-CN")
        book.add_metadata("DC", "description", self.__book.desc)
        book.add_metadata(
            "DC", "contributor", "Amundsen Severus Rubeus Bjaaland"
        )
        book.add_metadata("DC", "date", self.__book.update_time)
        for i in self.__book.tags:
            book.add_metadata("DC", "type", str(i))
        for i in self.__book.sources:
            book.add_metadata("DC", "source", i)
        
        if self.__book.cover_images:
            image = io.BytesIO(self.__book.cover_images[0])
            new_image = io.BytesIO()
            img_obj = Image.open(image)
            img_obj.convert("RGB").save(new_image, format="jpeg")
            new_image.seek(0)
            book.set_cover("images/cover.jpg", new_image.read())
        
        if self.__book.other_info:
            yaml_item = epub.EpubItem(
                uid="other_info",
                file_name="other_info.yml",
                media_type="application/octet-stream",
                content=yaml.dump(self.__book.other_info).encode()
            )
            book.add_item(yaml_item)

        intro_css = epub.EpubItem(
            uid="introduce_css",
            file_name="styles/introduce.css",
            media_type="text/css",
            content=INTRODUCE_CSS.encode()
        )
        book.add_item(intro_css)
        
        intro_e = epub.EpubHtml(
            title=f"《{self.__book.name}》基本信息",
            file_name="intro.xhtml", lang="zh-CN"
        )
        intro_e.add_link(
            rel="stylesheet", type="text/css",
            href="styles/introduce.css"
        )
        intro_e.content = \
f"""
<div class="container">
    <div class="cover">
        <img src="images/cover.jpg" alt="封面图片">
    </div>
    <h1>{self.__book.name}</h1>
    <p>
        <span class="info-title">作者:&emsp;</span>
        {self.__book.author}
    </p>
    <p>
        <span class="info-title">描述:&emsp;</span>
        {self.__book.desc}
    </p>
    <p>
        <span class="info-title">更新时间:&emsp;</span>
        {time.strftime(Settings.TIME_FORMAT, self.__book.update_time)}
    </p>
    <p><span class="info-title">标签:&emsp;</span></p>
    <ul class="tags">
        {"".join(
            [f"<li>{i}</li>" for i in self.__book.tags]
        )}
    </ul>
    <p><span class="info-title">来源:</span></p>
    <ul class="sources">
        {"".join(
            [f"<li>{i}</li>" for i in self.__book.sources]
        )}
    </ul>
</div>"""
        
        for chapter in self.__book.chapters:
            chapter_item = epub.EpubHtml(
                title=f"第{chapter.index}章 {chapter.name}",
                file_name=f"{chapter.str_index}-{chapter.name}.xhtml",
                lang="zh-CN"
            )
            
            content_str = ""
            for i in chapter.content:
                html_str, html_item = i.to_html()
                content_str += html_str
                if html_item:
                    book.add_item(html_item)
            chapter_item.content = \
f"""
<div class="container">
    <h1>第{chapter.index}章&emsp;{chapter.name}</h1>
    <p>
        <span class="info-title">更新时间:&emsp;</span>
        {time.strftime(Settings.TIME_FORMAT, chapter.update_time)}
    </p>
    <div class="chapter-content">
        {content_str}
    </div>
    <div class="hidden">
        <h2>来源</h2>
        <ul class="sources">
            {"".join(
                [f"<li>{i}</li>" for i in chapter.sources]
            )}
        </ul>
        <div class="other-info">
            <h2>其它信息</h2>
            <dl>
                {"".join(
                    [f"<dt>{k}</dt><dd>{v}</dd>" for k, v in chapter.other_info.items()]
                )}
            </dl>
        </div>
    </div>
</div>"""
            book.add_item(chapter_item)
            book.spine.append(chapter_item)
        
        file_path = os.path.join(
            Settings.BOOKS_STORAGE_DIR,
            f"{self.__book.author}-{self.__book.title}.epub"
        )
        epub.write_epub(file_path, book, {})
        return os.stat(file_path).st_size
    
    def __save_pdf(self):
        # TODO 添加保存为 PDF 的功能
        return 0
    
    def __save_txt(self):
        book = f"《{self.__book.name}》\n作者: {self.__book.author}\n" \
            f"更新时间: {time.strftime(
                Settings.TIME_FORMAT, 
                self.__book.update_time
            )}\n" \
            f"标签: {" ".join([i for i in self.__book.tags])}" \
            f"简介: {self.__book.desc}\n" \
            f"来源: \n{
                "".join([f'{i}\n' for i in self.__book.sources])
            }\n\n" \
        
        for chapter in self.__book.chapters:
            book += f"第{chapter.index}章 {chapter.name}\n" \
                f"更新时间: {
                    time.strftime(
                        Settings.TIME_FORMAT,
                        chapter.update_time
                    )
                }\n"
            book += "".join(
                [f"\t{i}\n" for i in chapter.content]
            )
            book += "\n"
        
        file_path = os.path.join(
            Settings.BOOKS_STORAGE_DIR,
            f"{self.__book.author}-{self.__book.title}.txt"
        )
        with open(file_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(book)
        
        return os.stat(file_path).st_size
        
        