// Debug Flag:
// Set LC_debug to true if you want to see notifications on the console.
var LC_debug = true;
debug = function (log_txt) {
    if (window.console != undefined && LC_debug) {
        console.log(log_txt);
    }
}





/*function get_json_data(url, callback_handle) {
	if (!url) {
		throw 'A URL is needed to fetch JSON data.';
	}
	var json_data = null;
	$.getJSON(url, function(data) {
		json_data = data;
		return json_data;
	});
	if (!json_data['members'] || !json_data['names']) {
		throw 'Fetched JSON data has wrong format.'
	}
	return json_data;
}
*/


// List Controller for simple listing of admins, sites, services, clusters, vos, tests
/************************************************************************************
url: 				[String],
click: 				[Boolean]
container: 			[jQuery Object],
title_proto 		[jQuery Object]
title: 				[jQuery Object],
list_proto: 		[jQuery Object],
list: 				[jQuery Object],
child_proto:		[jQuery Object],
link_proto: 		[jQuery Object],
links: 				[jQuery Object],
multiple: 			[Boolean],
name_tag: 			[String],
identifier: 		[String]
**************************************************************************************
Usage: 		(* means optional)
	var test = Object.create(ListController);
	*test.container = “DOM Element”;
	*test.title_proto = “another title prototype“;
	*test.list_proto = “another list prototype“;  		// should be some <ul> element
	*test.child_proto = “another child prototype“;		// should be some <li> element
	*test.link_proto = “another link prototype“;
	*test.multiple = true/false;						// select multiple list elements
	*test.click = true/false; 							// List elements selectable
	*test.set_link(string id, string link_text, bool remove) 	// 	id= "new", "edit",
	*test.set_link(string id, bool remove)						//	"del" have special
	*test.set_link(string id, string link_text)					//	meanings
	*test.set_title('Titelzeile:');
	test.init(name_tag, url); 			// name_tag: identifier for the generated list.
										// url: valid url where data is stored (JSON)
JSON data format url should return:
	{
	"id_key": "keyX",					// id_key should be a key that uniquely
										// identifies the list element.
										// id_key has to be an existing key,
										// id_key "hash" has a special meaning (key "hash" must exist)
	"show_keys": ["keyX","keyY", ...],
										// show_keys sets the text of the list element
	"order_keys": ["keyY", "keyZ", "keyX", ...],
										// order_keys sets the order of the keys (used by ListEditor)
	"names": {"key1": "Text for key1", "key2": "Text for key2", ...},
										// names maps a human readable string to every key
	"members": [{"key1": "Some", "key2": "thing"},{...},{...}, ...]
										// members is an array of 'key:value' pairs
	}

*************************************************************************************/
var ListController = {
	url: undefined,
	click: true,
	container: undefined,
	title_proto: $('<b/>'),
	title: null,
	list_proto: $('<ul class="LC_list_ul"/>'),
	list: null,
	child_proto:$('<li/>'),
	link_proto: $('<a href="#"/>'),
	links: null,
	multiple: false,
	name_tag: undefined,
	identifier: undefined,
	init: function(name_tag, url, that) {
		var that = that || this; 
		that.identifier = Math.random();
		if (!name_tag || typeof name_tag != 'string') {
			throw 'A ListController object has to be initiated with a valid name_tag.';
		}
		if (!url || typeof url != 'string') {
			throw 'A URL is needed to fetch JSON data.';
		}
		that.name_tag = name_tag;
		that.url = url;
		
		that.list = that.list_proto.clone();
		that.create_list();
		that.set_title();
		that.set_link();
		that.bind_click();
		that.build();
	},
	set_title: function(new_title) {
		// Initialization:
		this.title = this.title || this.title_proto.clone();
		if (new_title != undefined) {
			// Implicit deletion
			var new_title = new_title || '';
			this.title.text(new_title);
		}
	},
	set_link: function(id, link_text) {
		var remove = false;
		if (typeof link_text == 'boolean') {
			remove = !link_text;
		} else if (typeof id == 'boolean') {
			remove = !id;
			id = '*';
		}
		var link_text = link_text || id || '';
		var id = id || 'no_id';
		if (remove) {
			if (id == '*') {
				this.links.empty();
			} else if (id) {
				var old_link = this.links.find('#' + id);
				old_link.remove();
			}
		} else {
			this.links = this.links || $('<div/>');
			if (id && link_text) {
				var new_link = this.link_proto 	.clone()
												.text(link_text)
												.attr('id', id);
				new_link.append($('<br/>'));
				this.links.append(new_link);
			}
		}
	},
	has_link: function(id) {
		return this.links.has('#' + id + '').length > 0;
	},
	build: function() {
		var table = $('<table class="LC_table"/>');
		table.append($('<tr id="LC_title"><td/></tr>'));
		if (this.title) {
			table.find('td').last().append(this.title);
		}
		table.append($('<tr id="LC_list"><td/></tr>'));
		if (this.list) {
			table.find('td').last().append(this.list);
		}
		table.append($('<tr id="LC_links"><td/></tr>'));
		if (this.links) {
			table.find('td').last().append(this.links);
		}
		if (!this.container) {
			table.appendTo($('body'));
		} else {
			table.appendTo(this.container);
		}
	},
	create_list: function(http_get_params) {
		var that = this;
		var http_get_params = http_get_params || '';
		$.getJSON(this.url + http_get_params, function(data) {
			that.list.data('fields', data['names']);
			that.list.data('order_keys', data['order_keys']);
			var mem = data['members']
			for (var i in mem) {
				if (mem.hasOwnProperty(i)){
					var new_child = that.create_child(
							mem[i][data['id_key']],
							that.child_text(mem[i], data['show_keys'])
					);
					if (data['id_key'] == 'hash') {
						new_child.data('hash', mem[i]['hash']);
						delete mem[i]['hash'];
					}
					new_child.data('info', mem[i]);
				}
			}
		});
	},
	update_list: function(http_get_params) {
		this.list.empty();
		this.create_list(http_get_params);
	},
	child_text: function(member, keys) {
		var str = ''
		for (key in keys) {
			if (keys.hasOwnProperty(key)) {
				str += member[keys[key]];
				str += ' ';
			}
		}
		return str;
	},
	create_child: function(id, child_text) {
		return this.child_proto 	.clone(true)
									.appendTo(this.list)
									.attr('name', this.identifier)
									.attr('id', id)
									.text(child_text);
	},
	show: function() {
		this.list.parents('table').show();
	},
	hide: function() {
		this.list.parents('table').hide();
	},
	get_selected: function() {
		var child_selected = this.list.find('li.selected');
		if (child_selected.length < 1) {
			return undefined;
		} else {
			return child_selected;
		}
	},
	get_all: function() {
		return this.list.find('li');
	},
	bind_click: function() {
		this.list.delegate('li', 'click', {user:this}, function(event) {
			var that = event.data.user;
			that.handle_click_event(this);
		});
	},
	handle_click_event: function(clicked) {
		if (this.click) {
			if (this.multiple == false) {
				var state = $(clicked).hasClass('selected');
				this.list.find('li').toggleClass('selected', false);
				$(clicked).toggleClass('selected', !state);
			} else {
				$(clicked).toggleClass('selected');
			}
		}
	},
	
}

// List Controller for simple listing of admins, sites, services, clusters, vos, tests
// appended with the functionality of sub categories
// Only difference to ListController is documented here:
/************************************************************************************
	subchild_proto: 		[jQuery Object]
	child_proto: 			[jQuery Object]
**************************************************************************************
Usage: 		(* means optional)
	same as ListController
The url in the init function should return the following JSON structure:
	{
		"order_keys": ["keyZ", "keyX", "keyY", ... ],
							// the order of the keys when using ListEditorSub
		"parent_key": "keyZ",
							// the key to form groups
		"show_keys": ["keyX", ... ],
							// set the text of the sub list element
		"names": { "keyX": "Name for keyX", ... },
							// Mapping of human readable strings to every key
		"members": [{"keyX":"valueX"},{"keyY":"valueY"}, {}, {}, ... ],
							// 'key:value' pairs with actual data
		"id_key": "keyX"
							// Should uniquely identify the sub list element.
	}

*************************************************************************************/
var ListControllerSub = Object.create(ListController);
	ListControllerSub.subchild_proto = ListControllerSub.__proto__.child_proto;
	ListControllerSub.child_proto = $('<ul/>');
	/*ListControllerSub.init = function(name_tag, url, that) {
		if (!that) { var that = this }
		this.__proto__.init(name_tag, that);
	}*/
	ListControllerSub.create_list = function(http_get_params) {
		var that = this;
		http_get_params = http_get_params || '';
		$.getJSON(this.url + http_get_params, function(data) {
			that.list.data('fields', data['names']);
			that.list.data('order_keys', data['order_keys']);
			var mem = data['members']
			var par = []
			for (var k in mem) {
				if (mem.hasOwnProperty(k)) {
					var par_key = mem[k][data['parent_key']];
					if (($.inArray(par_key, par)) <= -1) {
						par[par.length] = par_key;
						var new_child = that.create_child(par_key, par_key);
						for (var i in mem) {
							if (mem.hasOwnProperty(i) && mem[i][data['parent_key']] == par_key){
								var new_subchild = that.create_subchild(
										mem[i][data['id_key']],
										that.child_text(mem[i], data['show_keys']),
										new_child
								);
								if (data['id_key'] == 'hash') {
									new_subchild.data('hash', mem[i]['hash']);
									delete mem[i]['hash'];
								}
								new_subchild.data('info', mem[i]);
							}
						}
					}
				}
			}
		});
	},
	ListControllerSub.create_subchild = function(id, child_text, parent) {
		return this.subchild_proto 	.clone()
								.appendTo(parent)
								.attr('id', id)
								.attr('name', this.identifier)
								.text(child_text);
	}


// Prototype of ListEditor
/************************************************************************************
	url: 					[String],
	status_container: 		[jQuery Object],
	list_contr: 			[ListController Object],
	selected_item: 			[jQuery Object],
	container: 				[jQuery Object],
	flush_container: 		[Boolean],
	table_proto: 			[jQuery Object],
	table: 					[jQuery Object],
	new_link: 				[Boolean],
	edit_link: 				[Boolean],
	del_link: 				[Boolean],
	click: 					[Boolean],
	hover: 					[Boolean],
**************************************************************************************
Usage:  		(* means optional)
	var editor = Object.create(ListEditor);
	*editor.url = "http://my.domain.com/somewhere/";
									// IMPORTANT: Save, change and delete are sent to
									// this url --> set it if you want to change data
	*editor.status_container = $('#my_status_container');
									// set this to steer where the status messages are
									// shown, otherwise they are displayed in the body
	*editor.container = $('my_editor_container');
									// set this to steer where the editor table should
									// appear, otherwise it's appended to the body
	*editor.flush_container = true;
									// Set this to delete the content of editor.container
									// before setting it.
									// WARNING: Only do this if you have set editor.container
	*editor.new_link = true;
	*editor.edit_link = true;
	*editor.del_link = true;
									// If you set these, the links will be generated
									// --> you don't need to do it by hand.
	*editor.click = true;
									// Allows to show the editor by just clicking on
									// a list element.
									// IMPORTANT: Sets the ListController.multiple to false
	*editor.hover = true;
									// Allows to show the editor by just mouseover on
									// a list element.
	editor.init(my_list_controller);


************************************************************************************/
var ListEditor = {
	url: undefined,
	status_container: null,
	list_contr: null,
	selected_item: null,
	container: undefined,
	flush_container: false,
	table_proto: $('<table class="LE_table"/>'),
	table: null,
	new_link: false,
	edit_link: false,
	del_link: false,
	click: false,
	hover: false,
	init: function(list_contr, that) {
		var that = that || this;
		if (ListController.isPrototypeOf(list_contr)) {
			that.list_contr = list_contr;
		} else {
			throw 'Argument list_contr has to be inherited from ListController.';
		}
		that.url = that.url || list_contr.url;
		// Only allow to select exactly one object in a list with a ListEditor Object pointing to it.
		that.list_contr.multiple = false;

		that.table = that.table_proto.clone();

		if (that.new_link && !(that.list_contr.has_link('new'))) {
			that.list_contr.set_link('new', 'Add new Element');
		}
		if (that.edit_link && !(that.list_contr.has_link('edit'))) {
			that.list_contr.set_link('edit', 'Edit Element');
		}
		if (that.del_link && !(that.list_contr.has_link('del'))) {
			that.list_contr.set_link('del', 'Delete Element');
		}

		that.delegate_click();
		that.delegate_hover();
		that.delegate_links();
		that.container = that.container || $('body');
		that.status_container = that.status_container || $('<div/>').appendTo('body');
		that.table.appendTo(that.container);
	},
	hide: function() {
		if (!(this.click) || !(this.list_contr.get_selected())) {
			this.table.empty();
		}
	},
	show: function(fields) {
		this.table.show();
		this.table.empty();
		if (this.flush_container) {
			this.container.empty();
		}
		var fields = fields || {};
		if (this.click && this.hover) {
			var child_selected = this.list_contr.get_selected() || this.selected_item;
		} else if (this.click) {
			var child_selected = this.list_contr.get_selected();
		} else if (this.hover) {
			var child_selected = this.selected_item;
		}
		debug(child_selected.data('info'));
		var info = child_selected.data().info;
		var keys = this.list_contr.list.data().order_keys;
		for (var k in keys) {
			if (info.hasOwnProperty(keys[k])) {
				var row = $('<tr><td/><td id="LE_change"/></tr>');
				this.table.append(row);
				fields[keys[k]] = fields[keys[k]] || $('<div/>');
				row.children('td').first().text(this.list_contr.list.data().fields[keys[k]]);
				var field = fields[keys[k]];
				field.text(info[keys[k]]);
				try {
					field.val(info[keys[k]]); 
					} catch(err) {

					}
				row.children('td').last().append(field);
			}
		}
		this.container.append(this.table);
	},
	new_child: function(fields, that) {
		var that = that || this;
		var field_names = that.list_contr.list.data().fields;
		var fields = fields || {};
		for (var k in field_names) {
			if (field_names.hasOwnProperty(k) && !(fields[k])) {
				fields[k] = $('<input type="text" id="' + k + '" />');
			}
		}
		that.list_contr.list.find('li').toggleClass('selected', false);
		var pseudo_selected = $('<li/>').toggleClass('selected', true).hide();
		pseudo_selected.data('info', that.list_contr.list.data('fields'));
		that.list_contr.list.append(pseudo_selected);
		that.show(fields);
		that.table.find('input').val('').empty();
		pseudo_selected.remove();
		var row = $('<tr style="border:0;"><td style="border:0;"/><td style="border:0;"/></<tr>');
		that.table.append(row);
		var save_button = $('<input id="LE_save" type="button" value="save"/>')
									.click(function() {
										that.commit('save');
									});
		var cancel_button = $('<input id="LE_cancel" type="button" value="cancel"/>')
									.click(function() {
										that.commit('cancel');
									});
		row.children('td').last().append(save_button);
		row.children('td').last().append(cancel_button);
	},
	edit_child: function(fields, that) {
		var that = that || this;
		var field_names = that.list_contr.list.data().fields;
		var fields = fields || {};
		for (var k in field_names) {
			if (field_names.hasOwnProperty(k) && !(fields[k])) {
				fields[k] = $('<input type="text" id="' + k + '" />');
			}
		}
		that.show(fields);
		var row = $('<tr style="border:0;"><td style="border:0;"/><td style="border:0;"/></<tr>');
		that.table.append(row);
		var save_button = $('<input id="LE_save" type="button" value="save"/>')
									.click(function() {
										that.commit('save');
									});
		var cancel_button = $('<input id="LE_cancel" type="button" value="cancel"/>')
									.click(function() {
										that.commit('cancel');
									});
		row.children('td').last().append(save_button);
		row.children('td').last().append(cancel_button);
	},
	delete_child: function() {
		var that = this;
		var field_names = this.list_contr.list.data().fields;
		var fields = {};
		for (var k in field_names) {
			if (field_names.hasOwnProperty(k)) {
				fields[k] = $('<div id="' + k + '" />');
			}
		}
		this.show(fields);
		var row = $('<tr style="border:0;"><td style="border:0;"/><td style="border:0;"/></<tr>');
		this.table.append(row);
		var del_button = $('<input id="LE_del" type="button" value="delete"/>')
									.click(function() {
										that.commit('del');
									});
		var cancel_button = $('<input id="LE_cancel" type="button" value="cancel"/>')
									.click(function() {
										that.commit('cancel');
									});
		row.children('td').last().append(del_button);
		row.children('td').last().append(cancel_button);
	},
	commit: function(button) {
		var that = this;
		var http_get_params = that.http_get_params || '';
		if (!button || button == 'cancel') {
			this.table.empty();
			this.list_contr.list.find('li').toggleClass('selected', false);
			return 'cancel';
		}
		var member = {'button': button};
		var keys = this.list_contr.list.data('fields');
		for (var k in keys) {
			if (keys.hasOwnProperty(k)) {
				try {
					var value = that.table.find('#' + k).val();
				} catch(err) {
					var value = that.table.find('#' + k).text();
				}
				if (value == "") {
					value = that.table.find('#' + k).text();
				}
			}
			member[k] = value;
		}
		debug(member);
		$.post(
			this.url,
			member,
			function(data) {
				var answer = data.split(';;;');
				if (answer[0] == 'OK') { that.status_container.attr('class', 'ok') }
				else if (answer[0] == 'ERROR') { that.status_container.attr('class', 'critical') }
				that.status_container.text(answer[1]);
				that.status_container.fadeIn().delay(3000).fadeOut();
				that.list_contr.update_list(http_get_params);
				that.table.empty();
				}, "text");
		that.status_container.ajaxError(function() {
		  $(this).attr('class', 'critical').text('AJAX request could not be completed.');
		});
	},
	delegate_show: function(evnt) {
		var evnt = evnt || 'click';
		this.list_contr.list.delegate('li', evnt, {user:this}, function(event) {
			var that = event.data.user;
			that.selected_item = $(this);
			that.show();
		});
	},
	delegate_hide: function(evnt) {
		var evnt = evnt || 'click';
		this.list_contr.list.delegate('li', evnt, {user:this}, function(event) {
			var that = event.data.user;
			that.selected_item = undefined;
			that.hide();
		});
	},
	delegate_click: function() {
		if (this.click) {
			this.delegate_show('click');
		}
	},
	delegate_hover: function() {
		if (this.hover) {
			this.delegate_show('mouseenter');
			this.delegate_hide('mouseleave');
		}
	},
	delegate_links: function() {
		var that = this;
		this.list_contr.links.delegate('a', 'click', function() { 
			if ($(this).attr('id') == 'new') {
				that.new_child();
			} else if ($(this).attr('id') == 'edit') {
				that.edit_child();
			} else if ($(this).attr('id') == 'del') {
				that.delete_child();
			}
		});
	}
}


// Prototype of ListMapper
/************************************************************************************
	source: 			[ListController object]
	target: 			[ListController object]
*************************************************************************************
Usage:
	var my_mapper = Object.create(ListMapper)
	my_mapper.init(my_listcontroller_1, my_listcontroller_2)
	
INFO: 	The whole selected source object is sent to the server side via HTTP GET request
		to the url of the target object. The whole logic is on the server side.
************************************************************************************/
var ListMapper = {
	source: null,		// has to be derived from ListController
	target: null,		// has to be derived from ListController
	init: function(source, target, that) {
		var that = that || this;
		if (ListController.isPrototypeOf(source) && ListController.isPrototypeOf(target)) {
			that.source = source;
			that.target = target;
		} else {
			throw 'init(source, target): Prototype of arguments has to be ListController';
		}
		that.delegate_click();
	},
	delegate_click: function() {
		this.source.list.delegate('li', 'click', {user:this}, function(event) {
			var that = event.data.user;
			that.map();
		});
	},
	map: function() {
		var http_get_params = this.build_params();
		this.target.update_list(http_get_params);
		this.target.show();
	},
	build_params: function() {
		var info = this.source.get_selected().data().info;
		var source_id = this.source.name_tag;
		var target_id = this.target.name_tag;
		var str = '?source_id=' + source_id + '&target_id=' + target_id;
		for (var k in info) {
			if (info.hasOwnProperty(k)) {
				str += '&';
				str += encodeURI(k);
				str += '=';
				str += encodeURI(info[k]);
			}
		}
		debug(str);
		return str;
	}
}
var ListMapperInverse = Object.create(ListMapper);
ListMapperInverse.map = function() {
	var http_get_params = this.build_params();
	http_get_params += '&inverse=true';
	this.target.update_list(http_get_params);
}




// Prototype of List Exchanger
/************************************************************************************
	left: 			[ListController object],			// has to be derived from ListController
	right: 			[ListController object],		// has to be derived from ListController
	doubleclick: 	[Boolean],
	enabled: 		[Boolean],
*************************************************************************************
Usage: 		(* means optional)
	var my_listexchanger = Object.create(ListExchanger)
	*my_listexchanger.doubleclick = false;
	my_listexchanger.init(my_listcontroller_1, my_listcontroller_2)
	*my_listexchanger.toggle(false);
					// If you want to inactivate the controller for some reason.
	*var my_ltr_button = $('<a href="#">left_to_right</a>').appendTo('body');
	*my_ltr_button.click(function() {my_listexchanger.ltr()});
					// If you want to have a button for left to right functionality
	*var my_ltr_button = $('<div>right_to_left</div>').appendTo('body');
	*my_ltr_button.click(function() {my_listexchanger.ltr()});
					// If you want to have a button for left to right functionality
************************************************************************************/
var ListExchanger = {
	left: null,			// has to be derived from ListController
	right: null,		// has to be derived from ListController
	doubleclick: true,
	enabled: true,
	init: function(first, second, that) {
		var that = that || this;
		if (ListController.isPrototypeOf(first) && ListController.isPrototypeOf(second)) {
			that.left = first;
			that.right = second;
		} else {
			throw 'init(first, second): Prototype of arguments has to be ListController';
		}
		if (that.doubleclick) {
			that.handle_dblclick(that.left);
			that.handle_mouseover_cursor(that.left, 'e-resize');
			that.handle_dblclick(that.right);
			that.handle_mouseover_cursor(that.right, 'w-resize');
		}
		this.left.list.find('li').attr('name', 'LE_left');
		this.right.list.find('li').attr('name', 'LE_right');
	},
	toggle: function(state) {
		this.enabled = state || !(this.enabled);
	},
	ltr: function() {
		var items = this.get_selected(this.left);
		var that = this;
		$(items).each(function() {
			that.exchange(this, that.left);
			$(this).toggleClass('selected', false);
		});
	},
	rtl: function() {
		var items = this.get_selected(this.right);
		var that = this;
		$(items).each(function() {
			that.exchange(this, that.right);
			$(this).toggleClass('selected', false);
		});
	},
	get_selected: function(contr) {
		return contr.get_selected();
	},
	get_diff: function(orig_contr) {
		var orig_contr = orig_contr || this.left;
		var other_contr = this.other_contr(orig_contr);
		var add = [];
		orig_contr.get_all().filter('*[name=' + other_contr.identifier + ']').each(function() {
			add[add.length] = $(this).data('info');
		});
		var del = [];
		other_contr.get_all().filter('*[name=' + orig_contr.identifier + ']').each(function() {
			del[del.length] = $(this).data('info');
		});
		var diff = {}
		if (add.length > 0) {
			diff['add'] = add;
		}
		if (del.length > 0) {
			diff['del'] = del;
		}
		return diff;
	},
	exchange: function(item, contr) {
		var new_parent = this.other_contr(contr);
		$(item).appendTo($(new_parent.list));
	},
	handle_dblclick: function(contr) {
		$(contr.list).delegate('li', 'dblclick', {user:this}, function(event) {
			var that = event.data.user;
			if (that.enabled) {
				that.exchange(this, contr);
				$(this).toggleClass('selected', false).mouseover();
			}
		});
	},
	handle_mouseover_cursor: function(contr, type) {
		$(contr.list).bind('mouseover', {user:this}, function(event) {
			var that = event.data.user;
			if (that.enabled) {
				$(this).css('cursor', type);
				$(this).find('li').css('cursor', type);
			} else {
				$(this).css('cursor', '');
				$(this).find('li').css('cursor', '');
			}
		});
	},
	other_contr: function(orig_contr) {
		var orig_contr = orig_contr || this.left;
		if (orig_contr == this.left) {
			var other_contr = this.right;
		} else if (orig_contr == this.right) {
			var other_contr = this.left;
		} else {
			throw 'Wrong argument.'
		}
		return other_contr;
	}
}

// Prototype of ListExchangerSub
/************************************************************************************
Usage:
	Exactly the same as ListExchanger:
	var my_listexchanger = Object.create(ListExchangerSub)
	my_listexchanger.init(my_listcontrollersub_1, my_listcontrollersub_2)
************************************************************************************/
var ListExchangerSub = Object.create(ListExchanger);
	ListExchangerSub.exchange = function(item, contr) {
		if (contr == this.left) {
			var new_parent = this.right;
		}  else if (contr == this.right) {
			var new_parent = this.left;
		}
		var parent_node = $(item).parent();
		if (!parent_node) {
			throw 'The given item has no parent node id.';
		}
		var new_parent_node = $(new_parent.list).find('[id=' + parent_node.attr('id') + ']').first();
		if (new_parent_node.length == 1) {
			$(item).appendTo($(new_parent_node));
		} else {
			$(new_parent.list).append(new_parent.create_child(parent_node.attr('id'), parent_node.attr('id')));
			new_parent_node = $(new_parent.list).find('[id=' + parent_node.attr('id') + ']').first();
			$(item).appendTo($(new_parent_node));
		}
		if (parent_node.children().length < 1) {
			parent_node.remove();
		}
	}
	
	
	
