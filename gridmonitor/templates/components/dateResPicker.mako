<%def name="dateResolution(start_t_str, end_t_str, resolution)">
<script language="javascript" type="text/javascript"> 

    var req_params = {
            modified: true,
            start_t: "${start_t_str}",
            end_t: "${end_t_str}",
            vo_list: [],
            resolution: "${resolution}",
            resolution_map: {
                'day': 86400,
                'week': 604800,
                'month': 2419200
            }
        };

    $(function() {
        var dates = $( "#from, #to" ).datepicker({
            changeMonth: true,
            numberOfMonths: 1,
            dateFormat: 'dd.mm.yy',
            onSelect: function( selectedDate ) {
                var option = this.id == "from" ? "minDate" : "maxDate";
                var instance = $( this ).data( "datepicker" );
                var _date = $.datepicker.parseDate(
                        instance.settings.dateFormat ||
                        $.datepicker._defaults.dateFormat,
                        selectedDate, instance.settings );
                dates.not( this ).datepicker( "option", option, _date );
            },
            onClose: function(selectedDate) {
                if (this.id == "from" && selectedDate != req_params.start_t){
                    req_params.modified = true; 
                    req_params.start_t = selectedDate;
                } 
                else if (this.id == 'to' && selectedDate != req_params.end_t){
                    req_params.modified = true; 
                    req_params.end_t = selectedDate;
                }
                /*
                else{ 
                    alert("XXX nothing changed");
                }
                */
            }
        });
    });

    $(function(){
        $("#resolution" ).buttonset();
        $("#resolution input").click(function() {
            if (this.id != req_params.resolution){
                req_params.modified = true; 
                req_params.resolution = this.id;
            }
        });
    })

</script>

<table id="ctrl_table">
<tr class='nohover'>
    <td> <label for="from">From</label>

        <input type="text" id="from" name="from" size="12" value="${c.start_t_str}"/>
        <label for="to">to</label>
        <input type="text" id="to" name="to" size="12" value="${c.end_t_str}"/>
    </td>
    <td>
        <div id="resolution">
        Resolution:
                <input type="radio" id="day" name="resolution" checked="checked"/><label for="day">day</label>
                <input type="radio" id="week" name="resolution" /><label for="week">week</label>
                <input type="radio" id="month" name="resolution" /><label for="month">month</label>
        </div>
    </td>
</tr>
</table>


</%def>
