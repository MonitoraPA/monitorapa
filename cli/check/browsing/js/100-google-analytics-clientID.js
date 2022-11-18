/**
 * This file is part of MonitoraPA
 *
 * Copyright (C) 2022 Giacomo Tesio <giacomo@tesio.it>
 *
 * MonitoraPA is a hack. You can use it according to the terms and
 * conditions of the Hacking License (see LICENSE.txt)
 */
if (!window.ga){
    return '';
}
if (window.MonitoraPA['GA_clientID'] !== undefined){
    return window.MonitoraPA['GA_clientID'];
}
monitoraPAWaitForCallback();
setTimeout(function(){
    if(window.MonitoraPA['GA_clientID'] === undefined){
        window.MonitoraPA['GA_clientID'] = '';
        monitoraPACallbackCompleted();
    }
}, 15000);
try{
    ga(function() {
        var allTrackers = ga.getAll();
        var clientIDs = '';
        for(var i = 0; i < allTrackers.length; i++){
            var clientId = allTrackers[i].get('clientId');
            if(clientIDs){
                clientIDs += ' ' + clientId;
            } else {
                clientIDs = clientId;
            }
            console.log(allTrackers[i]);
        }
        window.MonitoraPA['GA_clientID'] = clientIDs;
        monitoraPACallbackCompleted();
    });
} catch (e) {
    monitoraPACallbackCompleted();
    throw e;
}
return window.MonitoraPA['GA_clientID'];
