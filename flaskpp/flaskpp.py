# -*- coding: utf-8 -*-

import sys, os
import time
import datetime
import logging, random
import redis
from flask import Flask, jsonify, request, g, Response, make_response

from logging.handlers import RotatingFileHandler

from flaskpp.db import DBUtils, init_db, init_redis, get_db, get_redis
from flaskpp.error import *
from flaskpp.config import init_cfg, get_cfg
from flaskpp.log_agent import LogAgent

API_SUCCESS = {'code': 0 , 'msg': 'success'}

class MyResponse(Response):
    charset = 'utf-8'
    default_mimetype = 'application/json'

    @classmethod
    def force_type(cls, rv, environ=None):
        if isinstance(rv, dict):
            if 'code' in rv and 'msg' in rv:
                g.err_code = rv.get('code')
                g.err_msg = rv.get('msg')
                rv = jsonify(rv)
            else:
                g.err_code = ERR_SUCCESS
                g.err_msg = 'success'
                rv = jsonify({'code': g.err_code, 'msg': g.err_msg, 'data': rv})
        elif isinstance(rv, list):
            g.err_code = ERR_SUCCESS
            g.err_msg = 'success'
            rv = jsonify({'code': g.err_code, 'msg': g.err_msg, 'data': rv})

        elif isinstance(rv, Response):
            return rv

        else:
            g.err_code = ERR_INNER_SVR
            g.err_msg = '内部错误:%s' % str(rv)
            rv = jsonify({'code': g.err_code, 'msg': g.err_msg, 'data': {}})

        resp = make_response(rv)
        #resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        return super(MyResponse, cls).force_type(resp, environ)

class FlaskPlus(Flask):
    def __init__(self, name):
        Flask.__init__(self, name)
        self.response_class = MyResponse

        self._register_error_handler(None, APIError, self.base_error_handler)
        self.before_request_funcs.setdefault(None, []).append(self.before_handler)
        self.teardown_request_funcs.setdefault(None, []).append(self.teardown_handler)

        # 注意这里的初始化顺序!
        self._init_config()
        self._init_log()
        self._init_redis()
        self._init_db()
        self._init_log_agent()

        self.logger.info('APP开始服务请求')

    def _init_log(self):
        log_level_map = {'debug': logging.DEBUG, 'info': logging.INFO, 'warn': logging.WARN,
                         'error': logging.ERROR, 'fatal': logging.FATAL}

        log_path = self.cfg.get_str('log', 'path')
        log_level = self.cfg.get_str('log', 'level')

        file_handler = RotatingFileHandler('%s/%s.log' % (log_path, self.name), maxBytes=1024*1024*100, backupCount=20)
        formatter = logging.Formatter("%(asctime)s %(name)s [%(levelname)s] %(message)s")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.logger.setLevel(log_level_map.get(log_level.lower(), logging.INFO))
        self.logger.info('初始化日志成功')

    def base_error_handler(self, e):
        return e.to_dict()

    def _init_config(self):
        self.cfg = init_cfg('./conf/config.ini')
        assert self.cfg is not None
        self.logger.info('初始化配置文件成功')

    def _init_redis(self):
        try:
            red_ip = self.cfg.get_str('redis', 'ip')
            red_port = self.cfg.get_int('redis', 'port')
            self.redis = init_redis(red_ip, red_port)
            #self.redis = redis.Redis(host=red_ip, port=red_port)
        except Exception as e:
            self.logger.error('初始化redis失败，程序直接退出。')
            sys.exit(-1)

        self.logger.info('初始化redis成功')

    def _init_db(self):
        try:
            db_host = self.cfg.get_str('mysql', 'ip')
            db_port = self.cfg.get_int('mysql', 'port')
            db_usr = self.cfg.get_str('mysql', 'user')
            db_pwd = self.cfg.get_str('mysql', 'passwd')
            db_name = self.cfg.get_str('mysql', 'dbname')
            #g_db = DBUtils(db_host, db_port, db_usr, db_pwd, db_name)
            self.db = init_db(db_host, db_port, db_usr, db_pwd, db_name)
        except Exception as e:
            self.logger.error('初始化mysql失败，程序直接退出。exception: [%s]' % str(e))
            sys.exit(-1)

        assert self.db is not None
        self.logger.info('初始化mysql成功')

    def _init_log_agent(self):
        try:
            svr_ip = self.cfg.get_str('action_log', 'ip')
            svr_port = self.cfg.get_int('action_log', 'port')
            db_name = self.cfg.get_str('action_log', 'dbname')
            self.agent = LogAgent(svr_ip, svr_port, db_name)
        except Exception as e:
            self.logger.error('初始化Action Log失败，程序直接退出')
            sys.exit(-1)

        assert self.agent is not None
        self.logger.info('初始化LogAgent成功')

    def before_handler(self):
        """解密、认证、过载保护、防刷
        """
        g.ts = datetime.datetime.now()
        g.userid = 0

        return

        is_check = self.cfg.get_int('session', 'check')
        if not is_check:
            self.logger.info('不检查token')
            return

        no_check_urls = ['login', 'register', 'upload_editor_img']
        for url in no_check_urls:
            if url in request.url:
                return

        return self.validate_session()

    def validate_session(self):
        g.userid = get_qs_int('userid')
        token = get_qs_str('token')
        try:
            ret = self.redis.get('tokens::%d' % g.userid)
        except Exception as e:
            return make_err(-1, '从redis获取token失败')

        if ret is None:
            return make_err(-1, '无此用户')

        ret = ret.decode()
        if ret != token:
            return make_err(-1, 'token验证失败')
        return

    def teardown_handler(self, response):
        """ 统计、加密、日志
        """
        cost = (datetime.datetime.now() - g.ts).microseconds / 1000

        items = request.url.split('?')
        if len(items) == 2:
            qs = items[1]
        else:
            qs = ''

        access_data = {
            'userid': getattr(g, 'userid', 0),
            'access_time': datetime.datetime.strftime(g.ts, "%Y-%m-%d %H:%M:%S") if g.ts else '',
            'url': request.path,
            'qs': qs,
            'cost': cost,
            'http_code': self.response_class.default_status,
            'err_code': getattr(g, 'err_code', 0),
            'err_msg': getattr(g, 'err_msg', ''),
            'create_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))
        }
        self.agent.access_log(access_data)
        return response


def make_err(code, msg):
    return {'code': code, 'msg': msg}


def get_qs_int(key, min_val=None, max_val=None):
    val = request.args.get(key)
    if val is None:
        raise APIError(ERR_REQ_ARGUMENT, '请传入参数:%s' % key)

    try:
        res = int(val)
    except ValueError:
        raise APIError(ERR_REQ_ARGUMENT, '参数:%s不是整数' % key)
    if min_val is not None and res < min_val:
        raise APIError(ERR_REQ_ARGUMENT, '参数:%s值超出范围' % key)
    if max_val is not None and res > max_val:
        raise APIError(ERR_REQ_ARGUMENT, '参数:%s值超出范围' % key)

    return res

def get_qs_int_default(key, default_val=0):
    val = request.args.get(key)
    if val is None:
        return default_val
    try:
        res = int(val)
    except ValueError:
        raise APIError(ERR_REQ_ARGUMENT, '参数:%s不是整数' % key)
    return res

def get_qs_str(key):
    val = request.args.get(key)
    if val is None:
        raise APIError(ERR_REQ_ARGUMENT, '请传入参数:%s' % key)

    return val

def get_qs_str_default(key, default_val=''):
    val = request.args.get(key)
    if val is None:
        return default_val
    return val

def timestr(data):
    if data:
        return datetime.datetime.strftime(data, "%Y-%m-%d %H:%M:%S")
    else:
        return None


