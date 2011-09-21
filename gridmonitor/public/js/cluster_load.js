/**
 * @author Placi Flury
 */
google.load("visualization", "1", {
	packages : ["corechart"]
});


function drawCPUChart(hostname, tag) {
    var data, options, chart;
        
	var json_str = $.ajax({
		url : '/json/cluster/gc_cpu_load/'+ hostname,
		type : 'post',
        dataType: 'text',
        async: false
	}).responseText;

	
    if (json_str === 'SchedduledDown'){ 
       $('#' + tag).html('<div class="ok_status"> Scheduled Downtime </div>');
    }
    else{
        data = new google.visualization.DataTable(json_str, 0.6);

        options = {
            axisTitlesPosition : 'none',
            backgroundColor : '#ffffff',
            chartArea : {
                left : 10,
                top : 10,
                width : "90%",
                height : "40%"
            },
            colors : ['#ffa500', '#055670', '#4682b4'],
            width : 250,
            height : 75,
            hAxis : {
                textPosition : 'out',
                baseline: 0
            },
            isStacked : true,
            legend : 'none',
            vAxis : {
                title : 'none'
            }
        };

        chart = new google.visualization.BarChart(document.getElementById(tag));
        chart.draw(data, options);
    }
}

function drawQueueChart(hostname, tag) {
    var data, options, chart;

        
	var json_str = $.ajax({
		url : '/json/cluster/gc_queue_load/' + hostname,
		type : 'post',
        dataType: 'text',
        async: false
	}).responseText;

    if (json_str === 'NoQueueError'){ 
       $('#' + tag).html('<div class="error_status"> No Queue </div>');
    }
    else if (json_str === 'SchedduledDown'){ 
       $('#' + tag).html('<div class="ok_status"> Scheduled Downtime </div>');
    }
    else{
        data = new google.visualization.DataTable(json_str, 0.6);

        var options = {
            axisTitlesPosition : 'none',
            backgroundColor : '#ffffff',
            chartArea : {
                left : 50,
                top : 10,
                width : "100%",
                height : "40%"
            },
            colors : ['#ffa500', '#055670', '#4682b4'],
            width : 250,
            height : 75,
            hAxis:{ 
                baseline: 0
            },
            isStacked : true,
        };

        var chart = new google.visualization.BarChart(document.getElementById(tag));
        chart.draw(data, options);
    }
}


var generateLoadTable = function(hostname, tag){
    var  _url = '/json/cluster/get_cluster_load/' + hostname;
    $.ajax({
        url: _url,
        type: 'POST',
        dataType: 'json',
        success: function(data){
            // build table
            _html = '<table summary="Cluster load infobox" class="load_infobox" style="font-size: 4px;">' + 
                    '<tbody> <tr class="load_infobox"> <th scope ="col">Name</th>' + 
                    '<th scope="col" style="font-size: 4px;">Gridrun</th>' + 
                    '<th scope="col" style="font-size: 4px;">Run</th>' +
                    '<th scope="col" style="font-size: 4px;">Gridq</th>' + 
                    '<th scope="col" style="font-size: 4px;">Localq</th>' +
                    '<th scope="col" style="font-size: 4px;">Lrmsq</th> </tr>';
    
            // for each queue
            for(var qname in data['q']){
                _html += '<tr> <td>' + qname  + '</td>' + 
                         '<td> ' + data['q'][qname]['grid_running'] + '</td>' + 
                         '<td> ' + data['q'][qname]['running'] + '</td>' + 
                         '<td> ' + data['q'][qname]['grid_queued'] + '</td>' + 
                         '<td> ' + data['q'][qname]['local_queued'] + '</td>' + 
                         '<td> ' + data['q'][qname]['prelrms_queued'] + '</td></tr>';
            }

            // sum of jobs
            _html += '<tr style="border-top-style: double;">' + 
                    ' <td colspan="3">running:' +  data['cl']['cl_running'] + '</td>' + 
                    ' <td colspan="3">gridrunning:' +  data['cl']['cl_grid_running'] + '</td> </tr>' +
                    ' <tr> <td colspan="3"> total jobs:'+  data['cl']['cl_running'] +'/'+ data['cl']['cl_totaljobs'] + '</td>'+
                    ' <td colspan="3"> used cpus:' +  data['cl']['cl_usedcpus'] +'/' + data['cl']['cl_totalcpus'] + '</td></tr></tbody></table>';

           $('td#'+tag).html(_html);
        }
    });
}

function addTableExpandListener(){

    var swap = function() {
        var ltbs = $('table.load_infobox');
        var ths = $('table.load_infobox th');
        // let all tables change their size
            if($(ltbs).css('font-size') != '4px') {
                $(ltbs).css('font-size', '4px');
                $(ths).css('font-size', '4px');
            } else {
                $(ltbs).css('font-size', '11px');
                $(ths).css('font-size', '11px');
            }
        $('#expand_table').toggle();
        $('#shrink_table').toggle();
        };

    $('#expand_table').click(swap);
    $('#shrink_table').click(swap);
}

function _cpuLoadCallback(){
    $('table#grid_pub_summary tr[id]').each(function(){ 
        var _id = $(this).attr('id');
        var hostname = _id.replace(/-1-/g, '.');  // replacing '-1-' with '.'
        var cpu_tag = _id + '_cpu';
        var queue_tag = _id + '_queue';
        var table_tag = _id + '_table';

	drawCPUChart(hostname, cpu_tag);
	drawQueueChart(hostname, queue_tag);
    generateLoadTable(hostname, table_tag);
    });
}

function cpuLoadCallback(){
    var secs = 300
    _cpuLoadCallback();
    setInterval( "_cpuLoadCallback()", secs * 1000 );
}


$(document).ready(function() {
    cpuLoadCallback();
    addTableExpandListener();
});
    
