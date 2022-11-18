/**
 * This file is part of MonitoraPA
 *
 * Copyright (C) 2022 Giacomo Tesio <giacomo@tesio.it>
 *
 * MonitoraPA is a hack. You can use it according to the terms and
 * conditions of the Hacking License (see LICENSE.txt)
 */
/* Detect Google Analytics collecting the Tracking ID / Measurement ID
 * as an evidence of its presence
 */
 

var gaName = window.GoogleAnalyticsObject;
if(!gaName)
    gaName = "ga"
if(window[gaName] && window[gaName].q && window[gaName].q[0] && (window[gaName].l||window[gaName].L)){
    // fast track (thanks Augusto Zanellato)
    for(var i = 0; i < window[gaName].q.length; ++i){
        for(var j = 0; j < window[gaName].q[i].length; ++j){
            var candidate = window[gaName].q[i][j];
            if(typeof(candidate) == 'string' && 
              (candidate.indexOf('UA-') == 0 || candidate.indexOf('G-') == 0)){
                return candidate; 
            }
        }
    }
}

// cleanup comments in js
for(var sc of document.getElementsByTagName('script')){
    if(!sc.src) {
        sc.text = sc.text.replaceAll(/\/\/.+/g, "").replaceAll(/\n/g, ' ').replaceAll(/\/\*.*?\*\//g, '');
    }
}
var html = document.all[0].innerHTML;
html = html.replaceAll(/\n/g,' ').replaceAll('ga-disable-UA-', '').replaceAll(/<!--[\s\S]*?-->/g, ''); // cleanup comments in html


var test = html.match(/ga\(['"]create['"],\s*['"]([^'"]*)['"]/);
if(test){
    console.log(`found Google Analytics in html.match(/ga\(['"]create['"],\s*['"]([^'"]*)['"]/)`, test);
    return test[1];
}
test = html.match(/ga\('create',\s*{[^}]*}/gm);
if(test){
    objStr = test[0];
    objStr = objStr.replace ("ga('create',", 'window.MonitoraPAObj = ');
    objStr = objStr.replace ('ga("create",', 'window.MonitoraPAObj = ');
    eval(objStr);
    console.log(`found Google Analytics in html.match(/ga\('create',\s*{[^}]*}/gm);`, window.MonitoraPAObj);
    return window.MonitoraPAObj.trackingId;
}
test = html.match(/gtag\(['"]config['"],\s*['"]([^'"]*)['"]/);
if(test && (test[1].substr(0,3) == "UA-" || test[1].substr(0,2) == "G-")){
    console.log(`found Google Analytics in html.match(/gtag\(['"]config['"],\s*['"]([^'"]*)['"]/)`, test);
    return test[1];
}
test = html.match(/push\(\s*\[\s*['"]_setAccount['"]\s*,\s*['"]([^'"]*)['"]\s*\]/);
if(test && (test[1].substr(0,3) == "UA-" || test[1].substr(0,2) == "G-")){
    console.log(`found Google Analytics in html.match(/push\(\[['"]_setAccount['"], ?['"]([^'"]*)['"]\]/)`, test);
    return test[1];
}

for(var sc of document.getElementsByTagName('script')) {
    if(sc.src.indexOf('googletagmanager') > -1) {
        test = sc.src.match(/UA-[^&]+/);
        if(!test){
            test = sc.src.match(/G-[^&]+/);
        }
        if(test){
            console.log(`found Google Analytics in '${sc.src}'`, test);
            return test[0];
        }
    }
}

for(var sc of document.getElementsByTagName('script')){
    if(sc.src.indexOf('googletagmanager') > -1) {
        var txtFile = monitoraPADownloadResource(sc.src);
        var tId = txtFile.match(/UA-[^'"]+/);
        if(!tId){
            tId = txtFile.match(/G-[^'"]+/);
        }
        if(tId){
            if(tId[0].indexOf('d') == -1){
                console.log(`found Google Analytics inside '${sc.src}'`, tId);
                return tId[0];
            }
        }
    }
}

for(var sc of document.getElementsByTagName('script')) {
    if(!sc.src && sc.text.indexOf('_uacct') > -1){
        var tId = sc.text.match(/UA-[^'"]+/);
        if(!tId){
            tId = sc.text.match(/G-[^'"]+/);
        }
        if(tId){
            if(tId[0].indexOf('d') == -1){
                console.log(`found Google Analytics (old Urchin Tracker) in script '${sc.text}'`, tId);
                return tId[0];
            }
        }
    }
}

return "";
