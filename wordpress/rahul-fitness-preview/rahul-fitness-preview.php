<?php
/**
 * Plugin Name: Rahul Fitness — Elementor review preview
 * Description: Creates four editable Elementor drafts and shared header/footer templates. No payments, applications or public launch.
 * Version: 1.0.0
 * Requires PHP: 7.4
 * Requires Plugins: elementor
 * License: GPL-2.0-or-later
 */

if (!defined('ABSPATH')) { exit; }

define('RF_PREVIEW_DIR', plugin_dir_path(__FILE__));
define('RF_PREVIEW_URL', plugin_dir_url(__FILE__));

add_action('admin_menu', function () {
    add_management_page('Rahul Fitness preview', 'Rahul Fitness preview', 'manage_options', 'rf-preview', 'rf_preview_admin');
});

function rf_preview_read($name) {
    $path = RF_PREVIEW_DIR . 'templates/' . $name . '.json';
    $data = json_decode(file_get_contents($path), true);
    if (!is_array($data) || !isset($data['content'])) {
        throw new RuntimeException('The bundled template is invalid: ' . $name);
    }
    return $data;
}

function rf_preview_translate_string($value, $routes) {
    $value = str_replace('__RF_ASSET__/', RF_PREVIEW_URL . 'assets/', $value);
    if (isset($routes[$value])) { return $routes[$value]; }
    foreach ($routes as $route => $destination) {
        $value = str_replace('href="' . $route . '"', 'href="' . esc_url($destination) . '"', $value);
    }
    return $value;
}

function rf_preview_translate($value, $routes) {
    if (is_string($value)) { return rf_preview_translate_string($value, $routes); }
    if (is_array($value)) {
        foreach ($value as $key => $child) { $value[$key] = rf_preview_translate($child, $routes); }
    }
    return $value;
}

function rf_preview_write_document($post_id, $template, $routes, $type) {
    update_post_meta($post_id, '_elementor_edit_mode', 'builder');
    update_post_meta($post_id, '_elementor_template_type', $type);
    update_post_meta($post_id, '_elementor_version', ELEMENTOR_VERSION);
    update_post_meta($post_id, '_elementor_data', wp_slash(wp_json_encode(rf_preview_translate($template['content'], $routes))));
    update_post_meta($post_id, '_elementor_page_settings', $template['page_settings'] ?? array());
}

function rf_preview_create() {
    if (!did_action('elementor/loaded')) { throw new RuntimeException('Activate the existing Elementor plugin first.'); }
    $state = get_option('rf_preview_state', array());
    if (!empty($state['complete'])) { return; }
    $files = array('home' => 'Home', 'consultation' => 'One time consultation', 'the-method' => 'The X Frame Method', '1-1-coaching' => '1-1 Coaching with Rahul');
    // Validate the complete payload before creating any WordPress content.
    $templates = array();
    foreach (array_merge(array_keys($files), array('shared-header', 'shared-footer', 'global-styles')) as $file) {
        $templates[$file] = rf_preview_read($file);
    }
    foreach ($files as $slug => $title) {
        if (!empty($state['pages'][$slug]) && get_post($state['pages'][$slug])) { continue; }
        $post_id = wp_insert_post(array('post_title' => $title . ' — Rahul Fitness preview', 'post_name' => $slug === 'home' ? 'rahul-fitness-home' : $slug, 'post_status' => 'draft', 'post_type' => 'page'), true);
        if (is_wp_error($post_id)) { throw new RuntimeException($post_id->get_error_message()); }
        $state['pages'][$slug] = $post_id;
        update_post_meta($post_id, '_wp_page_template', 'rf-preview-canvas.php');
        update_post_meta($post_id, '_rf_preview', 1);
        update_option('rf_preview_state', $state, false);
    }
    foreach (array('shared-header', 'shared-footer', 'global-styles') as $key) {
        if (!empty($state[$key]) && get_post($state[$key])) { continue; }
        $post_id = wp_insert_post(array('post_title' => $templates[$key]['title'], 'post_status' => 'publish', 'post_type' => 'elementor_library'), true);
        if (is_wp_error($post_id)) { throw new RuntimeException($post_id->get_error_message()); }
        $state[$key] = $post_id;
        $type = $key === 'global-styles' ? 'kit' : 'section';
        rf_preview_write_document($post_id, $templates[$key], array(), $type);
        wp_set_object_terms($post_id, $type, 'elementor_library_type');
        update_option('rf_preview_state', $state, false);
    }
    $routes = rf_preview_routes($state);
    foreach ($state['pages'] as $slug => $post_id) { rf_preview_write_document($post_id, $templates[$slug], $routes, 'wp-page'); }
    foreach (array('shared-header', 'shared-footer') as $key) { rf_preview_write_document($state[$key], $templates[$key], $routes, 'section'); }
    $state['complete'] = true;
    update_option('rf_preview_state', $state, false);
    // The active theme, homepage, active Kit and all existing pages remain untouched.
}

function rf_preview_routes($state) {
    $routes = array();
    foreach ($state['pages'] ?? array() as $slug => $id) {
        $post = get_post($id);
        if (!$post) { continue; }
        $routes[$slug === 'home' ? '/' : '/' . $slug . '/'] = $post->post_status === 'publish' ? get_permalink($id) : add_query_arg(array('page_id' => $id, 'preview' => 'true'), home_url('/'));
    }
    return $routes;
}

function rf_preview_admin() {
    if (!current_user_can('manage_options')) { return; }
    $message = '';
    if (isset($_POST['rf_create'])) {
        check_admin_referer('rf_preview_create');
        try { rf_preview_create(); $message = 'Drafts and templates are ready. Review the pages below.'; }
        catch (Throwable $error) { $message = $error->getMessage(); }
    }
    $state = get_option('rf_preview_state', array());
    echo '<div class="wrap"><h1>Rahul Fitness — phase-one preview</h1>';
    echo '<p>Creates four new Elementor draft pages, one shared header, one shared footer and a separate global styles Kit. No existing pages, homepage setting or active Kit are changed.</p>';
    if ($message) { echo '<div class="notice notice-info"><p>' . esc_html($message) . '</p></div>'; }
    if (empty($state['complete'])) {
        echo '<form method="post">'; wp_nonce_field('rf_preview_create');
        submit_button('Create the four editable drafts', 'primary', 'rf_create'); echo '</form>';
    }
    if (!empty($state['pages'])) {
        echo '<h2>Review and edit</h2><p>Draft links work for signed-in editors. These are not public staging pages.</p><ul>';
        foreach ($state['pages'] as $slug => $id) {
            if (!get_post($id)) { continue; }
            echo '<li><strong>' . esc_html(get_the_title($id)) . '</strong> — <a href="' . esc_url(rf_preview_routes($state)[$slug === 'home' ? '/' : '/' . $slug . '/']) . '">Preview</a> · <a href="' . esc_url(admin_url('post.php?post=' . $id . '&action=elementor')) . '">Edit with Elementor</a></li>';
        }
        echo '</ul><h2>Shared templates and design system</h2><ul>';
        foreach (array('shared-header' => 'Shared header', 'shared-footer' => 'Shared footer', 'global-styles' => 'Rahul Fitness global styles Kit') as $key => $label) {
            if (!empty($state[$key])) { echo '<li><a href="' . esc_url(admin_url('post.php?post=' . $state[$key] . '&action=elementor')) . '">' . esc_html($label) . '</a></li>'; }
        }
        echo '</ul><p>The dedicated Kit contains the four global colours and two global type styles. It is not activated automatically. Activate it only on the intended staging site after reviewing its impact. Scoped CSS supplies the preview fallbacks.</p>';
    }
    echo '<h2>Before launch</h2><p>Confirm all marked facts and assets. Specify booking, payment, course access and application processing separately. Set final page URLs and add a permanent redirect from /1-1-coachin/ to /1-1-coaching/ at launch.</p><p>Keep this plugin active while using its shared canvas and assets. Deactivating it leaves the drafts in place. No payments, accounts, applications or browser data are collected.</p></div>';
}

add_filter('theme_page_templates', function ($templates) {
    $templates['rf-preview-canvas.php'] = 'Rahul Fitness preview canvas';
    return $templates;
});
add_filter('template_include', function ($template) {
    if (is_singular('page') && get_post_meta(get_queried_object_id(), '_rf_preview', true)) {
        return RF_PREVIEW_DIR . 'canvas.php';
    }
    return $template;
}, 99);

function rf_preview_is_rendering() {
    if (is_singular('page') && get_post_meta(get_queried_object_id(), '_rf_preview', true)) { return true; }
    $post_id = isset($_GET['elementor-preview']) ? absint($_GET['elementor-preview']) : 0;
    $state = get_option('rf_preview_state', array());
    return $post_id && in_array($post_id, array_merge(array_values($state['pages'] ?? array()), array($state['shared-header'] ?? 0, $state['shared-footer'] ?? 0)), true);
}

add_filter('body_class', function ($classes) { if (rf_preview_is_rendering()) { $classes[] = 'rf'; } return $classes; });
add_action('wp_enqueue_scripts', function () {
    if (!rf_preview_is_rendering()) { return; }
    wp_enqueue_style('rf-preview', RF_PREVIEW_URL . 'assets/styles.css', array(), '1.0.0');
    wp_enqueue_script('rf-preview', RF_PREVIEW_URL . 'assets/site.js', array(), '1.0.0', true);
}, 100);
add_action('wp_head', function () {
    if (rf_preview_is_rendering()) { echo '<meta name="robots" content="noindex,nofollow">'; }
}, 1);

// Resolve shared navigation from current draft IDs so a later slug change cannot break it.
add_filter('elementor/widget/render_content', function ($content, $widget) {
    if (!rf_preview_is_rendering()) { return $content; }
    $state = get_option('rf_preview_state', array());
    if (in_array($widget->get_name(), array('html', 'button'), true)) {
        foreach (rf_preview_routes($state) as $route => $destination) {
            $content = str_replace('href="' . $route . '"', 'href="' . esc_url($destination) . '"', $content);
        }
    }
    if ($widget->get_name() === 'image') {
        $alt = $widget->get_settings('_rf_alt');
        if ($alt) { $content = preg_replace('/alt="[^"]*"/', 'alt="' . esc_attr($alt) . '"', $content, 1); }
        // These tiny local SVG placeholders can load eagerly; revisit when photographs replace them.
        $content = str_replace('loading="lazy"', 'loading="eager"', $content);
    }
    return $content;
}, 10, 2);
