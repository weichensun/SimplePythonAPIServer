#!/usr/bin/python
# -*- coding: utf-8 -*-

from _core.base_worker import BaseWorker

class Image(BaseWorker):

    def do_GET(self):
        path = 'image/lenna.png'
        return self.replyFile(path)
