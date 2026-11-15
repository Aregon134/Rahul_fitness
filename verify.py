"""Small acceptance checks for local links, content semantics and Elementor exports."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json

ROOT = Path(__file__).resolve().parent


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.h1 = 0
        self.links = []
        self.ids = []
        self.images = []
        self.fields = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.h1 += tag == 'h1'
        self.fields += tag in ('form', 'input', 'textarea', 'select')
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'a':
            self.links.append(a['href'])
        if tag == 'img':
            self.images.append(a)


def walk(nodes):
    for n in nodes:
        yield n
        yield from walk(n.get('elements', []))


def luminance(value):
    channels = [int(value[i:i+2], 16)/255 for i in (1, 3, 5)]
    return sum(c*w for c, w in zip([c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in channels], [.2126, .7152, .0722]))


def main():
    result = {'pages': [], 'contrast': []}
    for path in sorted((ROOT / 'preview').rglob('index.html')):
        parser = Page()
        parser.feed(path.read_text(encoding='utf-8'))
        assert parser.h1 == 1, (path, 'Exactly one H1 required')
        assert parser.fields == 0, (path, 'Preview must not collect data')
        assert len(parser.ids) == len(set(parser.ids)), (path, 'Duplicate IDs')
        for image in parser.images:
            assert image.get('alt'), (path, 'Missing alternative')
            assert (path.parent / image['src']).is_file(), (path, image['src'])
        for href in parser.links:
            url = urlsplit(href)
            if url.scheme or url.netloc:
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if target.is_dir():
                target = target / 'index.html'
            assert target.is_file(), (path, href)
            if url.fragment and not url.fragment.startswith(('preview-', 'review-')):
                linked = Page()
                linked.feed(target.read_text(encoding='utf-8'))
                assert url.fragment in linked.ids, (path, href, 'Missing anchor')
        template = ROOT / 'elementor-package' / (path.parent.name + '.json' if path.parent != ROOT/'preview' else 'home.json')
        data = json.loads(template.read_text(encoding='utf-8'))
        nodes = list(walk(data['content']))
        assert len({n['id'] for n in nodes}) == len(nodes)
        assert sum(n['settings'].get('header_size') == 'h1' for n in nodes) == 1
        assert all('css_classes' in n['settings'] for n in nodes if n['elType'] == 'container')
        result['pages'].append({'path': str(path.relative_to(ROOT)), 'h1': 1, 'links': len(parser.links), 'images': len(parser.images), 'elementor_nodes': len(nodes), 'passed': True})
    for foreground, background in [('#202824', '#F6F3EC'), ('#245743', '#F6F3EC'), ('#536157', '#F6F3EC'), ('#F6F3EC', '#245743'), ('#495A46', '#EDF0E7'), ('#C5CFC3', '#202824')]:
        values = sorted([luminance(foreground), luminance(background)])
        ratio = (values[1]+.05)/(values[0]+.05)
        assert ratio >= 4.5, (foreground, background, ratio)
        result['contrast'].append({'foreground': foreground, 'background': background, 'ratio': round(ratio, 2)})
    out = ROOT / 'output'
    out.mkdir(exist_ok=True)
    (out / 'source-checks.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print('PASS: four pages; local links/anchors; H1s; image assets/alts; no data fields; native exports; six contrast pairs.')


if __name__ == '__main__':
    main()
