# -*- coding: utf-8 -*-

import logging

import MySQLdb, redis

from flaskpp.error import DBError

g_db = None
g_redis = None

def init_db(db_host, db_port, db_usr, db_pwd, db_name):
    global g_db
    g_db = DBUtils(db_host, db_port, db_usr, db_pwd, db_name)
    return g_db

def get_db():
    return g_db

def init_redis(ip, port):
    global g_redis
    g_redis = redis.Redis(host=ip, port=port)
    return g_redis

def get_redis():
    return g_redis

class DBUtils:
    def __init__(self, db_host, db_port, db_usr, db_pwd, db_name):
        self.db_host = db_host
        self.db_port = db_port
        self.db_usr = db_usr
        self.db_pwd = db_pwd
        self.db_name = db_name

        self.connect()

    def connect(self):
        try:
            self.db = MySQLdb.connect(host=self.db_host, port=self.db_port, user=self.db_usr, passwd=self.db_pwd,
                                      db=self.db_name, charset='utf8', connect_timeout=3)
        except Exception as e:
            raise e
        assert self.db is not None

    def check_db(self):
        try:
            self.db.ping(True)
        except Exception as ex:
            self.connect()

    def query_single(self, sql, args=None):
        """ 执行SQL，返回一行记录，比如select
        """
        assert sql
        try:
            self.check_db()
            self.db.autocommit(True)
            cursor = self.db.cursor()
            cursor.execute(sql, args)
            row = cursor.fetchone()
        except Exception as e:
            raise DBError(sql)
        finally:
            cursor.close()

        return row

    def query_multi(self, sql, args=None):
        """ 执行SQL，返回多行记录，比如select
        """
        assert sql
        try:
            self.check_db()
            self.db.autocommit(True)
            cursor = self.db.cursor()
            cursor.execute(sql, args)
            rows = cursor.fetchall()
        except Exception as e:
            raise DBError(sql)
        finally:
            cursor.close()
        return rows

    def execute(self, sql, args):
        """ 执行SQL，返回受影响的行数，比如insert, update, delete语句
        """
        assert sql
        print('enter execute')
        try:
            self.check_db()
            self.db.autocommit(True)
            cursor = self.db.cursor()
            nrows = cursor.execute(sql, args)
            if 'insert' in sql and 'tb_product' in sql:
                resp_id = self.db.insert_id()
                print('add product id : %s' % resp_id)

        except Exception as e:
            self.db.rollback()
            raise DBError(sql)
        finally:
            cursor.close()

        return nrows

    def execute_transaction(self, sql_list):
        assert sql_list
        nrows = 0
        try:
            self.check_db()
            self.db.autocommit(False)
            cursor = self.db.cursor()
            for sql, args in sql_list:
                nrows += cursor.execute(sql, args)
                if 'insert' in sql and 'tb_product' in sql:
                    resp_id = self.db.insert_id()
                    print('add product id : %s' % resp_id)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise DBError(sql)
        finally:
            cursor.close()
        return nrows

    def execute_many(self, sql, args):
        assert sql
        try:
            self.check_db()
            cursor = self.db.cursor()
            nrows = cursor.executemany(sql, args)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise DBError(sql)
        finally:
            cursor.close()
        return nrows
