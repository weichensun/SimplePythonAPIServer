#!/usr/bin/python
# -*- coding: utf-8 -*-

from _core.base_worker import Base_Worker

class Object(Base_Worker):

    def do_GET(self):
        return self.replyOK("The object id is %s." % self.route_parameter("id"))