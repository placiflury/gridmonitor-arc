var newwindow;

function poptastic(url){
    newwindow=window.open(url,'name', 'height= 800, width=750');
    if (window.focus) {newwindow.focus()}
}


function new_small_win(url){
    newwindow=window.open(url,'GridMonitor', 'height= 700, width=550');
    if (window.focus) {newwindow.focus()}
}

function new_big_resize_win(url){
    newwindow=window.open(url,'GridMonitor', 'height= 800, width=920, scrollbars');
    if (window.focus) {newwindow.focus()}
}

