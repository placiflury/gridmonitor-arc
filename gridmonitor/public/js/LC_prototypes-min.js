var LC_debug=true;debug=function(a){if(window.console!=undefined&&LC_debug){console.log(a)}};var StatusMessageController={event_types:undefined,container:null,delay:3000,init:function(a){var a=a||this;a.event_types=a.event_types||["OpDoneStatus"];if(a.event_types.indexOf("OpDoneStatus")<0){a.event_types[a.event_types.length]="OpDoneStatus"}if(!a.container){a.container=$("<div/>").appendTo("body").hide()}for(i in a.event_types){$(a.container).bind(a.event_types[i],function(b,c){a.set(c)})}$(a.container).ajaxError(function(){a.set("ERROR;;;AJAX Request Error.")});$(a.container).hide()},set:function(b){var a=b.split(";;;");if(a.length<2){var a=["UNKNOWN",b]}if(a[0]=="OK"){$(this.container).attr("class","ok")}else{if(a[0]=="ERROR"){$(this.container).attr("class","error")}else{if(a[0]=="CRITICAL"){$(this.container).attr("class","critical")}else{if(a[0]=="WARN"){$(this.container).attr("class","warn")}else{$(this.container).attr("class","unknown")}}}}$(this.container).empty().text(a[1]);$(this.container).fadeIn().delay(this.delay).fadeOut()}};var ListController={url:undefined,click:true,cursor:undefined,container:undefined,title_proto:$("<b/>"),title:null,list_proto:$('<ul class="LC_list_ul"/>'),list:null,child_proto:$("<li/>"),link_proto:$('<a href="#"/>'),links:null,multiple:false,name_tag:undefined,identifier:undefined,toggle:false,init:function(d,b,c){var c=c||this;var a=Math.random();c.identifier=a.toString().replace(/\W/g,"");if(!d||typeof d!="string"){throw"A ListController object has to be initiated with a valid name_tag."}if(!b||typeof b!="string"){throw"A URL is needed to fetch JSON data."}if(!c.cursor){c.cursor="pointer"}c.name_tag=d;c.url=b;c.list=c.list_proto.clone();c.create_list();c.set_title();c.set_link();c.bind_click();c.build()},set_title:function(a){this.title=this.title||this.title_proto.clone();if(a!=undefined){var a=a||"";this.title.text(a)}},set_link:function(e,b){var a=false;if(typeof b=="boolean"){a=!b}else{if(typeof e=="boolean"){a=!e;e="*"}}var b=b||e||"";var e=e||"no_id";if(a){if(e=="*"){this.links.empty()}else{if(e){var c=this.links.find("#"+e);c.remove()}}}else{this.links=this.links||$("<div/>");if(e&&b){var d=this.link_proto.clone().text(b).attr("id",e);d.append($("<br/>"));this.links.append(d)}}},has_link:function(a){return this.links.has("#"+a+"").length>0},build:function(){var a=$('<table class="LC_table"/>');a.append($('<tr id="LC_title"><td/></tr>'));if(this.title){a.find("td").last().append(this.title)}a.append($('<tr id="LC_list"><td/></tr>'));if(this.list){a.find("td").last().append(this.list)}a.append($('<tr id="LC_links"><td/></tr>'));if(this.links){a.find("td").last().append(this.links)}if(!this.container){a.appendTo($("body"))}else{a.appendTo(this.container)}},create_list:function(a){var b=this;var a=a||"";$.getJSON(this.url+a,function(e){b.list.empty();b.list.data("fields",e.names);b.list.data("order_keys",e.order_keys);var f=e.members;for(var c in f){if(f.hasOwnProperty(c)){var d=b.create_child(f[c][e.id_key],b.child_text(f[c],e.show_keys));if(e.id_key=="hash"){d.data("hash",f[c]["hash"]);delete f[c]["hash"]}d.data("info",f[c])}}})},update_list:function(a){this.list.empty();this.create_list(a)},child_text:function(c,a){var b="";for(key in a){if(a.hasOwnProperty(key)){b+=c[a[key]];b+=" "}}return b.replace(/^\s+|\s+$/g,"")},create_child:function(b,a){return this.child_proto.clone(true).appendTo(this.list).attr("name",this.identifier).attr("id",b.toString().replace(/\W/g,"")).css("cursor",this.cursor).text(a)},show:function(){this.container.show()},hide:function(){this.container.hide()},get_selected:function(){var a=this.list.find("li.selected");if(a.length<1){return undefined}else{return a}},get_all:function(){return this.list.find("li")},bind_click:function(){this.list.delegate("li","click",{user:this},function(b){var a=b.data.user;a.handle_click_event(this)})},handle_click_event:function(a){if(this.click){if(this.multiple==false){var b=$(a).hasClass("selected");this.list.find("li").toggleClass("selected",false);if(this.toggle){$(a).toggleClass("selected",!b)}else{$(a).toggleClass("selected",true)}}else{if(this.toggle){$(a).toggleClass("selected")}else{$(a).toggleClass("selected",true)}}}},};var ListControllerSub=Object.create(ListController);ListControllerSub.subchild_proto=ListControllerSub.__proto__.child_proto;ListControllerSub.child_proto=$("<ul/>");ListControllerSub.create_list=function(a){var b=this;a=a||"";$.getJSON(this.url+a,function(h){b.list.data("fields",h.names);b.list.data("order_keys",h.order_keys);var l=h.members;var f=[];for(var d in l){if(l.hasOwnProperty(d)){var j=l[d][h.parent_key];if(($.inArray(j,f))<=-1){f[f.length]=j;var g=b.create_child(j,j);for(var e in l){if(l.hasOwnProperty(e)&&l[e][h.parent_key]==j){var c=b.create_subchild(l[e][h.id_key],b.child_text(l[e],h.show_keys),g);if(h.id_key=="hash"){c.data("hash",l[e]["hash"]);delete l[e]["hash"]}c.data("info",l[e])}}}}}})},ListControllerSub.create_subchild=function(c,b,a){return this.subchild_proto.clone().appendTo(a).attr("id",c.toString().replace(/\W/g,"")).attr("name",this.identifier).css("cursor",this.cursor).text(b)};var ListEditor={url:undefined,event_type_status:"OpDoneStatus",list_contr:null,selected_item:null,container:undefined,flush_container:false,table_proto:$('<table class="LE_table"/>'),table:null,new_link:false,edit_link:false,del_link:false,click:false,hover:false,init:function(a,b){var b=b||this;if(ListController.isPrototypeOf(a)){b.list_contr=a}else{throw"Argument list_contr has to be inherited from ListController."}b.url=b.url||a.url;b.list_contr.multiple=false;b.table=b.table_proto.clone();if(b.new_link&&!(b.list_contr.has_link("new"))){b.list_contr.set_link("new","New")}if(b.edit_link&&!(b.list_contr.has_link("edit"))){b.list_contr.set_link("edit","Edit")}if(b.del_link&&!(b.list_contr.has_link("del"))){b.list_contr.set_link("del","Delete")}b.delegate_click();b.delegate_hover();b.delegate_links();b.container=b.container||$("body");b.table.appendTo(b.container)},hide:function(a){if(!(this.click)||!(this.list_contr.get_selected())||a){this.table.empty()}},show:function(d,e){var e=e||this;e.table.show();e.table.empty();if(e.flush_container){e.container.empty()}var d=d||{};if(e.click&&e.hover){var f=e.list_contr.get_selected()||e.selected_item}else{if(e.click){var f=e.list_contr.get_selected()}else{if(e.hover){var f=e.selected_item}else{var f=e.list_contr.get_selected()}}}debug(f.data("info"));var a=f.data().info;var h=e.list_contr.list.data().order_keys;for(var c in h){if(a.hasOwnProperty(h[c])){var j=$('<tr><td id="LE_name"/><td id="LE_change"/></tr>');e.table.append(j);d[h[c]]=d[h[c]]||$("<div/>");j.children("td").first().text(e.list_contr.list.data().fields[h[c]]);var g=d[h[c]];g.text(a[h[c]]);try{g.val(a[h[c]])}catch(b){}j.children("td").last().append(g)}}e.container.append(e.table)},show_child:function(a,b){var b=b||this;b.show(a,b)},new_child:function(b,f){var f=f||this;var g=f.list_contr.list.data().fields;var b=b||{};for(var d in g){if(g.hasOwnProperty(d)&&!(b[d])){b[d]=$('<input type="text" id="'+d+'" />')}}f.list_contr.list.find("li").toggleClass("selected",false);var c=$("<li/>").toggleClass("selected",true).hide();c.data("info",f.list_contr.list.data("fields"));f.list_contr.list.append(c);f.show(b,f);f.table.find("input, textarea").val("").empty();c.remove();var h=$('<tr style="border:0;"><td style="border:0;"/><td style="border:0;"/></tr>');f.table.append(h);var a=$('<a id="LE_save" value="save">save</a>').click(function(){f.commit("save")});var e=$('<a id="LE_cancel" value="cancel">cancel</a>').click(function(){f.commit("cancel")});h.children("td").last().append(a);h.children("td").last().append("<br/>");h.children("td").last().append(e)},edit_child:function(b,e){var e=e||this;var f=e.list_contr.list.data().fields;var b=b||{};for(var c in f){if(f.hasOwnProperty(c)&&!(b[c])){b[c]=$('<input type="text" id="'+c+'" />')}}e.show(b,e);var g=$('<tr style="border:0;"><td style="border:0;"/><td style="border:0;"/></<tr>');e.table.append(g);var a=$('<a id="LE_save" value="save">save</a>').click(function(){e.commit("save")});var d=$('<a id="LE_cancel" value="cancel">cancel</a>').click(function(){e.commit("cancel")});g.children("td").last().append(a);g.children("td").last().append("<br/>");g.children("td").last().append(d)},delete_child:function(a,e){var e=e||this;var f=e.list_contr.list.data().fields;var a=a||{};for(var b in f){if(f.hasOwnProperty(b)&&!a[b]){a[b]=$('<div id="'+b+'" />')}}e.show(a,e);var g=$('<tr style="border:0;"><td style="border:0;"/><td style="border:0;"/></<tr>');e.table.append(g);var d=$('<a id="LE_del" type="button" value="delete">delete</a>').click(function(){e.commit("del")});var c=$('<a id="LE_cancel" type="button" value="cancel">cancel</a>').click(function(){e.commit("cancel")});g.children("td").last().append(d);g.children("td").last().append("<br/>");g.children("td").last().append(c)},commit:function(c){var f=this;var b=f.list_contr.http_get_params||"";if(!c||c=="cancel"){this.table.empty();this.list_contr.list.find("li").toggleClass("selected",false);return"cancel"}var h={button:c};var e=this.list_contr.list.data("fields");for(var a in e){if(e.hasOwnProperty(a)){try{var g=f.table.find("#"+a).val()}catch(d){var g=f.table.find("#"+a).text()}if(g==""){g=f.table.find("#"+a).text()}}h[a]=g}debug(h);$.post(this.url,h,function(j){f.hide(true);b=f.http_get_params||"";f.list_contr.update_list(b);jQuery.event.trigger(f.event_type_status,j)},"text")},delegate_show:function(a){var a=a||"click";this.list_contr.list.delegate("li",a,{user:this},function(c){var b=c.data.user;b.selected_item=$(this);b.show_child()})},delegate_hide:function(a){var a=a||"click";this.list_contr.list.delegate("li",a,{user:this},function(c){var b=c.data.user;b.selected_item=undefined;b.hide()})},delegate_click:function(){if(this.click){this.delegate_show("click")}},delegate_hover:function(){if(this.hover){this.delegate_show("mouseenter");this.delegate_hide("mouseleave")}},delegate_links:function(){var a=this;this.list_contr.links.delegate("a","click",function(){if($(this).attr("id")=="new"){a.new_child()}else{if($(this).attr("id")=="edit"){a.edit_child()}else{if($(this).attr("id")=="del"){a.delete_child()}}}})}};var ListMapper={source:null,target:null,init:function(b,c,a){var a=a||this;if(ListController.isPrototypeOf(b)&&ListController.isPrototypeOf(c)){a.source=b;a.target=c}else{throw"init(source, target): Prototype of arguments has to be ListController"}a.delegate_click()},delegate_click:function(a){var a=a||this;a.source.list.delegate("li","click",function(b){a.map()})},map:function(){var a=this.build_params();this.target.update_list(a);this.target.show()},build_params:function(){var c=this.source.get_selected().data().info;var e=this.source.name_tag;var b=this.target.name_tag;var d="?source_id="+e+"&target_id="+b;for(var a in c){if(c.hasOwnProperty(a)){d+="&";d+=encodeURI(a);d+="=";d+=encodeURI(c[a])}}debug(d);return d}};var ListMapperInverse=Object.create(ListMapper);ListMapperInverse.map=function(){var a=this.build_params();a+="&inverse=true";this.target.update_list(a)};var ListExchanger={left:null,right:null,xtra_data:null,url:undefined,event_type_status:"OpDoneStatus",doubleclick:true,enabled:true,init:function(c,a,b){var b=b||this;if(ListController.isPrototypeOf(c)&&ListController.isPrototypeOf(a)){b.left=c;b.right=a}else{throw"init(first, second): Prototype of arguments has to be ListController"}if(b.doubleclick){b.handle_dblclick(b.left);b.handle_mouseover_cursor(b.left,"e-resize");b.handle_dblclick(b.right);b.handle_mouseover_cursor(b.right,"w-resize")}this.left.list.find("li").attr("name","LE_left");this.right.list.find("li").attr("name","LE_right")},toggle:function(a){this.enabled=a||!(this.enabled)},ltr:function(){var a=this.get_selected(this.left);var b=this;$(a).each(function(){b.exchange(this,b.left);$(this).toggleClass("selected",false)})},rtl:function(){var a=this.get_selected(this.right);var b=this;$(a).each(function(){b.exchange(this,b.right);$(this).toggleClass("selected",false)})},get_selected:function(a){return a.get_selected()},get_diff:function(e){var e=e||this.left;var b=this.other_contr(e);var d=[];e.get_all().filter("*[name="+b.identifier+"]").each(function(){d[d.length]=$(this).data("info")});var a=[];b.get_all().filter("*[name="+e.identifier+"]").each(function(){a[a.length]=$(this).data("info")});var c={};if(d.length>0){c.add=d}if(a.length>0){c.del=a}return c},save:function(e){var d=this;var e=e||this.left;var b=d.other_contr(e);var c=d.get_diff(e);if(d.xtra_data){for(var a in d.xtra_data){c[a]=d.xtra_data[a]}}$.post(d.url||e.url,c,function(f){jQuery.event.trigger(d.event_type_status,f)},"text")},exchange:function(b,a){var c=this.other_contr(a);$(b).appendTo($(c.list))},handle_dblclick:function(a){$(a.list).delegate("li","dblclick",{user:this},function(c){var b=c.data.user;if(b.enabled){b.exchange(this,a);$(this).toggleClass("selected",false).mouseover()}})},handle_mouseover_cursor:function(a,b){$(a.list).bind("mouseover",{user:this},function(d){var c=d.data.user;if(c.enabled){$(this).css("cursor",b);$(this).find("li").css("cursor",b)}else{$(this).css("cursor","");$(this).find("li").css("cursor","")}})},other_contr:function(b){var b=b||this.left;if(b==this.left){var a=this.right}else{if(b==this.right){var a=this.left}else{throw"Wrong argument."}}return a}};var ListExchangerSub=Object.create(ListExchanger);ListExchangerSub.exchange=function(b,a){if(a==this.left){var c=this.right}else{if(a==this.right){var c=this.left}}var d=$(b).parent();if(!d){throw"The given item has no parent node id."}var e=$(c.list).find("[id="+d.attr("id")+"]").first();if(e.length==1){$(b).appendTo($(e))}else{$(c.list).append(c.create_child(d.attr("id"),d.attr("id")));e=$(c.list).find("[id="+d.attr("id")+"]").first();$(b).appendTo($(e))}if(d.children().length<1){d.remove()}};