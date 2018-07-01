#-*- coding: utf-8 -*-
"""
===============================================================================
 `SMR_kakao_server.py`
===============================================================================

"""

import base64
import datetime
import json
# logging
import logging
import os
import pickle
import re
import sys
import time
import urllib
import yaml
from collections import deque
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from operator import itemgetter

import jpype
import msgpack
# image 관련
import numpy as np
import pybase64
import requests
# added
import smr_kakao.smr_status as status
import torch
# tornado
import tornado
from PIL import Image, ImageDraw, ImageFont
from konlpy.tag import Komoran
from logger import SetupLogging, logged, logged_func
from pymongo import MongoClient
from smr_kakao.grapher import grapher
# core - qa
from smr_kakao.hnqa.model import DocReaderModel
from smr_kakao.hnqa.utils import str2bool
from tornado import web, escape, ioloop, httpclient, gen
from tornado.concurrent import run_on_executor

client = MongoClient('localhost', 27017) # smr_mongodb 3000
db = client.wiki
# TODO: 적절한 테이블을 선택해주세요!
g_wiki_dictionary = db.dictionary # 전체 본문이 있는 collections
# g_wiki_dictionary = db.dictionary_abs # 전체 요약문이 있는 collections

g_loaded_model = {}
g_komoran = Komoran()
g_thread_pool = ThreadPoolExecutor() # 스레드 개수 설정
g_Session = {} # 사용자 개수 설정

@logged
class KeyboardHandler(web.RequestHandler):
    """ 키보드 핸들러
    """
    global g_thread_pool
    _thread_pool = g_thread_pool
    @gen.coroutine
    def get(self):
        self.logger.info('================ START KeyboardHandler ===================' )
        self.logger.info('================ END KeyboardHandler =====================' )


class Application(web.Application):
    def __init__(self, **kwargs):
        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "tmp"),
            "static_url_prefix": "/tmp/",
        }

        handlers = [
            # /keyboard
            (r"/keyboard", KeyboardHandler), # 카톡 플러스 친구 개발시 반드시 구현해야하는 URL
            # (r"/api/qna", QnAHandler),
            # (r"/leds/([0-9]+)", AsyncLedHandler),
            # (r"/altimeters/([0-9]+)", AsyncAltimeterHandler),
        ]
        super(Application, self).__init__(handlers, **settings)

if __name__ == "__main__":
    with SetupLogging( ):
        if os.path.exists(_SERVER_CONF_PATH):
            with open(_SERVER_CONF_PATH, 'rt') as f:
                global g_server_config
                global _GOOGLE_API_KEY

                g_server_config = yaml.load(f.read())
                g_loaded_model = load_model()
                _GOOGLE_API_KEY = g_server_config['GOOGLE_API_KEY']

        application = Application()
        application.listen(g_server_config['SERVER_PORT'])
        print('server start [%s] !!!'%(g_server_config['SERVER_PORT']))
        tornado_ioloop = ioloop.IOLoop.instance()
        ioloop.PeriodicCallback(lambda: None, 500, tornado_ioloop).start()
        tornado_ioloop.start()

