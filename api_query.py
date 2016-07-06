# -*- coding: utf-8 -*-
import json
from PIL import Image
from flaskpp.flaskpp import *
from flaskpp.img_util import *
from logic_comm import *

app = FlaskPlus(__name__)

ERR_MYSQL_COMMANDS = -1

@app.route('/login', methods=['post'])
def login():
    try:
        name = request.form['name']
        passwd = request.form['pwd']
    except Exception as ex:
        print(ex)
        return make_err(-1, '登录失败')
    print('name: %s, password: %s' % (name,passwd))
    app.logger.debug('name: %s, password: %s' % (name, passwd))
    sql = "SELECT id, nickname, avatar FROM tb_pack_user WHERE telephone = %s AND passwd = %s AND STATUS = 0"
    print(sql % (name, passwd))
    row = app.db.query_single(sql, (name, passwd))

    if row is None or not row[0]:
        return make_err(-1, '登录失败，请检查手机和密码')

    userid = row[0]
    g.userid = int(userid)
    name = row[1]
    avatar = row[2]

    token = gen_token(userid)
    if token is None:
        return make_err(-1, '生成验证失败')
    data = {'userid':userid, 'name':name, 'avator':avatar, 'token':token}
    return data

def gen_token(userid):
    """ 生成token
    """
    assert userid
    token_key = app.cfg.get_str('session', 'token_key')
    raw = '%d|%s|%s' % (int(time.time()), userid, token_key)
    print(raw)

    m = hashlib.md5()
    m.update(raw.encode('utf-8'))
    token = m.hexdigest()
    print(token)
    try:
        app.redis.set('tokens::%d' % userid, token)
    except Exception as e:
        return None
        
    return token

@app.route('/query/allshop', methods=['GET'])
def allshop():
    page = get_qs_int('page')
    limit = get_qs_int('limit')
    word = get_qs_str('word');
    if not word:
        word = ''
    start = (page-1) * limit
    return allshops(start, limit, word)

@app.route('/query/add_shop', methods=['POST'])
def add_shop():
    try:
        name    = request.form['name']
        addr    = request.form['addr']
        url     = request.form['url']
        desc    = request.form['desc']
        shop_type = request.form['shop_type']
    except Exception as ex:
        print(ex)
        return make_err(-1, '输入参数有误, %s' % str(ex))

    sql = ('select id from tb_shop where webSite=%s')
    row = app.db.query_single(sql, (url,))
    if row and row[0]:
        return make_err(-1, '该商店已添加过')

    sql = ( 'insert into tb_shop (name, address, webSite, desc_text, createtime, updatetime, shop_type)'
            'values(%s, %s, %s, %s, NOW(), NOW(), %s)')
    args = (name, addr, url, desc, shop_type)
    rows = app.db.execute(sql, args)
    return {'row':rows}

@app.route('/query/get_one_shop', methods=['GET'])
def get_one_shop():
    id = get_qs_int('id')

    sql = 'select name, address, webSite, desc_text, shop_type from tb_shop where id=%s'
    row = app.db.query_single(sql, (id,))
    item = {}
    item['name'] = row[0]
    item['addr'] = row[1]
    item['url'] = row[2]
    item['desc'] = row[3]
    item['shop_type'] = row[4]

    return item

@app.route('/query/update_shop', methods=['POST'])
def update_shop():
    try:
        id      = request.form['id']
        name    = request.form['name']
        addr    = request.form['addr']
        url     = request.form['url']
        desc    = request.form['desc']
        shop_type = request.form['shop_type']
    except Exception as ex:
        print(ex)
        return make_err(-1, '输入参数有误, %s' % str(ex))

    sql = ('update tb_shop set name=%s, address=%s, webSite=%s, desc_text=%s, shop_type=%s, updatetime=NOW() where id=%s')
    rows = app.db.execute(sql , (name, addr, url, desc, shop_type, id))
    return {'row':rows}

@app.route('/query/del_shop', methods=['GET'])
def del_shop():
    shops = get_qs_str('shops')
    if not shops:
        return make_err(-1, '请传入正确的参数')
    shops = shops.split(',')
    if len(shops) > 4:
        make_err(-1, '删除超过限制')
    num = 0
    for shop_id in shops:
        if not shop_id:
            continue
        num += logic_del_shop(shop_id)
    data = {'num':num}
    return data

@app.route('/query/get_prolist', methods=['GET'])
def get_prolist():
    page = get_qs_int('page')
    limit = get_qs_int('limit')
    start = (page-1) * limit

    shop_id = get_qs_int('shop_id')
    is_edit = get_qs_int('type')
    word = get_qs_str('word')
    shop = query_shop(shop_id)
    
    if is_edit == 0:
        products, total = query_product(shop_id, start, limit, word)
    else:
        products, total = query_tb_product(shop_id, start, limit, word)

    data = { 'shop':shop, 'products':products, 'total':total }
    return data

@app.route('/query/del_source_product', methods=['GET'])
def del_source_pro():
    source_ids = get_qs_str('ids')
    if not source_ids:
        return make_err(-1, '请传入正确的参数')
    source_ids = source_ids.split(',')
    data = []
    for id in source_ids:
        try:
            id = int(id)
        except:
            continue
        print(id)
        ret, msg =  del_source_product(id)
        item = {'id':id, 'ret':ret, 'msg':msg}
        data.append(item)
    return data

@app.route('/query/cate_brand', methods=['GET'])
def cate_brand():
    cate = category()
    brands = get_brands()
    return {'cates':cate, 'brands':brands}

@app.route('/query/del_pack_product', methods=['GET'])
def del_pack_product():
    source_ids = get_qs_str('ids')
    if not source_ids:
        return make_err(-1, '请传入正确的参数')
    source_ids = source_ids.split(',')
    data = []
    for id in source_ids:
        try:
            id = int(id)
        except:
            continue
        ret, msg =  del_tb_product(id)
        item = {'id':id, 'ret':ret, 'msg':msg}
        data.append(item)
    return data

@app.route('/query/get_unpack_product', methods=['GET'])
def get_unpack_product():
    page = get_qs_int('page')
    limit = get_qs_int('limit')
    start = (page - 1)*limit

    title = get_qs_str('title')
    shop_id= get_qs_int('shop_id')

    searchs, args, wheresql, total = [], [], '', 0
    if title:
        cond = '%%%s%%'
        searchs.append('name like %s')
        args.append(cond)
    if shop_id:
        searchs.append('shop_id=%s')
        args.append(shop_id)
    if len(searchs) > 0:
        wheresql = 'where %s' % (' and '.join(searchs))

    sql = ( 'select id, shop_id, name, old_price, now_price, webSite, is_edit '
            'from tb_sourse_product '+wheresql+' limit %s, %s')
    sarg =  [*args, start, limit]
    row = app.db.query_single('select count(id) from tb_sourse_product '+wheresql, args)
    if row:
        total = row[0]
    return {'total':total, 'pros':tb_source_products(sql, [*args, start, limit])}


@app.route('/query/add_brand', methods=['POST'])
def add_brand():
    try:
        ch_name = request.form['ch']
        en_name = request.form['en']
        story   = request.form['story']
    except Exception as ex:
        print(ex)
        return make_err(-1, '输入参数有误, %s' % str(ex))

    sql = ( 'insert into tb_brand (ch_name, en_name, story) values(%s,%s, %s)')
    args = (ch_name, en_name, story)
    rows = app.db.execute(sql, args)

    sql = ('select id, ch_name, en_name from tb_brand where ch_name=%s and en_name=%s')
    row = app.db.query_single(sql, (ch_name, en_name))
    data = {}
    if row:
        data['id'] = row[0]
        data['ch'] = row[1]
        data['en'] = row[2]
    return data

@app.route('/query/tag_list', methods=['GET'])
def tag_list():
    scenes = conf_scenes()
    styles = conf_styles()
    defect = defects()
    resps = response_tags()
    elements = element_tags()
    data = {
        'scenes':scenes, 'styles':styles, 'defects':defect, 
        'resps':resps, 'elements':elements
    }
    return data

"""
@app.route('/query/get_pack_product', methods=['GET'])
def get_pack_product():
    page = get_qs_int('page')
    limit = get_qs_int('limit')
    start = (page - 1)*limit

    title = get_qs_str('title')
    cate = get_qs_int('cate')
    brand = get_qs_int('brand')

    searchs, args, wheresql, total = [], [], '', 0
    if title:
        cond = '%%%s%%'
        searchs.append('title like %s')
        args.append(cond)
    if cate:
        searchs.append('category_id=%s')
        args.append(cate)
    if brand:
        searchs.append('brand=%s')
        args.append(brand)
    if len(searchs) > 0:
        wheresql = 'where %s' % (' and '.join(searchs))
    sql = ( 'select id, shop_id, title, brand, category_id, desc_imgs, original_price, price,'
            'source_id from tb_product '+wheresql+' order by id desc limit %s, %s')
    sarg =  [*args, start, limit]
    row = app.db.query_single('select count(id) from tb_product '+wheresql, args)
    if row:
        total = row[0]
    return {'total':total, 'pros':tb_products(sql, [*args, start, limit])}
"""

@app.route('/query/get_pack_product', methods=['GET'])
def get_tagpack_product():
    page = get_qs_int('page')
    limit = get_qs_int('limit')
    start = (page - 1)*limit
    
    title = get_qs_str_default('title')
    cate = get_qs_int_default('cate')
    brand = get_qs_int_default('brand')

    scene_id = get_qs_int_default('scene')
    style_id = get_qs_int_default('style')
    resp_id  = get_qs_int_default('resp')
    elem_id  = get_qs_int_default('elem')
    defect_id= get_qs_int_default('defect')
    args = None
    scenes = app.redis.smembers('match::scene::tag::%s' % scene_id) if scene_id else None
    styles = app.redis.smembers('match::style::tag::%s' % style_id) if style_id else None
    resps  = app.redis.smembers('resp::resp::tag::%s'   % resp_id ) if resp_id else None
    elems  = app.redis.smembers('resp::elem::tag::%s'   % elem_id ) if elem_id else None
    defects= app.redis.smembers('resp::defect::tag::%s' % defect_id) if defect_id else None
    if scenes is not None:
        args = args & scenes if args is not None else scenes
    if styles is not None:
        args = args & styles if args is not None else styles
    if resps is not None:
        args = args & resps if args is not None else resps
    if elems is not None:
        args = args & elems if args is not None else elems
    if defects is not None:
        args = args & defects if args is not None else defects
    total, wheresql, searchs, sqlargs = 0, '', [], []
    if args is not None:
        if len(args) == 0:
            return {'total':0, 'pros':[]}
        args = [id.decode('utf-8') if isinstance(id, bytes) else id for id in args]
        searchs.append('id in (%s)' % ','.join(args))

    if title:
        cond = '%%%s%%' % title
        searchs.append('title like %s')
        sqlargs.append(cond)
    if cate:
        searchs.append('category_id=%s')
        sqlargs.append(cate)
    if brand:
        searchs.append('brand=%s')
        sqlargs.append(brand)

    if len(searchs) > 0:
        wheresql = 'where %s' % (' and '.join(searchs))

    sql = ( 'select id, shop_id, title, brand, category_id, desc_imgs, original_price, price,'
            'source_id from tb_product '+wheresql+' order by id desc limit %s, %s')
    
    row = app.db.query_single(('select count(id) from tb_product '+wheresql), tuple(sqlargs) )
    if row:
        total = row[0]
    return {'total':total, 'pros':tb_products(sql, (*sqlargs, start, limit))}

@app.route('/query/add_source_product', methods=['POST'])
def add_source_product():
    try:
        name    = request.form['title']
        desc    = request.form['desc']
        op      = request.form['op']
        np      = request.form['np']
        url     = request.form['url']
        type    = request.form['type']
        shop_id = request.form['shop_id']
        imglist = json.loads(request.form['imglist'])
    except Exception as ex:
        print(ex)
        return make_err(-1, '输入参数有误, %s' % str(ex))

    sql = ('select id from tb_sourse_product where webSite=%s')
    row = app.db.query_single(sql, (url,) )
    source_id = 0
    if row and row[0]:
        source_id = int(row[0])
        sql = ( 'update tb_sourse_product set shop_id=%s,category_id=%s,name=%s,desc_text=%s,'
                'old_price=%s, now_price=%s where id=%s')
        args = (shop_id, type, name, desc, op, np, row[0])
        row  = app.db.execute(sql, args)
    else:
        sql = ( 'insert into tb_sourse_product (shop_id, category_id, name, old_price, now_price,'
                'desc_text,webSite) values(%s, %s, %s, %s, %s, %s, %s)')
        args = (shop_id, type, name, op, np, desc, url)
        row  = app.db.execute(sql, args)
        
        sql = ('select id from tb_sourse_product where webSite=%s')
        row = app.db.query_single(sql, (url,) )
        source_id = int(row[0])

    args = []
    for img in imglist:
        if not img:
            continue
        args.append((int(shop_id), source_id, img))

    print(args)

    sql = ('insert into tb_sourse_product_img(shop_id, product_id, url) values(%s, %s, %s)')
    rows = app.db.execute_many(sql, args)
    return {'rows':rows}


@app.route('/query/allproducts', methods=['GET'])
def allproducts():
    page = get_qs_int('page')
    limit = get_qs_int('limit')

    base = (page-1)*limit
    total = 0
    if page == 1:
        sql = ('select count(id) from tb_product')
        row = app.db.query_single(sql)
        if row and row[0]:
            total = row[0]

    sql = ( 'select id,shop_id, title, brand, category_id,desc_imgs, original_price, price,'
            'source_id from tb_product order by id desc limit %s, %s')
    args = (base, limit)

    print(sql % args)
    return {'total':total, 'pro':tb_products(sql, args)}

@app.route('/query/query_one', methods=['GET'])
def oneproduct():
    search_name = get_qs_str('name')
    type = get_qs_int('type')
    page = get_qs_int('page')
    limit = get_qs_int('limit')
    cate = get_qs_int('cate')

    base = (page - 1) * limit
    total = 0
    pre_sql = 'select id,shop_id,title,brand,category_id,desc_imgs,original_price,price,source_id from tb_product '
    if search_name != '':
        if page == 1:
            sql = ('select count(id) from tb_product where source_type=%s and lower(title) like %s')
            args = (type, '%%%s%%' % search_name.lower())
            row = app.db.query_single(sql, args)
            if row and row[0]:
                total = row[0]

        sql = pre_sql + 'where source_type=%s and lower(title) like %s order by id desc limit %s, %s'
        args = (type, '%%%s%%' % search_name.lower(), base, limit)
        if cate != 0:
            sql = pre_sql + 'where source_type=%s and lower(title) like %s and category_id=%s order by id desc limit %s, %s'
            args = (type, '%%%s%%' % search_name.lower(), cate, base, limit)

    
    elif search_name == '':
        if page == 1:
            sql = ('select count(id) from tb_product where source_type=%s')
            row = app.db.query_single(sql, (type,) )
            if row and row[0]:
                total = row[0]
            
        sql = pre_sql + 'where source_type=%s order by id desc limit %s, %s'
        args = (type, base, limit)
        if cate != 0:
            sql = pre_sql + 'where source_type=%s and category_id=%s order by id desc limit %s, %s'
            args = (type, cate, base, limit)
    print(sql % args)

    return {'total':total, 'pro':tb_products(sql, args)}

@app.route('/query/source_products', methods=['GET'])
def source_products():
    word = get_qs_str('word')
    page = get_qs_int('page')
    limit = get_qs_int('limit')
    products = query_source_products(word, page, limit)
    if not products:
        return make_err(-1, '查无数据')

    total = 0
    sql = ('select count(id) from tb_sourse_product where lower(name) like %s')
    args = ('%%%s%%' % word.lower(),)
    print(sql % args)
    row = app.db.query_single(sql, args)
    if row and row[0]:
        total = row[0]
    return {'total':total, 'pro':products}


@app.route('/query/search_shop', methods=['GET'])
def search_shop():
    shop_name = get_qs_str("name")
    shop_type = get_qs_int("type")
    if not shop_name:
        sql = 'select id, name from tb_shop where shop_type=%s'
        args = (shop_type, )
    else:
        sql = 'select id, name from tb_shop where shop_type=%s and lower(name) like %s'
        args = (shop_type, '%%%s%%' % shop_name.lower())
    rows = app.db.query_multi(sql, args )
    if not rows:
        return make_err(ERR_MYSQL_COMMANDS, '未查询到含"%s"的商店' % shop_name)

    data = []
    for id, name in rows:
        item = {'%s' % id : name }
        data.append(item)
    return data

@app.route('/query/shop_product', methods=['GET'])
def shop_product():
    shop_id = get_qs_int('shop_id')
    is_edit = get_qs_int('type')
    word = get_qs_str('word')
    shop = query_shop(shop_id)
    if is_edit == 0:
        products, total = query_product(shop_id, 1, word=word)
    else:
        products, total = query_tb_product(shop_id, 1, word=word)

    data = { 'shop':shop, 'product':products, 'total':total }
    return data

@app.route('/query/products', methods=['GET'])
def products():
    shop_id = get_qs_int('shop_id')
    page = get_qs_int('page')
    is_edit = get_qs_int('type')
    word = get_qs_str('word')
    
    shop = query_shop(shop_id)
    if is_edit == 0:
        products,total = query_product(shop_id, page, word=word)
    else:
        products, total = query_tb_product(shop_id, page, word=word)

    data = {'shop':shop, 'product':products, 'total':total}
    return data

@app.route('/query/iproduct', methods=['GET'])
def iproduct():
    shops = allshops()
    cate = category()
    return {'shops':shops, 'cate':cate}

@app.route('/query/product_detail', methods=['GET'])
def product_detail():
    id = get_qs_int('id')

    product = one_product(id)
    brands = get_brands()
    cate = category()
    subcate = sub_category()
    scenes = conf_scenes()
    styles = conf_styles()
    defect = defects()
    elements = element_tags()
    resps = response_tags()
    details, sizes = detail_size(id)
    imgs = pro_img(id)
    places = all_place()
    
    def select_img(key, datas, imgs):
        limgs, simgs = [], set()
        if not datas:
            return imgs
        for img in datas['imgs']:
            simgs.add(img['url'])
        for img in imgs:
            if img['url'] in simgs:
                img[key] = 1
            limgs.append(img)
        return limgs
    imgs = select_img('ds', details, imgs)
    imgs = select_img('ss', sizes, imgs)

    product['title'] = product['name']

    data = {
        'product':product,
        'brands':brands,
        'cate':cate,
        'scene':scenes,
        'style':styles,
        'defect':defect,
        'elements':elements,
        'resps':resps,
        'details':details,
        'sizes':sizes,
        'imgs':imgs,
        'place':places,
        'subcate':subcate
    }
    return data

@app.route('/query/before_edit', methods=['GET'])
def before_edit():
    pro_id = get_qs_int('pro_id')

    sql = ('select id, webSite, is_edit from tb_sourse_product where id=%s')
    row = app.db.query_single(sql, (pro_id,))
    if not row or not row[0]:
        return make_err(-1, '该商品尚未存在')
    print('isedit:', row[2])
    data = {}
    data['url'] = row[1]
    data['isedit'] = row[2]
    if data['isedit'] == 1:
        sql = ('select id from tb_product where source_id=%s')
        row = app.db.query_single(sql, (pro_id,))
        if not row or not row[0]:
            data['isedit'] == 0
            sql = ('update tb_sourse_product set is_edit=0 where id=%s')
            app.db.execute(sql, (pro_id,))
    return data

@app.route('/query/product_entry', methods=['GET'])
def product_entry():
    cate = category()
    subcate = sub_category()
    scenes = conf_scenes()
    styles = conf_styles()
    defect = defects()
    resps = response_tags()
    elements = element_tags()
    brands = get_brands()
    places = all_place()

    data = {
        'product':None,
        'imgs': None,
        'cate':cate,
        'scene':scenes,
        'style':styles,
        'defect':defect,
        'resps':resps,
        'elements':elements,
        'brands':brands,
        'place':places,
        'subcate':subcate
    }
    return data

@app.route('/query/product_change', methods=['GET'])
def product_change():
    id = get_qs_int('id')
    product = one_tb_product(id)
    imgs = pro_img(id)
    cate = category()
    subcate = sub_category()
    scenes = conf_scenes()
    styles = conf_styles()
    defect = defects()
    resps = response_tags()
    elements = element_tags()
    brands = get_brands()
    details, sizes = detail_size(id)
    places = all_place()

    if not product:
        return make_err(-1, "商品数据错乱，需要重置sourse表的状态，请将pro_id告知后台, pro_id:%d" % id)

    def select_it(items, val):
        if not val:
            return items
        for item in items:
            item['select'] = 1 if int(item['id']) == int(val) else 0
        return items

    cate = select_it(cate, product['cate'])
    brands = select_it(brands, product['brand'])
    places = select_it(places, product['place'])

    subcate_id = app.redis.get('match::subcategory::%s' % product['id'])
    if isinstance(subcate_id, bytes):
        subcate_id = subcate_id.decode('utf-8')
    subcate = select_it(subcate, subcate_id)

    scenesed  = get_proid_tags('match','scene', product['id'])
    stylesed  = get_proid_tags('match','style', product['id'])
    respsed   = get_proid_tags('resp','resp',   product['id'])
    defectsed = get_proid_tags('resp','defect', product['id'])
    elementsed= get_proid_tags('resp','elem',   product['id'])

    def select_multi(srcs, dests):
        if len(dests) == 0:
            return srcs
        for src in srcs:
            src['select'] = 1 if str(src['id']) in dests else 0
        return srcs
    scenes  = select_multi(scenes, scenesed)
    styles  = select_multi(styles, stylesed)
    defect  = select_multi(defect, defectsed)
    resps   = select_multi(resps, respsed)
    elements= select_multi(elements, elementsed)

    def select_img(key, datas, imgs):
        limgs, simgs = [], set()
        if not datas:
            return imgs
        for img in datas['imgs']:
            simgs.add(img['url'])
        for img in imgs:
            if img['url'] in simgs:
                img[key] = 1
            limgs.append(img)
        return limgs
    imgs = select_img('ds', details, imgs)
    imgs = select_img('ss', sizes, imgs)

    data = {
        'product':product,
        'imgs': imgs,
        'cate':cate,
        'scene':scenes,
        'style':styles,
        'defect':defect,
        'resps':resps,
        'elements':elements,
        'brands':brands,
        'details':details,
        'sizes':sizes,
        'place':places,
        'subcate':subcate
    }

    return data

@app.route('/query/add_product', methods=['POST'])
def add_product():
    try:
        source_id= request.form['source_id']
        shop_id = request.form['shop_id']
        shoptype= request.form['shop_type']
        title   = request.form['title']
        name    = request.form['name']
        op      = float(request.form['op'])
        np      = float(request.form['np'])
        brand   = request.form['brand']
        type    = request.form['cate']
        desc    = request.form['desc']
        pro_url = request.form['pro_url']
        main_img = request.form['main_img'].replace('http:////', 'http://')
        place = request.form['place']
        subcate = request.form['subcate']
        cash_back= request.form['cashback']
        can_try = request.form['cantry']
        profit = request.form['profit']
        word = request.form['word']
        elements  = request.form['elem_ids']
        defects   = request.form['defect_ids']
        scenes = request.form['scene_ids']
        styles = request.form['style_ids']
        resps  = request.form['resp_ids']
    except Exception as ex:
        print(ex)
        return make_err(-1, '输入参数有误, %s' % str(ex))

    code, is_new = gen_code(), True
    if int(source_id) < 0: #手动新增，不是来自爬取
        sql = ( 'insert into tb_sourse_product (shop_id, category_id, name, old_price, now_price,'
                'desc_text, webSite) values(%s, %s, %s, %s, %s, %s, %s)')
        args = (shop_id, type, title, op, np, desc, code)
        row  = app.db.execute(sql, args)
        
        sql = ('select id from tb_sourse_product where webSite=%s')
        row = app.db.query_single(sql, (code,) )
        source_id = int(row[0])
        
    else:
        sql = 'select id, category_id from tb_product where source_id=%s'
        row = app.db.query_single(sql, (source_id, ) )
        if row and row[0]: #如果商品存在，判断所有的标签是否有变更，有的话需要先删除
            pro_id = row[0]
            #正向索引不需处理，因为在重新写入redis前会将正向索引的key先删掉再插入，主要处理反向索引
            #这里有优化的空间
            app.redis.srem('match::category::tag::%s' % row[1], int(row[0]))
            srem_tag('match','scene', pro_id)
            srem_tag('match','style', pro_id)
            srem_tag('resp','resp', pro_id)
            srem_tag('resp','defect', pro_id)
            srem_tag('resp','elem', pro_id)

            subcate_id = app.redis.get('match::subcategory::%s' % pro_id)
            if isinstance(subcate_id, bytes):
                subcate_id = subcate_id.decode('utf-8')
            print('subcate:%s' % subcate_id)
            if subcate_id:
                app.redis.srem('match::subcategory::tag::%s' % subcate_id, pro_id)
                print('match::subcategory::tag::%s' % subcate_id, pro_id)

            is_new = False
    sql_list = []
    if is_new:
        sql = ( 'insert into tb_product (`code`, `shop_id`,`source_id`,source_type,`title`,`name`,`category_id`,'
                '`brand`,`desc_text`,`original_price`,`price`, place, cash_back, can_try, profit, word, `create_time`) values'
                '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())')
        args = (code, shop_id, source_id, shoptype, title, name, type, brand, desc, op, np, place, cash_back, can_try, profit, word)
    else:
        sql = ( 'update tb_product set title=%s,name=%s, category_id=%s, brand=%s, desc_text=%s, original_price=%s, price=%s, '
                'place=%s, cash_back=%s, can_try=%s, profit=%s, word=%s,create_time=NOW() where source_id=%s')
        args = (title, name, type, brand, desc, op, np, place, cash_back, can_try, profit, word, source_id)
    
    print(sql % args)
    sql_list.append( (sql, args) )

    sql = ('update tb_sourse_product set is_edit=1 where id=%s and is_edit=0;')
    sql_list.append( (sql, (source_id,) ) )
    rows = app.db.execute_transaction(sql_list)
    if not rows:
        return make_err(-1, '数据库更新失败')

    sql = ('select id from tb_product where source_id=%s')
    row = app.db.query_single(sql, (source_id,) )
    if not row:
        return make_err(-1, '数据库更新失败')
    id = row[0]
    ret = add_to_redis(int(id), type, subcate, scenes, styles, resps, defects, elements, None, None)
    rows = set_sku(id, shop_id, source_id, title, np, code)
    return {'source_id':source_id, 'pro_id':id}

@app.route('/query/up_detail_sizes', methods=['POST', 'GET'])
def up_detail_sizes():
    try:
        pro_id = request.form['pro_id']
        shop_id = request.form['shop_id']
        detail_desc = request.form['detail_desc']
        sizes_desc  = request.form['sizes_desc']
        detail_imgs = request.form['detail_imgs']
        sizes_imgs  = request.form['sizes_imgs']
    except:
        return make_err(-1, "传入参数有误")

    if int(pro_id) < 0:
        return  make_err(-1, '请先完成商品的基本信息')

    shop = query_shop(shop_id)
    if shop and shop['shop_type'] != 0:
        make_err(-1, '店铺非自营，无需修改详情内容')
    dimgs, simgs = [], []
    if detail_imgs:
        dimgs = due_imgs(detail_imgs.split(' '), pro_id, shop_id, 'detail')
    if sizes_imgs:
        simgs = due_imgs(sizes_imgs.split(' '), pro_id, shop_id, 'size')

    dattr = update_pro_ds(pro_id, shop_id, 'detail', detail_desc, dimgs)
    sattr = update_pro_ds(pro_id, shop_id, 'size', sizes_desc, simgs)

    data = {'details':dattr, 'sizes':sattr}
    return data

@app.route('/query/product_img', methods=['POST', 'GET'])
def product_img():
    pro_id  = get_qs_int('id')
    shop_id = get_qs_int('shop_id')
    up_type = get_qs_str('type')

    try:
        img_file = request.files['pro_%s' % up_type ]
        desc = request.form['%s-desc' % up_type ].replace("\n","").replace(' ', '')
    except:
        return make_err(-1,'无法获取图片参数')
    if not desc:
        desc = ''
    
    qiniu = QiNiu()
    ret, url, (w,h) = qiniu.upload(pro_id, shop_id, "%s" % up_type, img_file)
    print(url)
    if ret == -1:
        return make_err(ERR_GET_CODE, url)

    sql = 'select '+up_type+'_text from tb_product where source_id=%s'
    row = app.db.query_single(sql, (pro_id,) )
    if row and row[0]:
        if url in row[0]:
            return make_err(-1, '该图片已上传，无需重复上传')
        attr = json.loads(row[0])
        attr['imgs'].append({'url':url, 'width': w, 'height': h})
        attr['desc'] = desc if desc else attr['desc']
    else:
        attr = {'imgs':[{'url':url, 'width': w, 'height': h}], 'desc':desc}

    attr_str = json.dumps(attr)
    print(attr_str)

    sql = 'insert into tb_product (shop_id, source_id,'+up_type+'_text) values(%s,%s,%s) ON DUPLICATE KEY UPDATE '+up_type+'_text=%s;'
    args = (shop_id, pro_id, attr_str, attr_str)
    try:
        row = app.db.execute(sql, args )
    except Exception as ex:
        print(ex)
        return {'msg':'error'}
    return attr

@app.route('/query/add_pro_img', methods=['GET'])
def add_pro_img():
    source_id = get_qs_int('id')
    shop_id = get_qs_int('shop_id')
    img = get_qs_str('img')

    sql = 'insert into tb_sourse_product_img (shop_id, product_id, url) values(%s, %s, %s)'
    app.db.execute(sql, (shop_id, source_id, img))
    return []

@app.route('/query/upload_img', methods=['POST', 'GET'])
def upload_img():
    pro_id  = get_qs_int('id')
    shop_id = get_qs_int('shop_id')
    up_type = get_qs_str('type')
    try:
        img_file = request.files['pro_%s' % up_type ]
    except:
        return make_err(-1,'无法获取图片参数')
    
    qiniu = QiNiu()
    ret, url, (w,h) = qiniu.upload(pro_id, shop_id, "%s" % up_type, img_file)
    print(url)
    if ret == -1:
        return make_err(ERR_GET_CODE, url)

    sql = ('select id from tb_sourse_product_img where url=%s and shop_id=%s and product_id=%s')
    row = app.db.query_single(sql, (url, shop_id, pro_id))
    if not row:
        sql = ('insert into tb_sourse_product_img (shop_id, product_id, url) values(%s,%s,%s)')
        app.db.execute(sql, (shop_id, pro_id, url))
    else:
        return make_err(-1, "图片已上传过")

    img = {'url':url, 'width': w, 'height': h}

    return img

@app.route('/query/upload_editor_img', methods=['POST'])
def upload_editor_img():
    try:
        img_file = request.files['ipro_img']
    except:
        return make_err(-1,'无法获取图片参数')
    
    qiniu = QiNiu()
    ret, url, (w,h) = qiniu.upload('_', '_', "editor", img_file)
    print(url)
    if ret == -1:
        return make_err(-1, url)
    
    img = {'url':url, 'width': w, 'height': h}
    return img

@app.route('/query/get_sku', methods=['GET'])
def get_sku():
    source_id = get_qs_int('id')
    sql = ('select id from tb_product where source_id=%s')
    row = app.db.query_single(sql, (source_id,))
    if not row or not row[0]:
        return make_err(-1, '请先提交基本信息再设置sku')
    pro_id = int(row[0])
    attrs = logic_get_attrvalue()
    skus = logic_get_sku(pro_id)
    for sku in skus:
        maps = sku['maps'].split('|')
        for one_map in maps:
            key = one_map.split(':')[0]
            attr_id = one_map.split(':')[-1]
            sku[key] = attrs[key][attr_id]

    data = {'skus':skus, 'attrs':attrs}
    return data

@app.route('/query/update_sku', methods=['POST'])
def update_sku():
    try:
        source_id = request.form['id']
        skus    = json.loads(request.form['skus'])
    except:
        return make_err(-1, "传入参数有误")
    
    sql = ('select id, shop_id, title, code from tb_product where source_id=%s')
    row = app.db.query_single(sql, (source_id,))
    if not row or not row[0]:
        return make_err(-1, '请先提交基本信息再设置sku')
    
    pro_id = int(row[0])
    shop_id = int(row[1])
    title = row[2]
    code = row[3]
    sql_list = []
    
    sql = ('delete from tb_sku where product_id=%s')
    sql_list.append((sql, (pro_id,)))
    for sku in skus:
        maps = sku['maps']
        try:
            price = float(sku['price'])
            stock = int(sku['stock'])
        except:
            return make_err(-1, "价格和库存格式错误，须为数字")
        if price < 0 or stock < 0:
            return make_err(-1, "价格和库存不可小于0")
        
        sql = ('insert into tb_sku (product_id, shop_id, name, attr_maps, price,code,stock) '
               'values(%s,%s,%s,%s,%s,%s,%s)')
        args= (pro_id, shop_id, title, maps, price, code, stock)
        sql_list.append((sql, args))

    for sql in sql_list:
        print(sql[0] % sql[1])

    rows = app.db.execute_transaction(sql_list)
    if not rows:
        return make_err(-1, '数据库更新失败')

    data = {'num':rows}
    return data

@app.route('/query/get_match', methods=['GET'])
def get_match():
    source_id = get_qs_int('id')
    sql = ('select id from tb_product where source_id=%s')
    row = app.db.query_single(sql, (source_id,))
    if not row or not row[0]:
        return make_err(-1, '请先提交基本信息再设置搭配')

    pro_id = int(row[0])
    match = ProMatch(pro_id)

    match_ids = match.get_match()
    if len(match_ids) == 0:
        return []
    
    sql = ( 'select id,shop_id, title, brand, category_id,desc_imgs, original_price, price,'
            'source_id  from tb_product where id in (%s) order by id desc')
    args = ','.join(match_ids)
    sql = sql % args
    return tb_products(sql, None)

@app.route('/query/update_match', methods=['POST'])
def update_match():
    try:
        source_id = request.form['id']
        choose_ids= set(json.loads(request.form['choose_list']))
    except:
        return make_err(-1, "传入参数有误")
    
    sql = ('select id from tb_product where source_id=%s')
    row = app.db.query_single(sql, (source_id,))
    if not row or not row[0]:
        return make_err(-1, '请先提交基本信息再设置搭配')

    pro_id = int(row[0])
    match = ProMatch(pro_id)
    match.update_match(choose_ids)
    
    return []

@app.route('/query/account', methods=['GET'])
def account():
    catedict = cate_dict()
    total, cates = 0, []
    sql = ('select category_id, count(category_id) from tb_product where category_id group by category_id')
    rows = app.db.query_multi(sql)
    for cate_id, num in rows:
        total += num
        cates.append({'type': catedict[int(cate_id)], 'num': num})

    scene = conf_scenes()
    style = conf_styles()

    scenes, styles = [], []
    for sc in scene:
        key = 'match::scene::tag::%s' % sc['id']
        item = {}
        item['type'] = sc['name']
        item['num'] = app.redis.scard(key)
        scenes.append(item)

    for st in style:
        key = 'match::style::tag::%s' % st['id']
        item = {}
        item['type'] = st['name']
        item['num'] = app.redis.scard(key)
        styles.append(item)
    
    return {'total':total, 'cates':cates, 'styles':styles, 'scenes':scenes}

@app.route('/query/uptoken', methods=['OPTIONS', 'GET'])
def uptoken():
    if request.method == 'OPTIONS':
        return []
    qiniu = QiNiu()
    uk = qiniu.get_token()
    return {'uk': uk}

@app.route('/query/magazine', methods=['GET'])
def magazine():
    page = get_qs_int('page')
    limit = get_qs_int('limit')
    start = (page-1)*limit

    sql = 'select id, issue_id, title, cover_img, details, create_time, status from tb_magazine where type=2 order by id desc limit %s, %s'
    rows = app.db.query_multi(sql, (start, limit))

    magazines, total = [], 0
    for id, issue_id, title, cover_img, details, create_time, status in rows:
        item = {}
        item['id'] = id
        item['issue'] = issue_id
        item['title'] = title
        item['cover'] = cover_img
        item['details'] = details
        item['create_time'] = create_time.strftime('%Y-%m-%d %H:%M:%S')
        item['status'] = status
        magazines.append(item)

    sql = 'select count(id) from tb_magazine where type=2'
    row = app.db.query_single(sql)
    if row:
        total = row[0]
    return {'magazines':magazines, 'total':total}

@app.route('/query/change_magazine_status', methods=['GET'])
def change_magazine_status():
    id = get_qs_int('id')
    status = get_qs_int('status')

    sql = 'update tb_magazine set status=%s where id=%s'
    row = app.db.execute(sql, (status, id))
    return {'row':row}

@app.route('/query/update_magazine', methods=['GET'])
def update_magazine():
    id = get_qs_int('id')
    title = get_qs_str('title')
    url = get_qs_str('url')
    cover = get_qs_str('img')

    sql = 'update tb_magazine set title=%s, details=%s, cover_img=%s where id=%s'
    row = app.db.execute(sql, (title, url, cover, id))
    return {'row':row}

@app.route('/query/del_magazine', methods=['GET'])
def del_magazine():
    id = get_qs_int('id')

    sql = 'delete from tb_magazine where id=%s' 
    row = app.db.execute(sql, (id,))
    return {'row':row}

@app.route('/query/add_magazine', methods=['GET'])
def add_magazine():
    title = get_qs_str('title')
    url = get_qs_str('url')
    cover = get_qs_str('img')
    sql = 'select max(issue_id) from tb_magazine'
    issue, row = 1, app.db.query_single(sql)
    if row and row[0]:
        issue = row[0]+1

    sql = ('insert into tb_magazine (issue_id, title, cover_img, type, details, create_time, status)'
            'values(%s, %s, %s, 2, %s, NOW(), 0)')
    row = app.db.execute(sql, (issue, title, cover, url))
    return {'row':row}

@app.route('/query/update_formal_magazine', methods=['GET'])
def update_formal_magazine():
    id = get_qs_int('id')
    sql = 'select title, cover_img, type, details, status, issue_id from tb_magazine where id=%s'
    mgz = app.db.query_single(sql, (id,))
    
    host = get_cfg().get_str('formal_mysql', 'ip')
    port = get_cfg().get_int('formal_mysql', 'port')
    usr = get_cfg().get_str('formal_mysql', 'user')
    pwd = get_cfg().get_str('formal_mysql', 'passwd')
    dbname = get_cfg().get_str('formal_mysql', 'dbname')
    f_db = DBUtils(host, port, usr, pwd, dbname)
    sql = 'select id from tb_magazine where issue_id=%s' 
    row = f_db.query_single(sql, (mgz[5],))
    if row and row[0]:
        sql = ('update tb_magazine set title=%s, cover_img=%s, type=%s, details=%s, '
                'status=%s where issue_id=%s')
        row = f_db.execute(sql, mgz)
    else:
        sql = ('insert into tb_magazine (title, cover_img, type, details, status, issue_id,'
                ' create_time) values(%s, %s, %s, %s, %s, %s, NOW())')
        row = f_db.execute(sql, mgz)

    return {'row':row}


#标签相关
@app.route('/tag/add_tag', methods=['POST'])
def add_tag():
    try:
        resps  = request.form['resp'].replace("\n", "").replace("\r", "")
        elements= request.form['element'].replace("\n", "").replace("\r", "")
    except:
        return make_err(-1, '传入参数有误')
    print(elements)
    if not resps and not elements:
        return make_err(-1, '没有标签需要插入')

    def need_add_list(tb_name, datas):
        args, args_set = [], set()
        items = datas.split(" ")
        for item in items:
            if not item:
                continue
            args_set.add( (item, ) )
        args = list(args_set)
        sql = 'select name from %s' % tb_name
        rows = app.db.query_multi(sql)
        if rows:
            tmp_set = set()
            for arg in args_set:
                if arg in rows:
                    continue
                tmp_set.add(arg)
            args = list(tmp_set)
        if args:
            sql = 'insert into '+tb_name+' (name) values (%s)'
            rows = app.db.execute_many(sql, args)
        return args

    resp_args = need_add_list('tb_response_tag', resps)
    elem_args = need_add_list('tb_element_tag', elements)
    if not resp_args and not elem_args:
        return make_err(-1, '标签已存在不需重复插入')

    return get_tag()

@app.route('/tag/change_tag', methods=['GET'])
def change_tag():
    id = get_qs_int('id')
    type = get_qs_int('type')
    word = get_qs_str('word')
    
    tb_name = 'tb_response_tag'
    if type == 1:
        tb_name = 'tb_element_tag'

    sql = ('update '+tb_name+' set name=%s where id=%s')
    row = app.db.execute(sql, (word, id))
    data = {'num':row}
    return data

@app.route('/tag/get_tag', methods=['GET'])
def get_tag():
    resps, elements = [], []

    sql = 'select id, name from tb_response_tag'
    rows = app.db.query_multi(sql)
    if not rows:
        return make_err(-1, "无标签")
    for id, name in rows:
        resps.append({'id':id , 'name':name})

    sql = 'select id, name from tb_element_tag'
    rows = app.db.query_multi(sql)
    if not rows:
        return make_err(-1, "无标签")
    for id, name in rows:
        elements.append({'id':id, 'name':name})

    data = { 'resp':resps, 'element':elements }
    return data

@app.route('/tag/del_tag', methods=['GET'])
def del_tag():
    ids = get_qs_str('ids')
    type = get_qs_int('type')
    if not ids:
        return make_err(-1, '标签为空')
    items = ids.split('|')

    tb_name = 'tb_response_tag'
    if type == 1:
        tb_name = 'tb_element_tag'

    sql = 'select id from %s' % tb_name
    rows = app.db.query_multi(sql)
    if not rows:
        return make_err(-1, "无标签")

    del_set = set()
    for item in items:
        if (int(item),) not in rows:
            continue
        del_set.add( (int(item),)  )

    if not len(del_set):
        return make_err(-1, '已删除，无需重复删除')

    sql = 'delete from '+tb_name+' where id=%s'
    rows = app.db.execute_many(sql, list(del_set) )
    if not rows:
        return make_err(-1, '删除标签失败')
    data = {'msg':'success'}
    return data

@app.route('/tagword/word', methods=['GET'])
def tagwords():
    rwords = resp_tag_words()
    ewords = elem_tag_words()
    resps = response_tags()
    elements = element_tags()
    defect_list = defects()
    scenes = conf_scenes()
    styles = conf_styles()
    data = {'rwords': rwords, 'ewords': ewords,
            'elem':elements, 'defect':defect_list,
            'resp':resps, 'scene':scenes, 'style':styles,
    }
    return data

@app.route('/tagword/ewords', methods=['GET'])
def ewords():
    defect_id = get_qs_int('defect_id')
    elem_id = get_qs_int('elem_id')
    sql = ('select id, word from tb_element_tag_word where elem_id=%s and defect_id=%s')
    rows = app.db.query_multi(sql, (elem_id, defect_id))
    data = []
    for id, word in rows:
        data.append({'id':id, 'word':word})
    return data

@app.route('/tagword/rwords', methods=['GET'])
def rwords():
    resp_id = get_qs_int('resp_id')
    scene_id = get_qs_int('scene_id')
    style_id = get_qs_int('style_id')
    sql = ('select id, word from tb_response_tag_word where resp_id=%s and scene_id=%s and style_id=%s')
    rows = app.db.query_multi(sql, (resp_id, scene_id, style_id))
    data = []
    for id, word in rows:
        data.append({'id':id, 'word':word})
    return data

@app.route('/tagword/del_word', methods=['GET'])
def del_word():
    id = get_qs_int('id')
    type = get_qs_int('type')
    if type == 0:
        tb_name = 'tb_element_tag_word'
    elif type == 1:
        tb_name = 'tb_response_tag_word'
    else:
        return make_err(-1, "未定义类型")

    sql = 'delete from '+tb_name+' where id=%s'
    row = app.db.execute(sql, (id,) )
    if not row:
        return make_err(-1, '删除数据失败')
    print(row)
    data = {'msg':'删除数据成功'}
    return data

@app.route('/tagword/add_respword', methods=['POST'])
def add_respword():
    try:
        resp_id = request.form['resp_id']
        scene_id = request.form['scene_id']
        style_id = request.form['style_id']
        word   = request.form['words']
    except:
        return make_err(-1, "传入参数有误")
    if not word:
        return make_err(-1, '包装词不能为空')
    sql = 'insert into tb_response_tag_word (resp_id, scene_id, style_id, word) values(%s,%s,%s,%s)'
    row = app.db.execute(sql, (resp_id, scene_id, style_id, word) )
    if not row:
        return make_err(-1, "插入数据失败")
    sql = 'select id, word from tb_response_tag_word where resp_id=%s and scene_id=%s and style_id=%s and word=%s'
    row = app.db.query_single(sql, (resp_id, scene_id, style_id, word))

    return {'id':row[0], 'word':row[1]}

@app.route('/tagword/add_elemword', methods=['POST'])
def add_elemword():
    try:
        elem_id = request.form['elem_id']
        defect_id = request.form['defect_id']
        word = request.form['words']
    except:
        return make_err(-1, "传入参数有误")
    if not word:
        return make_err(-1, '包装词不能为空')

    sql = 'insert into tb_element_tag_word (elem_id, defect_id, word) values(%s,%s,%s)'
    row = app.db.execute(sql, (elem_id, defect_id, word) )
    if not row:
        return make_err(-1, "插入数据失败")

    sql = 'select id, word from tb_element_tag_word where elem_id=%s and defect_id=%s and word=%s'
    row = app.db.query_single(sql, (elem_id, defect_id, word))
    data = {'id':row[0], 'word':row[1]}
    return data

@app.route('/tagword/update_word', methods=['POST'])
def update_respword():
    try:
        word_id = request.form['word_id']
        resp_id = request.form['resp_id']
        scene_id = request.form['scene_id']
        style_id = request.form['style_id']
        word = request.form['words']
    except:
    	return make_err(-1, "传入参数有误")

    if not word:
    	return make_err(-1, " 包装词不能为空")

    sql = 'update tb_response_tag_word set resp_id=%s, scene_id=%s, style_id=%s, word=%s where id=%s'
    row = app.db.execute(sql, (resp_id, scene_id, style_id, word, word_id))
    if not row:
    	return make_err(-1, "更新数据失败")
    data = {'msg':'更新数据成功'}
    return data

@app.route('/tagword/update_elemword', methods=['POST'])
def update_elemword():
	try:
		word_id = request.form['word_id']
		ele_id = request.form['ele_id']
		defect_id = request.form['defect_id']
		word = request.form['words']
	except:
		return make_err(-1, "传入参数有误")
	if not word:
		return make_err(-1, "包装词不能为空")

	sql = 'update tb_element_tag_word set elem_id=%s, defect_id=%s, word=%s where id=%s'
	row = app.db.execute(sql, (ele_id, defect_id, word, word_id))
	if not row:
		return make_err(-1, "更新数据失败")
	data = {'msg':'更新数据成功'}
	return data

@app.route('/query/del_pro_img', methods=['GET'])
def del_pro_img():
    id = get_qs_int('id')

    sql = 'delete from tb_sourse_product_img where id=%s'
    row = app.db.execute(sql, (id,))
    return {}
    
if __name__ == '__main__':
    print("开始执行")
    app.run(host='0.0.0.0', port = 86, debug=True)
