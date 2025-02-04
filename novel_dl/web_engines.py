#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @FileName: web_engines.py
# @Time: 26/10/2024 16:30
# @Author: Amundsen Severus Rubeus Bjaaland


import json
import time
import random
import urllib
import socket
import urllib3
from typing import List
from threading import Lock

import requests

from .network import Network
from ._books import Book, Chapter
from .web_manager import BookWeb


class ProtectedError(Exception):
    pass


class Engine1(BookWeb):
    name = "笔趣阁"
    domains = ["www.biquge.hk"]
    book_url_pattern = r"^/book/\d+\.html$"
    chapter_url_pattern = r"^/book/\d+/\d+\.html$"
    encoding = "UTF-8"
    prestore_book_urls = False
    
    def get_book_info(self, response: Network) -> Book:
        name = response.h1
        author = response.bs.find("h2").find("a").text
        state_text = response.bs.find("h2").find_all("span")[2].text.split("：")[1]
        state = Book.State.END if state_text == "全本" else Book.State.SERIALIZING
        desc = response.bs.find("div", attrs={"class": "intro"}).find("p").text.strip("\r").strip(" ")
        image_url = response.bs.find("div", attrs={"class": "cover"}).find("img").get("src")
        image = Network.get(image_url).content
        return Book(name, author, response.response.url, state, desc, image)

    def get_chapter_url(self, response: Network) -> List[str]:
        chapter_response = Network.get(response.response.url.rstrip(".html") + "/", self.encoding)
        url_list = chapter_response.bs.find("ul").find_all("a")
        url_list = [i.get("href") for i in url_list]
        return [response.get_next_url(i) for i in url_list]

    def get_chapter(self, response: Network) -> Chapter:
        h1 = response.h1
        name = h1.split(" ")[1].split("（")[0]
        buffer = []
        prev_response = response
        while True:
            chapter_p = prev_response.bs.find("div", attrs={"id": "chaptercontent"}).find_all("p")
            for i in chapter_p:
                buffer.append(i.text.strip(" "))
            a_tag = prev_response.bs.find("div", attrs={"class": "read-page"}).find_all("a")[-1]
            if a_tag.text == "下一章":
                break
            prev_response = Network.get(prev_response.get_next_url(a_tag.get("href")), prev_response.encoding)
        return Chapter(name, 0, response.response.url, "", buffer)

    def is_protected(
        self, response: Network | None,
        network_error: Exception | None,
        analyze_error: Exception | None
    ) -> bool:
        return super().is_protected(response, network_error, analyze_error)

    def prevent_protected(self, *param):
        return super().prevent_protected(*param)


class Engine2(BookWeb):
    name = "笔趣阁"
    domains = ["www.biequgei.com"]
    book_url_pattern = r"^/novel/\d+\.html$"
    chapter_url_pattern = r"^/book/\d+/.*?\.html$"
    encoding = "UTF-8"
    prestore_book_urls = True
    
    def get_book_info(self, response: Network) -> Book:
        name = response.bs.find("div", attrs={"class": "top"}).find("h1").text
        united_info = response.bs.find("div", attrs={"class": "fix"}).find_all("p")
        author = united_info[0].text.split("：")[1]
        state_text = united_info[2].text.split("：")[1]
        state = Book.State.SERIALIZING if state_text == "连载中" else Book.State.END
        desc = response.bs \
            .find("div", attrs={"class": "info"}) \
            .find_all("div")[-1].text \
            .strip("\r\n ").replace("\u3000", "")
        image_url = response.bs.find("div", attrs={"class": "imgbox"}).find("img").get("src")
        image = Network.get(response.get_next_url(image_url)).content
        return Book(name, author, response.response.url, state, desc, image)

    def get_chapter_url(self, response: Network) -> List[str]:
        url_list = response.bs.find_all("div", attrs={"class": "section-box"})[-1].find_all("a")
        url_list = [i.get("href") for i in url_list]
        return [response.get_next_url(i) for i in url_list]

    def get_chapter(self, response: Network) -> Chapter:
        flag = response.bs.find("div", attrs={"class": "text-head"})
        if flag is None:
            article = response.bs.find("article")
            name = article.find("h3").text.split(" ")[-1]
            text = article.find_all("p")
        else:
            name = flag.find("h3").text.split(" ")[-1]
            text = response.bs.find("div", attrs={"class": "read-content j_readContent"}).find_all("p")
        text = [i.text.strip("\r\n ").replace("\u3000", "") for i in text]
        if text[0] == '章节内容转码失败！':
            raise ProtectedError("存在反爬机制!")
        return Chapter(name, 0, response.response.url, "", text)

    def is_protected(
        self, response: Network | None,
        network_error: Exception | None,
        analyze_error: Exception | None
    ) -> bool:
        if isinstance(analyze_error, ProtectedError):
            return True
        if isinstance(network_error, requests.exceptions.ConnectionError):
            return True
        if isinstance(network_error, requests.exceptions.ReadTimeout):
            return True
        if isinstance(network_error, requests.exceptions.SSLError):
            return True
        return super().is_protected(response, network_error, analyze_error)

    def prevent_protected(self, *param):
        time.sleep(5.0)


class Engine3(BookWeb):
    name = "番茄小说"
    domains = ["www.fanqienovel.com", "fanqienovel.com"]
    book_url_pattern = r"^/page/\d+$"
    chapter_url_pattern = r"^/reader/\d+$"
    encoding = "UTF-8"
    prestore_book_urls = False
    multi_thread = False
    
    class ChapterListProtectedError(Exception):
        pass
    
    CODE = [[58344, 58715], [58345, 58716]]
    CHARSET = [
        [
            "D","在","主","特","家","军","然","表","场","4","要","只","v",
            "和","?","6","别","还","g","现","儿","岁","?","?","此","象","月",
            "3","出","战","工","相","o","男","直","失","世","F","都","平",
            "文","什","V","O","将","真","T","那","当","?","会","立","些","u",
            "是","十","张","学","气","大","爱","两","命","全","后","东","性",
            "通","被","1","它","乐","接","而","感","车","山","公","了","常",
            "以","何","可","话","先","p","i","叫","轻","M","士","w","着","变",
            "尔","快","l","个","说","少","色","里","安","花","远","7","难",
            "师","放","t","报","认","面","道","S","?","克","地","度","I","好",
            "机","U","民","写","把","万","同","水","新","没","书","电","吃",
            "像","斯","5","为","y","白","几","日","教","看","但","第","加",
            "候","作","上","拉","住","有","法","r","事","应","位","利","你",
            "声","身","国","问","马","女","他","Y","比","父","x","A","H","N",
            "s","X","边","美","对","所","金","活","回","意","到","z","从","j",
            "知","又","内","因","点","Q","三","定","8","R","b","正","或","夫",
            "向","德","听","更","?","得","告","并","本","q","过","记","L","让",
            "打","f","人","就","者","去","原","满","体","做","经","K","走",
            "如","孩","c","G","给","使","物","?","最","笑","部","?","员","等",
            "受","k","行","一","条","果","动","光","门","头","见","往","自",
            "解","成","处","天","能","于","名","其","发","总","母","的","死",
            "手","入","路","进","心","来","h","时","力","多","开","已","许",
            "d","至","由","很","界","n","小","与","Z","想","代","么","分","生",
            "口","再","妈","望","次","西","风","种","带","J","?","实","情",
            "才","这","?","E","我","神","格","长","觉","间","年","眼","无","不",
            "亲","关","结","0","友","信","下","却","重","己","老","2","音","字",
            "m","呢","明","之","前","高","P","B","目","太","e","9","起","稜",
            "她","也","W","用","方","子","英","每","理","便","四","数","期",
            "中","C","外","样","a","海","们","任"
        ],
        [
            "s","?","作","口","在","他","能","并","B","士","4","U","克","才",
            "正","们","字","声","高","全","尔","活","者","动","其","主","报",
            "多","望","放","h","w","次","年","?","中","3","特","于","十","入",
            "要","男","同","G","面","分","方","K","什","再","教","本","己","结",
            "1","等","世","N","?","说","g","u","期","Z","外","美","M","行",
            "给","9","文","将","两","许","张","友","0","英","应","向","像","此",
            "白","安","少","何","打","气","常","定","间","花","见","孩","它",
            "直","风","数","使","道","第","水","已","女","山","解","d","P","的",
            "通","关","性","叫","儿","L","妈","问","回","神","来","S","","四",
            "望","前","国","些","O","v","l","A","心","平","自","无","军","光","代",
            "是","好","却","c","得","种","就","意","先","立","z","子","过","Y",
            "j","表","","么","所","接","了","名","金","受","J","满","眼","没","部",
            "那","m","每","车","度","可","R","斯","经","现","门","明","V","如","走",
            "命","y","6","E","战","很","上","f","月","西","7","长","夫","想","话",
            "变","海","机","x","到","W","一","成","生","信","笑","但","父","开",
            "内","东","马","日","小","而","后","带","以","三","几","为","认","X",
            "死","员","目","位","之","学","远","人","音","呢","我","q","乐","象",
            "重","对","个","被","别","F","也","书","稜","D","写","还","因","家",
            "发","时","i","或","住","德","当","o","l","比","觉","然","吃","去",
            "公","a","老","亲","情","体","太","b","万","C","电","理","?","失","力",
            "更","拉","物","着","原","她","工","实","色","感","记","看","出","相",
            "路","大","你","候","2","和","?","与","p","样","新","只","便","最","不",
            "进","T","r","做","格","母","总","爱","身","师","轻","知","往","加",
            "从","?","天","e","H","?","听","场","由","快","边","让","把","任","8",
            "条","头","事","至","起","点","真","手","这","难","都","界","用","法",
            "n","处","下","又","Q","告","地","5","k","t","岁","有","会","果","利","民"
        ]
    ]
    
    def __init__(self):
        self.__cookie = ""
        self.__lock = Lock()
    
    def __get_response(self, url: str, cookie: str):
        try:
            response = Network.get(
                url, cookie=cookie,
                User_Agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) " \
                    "Gecko/20100101 Firefox/133.0"
            )
            n = response.bs \
                .find("div", attrs={"class": "muye-reader-content noselect"}).text
        except Exception:
            return None
        else:
            if len(n) <= 200:
                return None
            return response
    
    def __get_chapter_response(self, url: str):
        if self.__cookie:
            result_1 = self.__get_response(url, self.__cookie)
            if result_1 is not None:
                return result_1
        
        bas = 1000000000000000000
        while_flag = True
        while while_flag:
            bas_1 = random.randint(bas * 6, bas * 8)
            for i in range(bas_1, bas_1 + 25):
                time.sleep(random.randint(50, 150) / 1000)
                cookie = 'novel_web_id=' + str(i)
                result_2 = self.__get_response(url, cookie)
                if result_2 is not None:
                    with self.__lock:
                        self.__cookie = cookie
                    return result_2
    
    def __decode_text(self, text: str):
        s = ""
        for i in range(len(text)):
            uni = ord(text[i])
            if self.CODE[0][0] <= uni <= self.CODE[0][1]:
                bias = uni - self.CODE[0][0]
                if bias < 0 or bias >= len(self.CHARSET[0]) or self.CHARSET[0][bias] == '?':
                    return chr(uni)
                s += self.CHARSET[0][bias]
            else:
                s += text[i]
        return s
    
    def get_book_info(self, response: Network) -> Book:
        name = response.h1
        author = response.bs.find("span", attrs={"class": "author-name-text"}).text
        state_text = response.bs.find("div", attrs={"class": "info-label"}) \
            .find_all("span")[0].text
        state = Book.State.SERIALIZING if state_text == "连载中" else Book.State.END
        desc = response.bs.find("div", attrs={"class": "page-abstract-content"}).text
        response.save_debug_file()
        image_url = response.bs.find_all("script", attrs={"type": "application/ld+json"})[1]
        image_url = json.loads(image_url.text)
        image_url = image_url.get("images")[0]
        image = Network.get(response.get_next_url(image_url)).content
        fq_id = response.response.url.split("/")[-1]
        return Book(name, author, response.response.url, state, desc, image, fq_id=fq_id)
    
    def get_chapter_url(self, response: Network) -> List[str]:
        response.save_debug_file()
        if response.bs.find("div", attrs={"class": "page-directory-more"}):
            raise self.ChapterListProtectedError
        volume_list = response.bs.find("div", attrs={"class": "page-directory-content"}) \
            .find_all("div", attrs={"class": "chapter"})
        url_list = []
        for one_volume in volume_list:
            a_list = one_volume.find_all("a")
            [url_list.append(i.get("href")) for i in a_list]
        return [response.get_next_url(i) for i in url_list]
    
    def get_chapter(self, response: Network) -> Chapter:
        chapter_response = self.__get_chapter_response(response.response.url)
        name = chapter_response.bs \
            .find("h1", attrs={"class": "muye-reader-title"}).text.split(" ")[-1]
        text_list = chapter_response.bs \
            .find("div", attrs={"class": "muye-reader-content noselect"}).find_all("p")
        text_list = [self.__decode_text(i.text) for i in text_list]
        text_list = filter(lambda x: True if x else False, text_list)
        return Chapter(name, 0, response.response.url, "", list(text_list))
    
    def is_protected(
        self, response: Network | None,
        network_error: Exception | None,
        analyze_error: Exception | None
    ) -> bool:
        # if isinstance(network_error, requests.exceptions.ConnectionError):
        #     return True
        # if isinstance(network_error, urllib3.exceptions.MaxRetryError):
        #     return True
        # if isinstance(network_error, urllib3.exceptions.NameResolutionError):
        #     return True
        # if isinstance(network_error, socket.gaierror):
        #     return True
        if isinstance(analyze_error, self.ChapterListProtectedError):
            return True
        return super().is_protected(response, network_error, analyze_error)
    
    def prevent_protected(self, *param):
        time.sleep(10.0)


ENGINE_LIST = (
    Engine1(),
    Engine2(),
    Engine3(),
)