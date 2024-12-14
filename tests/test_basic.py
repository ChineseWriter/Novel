#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: basic.py
# @Time: 20/04/2024 18:09
# @Author: Amundsen Severus Rubeus Bjaaland


import novel_dl


class TestManager:
    def test_manager_duplicate(self):
        manager_1 = novel_dl.Manager()
        manager_2 = novel_dl.Manager()
        assert id(manager_1) == id(manager_2)
