var template = {
    multiline: function(fn){
        return fn.toString().split('\n').slice(1,-1).join('\n') + '\n';
    },
    html_header: function(){/*!@preserve
        <ul class="nav navbar-nav navbar-avatar pull-right">
            <li class="dropdown">
                <a href="#" class="dropdown-toggle" data-toggle="dropdown">
                    <span class="hidden-sm-only"></span>
                    <span class="inline" style="margin-top: 10px;">欢迎您，<span class="user-nick"></span></span>
                    <b class="caret hidden-sm-only"></b>
                </a>
                <ul class="dropdown-menu">
                    <li><a href="javascript:;" class="user-nick"></a></li>
                    <li class="divider"></li>
                    <li><a href="javascript:;" onclick="util.logout();">退出</a></li>
                </ul>
            </li>
        </ul>
        <a class="navbar-brand" href="#">包装系统</a>
        <ul class="nav navbar-nav hidden-sm">
            <li><img src="img/naonao.png" height="50px"></li>
            <li class="slogan">挠挠  - 原创就要对味儿</li>
        </ul>
        <button type="button" class="btn btn-link pull-left nav-toggle hidden-lg" data-toggle="class:show" data-target="#nav">
            <i class="icon-reorder icon-xlarge text-default"></i>
        </button>
    */},
    html_nav: function(){/*!@preserve
        <ul class="nav">
            <li class="index-html"><a href="index.html"><i class="icon-bookmark icon-xlarge"></i>数据预览</a></li>
            <li class="shop-html"><a href="shop.html"><i class="icon-list-ul icon-xlarge"></i>商店列表</a></li>
            <li class="packed-html"><a href="packed.html"><i class="icon-th icon-xlarge"></i>已包装商品</a></li>
            <li class="unpack-html"><a href="unpack.html"><i class="icon-dropbox icon-xlarge"></i>待包装商品</a></li>
            <li class="tagpack-html"><a href="tagpack.html"><i class="icon-tags icon-xlarge"></i>标签搜索商品</a></li>
            <li class="magazine-html"><a href="magazine.html"><i class="icon-book icon-xlarge"></i>挠志列表</a></li>
        </ul>
    */},
    html_footer: function(){/*!@preserve
        <div class="text-center padder clearfix">
            <p>
                <small>&copy; 挠挠-原创就要对味儿 轩腾华兴出品 </small><br><br>
            </p>
        </div>
    */},
    html_plugin: function(){/*!@preserve
        <div class="modal fade" id="dialog">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                        <span class="modal-title"></span>
                    </div>
                    <div class="modal-body"></div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-error" data-dismiss="modal" id="cancel-btn">取消</button>
                        <button type="button" class="btn btn-primary" id="modal-btn">确定</button>
                    </div>
                </div>
            </div>
        </div>
        <div class="modal fade bs-example-modal-sm" tabindex="-1" id="tip">
            <div class="modal-dialog modal-sm">
                <div class="modal-content">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                        <h4 class="modal-title">提示</h4>
                    </div>
                    <div class="modal-body"></div>
                </div>
            </div>
        </div>
        <div class="zdc"></div>
        <div class="sk-spinner sk-spinner-cube-grid sk-loading">
            <div class="sk-cube"></div>
            <div class="sk-cube"></div>
            <div class="sk-cube"></div>
            <div class="sk-cube"></div>
            <div class="sk-cube"></div>
            <div class="sk-cube"></div>
            <div class="sk-cube"></div>
            <div class="sk-cube"></div>
            <div class="sk-cube"></div>
        </div>
    */},
    load: function(){
        String.prototype.replaceAll = function (exp, newStr) {
            return this.replace(new RegExp(exp, "gm"), newStr);
        };
        String.prototype.format = function(args) {
            var result = this;
            if (arguments.length < 1) {
                return result;
            }
        
            var data = arguments; // 如果模板参数是数组
            if (arguments.length == 1 && typeof (args) == "object") {
                // 如果模板参数是对象
                data = args;
            }
            for ( var key in data) {
                var value = data[key];
                if (undefined != value) {
                    result = result.replaceAll("\\{" + key + "\\}", value);
                }
            }
            return result;
        }
        $('#header').html(this.multiline(this.html_header));
        $('#nav').html(this.multiline(this.html_nav));
        $('#footer').html(this.multiline(this.html_footer));
        $('#plugin').html(this.multiline(this.html_plugin));
    }
};
template.load();
