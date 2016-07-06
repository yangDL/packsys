# -*- coding: utf-8 -*-

from flask import g

ERR_INNER_SVR           = -10000
ERR_DATABASE            = -20000
ERR_SUCCESS             = 0
ERR_REQ_ARGUMENT        = 10000


class APIError(Exception):
    """*Error类为API执行过程中抛出的异常，这种情况下不应该结束程序，应向Client返回具体的错误码
    """
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
        g.err_code = code
        g.err_msg = msg

    def to_dict(self):
        return {'code': self.code, 'msg': self.msg}


class DBError(APIError):
    def __init__(self, sql=''):
        APIError.__init__(self, ERR_DATABASE, 'SQL执行失败[%s]' % sql)


class ConfigException(Exception):
    """*Exception类为系统级异常，出现此类异常程序不应该继续执行
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
