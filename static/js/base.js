var cache = {
    keys: {
        user: 'xthx_admin::user'
    },
    remove: function(key){
        window.sessionStorage.removeItem(key);
    },
    set: function(key, value, duration) {
        var data = {
            value: value,
            expiryTime: !duration || isNaN(duration) ? 0 : this._getCurrentTimeStamp() + parseInt(duration)
        };
        window.sessionStorage[key] = JSON.stringify(data);
    },
    get: function(key) {
        var data = window.sessionStorage[key];
        if (!data || data === "null") {
            return null;
        }
        var now = this._getCurrentTimeStamp();
        var obj;
        try {
            obj = JSON.parse(data);
        } catch (e) {
            return null;
        }
        if (obj.expiryTime === 0 || obj.expiryTime > now) {
            return obj.value;
        }
        return null;
    },
    _getCurrentTimeStamp: function() {
        return Date.parse(new Date()) / 1000;
    }
}; 
var addr = 'pack.naonaome.com';
var util = {
    pre_url : 'http://'+addr,
    img_url : 'http://'+addr+'/query/uptoken',
    user: null,
    is_phone: function(str){
        if(!str) return false;
        var reg = /^(1[35678][0-9]{9})$/;
        return reg.test(str);
    },
    is_int: function(str){
        var reg = /^(-|\+)?\d+$/ ;
        return reg.test(str);
    },
    is_float: function(str){
        if(util.is_int(str))
            return true;
        var reg = /^(-|\+)?\d+\.\d*$/;
        return reg.test(str);
    },
    query_string: function(key){
        var reg = new RegExp("(^|&)" + key + "=([^&]*)(&|$)", "i"); 
        var r = window.location.search.substr(1).match(reg); 
        if (r != null) return unescape(r[2]); return null; 
    },
    loading: function() {
        $('html').css('overflow-y', 'hidden');
        $('.sk-loading').css('display', 'block');
        $('.zdc').css('display', 'block');
    },
    loaded: function() {
        $('.sk-loading').hide();
        $('.zdc').hide();
        $('html').css('overflow-y', 'auto');
    },
    dialog: function(title, body, callback, othercall){
        $('#dialog .modal-title').html(title);
        $('#dialog .modal-body').html(body);
        $('#dialog').modal('show');
        othercall && othercall(); 
        $('#modal-btn').off();
        !callback ? $('.modal-footer').hide() : $('.modal-footer').show();
        $('#modal-btn').click(function(){
           callback();
        })  
    },
    alert: function(msg){
        $('.modal-dialog').css('margin-top', '10%');
        $('#tip .modal-body').html(msg);
        $('#tip').modal('show');
    },
    get_val: function(id){
        var value = $('#'+id).val() || '';
        if(!value){
            $('#'+id).after('<span class="span-tip">该项不能为空</span>');
            $('#'+id).focus();
        }
        else
            $('#'+id).next('.span-tip').remove();
        return value;
    },
    ajax: function(opt){
        var _opt = {
            method: 'get',
            data:{},
            async:true,
            check:true,
            before:function() {util.loading();},
            complete:function() {util.loaded();}
        };
        opt = $.extend(_opt, opt);  
        if(opt.check !== false){
            util.load();
            var userid = util.user.userid;
            var token = util.user.token;
            if ('get' == opt.method.toLowerCase()){
                var _data = {'userid':userid, 'token':token};
                opt.data = $.extend(opt.data, _data);
            }else{
                if(opt.url.indexOf('?') == -1)
                    opt.url = opt.url +'?userid='+userid+'&token='+token;
                else{
                    opt.url = opt.url +'&userid='+userid+'&token='+token;
                }
            }  
        }
        $.ajax({
            type:opt.method,
            url :util.pre_url + opt.url,
            async:opt.async,
            data:opt.data,
            beforeSend: opt.before,
            complete: opt.complete,
            success: function(datas, status){
                if(datas.code == 0){
                    opt.success && opt.success(datas, status);
                }else{
                    util.alert(datas.msg);
                }
            },
            error: function(status) {
                util.alert("无法连接网络，请check网络连接和服务器");
                return false;
            }
        });
    },
    paging: function(total, pages, name, callback){
        var max_page = parseInt(total / pages.limit) + 1, page_list = [];
        if(pages.page > 1){
            page_list.push('<li><a href="javascript:;" id="left-'+name+'"><i class="icon-chevron-left"></i></a></li>');
            page_list.push('<li><a href="javascript:;">1</a></li>');
        }else{
            page_list.push('<li class="active"><a href="javascript:;">1</a></li>');
        }
            
        first_page = pages.page > 4 ? pages.page - 2 : 2;
        last_page = max_page - first_page > 3 ? first_page+4 : max_page;
        for (var i = first_page; i <= last_page; i++){
            var code = '';
            if(pages.page == i){
                code = '<li class="active"><a href="javascript:;">'+i+'</a></li>';
            }else{
                code = '<li><a href="javascript:;">'+i+'</a></li>';
            }
            page_list.push(code);
        }
        if(last_page != max_page)
            page_list.push('<li><a href="javascript:;">'+max_page+'</a></li>');  
        if(pages.page < max_page)
        page_list.push('<li><a href="javascript:;" id="right-'+name+'"><i class="icon-chevron-right"></i></a></li>');
        $('#'+name+'-page').html(page_list.join(''));
        $('#left-'+name).off(); $('#right-'+name).off();$('#'+name+'-page li a').off();
        $('#left-'+name).click(function(){
            if(pages.page <= 1)
                return;
            pages.page--;
            callback();
        });
        $('#right-'+name).click(function(){
            var maxnum = $(this).parent().prev('li').text();
            if(pages.page >= maxnum)
                return;
            pages.page++;
            callback();
        });
        $('#'+name+'-page li a').click(function(){
            if($(this).attr('id') == 'right-'+name || $(this).attr('id') == 'left-'+name)
                return;
            var page = $(this).text();
            pages.page = page;
            callback();
        })
    },
    logout: function(){
        cache.remove(cache.keys.user);
        location.href = 'login.html';
    },
    load: function(){
        if(!util.user){
            var user = cache.get(cache.keys.user);
            if(!user)location.href='login.html';
            util.user = user;
            util.img_url = util.img_url + '?userid='+user.userid+'&token='+user.token;
            $('.user-nick').text(user.name);
            var pagename = window.location.pathname.split('/').pop().replace('.', '-');
            $('#nav li').each(function(){
               var class_str = $(this).attr('class');
               if(class_str.indexOf(pagename) != -1){
                   $(this).addClass('active');
                   return;
               }
            });
        }
    }
};
