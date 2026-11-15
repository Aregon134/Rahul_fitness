"""Build the review preview and editable Elementor templates from one content tree."""
from pathlib import Path
import copy
import html
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'preview'
PACK = ROOT / 'elementor-package'
ASSETS = ROOT / 'assets'
counter = 0


def node(kind, cls='', children=None, **kw):
    global counter
    counter += 1
    return dict(kind=kind, cls=cls, children=children or [], id=f'{counter:08x}', **kw)


def box(cls, *children, tag='div', anchor=''):
    return node('box', cls, list(children), tag=tag, anchor=anchor)


def heading(text, level=2, cls=''):
    return node('heading', f'rf-heading {cls}', text=text, level=level)


def text(value, cls=''):
    return node('text', f'rf-copy {cls}', text=value)


def raw(value, cls=''):
    return node('html', cls, text=value)


def eyebrow(value):
    return text(value, 'rf-eyebrow')


def confirm(value):
    return text(f'[CLIENT TO CONFIRM: {value}]', 'rf-confirm')


def link(label, href, cls='rf-button'):
    return node('button', cls, text=label, href=href)


def photo(label, asset='photo-placeholder.svg', cls=''):
    return box(f'rf-photo {cls}',
               node('image', 'rf-image', src=f'assets/{asset}', alt=f'Image placeholder: {label}. Approved photograph required.'),
               box('rf-photo-caption', eyebrow('Photography / awaiting approval'), confirm(label)))


def section(kicker, title, *children, cls='', anchor='', intro=''):
    return box(f'rf-section {cls}', box('rf-wrap',
        box('rf-section-heading', eyebrow(kicker), heading(title), *([text(intro, 'rf-intro')] if intro else [])),
        *children), tag='section', anchor=anchor)


def hero(kicker, title, intro, cta, href, label, aside='', variant=''):
    return box(f'rf-hero {variant}', box('rf-wrap rf-hero-grid',
        box('rf-hero-copy', eyebrow(kicker), heading(title, 1), text(intro, 'rf-lead'),
            box('rf-actions', link(cta, href)), text(aside or 'Your starting point. Your pace. Your next step.', 'rf-hero-note')),
        photo(label, cls='rf-hero-photo')), tag='section')


def bullet_list(items):
    return raw('<ul class="rf-list">' + ''.join(f'<li>{html.escape(i)}</li>' for i in items) + '</ul>')


def card(number, title, copy, *extra, cls=''):
    return box(f'rf-card {cls}', eyebrow(number), heading(title, 3), text(copy), *extra)


def process(items):
    return box('rf-grid rf-three rf-process', *[
        card(f'0{i+1}', title, copy, *([confirm(missing)] if missing else []))
        for i, (title, copy, missing) in enumerate(items)])


def faq(items):
    return raw('<div class="rf-faq">' + ''.join(
        f'<details><summary>{html.escape(q)}<span aria-hidden="true" class="rf-plus"></span></summary>'
        f'<div class="rf-faq-answer"><p>{html.escape(a)}</p></div></details>' for q, a in items) + '</div>')


def cta(title, copy, label, href):
    return box('rf-section rf-cta', box('rf-wrap rf-cta-inner',
        box('', eyebrow('Take your next step'), heading(title), text(copy)), link(label, href)), tag='section')


def results():
    return box('rf-grid rf-three', *[box('rf-card rf-result',
        raw('<div class="rf-result-image" role="img" aria-label="Placeholder for a consented client result photograph"><span aria-hidden="true">↗</span><span>Client result / photo pending</span></div>'),
        eyebrow(f'Client story / 0{i}'), heading('A progress story, in context.', 3),
        text('Space for the client’s goal, starting point, experience and verified progress.'),
        confirm('client consent, name, photographs, outcome and timeframe')) for i in range(1, 4)])


OFFERS = [
    ('01 / Focused guidance', 'One time consultation', 'For a specific question or a clearer next step. Start with a focused conversation.',
     'One appointment', 'Explore consultation', '/consultation/', 'price, duration and appointment inclusions'),
    ('02 / Learn the foundations', 'The X Frame Method', 'An online fitness course. Explore the curriculum and learn what the course will cover.',
     'Online course', 'Explore the course', '/the-method/', 'curriculum, access period, support and price'),
    ('03 / Personal support', '1-1 Coaching with Rahul', 'For people looking for a personalised coaching relationship around their goals.',
     'Personal coaching', 'Explore 1-1 coaching', '/1-1-coaching/', 'coaching scope, duration, communication and price'),
]


def offer_cards():
    return box('rf-grid rf-three rf-offer-grid', *[box('rf-card rf-offer ' + ('rf-offer-green' if i == 1 else ''),
        eyebrow(kicker), heading(title, 3), text(copy), text(fmt, 'rf-format'),
        confirm(missing), link(label, href, 'rf-text-link'))
        for i, (kicker, title, copy, fmt, label, href, missing) in enumerate(OFFERS)])


def comparison():
    rows = [
        ('Who it is for', 'A focused question', 'People who want to learn', 'People seeking personal support'),
        ('Delivery format', 'One appointment', 'Online course', '1-1 coaching'),
        ('Personal support', '[CLIENT TO CONFIRM: appointment scope]', '[CLIENT TO CONFIRM: course support]', '[CLIENT TO CONFIRM: check-ins and contact]'),
        ('Commitment', '[CLIENT TO CONFIRM: call duration]', '[CLIENT TO CONFIRM: pace and access]', '[CLIENT TO CONFIRM: programme duration]'),
        ('Price (INR)', '[CLIENT TO CONFIRM: ₹ price]', '[CLIENT TO CONFIRM: ₹ price]', '[CLIENT TO CONFIRM: ₹ price]'),
    ]
    heads = ['Compare your options', 'Consultation', 'The X Frame Method', '1-1 coaching']
    return raw('<div class="rf-comparison"><table><caption class="rf-sr">Compare consultation, course and coaching</caption><thead><tr>' +
               ''.join(f'<th scope="col">{v}</th>' for v in heads) + '</tr></thead><tbody>' + ''.join(
                   '<tr><th scope="row">' + row[0] + '</th>' + ''.join(
                       f'<td data-label="{html.escape(heads[i+1])}">{html.escape(v)}</td>' for i, v in enumerate(row[1:])) + '</tr>'
                   for row in rows) + '</tbody></table></div>')


def facts(items):
    return raw('<dl class="rf-facts">' + ''.join(f'<div><dt>{html.escape(label)}</dt><dd>[CLIENT TO CONFIRM: {html.escape(value)}]</dd></div>' for label, value in items) + '</dl>')


HOME = [
    hero('Rahul Fitness / A stronger everyday', 'Build strength. Find your routine. Make progress that lasts.',
         'Focused guidance, an online course, or personal coaching. Find a way forward that fits where you are today.',
         'Explore your options', '#offers', 'Rahul coaching a client in a training space'),
    section('Progress, with perspective', 'Every story needs the full picture.', results(),
            intro='Client results will appear here once the stories, context and consent are approved. These are placeholders, not testimonials.'),
    section('Three ways to begin', 'Find the support that fits.', offer_cards(), cls='rf-sage', anchor='offers',
            intro='A little clarity, a structured way to learn, or support along the way. Choose your starting point.'),
    box('rf-section', box('rf-wrap rf-split', photo('Rahul’s approved portrait', cls='rf-portrait'),
        box('rf-bio', eyebrow('Meet your coach'), heading('Hi, I’m Rahul.'),
            text('This is where you’ll get to know the person behind Rahul Fitness: his background, how he coaches, and what matters to him.'),
            confirm('Rahul’s biography, qualifications, experience and coaching philosophy'),
            text('For now, explore the three formats and see which kind of support you are looking for.'),
            link('Find your starting point', '#offers', 'rf-text-link'))), tag='section'),
    section('The approach / draft for review', 'Start where you are. Build from there.', process([
        ('Get clear', 'Think about your goal, your routine and the questions you want answered.', ''),
        ('Choose your support', 'Compare focused guidance, course learning and personalised coaching.', ''),
        ('Take the next step', 'Review what is included before deciding how you would like to begin.', ''),
    ]), intro='A simple way to choose. Rahul’s training and coaching principles will be added after review.'),
    section('A clearer choice', 'Different formats. Different needs.', comparison(), cls='rf-white'),
    section('A few things you might be wondering', 'Let’s make it clearer.', faq([
        ('Where should I start?', 'Explore the three offer pages. A consultation is for focused guidance, The X Frame Method is an online course, and 1-1 coaching is the personalised support option. Final inclusions are awaiting client confirmation.'),
        ('Is the course the same as 1-1 coaching?', 'No. The X Frame Method is a learning product. 1-1 coaching is a separate personalised service. [CLIENT TO CONFIRM: the exact support included in each offer]'),
        ('Do I need training experience?', '[CLIENT TO CONFIRM: experience level, suitability and prerequisites for each offer]'),
        ('Can I book or enrol from this preview?', 'This is a design and content preview. Booking, payment, course access and application processing will be specified after client review. The buttons open preview panels only.'),
    ])),
    cta('Your next step starts here.', 'Explore the formats. Take a closer look at the one that feels right for you.', 'Explore your options', '#offers'),
]

CONSULTATION_FACTS = [('Price (INR)', '₹ amount and applicable taxes'), ('Call duration', 'appointment length'),
    ('Meeting platform', 'video or voice platform'), ('Preparation', 'what to share before the call'),
    ('Takeaways', 'agreed deliverables, if any'), ('Rescheduling', 'cancellation and rescheduling terms')]

CONSULTATION = [
    hero('One time consultation / Focused guidance', 'Get clear on your next step.',
         'A focused appointment to discuss your fitness questions. Review the topics, format and inclusions before you book.',
         'Book a consultation', '#preview-consultation', 'Rahul talking with a client during a consultation', 'One appointment. Scope and price awaiting confirmation.'),
    section('Is this your starting point?', 'For the questions on your mind.', box('rf-grid rf-three',
        card('01', 'You want a clearer direction.', 'You have questions about where to begin and want to discuss your next step.'),
        card('02', 'You want to talk it through.', 'You are weighing different options and want a focused conversation.'),
        card('03', 'You have a specific question.', 'You would like to check whether your topic fits the consultation scope.')),
        confirm('who the appointment is suitable for and any exclusions')),
    section('The conversation', 'What would you like to cover?', box('rf-grid rf-three',
        card('Proposed topic', 'Your starting point', 'Your current routine, training experience and the goal you want to discuss.'),
        card('Proposed topic', 'Your questions', 'The questions you would like to prioritise during the appointment.'),
        card('Proposed topic', 'Possible next steps', 'A discussion of your options within the confirmed scope.')),
        confirm('approved consultation topics, training/nutrition scope and professional boundaries'), cls='rf-sage'),
    section('Before / During / After', 'Know what to expect.', process([
        ('Before the call', 'Review the appointment details and prepare the questions you want to discuss.', 'preparation requirements and booking process'),
        ('During the call', 'Use the appointment to discuss the agreed topics with Rahul.', 'duration, platform and agenda'),
        ('After the call', 'Any written takeaways or next steps depend on the final inclusions.', 'deliverables; whether any follow-up is included'),
    ]), text('A personalised plan or follow-up support is not promised in this draft.', 'rf-note')),
    section('Your appointment, at a glance', 'The details before you decide.', box('rf-summary-grid',
        facts(CONSULTATION_FACTS), box('rf-summary-card', eyebrow('One time consultation'), heading('A focused conversation.', 3),
            confirm('₹ consultation price'), text('Review the confirmed inclusions and service terms before booking.'),
            link('Book a consultation', '#preview-consultation'), text('Preview only — payment and scheduling are not connected.', 'rf-small'))), cls='rf-white'),
    section('Your questions, answered', 'Before you book.', faq([
        ('Will I receive a personalised plan?', 'A personalised plan is not included unless Rahul confirms it as a specific deliverable. [CLIENT TO CONFIRM: appointment takeaways]'),
        ('Is follow-up support included?', 'Follow-up support is not promised in this draft. [CLIENT TO CONFIRM: whether follow-up is offered, and its scope]'),
        ('How long is the appointment and where does it happen?', '[CLIENT TO CONFIRM: appointment duration and meeting platform]'),
        ('What if I need to reschedule?', '[CLIENT TO CONFIRM: rescheduling notice, cancellation terms and refund policy]'),
        ('How will booking work?', 'The planned journey is booking, payment and scheduling. The exact order and providers will be specified after review. This preview does not make a booking or accept payment.'),
    ])),
    cta('Make space for your questions.', 'Take a look at the appointment preview and the details still to be confirmed.', 'Book a consultation', '#preview-consultation'),
]

COURSE_FACTS = [('Price (INR)', '₹ course price and applicable taxes'), ('Resources', 'worksheets, guides or other files'),
    ('Access period', 'length of course access'), ('Equipment', 'space and equipment requirements'),
    ('Support', 'whether support is included and its scope'), ('Lesson format', 'lesson count, video length and delivery format')]

METHOD = [
    hero('The X Frame Method / Online fitness course', 'Learn with purpose. Train with understanding.',
         'The X Frame Method is an online fitness course. Its curriculum and teaching approach are awaiting confirmation; this page previews the learning experience.',
         'Enrol in The X Frame Method', '#preview-course', 'Rahul demonstrating an exercise for a course lesson', 'Course learning is separate from personal coaching.', 'rf-course-hero'),
    section('Find your fit', 'A course for your learning journey.', box('rf-grid rf-two',
        box('rf-card', eyebrow('Who it is for'), heading('Know if it suits you.', 3),
            text('Review the intended audience and prerequisites before enrolling.'), confirm('intended audience, experience level and suitability')),
        box('rf-card', eyebrow('Learning outcomes'), heading('Know what you will learn.', 3),
            text('The approved outcomes will describe the knowledge and skills covered, without promising physical results.'),
            confirm('the actual X Frame method and specific learning outcomes')))),
    section('Inside The X Frame Method', 'A closer look at the curriculum.', box('rf-curriculum', *[
        box('rf-module', eyebrow(f'Module {i:02} / proposed layout'), heading(f'[CLIENT TO CONFIRM: module {i} title]', 3),
            text('[CLIENT TO CONFIRM: module topics, learning objective and lesson count]')) for i in range(1, 5)]),
        text('Four rows illustrate the curriculum layout only. The number and order of modules are unconfirmed.', 'rf-note'), cls='rf-sage'),
    section('A feel for the lessons', 'See how the course is taught.', box('rf-split rf-lesson',
        photo('approved lesson preview thumbnail', 'lesson-placeholder.svg'),
        box('', eyebrow('Lesson preview / not yet available'), heading('Your first look inside.', 3),
            text('An approved sample lesson will sit here so you can see the teaching style before deciding.'),
            confirm('sample lesson, title, transcript/captions and duration')))),
    section('What comes with the course', 'The full learning experience.', facts(COURSE_FACTS), cls='rf-white'),
    section('Meet your instructor', 'Learn with Rahul.', box('rf-split', photo('Rahul’s approved instructor portrait', cls='rf-portrait'),
        box('rf-bio', heading('The person behind the lessons.', 3),
            text('This section will introduce Rahul’s relevant training background and why he created the course.'),
            confirm('instructor biography, qualifications, experience and course origin')))),
    section('Your course, at a glance', 'Review the details. Then decide.', box('rf-summary-grid',
        box('', heading('The X Frame Method', 3), text('An online fitness course with its final curriculum, resources and access terms still under review.'),
            bullet_list(['Review the curriculum and prerequisites.', 'Check the access period and support inclusions.', 'Read the purchase and refund terms.']),
            confirm('purchase terms, refunds, platform and student access process')),
        box('rf-summary-card', eyebrow('Online course'), heading('A structured way to learn.', 3), confirm('₹ course price'),
            link('Enrol in The X Frame Method', '#preview-course'), text('Preview only — enrolment and payment are not connected.', 'rf-small'))), cls='rf-sage'),
    section('Before you enrol', 'A few course questions.', faq([
        ('What is The X Frame Method?', 'It is an online fitness course. [CLIENT TO CONFIRM: the actual method, curriculum, lesson count and learning outcomes]'),
        ('Will Rahul coach me personally?', 'The course is separate from 1-1 coaching. Personalised coaching is not promised with course purchase. [CLIENT TO CONFIRM: course support]'),
        ('What equipment and experience do I need?', '[CLIENT TO CONFIRM: training prerequisites, equipment and space requirements]'),
        ('How long can I access the lessons?', '[CLIENT TO CONFIRM: access period, release schedule and any download permissions]'),
        ('Where will I take the course?', 'The course platform and student experience belong to the later integration phase. [CLIENT TO CONFIRM: platform and access process]'),
        ('Can I enrol now?', 'This is a preview. The enrolment button shows the proposed purchase summary without collecting payment or creating an account.'),
    ])),
]

COACHING = [
    hero('1-1 Coaching with Rahul / Personal support', 'Personal coaching built around you.',
         'Explore a personalised coaching relationship around your goals and routine. Review the proposed approach, support and fit before applying.',
         'Apply for coaching', '#preview-coaching', 'Rahul reviewing a client’s exercise technique', 'Application preview only. Coaching inclusions are awaiting approval.'),
    section('Relevant progress, with context', 'The people behind the progress.', results(),
            intro='Approved coaching stories will appear here with context, client consent and verified outcomes. No results are claimed in this preview.'),
    section('Is coaching the right fit?', 'For a more personal way forward.', box('rf-grid rf-three',
        card('01', 'You want individual support.', 'You are looking for a coaching format that considers your own goals and circumstances.'),
        card('02', 'You can make room for it.', 'You want to understand the time commitment and what participation involves.'),
        card('03', 'You are ready to discuss fit.', 'You would like to explore whether the service matches the support you need.')),
        confirm('suitability criteria, programme expectations and exclusions'), cls='rf-sage'),
    section('The coaching process / draft', 'A plan for working together.', process([
        ('Explore the fit', 'Share your goal, experience and availability through the proposed application.', 'application review and suitability process'),
        ('Agree the approach', 'Discuss the confirmed service scope, commitments and expectations.', 'onboarding, assessment and programme delivery'),
        ('Review as you go', 'Understand how progress reviews and communication would work.', 'check-in frequency, adjustments and response times'),
    ])),
    section('Inclusions and communication', 'Know what support means.', box('rf-summary-grid',
        facts([('Training', 'training scope and programme delivery'), ('Nutrition', 'nutrition scope and boundaries'),
               ('Check-ins', 'frequency, format and review process'), ('Communication', 'channel, working hours and response time'),
               ('Duration', 'programme length and commitment'), ('Rahul’s involvement', 'direct involvement and any team support')]),
        box('rf-card', eyebrow('Clear expectations'), heading('The details matter.', 3),
            text('Before you commit, you should know who supports you, what is included and how communication works.'),
            confirm('₹ coaching price, payment schedule, cancellation and refund terms'))), cls='rf-white'),
    section('Course or coaching?', 'Choose the format you need.', box('rf-grid rf-two',
        box('rf-card', eyebrow('The X Frame Method'), heading('A learning product.', 3),
            text('An online course with an approved curriculum. Course purchase does not promise personal coaching.'),
            link('Explore the course', '/the-method/', 'rf-text-link')),
        box('rf-card rf-offer-green', eyebrow('1-1 coaching'), heading('A personal service.', 3),
            text('A personalised coaching relationship. Exact scope, contact and duration are awaiting confirmation.'),
            link('Apply for coaching', '#preview-coaching', 'rf-text-link')))),
    section('A first introduction', 'Tell Rahul where you are starting.', box('rf-application',
        box('', eyebrow('Application preview / no information is collected'), heading('A few useful starting points.', 3),
            text('The planned application asks about your goal and availability. Detailed health information belongs in later onboarding.'),
            raw('<ol class="rf-field-preview"><li><span>01</span> Name</li><li><span>02</span> Email</li><li><span>03</span> Primary goal</li><li><span>04</span> Training experience</li><li><span>05</span> Availability</li><li><span>06</span> Preferred contact method</li></ol>')),
        box('rf-summary-card', eyebrow('1-1 Coaching with Rahul'), heading('Let’s explore the fit.', 3),
            text('Open the application preview to review the planned next step.'), link('Apply for coaching', '#preview-coaching'),
            confirm('review process, reply timing, contact options and privacy notice'))), cls='rf-sage'),
    section('Before you apply', 'A few coaching questions.', faq([
        ('Will I work directly with Rahul?', '[CLIENT TO CONFIRM: Rahul’s direct involvement, any team involvement, and who handles programmes and check-ins]'),
        ('Does coaching include training and nutrition?', '[CLIENT TO CONFIRM: training and nutrition scope, inclusions and exclusions]'),
        ('How often are check-ins?', '[CLIENT TO CONFIRM: check-in frequency, review format and programme adjustments]'),
        ('How long does coaching last and what does it cost?', '[CLIENT TO CONFIRM: programme duration, commitment, ₹ price and applicable taxes]'),
        ('What happens after I apply?', 'Application review, response times and onboarding will be specified after client review. This preview does not send or save an application.'),
    ])),
]

PAGES = [('', 'Home', HOME), ('consultation', 'One time consultation', CONSULTATION),
         ('the-method', 'The X Frame Method', METHOD), ('1-1-coaching', '1-1 Coaching with Rahul', COACHING)]


def header():
    return [raw('''<div class="rf-preview-bar"><div class="rf-wrap"><span><span class="rf-dot" aria-hidden="true"></span> Design preview</span><a href="#review-checklist">Content awaiting client approval <span aria-hidden="true">↗</span></a></div></div>
<header class="rf-header"><div class="rf-wrap rf-header-inner"><a class="rf-brand" href="/" aria-label="Rahul Fitness home"><span class="rf-brand-mark" aria-hidden="true">rf<span>.</span></span><span>RAHUL<br>FITNESS</span></a>
<button class="rf-menu-toggle" type="button" aria-expanded="false" aria-controls="rf-main-nav"><span>Menu</span><span aria-hidden="true">☰</span></button>
<nav id="rf-main-nav" class="rf-nav" aria-label="Main navigation"><a href="/">Home</a><a href="/consultation/">Consultation</a><a href="/the-method/">The X Frame Method</a><a href="/1-1-coaching/">1-1 coaching</a></nav></div></header>''')]


def footer():
    return [raw('''<footer class="rf-footer"><div class="rf-wrap"><div class="rf-footer-top"><div><a class="rf-brand" href="/" aria-label="Rahul Fitness home"><span class="rf-brand-mark" aria-hidden="true">rf<span>.</span></span><span>RAHUL<br>FITNESS</span></a><p>A stronger everyday.<br>A starting point that feels like yours.</p></div><nav aria-label="Footer navigation"><a href="/">Home</a><a href="/consultation/">One time consultation</a><a href="/the-method/">The X Frame Method</a><a href="/1-1-coaching/">1-1 Coaching with Rahul</a></nav><div class="rf-footer-review"><span class="rf-eyebrow">For client review</span><p>Four pages. One shared direction.</p><a href="#review-checklist">Open the content checklist ↗</a></div></div><div class="rf-footer-bottom"><span>© Rahul Fitness · Design preview</span><span>English / INR</span><span>[CLIENT TO CONFIRM: legal name, contact and policies]</span></div></div></footer>''')]


def url_for_preview(value, base):
    if value.startswith('/'):
        path, _, frag = value.partition('#')
        return base + ('index.html' if path == '/' else path.lstrip('/')) + ('#' + frag if frag else '')
    return value


def render(n, base):
    cls = html.escape(n['cls'])
    kind = n['kind']
    val = html.escape(n.get('text', ''))
    if kind == 'box':
        tag = n['tag']
        anchor = f' id="{n["anchor"]}"' if n['anchor'] else ''
        return f'<{tag} class="{cls}"{anchor}>' + ''.join(render(c, base) for c in n['children']) + f'</{tag}>'
    if kind == 'heading':
        return f'<div class="{cls}"><h{n["level"]}>{val}</h{n["level"]}></div>'
    if kind == 'text':
        return f'<div class="{cls}"><p>{val}</p></div>'
    if kind == 'button':
        return f'<div class="{cls}"><a href="{url_for_preview(n["href"], base)}">{val}<span aria-hidden="true">↗</span></a></div>'
    if kind == 'image':
        return f'<div class="{cls}"><img src="{base + n["src"]}" alt="{html.escape(n["alt"])}" width="720" height="820"></div>'
    return re.sub(r'href="(/[^\"]*)"', lambda m: 'href="' + url_for_preview(m[1], base) + '"', n['text'])


def elementor(n):
    kind = n['kind']
    settings = {'_css_classes': n['cls']}
    out = dict(id=n['id'], elType='widget', isInner=False, settings=settings, elements=[])
    if kind == 'box':
        out['elType'] = 'container'
        settings['css_classes'] = settings.pop('_css_classes')
        settings.update(content_width='full', flex_direction='column', html_tag=n['tag'],
                        padding=dict(unit='px', top='0', right='0', bottom='0', left='0', isLinked=True),
                        flex_gap=dict(column='0', row='0', isLinked=True, unit='px'))
        if n['anchor']:
            settings['_element_id'] = n['anchor']
        out['elements'] = [elementor(c) for c in n['children']]
    elif kind == 'heading':
        out['widgetType'] = 'heading'
        settings.update(title=n['text'], header_size=f'h{n["level"]}',
                        __globals__={'title_color': 'globals/colors?id=rfcharcoal', 'typography_typography': 'globals/typography?id=rfheading'})
    elif kind == 'text':
        out['widgetType'] = 'text-editor'
        settings.update(editor='<p>' + html.escape(n['text']) + '</p>',
                        __globals__={'text_color': 'globals/colors?id=rfcharcoal', 'typography_typography': 'globals/typography?id=rfbody'})
    elif kind == 'button':
        out['widgetType'] = 'button'
        settings.update(text=n['text'] + ' ↗', link={'url': n['href'], 'is_external': '', 'nofollow': ''},
                        __globals__={'button_background_color': 'globals/colors?id=rfforest', 'typography_typography': 'globals/typography?id=rfbody'})
    elif kind == 'image':
        out['widgetType'] = 'image'
        settings.update(image={'url': '__RF_ASSET__/' + n['src'].split('/')[-1], 'id': ''}, image_size='full',
                        caption_source='custom', caption='', _rf_alt=n['alt'])
    else:
        out['widgetType'] = 'html'
        settings['html'] = n['text']
    return out


def export(title, nodes, kind='page'):
    return {'version': '0.4', 'title': title, 'type': kind, 'page_settings': {}, 'content': [elementor(n) for n in nodes]}


def main():
    DIST.mkdir(exist_ok=True)
    PACK.mkdir(exist_ok=True)
    (DIST / 'assets').mkdir(exist_ok=True)
    for item in ASSETS.iterdir():
        (DIST / 'assets' / item.name).write_bytes(item.read_bytes())
    head, foot = header(), footer()
    for slug, title, nodes in PAGES:
        base = '../' if slug else './'
        folder = DIST / slug
        folder.mkdir(exist_ok=True)
        document = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{html.escape(title)} | Rahul Fitness preview</title><meta name="description" content="Rahul Fitness design preview: consultation, online course and personal coaching. Content awaiting client approval."><link rel="stylesheet" href="{base}assets/styles.css"><script src="{base}assets/site.js" defer></script></head><body class="rf"><a href="#main" class="rf-skip">Skip to content</a>{''.join(render(n, base) for n in head)}<main id="main">{''.join(render(n, base) for n in nodes)}</main>{''.join(render(n, base) for n in foot)}<div id="rf-panels"></div></body></html>'''
        (folder / 'index.html').write_text(document, encoding='utf-8')
        template = export(title, nodes)
        (PACK / f'{slug or "home"}.json').write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding='utf-8')
    (PACK / 'shared-header.json').write_text(json.dumps(export('Rahul Fitness shared header', head, 'section'), indent=2), encoding='utf-8')
    (PACK / 'shared-footer.json').write_text(json.dumps(export('Rahul Fitness shared footer', foot, 'section'), indent=2), encoding='utf-8')
    kit = {'title': 'Rahul Fitness global styles', 'type': 'kit', 'version': '0.4', 'content': [], 'page_settings': {
        'custom_colors': [{'_id': i, 'title': title, 'color': color} for i, title, color in [
            ('rfivory', 'RF Ivory', '#F6F3EC'), ('rfcharcoal', 'RF Charcoal', '#202824'),
            ('rfforest', 'RF Forest', '#245743'), ('rfsage', 'RF Pale sage', '#E5EBE1')]],
        'custom_typography': [{'_id': 'rfheading', 'title': 'RF Headings', 'typography_typography': 'custom', 'typography_font_family': 'Manrope', 'typography_font_weight': '600'},
                              {'_id': 'rfbody', 'title': 'RF Body', 'typography_typography': 'custom', 'typography_font_family': 'Inter', 'typography_font_size': {'unit': 'px', 'size': 17}, 'typography_font_weight': '400', 'typography_line_height': {'unit': 'em', 'size': 1.7}}],
        'container_width': {'unit': 'px', 'size': 1200}}}
    (PACK / 'global-styles.json').write_text(json.dumps(kit, indent=2), encoding='utf-8')
    plugin = ROOT / 'wordpress' / 'rahul-fitness-preview'
    (plugin / 'templates').mkdir(parents=True, exist_ok=True)
    (plugin / 'assets').mkdir(exist_ok=True)
    for item in PACK.glob('*.json'):
        (plugin / 'templates' / item.name).write_bytes(item.read_bytes())
    for item in ASSETS.iterdir():
        (plugin / 'assets' / item.name).write_bytes(item.read_bytes())
    with zipfile.ZipFile(ROOT / 'rahul-fitness-elementor-preview.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for item in plugin.rglob('*'):
            if item.is_file():
                archive.write(item, item.relative_to(plugin.parent))
    with zipfile.ZipFile(ROOT / 'rahul-fitness-review-bundle.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for folder in [DIST, PACK, ASSETS, ROOT / 'wordpress']:
            for item in folder.rglob('*'):
                if item.is_file():
                    archive.write(item, item.relative_to(ROOT))
        for name in ['CONTENT-CHECKLIST.md', 'README.md', 'rahul-fitness-elementor-preview.zip', 'build.py', 'verify.py', 'Start-WordPress.ps1', 'local-wordpress.json', 'localhost-only.cjs']:
            if (ROOT / name).exists():
                archive.write(ROOT / name, name)
    print('Built four preview pages, six Elementor templates, global styles and WordPress package.')


if __name__ == '__main__':
    main()
