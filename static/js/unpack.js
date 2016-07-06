var unpack = {
    pages: {
        page:1,
        limit:5
    },
    gen: function(unpacks, total){
        $('#unpack-list').html('');
        var trs = [];
        for (var i in unpacks){
            var obj = unpacks[i];
            var code = template.multiline(function(){/*!@preserve
                <tr>
                    <td><img src="{img}" width="80px"></td><td>{name}</td><td>{shop}</td><td>{op}</td><td>{np}</td>
                    <td data-id="{id}">
                        <a target="_blank" href="editpro.html?id={id}&shopid={shopid}&st={shop_type}"><i class="icon-pencil icon-xlarge"></i></a>
                        <a class="rm" title="删除"><i class="icon-remove icon-xlarge text-danger text"></i></a>
                    </td>
                    <td><a target="_blank" href="{url}">前往</a></td>
                </tr>
            */}).format(obj);
            trs.push(code);
        }
        $('#unpack-list').html(trs.join(''));
        util.paging(total, unpack.pages, 'unpack', unpack.get);
        $('#count-num').html('共<b style="color:red">'+total+'</b>件商品');
        unpack.op();
    },
    get: function() {
        var data = {
            title  : $('#pro-title').val() || '',
            shop_id: $('#pro-shop').val()  || 0,
        };
        data = $.extend(data, unpack.pages);
        util.ajax({
            method:'get',
            url:'/query/get_unpack_product',
            data:data,
            success: function(datas, status){
                var unpacks = datas.data.pros, total = datas.data.total;
                unpack.gen(unpacks, total);
            }
        });
    },
    del: function(ids, img) {   
        var data = {ids:ids};
        util.ajax({
            method:'get',
            url:'/query/del_source_product',
            data:data,
            success: function(datas, status){
                $('#cancel-btn').click();
                util.alert('删除成功');
                unpack.get(); 
            }
        })
    },
    op: function(){
        $('.rm').click(function(){
            var id = $(this).parent().attr('data-id'), img = $(this).parent().parent().children('td').eq(0).html();
            var code = '<div style="text-align:center">'+img+'<br>您在进行删除杂志，删除后将 <b style="color:red">无法恢复</b>，确认继续删除</div>';
            util.dialog('删除商品', code, function(){
                unpack.del(id);
            });
        });
        $('#search').unbind('click').click(unpack.get);
    },
    load: function(){
        var data = {word:'',page:1,limit:999999999};
        util.ajax({
            method:'get',
            data:data,
            url:'/query/allshop',
            success: function(datas,status){
                var shops = datas.data.shops;
                var shop_list = ['<option value="0">选择商店</option>']
                for (var i in shops)
                    shop_list.push('<option value="'+shops[i].id+'">'+shops[i].name+'</option>');
                $('#pro-shop').html(shop_list.join(''));
            }
        })
    },
    init: function(){
        unpack.load();
        unpack.get();
    },
    end: true
};

$(document).ready(function() {
    unpack.init();
});