#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: main.py
# @Time: 23/02/2024 19:31
# @Author: Amundsen Severus Rubeus Bjaaland


import sys

import fire


class IngestionStage(object):
    def run(self):
        return 'Ingesting! Nom nom nom...'

class DigestionStage(object):
    def run(self, volume=1):
        return ' '.join(['Burp!'] * volume)

    def status(self):
        return 'Satiated.'

class Pipeline(object):
    def __init__(self):
        self.ingestion = IngestionStage()
        self.digestion = DigestionStage()

    def run(self):
        self.ingestion.run()
        self.digestion.run()
    
    def test_run(self):
        print("命令行可正常使用。")




if __name__ == "__main__":
    if len(sys.argv) == 1:
        # TODO 撰写可用的 GUI 界面
        print("该程序暂时不支持默认运行(GUI 界面)哦!")
    else:
        fire.Fire(Pipeline)