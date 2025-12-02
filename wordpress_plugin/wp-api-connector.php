<?php
if (!defined('ABSPATH')) exit;

function gpspro_fetch_backend($path) {
    $base = get_option('gpspro_backend_url', 'https://ton-backend.com');
    $url = rtrim($base, '/') . '/' . ltrim($path, '/');
    $response = wp_remote_get($url, ['timeout'=>15]);
    if (is_wp_error($response)) return [];
    $body = wp_remote_retrieve_body($response);
    return json_decode($body, true);
}
?>
