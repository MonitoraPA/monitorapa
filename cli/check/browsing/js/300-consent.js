/**
 * This file is part of MonitoraPA
 *
 * Copyright (C) 2022 Giacomo Tesio <giacomo@tesio.it>
 *
 * MonitoraPA is a hack. You can use it according to the terms and
 * conditions of the Hacking License (see LICENSE.txt)
 */
/* Detect (and click) Cookie Consent Button and collect its innerText.
 *
 * This check apply some heuristics to identify the consent button.
 */

var consentRegExps = [
    (new RegExp('^ok$', 'i')),
    (new RegExp('accett[iao] tutti', 'i')),
    (new RegExp('accett[iao]', 'i')),
    (new RegExp('acconsent', 'i')),
    (new RegExp('approv[ao]', 'i')),
    (new RegExp('capito', 'i')),
    (new RegExp('va bene', 'i')),
    (new RegExp('chiudi', 'i')),
    (new RegExp('alle akzepti', 'i')),
    (new RegExp('akzepti', 'i')),
    (new RegExp('^accept$', 'i')),
    (new RegExp('^accept all', 'i')),
    (new RegExp('allow', 'i')),
    (new RegExp('got it', 'i')),
    (new RegExp('agree', 'i')),
    (new RegExp('conferm', 'i')),
    (new RegExp('^ho letto$', 'i')),
    (new RegExp('continu', 'i'))
];
var consentElementsToCheck = [
    "button",
    "*[role='button']",
    "input[type='button']",
    "input[type='submit']",
    ".btn", // bootstrap
    "a",
    "span",
    "div"
];

var findElementToClick = function(elements){
    for(var e = elements.length; e > 0 ; --e){
        var element = elements[e-1];
        if(element.innerText.toLowerCase().indexOf('necessari') != -1
        || element.innerText.toLowerCase().indexOf('non ') != -1
        || element.innerText.toLowerCase().indexOf('selezionati') != -1
        || element.innerText.toLowerCase().indexOf('senza') != -1
        || element.innerText.toLowerCase().indexOf('auswahl') != -1){
            continue;
        }
        var elementStyles = window.getComputedStyle(element, null);
        if(elementStyles['visibility'] == 'visible' && element.getClientRects().length > 0){
            var textToTest = element.innerText;
            if(!textToTest && element.value){
                // input type=button with value
                textToTest = element.value;
            }
            for(var i = 0; i < consentRegExps.length; ++i){
                var regexp = consentRegExps[i];
                if(regexp.test(textToTest)){
                    return element;
                }
            }
        }
    }
    return null;
}
function inspectCookieBanner(element){
    for(var i = 0; i < consentElementsToCheck.length; ++i){
        var selector = consentElementsToCheck[i];
        var candidates = element.querySelectorAll(selector);
        var elementToClick = findElementToClick(candidates);
        if(elementToClick){
            return elementToClick;
        }
    }
    return null;
}
var computeZIndex = function(element){
    var zIndexStr = 'auto';
    while(zIndexStr == 'auto'){
        zIndexStr = window.getComputedStyle(element, null)['z-index'];
        element = element.parentElement;
    }
    return parseInt(zIndexStr);
}
var findCookieBanner = function (){
    var elements = document.getElementsByTagName("div");
    var topZIndex = 0;
    var topElement = null;

    for (var candidate of elements) {
        try{
            var zIndex = computeZIndex(candidate);
            if (zIndex > topZIndex 
            && candidate.innerText.toLowerCase().indexOf('cookie') > -1
            && inspectCookieBanner(candidate)) {
                topElement = candidate;
                topZIndex = zIndex;
            }
        } catch {
        }
    }
    
    return topElement;
}

var cookieBanner = findCookieBanner();
if (!cookieBanner){
    return "";
}

var elementToClick = inspectCookieBanner(cookieBanner);
if(!elementToClick){
    return "";
}

console.log("found consent button in ", elementToClick);
monitoraPAClick(elementToClick);
var clickedText = elementToClick.innerText;
if(!clickedText && elementToClick.value){
    // input type=button with value
    clickedText = elementToClick.value;
}
return "<" + clickedText + "> " + cookieBanner.innerText;
