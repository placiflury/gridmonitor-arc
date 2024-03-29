// Debug Flag:
// Set LC_debug to true if you want to see notifications on the console.
var LC_debug = false;
debug = function (log_txt) {
	if (window.console != undefined && LC_debug) {
		console.log(log_txt);
	}
}


// StatusMessageController: Show a Status String in a Box when some events get triggered
/************************************************************************************
event_types: 		[Array] containing all the events that should be bound
							default: ['OpDoneStatus']
container: 			[jQuery Object] refering to a DOM Element that should contain the
									status message
									default: $('body > div')
delay: 				[Int] in ms to keep the status message visible before it disappears

init(that): 		Initialization function (bind event_types)
set(data): 			[String] data contains a string to display (function gets called
					if an event in event_types gets triggered)
*************************************************************************************
Usage: 		(* means optional)
		var my_smc = Object.create(StatusMessageController);
		*my_smc.event_types = ['SpecialEvent', 'AnotherEvent', 'YetAnotherEvent'];
		*my_smc.container = $('div#StatusMessageContainer');  // an existing div with ID StatusMessageContainer
		*my_smc.delay = 4000;
		my_smc.init();
		
*************************************************************************************/
var StatusMessageController = {
	event_types: undefined,		// array
	container: null,
	delay: 3000,
	init: function(that) {
		var that = that || this;
		// Default value if no value is set:
		that.event_types = that.event_types || ['OpDoneStatus'];
		// Default value if some values are set:
		if (that.event_types.indexOf('OpDoneStatus') < 0) {
			that.event_types[that.event_types.length] = 'OpDoneStatus';
		}
		if (!that.container) {
			that.container = $('<div/>').appendTo('body').hide();
		}
		for (i in that.event_types) {
			$(that.container).bind(that.event_types[i], function(event, data) {
				that.set(data);
			});
		}
		$(that.container).ajaxError(function() {
			that.set("ERROR;;;AJAX Request Error.");
		});
		$(that.container).hide();
	},
	set: function(data) {
		var answer = data.split(';;;');
		if (answer.length < 2) {
			var answer = ['UNKNOWN', data];
		}
		if (answer[0] == 'OK') {
			$(this.container).attr('class', 'ok');
		} else if (answer[0] == 'ERROR') {
			$(this.container).attr('class', 'error');
		} else if (answer[0] == 'CRITICAL') {
			$(this.container).attr('class', 'critical');
		} else if (answer[0] == 'WARN') {
			$(this.container).attr('class', 'warn');
		} else {
			$(this.container).attr('class', 'unknown');
		}
		$(this.container).empty().text(answer[1]);
		$(this.container).fadeIn().delay(this.delay).fadeOut();
	}
}



// List Controller for simple listing of admins, sites, services, clusters, vos, tests
/************************************************************************************
(--: meant to be private)
--url:				[String],           A URL to find a JSON object with list data
click:				[Boolean]           Set list elements to clickable or not
container:			[jQuery Object],    The corresponding parent of the list, default appended to body
--title_proto	   	[jQuery Object]
--title:		   	[jQuery Object],    To change the title, use set_title('Text')
--list_proto:	   	[jQuery Object],
--list:				[jQuery Object],    Pointer to the <ul></ul> part
--child_proto:		[jQuery Object],
--link_proto:	   	[jQuery Object],
--links:		   	[jQuery Object],    To set link use set_link('link_id', 'link_text'), to remove link
                                        use set_link('link_id', false) or set_link(false) to remove all links
multiple:			[Boolean],          Enables the possibility to select multiple items
--name_tag:			[String],
--identifier:  		[String]
toggle:				[Boolean]           Enables toggling of selected items if true (unselect selected item)

init(name_tag, url, that):              Call init after having set the optional parameters above.
                                        name_tag: identifier for the kind of the list. Important if used together 
                                                  with ListMapper
                                        url: A URL to find a JSON object with list data
                                        that: internal use only (don't set)
set_title(new_title):                   Sets the text of the title to new_title

set_link(id, link_text):                Set link with ID "id" and text "link_text"
set_link(id):                           Set link with ID "id" and text "id"
set_link(id, false):                    Unset link with id "id"
set_link(false):                        Unset all links
--has_link(id):
--build():
--create_list(http_get_params):
update_list(http_get_params):           Send a HTTP_GET_REQUEST to renew the data of the list with or without http_get_params
--child_text(member, keys):
--create_child(id, child_text):
show():                                 Show list
hide():                                 Hide list
get_selected():                         Returns list of [jQuery Objects] with selected items
get_all():                              Returns all items of the list
--bind_click;():
--handle_click_event(clicked):
**************************************************************************************
Usage:		(* means optional)
	var test = Object.create(ListController);
	*test.container = “DOM Element”;                    // NOTICE: normally this should be set by hand to something like this: $('div#mydiv_id')
	*test.title_proto = “another title prototype“;
	*test.list_proto = “another list prototype“;		// should be some <ul> element
	*test.child_proto = “another child prototype“;		// should be some <li> element
	*test.link_proto = “another link prototype“;
	*test.multiple = true/false;						// select multiple list elements
	*test.click = true/false;							// List elements selectable
	*test.set_link(string id, string link_text, bool remove)	//	id= "new", "edit",
	*test.set_link(string id, bool remove)						//	"del" have special
	*test.set_link(string id, string link_text)					//	meanings
	*test.set_title('Titelzeile:');
	test.init(name_tag, url);			// name_tag: identifier for the generated list.
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
	cursor: undefined,
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
	toggle: false,
	init: function(name_tag, url, that) {
		var that = that || this;
		var my_identifier = Math.random();
		that.identifier = my_identifier.toString().replace(/\W/g, '');
		if (!name_tag || typeof name_tag != 'string') {
			throw 'A ListController object has to be initiated with a valid name_tag.';
		}
		if (!url || typeof url != 'string') {
			throw 'A URL is needed to fetch JSON data.';
		}
		if (!that.cursor) {
			that.cursor = 'pointer'
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
				var new_link = this.link_proto	.clone()
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
			that.list.empty();
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
		// Strip white spaces at beginning and end of String.
		return str.replace(/^\s+|\s+$/g, '');
	},
	create_child: function(id, child_text) {
		return this.child_proto		.clone(true)
									.appendTo(this.list)
									.attr('name', this.identifier)
									.attr('id', id.toString().replace(/\W/g, ''))
									.css('cursor', this.cursor)
									.text(child_text);
	},
	show: function() {
		this.container.show();
	},
	hide: function() {
		this.container.hide();
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
				if (this.toggle) {
					$(clicked).toggleClass('selected', !state);
				} else {
					$(clicked).toggleClass('selected', true);
				}
			} else {
				if (this.toggle) {
					$(clicked).toggleClass('selected');
				} else {
					$(clicked).toggleClass('selected', true);
				}
			}
		}
	},
	
}

// List Controller for simple listing of admins, sites, services, clusters, vos, tests
// appended with the functionality of sub categories
// Only difference to ListController is documented here:
/************************************************************************************
	subchild_proto:			[jQuery Object]
	child_proto:			[jQuery Object]
**************************************************************************************
Usage:		(* means optional)
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
		return this.subchild_proto	.clone()
								.appendTo(parent)
								.attr('id', id.toString().replace(/\W/g, ''))
								.attr('name', this.identifier)
								.css('cursor', this.cursor)
								.text(child_text);
	}


// Prototype of ListEditor: Edit the data of one element of ListController and
// send the changed data to the given url using a HTTP_POST_REQUEST
// If HTTP_POST_REQUEST is successful, event_type_status is triggered.
/************************************************************************************
		(--: Meant to be private)
Variables:
	url:					[String],                // URL where POST request should send post data to
	--list_contr:			[ListController Object], // set with init()
	event_type_status: 		[String]                 // The event type that gets triggered after successful
                                                     //   HTTP-POST-REQUEST, just needed if you want to catch it.
	--selected_item:		[jQuery Object],         
	container:				[jQuery Object],         // jQuery element to be parent of Editor UI. Usually some $('div#mydiv_id')
	flush_container:		[Boolean],               // Set to true if you want to use the same container for more
                                                     //   than one ListEditor
	--table_proto:			[jQuery Object],         
	--table:				[jQuery Object],         // Reference to the <table> object
	new_link:				[Boolean],               // If true, ListEditor will create a link in ListController
	edit_link:				[Boolean],               //   and delegate it with the corresponding function
	del_link:				[Boolean],               //   .
	click:					[Boolean],               // Will set a click delegation handler to every list element to show editor
	hover:					[Boolean],               // Will set a hover delegation handler to every list element to show editor
	                                                 
Methods:
	init(list_contr, that):                          // Call this after having set the options above
                                                     //   list_contr is a reference to the desired ListController or ListControllerSub
	hide(force):                                     // hide(true) will hide the table
	--show(fields, that):
	show_child(fields, that):                        // show data of ListController
	new_child(fields, that):                         // show data of ListController + Buttons save and cancel will be displayed
	edit_child(fields, that):                        // show data of ListController + Buttons save and cancel will be displayed
	delete_child(fields, that):                      // show data of ListController + Buttons delete and cancel will be displayed     
	                                                 //   --> fields is an object to control the field type (eg. fields={key:$('<div/>')})
	--commit(button):                                // commit() is called by buttons save and delete, on successful completion
	                                                 //   event_type_status is triggered.
	--delegate_show(evnt):
	--delegate_hide(evnt):
	--delegate_click():
	--delegate_hover():
	--delegate_links():
**************************************************************************************
Usage:			(* means optional)
	var editor = Object.create(ListEditor);
	*editor.url = "http://my.domain.com/somewhere/";
									// IMPORTANT: Save, change and delete are sent to
									// this url --> set it if you want to change data
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
									// IMPORTANT: This option sets the ListController.multiple to false
									// NOTICE: Either use click or hover (both do not make sense)
	*editor.hover = true;
									// Allows to show the editor by just mouseover on
									// a list element.
									// NOTICE: Either use click or hover (both do not make sense)
	editor.init(my_list_controller);


************************************************************************************/
var ListEditor = {
	url: undefined,
	event_type_status: "OpDoneStatus",
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
			that.list_contr.set_link('new', 'New');
		}
		if (that.edit_link && !(that.list_contr.has_link('edit'))) {
			that.list_contr.set_link('edit', 'Edit');
		}
		if (that.del_link && !(that.list_contr.has_link('del'))) {
			that.list_contr.set_link('del', 'Delete');
		}

		that.delegate_click();
		that.delegate_hover();
		that.delegate_links();
		that.container = that.container || $('body');
		that.table.appendTo(that.container);
	},
	hide: function(force) {
		if (!(this.click) || !(this.list_contr.get_selected()) || force) {
			this.table.empty();
		}
	},
	show: function(fields, that) {
		var that = that || this
		that.table.show();
		that.table.empty();
		if (that.flush_container) {
			that.container.empty();
		}
		var fields = fields || {};
		if (that.click && that.hover) {
			var child_selected = that.list_contr.get_selected() || that.selected_item;
		} else if (that.click) {
			var child_selected = that.list_contr.get_selected();
		} else if (that.hover) {
			var child_selected = that.selected_item;
		} else {
			var child_selected = that.list_contr.get_selected();
		}
		debug(child_selected.data('info'));
		var info = child_selected.data().info;
		var keys = that.list_contr.list.data().order_keys;
		for (var k in keys) {
			if (info.hasOwnProperty(keys[k])) {
				var row = $('<tr><td id="LE_name"/><td id="LE_change"/></tr>');
				that.table.append(row);
				fields[keys[k]] = fields[keys[k]] || $('<div/>');
				row.children('td').first().text(that.list_contr.list.data().fields[keys[k]]);
				var field = fields[keys[k]];
				field.text(info[keys[k]]);
				try {
					field.val(info[keys[k]]); 
					} catch(err) {

					}
				row.children('td').last().append(field);
			}
		}
		that.container.append(that.table);
	},
	show_child: function(fields, that) {
		var that = that || this;
		that.show(fields, that);
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
		that.show(fields, that);
		that.table.find('input, textarea').val('').empty();
		pseudo_selected.remove();
		var row = $('<tr style="border:0;"><td style="border:0;"/><td style="border:0;"/></tr>');
		that.table.append(row);
		var save_button = $('<a id="LE_save" value="save">save</a>')
									.click(function() {
										that.commit('save');
									});
		var cancel_button = $('<a id="LE_cancel" value="cancel">cancel</a>')
									.click(function() {
										that.commit('cancel');
									});
		row.children('td').last().append(save_button);
		row.children('td').last().append('<br/>');
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
		that.show(fields, that);
		var row = $('<tr style="border:0;"><td style="border:0;"/><td style="border:0;"/></<tr>');
		that.table.append(row);
		var save_button = $('<a id="LE_save" value="save">save</a>')
									.click(function() {
										that.commit('save');
									});
		var cancel_button = $('<a id="LE_cancel" value="cancel">cancel</a>')
									.click(function() {
										that.commit('cancel');
									});
		row.children('td').last().append(save_button);
		row.children('td').last().append('<br/>');
		row.children('td').last().append(cancel_button);
	},
	delete_child: function(fields, that) {
		var that = that || this;
		var field_names = that.list_contr.list.data().fields;
		var fields = fields || {};
		for (var k in field_names) {
			if (field_names.hasOwnProperty(k) && !fields[k]) {
				fields[k] = $('<div id="' + k + '" />');
			}
		}
		that.show(fields, that);
		var row = $('<tr style="border:0;"><td style="border:0;"/><td style="border:0;"/></<tr>');
		that.table.append(row);
		var del_button = $('<a id="LE_del" type="button" value="delete">delete</a>')
									.click(function() {
										that.commit('del');
									});
		var cancel_button = $('<a id="LE_cancel" type="button" value="cancel">cancel</a>')
									.click(function() {
										that.commit('cancel');
									});
		row.children('td').last().append(del_button);
		row.children('td').last().append('<br/>');
		row.children('td').last().append(cancel_button);
	},
	commit: function(button) {
		var that = this;
		var http_get_params = that.list_contr.http_get_params || '';
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
					that.hide(true);
					http_get_params = that.http_get_params || "";
					that.list_contr.update_list(http_get_params);
					jQuery.event.trigger(that.event_type_status, data);
			},
			"text"
		);
	},
	delegate_show: function(evnt) {
		var evnt = evnt || 'click';
		this.list_contr.list.delegate('li', evnt, {user:this}, function(event) {
			var that = event.data.user;
			that.selected_item = $(this);
			that.show_child();
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


// Prototype of ListMapper:
// Implements a n:m mapping of two tables
// Clicked element on the source ListController triggers target ListController to update
// itself with data of clicked element as additional HTTP_GET_PARAMS.
/************************************************************************************
Variables:
	--source:				[ListController object]
	--target:				[ListController object]
Methods:
	init(source, target, that)      // source and target: ListController or ListControllerSub
	--delegate_click(that)
	map()                           // Can be used to force update (eg. in combination with ListEditor)
	--build_params()
*************************************************************************************
Usage:
	var my_mapper = Object.create(ListMapper)
	my_mapper.init(my_listcontroller_1, my_listcontroller_2)
	
INFO:	The whole selected source object is sent to the server side via HTTP GET request
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
	delegate_click: function(that) {
		var that = that || this;
		that.source.list.delegate('li', 'click', function(event) {
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
// Prototype of ListMapperInverse
/************************************************************************************
	source:				[ListController object]
	target:				[ListController object]
*************************************************************************************
Usage:
	var my_mapper = Object.create(ListMapper)
	my_mapper.init(my_listcontroller_1, my_listcontroller_2)
	
INFO:	The whole selected source object is sent to the server side via HTTP GET request
		to the url of the target object. The whole logic is on the server side. Only
		difference to ListMapper: parameter inverse=true is also appended to the GET request.
************************************************************************************/
var ListMapperInverse = Object.create(ListMapper);
ListMapperInverse.map = function() {
	var http_get_params = this.build_params();
	http_get_params += '&inverse=true';
	this.target.update_list(http_get_params);
}




// Prototype of List Exchanger:
// Gives the functionality to swap elements of two different ListControllers.
/************************************************************************************
		(--: Meant to be private)
Variables:
	--left:				[ListController object],   // has to be derived from ListController
	--right:		   	[ListController object],   // has to be derived from ListController
	xtra_data: 			[Object] // {key: value}   // additional data to be sent on saving
	url: 				[String]                   // URL to send HTTP_GET_REQUEST to
	event_type_status: 	[String]                   // Event that is triggered on successful complete of HTTP_GET_REQUEST
	doubleclick:		[Boolean],                 // If true: Functionality to swap elements by doubleclicking on them
	--enabled:			[Boolean],
Methods:
	init(left, right, that)                        // Call init() after having set optional params above
	toggle(state)                                  // toggle(), toggle(true), toggle(false) to enable/disable functionality
	ltr()                                          // left to right: Set this on a callback function of a button
	rtl()                                          // right to left: Set this on a callback function of a button
	--get_selected(contr)
	--get_diff()
	--save()                                       // Is triggered by save button
	--exchange(item, contr)
	--handle_dblclick(contr)
	--handle_mouseover_cursor(contr, type)
	--other_contr(orig_contr)
*************************************************************************************
Usage:		(* means optional)
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
	xtra_data: null,	// {key: value}
	url: undefined,
	event_type_status: 'OpDoneStatus',
	doubleclick: true,
	enabled: true,
	init: function(left, right, that) {
		var that = that || this;
		if (ListController.isPrototypeOf(left) && ListController.isPrototypeOf(right)) {
			that.left = left;
			that.right = right;
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
	save: function(orig_contr) {
		var that = this;
		var orig_contr = orig_contr || this.left;
		var other_contr = that.other_contr(orig_contr);
		var site_diff = that.get_diff(orig_contr);
		if (that.xtra_data) {
			for (var key in that.xtra_data) {
				site_diff[key] = that.xtra_data[key];
			}
		}
		$.post(
				that.url || orig_contr.url,
				site_diff,
				function(data) {
					jQuery.event.trigger(that.event_type_status, data);
				},
				"text"
		);
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
	Exactly the same as ListExchanger, but can be used with ListControllerSub:
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
	
	
	
