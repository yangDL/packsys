var tagpack = {
    pages: {
        page:1,
        limit:5
    },
    gen: function(tagpacks, total){
        $('#tagpack-list').html('');
        var trs = [];
        for (var i in tagpacks){
            var obj = tagpacks[i];
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
        $('#tagpack-list').html(trs.join(''));
        util.paging(total, tagpack.pages, 'tagpack', tagpack.get);
        $('#count-num').html('共<b style="color:red">'+total+'</b>件商品');
        tagpack.op();
    },
    get: function() {
        var data = {
            scene  : $('#pro-scene').val() || 0,
            style  : $('#pro-style').val() || 0,
            resp   : $('#pro-resp').val()  || 0,
            elem   : $('#pro-elem').val()  || 0,
            defect : $('#pro-defect').val()|| 0
        };
        data = $.extend(data, tagpack.pages);
        util.ajax({
            method:'get',
            url:'/query/get_pack_product',
            data:data,
            success: function(datas, status){
                var tagpacks = datas.data.pros, total = datas.data.total;
                console.log(total);
                tagpack.gen(tagpacks, total);
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
                tagpack.get(); 
            }
        })
    },
    op: function(){
        $('.rm').unbind('click').click(function(){
            var id = $(this).parent().attr('data-id'), img = $(this).parent().parent().children('td').eq(0).html();
            var code = '<div style="text-align:center">'+img+'<br>您在进行删除杂志，删除后将 <b style="color:red">无法恢复</b>，确认继续删除</div>';
            util.dialog('删除商品', code, function(){
                tagpack.del(id);
            });
            console.log(id);
        });
        $('#search').unbind('click').click(tagpack.get);
    },
    gen_tag_opt: function(id, datas, name){
        var lis = ['<option value="0">选择'+name+'</option>'];
        for(var i in datas)
            lis.push('<option value="'+datas[i].id+'">'+datas[i].name+'</option>');
        $('#'+id).html(lis.join(''));
    },
    load: function(){
        util.ajax({
            method:'get',
            url:'/query/tag_list',
            data:{},
            success: function(datas, status){
                tagpack.gen_tag_opt('pro-scene', datas.data.scenes,  '场景标签');
                tagpack.gen_tag_opt('pro-style', datas.data.styles,  '风格标签');
                tagpack.gen_tag_opt('pro-resp',  datas.data.resps,   '回应标签');
                tagpack.gen_tag_opt('pro-elem', datas.data.elements, '元素标签');
                tagpack.gen_tag_opt('pro-defect', datas.data.defects,'身材标签');
                $('#pro-resp').comboSelect();
                $('#pro-elem').comboSelect();
            }
        })
    },
    init: function(){
        tagpack.load();
        tagpack.get();
    },
    end: true
};

$(document).ready(function() {
    tagpack.init();
});