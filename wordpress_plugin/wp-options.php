<?php
if (!defined('ABSPATH')) exit;

add_action('admin_init', function() {
    register_setting('gpspro_settings', 'gpspro_backend_url');
});

add_action('admin_menu', function() {
    add_submenu_page('gps-dashboard', 'GPS Backend', 'Backend', 'manage_options', 'gps-backend', function() {
        ?>
        <div class="wrap">
            <h1>GPS Backend</h1>
            <form method="post" action="options.php">
                <?php settings_fields('gpspro_settings'); do_settings_sections('gpspro_settings'); ?>
                <table class="form-table">
                    <tr valign="top">
                        <th scope="row">Backend URL</th>
                        <td><input type="text" name="gpspro_backend_url" value="<?php echo esc_attr(get_option('gpspro_backend_url', 'https://ton-backend.com')); ?>" style="width: 400px;"></td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    });
});
?>
