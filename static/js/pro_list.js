var pros = {
    shop_id: 0,
    shop_type: 0,
    pages: {
        page:1,
        limit:15
    },
    shop_info: function(shopinfo) {
        pros.shop_type = shopinfo.shop_type;
        $("#shop-info").html('');
        var code = template.multiline(function(){/*!@preserve
            <table class="table table-bordered">
                <tr><td>商店id</td><td>{id}</td><td>商店名称</td><td>{name}</td></tr>
                <tr><td>商品总数</td><td>{num}</td><td>商店属地</td><td>{addr}</td></tr>
                <tr><td>店铺链接</td><td><a href="{url}">{url}</a></td></tr>
            </tabl>
        */}).format(shopinfo);
        
        $("#shop-info").html(code);
    },
    product_list: function(products, total) {
        $("#product-list").html('');
        var trs = [];
        for (var i in products) {
            var obj = $.extend({}, products[i], {shopid:pros.shop_id, shop_type:pros.shop_type});
            var code = template.multiline(function(){/*!@preserve
                <tr>
                    <td><input type="checkbox" name="pros-checkbox" value="" /></td><td>{name}</td><td>{id}</td><td>{type}</td><td>{op}</td><td>{np}</td>
                    <td data-id="{id}">
                        <a target="_blank" href="editpro.html?id={id}&shopid={shopid}&st={shop_type}"><i class="icon-pencil icon-xlarge"></i></a>
                        <a class="rm"><i class="icon-remove icon-xlarge text-danger text"></i></a>
                    </td>
                    <td>
                        <a target="_blank" href="{url}">前往</a>
                    </td>
                </tr>
            */});
            if (obj.is_edit == 1){
                code= code.replace('<input type="checkbox" name="pros-checkbox" value="" />','已包装')
                          .replace('<a class="rm"><i class="icon-remove icon-xlarge text-danger text"></i></a>', 
                                   '<a target="_blank" href="http://dev.naonaome.com/pro?proid={proid}"><i class="icon-eye-open icon-xlarge"></i></a>');
            }
            trs.push(code.format(obj)); 
        }
        $("#pros-list").html(trs.join('')); 
        util.paging(total, pros.pages, 'pros', pros.get);
        pros.op();
    },
    get: function() {
        var data = {
            shop_id: pros.shop_id,
            word:$('#pro-name').val() || '',
            type:$("#pro-type").val() || 0
        };
        data = $.extend({}, data, pros.pages);
        console.log(data);
        util.ajax({
            method:'get',
            url:'/query/get_prolist',
            data:data,
            success: function(datas, status){
                var products = datas.data.products, shop = datas.data.shop, total = datas.data.total;
                pros.shop_info(shop);
                pros.product_list(products, total);
            }
        })
    },
    del: function(ids, name) {   
        var data = {ids:ids};
        util.ajax({
            method:'get',
            url:'/query/del_source_product',
            data:data,
            success: function(datas, status){
                $('#cancel-btn').click();
                util.alert('删除商品<b style="color:red;">'+name+'</b>成功');
                pros.get(); 
            }
        })
    },
    op: function(){
        $('#search').click(pros.get);
        $('#pros-add').click(function(){
            location.href = 'editpro.html?id=-1&shopid='+pros.shop_id+'&st='+pros.shop_type;
        });
        $('.rm').click(function(){
            var id = $(this).parent().attr('data-id'), name = $(this).parent().parent().children('td').eq(1).text();
            var code = '您在进行删除商品<strong  style="color:red">'+name+'</strong>，删除后将 <b style="color:red">无法恢复</b>，确认继续删除';
            util.dialog('删除商品', code, function(){
                pros.del(id, name);
            });
            console.log(id);
        })
    },
    load: function(){
        var shopid = util.query_string('shopid');
        if (!shopid){
            util.alert("请传入商店id和类型");
            return false;
        }
        pros.shop_id = shopid;
        pros.get();
    },
    end: true
};

$(document).ready(function() {
    pros.load();
});