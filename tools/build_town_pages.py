#!/usr/bin/env python3
"""Generate the per-town ADU plan pages from tools/towns.json.

The site has no build step and the generated HTML is committed, so this script
is a convenience for keeping ~N town pages consistent — not a dependency of
deployment. Run it after editing towns.json, then commit the output:

    python3 tools/build_town_pages.py

Every factual claim in the template below is either statewide (760 CMR 71.00 /
Affordable Homes Act) or comes from a verified per-town field in towns.json.
Do not add per-town assertions here; add them to towns.json where they can be
sourced and dated.
"""

import datetime
import json
import pathlib
import sys
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "towns.json"

SITE = "https://sequoialodges.com"
FORM = "https://formspree.io/f/maqgzynr"

# The site's design tokens and chrome, lifted from index.html so generated
# pages are visually identical to hand-authored ones.
HEAD_STYLE = """    <style>
        :root {
            --ink: #16241b;
            --primary: #0f3b24;
            --primary-dark: #082014;
            --paper: #faf6ec;
            --line: rgba(15,59,36,0.18);
            --line-soft: rgba(15,59,36,0.10);
            --rust: #b85c2c;
        }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: var(--ink);
            background-color: var(--paper);
        }
        h1, h2, h3, .display {
            font-family: 'Source Serif 4', Georgia, 'Times New Roman', serif;
            font-weight: 600;
            letter-spacing: -0.005em;
            line-height: 1.12;
        }
        .eyebrow {
            font-family: 'Inter', sans-serif;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.14em;
        }
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-family: 'Inter', sans-serif;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            padding: 0.95rem 1.75rem;
            border-radius: 3px;
            border: 1px solid var(--primary);
            transition: background-color .15s, color .15s;
        }
        .btn-solid { background-color: var(--primary); color: var(--paper); }
        .btn-solid:hover { background-color: var(--primary-dark); }
        .btn-outline { background-color: transparent; color: var(--primary); }
        .btn-outline:hover { background-color: rgba(15,59,36,0.06); }
        .btn-cream { background-color: var(--paper); color: var(--primary); border-color: var(--paper); }
        .btn-cream:hover { background-color: #efe8d8; }
        .blueprint-grid {
            background-image:
                linear-gradient(var(--line-soft) 1px, transparent 1px),
                linear-gradient(90deg, var(--line-soft) 1px, transparent 1px);
            background-size: 36px 36px;
        }
        .tag {
            display: inline-block;
            border-top: 1px solid var(--primary);
            border-bottom: 1px solid var(--primary);
            padding: 0.4rem 0;
        }
        .field {
            width: 100%;
            background: transparent;
            border: none;
            border-bottom: 1px solid var(--line);
            padding: 0.6rem 0.1rem;
            font-family: 'Inter', sans-serif;
        }
        .field:focus { outline: none; border-bottom-color: var(--primary); }
        .field::placeholder { color: #8a9089; }
        table.schedule th, table.schedule td {
            border-bottom: 1px solid var(--line);
            padding: 1.1rem 1rem;
            text-align: left;
        }
        table.schedule th {
            font-family: 'Inter', sans-serif;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #56604f;
            font-weight: 600;
            border-bottom: 1px solid var(--primary);
        }
        table.schedule tr.featured { background-color: rgba(15,59,36,0.05); }
        .num { font-family: 'Source Serif 4', Georgia, serif; font-weight: 500; color: var(--rust); }
        .deliverable { border-top: 1px solid var(--line); padding: 1.4rem 0; }
        .rule-item { border-left: 2px solid var(--line); padding: 0.15rem 0 0.15rem 1.15rem; }
    </style>"""

ANALYTICS = """    <!-- Google Analytics (GA4) + Consent Mode v2 -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-SN14KG7Y2M"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('consent', 'default', {
        ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'denied',
        region: ['AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE','GR','HU','IE','IS','IT','LI','LV','LT','LU','MT','NL','NO','PL','PT','RO','SK','SI','ES','SE','GB','CH']
      });
      gtag('consent', 'default', {
        ad_storage: 'granted', ad_user_data: 'granted', ad_personalization: 'granted', analytics_storage: 'granted'
      });
      gtag('set', 'url_passthrough', true);
      gtag('config', 'G-SN14KG7Y2M');
    </script>
    <script defer src="/tracking.js"></script>"""

HEADER = """    <header class="w-full">
        <div class="container mx-auto px-6 py-5 flex items-center justify-between">
            <a href="/">
                <img src="/logo.svg" alt="Sequoia Lodges" class="h-11 w-auto">
            </a>
            <nav class="hidden md:flex items-center gap-10 eyebrow text-[var(--ink)]">
                <a href="/" class="hover:text-[var(--rust)]">Home</a>
                <a href="/adu-plans.html" class="hover:text-[var(--rust)]">Plans</a>
                <a href="/massachusetts-adu-guide.html" class="hover:text-[var(--rust)]">MA ADU Law</a>
                <a href="/adu-cost-calculator.html" class="hover:text-[var(--rust)]">Calculator</a>
                <a href="#contact" class="hover:text-[var(--rust)]">Contact</a>
            </nav>
            <a href="mailto:sequoialodges@gmail.com?subject=ADU%20plan%20inquiry" class="btn btn-outline">sequoialodges@gmail.com</a>
        </div>
    </header>"""

FOOTER = """    <footer class="py-8">
        <div class="container mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4 text-sm">
            <div class="flex items-center gap-3">
                <img src="/logo.svg" alt="Sequoia Lodges" class="h-7 w-auto">
                <span class="text-[#56604f]">&copy; 2026 Sequoia Lodges LLC</span>
            </div>
            <div class="flex items-center gap-6 text-[#56604f]">
                <a href="/privacy-policy.html" class="hover:text-[var(--primary)]">Privacy</a>
                <a href="/terms-of-service.html" class="hover:text-[var(--primary)]">Terms</a>
            </div>
        </div>
    </footer>

    <script>
        feather.replace();
    </script>"""

PROJECT_BLOCK = """
    <!-- Built work -->
    <section class="border-t" style="border-color: var(--line);">
        <div class="container mx-auto px-6 py-20">
            <span class="eyebrow text-[#56604f]">Built Work</span>
            <h2 class="text-3xl md:text-4xl mt-3 mb-6 text-[var(--primary)]">We designed an ADU here.</h2>
            <div class="grid md:grid-cols-12 gap-10">
                <div class="md:col-span-7 space-y-5 text-[#3c463d] leading-relaxed">
                    <p>17R Harding Rd in Norwood is a two-bedroom ADU we designed &mdash; 756 square feet, two
                    bedrooms, one bath. We drew it and stamped it. Someone else built it, which is how
                    every one of our projects works. It is finished, occupied, and was listed for rent at
                    $2,246 a month in January 2026.</p>
                    <p>We show it because &ldquo;permit-ready&rdquo; is easy to claim and harder to demonstrate.
                    This set went through a real building department and a real contractor, and came out
                    the other side as a dwelling somebody lives in.</p>
                    <p class="text-sm text-[#56604f]">That rent figure is what this specific unit was listed
                    at on that date, not a projection for your property. Rents vary by town, size, and
                    condition, and we don't forecast them.</p>
                </div>
                <div class="md:col-span-5">
                    <div class="border p-7" style="border-color: var(--line); background: rgba(15,59,36,0.03);">
                        <div class="deliverable" style="border-top: none; padding-top: 0;">
                            <span class="eyebrow text-[#56604f]">Size</span>
                            <p class="text-2xl mt-1 num">756 sf</p>
                        </div>
                        <div class="deliverable">
                            <span class="eyebrow text-[#56604f]">Configuration</span>
                            <p class="mt-1 font-semibold">2 bed &middot; 1 bath</p>
                        </div>
                        <div class="deliverable">
                            <span class="eyebrow text-[#56604f]">Our role</span>
                            <p class="mt-1 font-semibold">Design &amp; engineering only</p>
                        </div>
                        <div class="deliverable">
                            <span class="eyebrow text-[#56604f]">Status</span>
                            <p class="mt-1 font-semibold">Built from our plans</p>
                        </div>
                        <div class="deliverable">
                            <span class="eyebrow text-[#56604f]">Town</span>
                            <p class="mt-1 font-semibold">Norwood, MA</p>
                        </div>
                    </div>
                </div>
            </div>
            <!--GALLERY-->
        </div>
    </section>
"""


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def project_images(town: dict) -> list:
    """Return the declared project images that actually exist on disk.

    Gating on existence means a missing or not-yet-added photo silently drops out
    instead of shipping a broken <img> to production.
    """
    found = []
    for img in town.get("project_images", []):
        path = ROOT / "images" / town["slug"] / img["file"]
        if path.is_file():
            found.append({**img, "src": f"/images/{town['slug']}/{img['file']}"})
    return found


def gallery_html(images: list) -> str:
    """Responsive gallery.

    One image: full width. Two: an equal side-by-side pair, which reads better
    than a big lead plus one orphaned thumbnail. Three or more: lead plus grid.
    """
    if not images:
        return ""

    if len(images) == 2:
        tiles = "".join(
            f"""
                <figure class="m-0">
                    <img src="{i["src"]}" alt="{esc(i["alt"])}" loading="lazy" decoding="async"
                         class="w-full object-cover" style="aspect-ratio: 3 / 2; border: 1px solid var(--line);">
                </figure>"""
            for i in images
        )
        return f"""
            <div class="grid md:grid-cols-2 gap-4">{tiles}
            </div>"""

    lead, rest = images[0], images[1:]
    tiles = "".join(
        f"""
                <figure class="m-0">
                    <img src="{i["src"]}" alt="{esc(i["alt"])}" loading="lazy" decoding="async"
                         class="w-full h-64 object-cover" style="border: 1px solid var(--line);">
                </figure>"""
        for i in rest
    )
    grid = (
        f"""
            <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">{tiles}
            </div>"""
        if rest
        else ""
    )
    return f"""
            <figure class="m-0">
                <img src="{lead["src"]}" alt="{esc(lead["alt"])}" loading="lazy" decoding="async"
                     class="w-full object-cover" style="max-height: 30rem; border: 1px solid var(--line);">
            </figure>{grid}"""


def render(town: dict) -> str:
    name = town["name"]
    slug = town["slug"]
    url = f"{SITE}/adu-plans-{slug}.html"
    own_path = town.get("own_path", False)

    title = f"ADU Plans in {name}, MA | PE-Stamped &amp; Permit-Ready | Sequoia Lodges"
    desc = (
        f"PE-stamped, permit-ready ADU plan sets for {name}, Massachusetts. "
        f"Flat-fee pricing from $3,500, filing-ready in about two weeks. "
        f"What the state ADU law allows and what {name} still reviews."
    )

    # Boston runs its own program rather than the statewide by-right provision, so the
    # statewide rules are presented as context there instead of as the operative path.
    if own_path:
        lede = (
            f"{name} runs its own ADU process rather than the statewide by-right provision. "
            f"The city's program is built around owner-occupied 1-, 2-, and 3-family homes, and "
            f"some projects still go to the Zoning Board of Appeal. We design to it, and we stamp the result."
        )
        framework_heading = "The statewide rules, and why they aren't the path here"
        framework_intro = (
            f"The Affordable Homes Act created a by-right ADU route under <strong>760 CMR 71.00</strong>, "
            f"Protected Use Accessory Dwelling Units. It is the operative path in most Massachusetts towns "
            f"&mdash; but not in {name}, which has its own process. The statewide rules are still worth "
            f"understanding, because they set the baseline everyone else is working from."
        )
    else:
        lede = (
            f"Since February 2025, a qualifying ADU is allowed <em>by right</em> in "
            f"single-family zoning across Massachusetts &mdash; {name} included. No variance, "
            f"no special permit, no trip to the zoning board. You still need a building permit, "
            f"and {name} still reviews the things it always reviewed."
        )
        framework_heading = f"What the state law actually gives you in {name}"
        framework_intro = (
            "The governing regulation is <strong>760 CMR 71.00</strong>, Protected Use Accessory "
            "Dwelling Units, under the Affordable Homes Act. It is worth knowing what it does and "
            "does not do."
        )

    notes = "".join(
        f'\n                        <li class="rule-item">{esc(n)}</li>' for n in town.get("local_notes", [])
    )
    energy = ""
    if town.get("energy_code"):
        energy = f"""
                    <div class="deliverable">
                        <span class="eyebrow text-[#56604f]">Energy code</span>
                        <p class="mt-2 text-[#3c463d] leading-relaxed">{esc(town["energy_code"])}</p>
                    </div>"""

    if town.get("featured_project"):
        gallery = gallery_html(project_images(town))
        wrapped = (
            f'<div class="mt-12">{gallery}\n                <figcaption class="text-sm text-[#56604f] mt-3">'
            f"17R Harding Rd, Norwood &mdash; designed and stamped by Sequoia Lodges, built by others."
            f"</figcaption>\n            </div>"
            if gallery
            else ""
        )
        project = PROJECT_BLOCK.replace("<!--GALLERY-->", wrapped)
    else:
        project = ""

    faq_entries = [
        (
            f"Can I build an ADU in {name}?",
            (
                f"{name} runs its own ADU program, aimed at owners living in 1-, 2-, and 3-family homes. "
                "Whether a specific parcel works depends on its zoning district, dimensions, existing "
                "conditions, and whether it needs Zoning Board of Appeal review. Send us the address "
                "and we'll give you an honest read. The city also runs free ADU workshops that are "
                "worth attending first."
                if own_path
                else f"Most single-family lots in {name} can, under the state's by-right ADU provision — "
                f"an ADU up to 900 square feet, or half your home's gross floor area, whichever is smaller. "
                f"We can't tell you a specific property qualifies without looking at it, and we won't pretend otherwise. "
                f"Send us the address and we'll give you an honest read."
            ),
        ),
        (
            "What does a plan set cost?",
            "Flat fees by size: $3,500 for a studio, $4,000 for a one-bedroom, $4,500 for a two-bedroom. "
            "Attached ADUs add about $3,000, because they need an as-built of the existing house tied into the new work. "
            "Up to three minor revisions are included.",
        ),
        (
            "What's in the set, and what isn't?",
            "In: general notes, floor plans, elevations, foundation plan, structural framing plans, cross-sections, "
            "and details — PE-stamped and ready to file. Not in: MEP drawings, which aren't required for residential "
            "permitting in Massachusetts; surveys and plot plans; water and sewer work; and HERS ratings. "
            "We don't build, either — your own contractor builds from the drawings.",
        ),
        (
            "How long does it take?",
            "About two weeks from go-ahead to a filing-ready set, assuming we have a plot plan and photos, or an address to work from.",
        ),
    ]
    faq_json = ",\n        ".join(
        '{ "@type": "Question", "name": %s, "acceptedAnswer": { "@type": "Answer", "text": %s } }'
        % (json.dumps(q), json.dumps(a))
        for q, a in faq_entries
    )
    faq_html = "".join(
        f"""
                <details class="faq">
                    <summary>{esc(q)}</summary>
                    <p>{esc(a)}</p>
                </details>"""
        for q, a in faq_entries
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <meta name="robots" content="index, follow">
    <meta name="theme-color" content="#0f3b24">
    <link rel="canonical" href="{url}">

    <!-- Open Graph -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{url}">
    <meta property="og:title" content="ADU Plans in {name}, MA | Sequoia Lodges">
    <meta property="og:description" content="{desc}">
    <meta property="og:image" content="{SITE}/logo.svg">
    <meta property="og:site_name" content="Sequoia Lodges">

    <link rel="icon" type="image/svg+xml" href="/logo.svg">
    <link rel="apple-touch-icon" href="/logo.svg">

    <!-- Service + area schema -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Service",
      "serviceType": "ADU design and structural engineering",
      "name": "Permit-Ready ADU Plans — {name}, MA",
      "url": "{url}",
      "provider": {{
        "@type": "LocalBusiness",
        "name": "Sequoia Lodges",
        "legalName": "Sequoia Lodges LLC",
        "url": "{SITE}",
        "email": "sequoialodges@gmail.com",
        "priceRange": "$$",
        "address": {{ "@type": "PostalAddress", "addressLocality": "Boston", "addressRegion": "MA", "addressCountry": "US" }}
      }},
      "areaServed": {{ "@type": "City", "name": "{name}", "address": {{ "@type": "PostalAddress", "addressRegion": "MA", "addressCountry": "US" }} }},
      "hasOfferCatalog": {{
        "@type": "OfferCatalog",
        "name": "ADU Plan Collections",
        "itemListElement": [
          {{ "@type": "Offer", "price": "3500", "priceCurrency": "USD", "itemOffered": {{ "@type": "Service", "name": "Studio ADU Plans" }} }},
          {{ "@type": "Offer", "price": "4000", "priceCurrency": "USD", "itemOffered": {{ "@type": "Service", "name": "1-Bedroom ADU Plans" }} }},
          {{ "@type": "Offer", "price": "4500", "priceCurrency": "USD", "itemOffered": {{ "@type": "Service", "name": "2-Bedroom ADU Plans" }} }}
        ]
      }}
    }}
    </script>

    <!-- FAQ Schema -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [
        {faq_json}
      ]
    }}
    </script>

{ANALYTICS}

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600;8..60,700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/feather-icons"></script>
{HEAD_STYLE}
</head>
<body class="antialiased">

{HEADER}

    <!-- Hero -->
    <section class="blueprint-grid border-t border-b" style="border-color: var(--line);">
        <div class="container mx-auto px-6 py-20 md:py-24">
            <div class="grid md:grid-cols-12 gap-12 items-center">
                <div class="md:col-span-7">
                    <span class="tag eyebrow mb-8">{esc(name)}, Massachusetts</span>
                    <h1 class="text-4xl md:text-5xl mb-6 mt-6 text-[var(--primary)]">ADU plans for {esc(name)},<br>stamped and ready to file.</h1>
                    <p class="text-lg text-[#3c463d] leading-relaxed max-w-2xl">{lede}</p>
                    <div class="flex flex-col sm:flex-row gap-4 mt-10">
                        <a href="#contact" class="btn btn-solid justify-center">Get a free eligibility read</a>
                        <a href="/Sequoia_Lodges_ADU_Sample_Plan.pdf" download target="_blank" rel="noopener" class="btn btn-outline justify-center">See a sample plan set</a>
                    </div>
                </div>
                <div class="md:col-span-5">
                    <table class="schedule w-full">
                        <thead>
                            <tr><th>Package</th><th>Size</th><th>Price</th></tr>
                        </thead>
                        <tbody>
                            <tr><td>Studio</td><td>400&ndash;550 sf</td><td class="num">$3,500</td></tr>
                            <tr><td>1-Bedroom</td><td>550&ndash;750 sf</td><td class="num">$4,000</td></tr>
                            <tr class="featured"><td>2-Bedroom</td><td>800&ndash;900 sf</td><td class="num">$4,500</td></tr>
                        </tbody>
                    </table>
                    <p class="text-sm text-[#56604f] mt-4">Flat fees. Attached ADUs add about $3,000 for the as-built of the existing house. Filing-ready in roughly two weeks.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Framework -->
    <section class="border-b" style="border-color: var(--line);">
        <div class="container mx-auto px-6 py-20">
            <div class="grid md:grid-cols-12 gap-12">
                <div class="md:col-span-5">
                    <span class="eyebrow text-[#56604f]">The Rules</span>
                    <h2 class="text-3xl md:text-4xl mt-3 text-[var(--primary)]">{framework_heading}</h2>
                    <p class="text-[#3c463d] leading-relaxed mt-6">{framework_intro}</p>
                </div>
                <div class="md:col-span-7">
                    <ul class="space-y-4 text-[#3c463d] leading-relaxed">
                        <li class="rule-item"><strong>Size.</strong> Up to 900 square feet, or 50% of the principal dwelling's gross floor area &mdash; whichever is smaller.</li>
                        <li class="rule-item"><strong>No owner-occupancy requirement.</strong> A town cannot make you live in either unit.</li>
                        <li class="rule-item"><strong>Parking is capped.</strong> At most one additional space, and none at all within a half mile of transit.</li>
                        <li class="rule-item"><strong>Separate utility connections can't be forced.</strong></li>
                        <li class="rule-item"><strong>But dimensional rules still apply.</strong> Setbacks, height, and lot coverage are unchanged, and towns may still require site plan review. &ldquo;By right&rdquo; means no variance &mdash; not no review.</li>
                        <li class="rule-item"><strong>And you still need the permits.</strong> Building permit, septic (Title 5) or sewer sign-off, and a certificate of occupancy.</li>
                        <li class="rule-item"><strong>Historic districts and short-term rentals</strong> are two places a town keeps real latitude to impose stricter rules.</li>
                    </ul>
                </div>
            </div>
        </div>
    </section>

    <!-- Local -->
    <section class="border-b" style="border-color: var(--line);">
        <div class="container mx-auto px-6 py-20">
            <span class="eyebrow text-[#56604f]">Locally</span>
            <h2 class="text-3xl md:text-4xl mt-3 mb-8 text-[var(--primary)]">Worth knowing about {esc(name)}</h2>
            <div class="grid md:grid-cols-12 gap-12">
                <div class="md:col-span-7">
                    <ul class="space-y-4 text-[#3c463d] leading-relaxed">{notes}
                    </ul>
                </div>
                <div class="md:col-span-5">
                    <div class="border p-7" style="border-color: var(--line);">
                        <div class="deliverable" style="border-top: none; padding-top: 0;">
                            <span class="eyebrow text-[#56604f]">Check with the town</span>
                            <p class="mt-2 text-[#3c463d] leading-relaxed">Local requirements change, and the town is the
                            authority on its own process.</p>
                            <a href="{town["official_url"]}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-2 mt-3 font-semibold text-[var(--primary)] hover:text-[var(--rust)]">
                                <i data-feather="external-link" class="w-4 h-4"></i> {esc(town["official_label"])}
                            </a>
                        </div>{energy}
                        <div class="deliverable">
                            <span class="eyebrow text-[#56604f]">Energy codes vary by town</span>
                            <p class="mt-2 text-[#3c463d] leading-relaxed">Whether a town runs the base code, the stretch
                            code, or the specialized opt-in code changes how an ADU has to be designed. The state
                            publishes the current adoption list by municipality.</p>
                            <a href="https://www.mass.gov/info-details/massachusetts-building-energy-code-adoption-by-municipality" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-2 mt-3 font-semibold text-[var(--primary)] hover:text-[var(--rust)]">
                                <i data-feather="external-link" class="w-4 h-4"></i> Energy code by municipality
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
{project}
    <!-- What you get -->
    <section class="border-b" style="border-color: var(--line);">
        <div class="container mx-auto px-6 py-20">
            <div class="grid md:grid-cols-12 gap-12">
                <div class="md:col-span-5">
                    <span class="eyebrow text-[#56604f]">The Deliverable</span>
                    <h2 class="text-3xl md:text-4xl mt-3 text-[var(--primary)]">A set your contractor can build from.</h2>
                    <p class="text-[#3c463d] leading-relaxed mt-6">We are a design and engineering firm. We don't build,
                    which means we have no incentive in who you hire &mdash; you take the drawings to your own contractor.
                    Plans are stamped by our principal engineer, Chris Kirby, PE.</p>
                </div>
                <div class="md:col-span-7 grid sm:grid-cols-2 gap-x-10">
                    <div>
                        <div class="deliverable"><span class="eyebrow text-[#56604f]">Included</span></div>
                        <div class="deliverable">General notes</div>
                        <div class="deliverable">Floor plans &amp; elevations</div>
                        <div class="deliverable">Foundation plan</div>
                        <div class="deliverable">Structural framing plans</div>
                        <div class="deliverable">Cross-sections &amp; details</div>
                        <div class="deliverable">PE stamp</div>
                    </div>
                    <div>
                        <div class="deliverable"><span class="eyebrow text-[#56604f]">Not included</span></div>
                        <div class="deliverable text-[#56604f]">MEP drawings &mdash; not required for residential permitting in MA</div>
                        <div class="deliverable text-[#56604f]">Survey / plot plan</div>
                        <div class="deliverable text-[#56604f]">Water &amp; sewer work</div>
                        <div class="deliverable text-[#56604f]">HERS rating</div>
                        <div class="deliverable text-[#56604f]">Construction</div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- FAQ -->
    <section class="border-b" style="border-color: var(--line);">
        <div class="container mx-auto px-6 py-20">
            <span class="eyebrow text-[#56604f]">Questions</span>
            <h2 class="text-3xl md:text-4xl mt-3 mb-8 text-[var(--primary)]">Straight answers</h2>
            <div class="max-w-3xl">{faq_html}
            </div>
        </div>
    </section>

    <!-- Contact -->
    <section id="contact" class="bg-[var(--primary)] text-[var(--paper)] py-20">
        <div class="container mx-auto px-6">
            <div class="grid md:grid-cols-2 gap-16">
                <div>
                    <span class="eyebrow" style="color:#cfd8cf;">{esc(name)} Inquiries</span>
                    <h2 class="text-3xl md:text-4xl mt-3 mb-6">Send us the address.</h2>
                    <p class="text-[#cfd8cf] mb-10 max-w-sm">Tell us the property and what you're trying to do. You'll get an
                    honest read on whether it fits, usually within one business day. If it doesn't work, we'll say so.</p>
                    <div class="space-y-5">
                        <a href="mailto:sequoialodges@gmail.com?subject=ADU%20inquiry%20%E2%80%94%20{quote(name)}" class="flex items-center gap-3 font-semibold hover:text-white">
                            <i data-feather="mail" class="w-4 h-4"></i> sequoialodges@gmail.com
                        </a>
                        <div class="flex items-center gap-3 font-semibold">
                            <i data-feather="map-pin" class="w-4 h-4"></i> Serving {esc(name)} &amp; Greater Boston
                        </div>
                    </div>
                </div>
                <form class="space-y-5" action="{FORM}" method="POST" data-lead-form="inquiry" data-variant="town-{slug}">
                    <input type="text" name="name" required placeholder="Name" class="field text-[var(--paper)]" style="border-bottom-color: rgba(250,246,236,0.35);">
                    <input type="email" name="email" required placeholder="Email" class="field text-[var(--paper)]" style="border-bottom-color: rgba(250,246,236,0.35);">
                    <input type="text" name="property_town" value="{esc(name)}" class="field text-[var(--paper)]" style="border-bottom-color: rgba(250,246,236,0.35);" placeholder="Property town">
                    <textarea name="message" rows="3" required placeholder="Property address and what you have in mind" class="field text-[var(--paper)]" style="border-bottom-color: rgba(250,246,236,0.35);"></textarea>
                    <input type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute; left:-9999px;">
                    <button type="submit" class="btn btn-cream w-full justify-center mt-2">Send</button>
                    <p data-form-error class="hidden text-sm" style="color:#f3c9a8;">Something went wrong sending your message. Please try again, or email us directly at sequoialodges@gmail.com.</p>
                    <input type="hidden" name="_subject" value="ADU inquiry &mdash; {esc(name)} (/adu-plans-{slug})">
                    <input type="hidden" name="_next" value="{SITE}/thank-you.html">
                </form>
            </div>
        </div>
    </section>

    <!-- Other towns -->
    <section class="border-t" style="border-color: var(--line);">
        <div class="container mx-auto px-6 py-14">
            <span class="eyebrow text-[#56604f]">Also serving</span>
            <div class="flex flex-wrap gap-x-8 gap-y-3 mt-4 text-[#3c463d]">
                {{OTHER_TOWNS}}
            </div>
            <p class="text-sm text-[#56604f] mt-6">Plans are deliverable anywhere in Massachusetts. These are the towns we work in most.</p>
        </div>
    </section>

    <!-- Disclaimer -->
    <section class="border-t" style="border-color: var(--line);">
        <div class="container mx-auto px-6 py-10">
            <p class="text-sm text-[#56604f] max-w-4xl">General information only, current as of August 2026. Regulations change and
            local requirements vary. Nothing here confirms that a particular property qualifies for an ADU, and nothing here is
            legal advice &mdash; eligibility is specific to your parcel and subject to municipal and code review. Sequoia Lodges LLC
            is a design and engineering firm; we are not a general contractor and we do not build.</p>
        </div>
    </section>

{FOOTER}
</body>
</html>
"""


# Pages excluded from the sitemap: gated download hubs and the post-submit page.
SITEMAP_EXCLUDE = {
    "kit-download-x7q4m.html",
    "guide-download-t9m2c.html",
    "thank-you.html",
}

# Crawl priority. Anything not listed defaults to 0.6.
SITEMAP_PRIORITY = {
    "index.html": "1.0",
    "adu-plans.html": "0.9",
    "permit-ready-adu-plans.html": "0.9",
    "adu-design-engineering.html": "0.8",
    "massachusetts-adu-guide.html": "0.8",
    "adu-cost-calculator.html": "0.8",
    "adu-planning-kit.html": "0.7",
    "privacy-policy.html": "0.2",
    "terms-of-service.html": "0.2",
}


def build_sitemap() -> int:
    """Emit sitemap.xml covering every indexable page currently in the repo."""
    today = datetime.date.today().isoformat()
    pages = sorted(p.name for p in ROOT.glob("*.html") if p.name not in SITEMAP_EXCLUDE)
    entries = []
    for name in pages:
        loc = SITE if name == "index.html" else f"{SITE}/{name}"
        priority = SITEMAP_PRIORITY.get(name, "0.6")
        entries.append(
            f"    <url>\n"
            f"        <loc>{loc}</loc>\n"
            f"        <lastmod>{today}</lastmod>\n"
            f"        <priority>{priority}</priority>\n"
            f"    </url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(xml)
    return len(pages)


def main() -> int:
    data = json.loads(DATA.read_text())
    towns = data["towns"]
    written = []
    for town in towns:
        others = " ".join(
            f'<a href="/adu-plans-{o["slug"]}.html" class="font-semibold hover:text-[var(--rust)]">{o["name"]}</a>'
            for o in towns
            if o["slug"] != town["slug"]
        )
        html = render(town).replace("{OTHER_TOWNS}", others)
        out = ROOT / f"adu-plans-{town['slug']}.html"
        out.write_text(html)
        written.append(out.name)
    print(f"Wrote {len(written)} town pages:")
    for name in written:
        print(f"  {name}")
    count = build_sitemap()
    print(f"Wrote sitemap.xml ({count} URLs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
