<!doctype html>
<html <?php language_attributes(); ?>>
<head><meta charset="<?php bloginfo('charset'); ?>"><meta name="viewport" content="width=device-width, initial-scale=1"><?php wp_head(); ?></head>
<body <?php body_class('rf-site'); ?>>
<?php wp_body_open(); ?>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
 <div class="nav-row">
  <a class="brand" href="<?php echo esc_url(home_url('/')); ?>" aria-label="Rahul Fitness home">R<span>F</span><i></i></a>
  <div class="nav-shell">
  <nav class="desktop-nav" aria-label="Main navigation">
   <a href="<?php echo esc_url(home_url('/#programs')); ?>">Training Programs</a>
   <button class="menu-toggle" aria-label="Open navigation menu" aria-expanded="false" aria-controls="navigation-panel"><svg class="menu-grid-icon" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M3 3h5v5H3zm9 0h5v5h-5zM3 12h5v5H3zm9 0h5v5h-5z"/></svg><span class="menu-close-icon" aria-hidden="true">×</span></button>
  </nav>
  <div id="navigation-panel" class="expanded-navigation" hidden>
   <nav class="expanded-links" aria-label="Expanded navigation">
    <a href="<?php echo esc_url(home_url('/#programs')); ?>">Training Programs</a>
    <a href="<?php echo esc_url(home_url('/#about')); ?>">About</a>
    <a href="<?php echo esc_url(home_url('/#contact')); ?>">Contact</a>
   </nav>
   <div class="menu-social"><a href="https://www.instagram.com/real.rahulsaxena/">INSTAGRAM</a><span>•</span><a href="https://www.youtube.com/@rahul77999">YOUTUBE</a><span>•</span><a href="https://www.skool.com/xframe-8914/about">SKOOL COMMUNITY</a></div>
  </div>
  </div>
  <a class="member-link" href="https://www.skool.com/xframe-8914" aria-label="Open Skool member community"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="8" r="3"/><path d="M5 21v-3a7 7 0 0 1 14 0v3"/></svg></a>
 </div>
 <button class="program-finder" data-open-finder>NOT SURE WHERE TO START? <span>FIND YOUR PROGRAM ↗</span></button>
</header>
