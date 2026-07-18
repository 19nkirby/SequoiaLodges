# Google Ads Launch Checklist — Sequoia Lodges

Everything below is ready to click through in [ads.google.com](https://ads.google.com). The site side is already built: attribution capture, AJAX form submission, and conversion events are live in `tracking.js` on every page. The only wiring left is pasting two conversion IDs (step 4).

**Sources reconciled:** the full lead-gen system plan, the paid-media recommendation, and the SKAG forecast built from the live Keyword Planner pull (July 12, 2026). Where they conflict, the keyword-data-driven SKAG plan wins: **exact/phrase match across 9 tight ad groups — no broad match at launch.** And per owner policy this is an **email-only business — no call tracking, no phone conversions, no phone CTAs.** The single primary conversion is a Formspree-accepted form lead.

---

## 0. Set expectations first (from the live keyword data)

The measured exact-theme market in Massachusetts is small:

- **~190 deduplicated searches/month** across all ADU plan/design themes
- **~11.4 modeled clicks/month** at 6% CTR → **~0.57 modeled leads/month** at 5% CVR
- Modeled CPA ≈ **20 × actual CPC** ($2 CPC → $40 CPA; $5 → $100; $10 → $200)

What this means operationally:

1. **The constraint is demand, not budget.** Expect the $15/day cap to go largely unspent with exact/phrase match. That is correct behavior — do not raise budget or loosen match types to force spend.
2. **Don't judge conversion rate on fewer than ~100 clicks**, which may take months at this volume. Judge early performance on search-term *quality* instead.
3. One good lead pays for months of this campaign at these prices ($3,500–$4,500 packages), so patience is economically rational.
4. Because paid demand is capped, **SEO/content is the long-term volume lever** — the landing pages and planning-kit guides are indexed with that in mind.

Budget tiers: $10/day lean validation · **$15/day recommended** · $25/day only after search-term quality and tracking are proven.

## 1. Account prerequisites

- [ ] Create the Google Ads account with `sequoialodges@gmail.com`.
- [ ] Turn **auto-tagging ON** (Admin → Account settings → Auto-tagging). This appends `gclid`, which the site captures automatically.
- [ ] Link Google Ads ↔ GA4 property `G-SN14KG7Y2M` (Admin → Linked accounts).
- [ ] Set billing, time zone `(GMT-05:00) Eastern Time`, currency USD.

## 2. Conversion actions

Create in Goals → Conversions → New conversion action → **Website**:

| Conversion action | Category | Goal setting | Count | Click-through window |
|---|---|---|---|---|
| `Accepted ADU Inquiry` | Submit lead form | **Primary** | One | 90 days |
| `Planning Kit Download` | Submit lead form | **Secondary** | One | 30 days |

For both, choose "Use Google tag" / manual event snippet — **do not** use automatic page-load detection. The site fires them only after Formspree confirms the submission (the "backend-accepted" principle, adapted to a static site).

GA4 events already flowing for diagnostics: `form_start`, `form_error`, `generate_lead`, `sample_kit_download`, `guide_view`, `email_click`, `sample_plan_download`. Do **not** import GA4 events as primary conversions — the Ads tag above is the single source of truth for bidding.

## 3. Enhanced conversions (optional, recommended later)

Once the Ads conversion tag is verified, enable Enhanced Conversions for Leads (Conversion settings → Enhanced conversions) using the Google tag. Revisit only after the basic tag is proven — one thing at a time.

## 4. Paste the conversion IDs into the site

After step 2, Google shows a conversion ID (`AW-XXXXXXXXX`) and a label per action. Edit [tracking.js](tracking.js) (top of file):

```js
window.SL_TRACKING = window.SL_TRACKING || {
    adsId: 'AW-XXXXXXXXX',          // your conversion ID
    inquiryLabel: 'AbCdEfGhIjK',    // label for Accepted ADU Inquiry
    magnetLabel: 'LmNoPqRsTuV'      // label for Planning Kit Download
};
```

Commit and push. The Google Ads site tag loads and conversions fire automatically — no other code changes.

**Verify before launching:** Google Tag Assistant (tagassistant.google.com) on sequoialodges.com → submit a test lead (mark it "TEST" in the message field) → confirm exactly ONE conversion event fires, only after the success redirect begins. Also check the lead email arrived with `gclid`/`utm_*` fields populated (visit the site once with `?gclid=test123&utm_source=google&utm_medium=cpc` first).

## 5. Campaign settings

| Setting | Value |
|---|---|
| Campaign name | `Search \| MA \| ADU Plans \| Non-Brand` |
| Type / Goal | Search / Leads |
| Networks | Google Search only — **Search Partners OFF, Display OFF** |
| Location | Massachusetts (service focus: Boston, Cambridge, Newton, Brookline) |
| Location option | **Presence: in or regularly in** (NOT "interest") — under Location options |
| Language | English |
| Budget | $15/day (ceiling, not a spend target) |
| Bidding | **Maximize Clicks** with max CPC limit **$4.00** |
| Ad schedule | All day (adjust only from real evidence later) |
| Automatically created assets | OFF at launch |
| Final URL expansion | OFF |

**Campaign final URL suffix** (Settings → Additional settings → Campaign URL options → Final URL suffix):

```
utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_term={keyword}&utm_content={creative}&campaign_id={campaignid}&ad_group_id={adgroupid}&creative_id={creative}&keyword={keyword}&matchtype={matchtype}&device={device}
```

The site captures every one of these into the lead email automatically.

## 6. Ad groups and keywords (SKAG structure, exact + phrase only)

Nine single-theme ad groups. In each, add the keywords as **both** `[exact]` and `"phrase"`. Do not duplicate close variants across ad groups; add cross-ad-group negatives only if real queries show routing problems.

| Ad group | Keywords (add each as exact + phrase) | Searches/mo | Landing page |
|---|---|---:|---|
| `SKAG \| ADU Plans` | adu plans · accessory dwelling unit plans · adu home plans · adu house plans | 70 | `/adu-plans` |
| `SKAG \| ADU Design` | adu design · adu designer · adu design plans | 40 | `/adu-design-engineering` |
| `SKAG \| ADU Floor Plans` | adu floor plans · accessory dwelling unit floor plans | 20 | `/adu-plans` |
| `SKAG \| ADU Architect` | adu architect · architect for adu · adu architect near me · adu architect cost | 10 | `/adu-design-engineering` |
| `SKAG \| Permit Ready ADU` | permit ready adu plans · pre approved adu plans · adu approved plans | 10 | `/permit-ready-adu-plans` |
| `SKAG \| 1 Bedroom ADU` | 1 bedroom adu plans · 1 bedroom adu floor plans · one bedroom adu plans | 10 | `/adu-plans` |
| `SKAG \| 2 Bedroom ADU` | 2 bedroom adu plans · adu plans 2 bedroom · 2 bedroom adu floor plans | 10 | `/adu-plans` |
| `SKAG \| Garage ADU` | garage adu plans · adu garage plans · adu plans with garage | 10 | `/adu-design-engineering` |
| `SKAG \| Backyard Cottage` | backyard cottage plans · backyard adu plans · backyard cottage design | 10 | `/adu-plans` |

**Local zero-volume exacts** (strategically relevant; Planner rounds them to 0 — keep as exact-only additions, no separate budget): add `[permit ready adu plans boston]`, `[permit ready adu plans massachusetts]` to the Permit Ready ad group; `[adu plans boston]`, `[adu plans massachusetts]` to ADU Plans; `[adu design boston]`, `[adu architect boston]` to their ad groups. Add more city variants (cambridge/newton/brookline) only if impressions actually appear.

**No broad match at launch.** If after 4–6 weeks spend is far below budget AND search-term quality is clean, the controlled expansion is: add ONE broad keyword (`adu plans`) to its own ad group with the full negative list, and watch it twice weekly. That is the month-2 decision, not a launch setting.

## 7. Responsive search ads — ONE per ad group at launch

Nine RSAs per ad group would fragment ~11 clicks/month into noise. Launch one theme-matched RSA per ad group; add a second bundle only after query quality is proven (month 2+).

Pin nothing; give Google 6–10 headlines and 2–3 descriptions per ad. All copy below is ≤30/≤90 chars and phone-free.

**SKAG | ADU Plans** → `/adu-plans`
- H: ADU Plans From $3,500 · Boston ADU Plan Packages · View Plans and Pricing · Plans Tailored to Your Lot · Studio to 2-Bedroom Plans · Massachusetts ADU Experts · Complete ADU Drawing Sets · Permit-Ready Plan Sets
- D: Compare studio, one-bedroom, and two-bedroom ADU plans designed for Massachusetts homeowners. · Choose a plan, tailor it to your lot, and receive a complete drawing package for permitting.

**SKAG | ADU Design** → `/adu-design-engineering`
- H: Massachusetts ADU Design · ADU Architects and Engineers · Site-Specific Engineering · Complete ADU Design Sets · Structural Design Available · Designed for Your Property · Boston ADU Engineering · ADU Design From $3,500
- D: Get coordinated ADU design and engineering from a Massachusetts firm focused on Boston-area projects. · Plans can include structural and MEP design based on the selected package and project requirements.

**SKAG | ADU Floor Plans** → `/adu-plans`
- H: View ADU Floor Plans · ADU Plans From $3,500 · Studio to 2-Bedroom Layouts · Compare Plans and Pricing · Plans Tailored to Your Lot · Boston ADU Floor Plans · Start With a Proven Layout · Complete Drawing Sets
- D: Compare studio, one-bedroom, and two-bedroom ADU floor plans with clear package pricing. · Choose a layout and have it tailored to your property by a Massachusetts ADU design firm.

**SKAG | ADU Architect** → `/adu-design-engineering`
- H: ADU Architects and Engineers · Massachusetts ADU Experts · Licensed MA Coordination · Site-Specific ADU Design · Fixed-Price Plan Packages · Complete Architectural Plans · Design Your Boston ADU · Floor Plans and Elevations
- D: Work with an ADU-focused Massachusetts design firm for coordinated plans and site-specific engineering. · Receive floor plans, elevations, sections, compliance notes, and engineering based on your package.

**SKAG | Permit Ready ADU** → `/permit-ready-adu-plans`
- H: Permit-Ready ADU Plans · Move Toward Permitting Fast · Designed for Boston Rules · Skip Months of Redesign · BPDA-Compliant Plan Sets · Filing-Ready in Two Weeks · Plans Ready for Your Lot · Greater Boston ADU Plans
- D: Start with a pre-designed ADU plan and move toward a filing-ready package without a blank-page design phase. · Get coordinated plans tailored to your property and designed around Boston-area ADU requirements.

**SKAG | 1 Bedroom ADU** → `/adu-plans`
- H: 1-Bedroom ADU Plans · 1BR ADU Plan Set: $4,000 · Structural Design Included · 550–750 SF Layouts · Permit-Ready Plan Sets · Tailored to Your Lot · Boston 1-Bedroom ADUs · Compare ADU Plan Packages
- D: One-bedroom ADU plan sets with structural engineering included, tailored to Massachusetts lots. · Fixed $4,000 package. Choose the plan, we adapt it to your property, you file for permit.

**SKAG | 2 Bedroom ADU** → `/adu-plans`
- H: 2-Bedroom ADU Plans · 2BR Plan Set: $4,500 Fixed · Full Structural + MEP Design · Our Most Requested Plan · 800–900 SF Layouts · Permit-Ready Plan Sets · Boston 2-Bedroom ADUs · Strong Rental Layouts
- D: Two-bedroom ADU plans with full structural and MEP engineering — our most requested package. · Fixed $4,500 package tailored to your lot and designed around Boston-area ADU requirements.

**SKAG | Garage ADU** → `/adu-design-engineering`
- H: Garage ADU Plans · Garage Conversion Design · Site-Specific Engineering · Massachusetts ADU Experts · Structural Design Included · Custom Scope by Inquiry · Boston Garage ADUs · Engineered for Your Lot
- D: Converting or replacing a garage with an ADU takes real engineering. Site-specific design for MA lots. · Tell us about your garage and lot — we'll give you an honest read on fit and a fixed-price path.

**SKAG | Backyard Cottage** → `/adu-plans`
- H: Backyard Cottage Plans · Backyard ADU Plan Sets · Plans From $3,500 · Permit-Ready Designs · Studio to 2-Bedroom Plans · Tailored to Your Lot · Boston Backyard ADUs · Complete Drawing Sets
- D: Pre-designed backyard cottage and ADU plans for Massachusetts lots, ready for permitting. · Compare studio, one-bedroom, and two-bedroom packages with clear fixed pricing.

**Law/education intent (from the July 2026 marketing plan):** the gated lead magnet `/massachusetts-adu-guide` and the `/adu-cost-calculator` are live for education-intent queries (`massachusetts adu law`, `can i build an adu in massachusetts`, `adu by right massachusetts`, `affordable homes act adu`). These convert lower but feed the nurture list — if added, make it a separate `SKAG | ADU Law` ad group at exact/phrase, landing on `/massachusetts-adu-guide`, and judge it on magnet leads (Secondary conversion), not inquiries. Both pages fire the same `magnet` conversion flow via tracking.js (`data-variant`: `law-guide`, `cost-calculator`).

Sitelinks (campaign level): Plans & Pricing (`/adu-plans#pricing`) · Free Planning Kit (`/adu-planning-kit.html`) · MA ADU Law Guide (`/massachusetts-adu-guide.html`) · Cost Calculator (`/adu-cost-calculator.html`)

Callouts: Fixed Pricing · Engineering Included · 2-Week Turnaround · BPDA Compliant · No Sales Calls · Plans, Not Construction

## 8. Negative keywords (campaign level, at launch)

Merged from all three source docs. The keyword data confirms design-build/construction intent is the biggest waste risk — the ads and pages both say "plans, not construction," and these negatives enforce it:

```
free
diy
kit
kits
prefab
prefabricated
modular
manufacturer
contractor
builder
construction company
design build
design and build
for sale
shed
sheds
tiny home
tiny house
container
jobs
job
salary
career
hiring
course
software
template
app
zoning map
rent
for rent
apartment
airbnb
```

Do **not** pre-negative `permit`, `architect`, `engineer`, `cost`, or `construction plans` — often buying intent. Judge from actual search terms. (Watchlist from the data: `adu construction plans` sits right on the line — check what those queries actually want before blocking.)

## 9. Operating cadence (first month)

- [ ] **Twice weekly:** review Search terms report; add negatives; confirm spend is on plan/design intent.
- [ ] **Weekly:** compare Ads-reported conversions to actual Formspree lead emails (each has an `event_id` — they should reconcile 1:1).
- [ ] **Expect low spend.** Exact/phrase on a 190-search/month market will not consume $15/day. Unspent budget is not a problem to fix.
- [ ] **Rollback rule:** if ~$150 spends with zero accepted leads AND search terms look irrelevant, pause and reassess. If terms look right but volume is just tiny, keep running — see §0.
- [ ] Log every lead's outcome (new → contacted → qualified → purchased / disqualified) in a simple spreadsheet with its `event_id` and `gclid` — this becomes the offline-import source later.

## 10. Month-2+ expansion path (in order)

1. Add a second RSA bundle to the top-performing ad group(s).
2. Controlled broad-match test: one broad `adu plans` keyword in its own ad group (see §6).
3. Microsoft Ads import ($5/day, UET installed, `msclkid` already captured by the site) — only after Google query quality is understood.
4. Meta/YouTube remarketing — only once audiences are actually usable (hundreds of visitors, not dozens).

## 11. Bidding transition (month 3, evaluate — don't auto-switch)

Move to **Maximize Conversions** only when ALL are true:

- [ ] Conversion tracking verified and duplicates absent (event_id reconciliation clean).
- [ ] Kit downloads, email clicks, and form starts are Secondary (never primary).
- [ ] Search terms are stable and relevant.
- [ ] Meaningful recent primary conversion volume (Google's guidance: ~15+ in 30 days — at modeled demand this may take many months; that's fine).

If volume is too low, stay on Maximize Clicks. The calendar is not a bidding signal. When you do switch, run Maximize Conversions **without** a target CPA first; add tCPA only after real qualified-lead CPA stabilizes.
