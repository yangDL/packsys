# -*- coding: utf-8 -*-

import hashlib, os, json

from PIL import Image
from flaskpp.config import Config, get_cfg
from qiniu import Auth, put_file

class QiNiu():
    def __init__(self):
        self.ak     = get_cfg().get_str('qiniu', 'ACCESS_KEY')
        self.sk     = get_cfg().get_str('qiniu', 'SECRET_KET')
        self.folder = get_cfg().get_str('qiniu', 'UPLOAD_FOLDER')
        self.url    = get_cfg().get_str('qiniu', 'URL_PREFIX')
        self.zone   = get_cfg().get_str('qiniu', 'ZONE')

    def get_token(self):
        q = Auth(self.ak, self.sk)
        return q.upload_token(self.zone)

    def get_folder(self, img_type):
        folder_path = os.path.join(self.folder, img_type)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        return folder_path

    def random_str(self, len):
        str = ""
        for i in range(len):
            str += random.choice("0123456789abcdefghijklmnopqrstuvwxyz")
        return str


    def gen_img_name(self, id, img_type, f):
        md5 = hashlib.md5(f.read()).hexdigest()
        img_fname = '%s_%s_%s' % (id, img_type, md5)
        return img_fname

    def upload(self, pro_id, shop_id, img_type, f):
        if not pro_id or not shop_id or not img_type:
            return -1, '未传入userid或businesstype', (0,0)

        folder_path = os.path.join(self.folder, img_type)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        new_fname = self.gen_img_name(pro_id, img_type, f)
        new_fpath = os.path.join(folder_path, new_fname)

        im = Image.open(f)
        size = im.size
        if size[0] > 1000:
            w = size[0]
            h = size[1]
            size = (1000, int(h/w * 1000))

        nim = im.resize(size, Image.ANTIALIAS)
        nim.save(new_fpath, 'JPEG')
        size = nim.size

        token = self.get_token()
        ret, resp = put_file(token, new_fname, new_fpath, mime_type='image/jpeg', check_crc=True)
        if int(resp.status_code) == 614:
            print('已上传过，无需重复上传')
            return 614, '%s%s' % (self.url, new_fname), size
        elif int(resp.status_code) == 200:
            print("上传成功")
            return 200, '%s%s' % (self.url, new_fname), size
        else:
            print('访问出错，code:%s' % resp.status_code )
            return -1, resp.error, (0,0)
