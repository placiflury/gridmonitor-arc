<%def name="job_table(dn, ca, joblist)">
<!-- XXX display job details in pannel or similar inline construct. Currently we need to search 
again for the job, what isn't very efficient O(n)-->

<div id="${dn}_jobscontainer">
<table id="${dn}_jobstable">
    <thead>
        <tr>
          <th>Cluster</th>
          <th>Queue</th>
          <th>Status</th>
          <th>Job</th>
          <th>Id</th>
           <th>Exit Code<th>
        </tr>
    </thead>
    <tbody>
       % for job in joblist:
        <tr>
        <td >${job.get_cluster_name()} </td>
        <td> ${job.get_queue_name()}</td>
        <td> ${job.get_status()}</td>
        <td> ${job.get_jobname()}</td>
        <!-- next we double-escape link...-->
        <!--
        <td><a href="/user/jobdetails/${h.quote_plus(dn)|u}/${h.quote_plus(job.get_globalid())|u}" target="_blank">${job.get_globalid()}</a> 
        </td>  -->         
        <!-- TRIPLE QUOTE -->
        <% dn_escaped = h.quote_plus(h.quote_plus(h.quote_plus(dn)))%>
        <% jobid_escaped = h.quote_plus(h.quote_plus(h.quote_plus(job.get_globalid())))%>
        <td>
        <a href="javascript:poptastic('/user/jobdetails/${dn_escaped}/${jobid_escaped}');">${job.get_globalid()}</a> 
        </td>
          
        <td> ${job.get_exitcode()}</td>
        </tr>
    %endfor
    </tbody>
</table>
</div>

<script type="text/javascript">
var newwindow;
function poptastic(url)
{
    newwindow=window.open(url,'name', 'height= 600, width=750');
    if (window.focus) {newwindow.focus()}
}
</script>

<script type="text/javascript">
YAHOO.util.Event.onAvailable('${dn}_jobscontainer',function(){
    var myColumnDefs = [
        {key:"Cluster", sortable:true},
        {key:"Queue", resizeable:true},
        {key:"Status", sortable:true},
        {key:"Job", sortable:true},
        {key:"Id", sortable:true},
        {key:"Exit Code", sortable:true}
    ];
    var myDataSource = new YAHOO.util.DataSource(YAHOO.util.Dom.get("${dn}_jobstable"));
    
    var myConfigs = {
        paginator : new YAHOO.widget.Paginator({
            rowsPerPage: 20, // REQUIRED

            // use a custom layout for pagination controls
            template: "{PageLinks} Show {RowsPerPageDropdown} per page",

            // show all links
            pageLinks: YAHOO.widget.Paginator.VALUE_UNLIMITED,

            // use these in the rows-per-page dropdown
            rowsPerPageOptions: [10, 20, 40, 80],

            // use custom page link labels
            pageLabelBuilder: function (page,paginator) {
                var recs = paginator.getPageRecords(page);
                return (recs[0] + 1) + ' - ' + (recs[1] + 1 + ' | ');
            }
        }),
        caption:"Job of user with DN: ${dn}",
        summary: "Listing of jobs of user with DN:  ${dn} that could be found in the Grid Information System."

    };
    
    myDataSource.responseType = YAHOO.util.DataSource.TYPE_HTMLTABLE;
    
    myDataSource.responseSchema = {
        fields: [{key:"Cluster"}, {key:"Queue"},{key:"Status"},{key:"Job"},{key:"Id"},{key:"Exit Code"}]
        };

    var myDataTable = new YAHOO.widget.DataTable("${dn}_jobscontainer", myColumnDefs, myDataSource, myConfigs);
});
</script>


</%def>




