<?php
/*
Plugin Name: GPS Dashboard Plugin
Description: Dashboard admin GPS pour analytics et gestion livreurs
Version: 2.0
Author: Toi et Moi
*/

if (!defined('ABSPATH')) exit;

// Ajouter le menu admin
add_action('admin_menu', function() {
    add_menu_page(
        'GPS Dashboard',
        'GPS Dashboard',
        'manage_options',
        'gps-dashboard',
        'gps_dashboard_page',
        'dashicons-location',
        6
    );
});

// Affichage dashboard
function gps_dashboard_page() {
    $html_file = plugin_dir_path(__FILE__) . 'admin-ui.html';
    if (file_exists($html_file)) {
        include $html_file;
    } else {
        echo '<h2>Fichier admin-ui.html introuvable.</h2>';
    }
}

// Enqueue scripts
add_action('admin_enqueue_scripts', function($hook) {
    if ($hook === 'toplevel_page_gps-dashboard') {
        wp_enqueue_script('jquery');
    }
});

// Endpoint REST API WordPress pour backend
add_action('rest_api_init', function () {
    register_rest_route('gps/v2', '/analytics', array(
        'methods' => 'GET',
        'callback' => 'gps_get_analytics',
        'permission_callback' => function() { return current_user_can('manage_options'); }
    ));
});

function gps_get_analytics() {
    $backend_url = 'https://ton-backend.com/analytics'; // <- ton backend réel
    $response = wp_remote_get($backend_url, ['timeout' => 15]);
    if (is_wp_error($response)) {
        return new WP_Error('backend_error', 'Impossible de récupérer les données du backend', ['status' => 500]);
    }
    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);
    if ($data === null) {
        return new WP_Error('backend_error', 'Erreur JSON du backend', ['status' => 500]);
    }
    return $data;
}
?>
