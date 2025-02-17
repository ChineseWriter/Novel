#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: saver.py
# @Time: 15/02/2025 11:41
# @Author: Amundsen Severus Rubeus Bjaaland
"""保存书籍模块
该模块提供了将书籍对象保存为不同格式文件的功能，包括 EPUB、PDF 和 TXT 格式。
模块包含以下类和常量：
- SaveMethod: 保存书籍的方式枚举类
- Saver: 保存书籍的类
常量:
- INTRODUCE_CSS: 简介页面的 CSS 样式
- CHAPTER_CSS: 章节页面的 CSS 样式
类:
- SaveMethod: 保存书籍的方式枚举类
    - EPUB: 保存为 EPUB 格式
    - PDF: 保存为 PDF 格式
    - TXT: 保存为 TXT 格式
    - to_obj(value: int | str) -> "SaveMethod": 将常量的ID或名称转换为常量对象
    - __int__() -> int: 返回常量的 ID
    - __str__() -> str: 返回常量的名称
- Saver: 保存书籍的类
    - __init__(self, book: Book, save_method: SaveMethod): 初始化 Saver 对象
    - save(self) -> int: 保存书籍，返回保存文件的大小，单位是字节
    - __save_epub(self): 保存书籍为 EPUB 格式
    - __save_pdf(self): 保存书籍为 PDF 格式
    - __save_txt(self): 保存书籍为 TXT 格式
"""


# 导入标准库
import os
import time
from enum import Enum

# 导入第三方库
import yaml
from ebooklib import epub

# 导入自定义库
from .book import Book
from .line import ContentType
from novel_dl.core.settings import Settings
from novel_dl.utils.options import hash as _hash
from novel_dl.utils.options import mkdir, convert_image


# 简介页面的 CSS 样式
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
# 章节页面的 CSS 样式
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
    """保存书籍的方式枚举类
    
    常量中, 第一个参数是ID, 第二个参数是名称
    """
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
        """保存书籍的类
        
        :param book: 书籍对象
        :type book: Book
        :param save_method: 保存书籍的方式
        :type save_method: SaveMethod
        
        Example:
            >>> s = Saver(book, SaveMethod.EPUB)
            >>> s.save()
        """
        # 确认传入的参数的类型是否正确
        assert isinstance(book, Book)
        assert isinstance(save_method, SaveMethod)
        # 创建运行时必要的目录
        mkdir(Settings().DATA_DIR)
        mkdir(Settings().BOOKS_DIR)
        mkdir(Settings().BOOKS_STORAGE_DIR)
        # 初始化数据
        self.__book = book
        self.__save_method = save_method
    
    def save(self) -> int:
        """保存书籍
        
        :return: 保存文件的大小, 单位是字节
        :rtype: int
        """
        # 根据保存方式保存书籍
        match self.__save_method:
            case SaveMethod.EPUB:
                return self.__save_epub()
            case SaveMethod.PDF:
                return self.__save_pdf()
            case SaveMethod.TXT:
                return self.__save_txt()
    
    def __save_epub(self):
        # 创建 EpubBook 对象
        book = epub.EpubBook()
        
        # 设置书籍的基本信息
        book_id = self.__book.other_info.get("id")
        if book_id:
            book.set_identifier(book_id)
        book.set_title(self.__book.name)
        book.add_author(self.__book.author)
        book.set_language("zh-CN")
        
        # 添加元数据, 包括作者, 书籍简介, 贡献者, 更新时间, 标签和来源
        book.add_metadata("DC", "description", self.__book.desc)
        book.add_metadata(
            "DC", "contributor", "Amundsen Severus Rubeus Bjaaland"
        )
        book.add_metadata(
            "DC", "date",
            time.strftime(
                Settings().TIME_FORMAT,
                time.localtime(self.__book.update_time)
            )
        )
        for i in self.__book.tags:
            book.add_metadata("DC", "type", str(i))
        for i in self.__book.sources:
            book.add_metadata("DC", "source", i)
        
        # 如果有的话, 添加封面图片, 默认为第一张图片
        cover_images = list(self.__book.cover_images)
        if cover_images:
            book.set_cover(
                "images/cover.jpg",
                convert_image(cover_images[0])
            )
        
        # 添加其它信息, 以 YAML 格式保存
        if self.__book.other_info:
            yaml_item = epub.EpubItem(
                uid="other_info",
                file_name="others/other_info.yaml",
                media_type="application/octet-stream",
                content=yaml.dump(self.__book.other_info).encode()
            )
            book.add_item(yaml_item)

        # 添加章节和简介页面的 CSS 样式
        intro_css = epub.EpubItem(
            uid="introduce_css",
            file_name="styles/introduce.css",
            media_type="text/css",
            content=INTRODUCE_CSS.encode()
        )
        book.add_item(intro_css)
        chapter_css = epub.EpubItem(
            uid="chapter_css",
            file_name="styles/chapter.css",
            media_type="text/css",
            content=CHAPTER_CSS.encode()
        )
        book.add_item(chapter_css)
        
        # 添加简介页面
        intro_e = epub.EpubHtml(
            uid="introduce_html",
            title=f"《{self.__book.name}》基本信息",
            file_name="pages/intro.xhtml", lang="zh-CN"
        )
        intro_e.add_link(
            rel="stylesheet", type="text/css",
            href="../styles/introduce.css"
        )
        intro_e.content = \
f"""
<div class="container">
    <div class="cover" >
        <img src="../images/cover.jpg" alt="封面图片" style="width:100%;height:100%;object-fit:cover;">
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
        {time.strftime(
            Settings().TIME_FORMAT,
            time.localtime(self.__book.update_time)
        )}
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
        book.add_item(intro_e)
        
        # 初始化书籍的目录
        book.spine = [intro_e, "nav", intro_e]
        toc = []
        
        # 遍历所有章节, 添加到书籍中
        for chapter in self.__book.chapters:
            # 创建章节页面, 并添加章节的 CSS
            chapter_item = epub.EpubHtml(
                uid=f"chapter_{chapter.str_index}",
                title=f"第{chapter.index}章 {chapter.name}",
                file_name=\
                    f"pages/{chapter.str_index}-{chapter.name}.xhtml",
                lang="zh-CN"
            )
            chapter_item.add_link(
                rel="stylesheet", type="text/css",
                href="../styles/chapter.css"
            )
            
            # 遍历章节的内容, 创建内容部分的 HTML, 如果存在附件, 则添加到书籍中
            content_str = ""
            for i in chapter.content:
                match i.content_type:
                    case ContentType.Text:
                        content_str += \
                            f"<p>&emsp;&emsp;{i.content}</p>"
                    case ContentType.Image:
                        image_hash = _hash(i.content, "HEX")
                        image_path = f"images/{chapter.str_index}-" \
                            f"{chapter.name}/{image_hash}.jpg"
                        image_item = epub.EpubImage(
                            uid=image_hash,
                            file_name=image_path,
                            media_type="image/jpeg",
                            content=convert_image(i.content)
                        )
                        book.add_item(image_item)
                        alt = i.attrs.get("alt", "一张图片")
                        content_str += \
                            f'<img src="../{image_path}" alt="{alt}">'
                    case ContentType.Audio:
                        # TODO 添加音频的支持
                        pass
                    case ContentType.Video:
                        # TODO 添加视频的支持
                        pass
                    case ContentType.CSS:
                        css_hash = _hash(i.content, "HEX")
                        css_path = f"styles/{chapter.str_index}-" \
                            f"{chapter.name}/{css_hash}.css"
                        css_item = epub.EpubItem(
                            uid=css_hash,
                            file_name=css_path,
                            media_type="text/css",
                            content=i.content.encode()
                        )
                        book.add_item(css_item)
                        content_str += \
                            f'<link rel="stylesheet" ' \
                            f'type="text/css" href="../{css_path}">'
                    case ContentType.JS:
                        js_hash = _hash(i.content, "HEX")
                        js_path = f"scripts/{chapter.str_index}-" \
                            f"{chapter.name}/{js_hash}.js"
                        js_item = epub.EpubItem(
                            uid=js_hash,
                            file_name=js_path,
                            media_type="text/javascript",
                            content=i.content.encode()
                        )
                        book.add_item(js_item)
                        content_str += \
                            f'<script src="../{js_path}"></script>'
            # 添加章节的内容到章节页面
            chapter_item.content = \
f"""
<div class="container">
    <h1>第{chapter.index}章&emsp;{chapter.name}</h1>
    <p>
        <span class="info-title">更新时间:&emsp;</span>
        {time.strftime(
            Settings().TIME_FORMAT,
            time.localtime(chapter.update_time)
        )}
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

            # 添加章节页面到书籍中, 并添加到目录中
            book.add_item(chapter_item)
            toc.append(chapter_item)
            book.spine.append(chapter_item)
        
        # 添加目录到书籍中
        book.toc = toc
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # 保存书籍
        file_path = os.path.join(
            Settings().BOOKS_STORAGE_DIR,
            f"{self.__book.author}-{self.__book.name}.epub"
        )
        epub.write_epub(file_path, book, {})
        
        # 返回保存文件的大小
        return os.stat(file_path).st_size
    
    def __save_pdf(self):
        # TODO 添加保存为 PDF 的功能
        return 0
    
    def __save_txt(self):
        # 初始化书籍的开头
        book = f"《{self.__book.name}》\n作者: {self.__book.author}\n" \
            f"更新时间: {time.strftime(
                Settings().TIME_FORMAT, 
                time.localtime(self.__book.update_time)
            )}\n" \
            f"标签: {" ".join([str(i) for i in self.__book.tags])}\n" \
            f"简介: {self.__book.desc}\n" \
            f"来源: \n{
                "".join([f'{i}\n' for i in self.__book.sources])
            }\n\n" \
        
        # 遍历所有章节, 添加到书籍中
        for chapter in self.__book.chapters:
            # 添加章节的信息到书籍中
            book += f"第{chapter.index}章 {chapter.name}\n" \
                f"更新时间: {
                    time.strftime(
                        Settings().TIME_FORMAT,
                        time.localtime(chapter.update_time)
                    )
                }\n"
            # 添加章节的内容到书籍中
            book += "".join(
                [f"\t{i}\n" for i in chapter.content]
            )
            book += "\n"
        
        # 保存书籍
        file_path = os.path.join(
            Settings().BOOKS_STORAGE_DIR,
            f"{self.__book.author}-{self.__book.name}.txt"
        )
        with open(file_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(book)
        
        # 返回保存文件的大小
        return os.stat(file_path).st_size