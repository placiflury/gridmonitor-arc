function showCluster(num_clusters,active_cluster) {
    var prefix = "cluster_" ;
    var prefix2 = "h2_name_";
    var i = 0; 
    for(i= 0; i< num_clusters; i++){
        var objId = prefix+i;
        var objId2 = prefix2+i;
        var cluster_name = document.getElementById(objId);
        var h2_name = document.getElementById(objId2);

        if(objId == active_cluster){
            cluster_name.style.display = '';
            h2_name.style.display = '';
        }else{
            cluster_name.style.display = "none";
            h2_name.style.display = "none";
        }
    }
}


function showUserClusters(access_type) {
    var allElems = document.getElementsByTagName('*');
    var pie_slcs_browser = document.getElementById('pie_slcs_browser_access');
    var pie_slcs = document.getElementById('pie_slcs_access');
    var pie_all = document.getElementById('pie_all');


    for (var i = 0; i < allElems.length; i++) {
        var el= allElems[i];

        if (!(el.className) ||  !(el.className == 'slcs_dn_access' || el.className == 'slcs_access' || el.className == 'no_access' || el.className=='browser_dn' || el.className=="slcs_browser_access")){
            continue;
        }
        if (access_type == 'all'){
            if (pie_all){
                pie_all.style.display='';
                pie_slcs_browser.style.display='none';
                pie_slcs.style.display='none';
            }
            if (el.className == "no_access" || el.className == 'browser_dn_access' || el.className=="slcs_access"  || el.className=="slcs_browser_access"){
                el.style.display = ''; 
                continue;
            }
        }
        
        if (access_type == 'slcs'){
            if (pie_slcs){
                pie_slcs.style.display='';
                pie_slcs_browser.style.display='none';
                pie_all.style.display='none';
            }
            if (el.className == "no_access" || el.className == 'browser_dn_access'){
                el.style.display = 'none'; 
                continue;
            }
            if (el.className == 'slcs_access' || el.className == 'slcs_browser_access'){
                el.style.display='';
                continue
            }
        }

        if (access_type == 'browser_cert'){
            if (pie_slcs_browser){
                pie_slcs.style.display='none';
                pie_slcs_browser.style.display='';
                pie_all.style.display='none';
            }
            if (el.className == "no_access" || el.className == 'slcs_access'){
                el.style.display = 'none'; 
                continue;
            }
            if (el.className == 'browser_dn_access' || el.className == 'slcs_browser_access'){
                el.style.display='';
                continue;
            }
        }
      }      
} 


