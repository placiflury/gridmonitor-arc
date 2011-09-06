/**
 * @author Placi Flury
 */
google.load("visualization", "1", {
	packages : ["corechart"]
});


function drawCPUChart() {
    var data, options, chart;
        
	var json_str = $.ajax({
		url : '/json/grid/gc_cpu_load',
		type : 'post',
        dataType: 'text',
        async: false
	}).responseText;

	
    data = new google.visualization.DataTable(json_str, 0.6);

    options = {
		axisTitlesPosition : 'none',
		backgroundColor : '#ffffff',
		colors : ['#ffa500', '#055670', '#4682b4'],
		width : 250,
		height : 75,
		hAxis : {
            baseline: 0
		},
		isStacked : true,
		legend : 'none',
        title: 'GRID Jobs and Cores'
	};

	chart = new google.visualization.BarChart(document.getElementById('grid_load_cpu'));
	chart.draw(data, options);
}

function drawQueueChart() {
    var data, options, chart;

        
	var json_str = $.ajax({
		url : '/json/grid/gc_queue_load',
		type : 'post',
        dataType: 'text',
        async: false
	}).responseText;

    if (json_str === 'NoQueueError'){ 
       $('#' + tag).html('<div class="error_status"> No Queue </div>');
    }
    else{
        data = new google.visualization.DataTable(json_str, 0.6);

        var options = {
            axisTitlesPosition : 'none',
            backgroundColor : '#ffffff',
            colors : ['#ffa500', '#055670', '#4682b4'],
            width : 250,
            height : 75,
            hAxis:{ 
                baseline: 0
            },
            isStacked : true,
		    legend : 'none',
            title: 'GRID Queueing Backlog'
        };

        var chart = new google.visualization.BarChart(document.getElementById('grid_load_queue'));
        chart.draw(data, options);
    }
}


var generateLoadTable = function(){
    var  _url = '/json/grid/get_grid_load';
    $.ajax({
        url: _url,
        type: 'POST',
        dataType: 'json',
        success: function(data){
            // build table
            _html = '<table summary="Cluster load infobox" class="load_infobox" >' + 
                    '<tbody> <tr class="load_infobox"> <th scope ="col">#Clusters</th>' + 
                    '<th scope="col" >Gridrun</th>' + 
                    '<th scope="col" >Run</th>' +
                    '<th scope="col" >Gridq</th>' + 
                    '<th scope="col" >Localq</th>' +
                    '<th scope="col" >Lrmsq</th> </tr>';
    
            _html += '<tr> <td>' + data['num_clusters']  + '</td>' + 
                     '<td> ' + data['grid_running'] + '</td>' + 
                     '<td> ' + data['running'] + '</td>' + 
                     '<td> ' + data['grid_queued'] + '</td>' + 
                     '<td> ' + data['local_queued'] + '</td>' + 
                     '<td> ' + data['prelrms_queued'] + '</td></tr>';

            // sum of jobs
            _html += '<tr style="border-top-style: double;">' + 
                    ' <td colspan="3">running: ' +  data['running'] + '</td>' + 
                    ' <td colspan="3">gridrunning: ' +  data['grid_running'] + '</td> </tr>' +
                    ' <tr> <td colspan="3"> total jobs: '+  data['running'] +'/'+ data['totaljobs'] + '</td>'+
                    ' <td colspan="3"> used cpus: ' +  data['usedcpus'] +'/' + data['totalcpus'] + '</td></tr></tbody></table>';

           $('td#grid_load_table').html(_html);
        }
    });
}


function _cpuLoadCallback(){
	drawCPUChart();
	drawQueueChart();
    generateLoadTable();
}

function cpuLoadCallback(){
    var secs = 300
    _cpuLoadCallback();
    setInterval( "_cpuLoadCallback()", secs * 1000 );
}

    
google.setOnLoadCallback(cpuLoadCallback);