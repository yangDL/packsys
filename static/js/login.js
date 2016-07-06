var user = {
	login: function(name, pwd){
	    util.ajax({
	        method:'post',
	        url:'/login',
	        check:false,
	        data:{name:name, pwd:hex_md5(pwd)},
	        success: function(datas, status){
	            cache.set(cache.keys.user, datas.data);
	            window.location.href="index.html";
	        }
	    });
	},
	init: function(){
		$('#submit').click(function(){
			var name = util.get_val('username');
			if(!name) return false;
			var pwd = util.get_val('pwd');
			if (!pwd) return false;
			user.login(name, pwd);
		});
	}
};
$(document).ready(function(){
	user.init();
})
