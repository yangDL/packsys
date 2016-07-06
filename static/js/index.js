var index = {
    gen_tr: function(datas){
       var code = '';
        for (var i in datas){
            var obj = datas[i];
            code += '<tr><td>'+obj.type+'</td><td>'+obj.num+'</td></tr>';
        }
        return code;
    },
    gen_table: function(datas, id){
        var code = index.gen_tr(datas);
        $('#'+id).html(code);
    },
    load: function(){
        util.ajax({
            method:'get',
            url:'/query/account',
            success: function(data, status){
                index.gen_table(data.data.cates, 'cate-list');
                index.gen_table(data.data.scenes, 'scene-list');
                index.gen_table(data.data.styles, 'style-list');
            }
        });
    }
};

index.load();
