/**
 * @author Placi Flury
 */

var UserJobStates = function (html_tag){
 
    var _url = '/json/jobs/get_ucj_states';
    $.ajax({
        url: _url,
        type: 'POST',
        dataType: 'json',
        success: function(data){
            
            var _html = '';
            for (prop in data.summary){
                if (prop != 'total' && data.summary[prop] != 0){
                    _html  += data.summary[prop] + ' ' +  prop + ' '; 
                }
            }
            if(_html == ''){
                _html = "No Jobs found";
            }
            $('#jobs').html(_html);
        }
    });
}


function refreshCallback(){
    var secs = 120;
    setInterval( "UserJobStates()", secs * 1000);
}       
     
$(document).ready(function() {
    UserJobStates();
    refreshCallback();
});


