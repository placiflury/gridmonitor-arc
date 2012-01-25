/**
* Creation of the TO - FROM calendars for SMSCG (tagging of websites
* must be 
*/

YAHOO.namespace("smscg.calendar");

YAHOO.smscg.calendar.init = function(mindate, maxdate) {
    var Dom = YAHOO.util.Dom 
    var inEl = Dom.get('inlinetable') ;

    function handleSelectFrom(type,args,obj) {
        var dates = args[0]; 
        var date = dates[0];
        var year = date[0], month = date[1], day = date[2];
        
        var txtfrom = document.getElementById("start_t_from");
        txtfrom.value = day + "." + month + "." + year;
    }
    
    function handleSelectTo(type,args,obj) {
        var dates = args[0]; 
        var date = dates[0];
        var year = date[0], month = date[1], day = date[2];
        
        var txtto = document.getElementById("end_t");
        txtto.value = day + "." + month + "." + year;
    }
    
    function hideme(e) {
        var el = YAHOO.util.Event.getTarget(e);
        if (el != inEl && !Dom.isAncestor(inEl, el)) {
            document.getElementById("fromContainer").style.display='none';
            document.getElementById("toContainer").style.display='none';
        }
    }

    YAHOO.util.Event.addListener(document, "click", hideme);


    YAHOO.smscg.calendar.cal1 = new YAHOO.widget.Calendar("fromBtn","fromContainer", { 
                                title:"Starting from:", close:true});

    // Correct formats for Germany: dd.mm.yyyy, dd.mm, mm.yyyy
    YAHOO.smscg.calendar.cal1.cfg.setProperty("DATE_FIELD_DELIMITER", ".");

    YAHOO.smscg.calendar.cal1.cfg.setProperty("MDY_DAY_POSITION", 1);
    YAHOO.smscg.calendar.cal1.cfg.setProperty("MDY_MONTH_POSITION", 2);
    YAHOO.smscg.calendar.cal1.cfg.setProperty("MDY_YEAR_POSITION", 3);
    YAHOO.smscg.calendar.cal1.cfg.setProperty("mindate", mindate);
    YAHOO.smscg.calendar.cal1.cfg.setProperty("maxdate", maxdate);


    YAHOO.smscg.calendar.cal1.selectEvent.subscribe(handleSelectFrom, YAHOO.smscg.calendar.cal1, true);
    YAHOO.smscg.calendar.cal1.render();
    
    
    YAHOO.smscg.calendar.cal2 = new YAHOO.widget.Calendar("toBtn","toContainer", { title:"Until:", close:true} );
    
    YAHOO.smscg.calendar.cal2.cfg.setProperty("DATE_FIELD_DELIMITER", ".");

    YAHOO.smscg.calendar.cal2.cfg.setProperty("MDY_DAY_POSITION", 1);
    YAHOO.smscg.calendar.cal2.cfg.setProperty("MDY_MONTH_POSITION", 2);
    YAHOO.smscg.calendar.cal2.cfg.setProperty("MDY_YEAR_POSITION", 3);
    YAHOO.smscg.calendar.cal2.cfg.setProperty("mindate", mindate);
    YAHOO.smscg.calendar.cal2.cfg.setProperty("maxdate", maxdate);

    YAHOO.smscg.calendar.cal2.selectEvent.subscribe(handleSelectTo, YAHOO.smscg.calendar.cal2, true);
    YAHOO.smscg.calendar.cal2.render();

    // Listener to show the 1-up Calendar when the button is clicked
    YAHOO.util.Event.addListener("fromBtn", "click", YAHOO.smscg.calendar.cal1.show, YAHOO.smscg.calendar.cal1, true);
    YAHOO.util.Event.addListener("toBtn", "click", YAHOO.smscg.calendar.cal2.show, YAHOO.smscg.calendar.cal2, true);
    
}
