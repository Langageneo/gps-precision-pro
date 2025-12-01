<?php
/*
Plugin Name: GPS Precision Dashboard
Description: Minimal integration with GPS Precision API to embed stats into WP admin
Version: 1.0
Author: YourName
*/

add_action('admin_menu', 'gps_precision_menu');

function gps_precision_menu(){
    add_menu_page('GPS Precision', 'GPS Precision', 'manage_options', 'gps-precision', 'gps_precision_page');
}

function gps_precision_page(){
    $api = get_option('gps_precision_api', 'http://localhost:8000');
    ?>
    <div class="wrap">
      <h1>GPS Precision — Dashboard</h1>
      <div id="gps-app"></div>
      <script>
        async function loadStats(){
          const res = await fetch('<?php echo $api; ?>/analytics');
          const j = await res.json();
          document.getElementById('gps-app').innerText = JSON.stringify(j, null, 2);
        }
        loadStats();
      </script>
    </div>
    <?php
}
