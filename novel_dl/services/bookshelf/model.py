#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: model.py
# @Time: 12/03/2025 15:37
# @Author: Amundsen Severus Rubeus Bjaaland
"""
模块名称: novel_dl.services.bookshelf.model
模块功能: 定义与书架相关的数据库模型，包括书籍、章节、附件和封面等。
类:
    - Attechments:
        描述章节中的附件信息，例如图片、音频、视频等。
        属性:
            - things_hash: 附件的唯一哈希值 (主键)。
            - chapter_hash: 所属章节的哈希值 (外键)。
            - index: 附件在章节中的索引。
            - content: 附件的内容。
            - content_type: 附件的类型 (如图片、音频、视频等)。
            - attrs: 附件的其他属性 (JSON 格式)。
        方法:
            - from_chapter: 从章节对象生成附件列表。
            - to_line: 将附件转换为章节内容行对象。
    - Chapters:
        描述书籍中的章节信息。
        属性:
            - things_hash: 章节的唯一哈希值 (主键)。
            - book_hash: 所属书籍的哈希值 (外键)。
            - index: 章节的索引。
            - name: 章节名称。
            - sources: 章节来源信息 (JSON 格式)。
            - update_time: 章节的更新时间 (时间戳)。
            - book_name: 所属书籍的名称。
            - content: 章节的内容 (HTML 格式)。
            - cache_method: 缓存方式。
            - attrs: 章节的其他属性 (JSON 格式)。
        方法:
            - encode_content: 将章节内容编码为 HTML 格式。
            - from_chapter: 从章节对象生成数据库章节对象。
            - to_chapter: 将数据库章节对象转换为章节对象。
    - BookCovers:
        描述书籍的封面信息。
        属性:
            - things_hash: 封面的唯一哈希值 (主键)。
            - book_hash: 所属书籍的哈希值 (外键)。
            - cover_image: 封面图片的内容。
        方法:
            - from_book: 从书籍对象生成封面列表。
            - to_cover: 将封面对象转换为图片内容。
    - Books:
        描述书籍的基本信息。
        属性:
            - things_hash: 书籍的唯一哈希值 (主键)。
            - name: 书籍名称。
            - author: 作者名称。
            - state: 书籍状态 (如连载中、已完结等)。
            - desc: 书籍简介。
            - sources: 书籍来源信息 (JSON 格式)。
            - tags: 书籍的标签列表。
            - attrs: 书籍的其他属性 (JSON 格式)。
        方法:
            - from_book: 从书籍对象生成数据库书籍对象。
            - to_book: 将数据库书籍对象转换为书籍对象。
注意:
    - 本模块依赖 SQLAlchemy 进行 ORM 映射。
    - 使用了自定义的枚举类 (ContentType, CacheMethod, State, Tag) 和工具函数 (如 _hash)。
    - 数据库字段类型包括 BLOB、JSON、String 等，适用于存储多种类型的数据。
"""



# 导入标准库
import json
import base64
from typing import List

# 导入第三方库
from bs4 import BeautifulSoup as bs
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, CheckConstraint
from sqlalchemy import Integer, String, BLOB, SmallInteger, JSON

# 导入自定义库
from novel_dl.utils.options import hash as _hash
from novel_dl.core.books import Line, Chapter, Book
from novel_dl.core.books import ContentType, CacheMethod, State, Tag


# 创建数据库映射基类
Base = declarative_base()


class Attechments(Base):
    __tablename__ = "attechments"
    
    things_hash = Column(BLOB, primary_key=True)
    chapter_hash = Column(
        BLOB, ForeignKey("chapters.things_hash"), nullable=False
    )
    index = Column(Integer, nullable=False)
    content = Column(BLOB, nullable=False)
    content_type = Column(SmallInteger, nullable=False)
    attrs = Column(JSON, nullable=False)
    
    __table_args__ = (
        CheckConstraint(
            content_type.in_([int(i) for i in list(ContentType)]),
            name="content_type_check"
        ),
    )
    
    def __repr__(self):
        return f"<Attechments index={self.index} " \
            f"content_type={self.content_type}>"
    
    @classmethod
    def from_chapter(cls, chapter: Chapter) -> List["Attechments"]:
        buffer = []
        for i in chapter.content:
            if i.content_type in [
                ContentType.Image, ContentType.Audio,
                ContentType.Video
            ]:
                buffer.append(
                    cls(
                        things_hash=i.hash,
                        chapter_hash=chapter.hash,
                        index=i.index, content=i,
                        content_type=int(i.content_type),
                        attrs=i.attrs
                    )
                )
        return buffer
    
    def to_line(self) -> Line:
        return Line(
            self.index, self.content,
            ContentType.to_obj(self.content_type),
            *self.attrs
        )


class Chapters(Base):
    __tablename__ = "chapters"

    things_hash = Column(BLOB, primary_key=True)
    book_hash = Column(
        BLOB, ForeignKey("books.things_hash"), nullable=False
    )
    index = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    sources = Column(JSON, nullable=False)
    update_time = Column(Integer, nullable=False)
    book_name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    cache_method = Column(SmallInteger, nullable=False)
    attrs = Column(JSON, nullable=False)
    
    attechments = relationship(
        "Attechments", cascade="all", backref="chapter"
    )
    
    __table_args__ = (
        CheckConstraint(
            cache_method.in_([int(i) for i in list(CacheMethod)]),
            name="cache_method_check"
        ),
    )

    def __repr__(self):
        return f"<Chapters index={self.index} " \
            f"name={self.name} book_name={self.book_name}>"
    
    @staticmethod
    def encode_content(chapter: Chapter) -> str:
        content = ""
        for i in chapter.content:
            attrs = base64.b64encode(
                json.dumps(i.attrs).encode()
            ).decode()
            match i.content_type:
                case ContentType.Text:
                    content += f"<p attrs='{attrs}'>{i.content}</p>"
                case ContentType.Image:
                    content += \
                        f"<image attrs='{attrs}'>" \
                        f"{base64.b64encode(i.hash).decode()}" \
                        "</image>"
                case ContentType.Audio:
                    content += \
                        f"<audio attrs='{attrs}'>" \
                        f"{base64.b64encode(i.hash).decode()}" \
                        "</audio>"
                case ContentType.Video:
                    content += \
                        f"<video attrs='{attrs}'>" \
                        f"{base64.b64encode(i.hash).decode()}" \
                        "</video>"
                case ContentType.CSS:
                    content += \
                        f"<link attrs='{attrs}'>{i.content}</link>"
                case ContentType.JS:
                    content += \
                        f"<script attrs='{attrs}'>{i.content}</script>"
        return content
    
    @classmethod
    def from_chapter(cls, chapter: Chapter, book_hash: bytes):
        return cls(
            things_hash=chapter.hash, book_hash=book_hash,
            index=chapter.index, name=chapter.name,
            sources=list(chapter.sources),
            update_time=chapter.update_time,
            book_name=chapter.book_name,
            content=Chapters.encode_content(chapter),
            cache_method=int(chapter.cache_method),
            attrs=chapter.other_info
        )
    
    def to_chapter(self) -> Chapter:
        content = []
        contents = bs(self.content, "lxml")
        contents = contents.find("body")
        for index, item in enumerate(contents.children):
            attrs = json.loads(
                base64.b64decode(item.get("attrs").encode()).decode()
            )
            match item.name:
                case "p":
                    content.append(Line(
                        index+1, item.text,
                        ContentType.Text, *attrs
                    ))
                case "link":
                    content.append(Line(
                        index+1, item.text,
                        ContentType.CSS, *attrs
                    ))
                case "script":
                    content.append(Line(
                        index+1, item.text,
                        ContentType.JS, *attrs
                    ))
                case _:
                    hash_value = base64.b64decode(item.text.encode())
                    for i in self.attechments:
                        if i.things_hash == hash_value:
                            content.append(i.to_line())
        return Chapter(
            self.index, self.name, self.sources,
            float(self.update_time), self.book_name, content,
            CacheMethod.to_obj(self.cache_method), *self.attrs
        )


class BookCovers(Base):
    __tablename__ = "book_covers"

    things_hash = Column(BLOB, primary_key=True)
    book_hash = Column(
        BLOB, ForeignKey("books.things_hash"), nullable=False
    )
    cover_image = Column(BLOB, nullable=False)
    
    @classmethod
    def from_book(cls, book: Book) -> List["BookCovers"]:
        buffer = []
        for i in book.cover_images:
            buffer.append(
                cls(
                    things_hash=_hash(i),
                    book_hash=book.hash,
                    cover_image=i
                )
            )
        return buffer
    
    def to_cover(self) -> bytes:
        return self.cover_image


class Books(Base):
    __tablename__ = "books"

    things_hash = Column(BLOB, primary_key=True)
    name = Column(String, nullable=False)
    author = Column(String, nullable=False)
    state = Column(SmallInteger, nullable=False)
    desc = Column(String, nullable=False)
    sources = Column(JSON, nullable=False)
    tags = Column(JSON, nullable=False)
    attrs = Column(JSON, nullable=False)
    
    chapters = relationship("Chapters", cascade="all", backref="book")
    cover_images = relationship(
        "BookCovers", cascade="all", backref="book"
    )

    def __repr__(self):
        return f"<Books name={self.name} author={self.author}>"
    
    @classmethod
    def from_book(cls, book: Book):
        cover_images = []
        for i in book.cover_images:
            cover_images.append(base64.b64encode(i).decode())
        return cls(
            things_hash=book.hash, name=book.name,
            author=book.author, state=int(book.state),
            desc=book.desc, sources=list(book.sources),
            tags=[int(i) for i in list(book.tags)],
            attrs=book.other_info
        )
    
    def to_book(self) -> Book:
        return Book(
            self.name, self.author, State.to_obj(self.state), self.desc,
            self.sources, self.cover_images,
            [Tag.to_obj(i) for i in self.tags], *self.attrs
        )