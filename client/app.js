// client/app.js
const API = "http://localhost:8000";

function log(msg){ document.getElementById('log').innerText += msg + "\n"; }

document.getElementById('sendBtn').addEventListener('click', () => {
  if(!navigator.geolocation){ log("Geolocation non supportée"); return; }
  navigator.geolocation.getCurrentPosition(async (pos) => {
    const point = {
      device_id: "device-"+(localStorage.deviceId || (localStorage.deviceId=Math.random().toString(36).slice(2))),
      lat: pos.coords.latitude,
      lon: pos.coords.longitude,
      accuracy: pos.coords.accuracy,
      timestamp: Math.floor(Date.now()/1000)
    };
    log("Point local: " + JSON.stringify(point));
    const payload = {
      device_id: point.device_id,
      lat: point.lat,
      lon: point.lon,
      accuracy: point.accuracy,
      timestamp: point.timestamp
    };
    const res = await fetch(API + "/gps-correct", {
      method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(payload)
    });
    const j = await res.json();
    log("Correction reçue: " + JSON.stringify(j));
  }, (err)=>{ log("Erreur GPS: " + err.message); }, {enableHighAccuracy:true});
});
