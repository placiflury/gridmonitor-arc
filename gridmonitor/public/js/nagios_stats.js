/**
 * @author Placi Flury
 */

var nagiosSummary = function (tag, hlist){
    /* tag -- either cores or ces  */
 
    var _url = '/json/grid/get_nagios_ces_stats';

    if (tag === 'cores'){
        _url = '/json/grid/get_nagios_cores_stats';
    }
    else if (tag == 'ces'){
        _url = '/json/grid/get_nagios_ces_stats';
    }
    else {
        _url = '/json/grid/get_nagios_stats'; /* requires to post a hostlist */
    }
    
    var condShow = function(div_tag, val, _html, _details, _title){
        if (val > 0) {
            div_tag.css('display','inline');
            div_tag.html(_html);
            div_tag.qtip({
                    content: _details,
                    title: { 
                        text: _title
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
                            max:500,
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
                });
        } else {
            div_tag.css('display','none');
            div_tag.html('');
        }  
    };


    $.ajax({
        url: _url,
        type: 'POST',
        dataType: 'json',
        data: {'hostlist': hlist },
        success: function(data){
            var n, host, service;
            var i, _html, _details, _title;


            /** HOSTS SUMMARY **/
            /* UPHOSTS */
            n = data.host_summary.up.length ;
            
            if (n > 0){
                _html = n + ' OK';
                _details = '<table> <tr> <th class="gm">Hostname</th> <th class="gm"> Last Check </th> <th class="gm"> Performance </th></tr>';
                _title = 'Details for Up Hosts'; 
                /* for obj in data.host_summary.up' */
                for(i = 0; i < n; i++){
                    _details += '<tr class="ok_status"><td>' + data.host_summary.up[i].hostname + '</td>';
                    _details += '<td>' + data.host_summary.up[i].date + '</td>' ;
                    _details += '<td>' + data.host_summary.up[i].output + '</td></tr>';
                }
                _details += '</table>';
            }
            condShow($('#' + tag + ' div[status=host_up]'), n, _html, _details, _title);

            /* SCHEDULED DOWN HOSTS */
            n = data.host_summary.scheduleddown.length ;
            _details= '';
            if (n > 0){
                _html = n + ' SCHED. DOWN';
                _details = '<table> <tr> <th class="gm"> Hostname </th> <th class="gm"> Scheduled Downtime </th></tr>';
                _title = 'Details for Scheduled Downtime Hosts'; 
                for(i = 0; i < n; i++){
                    _details += '<tr class="ok_status"><td>' + data.host_summary.scheduleddown[i].hostname + '</td>';
                    _details += '<td>' + data.host_summary.scheduleddown[i].output + '</td></tr>';
                }
                _details += '</table>';
            }
            condShow($('#' + tag + ' div[status=host_sdown]'), n, _html, _details, _title);

            /* DOWN Hosts */
            n = data.host_summary.down.length ;
            _details = '';
            if (n > 0){
                _html = n + ' DOWN';
                _title = 'Details for DOWN hosts'; 
                _details = '<table> <tr> <th class="gm">Hostname</th> <th class="gm"> Last Check </th> <th class="gm"> Performance </th></tr>';
                for(i = 0; i < n; i++){
                    _details += '<tr class="error_status"><td>' + data.host_summary.down[i].hostname + '</td>';
                    _details += '<td>' + data.host_summary.down[i].date + '</td>' ;
                    _details += '<td>' + data.host_summary.down[i].output + '</td></tr>';
                }
                _details += '</table>';
            }
            condShow($('#' + tag + ' div[status=host_down]'), n, _html, _details, _title);

            /* UNKNOWN Hosts */
             n = data.host_summary.unknown.length ;
            _details = '';
            if (n > 0){
                _html = n+ ' UNKNOWN';
                _title = 'Details for UNKNOWN hosts'; 
                _details = '<table> <tr> <th class="gm">Hostname</th> <th class="gm"> Last Check </th> <th class="gm"> Performance </th></tr>';
                for(i = 0; i < n; i++){
                    _details += '<tr class="undef_status"><td>' + data.host_summary.unknown[i].hostname + '</td>';
                    _details += '<td>' + data.host_summary.unknown[i].date + '</td>' ;
                    _details += '<td>' + data.host_summary.unknown[i].output + '</td></tr>';
                }
                _details += '</table>';
            }
            condShow($('#' + tag + ' div[status=host_unknown]'), n, _html, _details, _title);

        /** PLUGINS SUMMARY **/
        
        _details = '';
        n = data.plugins_summary.ok.cnt ;
        if (n > 0){
            _html = n + ' OK';
            _title = 'Services in OK status';

            _details = '<table> <tr> <th class="gm">Hostname</th><th class="gm">Service</th> <th class="gm"> Last Check </th> <th class="gm"> Output</th></tr>';
            for(i = 0; i < n; i++){
                host = data.plugins_summary.ok.hs[i][0];
                service = data.plugins_summary.ok.hs[i][1];
                    _details += '<tr class="ok_status"><td>' + host.replace(/-1-/g, '.') + '</td>';
                    _details += '<td>' + data.service_name_map[service] + '</td>' ;
                    _details += '<td>' + data.details[host][service].last_check+ '</td>';
                    _details += '<td>' + data.details[host][service].output+ '</td></tr>';
            }
            _details += '</table>';
        }
        condShow($('#' + tag + ' div[status=plugins_ok]'), n, _html, _details, _title);
       
         
        _details = '';
        n = data.plugins_summary.warn.cnt ;
        if (n > 0){
            _html = n + ' WARN';
            _title = 'Services in WARN status';
            _details = '<table> <tr> <th class="gm">Hostname</th><th class="gm">Service</th> <th class="gm"> Last Check </th> <th class="gm"> Output</th></tr>';
            for(i = 0; i < n; i++){
                host = data.plugins_summary.warn.hs[i][0];
                service = data.plugins_summary.warn.hs[i][1];
                    _details += '<tr class="warn_status"><td>' + host.replace(/-1-/g, '.') + '</td>';
                    _details += '<td>' + data.service_name_map[service] + '</td>' ;
                    _details += '<td>' + data.details[host][service].last_check+ '</td>';
                    _details += '<td>' + data.details[host][service].output+ '</td></tr>';
            }
            _details += '</table>';
        }
        condShow($('#' + tag + ' div[status=plugins_warn]'), n, _html, _details, _title);
        
        _details = '';
        n = data.plugins_summary.critical.cnt;
        if (n > 0){
            _html = n + ' CRIT';
            _title = 'Services in CRTITICAL status';
            _details = '<table> <tr> <th class="gm">Hostname</th><th class="gm">Service</th> <th class="gm"> Last Check </th> <th class="gm"> Output</th></tr>';
            for(i = 0; i < n; i++){
                host = data.plugins_summary.critical.hs[i][0];
                service = data.plugins_summary.critical.hs[i][1];
                    _details += '<tr class="error_status"><td>' + host.replace(/-1-/g, '.') + '</td>';
                    _details += '<td>' + data.service_name_map[service] + '</td>' ;
                    _details += '<td>' + data.details[host][service].last_check+ '</td>';
                    _details += '<td>' + data.details[host][service].output+ '</td></tr>';
            }
            _details += '</table>';
        }
        condShow($('#' + tag + ' div[status=plugins_crit]'), n, _html, _details, _title);
        
        _details = '';
        n = data.plugins_summary.unknown.cnt;
        if (n > 0){
            _html = n + ' UNKNOWN';
            _title = 'Services in UNKNOWN status';
            _details = '<table> <tr> <th class="gm">Hostname</th><th class="gm">Service</th> <th class="gm"> Last Check </th> <th class="gm"> Output</th></tr>';
            for(i = 0; i < n; i++){
                host = data.plugins_summary.unknown.hs[i][0];
                service = data.plugins_summary.unknown.hs[i][1];
                    _details += '<tr class="undef_status"><td>' + host.replace(/-1-/g, '.') + '</td>';
                    _details += '<td>' + data.service_name_map[service] + '</td>' ;
                    _details += '<td>' + data.details[host][service].last_check+ '</td>';
                    _details += '<td>' + data.details[host][service].output+ '</td></tr>';
            }
            _details += '</table>';
        }
        condShow($('#' + tag + ' div[status=plugins_unknown]'), n, _html, _details, _title);
        
        }
    });
}
