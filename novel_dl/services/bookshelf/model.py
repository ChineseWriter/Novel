#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: model.py
# @Time: 12/03/2025 15:37
# @Author: Amundsen Severus Rubeus Bjaaland


import base64
import json
from typing import List

from sqlalchemy import Column
from sqlalchemy import String, BLOB, SmallInteger, JSON
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from bs4 import BeautifulSoup as bs

from novel_dl.utils.options import hash as _hash

from novel_dl.core.books import ContentType, CacheMethod, State
from novel_dl.core.books import Line, Chapter, Book, Tag


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