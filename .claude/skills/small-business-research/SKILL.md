---
name: small-business-research
description: Research a small or local business from its public footprint (website, Instagram, Google Maps rating and reviews, booking and review platforms, press) and write a grounded business profile covering what the business does, how it runs today, its likely pain points and concrete suggestions for where AI or simple fixes could help. Use this whenever the user gives a business URL, Instagram handle, Google Maps link or a business name and city and wants to understand, profile, scrape, audit, pitch to, prepare a call with or onboard that business. Example requests include "look into this café", "what are this salon's pain points", "scrape this shop's site and reviews", "what could AI do for this bakery" and "generate a business profile for the Teach Your AI demo". Use it even when the user only names one source (e.g. "check their Google reviews"), because the other sources make the analysis much better.
---

# Small business research

Build an honest, evidence-backed picture of a small business from what it shows the public. The output answers three questions:

1. **What is this business?** Say it in plain words, the way a regular customer would describe it.
2. **Where does it hurt?** Find where the owner is likely losing time, money or customers, and give the evidence.
3. **What would help?** Suggest a few concrete things the owner would recognise as their own work ("handling party bookings"), not technology ("an LLM agent").

The reader is often going to put this in front of the owner, or use it to start a conversation with them. Overclaiming ruins that, so keep what you *saw* separate from what you *inferred* and from what is merely *typical* for the category.

## Tools

The bundled script `scripts/scout.mjs` (in this skill's directory) needs Node 22+ and a local Chrome or Chromium. It prints JSON.

| Command | What it gets |
|---|---|
| `node scout.mjs page <url> [<url>…] [--check-links]` | Renders the page with JavaScript (many small-business sites are empty without it). Returns text, headings, meta/OG tags, JSON-LD, site builder, links sorted by platform (Instagram, booking tools, delivery apps…), emails and phones. With `--check-links` it also loads every internal link without JavaScript and reports status codes. |
| `node scout.mjs maps <maps-url \| "name, street, city">` | Google Maps listing: rating, review count, category, address, hours, attributes, quoted review snippets, review topic chips and, when Google shows them, a handful of full review texts (often the 5 "most relevant") with owner replies. Reviewer names are dropped. |
| `node scout.mjs instagram <handle>` | Followers, following and post count. That's all Instagram shows logged-out visitors. |
| `node scout.mjs places "name, street, city"` | Google Places API, only if `GOOGLE_MAPS_API_KEY` is set. Gives rating, review count, hours and the 5 "most relevant" reviews. Reliable when available. |

If there's no Chrome, use WebFetch or `curl` for pages. Note in the report that a JavaScript-only site may have looked empty. Read PDFs (menus, price lists) by downloading them into the scratchpad with `curl` and opening them with the Read tool.

## Workflow

Aim for roughly 25–40 tool calls. This is a snapshot, not an audit. Run independent steps in parallel.

### 1. Website (the main source)

Start with `scout.mjs page <homepage> --check-links`. From its links, pick the 2–5 most informative subpages: about, services/prices/menu, booking, events, team/jobs, contact, Impressum/legal. Render them in one call. Download and read linked PDFs.

Note as you go:
- What they sell, to whom, at what prices, with what vibe or positioning.
- **How things get done today.** How do customers book, order, ask questions or plan events? Phone only? Email? A platform? This is where most pain points come from.
- Hours, location, languages, team size hints, job ads, supplier and brand names.
- The legal operator (Impressum, footer ©). It often reveals sister businesses.
- Site health from the JSON: `needs_javascript`, `tech`, `link_check` 404s, wrong `lang`, builder-default `og:image`, missing `jsonld`.

**If the site has a shop, read its public product feed.** Shopify shops serve `<site>/products.json` (add `?limit=250`), and WooCommerce shops serve `<site>/wp-json/wc/store/v1/products?per_page=100`. Fetch them with `curl` into the scratch folder. A shop built on Shopify shows `Shopify` in `tech`, and one on WooCommerce shows `WordPress` plus `/product/` links. The feed gives you facts no page shows directly:
- how many products there are, and what share is out of stock but still listed
- price ranges, and duplicate listings (e.g. "- Wholesale" copies) that mean everything is entered by hand twice
- creation dates, which show how often new products launch
- copy-paste errors: sizes in the title that don't match the variants, typos, `-copy` handles

If no URL was given, find the website first. Use WebSearch for the name and city, or `scout.mjs maps "name, city"`, which returns the listed website.

### 2. Reviews: Google Maps plus at least one other source

Reviews are the best source of *real* pain points. Customers name the slow service, the booking mix-up and the overpriced cheese plate. Owner replies show how the owner thinks and whether they respond at all.

**Google Maps first.** Use the Maps link from the website if there is one, otherwise `"name, street, city"`. Note the rating, the count, the topic chips (what people mention most) and how many visible reviews have owner replies. Logged out, Google shows at most about 5 reviews, and often a "limited view" with only quoted snippets. The script retries once. If a `GOOGLE_MAPS_API_KEY` is set, run `places` too.

**Then always check at least one other review source.** Five "most relevant" reviews are too few to call something a pattern. Find each source with a WebSearch for the business name plus the platform, then read it with `scout.mjs page <url>`:

| Source | Use it for | What it adds |
|---|---|---|
| **TripAdvisor** | Cafés, restaurants, bars, hotels, attractions | Dozens of full, dated reviews, often from tourists. Check for duplicate or unclaimed listings (e.g. one at an old address) and whether the owner replies. |
| **coolibri.de** | German businesses | Compiles Google reviews: star distribution, theme scores (food, service, ambience, price), the trend by year, which season reviews come in, and how many have an owner reply. Comparing replies in the last 12 months with older ones shows whether the owner has stopped keeping up. |
| **Restaurant Guru** | Food and drink outside Germany | Similar Google review compilation with themes. |
| **Trusted Shops** | Any business with a web shop (look for the badge in the footer) | Shop rating and count, recent order reviews, merchant replies. Compare it with the café or store rating: a gap shows where the experience breaks. |

Other platforms by category are in `references/signals.md` → category playbooks (Treatwell for salons, Doctolib for practices, Booking.com for hotels…).

If a platform shows a captcha or bot check, or a page answers 403 Forbidden, record it as `blocked` and move to the next source. Don't retry it with a different tool. If nothing beyond Google's snippets is readable, say so, and ask the user to paste a few reviews if they want more.

From all sources together, note the recurring complaints and praise with dates, and how much of the business's review volume you actually read.

### 3. Instagram and other channels

Run `scout.mjs instagram <handle>` with the handle from the website links. A following/followers ratio near 1 suggests growth through follow-back. Logged-out Instagram shows no bio or post dates. If a browser tool is available and already signed in, you may read the profile (bio, date of the last post, how often they post). Otherwise a WebSearch for the handle sometimes surfaces captions. Never log in or create accounts.

Then run 2–4 quick WebSearches for press or local guides, directory listings (do their hours match the website?), job posts, booking and delivery platforms and sister venues.

### 4. Analyse

Read `references/signals.md` now. It maps what you found (signals) to likely pains and to what could help, and gives category playbooks for typical weekly activities.

- **Pain points.** Pick the 3–7 that best combine *impact on the owner* with *strength of evidence*. Start from the signals you found, not from a generic SMB list. One vivid, sourced pain (a 1-star review about a botched private party, with the owner admitting the booking process needs fixing) beats five generic ones.
- **Suggestions.** Give 3–5 business activities where AI could take work off the owner's plate. Each ties back to a pain point and is phrased as the owner's own work. For each, write the *opening question* you'd ask the owner to learn how they do it today. That's the start of a useful conversation.
- **Quick wins.** List cheap non-AI fixes (broken legal pages, mismatched hours, missing preview image). Keep them separate so they don't crowd out the bigger story.

### Evidence labels

Tag every pain point and every notable claim:
- **Seen**: directly observed. Cite the source (page, review, listing).
- **Inferred**: reasoned from something seen. Say the reasoning in a few words.
- **Typical**: common for this kind of business, not observed here. Use sparingly. It usually works better as an open question for the owner.

## Ground rules

- **Public information only. Respect walls.** If a site shows a captcha, a bot check ("checking your browser", "unusual traffic"), or a login wall, stop and record it as `blocked` in the sources table. Don't solve captchas, rotate identities or log in to get around it. Those defences are the site owner's call, and the gap itself is worth reporting.
- **People's privacy.** Don't record reviewer names or profile details. Paraphrase reviews, and quote only short snippets that carry the point. It's fine to name the business's operator or legal entity. Leave staff out unless the business itself features them publicly.
- **Quote faithfully, in the original language**, with a translation when the report language differs. Write the report in the user's language.
- **Date things.** Reviews and listings age, and "a year ago" matters. Put the research date in the report.

## Output

Save two files under `business-profiles/<business-slug>/` in the current working directory, unless the user asked for somewhere else:

**`profile.md`**, the readable report:

```markdown
# <Business name>: business snapshot
<one-line positioning> · <neighbourhood, city> · researched <YYYY-MM-DD>

## At a glance
| | |
|---|---|
| Category | … |
| Location | … |
| Hours | … |
| Price level | … (with 2–3 example prices) |
| Rating | 4.9 ★ (106 Google reviews) · topics: … |
| Channels | website (builder), Instagram (n followers, n posts), booking via … |
| Operator | legal entity · sister businesses |

## What they do
2–4 sentences a customer would recognise: offer, audience, vibe, what makes them distinct.
Then a short list of products/services with example prices.

## How the business runs today
Bullets of observed operations: how bookings, orders, inquiries, events, menus/prices,
staffing and suppliers are handled. Each with its source.

## Pain points
### 1. <Owner-language title> (Seen | Inferred | Typical)
**Evidence:** what you saw, with source and date.
**Why it hurts:** the cost in time, money or customers.
(3–7 of these, most important first)

## Where AI could help
| Activity (owner's words) | What it would take off their plate | Linked pain | Needs / approval | Opening question for the owner |
(3–5 rows)

## Quick wins
Short bullets: fix → why → source.

## Open questions
What you couldn't verify and would ask the owner.

## Reaching out (only when the user plans to contact the owner, see below)

## Sources
| Source | Status (ok / partial / blocked / not found) | What it gave |
```

**`profile.json`** has the same content in structured form, for apps and demos:

```json
{
  "business": { "name": "", "category": "", "address": "", "city": "", "website": "", "phone": "", "email": "",
                "hours": [], "price_level": "", "languages": [], "operator": "", "related_businesses": [] },
  "description": "",
  "offerings": [{ "name": "", "price": "" }],
  "audience": "",
  "channels": { "instagram": { "handle": "", "followers": 0, "following": 0, "posts": 0 },
                "google": { "rating": 0, "review_count": 0, "topics": [] }, "other": [] },
  "operations": [{ "activity": "", "how_today": "", "source": "" }],
  "pain_points": [{ "title": "", "label": "seen|inferred|typical", "severity": "high|medium|low",
                    "evidence": [{ "source": "", "detail": "", "date": "" }], "why_it_hurts": "" }],
  "suggested_activities": [{ "activity": "", "how_ai_could_help": "", "pain_point": "", "needs": "",
                             "approval": "", "opening_question": "" }],
  "quick_wins": [{ "fix": "", "why": "", "source": "" }],
  "open_questions": [],
  "outreach": { "contact": "", "channel": "", "timing": "", "message": "" },
  "sources": [{ "name": "", "url": "", "status": "ok|partial|blocked|not_found", "note": "" }],
  "researched_at": "YYYY-MM-DD"
}
```

### Outreach draft

Add the "Reaching out" section, and fill `outreach` in the JSON, only when the user says they're going to contact the owner: "I want to reach out", "pitch them", "I'm meeting them next week", "prep me for a call". Otherwise leave both out.

- **Who and how:** the owner's name if the business publishes it (About page, Impressum, press), and the public channels: the business email, an Instagram DM, or in person. Prefer the business's own contact points over personal numbers from the Impressum. Note good and bad timing you found evidence for (roast days, opening hours, a busy season).
- **The message:** a short, ready-to-send email or DM in the language the business uses with customers. Leave placeholders like `[your name]` and `[one line on who you are]` for whatever you don't know about the user.
  - Open with something specific and genuine: an award, a press feature, a dish people rave about in reviews.
  - Give before asking: 2–3 concrete quick wins from the profile that the owner can check in a minute (a broken link, mismatched hours).
  - Name one pain point in the owner's terms, and offer one concrete thing tied to it, e.g. a draft built from their own reviews or menu.
  - End with a small ask, such as a 20-minute coffee. Keep it under 200 words.
- **Tone:** respect the craft. Don't open with "AI", and don't mention sensitive things you found (a closed second site, a bad review naming staff, personal history). Put those in "Open questions" for a face-to-face conversation instead.
- **Never send anything.** The draft is for the user to edit and send themselves.

### Chat summary

In chat, give a short summary: the description, the top 3 pain points with their evidence, the top suggestions, and anything blocked or missing. If you drafted an outreach message, paste it in the chat too, since the user will want to copy it. Then link the two files. The user shouldn't have to open the file to get the gist.
