#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: test_book.py
# @Time: 31/01/2025 18:25
# @Author: Amundsen Severus Rubeus Bjaaland


from novel_dl import ContentType, Line


class TestLine:
    def test_content_type(self):
        assert ContentType.to_obj(1) == ContentType.Text
        assert ContentType.to_obj("文本") == ContentType.Text
        assert int(ContentType.Text) == 1
        assert str(ContentType.Text) == "文本"
        assert ContentType.Text.is_bytes() == False
        assert ContentType.Text.html_tag() == "p"

        assert ContentType.to_obj(2) == ContentType.Image
        assert ContentType.to_obj("图片") == ContentType.Image
        assert int(ContentType.Image) == 2
        assert str(ContentType.Image) == "图片"
        assert ContentType.Image.is_bytes() == True
        assert ContentType.Image.html_tag() == "img"

        assert ContentType.to_obj(3) == ContentType.Audio
        assert ContentType.to_obj("音频") == ContentType.Audio
        assert int(ContentType.Audio) == 3
        assert str(ContentType.Audio) == "音频"
        assert ContentType.Audio.is_bytes() == True
        assert ContentType.Audio.html_tag() == "audio"

        assert ContentType.to_obj(4) == ContentType.Video
        assert ContentType.to_obj("视频") == ContentType.Video
        assert int(ContentType.Video) == 4
        assert str(ContentType.Video) == "视频"
        assert ContentType.Video.is_bytes() == True
        assert ContentType.Video.html_tag() == "video"

        assert ContentType.to_obj(5) == ContentType.CSS
        assert ContentType.to_obj("层叠式设计样表") == ContentType.CSS
        assert int(ContentType.CSS) == 5
        assert str(ContentType.CSS) == "层叠式设计样表"
        assert ContentType.CSS.is_bytes() == False
        assert ContentType.CSS.html_tag() == "link"

        assert ContentType.to_obj(6) == ContentType.JS
        assert ContentType.to_obj("JavaScript") == ContentType.JS
        assert int(ContentType.JS) == 6
        assert str(ContentType.JS) == "JavaScript"
        assert ContentType.JS.is_bytes() == False
        assert ContentType.JS.html_tag() == "script"
        
        assert ContentType.to_obj(7) == ContentType.Text
        assert ContentType.to_obj("未知") == ContentType.Text


    def test_line(self):
        line_1 = Line("Hello, World!", ContentType.Text)
        
        assert line_1.encode() == "SGVsbG8sIFdvcmxkIQ=="
        assert line_1.content == "Hello, World!"
        assert line_1.content_type == ContentType.Text
        assert line_1.attrs == {}
        
        assert line_1.to_dict() == {
            "content": "SGVsbG8sIFdvcmxkIQ==", "attrs": {},
            "content_type": int(ContentType.Text)
        }
        assert line_1 == Line.from_dict(
            {
                "content": "SGVsbG8sIFdvcmxkIQ==", "attrs": {},
                "content_type": int(ContentType.Text)
            }
        )
        
        assert Line.default() == Line("默认的 Line 对象.", ContentType.Text)
