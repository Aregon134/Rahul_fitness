#!/usr/bin/env python3
"""
Deploy & Static Export Script for Rahul Fitness
Usage:
  python deploy.py            # Builds static site in _site/
  python deploy.py --publish  # Builds and deploys directly to origin/gh-pages
"""

import sys
import os
import subprocess
import urllib.request
import re
import shutil
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
THEME_DIR = ROOT_DIR / "app" / "public" / "wp-content" / "themes" / "rahul-fitness"
LOCAL_THEME_DIR = Path(r"C:\Users\kusha\Local Sites\rahulfitness\app\public\wp-content\themes\rahul-fitness")
OUT_DIR = ROOT_DIR / "_site"
THEME_ASSETS = THEME_DIR / "assets"
THEME_STYLE = THEME_DIR / "style.css"

PAGES = [
    ("", "index.html", "./", "home", "Rahul Fitness – Build your physique naturally."),
    ("x-frame-method/", "x-frame-method/index.html", "../", "x-frame-method", "The X Frame Method – Rahul Fitness"),
    ("coaching/", "coaching/index.html", "../", "coaching", "1–1 Coaching – Rahul Fitness"),
    ("diet-plan/", "diet-plan/index.html", "../", "diet-plan", "Diet Plan – Rahul Fitness"),
]

def sync_to_local_wp():
    """Sync edits made in this repo to the LocalWP theme directory if it exists."""
    if LOCAL_THEME_DIR.exists():
        try:
            print("Syncing theme files to LocalWP...")
            for src in [THEME_STYLE, THEME_ASSETS]:
                dst = LOCAL_THEME_DIR / src.name
                if src.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
            # Also sync content/ folder
            content_src = THEME_DIR / "content"
            content_dst = LOCAL_THEME_DIR / "content"
            if content_src.exists():
                shutil.copytree(content_src, content_dst, dirs_exist_ok=True)
            print("Sync to LocalWP complete.")
        except Exception as e:
            print(f"Notice: Could not sync to LocalWP directory: {e}")

def clean_html(html_str, base, version):
    html_str = re.sub(r'<link\s+rel=[\'"](?:EditURI|alternate|https://api\.w\.org/|shortlink)[\'"][^>]*>', '', html_str)
    html_str = re.sub(r'/\*# sourceURL=[^\*]+\*/', '', html_str)
    html_str = re.sub(r'//# sourceURL=[^\n]+', '', html_str)
    
    html_str = re.sub(r'<script\b[^>]*id=[\'"]wp-emoji-settings[\'"][^>]*>[\s\S]*?</script>', '', html_str)
    html_str = re.sub(r'<script\b[^>]*type=[\'"]module[\'"][^>]*>[\s\S]*?wpemojiSettings[\s\S]*?</script>', '', html_str)
    html_str = re.sub(r'<script\b[^>]*type=[\'"]speculationrules[\'"][^>]*>[\s\S]*?</script>', '', html_str)
    
    html_str = re.sub(r'http://rahulfitness\.local/wp-content/themes/rahul-fitness/assets/', f'{base}assets/', html_str)
    html_str = re.sub(r'http://rahulfitness\.local/wp-content/themes/rahul-fitness/style\.css(?:\?ver=[^"\'\s>]*)?', f'{base}style.css?v={version}', html_str)
    
    html_str = re.sub(r'http://rahulfitness\.local/\?page_id=7', f'{base}x-frame-method/', html_str)
    html_str = re.sub(r'http://rahulfitness\.local/x-frame-method/?', f'{base}x-frame-method/', html_str)
    
    html_str = re.sub(r'http://rahulfitness\.local/\?page_id=8', f'{base}coaching/', html_str)
    html_str = re.sub(r'http://rahulfitness\.local/coaching/?', f'{base}coaching/', html_str)
    
    html_str = re.sub(r'http://rahulfitness\.local/\?page_id=9', f'{base}diet-plan/', html_str)
    html_str = re.sub(r'http://rahulfitness\.local/diet-plan/?', f'{base}diet-plan/', html_str)
    
    html_str = re.sub(r'http://rahulfitness\.local/#', f'{base}#', html_str)
    html_str = re.sub(r'http://rahulfitness\.local/?(?=["\'])', f'{base}', html_str)
    
    html_str = re.sub(r'assets/site\.js(?:\?ver=[^"\'\s>]*)?', f'assets/site.js?v={version}', html_str)
    html_str = re.sub(r'<meta name=[\'"]robots[\'"][^>]*>', '', html_str)

    if 'assets/site.js' not in html_str:
        html_str = html_str.replace('</body>', f'<script src="{base}assets/site.js?v={version}"></script>\n</body>')
    
    return html_str

def build_offline_page(slug, base, title, version):
    """Fallback compiler that renders directly from theme templates and content/*.html."""
    header_path = THEME_DIR / "header.php"
    footer_path = THEME_DIR / "footer.php"
    content_path = THEME_DIR / "content" / f"{slug}.html"
    
    if not content_path.exists():
        raise FileNotFoundError(f"Content file missing: {content_path}")

    header = header_path.read_text(encoding='utf-8')
    footer = footer_path.read_text(encoding='utf-8')
    body = content_path.read_text(encoding='utf-8')

    # Replace content tokens
    replacements = {
        '{{assets}}': f"{base}assets",
        '{{x-frame-method}}': f"{base}x-frame-method/",
        '{{coaching}}': f"{base}coaching/",
        '{{diet-plan}}': f"{base}diet-plan/",
    }
    for k, v in replacements.items():
        body = body.replace(k, v)

    # Convert header.php to static HTML
    header = re.sub(r'<\?php language_attributes\(\); \?>', 'lang="en-US"', header)
    header = re.sub(r'<\?php bloginfo\(\'charset\'\); \?>', 'UTF-8', header)
    
    head_injections = f"""<title>{title}</title>
<link rel='dns-prefetch' href='//api.fontshare.com' />
<link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=switzer@400,500,600,700&display=swap">
<link rel="stylesheet" href="{base}style.css?v={version}">"""
    
    header = re.sub(r'<\?php wp_head\(\); \?>', head_injections, header)
    header = re.sub(r'<\?php body_class\(\'rf-site\'\); \?>', f'class="page-{slug} rf-site"', header)
    header = re.sub(r'<\?php wp_body_open\(\); \?>', '', header)
    header = re.sub(r'<\?php echo esc_url\(home_url\(\'/\'\)\); \?>', f'{base}', header)
    header = re.sub(r'<\?php echo esc_url\(home_url\(\'/#programs\'\)\); \?>', f'{base}#programs', header)
    header = re.sub(r'<\?php echo esc_url\(home_url\(\'/#about\'\)\); \?>', f'{base}#about', header)
    header = re.sub(r'<\?php echo esc_url\(home_url\(\'/#contact\'\)\); \?>', f'{base}#contact', header)

    # Convert footer.php to static HTML
    footer = re.sub(r'<\?php echo esc_url\(home_url\(\'/\'\)\); \?>', f'{base}', footer)
    footer = re.sub(r'<\?php echo esc_url\(rf_url\(\'x-frame-method\'\)\); \?>', f'{base}x-frame-method/', footer)
    footer = re.sub(r'<\?php echo esc_url\(rf_url\(\'coaching\'\)\); \?>', f'{base}coaching/', footer)
    footer = re.sub(r'<\?php echo esc_url\(rf_url\(\'diet-plan\'\)\); \?>', f'{base}diet-plan/', footer)
    footer = re.sub(r'<\?php echo esc_html\(wp_date\(\'Y\'\)\); \?>', '2026', footer)
    
    script_injections = f"""<script src="{base}assets/site.js?v={version}"></script>"""
    footer = re.sub(r'<\?php wp_footer\(\); \?>', script_injections, footer)

    full_html = f"{header}\n<main id=\"main\" class=\"site-content\">\n{body}\n</main>\n{footer}"
    return full_html

def export_site():
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    shutil.copytree(THEME_ASSETS, OUT_DIR / "assets")
    shutil.copy2(THEME_STYLE, OUT_DIR / "style.css")
    (OUT_DIR / ".nojekyll").touch()

    version = str(int(time.time()))

    # Check if LocalWP is accessible
    use_local_wp = False
    try:
        test_url = "http://127.0.0.1:10004/"
        test_req = urllib.request.Request(test_url, headers={'Host': 'rahulfitness.local'})
        with urllib.request.urlopen(test_req, timeout=1.5):
            use_local_wp = True
            print("Connected to LocalWP (http://127.0.0.1:10004). Scraping live WordPress output...")
    except Exception:
        print("LocalWP not detected on port 10004. Assembling directly from theme template files...")

    for wp_path, out_file_rel, base, slug, title in PAGES:
        if use_local_wp:
            url = f"http://127.0.0.1:10004/{wp_path}"
            req = urllib.request.Request(url, headers={'Host': 'rahulfitness.local'})
            with urllib.request.urlopen(req) as resp:
                content = resp.read().decode('utf-8')
            cleaned = clean_html(content, base, version)
        else:
            cleaned = build_offline_page(slug, base, title, version)

        out_file = OUT_DIR / out_file_rel
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(cleaned, encoding='utf-8')
        print(f"Exported {out_file_rel} ({len(cleaned)} bytes, site.js: {'site.js' in cleaned})")

    print(f"Static build complete in {OUT_DIR}")

def publish_gh_pages():
    import tempfile
    temp_dir = Path(tempfile.gettempdir()) / "rf-gh-pages"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    print("Deploying to gh-pages branch...")
    subprocess.run(["git", "worktree", "add", str(temp_dir), "gh-pages"], check=True)
    try:
        for item in OUT_DIR.iterdir():
            dst = temp_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dst)
        
        subprocess.run(["git", "-C", str(temp_dir), "add", "-A"], check=True)
        status_out = subprocess.check_output(["git", "-C", str(temp_dir), "status", "--porcelain"], text=True)
        if not status_out.strip():
            print("No changes to publish to gh-pages.")
        else:
            subprocess.run(["git", "-C", str(temp_dir), "commit", "-m", "deploy: update live site build"], check=True)
            subprocess.run(["git", "-C", str(temp_dir), "push", "origin", "gh-pages"], check=True)
            print("Successfully deployed to GitHub Pages! https://aregon134.github.io/Rahul_fitness/")
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(temp_dir)], check=True)
        if OUT_DIR.exists():
            shutil.rmtree(OUT_DIR)

if __name__ == "__main__":
    sync_to_local_wp()
    export_site()
    if "--publish" in sys.argv:
        publish_gh_pages()
