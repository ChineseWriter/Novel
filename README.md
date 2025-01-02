# 小说下载器
这是一个用 [Python](https://baike.baidu.com/item/Python/407313) 实现的用于下载小说的程序.

## 开始使用
注: 前两个步骤("解释器安装", "第三方库安装")在之后的更新中可能会写一个安装程序, 目前暂时需要手动安装.

### Python 解释器安装
首先, 请确保你的系统中已经安装了 Python 解释器, 并确保这个解释器的版本至少高于 3.10, 没有安装则请访问 [Python 官网](https://www.python.org/downloads/).

### 第三方库安装
<!-- TAG 每次更新时应当确认使用的第三方库是否有变化 -->
其次, 请确认你已经按照文件夹中的 requirements.txt 文件的内容正确地安装了程序所需要的第三方库, 若没有安装完成, 请依照文件进行安装, 或自行手动安装.

所需要的第三方库列表如下(更新可能滞后于项目):
| 计数 | 名称 | 用途 |
| :-: | :-: | :-: |
| 1 | yaml(安装时名称为 pyyaml) | 将书籍对象的其它数据转换为 EPUB 存储时所需要的格式 |
| 2 | ebooklib | 将书籍对象保存为 EPUB 格式 |
| 3 | PIL(安装时名称为 pillow) | 将书籍对象的封面转换为统一的 JPEG 格式, 便于书籍存储 |
| 4 | jieba | 将书籍名分词, 以便于制作倒排索引 |
| 5 | requests | 发起 HTTP 请求 |
| 6 | fake_useragent | 用于在获取 HTTP 时使用不同的 User-Agent 请求头, 以绕过部分网站的反爬机制 |
| 7 | bs4 | 用于 HTML 文档的解析 |
| 8 | tqdm | 用于默认回调函数, 指示一些进度的执行情况 |
| 9 | fire | 用于获取命令行数据 |
| 10 | pytest | 用于程序开发测试, 若不使用可不安装 |

### 在命令行中使用
<!-- TAG 每次更新时应当确认支持的命令和参数是否有变化 -->
目前该程序仅支持通过[命令提示符](https://baike.baidu.com/item/%E5%91%BD%E4%BB%A4%E6%8F%90%E7%A4%BA%E7%AC%A6/998728)输入命令使用, 以后可能会支持通过在命令提示符中的 TUI 使用, 以及通过 GUI 使用.

目前该程序支持的操作都在 downloader.py 文件中, 要使用该程序请输入`python downloader.py`, 在这之后跟进输入命令即可.

这是一个示例性命令: `python downloader.py download_novels --multi_thread=false`

以下是支持的命令列表:
| 计数 | 名称 | 参数(非全局) | 用途 |
| :-: | :-: | :-: | :-: |
| 1 | test_cmd | 无 | 测试命令行是否可以使用 |
| 2 | run_test | 无 | 运行程序测试, 用于开发时测试找 BUG |
| 3 | download_novel | url: str | 下载指定 URL 下的书籍 |
| 4 | download_novels | 无 | 从 book_urls.txt 文件中读取所有 URL 并下载它们下的书籍, 若文件不存在则自动创建并退出 |
| 5 | search_books_by_name | name: str | 从本地书架中寻找书籍, 该命令处于测试阶段 |

以下是可以指定的全局设置参数:
| 计数 | 参数名 | 用途 | 默认值 |
| :-: | :-: | :-: | :-: |
| 1 | debug | 程序是否在测试模式下运行, 主要改变程序日志的输出情况 | False |
| 2 | data_dir | 程序运行数据保存的文件夹位置 | (该项目根目录) |
| 3 | multi_thread | 下载书籍章节时是否采用多线程, 若某引擎不支持, 则该参数在该引擎上无效 | True |
| 4 | force_reload | 是否要强制从网站上获取内容, 这会覆盖掉本地的缓存 | False |
| 5 | log_file_name | 日志文件的文件名 | "logs" |
| 6 | log_format | 日志的格式 | "[%(asctime)s]{%(levelname)s} %(name)s (%(filename)s - %(lineno)s):\n\t%(message)s" |

## 支持的网站列表
目前小说下载器可以从以下网站下载小说:
| 计数 | 网站名 | 网站网址 |
| :-: | :-: | :-: |
| 1 | 笔趣阁 | www.biquge.hk, www.biequgei.com |
| 2 | 番茄小说 | www.fanqienovel.com |

## 项目相关信息
项目的概述请移步[概述](/info/summary.md).  
所有项目相关的进度请移步[计划](/info/plans.md).  
构建项目时使用到的知识请移步[学习笔记目录](/info/learn/contents.md).  
构建项目时遇到的问题请移步[问题目录](/info/problems/contents.md).  

## 重用内部 novel_dl 包
该部分文档暂时未编写.