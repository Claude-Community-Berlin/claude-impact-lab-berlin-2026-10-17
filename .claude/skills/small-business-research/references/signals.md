# Reading the signals

How to turn what you find in a business's public footprint into pain points and suggestions. Two parts:

1. [Signal → pain tables](#signal--pain-tables), grouped by area of the business
2. [Category playbooks](#category-playbooks): typical activities, typical pains and where the reviews live, per kind of business

A signal is something you can point at, like a phone-only booking line, a PDF menu or a review that says "waited 40 minutes". The pain is what that signal probably costs the owner in time, money or customers. Write each pain point from the signal outward. Starting from a generic list of SMB problems and hunting for evidence gives bland, interchangeable reports.

---

## Signal → pain tables

### Bookings and appointments

| Signal | Likely pain | What could help |
|---|---|---|
| "Call us to reserve" / phone-only booking | Staff answer the phone mid-service; missed calls after hours = lost bookings; booking book kept by hand | Online booking, or an assistant that handles booking requests by message and confirms |
| Booking via email or DM only | Back-and-forth to agree a time; double bookings | Request form → drafted confirmation for owner approval |
| Third-party platform (Treatwell, Booksy, Quandoo, OpenTable…) | Commission per booking, customer data sits with the platform, availability kept in two places | Direct booking for returning customers; keeping availability in sync |
| Reviews mention no-shows, being forgotten, double booking | Revenue lost on empty slots; awkward customer moments | Reminders, deposit or confirmation flow, waitlist |
| Group / private-hire / event "send us an email" | Every inquiry needs a custom quote: dates, headcount, menu, price | Inquiry intake → draft quote from a price sheet, owner approves |

### Inquiries and communication

| Signal | Likely pain | What could help |
|---|---|---|
| Same questions answered in Google Q&A, Instagram comments, reviews ("do you have vegan options?", "is there parking?") | Owner answers the same question many times; unanswered = lost customers | FAQ answers drafted from what the business already knows |
| Contact form with no stated response time; reviews mention "never got a reply" | Inbox overwhelm, slow replies | Inbox triage, suggested replies |
| Multiple channels (phone, email, Instagram DM, WhatsApp) | Messages scattered, things fall through the cracks | One place to see and answer |
| Website language ≠ customer language (German-only site, English-speaking reviews, tourist area) | Foreign customers can't find answers, call or leave | Translated key info; multilingual replies |

### Menus, prices and catalogue

| Signal | Likely pain | What could help |
|---|---|---|
| Menu / price list as PDF or image | Every change means re-exporting and re-uploading; not readable on phones; not searchable; prices drift out of sync with Google, delivery apps and the printed menu | Single source for menu/prices that updates every channel |
| "Daily specials" / "wechselnde Gerichte" mentioned but not published anywhere | Owner posts specials by hand (or not at all) | Daily specials drafted from what's in stock, posted to Instagram/Google |
| Price inconsistency between website, delivery app and reviews ("prices went up") | Customer complaints, trust erosion | Price sync, change log |
| Online shop with thin product descriptions or missing stock info | Lost sales; "is X in stock?" questions | Product descriptions, stock answers |

### Hours and listings consistency

| Signal | Likely pain | What could help |
|---|---|---|
| Opening hours differ between website, Google, directories, Instagram | Customers arrive at a closed door → angry reviews | One update that pushes hours everywhere; seasonal/holiday hour reminders |
| Google listing missing phone/website/menu/attributes, or owner hasn't claimed it | Lost discovery, wrong info | Listing clean-up |
| Seasonal business (beer garden, ice cream, outdoor) | Hours and staffing change with weather/season; constant re-announcements | Seasonal schedule templates, weather-based announcements |

### Reviews and reputation

| Signal | Likely pain | What could help |
|---|---|---|
| Few or no owner replies to reviews | Missed chance to recover unhappy customers; looks absent | Drafted, on-brand replies for owner approval |
| Recurring complaint theme (slow service, wait time, cleanliness, noise, price, staff attitude, temperature, card payment) | Real operational problem, usually staffing or process | Name the theme; suggest the process behind it (e.g. staffing peaks, order flow) |
| Recurring praise theme | Strength to build on (signature item, a staff member, atmosphere) | Use in marketing, keep consistent |
| Rating count low vs. age of business | Happy customers don't leave reviews | Post-visit review request |
| Recent drop in rating | Something changed (new staff, new owner, price rise) | Flag as question for the owner |

Google's "topic chips" under the review summary (e.g. "käseplatte 5", "atmosphere 26") show what people talk about most. Mention them.

### Social media and marketing

| Signal | Likely pain | What could help |
|---|---|---|
| Last Instagram post weeks/months ago, or bursts then silence | No time to post; content creation is a chore | Drafted posts from photos + weekly calendar |
| Following ≈ followers (ratio > 0.7) | Growth through follow-back, low organic reach | Content that gets shared; local collaborations |
| Events section empty, or events announced only on Instagram stories | Events get no reach beyond existing followers | Event listings pushed to website, Google, event platforms |
| No newsletter / no way to reach past customers | Every quiet week starts from zero | Simple customer list + occasional message |

### Website health and discoverability

| Signal (from `scout.mjs page`) | Likely pain | What could help |
|---|---|---|
| `needs_javascript: true` (raw HTML nearly empty) | Search engines, link previews, AI assistants and some screen readers see a blank page | Pre-rendering / static export |
| Builder default `og:image` / `twitter:site` (e.g. Lovable, Wix placeholder) | Shared links on WhatsApp/Instagram show the builder's logo instead of the business | Own preview image and description |
| `link_check` shows 404 on internal pages | Direct links, Google results and shared links break; in Germany a broken Impressum/Datenschutz link is a legal risk | Fix server routing (SPA fallback) |
| `lang` attribute wrong (e.g. `en` on a German site) | Wrong language in search results and translation prompts | One-line fix |
| No `jsonld` LocalBusiness / Restaurant schema | Weaker Google rich results (hours, price range, menu) | Add structured data |
| Copyright year old, dead links, outdated hours | Looks abandoned | Content refresh |
| No mobile-friendly menu, tiny text, PDFs | Most local searches are on phones | Mobile-first pages |
| No booking/contact button above the fold | Visitors leave without acting | Clear primary action |

Treat these as quick wins rather than headline pain points. The owner feels them only indirectly.

### Staffing and operations

| Signal | Likely pain | What could help |
|---|---|---|
| Job posts ("Wir suchen Verstärkung", "we're hiring") on site/Instagram/job boards | Short-staffed; hiring takes owner time | Job post drafting, applicant screening questions, shift planning |
| Reviews mention self-service, slow service, "only one person working" | Thin staffing at peaks | Peak-time planning, pre-orders, simpler ordering |
| Long opening hours (e.g. until 1–2 am), 7 days | Rota complexity, owner burnout | Shift scheduling, handover notes |
| Same operator runs several venues (legal entity in Impressum, "our other place", shared staff) | Coordinating stock, staff and money across sites | Shared ordering, cross-venue scheduling, consolidated numbers |
| Rotating/seasonal menu, "fresh daily" | Daily purchasing and prep decisions, waste | Ordering suggestions from sales + stock |

### Payments, orders and admin

| Signal | Likely pain | What could help |
|---|---|---|
| "Cash only" / reviews complain about no card | Lost sales, cash handling | — (business decision; note it) |
| Gift vouchers sold only in store / by email | Manual voucher handling, missed online sales | Online vouchers |
| B2B / catering / wholesale offers | Quotes, invoices, payment chasing | Quote → invoice → reminder flow |
| Supplier names visible (beer brand, roaster, wine estates) | Regular supplier ordering, price tracking | Order drafting from stock levels |

---

## Category playbooks

Use these for the "typical activities" (what the business does every week) and to know where to look for reviews. Name activities in the owner's words ("ordering supplies"), not as technology ("procurement automation").

### Café, bar, restaurant, bakery

Roasteries, bakeries and delis that also sell online: check Trusted Shops for the web shop and the public product feed (Shopify or WooCommerce) for stock and listings.

- **Typical activities:** ordering from suppliers, stock counts, staff rota, reservations and walk-in management, group/event inquiries, menu and price updates, daily specials, posting on Instagram, answering reviews, cash-up and bookkeeping, allergen info.
- **Typical pains:** phone reservations mid-service, no-shows, event inquiries by email, menu sync across PDF/Google/delivery apps, staffing peaks, supplier ordering by hand, reviews unanswered.
- **Reviews live on:** Google Maps, TripAdvisor, coolibri.de (Germany), Restaurant Guru, Yelp, Wanderlog, TheFork, Quandoo/OpenTable, delivery apps (Lieferando, Wolt, Uber Eats), Facebook.

### Hair, beauty, barber, nails, spa

- **Typical activities:** appointment booking, reminders, rebooking regulars, client notes (colour formulas, preferences), product stock and reorders, staff schedules, consultations, price list updates, before/after posts.
- **Typical pains:** platform commissions (Treatwell, Booksy, Fresha, Planity), no-shows, phone ringing during treatments, client notes on paper, product stock-outs.
- **Reviews live on:** Google Maps, Treatwell, Booksy, Fresha, Planity, Yelp, Facebook.

### Retail (shops, florists, bike shops, concept stores)

- **Typical activities:** stock tracking and reorders, product listings (online shop), price tags, customer "do you have…?" questions, repairs/orders intake, opening-hours updates, newsletter.
- **Typical pains:** stock counted by hand, online shop out of sync with the till, product descriptions, repair job tracking, seasonal peaks.
- **Reviews live on:** Google Maps, coolibri.de (Germany), Yelp, Trusted Shops or Trustpilot (if online shop), Facebook, Etsy/eBay/Amazon storefronts.

### Fitness, yoga, dance, martial arts studios

- **Typical activities:** class schedule, bookings and waitlists, memberships and payments, instructor cover, onboarding new members, announcements.
- **Typical pains:** last-minute cancellations, instructor substitutions, membership admin, aggregator commissions (Urban Sports Club, ClassPass).
- **Reviews live on:** Google Maps, Urban Sports Club / ClassPass, Eversports, Facebook.

### Health and therapy practices (physio, dentists, psychotherapists, vets)

- **Typical activities:** appointment booking, reminders, intake forms, recall reminders, insurance/billing admin, phone triage.
- **Typical pains:** phone overload, no-shows, paperwork. Be careful: patient data is sensitive. Suggest only things that keep it inside the practice's own systems.
- **Reviews live on:** Google Maps, Doctolib, Jameda, Yelp.

### Trades and home services (plumber, electrician, cleaner, movers, gardener)

- **Typical activities:** quote requests, site visits scheduling, job photos, quotes and invoices, payment reminders, material ordering.
- **Typical pains:** quotes written in the evening, missed calls while on a job, late payments, scheduling across a team.
- **Reviews live on:** Google Maps, MyHammer, Check24, Yelp, ProvenExpert, Trustpilot.

### Professional services and agencies (accountants, studios, consultants, lawyers)

- **Typical activities:** lead intake, proposals, client onboarding, scheduling, invoicing, chasing payments, reporting to clients.
- **Typical pains:** proposal writing, unbilled hours, document collection from clients.
- **Reviews live on:** Google Maps, ProvenExpert, Trustpilot, Clutch (agencies), LinkedIn.

### Hotels, B&Bs, holiday rentals

- **Typical activities:** booking management across platforms, guest messages, check-in instructions, cleaning schedules, reviews replies, pricing.
- **Typical pains:** channel sync (Booking.com/Airbnb/direct), repetitive guest questions, review replies, OTA commissions.
- **Reviews live on:** Google Maps, Booking.com, Airbnb, TripAdvisor, HolidayCheck.

### Education, tutoring, kids' activities

- **Typical activities:** enrolment, scheduling, parent communication, payments, progress updates.
- **Typical pains:** parent messages at all hours, rescheduling, payment chasing.
- **Reviews live on:** Google Maps, Facebook, local parent forums.

---

## Germany-specific checks (and similar markets)

- **Impressum** (legal notice) is mandatory for commercial sites. It names the legal entity, which often reveals sister businesses or the operating company. A missing or broken Impressum is a legal risk, so flag it.
- **Datenschutzerklärung** (privacy policy) and cookie consent are required under GDPR.
- Common local platforms: coolibri.de (compiles Google reviews), Trusted Shops (web shops), Treatwell, Planity, Doctolib, Jameda, Quandoo, Lieferando, Wolt, golocal, Das Örtliche, Gelbe Seiten, MyHammer, rausgegangen (events).
