// Simple helper used by admin-ui.html if you enqueue it
async function fetchBackend(path) {
    const res = await fetch(`/wp-json/gps/v2/proxy?path=${encodeURIComponent(path)}`, {
        headers: { 'X-WP-Nonce': gpspro_nonce }
    });
    return res.json();
}

// Example usage:
// fetchBackend('analytics/livreurs').then(data => console.log(data));
