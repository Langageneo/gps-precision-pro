<?php
function gpspro_get_stats() {
    $json = file_get_contents("http://localhost:8000/analytics");
    return $json;
}
add_shortcode("gpspro_stats", "gpspro_get_stats");
