/**
 * @author Placi Flury
 */


$('div.cluster_details').each(function() {
	var display_name  = $(this).parent('td').attr('display_name');
	$(this).qtip({
		content : {
			text: $(this).html(),
			title: {
				text:'Cluster Details'
				}
		},
		show : {
                 when: { event:'click'}
               },
		hide : {
                when: {event: 'unfocus'},
                delay: 500
                },
		style: { 
      		width:{
      			max:400,
      			min:120
      		},
      	padding: 5,
      	background:'#FFFFFF',
      	color: '#055670',
      	textAlign: 'left',
      	border: {
        	 width: 1,
         	radius: 5,
         	color: '#4682B4'
      	},
      	tip: {
      		corner:'leftTop'
      	}, 
      	 
      name: 'blue' // Inherit the rest of the attributes from the preset dark style
   	}
		
	}).html(display_name).show();
});

$('div[status]').each(function() {
	var _status  = $(this).attr('status');
    var cluster_name = $(this).parents('tr').attr('id').replace(/-1-/g, '.'); 

	$(this).qtip({
		content : {
			//text: $(this).html(), will not display dynamic data
            url: 'json/cluster/get_cluster_meta_table/' + cluster_name + '/' + _status,
            method: 'post',
			title: {
				text:'Status'
				}
		},
		show : {
                 when: { event:'click'}
               },
		hide : {
                when: {event: 'unfocus'},
                delay: 500
                },
		style: { 
      		width:{
      			max:400,
      			min:120
      		},
      	padding: 5,
      	background:'#FFFFFF',
      	color: '#055670',
      	textAlign: 'left',
      	border: {
        	 width: 1,
         	radius: 5,
         	color: '#4682B4'
      	},
      	tip: {
      		corner:'leftTop'
      	},
      	 
      name: 'blue' // Inherit the rest of the attributes from the preset dark style
   	}
		
	}).html(_status).show();
});
