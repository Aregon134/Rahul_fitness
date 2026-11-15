# Rahul Fitness — consolidated content and integration checklist

All items below are awaiting confirmation. The preview makes no client-result, qualification, price or service-inclusion claims. Bracketed labels must be replaced with approved content before public launch.

| Area | Required confirmation or asset | Where it appears |
| --- | --- | --- |
| Brand | Legal/trading name, approved wordmark, contact details | Header/footer, policies |
| Biography | Rahul’s background, qualifications, experience, coaching philosophy and direct involvement | Home, course, coaching |
| Photography | Portrait, coaching interaction, consultation, course demonstration; ownership, consent and approved crop | All four pages |
| Client results | Written publication consent, approved quote/name, image rights, starting context, verified outcome, timeframe | Home and coaching; three layout slots do not imply three confirmed clients |
| Consultation price | INR amount, taxes, payment terms | Consultation, home comparison, booking preview |
| Consultation format | Duration, platform, preparation, topics, exclusions | Consultation |
| Consultation deliverables | Agreed takeaways; whether a plan or follow-up exists | Consultation; neither is promised |
| Consultation terms | Rescheduling notice, cancellations, refunds | Consultation and later booking |
| Course positioning | Actual X Frame method, intended audience, suitability, prerequisites, outcomes | Course |
| Course curriculum | Actual module titles, order, lesson counts and durations | Course; four rows are layout samples only |
| Lesson preview | Approved sample lesson, thumbnail, captions/transcript and duration | Course |
| Course inclusions | Resources, equipment/space, access period, release schedule, downloads, support | Course |
| Course price/terms | INR amount, taxes, purchase/refund terms | Course and home comparison |
| Coaching scope | Training/nutrition boundaries, programme delivery, suitability/exclusions | Coaching |
| Coaching support | Check-in frequency, channels/hours, response time, adjustments, Rahul/team involvement | Coaching |
| Coaching commitment | Programme duration, participation expectations, INR price/taxes, payment/cancellation/refund terms | Coaching and home comparison |
| Application | Final wording, preferred-contact options, review steps, response timing and privacy notice | Coaching |
| Legal | Privacy, service terms, refunds, contact and applicable approved statements | Footer and later conversion flows |

## Later integration decisions

- Booking: scheduling provider, availability, timezone, payment order, confirmations, cancellation and rescheduling.
- Payments: INR provider, taxes/invoicing, refund process and payment failures.
- Course: hosting/LMS choice, student login/access, lesson delivery, captions, account support and revocation rules.
- Applications: destination, review owner, response process, consent/privacy and retention rules. Detailed health information belongs in later onboarding.
- No custom API, database, LMS or paid plugin is implemented or required by this preview.

## WordPress staging and launch

- A local WordPress/Elementor preview has been created and checked at `http://127.0.0.1:9400/`. Review the plugin on the existing Elementor staging setup later, including theme/plugin compatibility. A remote staging URL was not supplied; no remote WordPress content has been changed.
- Import four drafts using the included plugin, then check their native Elementor editing controls. Header/footer are shared Elementor library templates.
- Review the separate global styles Kit; do not activate a site-wide Kit on a production site without checking its effect on existing pages. The preview has scoped fallback styles.
- Final routes: `/`, `/consultation/`, `/the-method/`, `/1-1-coaching/`.
- Add a permanent redirect from `/1-1-coachin/` to `/1-1-coaching/` at launch, after confirming the final destination.
- The preview canvas omits the old theme’s grocery header, coupon banner, sample reviews and cart. Check any globally injected popups or third-party floating-cart plugins on the actual staging environment.
- Confirm all content and media; remove review-only labels/panels only after approval. Specify working conversion flows before making transaction CTAs live.
- Recheck all pages at 360, 390, 768 and 1440px; keyboard navigation, FAQ operation, focus visibility, image alternatives, colour contrast and internal links.
- Public launch, homepage switching and redirects remain separate from this draft package.
