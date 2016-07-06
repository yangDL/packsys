var edit = {
    source_id: 0,
    shop_id:0,
    url:'',
    is_edit:0,
    subcate: {},
    gen_subcate: function(){
        var cate_id = $('#pro-cate').val(), code = '';
        for (var i in edit.subcate){
            var obj = edit.subcate[i];
            if(obj.cate_id == cate_id){
                if (obj.select && obj.select == 1)
                    code += '<option value="' + obj.id + '" selected>' + obj.name + '</option>';
                else
                    code += '<option value="' + obj.id + '">' + obj.name + '</option>';
            }   
        }
        $('#pro-subcate').html(code);
    },
    show_base: function(pro){
        $('#pro-cashback').attr('value', '0');
        pro.details && $('#detail-desc').val(pro.details.desc);
        if(pro.product){
            var rpro = pro.product;
            $('#pro-title').attr('value', rpro.title);
            $('#edit-title').text(rpro.title).attr('href', edit.url);
            $('#pro-name').attr('value', rpro.name);
            $('#pro-op').attr('value', rpro.op);
            $('#pro-np').attr('value', rpro.np);
            $('#pro-word').attr('value', rpro.word);
            if(rpro.cash_back)
                $('#pro-cashback').attr('value',parseFloat(rpro.cash_back / 100).toFixed(2) );
            if(rpro.profit)
                $('#pro-profit').attr('value', parseFloat(rpro.profit / 100).toFixed(2) );
            $('#pro-cantry').attr('value', rpro.can_try);
        }
        var brand_options = '';
        for (var i in pro.brands) {
            var obj = pro.brands[i];
            if (obj.select && obj.select == 1)
                brand_options += '<option value="' + obj.id + '" selected>' + obj.ch + '(' + obj.en + ')</option>';
            else
                brand_options += '<option value="' + obj.id + '">' + obj.ch + '(' + obj.en + ')</option>';
        }
        
        $('#pro-brand').html(brand_options);
        $('#match-brand').html(brand_options);
        function select_it(_id, datas){
            if(!datas)
                return false;
            datas.sort(function(a,b){
                return (a.name).localeCompare((b.name));
            });
            var options = '<option value="0">请选择</option>';
            for (var i in datas){
                var obj = datas[i], sect = obj.select == 1 ? 'selected' : '';
                options += '<option value="' + obj.id + '" '+sect+'>' + obj.name + '</option>';
            }
            $('#'+_id).append(options);
        };
        select_it('pro-place', pro.place);
        select_it('pro-cate', pro.cate);
        edit.gen_tag_list('tag-scene', pro.scene);
        edit.gen_tag_list('tag-style', pro.style);
        edit.gen_tag_list('tag-element', pro.elements);
        edit.gen_tag_list('tag-defect', pro.defect);
        edit.gen_tag_list('tag-resp', pro.resps);
        pro.product && $('#pro-desc').attr('value', rpro.desc);
        $('#pro-cate').change();
        $('#pro-defect').change();
        $('#pro-scene').change();
        
        select_it('match-cate', pro.cate);
        select_it('match-scene', pro.scene);
        select_it('match-style', pro.style);
        select_it('match-defect', pro.defect);
    },
    gen_tag_list: function(_id, datas){
        if(!datas) return false;
        datas.sort(function(a,b){
            return (a.name).localeCompare((b.name));
        });
        var lis = [];
        for( var i in datas){
            var obj = datas[i], cls = obj.select == 1 ? 'class="selected"' : 'class=""';
            lis.push('<li '+cls+' data-id="'+obj.id+'">'+obj.name+'</li>');
        }
        $('#'+_id).html(lis.join(''));
        $('#'+_id+' li').unbind('click').click(function(){
            $(this).is('.selected') ? $(this).removeClass('selected') : $(this).addClass('selected');
        });
    },
    gen_select_tag: function(id){
        var word_list = [];
        $('#'+id+' li.selected').each(function(){
            word_list.push($(this).attr('data-id'));
        });
        return word_list.join(',');
    },
    update_base: function() {
        var title = util.get_val('pro-title');
        var name = util.get_val('pro-name');
        var desc = util.get_val('pro-desc');
        var op = util.get_val('pro-op');
        var np = util.get_val('pro-np');
        var brand = $("#pro-brand option:selected").val();
        var place = $("#pro-place option:selected").val();
        var cate = $("#pro-cate option:selected").val();
        var subcate = $("#pro-subcate option:selected").val();
        var word = $('#pro-word').val();
        if(!name) name = title;
        if(cate == 0 || subcate == 0){
            util.alert('请选择商品分类和子分类');
            return false;
        }
        if (!(title && op && np && cate && brand && desc && word)) {
            util.alert('参数输入不全');
            return false;
        }
        var cashback = $('#pro-cashback').val();
        var profit = $('#pro-profit').val();
        if(!util.is_float(cashback) || !util.is_float(profit)){
            util.alert('推广佣金和利润必须为整数或小数');
            return false;
        }
        var cantry = $('#pro-cantry').val();
        elem_ids = edit.gen_select_tag('tag-element');
        defect_ids = edit.gen_select_tag('tag-defect');
        scene_ids = edit.gen_select_tag('tag-scene');
        style_ids = edit.gen_select_tag('tag-style');
        resp_ids = edit.gen_select_tag('tag-resp');
        pro_url = '', main_img = '';
        
        var data = {
            source_id: edit.source_id,
            shop_id: edit.shop_id,
            shop_type: edit.shop_type || 0,
            title: title,
            name: name,
            op: op,
            np: np,
            brand: brand,
            cate: cate,
            subcate:subcate,
            desc: desc,
            pro_url: pro_url,
            main_img : main_img,
            place:place,
            cashback: cashback * 100,
            cantry: cantry,
            profit: profit * 100,
            word:word,
            elem_ids:elem_ids,
            defect_ids:defect_ids,
            scene_ids:scene_ids,
            style_ids:style_ids,
            resp_ids:resp_ids
        };
        util.ajax({
            method:'post',
            url:'/query/add_product',
            data:data,
            success: function(datas, status){
                util.alert('更新<b style="color:red;">'+data.title+'</b>成功');
                edit.id = datas.data.source_id;
                
            }
        })
    },
    img_select_list : function(_id){
        var imglist = [];
        $('.'+_id+' li').each(function(){
            if($(this).is('.select')){
                imglist.push($(this).children('img').attr('src'));
            }
        });
        return imglist;
    },
    update_ds : function(){
        if(edit.source_id < 0){
            util.alert('请先提交完成基本信息');
            return;
        }
        var detail_desc = util.get_val('detail-desc');
        var size_desc = util.get_val('size-desc') || '';
        var dimgs = edit.img_select_list('upload-detail');
        var simgs = edit.img_select_list('upload-size');
        if (dimgs.length == 0 || detail_desc == false){
            util.alert('商品详情介绍不能为空，商品图片至少一张');
            return false;
        }
        var data = {
            pro_id: edit.source_id,
            shop_id: edit.shop_id,
            detail_desc : detail_desc,
            sizes_desc : size_desc, 
            detail_imgs : dimgs.join(' '),
            sizes_imgs : simgs.join(' ')
        };
        $('#product-ds').attr('disabled', 'disabled');
        $('#product-ds').text('上传中...');
        util.ajax({
            method:'post', 
            url:'/query/up_detail_sizes', 
            data:data, 
            success:function(datas, status){
                util.alert('更新详情信息成功');
            },
            complete: function(){
                $('#product-ds').attr('disabled', false);
                $('#product-ds').text('提交详情信息');
            }
        });
    },
    show_img: function(imgs){
        var detail_lis = [], size_lis = [];
        var select_code = '<li href="javascript:;" class="thumbnail select"><img src="{url}" data-id="{id}"/></li>';
        var unsele_code = '<li href="javascript:;" class="thumbnail"><i class="icon-remove-sign img-delete"></i><img src="{url}" data-id="{id}"/></li>';
        for (var i in imgs){
            var obj = imgs[i];
            if(i == 0)
                $('#show-mainimg').prepend('<img src="'+obj.url+'" width="100%">');
            obj.ds == 1 ? detail_lis.push(select_code.format(obj)) : detail_lis.push(unsele_code.format(obj));
            obj.ss == 1 ? size_lis.push(select_code.format(obj)) : size_lis.push(unsele_code.format(obj));
        }
        $('.upload-detail').prepend(detail_lis.join(''));
        $('.upload-size').prepend(size_lis.join(''));
        edit.img_op();
    },
    
    edit_product: function(){
        console.log('edit');
        util.ajax({
            method: 'get',
            url:'/query/product_detail',
            data: {id:edit.source_id},
            success: function(datas, status){
                var pro = datas.data;
                edit.subcate = pro.subcate;
                edit.show_base(pro);
                edit.show_img(pro.imgs);
                //product.insert_img('detail', datas.details);
                //product.insert_img('sizes', datas.sizes);
            }
        })
    },
    change_product:function(){
        util.ajax({
            method: 'get',
            url:'/query/product_change',
            data:{id:edit.source_id},
            success: function(datas, status){
                var pro = datas.data;
                edit.subcate = pro.subcate;
                edit.show_base(pro);
                edit.show_img(pro.imgs);
            }
        })
    },
    entry_product: function(){
        util.ajax({
            method: 'get',
            url: '/query/product_entry',
            data:{},
            success: function(datas, status){
                var pro = datas.data;
                edit.subcate = pro.subcate;
                edit.show_base(pro);
                edit.show_img({});
            }
        });
    },
    img_op: function(){
        $('.pro-imgs img').off();
        $('.pro-imgs img').click(function(){
            var $par = $(this).parent();
            $par.is('.select') ? $par.removeClass('select') : $par.addClass('select');
        });
        $('.img-delete').off();
        $('.img-delete').click(function(){
            var id = $(this).next().attr('data-id'), self = this;
            var code = '<div style="text-align:center;"><img src="'+$(this).next().attr('src')+'" width=100>' + '<br>您将删除该图片，是否继续</div>';
            util.dialog('删除图片', code, function(){
                util.ajax({
                    method:'get', 
                    url:'/query/del_pro_img', 
                    data:{id:id}, 
                    success:function(datas,status){
                        $('#cancel-btn').click();
                        $(self).parent().remove();
                        util.alert('删除图片成功');
                    }
                });
            });
        });
        $('.upload-detail').dragsort({
            dragSelector: "li", 
            dragBetween: true, 
        });
    },
    op: function(){
        $('#pro-cate').change(edit.gen_subcate);
        $('#product-base').click(edit.update_base);
        $('#product-ds').click(edit.update_ds);
    },
    add_to_source_img: function(img){
        util.ajax({
            method: 'get',
            url: '/query/add_pro_img',
            data: {id: edit.source_id, shop_id:edit.shop_id, img:img},
            success: function(datas, status){
                console.log('add img success');
            }
        });
    },
    qiniu_init: function(){
        var uploader = Qiniu.uploader({
            runtimes: 'html5,flash,html4',    //上传模式,依次退化
            browse_button: 'upload-file',     //上传选择的点选按钮，**必需**
            uptoken_func: function(){
                var uptoken = '';
                util.ajax({
                    method:'get', async:false, url:'/query/uptoken',
                    success:function(datas,status){uptoken = datas.data.uk;}
                })
                return uptoken;
            },
            domain: 'http://7xrvqr.com1.z0.glb.clouddn.com/',   //bucket 域名，下载资源时用到，**必需**
            get_new_uptoken: false,  //设置上传文件的时候是否每次都重新获取新的token
            max_file_size: '10mb',           //最大文件体积限制
            flash_swf_url: 'plupload/Moxie.swf',  //引入flash,相对路径
            max_retries: 2,                   //上传失败最大重试次数
            dragdrop: true,                   //开启可拖曳上传
            drop_element: 'upload-file',        //拖曳上传区域元素的ID，拖曳文件或文件夹后可触发上传
            chunk_size: '4mb',                //分块上传时，每片的体积
            auto_start: true,                 //选择文件后自动上传，若关闭需要自己绑定事件触发上传
            init: {
                'BeforeUpload': function(up, file) {
                    $('.pro-imgs').append('<li href="javascript:;" class="thumbnail"><img src="{url}"/></li>'.format({url:'img/load.gif'}));
                },
                'FileUploaded': function(up, file, info) {
                    var domain = up.getOption('domain');
                    var res = JSON.parse(info);
                    var sourceLink = domain + res.key;
                    edit.add_to_source_img(sourceLink);
                    $('.upload-detail').children('li:last').children('img').attr('src', sourceLink);
                    $('.upload-size').children('li:last').children('img').attr('src', sourceLink);
                    edit.img_op();
                },
                'Error': function(up, err, errTip) {
                       util.alert('上传图片失败, tip:'+errTip);
                },
            }
        });
    },
    load: function(){
        var sourceid = util.query_string('id');
        var shopid = util.query_string('shopid');
        if (!shopid || !sourceid){
            util.alert("请传入商品id和商店id");
            return false;
        }
        edit.source_id = sourceid;
        edit.shop_id = shopid;
        if(edit.source_id > 0){
            util.ajax({
                mathod: 'get',
                async:false,
                url: '/query/before_edit',
                data: {pro_id:edit.source_id},
                success: function(datas,status){
                    edit.url = datas.data.url;
                    edit.is_edit = datas.data.isedit;
                }
            })
        }else{
            edit.entry_product();
            $('[href="#ds"]').click(function(){
                if(edit.source_id < 0){
                    util.alert('请先完成基本信息，再填写商品详情和尺码');
                    return;
                }
            });
            return;
        }
        edit.is_edit == 0 ? edit.edit_product() : edit.change_product();
        return;
    },
    init: function(){
        edit.load();
        edit.op();
        edit.qiniu_init();
    }
};

var adder = {
    gen_brand_code: function(){
        return template.multiline(function(){/*!@preserve
            <div class="row form-group">
                <div class="col-lg-6 col-md-6">
                    <label>中文名称</label><input type="text" class="form-control" id="brand-ch" placeholder="若无中文名称可与英文一致">
                </div>
            </div>
            <div class="row form-group">
                <div class="col-lg-12 col-md-12">
                    <label>英文名称</label><input type="text" class="form-control" id="brand-en">
                </div>
            </div>
            <div class="row form-group">
                <div class="col-lg-12 col-md-12">
                    <label>品牌介绍</label><textarea row=3 class="form-control" id="brand-desc"></textarea>
                </div>
            </div>
        */});
    },
    gen_tag_code: function(){
        return template.multiline(function(){/*!@preserve
            <div class="row form-group">
                <div class="col-lg-12 col-md-12">
                    <label>元素标签</label><input type="text" class="form-control" id="add-elem-tag" placeholder="多个标签空格分开">
                </div>
            </div>
            <div class="row form-group">
                <div class="col-lg-12 col-md-12">
                    <label>回应标签</label><input type="text" class="form-control" id="add-resp-tag" placeholder="多个标签空格分开">
                </div>
            </div>
        */})
    },
    add_tag: function(){
        var data = {
            element: $('#add-elem-tag').val() || '',
            resp: $('#add-resp-tag').val() || ''
        };
        util.ajax({
            method: 'post',
            url: '/tag/add_tag',
            data:data,
            success: function(datas, status){
                $('#cancel-btn').click();
                elem_ids = adder.gen_tag('tag-element', datas.data.element);
                resp_ids = adder.gen_tag('tag-resp', datas.data.resp);
                edit.gen_tag_list('tag-element', elem_ids);
                edit.gen_tag_list('tag-resp', resp_ids);
                util.alert('标签已添加成功， 已在列表中按拼音字母排序!');
            }
        })
    },
    gen_select_tag: function(id){
        var word_list = [];
        $('#'+id+' li.selected').each(function(){
            word_list.push( parseInt($(this).attr('data-id')) );
        });
        return word_list;
    },
    gen_tag: function(id, datas){
        tag_ids = adder.gen_select_tag(id);
        for(var i in datas){
            var obj = datas[i];
            $.inArray(parseInt(obj.id), tag_ids) == -1 ? obj.select = 0 : obj.select = 1;
        }
        return datas;
    },
    add_brand: function(){
        var data = {
            ch: util.get_val('brand-ch') || '',
            en: util.get_val('brand-en') || '',
            story: util.get_val('brand-desc') || ''
        };
        if (!data.ch && !data.en && !data.story) return;
        util.ajax({
            method: 'post',
            url:'/query/add_brand',
            data:data,
            success: function(datas, status){
                $('#cancel-btn').click();
                var obj = datas.data;
                var opt = '<option value="' + obj.id + '">' + obj.ch + '(' + obj.en + ')</option>';
                $('#pro-brand').append(opt);
                $('#pro-brand').val(obj.id);
                util.alert('品牌<b style="color:red">'+obj.en+'</b>已添加成功!<br><b style="color:blue">品牌选项已更改为该品牌</b>');
            }
        });
    },
    op: function(){
        $('#add-brand').click(function(){
            var code = adder.gen_brand_code();
            util.dialog('添加品牌', code, adder.add_brand);
        });
        $('#add-tag').click(function(){
            var code = adder.gen_tag_code();
            util.dialog('添加标签', code, adder.add_tag);
        })
    }
};

var sku = {
    gen_opts: function(items){
        for (var i in items){
            var item = items[i], lis = [];
            for (var j in item){
                lis.push('<option value="'+j+'">'+item[j]+'</option>');
            }
            $('#sku-'+i).html(lis.join(''));
            lis = [];
        }
    },
    gen_sku_code: function(){
        return template.multiline(function(){/*!@preserve
            <div class="alert alert-{type} col-lg-12 form-group" style="position:relative;" 
                data-map="{maps}" data-price="{price}" data-stock="{stock}">
                <strong class="col-3">颜色 : {1}</strong><strong class="col-3">尺码 : {2}</strong>
                <strong class="col-3">价格 : {price}</strong><strong class="col-3">库存 : {stock}</strong>
                <a href="javascript:;" class="sku-rm"><i class="icon-remove"></i></a>
            </div>
        */}); 
    },
    gen_skus: function(skus){
        var code = sku.gen_sku_code();
        var lis = [];
        for(var i in skus){
            var obj = skus[i];
            obj.type = i % 2 == 0 ? 'info' : 'success';
            lis.push(code.format(obj));
        }
        $('#sku-list').html(lis.join(''));
        $('.sku-rm').unbind('click').click(function(){
            var $par = $(this).parent();
            $par.fadeOut(500, function(){$par.remove();});
        });
    },
    gen_sku: function(obj){
        var code = sku.gen_sku_code();
        obj.type = 'danger';
        $('#sku-list').append(code.format(obj));
        $('.sku-rm').unbind('click').click(function(){
            var $par = $(this).parent();
            $par.fadeOut(500, function(){$par.remove();});
        });
    },
    get: function(){
        util.ajax({
            method: 'get',
            url: '/query/get_sku',
            data: {id : edit.source_id},
            success: function(datas, status){
                var skus = datas.data;
                sku.gen_opts(skus.attrs);
                sku.gen_skus(skus.skus);
            }
        })
    },
    gen_sku_list: function(){
        var items = [];
        $('#sku-list .alert').each(function(){
            var item = {};
            item['maps'] = $(this).attr('data-map');
            item['price'] = $(this).attr('data-price');
            item['stock'] = $(this).attr('data-stock');
            items.push(item);
        });
        return items;
    },
    op: function(){
        $('[href="#sku"]').click(function(){
            if(edit.source_id < 0){
                util.alert('请先完成基本信息，再填写sku信息');
                return;
            }
            sku.get();
        });
        $('#add-sku').click(function(){
            var data = {
                color: util.get_val('sku-1'),
                size : util.get_val('sku-2'),
                1: $('#sku-1').find('option:selected').text() || '',
                2: $('#sku-2').find('option:selected').text() || '',
                price: util.get_val('sku-price') || 0,
                stock: util.get_val('sku-stock') || 0
            };
            for (var i in data)
                if (!data[i]) return false;
            data.maps = '1:{color}|2:{size}'.format(data);
            sku.gen_sku(data);
        });
        $('#product-sku').click(function(){
            var sku_list = sku.gen_sku_list();
            if(sku_list.length < 1){
                util.alert('无sku信息、无需提交');
                return;
            }
            util.ajax({
                method: 'post',
                url: '/query/update_sku',
                data: {id:edit.source_id, skus: JSON.stringify(sku_list)},
                success: function(datas, status){
                    util.alert('更新sku信息成功');
                    $('[href="#sku"]').click();
                }
            });
        })
    },
    init: function(){
        sku.op();
    }
};

var match = {
    pages: {
        page:1,
        limit:5
    },
    gen_search: function(searchs, total){
        $('#match-list').html('');
        var trs = [];
        for (var i in searchs){
            var obj = searchs[i];
            var code = template.multiline(function(){/*!@preserve
                <tr data-id="{id}">
                    <td><img src="{img}" width="80px"></td><td>{id}</td><td>{title}</td>
                    <td>{shop}</td><td>{brand}</td><td>{cate}</td><td>{np}</td>
                    <td>
                        <a href="javascript:;" class="add-match">加入搭配</a>
                        <a class="view" target="_blank" href="http://dev.naonaome.com/pro?proid={id}">预览</a>
                    </td>
                </tr>
            */}).format(obj);
            trs.push(code);
        }
        $('#match-list').html(trs.join(''));
        util.paging(total, match.pages, 'match', match.search);
        $('#count-num').html('共<b style="color:red">'+total+'</b>件商品');
        match.op();
    },
    gen_matchs: function(matchs){
        var trs = [];
        for (var i in matchs){
            var obj = matchs[i];
            var code = template.multiline(function(){/*!@preserve
                <tr data-id="{id}">
                    <td><img src="{img}" width="80px"></td><td>{id}</td><td>{title}</td>
                    <td>{shop}</td><td>{brand}</td><td>{cate}</td><td>{np}</td>
                    <td><a href="javascript:;" class="rm-match text-danger">移除搭配</a></td>
                </tr>
            */}).format(obj);
            trs.push(code);
        }
        $('#match-choose-list').html(trs.join(''));
        $('.rm-match').unbind('click').click(function(){
            $(this).parent().parent().remove();
        });
    },
    get: function(){
        util.ajax({
            method: 'get',
            url: '/query/get_match',
            data: {id: edit.source_id},
            success: function(datas, status){
                match.gen_matchs(datas.data);
            }
        })
    },
    search: function() {
        var data = {
            title : $('#match-title').val() || '',
            cate  : $('#match-cate').val()  || 0,
            brand : $('#match-brand').val() || 0,
            scene : $('#match-scene').val() || 0,
            style : $('#match-style').val() || 0,
            defect: $('#match-defect').val()|| 0
        };
        data = $.extend(data, match.pages);
        util.ajax({
            method:'get',
            url:'/query/get_pack_product',
            data:data,
            success: function(datas, status){
                var matchs = datas.data.pros, total = datas.data.total;
                match.gen_search(matchs, total);
            }
        });
    },
    gen_match_list: function(){
        var match_list = [];
        $('#match-choose-list tr').each(function(){
            match_list.push($(this).attr('data-id'));
        })
        return match_list;
    },
    op: function(){
        $('#match-search').unbind('click').click(match.search);
        $('[href="#match"]').unbind('click').click(function(){
            if(edit.source_id < 0){
                util.alert('请先完成基本信息，再设置搭配信息');
                return;
            }
            match.get();
        });
        $('.add-match').unbind('click').click(function(){
            var $tr = $(this).parent().parent();
            $(this).parent().html('<a href="javascript:;" class="rm-match text-danger">移除搭配</a>');
            $('#match-choose-list').append($tr.prop('outerHTML'));
            $tr.remove();
            $('.match-rm').unbind('click').click(function(){
                $(this).parent().parent().remove();
            });
        });
        
        $('#product-match').unbind('click').click(function(){
            var match_list = match.gen_match_list();
            if(match_list.length < 1){
                util.alert('无搭配信息、无需提交');
                return;
            }
            util.ajax({
                method: 'post',
                url: '/query/update_match',
                data: {id:edit.source_id, choose_list: JSON.stringify(match_list)},
                success: function(datas, status){
                    util.alert('更新搭配信息成功');
                    $('[href="#match"]').click();
                }
            });
        })
    },
    init: function(){
        match.op();
    }
};

$(document).ready(function(){
    edit.init();
    adder.op();
    sku.init();
    match.init();
})
