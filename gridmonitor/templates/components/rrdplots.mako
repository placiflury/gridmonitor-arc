<%def name="rrd_graphs(CE, time_period=['day','week','year'], type='load')">
    <table  cellspacing="0" summary="RRD graphs of ${CE} computing element">
    <caption> 
    %if type == 'load':
        Number of Jobs and Walltime Durations on ${CE}.
    %else:
        Information System Response and Processing Times for ${CE}.
    %endif
    </caption> 
 
    %if type == 'load':
        <!-- GRID LOAD PLOTS --> 
        %if 'day' in time_period:
            <tr id='day_load1'>
            <td>
            <img src="/rrd/${CE}stats_ch24.png" alt="CPU/Cores usage on ${CE}">
            </td>
            </tr>
            <tr id='day_load2'>
            <td>
            <img src="/rrd/${CE}stats_qh24.png" alt="Queue backlog on ${CE}">
            </td>
            </tr>
        %endif
        %if 'week' in time_period:
            <tr id='week_load1'>
            <td>
            <img src="/rrd/${CE}stats_cw1.png" alt="CPU/Cores usage on ${CE}">
            </td>
            </tr>
            <tr id='week_load2'>
            <td>
            <img src="/rrd/${CE}stats_qw1.png" alt="Queue backlog on ${CE}">
            </td>
            </tr>
        %endif
        %if 'year' in time_period:
            <tr id='year_load1'>
            <td>
            <img src="/rrd/${CE}stats_cy1.png" alt="CPU/Cores usage on ${CE}">
            </td>
            </tr>
            <tr id='year_load2'>
            <td>
            <img src="/rrd/${CE}stats_qy1.png" alt="Queue backlog on ${CE}">
            </td>
            </tr>
        %endif
    %else:
        <!-- INFORMATION SYSTEM PLOTS --> 
        %if 'day' in time_period:
            <tr id='day_infosys1'>
            <td>
            <img src="/rrd/${CE}_h24r.png" alt="Response time of GRIS: ${CE}">
            </td>
            <td>
            <img src="/rrd/${CE}_h24p.png" alt="Processing time of GRIS: ${CE}">
            </td>
            </tr>
        %endif
        %if 'week' in time_period:
            <tr id='week_infosys1'>
            <td>
            <img src="/rrd/${CE}_w1r.png" alt="Response time of GRIS: ${CE}">
            </td>
            <td>
            <img src="/rrd/${CE}_w1p.png" alt="Processing time of GRIS: ${CE}">
            </td>
            </tr>
        %endif
        %if 'year' in time_period:
            <tr id='year_infosys1'>
            <td>
            <img src="/rrd/${CE}_y1r.png" alt="Response time of GRIS: ${CE}">
            </td>
            <td>
            <img src="/rrd/${CE}_y1p.png" alt="Processing time of GRIS: ${CE}">
            </td>
            </tr>
        %endif
    %endif
    
    </table>
</%def>
