var magazine = {
    pages: {
        page:1,
        limit:5
    },
    gen_edit_code: function(){
        return template.multiline(function(){/*!@preserve
            <div class="row form-group">
                <div class="col-lg-12 col-md-12 form-group">
                    <label>标题</label><input type="text" class="form-control" id="xiumi-title" placeholder="标题">
                </div>  
                <div class="col-lg-12 col-md-12 form-group">
                    <label>秀米链接</label><input type="text" class="form-control" id="xiumi-url" placeholder="秀米网页链接">
                </div>
                <div class="col-lg-12 col-md-12 form-group">
                    <label>封面(点击图片修改)</label>
                    <div id="cover-show" style="position:relative; width:80px; height:143px; margin:0 auto;">
                        <input type="file" class="form-control" id="magazine-cover" style="position:absolute; top:0; width:100%; height:100%; opacity: 0;">
                    </div>
                </div>
            </div>
        */});
    },
    gen: function(magazines, total){
        $('#magazine-list').html('');
        var trs = [];
        for (var i in magazines){
            var obj = magazines[i];
            if(obj.type == 1) continue;
            //obj.type == 2 ? obj['url'] = obj.details : obj['url'] = '一类杂志';
            obj.status == 1 ? obj.isup = '<i class="icon-ok icon-xlarge"></i>' : obj.isup = '<i class="icon-off icon-xlarge text-danger"></i>';
            var code = template.multiline(function(){/*!@preserve
                <tr>
                    <td><img src="{cover}" width="80px"></td><td>{issue}</td>
                    <td>{title}</td><td width="450px">{details}</td><td>{create_time}</td>
                    <td data-id="{id}"><a class="up" data-type="{status}">{isup}</a></td>
                    <td data-id="{id}">
                        <a class="edit" title="编辑"><i class="icon-pencil icon-xlarge"></i></a>
                        <a class="view" title="预览" target="_blank" href="{details}"><i class="icon-eye-open icon-xlarge"></i></a>
                        <a class="forward" title="同步至正式服"><i class="icon-mail-forward text-success icon-xlarge"></i></i></a>
                        <a class="rm" title="删除"><i class="icon-remove icon-xlarge text-danger text"></i></a>
                    </td>
                </tr>
            */}).format(obj);
            trs.push(code);
        }
        $('#magazine-list').html(trs.join(''));
        util.paging(total, magazine.pages, 'magazine', magazine.get);
        magazine.op();
    },
    get: function() {
        util.ajax({
            method:'get',
            url:'/query/magazine',
            data:magazine.pages,
            success: function(datas, status){
                var magazines = datas.data.magazines, total = datas.data.total;
                magazine.gen(magazines, total);
            }
        })
    },
    update: function(id){
        var data = {
            id:id,
            title:$('#xiumi-title').val(),
            url:$('#xiumi-url').val(),
            img:$('#cover-show img').attr('src')
        };
        util.ajax({
            method: 'get',
            url:'/query/update_magazine',
            data:data,
            success: function(datas, status){
                $('#cancel-btn').click();
                util.alert('更新杂志链接成功');
                magazine.get();
            }
        })
    },
    add: function(){
        var data = {
            title:$('#xiumi-title').val(),
            url:$('#xiumi-url').val(),
            img:$('#cover-show img').attr('src')
        };  
        util.ajax({
            method: 'get',
            url:'/query/add_magazine',
            data:data,
            success: function(datas, status){
                $('#cancel-btn').click();
                util.alert('新增二类杂志链接成功');
                magazine.get();
            }
        })
    },
    del: function(id) {   
        util.ajax({
            method:'get',
            url:'/query/del_magazine',
            data:{id:id},
            success: function(datas, status){
                $('#cancel-btn').click();
                util.alert('删除杂志成功');
                magazine.get(); 
            }
        })
    },
    forward: function(id){
        util.ajax({
            method: 'get',
            url:'/query/update_formal_magazine',
            data:{id:id},
            success: function(datas, status){
                $('#cancel-btn').click();
                util.alert('同步杂志成功');
            }
        })
    },
    qiniu_init: function(){
        var uploader = Qiniu.uploader({
            runtimes: 'html5,flash,html4',    //上传模式,依次退化
            browse_button: 'magazine-cover',     //上传选择的点选按钮，**必需**
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
            drop_element: 'magazine-cover',        //拖曳上传区域元素的ID，拖曳文件或文件夹后可触发上传
            chunk_size: '4mb',                //分块上传时，每片的体积
            auto_start: true,                 //选择文件后自动上传，若关闭需要自己绑定事件触发上传
            init: {
                'BeforeUpload': function(up, file) {
                    $('#cover-show img').attr('src', 'img/load.gif');
                },
                'FileUploaded': function(up, file, info) {
                    var domain = up.getOption('domain');
                    var res = JSON.parse(info);
                    var sourceLink = domain + res.key;
                    $('#cover-show img').attr('src', sourceLink);         
                },
                'Error': function(up, err, errTip) {
                       util.alert('上传图片失败, tip:'+errTip);
                },
            }
        });
    },
    op: function(){
        $('#magazine-add').click(function(){
            var code = magazine.gen_edit_code();
            util.dialog('新增二类杂志', code, magazine.add, function(){
                magazine.qiniu_init();
                $('#cover-show').append('<img src="img/add.png" width="100px">');
            })
        });
        $('.edit').click(function(){
            var id = $(this).parent().attr('data-id'), tds = $(this).parent().parent().children('td');
            var code = magazine.gen_edit_code();
            util.dialog('修改秀米链接', code, function(){
                magazine.update(id);
            }, function(){
                magazine.qiniu_init();
                $('#xiumi-title').val(tds.eq(2).text());
                $('#xiumi-url').val(tds.eq(3).text());
                $('#cover-show').append(tds.eq(0).html());
            })
        });
        $('.up').click(function(){
            var data = {
                id    : $(this).parent().attr('data-id'),
                status: $(this).attr('data-type') == 0 ? 1 : 0
            }
            util.ajax({
                method:'get',
                url:'/query/change_magazine_status',
                data:data,
                success: function(datas,status){magazine.get()}
            })
        });
        $('.forward').click(function(){
            var id = $(this).parent().attr('data-id'), img = $(this).parent().parent().children('td').eq(0).html();
            var code = '<div style="text-align:center">'+img + '<br>您在进行将该杂志<b style="color:red">同步至正式服</b>，是否确定继续？</div>';
            util.dialog('同步杂志', code, function(){magazine.forward(id);});
        });
        $('.rm').click(function(){
            var id = $(this).parent().attr('data-id'), img = $(this).parent().parent().children('td').eq(0).html();
            var code = '<div style="text-align:center">'+img+'<br>您在进行删除杂志，删除后将 <b style="color:red">无法恢复</b>，确认继续删除</div>';
            util.dialog('删除商品', code, function(){
                magazine.del(id);
            });
            console.log(id);
        })
    },
    load: function(){
        magazine.get();
    },
    end: true
};

$(document).ready(function() {
    magazine.load();
});