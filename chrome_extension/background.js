navigator.geolocation.watchPosition(pos => {
    fetch("http://localhost:8000/gps-correct", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            lat: pos.coords.latitude,
            lon: pos.coords.longitude,
            accuracy: pos.coords.accuracy,
            device_id: "chrome-plugin"
        })
    });
});
