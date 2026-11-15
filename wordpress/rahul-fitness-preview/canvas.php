<?php
if (!defined('ABSPATH')) { exit; }
$rf_state = get_option('rf_preview_state', array());
?><!doctype html>
<html <?php language_attributes(); ?>>
<head><meta charset="<?php bloginfo('charset'); ?>"><meta name="viewport" content="width=device-width, initial-scale=1"><?php wp_head(); ?></head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="rf-skip" href="#main">Skip to content</a>
<?php
if (did_action('elementor/loaded') && !empty($rf_state['shared-header'])) {
    echo \Elementor\Plugin::instance()->frontend->get_builder_content_for_display($rf_state['shared-header'], true);
}
?>
<main id="main"><?php while (have_posts()) { the_post(); the_content(); } ?></main>
<?php
if (did_action('elementor/loaded') && !empty($rf_state['shared-footer'])) {
    echo \Elementor\Plugin::instance()->frontend->get_builder_content_for_display($rf_state['shared-footer'], true);
}
?>
<div id="rf-panels"></div>
<?php wp_footer(); ?>
</body></html>
