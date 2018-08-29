#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
if sys.version_info[0] < 3:
    from BaseHTTPServer import BaseHTTPRequestHandler
    from urlparse import urlparse
else:
    from http.server import BaseHTTPRequestHandler
    from urllib.parse import urlparse

import json
import time
from _core import request_types
from _core.router import Router
from _core.processor import Processor
from _core.log import Log

class Http_Handler(BaseHTTPRequestHandler):

    def __init__(self, *args):
        self.router     = Router()
        self.processor  = Processor()
        self.duration   = 0
        BaseHTTPRequestHandler.__init__(self, *args)

    def log_message(self, format, *args):
        client_addr = self.headers.get('X-Forwarded-For')
        if client_addr == None:
            client_addr = self.client_address[0]
        code = args[1]
        request_info = args[0].split()
        request_type = request_info[0]
        request_path  = request_info[1]
        Log.l("[REQUEST][%s][%s][%s][%s][%s][%.2f ms]" % (time.asctime(), client_addr, code, request_type, request_path, self.duration))

    def do_GET(self):
        self.process(request_types.GET)

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

        post_data = None
        form      = None

        if ctype == 'text/plain':
            post_data = self.rfile.read(int(self.headers.getheader('Content-Length')))
        elif ctype == 'application/json':
            post_data = json.loads(self.rfile.read(int(self.headers.getheader('Content-Length'))))
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            post_data = cgi.parse_qs(self.rfile.read(length), keep_blank_values = 1)
        elif ctype == 'multipart/form-data':
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={ 'REQUEST_METHOD':'POST',
                          'CONTENT_TYPE':self.headers['Content-Type']
                }
            )

        self.process(request_types.POST)

    def do_PUT(self):
        self.process(request_types.PUT)

    def do_DELETE(self):
        self.process(request_types.DELETE)

    def process(self, request_type):
        begin_time = time.time()
        # process url
        parsed_url      = urlparse(self.path)
        resource_path   = parsed_url.path
        url_query       = parsed_url.query

        # get worker
        worker = self.router.get_worker(resource_path)
        if worker == None:
            self.do_HEAD(404, 'application/json')
            self.wfile.write('{"status":404,"message":"NOT_FOUND"}')
        else:
            # Start worker
            worker.set_input_data(self.get_input_data(request_type))
            response = self.processor.process(request_type, worker)
            self.duration = (time.time() - begin_time) * 1000
            self.do_HEAD(response['code'], response['content_type'])
            self.wfile.write(str.encode(response['message']))
        if sys.version_info[0] < 3:
            self.wfile.close()

    def do_HEAD(self, errorCode, content_type):
        self.send_response(errorCode)
        self.send_header('Content-type', content_type)
        self.end_headers()


    def get_input_data(self, request_type):
        return None
