# Instructions for AI Agents & Developers (Codex, Claude, Cursor, Copilot)

This repository contains the source code for the **Rahul Fitness** website and WordPress custom theme.

## Architecture & Directory Structure
```
├── app/
│   └── public/
│       └── wp-content/
│           └── themes/
│               └── rahul-fitness/
│                   ├── assets/          <- JS, fonts, images (site.js, manrope.woff2, etc.)
│                   ├── content/         <- Page content templates (home.html, etc.)
│                   │   ├── home.html
│                   │   ├── x-frame-method.html
│                   │   ├── coaching.html
│                   │   └── diet-plan.html
│                   ├── footer.php       <- Global site footer & inquiry dialogs
│                   ├── functions.php    <- WordPress setup & asset enqueue
│                   ├── header.php       <- Navigation header & metadata
│                   ├── index.php        <- Page template wrapper
│                   └── style.css        <- Complete CSS stylesheet & responsive clamps
├── deploy.py                            <- Static export & deployment script
└── .gitignore                           <- Git exclusion rules
```

## How to Edit This Website

### 1. Editing Text, Content & Sections
* **Home Page:** Edit `app/public/wp-content/themes/rahul-fitness/content/home.html`.
* **Program Pages:**
  * The X Frame Method: `app/public/wp-content/themes/rahul-fitness/content/x-frame-method.html`
  * 1–1 Coaching: `app/public/wp-content/themes/rahul-fitness/content/coaching.html`
  * Diet Plan: `app/public/wp-content/themes/rahul-fitness/content/diet-plan.html`
* **Header & Navigation:** Edit `app/public/wp-content/themes/rahul-fitness/header.php`.
* **Footer & Dialog Popups:** Edit `app/public/wp-content/themes/rahul-fitness/footer.php`.

### 2. Editing Styling & Responsiveness
* All styles reside in `app/public/wp-content/themes/rahul-fitness/style.css`.
* **Mobile Responsiveness Rule:** Headings and cards use dynamic `clamp(...)` rules in `@media(max-width:700px)`. Do not use hardcoded font sizes (e.g. `60px`) for headings; use `clamp()` to prevent horizontal overflow on 320px–375px screens. Always ensure `overflow-wrap: break-word` is preserved.

### 3. Editing Hero Slider & Interactivity
* The slider logic lives in `app/public/wp-content/themes/rahul-fitness/assets/site.js`.
* It includes Previous/Next arrow listeners, dot clicks, 5-second autoplay timer, and touch/mouse drag handlers.

## How to Build & Deploy Updates
Run the included `deploy.py` script from the repository root:

* **To build static output locally (`_site/`):**
  ```bash
  python deploy.py
  ```
* **To build and publish live to GitHub Pages (`gh-pages`):**
  ```bash
  python deploy.py --publish
  ```
* **To push source code changes to GitHub (`main`):**
  ```bash
  git add .
  git commit -m "your descriptive commit message"
  git push origin main
  ```
