var packpro = {
    pages: {
        page:1,
        limit:5
    },
    gen: function(packpros, total){
        $('#packpro-list').html('');
        var trs = [];
        for (var i in packpros){
            var obj = packpros[i];
            var code = template.multiline(function(){/*!@preserve
                <tr>
                    <td><img src="{img}" width="80px"></td><td>{id}</td><td>{title}</td>
                    <td>{shop}</td><td>{brand}</td><td>{cate}</td><td>{op}</td><td>{np}</td>
                    <td data-id="{source_id}">
                        <a target="_blank" href="editpro.html?id={source_id}&shopid={shop_id}&st={shop_type}"><i class="icon-pencil icon-xlarge"></i></a>
                        <a class="view" title="预览" target="_blank" href="http://dev.naonaome.com/pro?proid={id}"><i class="icon-eye-open icon-xlarge"></i></a>
                        <a class="rm" title="删除"><i class="icon-remove icon-xlarge text-danger text"></i></a>
                    </td>
                </tr>
            */}).format(obj);
            trs.push(code);
        }
        $('#packpro-list').html(trs.join(''));
        util.paging(total, packpro.pages, 'packpro', packpro.get);
        $('#count-num').html('共<b style="color:red">'+total+'</b>件商品');
        packpro.op();
    },
    get: function() {
        var data = {
            title : $('#pro-title').val() || '',
            cate  : $('#pro-cate').val() || 0,
            brand : $('#pro-brand').val() || 0,
        };
        data = $.extend(data, packpro.pages);
        util.ajax({
            method:'get',
            url:'/query/get_pack_product',
            data:data,
            success: function(datas, status){
                var packpros = datas.data.pros, total = datas.data.total;
                packpro.gen(packpros, total);
            }
        });
    },
    del: function(id) {   
        util.ajax({
            method:'get',
            url:'/query/del_pack_product',
            data:{ids:id},
            success: function(datas, status){
                $('#cancel-btn').click();
                util.alert('删除商品成功');
                packpro.get(); 
            }
        })
    },
    op: function(){
        $('.rm').click(function(){
            var id = $(this).parent().attr('data-id'), img = $(this).parent().parent().children('td').eq(0).html();
            var code = '<div style="text-align:center">'+img+'<br>您在进行删除杂志，删除后将 <b style="color:red">无法恢复</b>，确认继续删除</div>';
            util.dialog('删除商品', code, function(){
                packpro.del(id);
            });
            console.log(id);
        });
        $('#search').unbind('click').click(packpro.get);
    },
    load: function(){
        util.ajax({
            method:'get',
            url:'/query/cate_brand',
            data:{},
            success: function(datas, status){
                var cates = datas.data.cates, brands = datas.data.brands;
                var cate_list = ['<option value="0">选择分类</option>'], brand_list = [];
                for (var i in cates)
                    cate_list.push('<option value="'+cates[i].id+'">'+cates[i].name+'</option>');
                for (var i in brands){
                    brands[i].ch = brands[i].id == 0 ? '选择品牌' : brands[i].ch;
                    brand_list.push('<option value="'+brands[i].id+'">'+brands[i].ch+'</option>');
                }
                $('#pro-cate').html(cate_list.join(''));
                $('#pro-brand').html(brand_list.join(''));
            }
        })
    },
    init: function(){
        packpro.load();
        packpro.get();
    },
    end: true
};

$(document).ready(function() {
    packpro.init();
});