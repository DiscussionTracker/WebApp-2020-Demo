function waitForElm(selector) {
    return new Promise(resolve => {
        if (document.querySelector(selector)) {
            return resolve(document.querySelector(selector));
        }

        const observer = new MutationObserver(mutations => {
            if (document.querySelector(selector)) {
                resolve(document.querySelector(selector));
                observer.disconnect();
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
}

function attachZoom(){
    svgPanZoom("#svg-id",
               {
                   zoomEnabled: true,
                   controlIconsEnabled: true,
                   fit: true,
                   center: true,
                   maxZoom: 100,
                   minZoom: 1,
                   zoomScaleSensitivity: .5
               }
              );
}

function setUpMap(){
    waitForElm("[dtname=collabMap][style*=block]").then(
        function (){ attachZoom();
                     initSetUpMap();
                    });
}

function initSetUpMap(){
    waitForElm("[dtname=collabMap][style*=none]").then(setUpMap);
}

setUpMap();
