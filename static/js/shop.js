var shop = {
    type:0,
    pages: {
        page: 1,
        limit: 15
    },
    gen_edit_code: function(){
        return template.multiline(function(){/*!@preserve
            <div class="row form-group">
                <div class="col-lg-6 col-md-6">
                    <label>商店类型</label><select id="add-shoptype" class="form-control"><option value="0">自营</option><option value="1">淘宝</option></select>
                </div>
                <div class="col-lg-6 col-md-6">
                    <label>商店地址</label><input type="text" class="form-control" id="add-shopaddr" placeholder="随便填个地区，如中国、海外">
                </div>
            </div>
            <div class="row form-group">
                <div class="col-lg-12 col-md-12">
                    <label>商店名称</label><input type="text" class="form-control" id="add-shopname">
                </div>
            </div>
            <div class="row form-group">
                <div class="col-lg-12 col-md-12">
                    <label>网址</label><input type="text" class="form-control" id="add-shopurl">
                </div>
            </div>
            <div class="row form-group">
                <div class="col-lg-12 col-md-12">
                    <label>商店描述</label><textarea class="form-control" id="add-shopdesc"></textarea>
                </div>
            </div>
        */});
    },
    gen_shop_list : function(shops, total){
        $('#shop-list').html('');
        var trs = [];
        for (var i in shops) {
            var obj = shops[i];
            var code = template.multiline(function(){/*!@preserve
                <tr data-id="{id}">
                    <td><input type="checkbox" name="shop-list" value="" /></td><td>{id}</td><td>{name}</td>
                    <td>{address}</td><td>{shop_type}</td><td>{url}</td><td><a href="pro_list.html?shopid={id}">商品列表</a></td>
                    <td data-id="{id}">
                        <a class="edit"><i class="icon-pencil icon-xlarge"></i></a>
                        <a class="rm"><i class="icon-remove icon-xlarge text-danger text"></i></a>
                    </td>
                </tr>
            */});
            trs.push(code.format(obj));
        }
        $('#shop-list').html(trs.join(''));
        util.paging(total, shop.pages, 'shop', shop.get);
        shop.op();
    },
    get: function(){
        var word = $('#shop-name').val() || '';
        var data = $.extend({}, shop.pages, {'word':word});
        util.ajax({
            method:'get',
            data:data,
            url:'/query/allshop',
            success: function(datas,status){
                var shops = datas.data.shops, total = datas.data.total;
                shop.gen_shop_list(shops, total);
            }
        })
    },
    add: function(){
        var data = {
            name: util.get_val('add-shopname'),
            addr: util.get_val('add-shopaddr'),
            desc: util.get_val('add-shopdesc'),
            url:util.get_val('add-shopurl'),
            shop_type: util.get_val('add-shoptype')
        };
        for(var i in data){
            if(i != 'shop_type' && !data[i]) return;
        }
        util.ajax({
            method:'post',
            data:data,
            url:'/query/add_shop',
            success: function(datas,status){
                $('#cancel-btn').click();
                util.alert('新增商店<strong style="color:red">'+data.name+'</string>成功');
                shop.get();
            }
        })
    },
    update: function(id){    
        var data = {
            id  : id,
            name: util.get_val('add-shopname'),
            addr: util.get_val('add-shopaddr'),
            desc: util.get_val('add-shopdesc'),
            url:util.get_val('add-shopurl'),
            shop_type: util.get_val('add-shoptype')
        };
        for(var i in data){
            if(i != 'shop_type' && !data[i]) return;
        }
        util.ajax({
            method:'post',
            data:data,
            url:'/query/update_shop',
            success: function(datas,status){
                $('#cancel-btn').click();
                util.alert('更新商店<strong style="color:red">'+data.name+'</string>成功');
                shop.get();
            }
        })
    },
    del: function(ids, name){
        util.ajax({
            method:'get',
            data:{shops:ids},
            url:'/query/del_shop',
            success: function(datas,status){
                $('#cancel-btn').click();
                util.alert('删除商店<strong style="color:red">'+name+'</string>成功');
                shop.get(); 
            }
        })
    },
    op: function(){
        $('#search').click(shop.get);
        $('#shop-add').click(function(){
            $('#dialog .modal-dialog').css({"width": "550px", "margin-left": "-275px"});
            var code = shop.gen_edit_code();
            util.dialog('新增商店', code, function(){
                shop.add();
            }); 
        });
        $('.edit').click(function(){
            $('#dialog .modal-dialog').css({"width": "550px", "margin-left": "-275px"});
            var code = shop.gen_edit_code(), id = $(this).parent().attr('data-id'), $tr = $(this).parent().parent();
            util.dialog('更新商店', code, function(){
                shop.update(id);
            }, function(){
                util.ajax({
                    method:'get', 
                    url:'/query/get_one_shop', 
                    data:{id:id}, 
                    success:function(datas,status){
                        $('#add-shopname').val(datas.data.name);
                        $('#add-shopaddr').val(datas.data.addr); 
                        $('#add-shopdesc').val(datas.data.desc); 
                        $('#add-shopurl').val(datas.data.url); 
                        $('#add-shoptype').val(datas.data.shop_type);  
                    }
                })
                 
            });
        });
        $('.rm').click(function(){
            $('#dialog .modal-dialog').css({"width": "400px", "margin-left": "-200px"});
            var id = $(this).parent().attr('data-id'), name = $(this).parent().parent().children('td').eq(2).text();
            var code = '您在进行删除商店<strong  style="color:red">'+name+'</strong>，删除后将 <b style="color:red">无法恢复</b>，确认继续删除';
            util.dialog('删除商店', code, function(){
                shop.del(id, name);
            })
        })
    },
    load: function(){
        shop.get();
    }
};

$(document).ready(function(){
    shop.load();
});
