let watchId = null;

function startWatch() {
    if (!navigator.geolocation) return;
    watchId = navigator.geolocation.watchPosition(async (pos) => {
        const payload = {
            lat: pos.coords.latitude,
            lon: pos.coords.longitude,
            accuracy: pos.coords.accuracy,
            device_id: "chrome_ext_" + (chrome.runtime.id || 'local')
        };
        try {
            await fetch('https://ton-backend.com/gps-correct', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        } catch (e) {
            console.error("Erreur envoi GPS", e);
        }
    }, (err) => console.error(err), { enableHighAccuracy: true, maximumAge: 5000 });
}

function stopWatch() {
    if (watchId !== null) navigator.geolocation.clearWatch(watchId);
}

chrome.runtime.onInstalled.addListener(() => {
    startWatch();
});
