# -*- coding: utf-8 -*-
import json, requests
import sys, subprocess
from flaskpp.img_util import *
from flaskpp.flaskpp import *

def gen_code():
    base_time = 1451577600  #20160101 00:00:00的时间戳
    bts = int(time.time()) - base_time
    r = requests.get('http://119.29.94.190:88/gen_key?key=%s' % bts)
    if r.status_code != 200:
        return ''
    resp_id = json.loads(r.text)['id']
    return 'PN%09d%04d' % (bts, resp_id)

def allshops(start, limit=20, word=''):
    total_sql, total_args = '', []
    if not word:
        sql = 'select id, name, address, webSite, shop_type from tb_shop order by id desc limit %s, %s'
        total_sql = 'select count(id) from tb_shop' 
        args = (start, limit)
    else:
        sql = 'select id, name, address, webSite, shop_type from tb_shop where name like %s order by id desc limit %s, %s'
        total_sql = 'select count(id) from tb_shop where name like %s' 
        args = ('%%%s%%' % word, start, limit)
        total_args = ['%%%s%%' % word]
    
    rows = get_db().query_multi(sql, args)
    if not rows:
        return None
    items, total = [], 0
    for id, name, address, webSite, shop_type in rows:
        item = {}
        item['id'] = int(id)
        item['name'] = name
        item['address'] = address
        item['url'] = webSite
        item['shop_type'] = '自营' if int(shop_type) == 0 else '淘宝'
        item['shoptype'] = int(shop_type)
        items.append(item)

    row = get_db().query_single(total_sql, total_args)
    if row:
        total = row[0]
    return {'shops':items, 'total':total}

def response_tags():
    sql = ('select id, name from tb_response_tag')
    rows = get_db().query_multi(sql)
    if not rows:
        return None
    resps = []
    for id, name in rows:
        item = {'id':id, 'name':name}
        resps.append(item)
    return resps

def element_tags():
    sql = ('select id, name from tb_element_tag')
    rows = get_db().query_multi(sql)
    if not rows:
        return None
    elements = []
    for id, name in rows:
        elements.append({'id':id, 'name':name})

    return elements

def get_brands():
    sql = ('select id, ch_name, en_name from tb_brand')
    rows = get_db().query_multi(sql)
    if not rows:
        return None
    brands = []
    for id, ch_name, en_name in rows:
        brands.append({'id':id, 'ch':ch_name, 'en':en_name})

    return brands

def category():
    sql = ('select id, name from tb_config_category')
    rows = get_db().query_multi(sql)
    if not rows:
        return None

    data = []
    for id, name in rows:
        item = {'id':int(id), 'name': name}
        data.append(item)
    return data

def cate_dict():
    sql = ('select id, name from tb_config_category')
    rows = get_db().query_multi(sql)
    if not rows:
        return None

    data = {}
    for id, name in rows:
        data[int(id)] = name
    return data

def sub_category():
    sql = ('select id, cate_id, name from tb_config_subcategory')
    rows = get_db().query_multi(sql)
    if not rows:
        return None
    data = []
    for id, cate_id, name in rows:
        item = {'id':id, 'cate_id':cate_id, 'name':name}
        data.append(item)
    
    return data

def conf_scenes():
    sql = 'select id, name from tb_config_scene'
    rows = get_db().query_multi(sql)
    if not rows:
        return None
    data = []
    for id, name in rows:
        item = {'id':id, 'name':name}
        data.append(item)
    return data

def conf_styles():
    sql = 'select id, name from tb_config_style'
    rows = get_db().query_multi(sql)
    if not rows:
        return None
    data = []
    for id, name in rows:
        item = {'id':id, 'name':name}
        data.append(item)
    return data

def resp_tag_words():
    sql = ( 'select w.id, t.name, c.name, s.name, w.word from tb_response_tag_word as w'
            ' inner join tb_response_tag as t on t.id=w.resp_id'
            ' inner join tb_config_scene as c on c.id=w.scene_id'
            ' inner join tb_config_style as s on s.id=w.style_id')
    rows = get_db().query_multi(sql)
    if not rows:
        return None
    data = []
    for id, tname, cname, sname, word in rows:
        item = {'id':id, 'resp':tname, 'scene':cname, 'style':sname, 'word':word}
        data.append(item)

    return data

def tag_word(word_id, tb_name):
    sql = ( 'select word from %s where id=%s' % (tb_name, word_id))
    print(sql)
    row = get_db().query_single(sql)
    if not row or not row[0]:
        return None
    return row[0]

def elem_tag_words():
    sql = ('select w.id, e.name, d.name ,w.word from tb_element_tag_word as w '
           'inner join tb_element_tag as e on e.id=w.elem_id '
           'inner join tb_config_body_defect as d on d.id=w.defect_id')

    rows = get_db().query_multi(sql)
    if not rows:
        return None
    data = []

    for id, ename, dname, word in rows:
        item = {'id':id, 'elem':ename, 'defect':dname, 'word':word}
        data.append(item)

    return data

def defects():
    sql = 'select id, name from tb_config_body_defect'
    rows = get_db().query_multi(sql)
    if not rows:
        return None
    data = []
    for id, name in rows:
        item = {'id':id, 'name':name}
        data.append(item)
    return data

def query_shop(shop_id):
    sql = ( 'select id, name, webSite, address, desc_text, updatetime, shop_type '
            'from tb_shop where shop_status=0 and id=%s')

    row = get_db().query_single(sql, (shop_id,) )
    if not row:
        return None

    shop = {}
    shop['id'] =    int(row[0])
    shop['name'] =  row[1]
    shop['url'] =   row[2]
    shop['addr'] =  row[3]
    shop['desc'] =  row[4]
    shop['utime'] = timestr(row[5])
    shop['shop_type'] = int(row[6])
    shop['num'] = count_product(shop_id)

    return shop

def count_product(shop_id):
    sql = ('select count(id) from tb_sourse_product where shop_id=%s')
    row = get_db().query_single(sql, (shop_id,) )
    if not row:
        return None

    return int(row[0])

def query_img(shop_id, product_id):
    sql = ('select url from tb_sourse_product_img where shop_id=%s and product_id=%s limit 1;')
    row = get_db().query_single(sql,(shop_id, product_id))
    if not row:
        return None
    return row[0]

def tb_source_products(sql, args):
    rows = get_db().query_multi(sql, args)
    if not rows:
        return None
    products = []
    for id, shop_id, name, old_price, now_price, website, is_edit in rows:
        shop_info = query_shop(shop_id)
        item = {}
        item['id'] = int(id)
        item['shopid'] = int(shop_id)
        item['name'] = name
        item['op'] = old_price
        item['np'] = now_price
        item['url']= website
        item['edit'] = is_edit
        item['img'] = query_img(shop_id, id)
        item['shop'] = shop_info['name']
        item['shop_type'] = shop_info['shop_type']
        products.append(item)
    return products

def query_source_products(word, page, limit=40):
    min = (page - 1) * limit
    if not word:
        sql = ( 'select id, shop_id, name, old_price, now_price, webSite, price_type, is_edit from tb_sourse_product limit %s, %s;')
        args = ( min, limit)
    else:
        sql = ( 'select id, shop_id, name, old_price, now_price, webSite, price_type, is_edit from tb_sourse_product '
                'where lower(name) like %s limit %s, %s;')
        args = ('%%%s%%' % word.lower(),  min, limit)

    rows = get_db().query_multi(sql, args)
    if not rows:
        return None
    products = []
    for id, shop_id, name, old_price, now_price, website, price_type, is_edit in rows:
        shop_info = query_shop(shop_id)
        item = {}
        item['id'] = int(id)
        item['shopid'] = int(shop_id)
        item['name'] = name
        item['op'] = old_price
        item['np'] = now_price
        item['url']= website
        item['price_type'] = price_type
        item['edit'] = is_edit
        item['img'] = query_img(shop_id, id)
        item['shop'] = shop_info['name']
        item['shop_type'] = shop_info['shop_type']
        products.append(item)

    return products

def query_product(shop_id, start, limit=20, word=''):
    total = 0
    if not word:
        sql = ('select count(id) from tb_sourse_product where shop_id = %s')
        row = get_db().query_single(sql, (shop_id,))
        if row and row[0]:
            total = row[0]
        sql = ( 'select p.id, p.name, c.name, p.old_price, p.now_price, p.webSite, p.price_type, '
                'p.is_edit from tb_sourse_product as p inner join tb_config_category as c on '
                'c.id = p.category_id where p.shop_id = %s limit %s, %s')
        args = (shop_id, start, limit)

    else:
        sql = ('select count(id) from tb_sourse_product where shop_id = %s and lower(name) like %s')
        row = get_db().query_single(sql, (shop_id, '%%%s%%' % word.lower()))
        if row and row[0]:
            total = row[0]
        sql = ( 'select p.id, p.name, c.name, p.old_price, p.now_price, p.webSite, p.price_type, '
                'p.is_edit from tb_sourse_product as p inner join tb_config_category as c on '
                'c.id = p.category_id where p.shop_id = %s and lower(p.name) like %s limit %s, %s;')
        args = (shop_id, '%%%s%%' % word.lower(), start, limit)
    print(sql % args)

    rows = get_db().query_multi(sql, args )
    if not rows:
        return None, 0

    products = []
    cates = cate_dict()
    for id, name, type, oprice, nprice, url, pricetype, is_edit in rows:
        proid = 0
        if is_edit == 1:
            tb_product = one_tb_product(id)
            if tb_product:
                name = tb_product['title']
                oprice = tb_product['op']
                nprice = tb_product['np']
                type = cates[int(tb_product['cate'])]
                proid = tb_product['id']
            else:
                is_edit = 0
        item = {}
        item['proid'] = proid
        item['id'] = int(id)
        item['name'] = name
        item['type'] = type
        item['op'] = oprice
        item['np'] = nprice
        item['url'] = url
        item['is_edit'] = is_edit
        products.append(item)

    return products, total


def query_tb_product(shop_id, start, limit=20, word=''):
    total = 0
    if not word:
        sql = ('select count(id) from tb_product where shop_id = %s')
        row = get_db().query_single(sql, (shop_id,))
        if row and row[0]:
            total = row[0]
        sql = ( 'select p.id, p.source_id, p.title, c.name, p.original_price, p.price '
                'from tb_product as p inner join tb_config_category as c on '
                'c.id = p.category_id where p.shop_id = %s limit %s, %s;')
        args = (shop_id, start, limit)
    else:
        sql = ('select count(id) from tb_product where shop_id = %s and lower(title) like %s')
        row = get_db().query_single(sql, (shop_id, '%%%s%%' % word.lower()))
        if row and row[0]:
            total = row[0]
        sql = ( 'select p.id, p.source_id, p.title, c.name, p.original_price, p.price from tb_product as p '
                'inner join tb_config_category as c on c.id = p.category_id '
                'where p.shop_id = %s and lower(p.title) like %s limit %s, %s;')
        args = (shop_id, '%%%s%%' % word.lower(), start, limit)

    rows = get_db().query_multi(sql, args )
    if not rows:
        return None, 0

    products = []
    for pid, id, name, type, oprice, nprice in rows:
        item = {}
        item['proid'] = pid
        item['id'] = int(id)
        item['name'] = name
        item['type'] = type
        item['op'] = oprice
        item['np'] = nprice
        item['is_edit'] = 1
        products.append(item)
    return products, total

def one_product(product_id):
    sql = ( 'select p.id, p.name, c.name, p.old_price, p.now_price, p.webSite, p.price_type, '
            'desc_text, attr from tb_sourse_product as p inner join tb_config_category as c '
            'on c.id = p.category_id where p.id = %s')
    row = get_db().query_single(sql, (product_id, ) )
    if not row:
        return None

    product = {}
    product['id'] = int(row[0])
    product['name'] = row[1]
    product['type'] = row[2]
    product['op'] = row[3]
    product['np'] = row[4]
    product['url'] = row[5]
    product['pricetype'] = row[6]
    product['desc'] = row[7]
    product['attr'] = row[8]

    return product

def tb_attr_value():
    sql = 'select id, attr_id, name from tb_attr_value'
    rows = get_db().query_multi(sql)
    if not rows:
        return None
    data = {}
    for id, attr_id, name in rows:
        data[name] = {'id':id, 'attr_id':attr_id}

    return data

def detail_size(pro_id):
    sql = ('select detail_text, size_text from tb_product where source_id=%s')
    print(sql % pro_id)
    row = get_db().query_single(sql, (pro_id, ) )
    if not row:
        return None, None
    try:
        details = json.loads(row[0])
    except Exception as ex:
        print(ex)
        details = None
    try:
        sizes = json.loads(row[1])
    except Exception as ex:
        print(ex)
        sizes = None
    return details, sizes

def one_tb_product(id):
    sql = ( 'select id,title,name, brand, category_id, desc_text, desc_imgs, original_price, price, '
            'detail_text,size_text,source_type, place,cash_back, can_try, profit, word '
            'from tb_product where source_id=%s')
    row = get_db().query_single(sql, (id, ) )
    if not row:
        return None

    data = {}
    data['id'] = row[0]
    data['title'] = row[1]
    data['name'] = row[2]
    data['brand'] = row[3]
    data['cate'] = row[4]
    data['desc'] = row[5]
    data['desc_img'] = row[6]
    data['op'] = row[7]
    data['np'] = row[8]
    data['place'] = row[12]
    data['cash_back'] = row[13]
    data['can_try'] = row[14]
    data['profit'] = row[15]
    data['word'] = row[16]
    """
    data['scenes']  = get_proid_tags('match','scene', row[0])
    data['styles']  = get_proid_tags('match','style', row[0])
    data['resps']   = get_proid_tags('resp','resp',   row[0])
    data['defects'] = get_proid_tags('resp','defect', row[0])
    data['elements']= get_proid_tags('resp','elem',   row[0])
    """
    return data

def pro_img(product_id):
    sql = ('select id, url from tb_sourse_product_img where product_id=%s')
    rows = get_db().query_multi(sql, (product_id, ) )
    if not rows:
        return []

    product_imgs = []
    for id, url in rows:
        item = {}
        item['id'] = id
        item['url'] = url
        item['ds'] = 0 #details 选中为1
        item['ss'] = 0 #sizes 选中为1
        product_imgs.append(item)

    return product_imgs

def set_sku(id, shop_id, source_id, title, np, code):
    sql = 'select price from tb_sku where product_id=%s limit 1'
    row = get_db().query_single(sql, (id,) )
    rows = 0
    if row and row[0]:
        if int(row[0]) != int(np):
            sql = 'update tb_sku set price=%s where product_id=%s'
            rows = get_db().execute(sql, (np, id) )
    else:
        attr_vals = tb_attr_value()
        sql = 'select attr from tb_sourse_product where id=%s'
        row = get_db().query_single(sql, (source_id, ) )
        args = []
        if row[0]:
            try:
                attr = json.loads(row[0].replace("'", '"'))
                szs, skus = set(), set()
                if attr['sz']:
                    for sz in attr['sz']:
                        if sz not in attr_vals:
                            szs.add('2:200')
                        else:
                            szs.add('2:%s' % attr_vals[sz]['id'])

                if not szs:
                    szs.add('2:200')
                szs = list(szs)

                if attr['color']:
                    for color in attr['color']:
                        if color not in attr_vals:
                            cls = '1:100'
                        else:
                            cls = '1:%s' % attr_vals[color]['id']
                        for sz in szs:
                            skus.add('%s|%s' % ( sz, cls) )
                if not skus:
                    for sz in szs:
                        skus.add('%s|1:100' % sz )

                for sku in skus:
                    args.append( (id, shop_id, title, sku, np, code) )

            except:
                args.append( (id, shop_id, title, '1:100|2:200', np, code) )

        else:
            args.append( (id, shop_id, title, '1:100|2:200', np, code) )

        sql = ('insert into tb_sku (product_id, shop_id, name, attr_maps, price, code, stock) '
               'values(%s, %s, %s, %s, %s, %s, 10)')
        rows = get_db().execute_many(sql , args)
    return rows

def tb_products(sql, args=None):
    products = get_db().query_multi(sql, args)
    if not products:
        return []
    cates = category()
    brands = get_brands()
    shops = allshops(0, 999999999)['shops']

    def mate_multi(datas, mateval):
        if not mateval:
            return ''
        res = []
        for data in datas:
            if str(data['id']) in mateval.split(','):
                res.append(data['name'])
        return ','.join(res)

    datas = []

    for id, shop_id, title, brand, cateid,img, op, np,source_id in products:
        item = {}
        item['id'] = id
        item['title'] = title
        item['shop_id'] = shop_id
        item['source_id'] = source_id
        for shop in shops:
            if int(shop['id']) == int(shop_id):
                item['shop'] = shop['name']
                item['type'] = shop['shop_type']
                item['shop_type'] = shop['shoptype']
                break

        for b in brands:
            if b['id'] == brand:
                item['brand'] = b['ch']
                break

        for cate in cates:
            if cate['id'] == cateid:
                item['cate'] = cate['name']
                break

        item['img'] = img
        item['op'] = op
        item['np'] = np

        datas.append(item)

    return datas

def down_img(img_url):
    folder = get_cfg().get_str('qiniu', 'UPLOAD_FOLDER')
    img_name = '%s' % img_url.split('/')[-1].split('?')[0]
    file_path = '%s%s' % (folder, img_name)
    if os.path.isfile(file_path):
        if os.stat(file_path).st_size < 10:
            os.system('rm %s' % file_path)

    if not os.path.isfile(file_path):
        try:
            cmd = 'cd %s; wget -O "%s" "%s"' % (folder, img_name, img_url)
            print(cmd)
            os.system(cmd)
        except Exception as ex:
            print(ex)
    if not os.path.isfile(file_path):
        return None
    return file_path

def update_img_url(old_url, new_url):
    id = query_img_by_url(old_url)
    if not id:
        return None
    sql = ('update tb_sourse_product_img set url=%s where id=%s')
    row = get_db().execute(sql, (new_url, id))
    if not row:
        return None
    return id

def query_img_by_url(url):
    sql = ('select id from tb_sourse_product_img where url=%s')
    row = get_db().query_single(sql, (url,))
    if not row or not row[0]:
        return None
    return row[0]


def due_imgs(imglist, pro_id, shop_id, type):
    imgs = []
    qiniu = QiNiu()
    for img in imglist:
        if 'qiniucdn.com' not in img:
            img_path = down_img(img)
            if not img_path:
                continue
            if os.stat(img_path).st_size < 10:
                continue
            print(img_path)
            f = open(img_path, 'rb')
            ret, url, (w,h) = qiniu.upload(pro_id, shop_id, type, f)
            print(ret, url )
            if ret == -1:
                continue
            id = update_img_url(img, url)
            if not id:
                continue
            item = {'url':url, 'width':w, 'height':h, 'id':id}
            imgs.append(item)
        else:
            chk_url = '%s?imageInfo' % img
            print(chk_url)
            output = subprocess.check_output(['curl', chk_url]).decode('utf-8')
            imginfo = json.loads(output)
            if 'error' in imginfo:
                continue
            id = query_img_by_url(img)
            if not id:
                continue
            item = {'url':img, 'width':imginfo['width'], 'height':imginfo['height'], 'id':id}
            imgs.append(item)
    return imgs

def update_pro_ds(pro_id, shop_id, up_type, desc, imgs):
    attr = {}
    attr['desc'] = desc
    attr['imgs'] = imgs
    attr_str = json.dumps(attr)
    print(attr_str)

    sql = 'insert into tb_product (shop_id, source_id,'+up_type+'_text) values(%s,%s,%s) ON DUPLICATE KEY UPDATE '+up_type+'_text=%s;'
    args = (shop_id, pro_id, attr_str, attr_str)
    try:
        row = get_db().execute(sql, args )
    except Exception as ex:
        print(ex)
        return {'msg':str(ex)}

    if 'detail' == up_type and imgs is not None:#选第一张为主图
        try:
            main_img = imgs[0]['url']
            sql = ('update tb_product set desc_imgs=%s where source_id=%s')
            print(sql % (main_img, pro_id) )
            row = get_db().execute(sql, (main_img, pro_id))
            if not row:
                print('更新主图失败')
        except Exception as ex:
            print(ex)
    return attr

def analysis_elist(elist):
    elements, defects, ewords = '', '', []
    for item in elist:
        word_id = int(item['key'].split('_')[0])
        elem_id = int(item['key'].split('_')[1])
        defect_id = int(item['key'].split('_')[2])
        elements += '%s,' % elem_id
        defects  += '%s,' % defect_id
        ewords.append(item['key'])
    
    return elements, defects, ewords

def analysis_rlist(rlist):
    scenes, styles, resps,rwords  = '', '', '', []
    for item in rlist:
        dk = item['key'].split('_')
        word_id = dk[0]
        scene_id = dk[1]
        style_id = dk[2]
        resp_id = dk[3]
        scenes += '%s,' % scene_id
        styles += '%s,' % style_id
        resps += '%s,' % resp_id
        rwords.append(item['key'])
    
    return scenes, styles, resps, rwords

def all_place():
    sql = ('select id, name from tb_place')
    rows = get_db().query_multi(sql)
    if not rows:
        return None
    resps = []
    for id, name in rows:
        item = {'id':id, 'name':name}
        resps.append(item)
    return resps

def get_proid_tags(pre_str,raw_str, pro_id):
    '''获取正向索引下的标签
    '''
    key = '%s::%s::%s' % (pre_str, raw_str, pro_id)
    print('key:', key)
    items = get_redis().smembers(key)
    items = [id.decode('utf-8') if isinstance(id, bytes) else id for id in items]
    return items

def del_proid_key(pre_str, raw_str, pro_id):
    key = '%s::%s::%s' % (pre_str, raw_str, pro_id)
    get_redis().delete(key) #删除正向索引的key

def srem_tag(pre_str, raw_str, pro_id):
    items = get_proid_tags(pre_str, raw_str, pro_id) #获取该商品的标签
    
    for item in items: #遍历商品的标签，删除标签下该件商品
        if not item:
            continue
        tag_key = '%s::%s::tag::%s' % (pre_str, raw_str, item)
        get_redis().srem(tag_key, pro_id)

    del_proid_key(pre_str, raw_str, pro_id) #删除正向索引

def srem_proid_tagword(pro_id):
    key = 'tagword::elem::%s' % pro_id
    get_redis().delete(key)
    key = 'tagword::resp::%s' % pro_id
    get_redis().delete(key)
    key = 'tagword::element::%s' % pro_id
    get_redis().delete(key)
    key = 'tagword::response::%s' % pro_id
    get_redis().delete(key)


def add_to_redis(id, type, subcate, scenes, styles, resps, defects, elements, ewords, rwords):
    #发布需求相关
    match_key = 'match::category::%s' % id
    get_redis().set(match_key, type)
    match_key = 'match::category::tag::%s' % type
    get_redis().sadd(match_key, id)

    match_key = 'match::subcategory::%s' % id
    get_redis().set(match_key,subcate)
    match_key = 'match::subcategory::tag::%s' % subcate
    print(match_key, id)
    get_redis().sadd(match_key, id)

    def sadd_it(items, key):
        get_redis().delete(key)
        for item in items:
            if not item:
                continue
            get_redis().sadd(key, item )

    sadd_it(scenes.split(','), 'match::scene::%s' % id)
    sadd_it(styles.split(','), 'match::style::%s' % id)
    sadd_it(resps.split(','), 'resp::resp::%s' % id)
    sadd_it(defects.split(','), 'resp::defect::%s' % id)
    sadd_it(elements.split(','), 'resp::elem::%s' % id)
    """
    sadd_it(ewords, 'tagword::element::%s' % id)
    sadd_it(rwords, 'tagword::response::%s' % id)
    """
    def sadd_tag(items, key_raw):
        for item in items:
            if not item:
                continue
            key = key_raw % item
            get_redis().sadd(key, id)

    sadd_tag(scenes.split(','), 'match::scene::tag::%s')
    sadd_tag(styles.split(','), 'match::style::tag::%s')
    sadd_tag(resps.split(','), 'resp::resp::tag::%s')
    sadd_tag(defects.split(','), 'resp::defect::tag::%s')
    sadd_tag(elements.split(','), 'resp::elem::tag::%s')

    return True

def del_tb_product(source_id):
    sql = ('select id from tb_product where source_id=%s')
    row = get_db().query_single(sql, (source_id,))
    if not row or not row[0]:
        return False, '未找到该商品信息'
    pro_id = row[0]
    print(pro_id)
    cate = get_redis().get('match::category::%s' % pro_id)
    if isinstance(cate, bytes):
        cate = cate.decode('utf-8')
    get_redis().srem('match::category::tag::%s' % cate, pro_id)
    get_redis().delete('match::category::%s' % pro_id)

    subcate = get_redis().get('match::subcategory::%s' % pro_id)
    if isinstance(subcate, bytes):
        subcate = subcate.decode('utf-8')
    get_redis().srem('match::subcategory::tag::%s' % subcate, pro_id)
    get_redis().delete('match::subcategory::%s' % pro_id)

    srem_tag('match','scene', pro_id)
    srem_tag('match','style', pro_id)
    srem_tag('resp','resp', pro_id)
    srem_tag('resp','defect', pro_id)
    srem_tag('resp','elem', pro_id)

    srem_proid_tagword(pro_id)
    #删除搭配
    match = ProMatch(pro_id)
    match.del_match()
    
    sql_list = []
    sql = ('delete from tb_product where id=%s')
    sql_list.append((sql, (pro_id,)))
    sql = ('delete from tb_sku where product_id=%s')
    sql_list.append((sql, (pro_id,)))
    sql = ('delete from tb_sourse_product where id=%s')
    sql_list.append((sql, (source_id,)))
    sql = ('delete from tb_sourse_product_img where product_id=%s')
    sql_list.append((sql, (source_id,)))

    rows = get_db().execute_transaction(sql_list)
    return True, '成功'

def del_source_product(source_id):
    sql = ('select id from tb_sourse_product where id=%s')
    row = get_db().query_single(sql, (source_id,))
    if not row or not row[0]:
        return False, '未找到该商品信息'

    sql_list = []
    sql = ('delete from tb_sourse_product where id=%s')
    sql_list.append((sql, (source_id,)))
    sql = ('delete from tb_sourse_product_img where product_id=%s')
    sql_list.append((sql, (source_id,)))
    rows = get_db().execute_transaction(sql_list)
    print (rows)

    return True, '成功'

def logic_del_shop(shop_id):
    sql_list = []
    sql = ('delete from tb_sourse_product where shop_id=%s')
    sql_list.append((sql, (shop_id,)))
    sql = ('delete from tb_sourse_product_img where shop_id=%s')
    sql_list.append((sql, (shop_id,)))
    sql = ('delete from tb_shop where id=%s')
    sql_list.append((sql, (shop_id,)))
    
    rows = get_db().execute_transaction(sql_list)
    
    sql = ('select id, source_id from tb_product where shop_id=%s')
    rows = get_db().query_multi(sql, (shop_id,))

    for id, source_id in rows:
        ret, msg = del_tb_product(source_id)
        if not ret:
            print('%s, source_id:%s, shop_id:%s' % (msg, source_id, shop_id))

    return len(rows)

def logic_get_sku(pro_id):
    sql = ('select attr_maps, price, stock from tb_sku where product_id=%s')
    rows = get_db().query_multi(sql, (pro_id,))
    if not rows:
        return None

    data = []
    for maps, price, stock in rows:
        item = {}
        item['maps'] = maps
        item['price'] = price
        item['stock'] = stock
        data.append(item)
    return data

def logic_get_attrvalue():
    sql = ('select id, attr_id, name from tb_attr_value')
    rows = get_db().query_multi(sql)
    if not rows:
        return None
    data = {}
    for id, aid, name in rows:
        attr_type =  str(aid)
        if attr_type not in data:
            data[attr_type] = {}
        data[attr_type][str(id)] = name
    return data

class ProMatch:
    def __init__(self, pro_id):
        self.pro_id = pro_id
        self.raw_key = 'product::match::%s'
        self.key = self.raw_key % pro_id

    def get_match(self):
        return get_proid_tags('product', 'match', self.pro_id)

    def del_match(self):
        match_ids = set(self.get_match())

        for mid in match_ids:
            key = self.raw_key % mid
            get_redis().srem(key, self.pro_id)

        get_redis().delete(self.key)

    def update_match(self, add_ids):
        match_ids = set( self.get_match() )
        print(match_ids)

        new_ids = add_ids - match_ids
        unbind_ids = match_ids - add_ids

        print('new', new_ids)
        print('unbind', unbind_ids)

        for unbind_id in unbind_ids:
            key = self.raw_key % unbind_id
            get_redis().srem(key, self.pro_id)
            get_redis().srem(self.key, unbind_id)

        for new_id in new_ids:
            key = self.raw_key % new_id
            get_redis().sadd(key, self.pro_id)
            get_redis().sadd(self.key, new_id)
