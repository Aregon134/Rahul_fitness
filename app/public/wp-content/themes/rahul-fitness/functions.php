<?php
if (!defined('ABSPATH')) { exit; }

add_action('after_setup_theme', function () {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('responsive-embeds');
    add_theme_support('editor-styles');
    add_editor_style(array('https://api.fontshare.com/v2/css?f[]=switzer@400,500,600,700&display=swap', 'style.css'));
    register_nav_menus(array('primary' => 'Primary navigation'));
});
add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style('rahul-switzer', 'https://api.fontshare.com/v2/css?f[]=switzer@400,500,600,700&display=swap', array(), null);
    wp_enqueue_style('rahul-fitness', get_stylesheet_uri(), array('rahul-switzer'), (string) filemtime(get_stylesheet_directory() . '/style.css'));
    wp_enqueue_script('rahul-fitness', get_theme_file_uri('assets/site.js'), array(), (string) filemtime(get_stylesheet_directory() . '/assets/site.js'), true);
});

function rf_url($key) {
    $pages = get_option('rf_client_pages', array());
    return isset($pages[$key]) ? get_permalink($pages[$key]) : home_url('/');
}

add_action('admin_menu', function () {
    add_theme_page('Rahul Fitness setup', 'Rahul Fitness setup', 'edit_theme_options', 'rahul-fitness-setup', 'rf_setup_screen');
});
add_action('admin_notices', function () {
    if (current_user_can('edit_theme_options') && !get_option('rf_client_pages')) {
        echo '<div class="notice notice-info"><p>Rahul Fitness is ready. <a href="' . esc_url(admin_url('themes.php?page=rahul-fitness-setup')) . '">Create the four website pages</a>.</p></div>';
    }
});

function rf_setup_screen() {
    if (!current_user_can('edit_theme_options')) { return; }
    $error = '';
    if (isset($_POST['rf_create_pages'])) {
        check_admin_referer('rf_setup_pages');
        $pages = get_option('rf_client_pages', array());
        if (!get_option('rf_previous_frontpage')) {
            update_option('rf_previous_frontpage', array('show_on_front' => get_option('show_on_front'), 'page_on_front' => get_option('page_on_front')));
        }
        $titles = array('home' => 'Home', 'x-frame-method' => 'The X Frame Method', 'coaching' => '1–1 Coaching', 'diet-plan' => 'Diet Plan');
        foreach ($titles as $slug => $title) {
            if (!empty($pages[$slug]) && get_post($pages[$slug])) { continue; }
            $id = wp_insert_post(array('post_title' => $title, 'post_name' => $slug, 'post_type' => 'page', 'post_status' => 'draft'), true);
            if (is_wp_error($id)) { $error = $id->get_error_message(); break; }
            $pages[$slug] = $id;
            update_option('rf_client_pages', $pages);
        }
        if (!$error) {
            $replacements = array('{{assets}}' => esc_url_raw(get_theme_file_uri('assets')));
            foreach ($pages as $slug => $id) { $replacements['{{' . $slug . '}}'] = esc_url_raw(get_permalink($id)); }
            foreach ($pages as $slug => $id) {
                // Existing editor changes are preserved when setup is run again.
                if (get_post_meta($id, '_rf_initialized', true)) { continue; }
                $content = file_get_contents(get_theme_file_path('content/' . $slug . '.html'));
                if ($content === false) { $error = 'Could not read page content.'; break; }
                $result = wp_update_post(wp_slash(array('ID' => $id, 'post_status' => 'publish', 'post_content' => strtr($content, $replacements))), true);
                if (is_wp_error($result)) { $error = $result->get_error_message(); break; }
                update_post_meta($id, '_rf_initialized', 1);
            }
        }
        if (!$error) {
            update_option('show_on_front', 'page');
            update_option('page_on_front', $pages['home']);
            update_option('blogname', 'Rahul Fitness');
            update_option('blogdescription', 'Build your physique naturally.');
            echo '<div class="notice notice-success"><p>The four Rahul Fitness pages are ready. <a href="' . esc_url(home_url('/')) . '">View website</a>.</p></div>';
        }
    }
    echo '<div class="wrap"><h1>Rahul Fitness website</h1><p>Creates Home, The X Frame Method, 1–1 Coaching and Diet Plan, then sets Home as the front page. Other pages and posts are preserved. Repeat runs preserve changes made in the page editor.</p>';
    if ($error) { echo '<div class="notice notice-error"><p>' . esc_html($error) . '</p></div>'; }
    echo '<form method="post">';
    wp_nonce_field('rf_setup_pages');
    submit_button('Create website pages', 'primary', 'rf_create_pages');
    echo '</form><h2>Edit page content</h2><ul>';
    foreach (get_option('rf_client_pages', array()) as $id) {
        echo '<li><a href="' . esc_url(get_edit_post_link($id)) . '">' . esc_html(get_the_title($id)) . '</a></li>';
    }
    echo '</ul><p>X Frame checkout is handled on Skool. Coaching and diet-plan pricing are unconfirmed; these pages do not collect payments or applications.</p></div>';
}
