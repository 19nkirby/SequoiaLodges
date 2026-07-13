# Google Ads Launch Checklist — Sequoia Lodges

Everything below is ready to click through in [ads.google.com](https://ads.google.com). The site side is already built: attribution capture, AJAX form submission, and conversion events are live in `tracking.js` on every page. The only wiring left is pasting two conversion IDs (step 4).

Adapted from the full lead-gen system plan: **email-only business — no call tracking, no phone conversions.** The single primary conversion is a Formspree-accepted form lead.

---

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

For both, choose "Use Google tag" / manual event snippet — **do not** use automatic page-load detection. The site fires them only after Formspree confirms the submission (this is the "backend-accepted" principle, adapted to a static site).

GA4 events `form_start`, `form_error`, `generate_lead`, `sample_kit_download`, and `guide_view` are already flowing for diagnostics. Do **not** import GA4 events as primary conversions — the Ads tag above is the single source of truth for bidding.

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
| Location | Massachusetts (or tighter: Boston, Cambridge, Newton, Brookline + radius) |
| Location option | **Presence: in or regularly in** (NOT "interest") — under Location options |
| Language | English |
| Budget | $15/day |
| Bidding | **Maximize Clicks** with max CPC limit **$4.00** |
| Ad schedule | All day (adjust only from real evidence later) |
| Automatically created assets | OFF at launch |
| Broad match keywords setting (campaign level) | OFF — set match types per keyword |
| Final URL expansion | OFF |

**Campaign final URL suffix** (Settings → Additional settings → Campaign URL options → Final URL suffix):

```
utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_term={keyword}&utm_content={creative}&campaign_id={campaignid}&ad_group_id={adgroupid}&creative_id={creative}&keyword={keyword}&matchtype={matchtype}&device={device}
```

The site captures every one of these into the lead email automatically.

## 6. Ad groups, keywords, landing pages

One broad keyword per ad group (single-keyword broad + smart bidding comes later; at launch, broad match with a $4 cap and tight negatives):

| Ad group | Keyword | Landing page |
|---|---|---|
| `AG \| ADU Plans` | `adu plans` | `https://sequoialodges.com/adu-plans` |
| `AG \| ADU Design` | `adu design` | `https://sequoialodges.com/adu-design-engineering` |
| `AG \| ADU Floor Plans` | `adu floor plans` | `https://sequoialodges.com/adu-plans` |
| `AG \| Permit Ready` (optional 4th) | `adu permit` | `https://sequoialodges.com/permit-ready-adu-plans` |

## 7. Responsive search ads

One RSA per ad group. Headlines (mix and match, ≤30 chars each):

**AG | ADU Plans**
- ADU Plans From $3,500
- Permit-Ready ADU Plans
- Boston ADU Plan Sets
- Fixed-Price ADU Plans
- Studio, 1BR & 2BR ADU Plans
- File For Permit In 2 Weeks
- BPDA-Compliant ADU Plans
- Engineering Included
- Tailored To Your Lot
- See Plans & Pricing Online

**AG | ADU Design**
- ADU Design & Engineering
- Structural + MEP Included
- Licensed MA Engineers
- Site-Specific ADU Design
- Boston ADU Design Firm
- Fixed-Price ADU Design
- No Months Of Custom Design
- Tailored To Your Lot

**AG | ADU Floor Plans / Permit Ready** — reuse from the two lists above plus:
- ADU Floor Plans That File
- Real Plan Sets, Not JPEGs
- Article 53 Compliant Plans
- Permit-Ready In 2 Weeks

Descriptions (≤90 chars):
- Complete permit-ready ADU plan sets for Boston lots. $3,500–$4,500 fixed. Engineering included.
- Pick a plan, we tailor it to your lot, you file within two weeks. BPDA & Article 53 compliant.
- Coordinated with licensed MA architects & engineers. Fixed pricing, no hourly design fees.
- Get a plan recommendation for your lot within one business day. Email-based, no sales calls.

Sitelinks: Plans & Pricing (`/adu-plans#pricing`), Free Planning Kit (`/adu-planning-kit.html`), What Permit-Ready Means (`/permit-ready-adu-plans`), Design & Engineering (`/adu-design-engineering`).

Callouts: Fixed Pricing · Engineering Included · 2-Week Turnaround · BPDA Compliant · No Sales Calls

## 8. Negative keywords (campaign level, at launch)

```
free
diy
kit
kits
prefab
prefabricated
modular
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
software
app
course
rent
for rent
rental listing
apartment
airbnb
how to build yourself
plans pdf free
```

Do **not** pre-negative `permit`, `architect`, `engineer`, `cost`, or `construction plans` — those are often buying intent. Judge them from actual search terms.

## 9. Operating cadence (first month)

- [ ] **Twice weekly:** review Search terms report; add negatives; confirm spend is on plan/design intent.
- [ ] **Weekly:** compare Ads-reported conversions to actual Formspree lead emails (each has an `event_id` — they should reconcile 1:1).
- [ ] **Rollback rule:** if ~$150 spends with zero accepted leads and search terms look irrelevant, pause and reassess keywords/pages rather than raising budget.
- [ ] Log every lead's outcome (new → contacted → qualified → purchased / disqualified) in a simple spreadsheet with its `event_id` and `gclid` — this becomes the offline-import source later.

## 10. Bidding transition (month 3, evaluate — don't auto-switch)

Move to **Maximize Conversions** only when ALL are true:

- [ ] Conversion tracking verified and duplicates absent (event_id reconciliation clean).
- [ ] Kit downloads and form starts are Secondary (never primary).
- [ ] Search terms are stable and relevant.
- [ ] Roughly 15+ accepted-lead conversions in the last 30 days.

If volume is too low, stay on Maximize Clicks. The calendar is not a bidding signal.

---

*Later phases (Microsoft Ads, Meta, remarketing, offline conversion imports, nurture automation) are deliberately excluded — sequence them only after Google Search is producing reconciled, qualified leads.*
