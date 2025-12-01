const API = "http://localhost:8000";
document.getElementById('send').addEventListener('click', () => {
  if(!navigator.geolocation) return alert("Pas de géoloc");
  navigator.geolocation.getCurrentPosition(async (pos)=>{
    const payload = {
      device_id: 'chrome-ext-' + (localStorage.deviceId || (localStorage.deviceId=Math.random().toString(36).slice(2))),
      lat: pos.coords.latitude,
      lon: pos.coords.longitude,
      accuracy: pos.coords.accuracy,
      timestamp: Math.floor(Date.now()/1000)
    };
    const r = await fetch(API + '/gps-correct', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
    const j = await r.json();
    document.getElementById('res').innerText = JSON.stringify(j, null, 2);
  }, (err)=>alert(err.message), {enableHighAccuracy:true});
});
