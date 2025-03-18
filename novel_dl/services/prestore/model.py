#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: model.py
# @Time: 17/03/2025 16:52
# @Author: Amundsen Severus Rubeus Bjaaland


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, CheckConstraint
from sqlalchemy import BLOB, SmallInteger


Base = declarative_base()


class URL(Base):
    __tablename__ = 'url'
    
    thing_hash = Column(BLOB, primary_key=True)
    visited = Column(SmallInteger, nullable=False, default=0)
    is_404 = Column(SmallInteger, nullable=False, default=0)
    is_book = Column(SmallInteger, nullable=False, default=0)
    is_chapter = Column(SmallInteger, nullable=False, default=0)
    
    __table_args__ = (
        CheckConstraint(visited.in_([0, 1])),
        CheckConstraint(is_404.in_([0, 1])),
        CheckConstraint(is_book.in_([0, 1])),
        CheckConstraint(is_chapter.in_([0, 1])),
    )
    
    def __repr__(self):
        return f'<URL thing_hash={self.thing_hash} ' \
            f'visited={True if self.visited else False} ' \
            f'is_404={True if self.is_404 else False} ' \
            f'is_book={True if self.is_book else False} ' \
            f'is_chapter={True if self.is_chapter else False}>'