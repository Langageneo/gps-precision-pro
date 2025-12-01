<?php
/*
Plugin Name: GPS Dashboard Plugin
Description: Dashboard admin GPS pour analytics et gestion livreurs
Version: 1.0
Author: Toi et Moi
*/

if (!defined('ABSPATH')) exit; // Sécurité

// Ajouter le menu admin
add_action('admin_menu', function() {
    add_menu_page(
        'GPS Dashboard',      // Titre de la page
        'GPS Dashboard',      // Titre du menu
        'manage_options',     // Capacité requise
        'gps-dashboard',      // Slug
        'gps_dashboard_page', // Fonction d'affichage
        'dashicons-location', // Icône
        6                     // Position
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

// Enqueue scripts si besoin
add_action('admin_enqueue_scripts', function($hook) {
    if ($hook === 'toplevel_page_gps-dashboard') {
        // Ajouter scripts ou CSS si nécessaire
    }
});

// Endpoint REST API WordPress
add_action('rest_api_init', function () {
    register_rest_route('gps/v1', '/analytics', array(
        'methods' => 'GET',
        'callback' => 'gps_get_analytics',
        'permission_callback' => function() { return current_user_can('manage_options'); }
    ));
});

// Fonction pour récupérer les analytics depuis le backend réel
function gps_get_analytics() {
    $backend_url = 'https://ton-backend.com/api/analytics'; // <- mettre ton backend réel

    $response = wp_remote_get($backend_url, array(
        'timeout' => 15,
        'headers' => array(
            'Accept' => 'application/json'
        )
    ));

    if (is_wp_error($response)) {
        return new WP_Error('backend_error', 'Impossible de récupérer les données du backend', array('status' => 500));
    }

    $body = wp_remote_retrieve_body($response);
    $data = json_decode($body, true);

    if ($data === null) {
        return new WP_Error('backend_error', 'Erreur JSON du backend', array('status' => 500));
    }

    return $data;
}
?>
