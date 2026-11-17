<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the installation.
 * You don't have to use the web site, you can copy this file to "wp-config.php"
 * and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * Database settings
 * * Secret keys
 * * Database table prefix
 * * Localized language
 * * ABSPATH
 *
 * @link https://wordpress.org/support/article/editing-wp-config-php/
 *
 * @package WordPress
 */

// ** Database settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'local' );

/** Database username */
define( 'DB_USER', 'root' );

/** Database password */
define( 'DB_PASSWORD', 'root' );

/** Database hostname */
define( 'DB_HOST', 'localhost' );

/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8' );

/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );

/**#@+
 * Authentication unique keys and salts.
 *
 * Change these to different unique phrases! You can generate these using
 * the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}.
 *
 * You can change these at any point in time to invalidate all existing cookies.
 * This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define( 'AUTH_KEY',          'a1F^;! Ou5*,r].n4[-VdZ!kxzm|/ZeCJH^gIVkRfSCv.n/qv>PQu2i?[OGo7U:m' );
define( 'SECURE_AUTH_KEY',   '.F@FdB7&ECxC`joW%PQ0P_^#T!0f)C7YREMmZ3uUc{I0]X6osB9TJNH4va_LvDnm' );
define( 'LOGGED_IN_KEY',     '0;QX6p0DtN$iRZUpN+`tqLe^h/3jYLEbXS|1jz?5!htjqlR9AZovam7c9Fj@Jo3<' );
define( 'NONCE_KEY',         '*9DW$;0%{rDP?$_o?G9!O>+J,<gsB)}[1@N~*cCIVgVLJ7nLhxOD<se_{5Bnm7O2' );
define( 'AUTH_SALT',         '@; x&KExhZ>FM&g@kA#!WP;$-H]<:,SJ*M(<AaK1C~E0)KSXLd5O4@Wak<L.sNB*' );
define( 'SECURE_AUTH_SALT',  't$}&|xmN6f=+$P|Igd)Q*{v.|3.8cx_H!)!oN{VrO-,WPfWx2Sj(X{MCM0rHc#8O' );
define( 'LOGGED_IN_SALT',    '15F+{-O<]aS8|piUPMH{{kCK+}qO$S6VIuTi@9j@Iw*prd7Nk!rhbqqQ~rFu$V!{' );
define( 'NONCE_SALT',        '_w[XIN!JA$B)y|nYc!7RxD+3n>,C6UGpV(!;?u5qk}ABRN<Z_[u=8W(e+eU2.2-W' );
define( 'WP_CACHE_KEY_SALT', 'wn{jeelH>.!zJ!VBQe5NSEd@ !uu1Vhsh24.Q*&&7/kWD#e(Uyn_SL3[cj@0X&]&' );


/**#@-*/

/**
 * WordPress database table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix = 'wp_';


/* Add any custom values between this line and the "stop editing" line. */



/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the documentation.
 *
 * @link https://wordpress.org/support/article/debugging-in-wordpress/
 */
if ( ! defined( 'WP_DEBUG' ) ) {
	define( 'WP_DEBUG', false );
}

/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';
