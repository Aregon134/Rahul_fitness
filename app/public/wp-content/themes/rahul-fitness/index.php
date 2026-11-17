<?php get_header(); ?>
<main id="main" class="site-content">
<?php if (have_posts()) : while (have_posts()) : the_post(); ?>
<?php if (!get_post_meta(get_the_ID(), '_rf_initialized', true)) : ?><div class="fallback-title"><h1><?php the_title(); ?></h1></div><?php endif; ?>
<?php the_content(); ?>
<?php endwhile; else : ?><section class="section"><h1>Find your next step.</h1><p>This page could not be found.</p><a class="pill" href="<?php echo esc_url(home_url('/')); ?>">Back to home ↗</a></section><?php endif; ?>
</main>
<?php get_footer(); ?>
