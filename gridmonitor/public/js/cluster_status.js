/*
Used by cluster summary page
to (dynamically) populate/refresh
cluster status information. -> which consists of
Nagios, SFT and Infosys reports.
*/

var refreshClusterMeta = function(){

    $('table#grid_pub_summary tr[id]').each(function(){

        var hostname = $(this).attr('id').replace(/-1-/g, '.');  // replacing '-1-'' with '.'
        var _url = '/json/cluster/get_cluster_meta/' + hostname ;
        
        //var status_td  =  $(this).children('td');
        var status_td  =  $(this).children('td')[1];

        // now fetch metadata about cluster
        $.ajax({
            url: _url,
            type: 'POST',
            dataType: 'json',
            success: function(data){
                // generate qTip entry for 2nd <td>

                var nagios_div = $(status_td).find('div[status=Nagios]');
                var sft_div = $(status_td).find('div[status=SFT]');
                var infosys_div = $(status_td).find('div[status=Infosys]');
                var downtime_div = $(status_td).find('div[status=Downtime]');
                var nsi_div = $(status_td).find('div[group=nsi]');

                if(data['status'] === 'Downtime'){ // scheduled downtime 
                    $(downtime_div).css('display','inline');
                    $(nsi_div).css('display','none');
                }   
                else{
                    $(downtime_div).css('display','none');
                    $(nsi_div).css('display','inline');
                    
                    // qTip for Nagios
                    var _nagios = data['nagios'];

                    var _nagios_status = 'undef_status';
                    for (var ntest in _nagios){
                        if (_nagios[ntest].status == 2){
                            _nagios_status = 'error_status';
                            break;
                        }
                        if (_nagios[ntest].status == 1){
                            _nagios_status = 'warn_status';
                        }
                        if (_nagios_status == 'undef_status' && _nagios[ntest].status == 0){
                                _nagios_status = 'ok_status';
                        }
                    }
                    $(nagios_div).attr('class', _nagios_status);

                    //  qTIP for Infosys
                    switch(data['status']){
                        case 'active':
                            $(infosys_div).attr('class','ok_status');
                            break;
                        case 'inactive':
                            $(infosys_div).attr('class','error_status');
                            break;
                        default:
                            $(infosys_div).attr('class','undef_status');
                    } // switch
                }
            }
        });
        
    });
}

function refreshCallback(){
    var secs = 300;
    setInterval( "refreshClusterMeta()", secs * 1000);
}       
     
$(document).ready(function() {
    refreshClusterMeta();
    refreshCallback();
});

