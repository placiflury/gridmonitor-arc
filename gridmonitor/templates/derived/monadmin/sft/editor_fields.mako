%if c.short_identifier == 'test':
	MA_sft_${c.short_identifier}_editor.new_child = function(fields, that) {
		var that = that || this;
		var fields = fields || {};
		that.__proto__.new_child(fields, that);
		fields['xrsl'].removeAttr('disabled');
	}

	MA_sft_${c.short_identifier}_editor.edit_child = function(fields, that) {
		var that = that || this;
		var fields = {};
	
		var name_field = MA_sft_${c.short_identifier}_list.get_selected().data('info').name;
		var xrsl = MA_sft_${c.short_identifier}_list.get_selected().data('info').xrsl;
	
		fields['name'] = $('<div id="name"/>');
		that.__proto__.edit_child(fields, that);
	
		fields['name'].val(undefined).text(name_field);
		fields['xrsl'].val(xrsl);
		fields['xrsl'].removeAttr('disabled');
	}

	MA_sft_${c.short_identifier}_editor.show = function(fields, that) {
		var that = that || this;
		var fields = fields || {};
		fields['xrsl'] = $('<textarea id="xrsl" disabled/>');
		that.__proto__.show(fields, that);
	}
	
	
%elif c.short_identifier == 'cluster':
	MA_sft_${c.short_identifier}_editor.edit_child = function(fields, that) {
		var that = that || this;
		var fields = {};
		var hostname = MA_sft_${c.short_identifier}_list.get_selected().data('info').hostname;
		fields['hostname'] = $('<div id="hostname"/>');
		that.__proto__.edit_child(fields, that);
		fields['hostname'].val(undefined).text(hostname);
	}
	
	
%elif c.short_identifier == 'vo':
	MA_sft_${c.short_identifier}_editor.edit_child = function(fields, that) {
		var that = that || this;
		var fields = {};
		var name_field = MA_sft_${c.short_identifier}_list.get_selected().data('info').name;
		fields['name'] = $('<div id="name"/>');
		that.__proto__.edit_child(fields, that);
		fields['name'].val(undefined).text(name_field);
	}
%endif


















