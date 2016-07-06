# -*- coding: utf-8 -*-

from pymongo import MongoClient

class LogAgent():
    def __init__(self, host, port, dbname):
        self.client = MongoClient(host=host, port=port)
        self.db = self.client[dbname]

    def access_log(self, data):
        """ 访问日志
        """
        if not isinstance(data, dict) or not data:
            return None

        try:
            result = self.db.access_log.insert(data)
        except Exception as e:
            return None
        return str(result)
