#!/usr/bin/env python3
"""
Craft Collective Salon Group - SEO Enhancement Generator
Generates: location landing pages, service pages, blog posts, enhanced sitemap
"""
import os
import json
from datetime import datetime

SITE_URL = "https://www.craftcollectivesalongroup.com"
PHONE = "724-514-7231"
PHONE_TEL = "+17245147231"
EMAIL = "info@craftcollectivesalongroup.com"
NH_ADDRESS = "2014D Babcock Blvd"
NH_CITY = "Pittsburgh"
NH_STATE = "PA"
NH_ZIP = "15209"
CB_ADDRESS = "115 W Pike St"
CB_CITY = "Canonsburg"
CB_STATE = "PA"
CB_ZIP = "15317"
NH_LAT = 40.5005
NH_LNG = -79.9959
CB_LAT = 40.2626
CB_LNG = -80.1870

# ============================================================
# SHARED STYLES & NAV & FOOTER
# ============================================================
SHARED_CSS = """
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root { --black: #0e0d0b; --off-white: #f7f4ef; --cream: #ede9e1; --gold: #b89a6a; --gold-light: #d4b98a; --mid: #6b6560; --rule: #d5cfc6; --text: #2a2724; }
    body { font-family: 'Jost', sans-serif; background: var(--off-white); color: var(--text); font-weight: 300; }
    .nav { position: fixed; top: 0; left: 0; right: 0; z-index: 100; background: rgba(14,13,11,0.96); backdrop-filter: blur(8px); border-bottom: 1px solid rgba(184,154,106,0.2); }
    .nav-inner { max-width: 1200px; margin: 0 auto; padding: 0 2rem; display: flex; align-items: center; justify-content: space-between; height: 68px; }
    .nav-logo { font-family: 'Cormorant Garamond', serif; font-size: 1.15rem; font-weight: 400; letter-spacing: 0.12em; color: var(--off-white); text-decoration: none; text-transform: uppercase; }
    .nav-logo span { color: var(--gold); }
    .nav-links { display: flex; gap: 2.2rem; list-style: none; }
    .nav-links a { color: rgba(247,244,239,0.7); text-decoration: none; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 400; transition: color 0.2s; }
    .nav-links a:hover { color: var(--gold-light); }
    .nav-book { background: var(--gold); color: var(--black) !important; padding: 0.5rem 1.2rem; font-weight: 500 !important; }
    .hero-page { padding: 10rem 2rem 5rem; background: var(--black); text-align: center; }
    .hero-page h1 { font-family: 'Cormorant Garamond', serif; font-size: clamp(2.5rem, 5vw, 4.5rem); font-weight: 300; color: var(--off-white); line-height: 1.1; margin-bottom: 1rem; }
    .hero-page h1 em { font-style: italic; color: var(--gold); }
    .hero-page .subtitle { font-size: 1rem; color: rgba(247,244,239,0.5); max-width: 600px; margin: 0 auto 2rem; line-height: 1.7; }
    .breadcrumb-bar { font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; color: rgba(247,244,239,0.35); margin-bottom: 2rem; }
    .breadcrumb-bar a { color: var(--gold); text-decoration: none; }
    .breadcrumb-bar span { margin: 0 0.5rem; }
    .content-section { padding: 5rem 2rem; }
    .content-section.alt { background: var(--cream); }
    .content-inner { max-width: 900px; margin: 0 auto; }
    .section-label { font-size: 0.65rem; letter-spacing: 0.25em; text-transform: uppercase; color: var(--gold); font-weight: 400; margin-bottom: 1rem; }
    .section-headline { font-family: 'Cormorant Garamond', serif; font-size: clamp(2rem, 3vw, 3rem); font-weight: 300; color: var(--text); margin-bottom: 2rem; line-height: 1.2; }
    .section-headline em { font-style: italic; color: var(--gold); }
    .prose { font-size: 0.9rem; line-height: 1.95; color: var(--mid); font-weight: 300; }
    .prose p { margin-bottom: 1.4rem; }
    .prose h2 { font-family: 'Cormorant Garamond', serif; font-size: 1.8rem; font-weight: 300; color: var(--text); margin: 2.5rem 0 1rem; }
    .prose h3 { font-family: 'Cormorant Garamond', serif; font-size: 1.3rem; font-weight: 400; color: var(--text); margin: 2rem 0 0.8rem; }
    .prose ul, .prose ol { margin: 1rem 0 1.4rem 1.5rem; }
    .prose li { margin-bottom: 0.5rem; }
    .prose a { color: var(--gold); text-decoration: underline; }
    .btn-primary { display: inline-block; background: var(--gold); color: var(--black); padding: 0.9rem 2.2rem; text-decoration: none; font-size: 0.75rem; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 500; transition: background 0.2s; }
    .btn-primary:hover { background: var(--gold-light); }
    .book-cta { background: var(--gold); padding: 4rem 2rem; text-align: center; }
    .book-cta h2 { font-family: 'Cormorant Garamond', serif; font-size: 2.5rem; font-weight: 300; color: var(--black); margin-bottom: 0.8rem; }
    .book-cta p { font-size: 0.875rem; color: rgba(14,13,11,0.6); margin-bottom: 2rem; }
    .btn-dark { display: inline-block; background: var(--black); color: var(--off-white); padding: 0.9rem 2.5rem; text-decoration: none; font-size: 0.75rem; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 500; }
    .service-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 2rem; margin-top: 2rem; }
    .service-card { background: white; padding: 2rem; border: 1px solid var(--rule); }
    .service-card h3 { font-family: 'Cormorant Garamond', serif; font-size: 1.3rem; font-weight: 400; color: var(--text); margin-bottom: 0.8rem; }
    .service-card p { font-size: 0.85rem; line-height: 1.7; color: var(--mid); }
    .service-card a { display: inline-block; margin-top: 1rem; color: var(--gold); font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; text-decoration: none; font-weight: 500; }
    .nap-box { background: white; border: 1px solid var(--rule); padding: 2.5rem; margin-top: 2rem; }
    .nap-box h3 { font-family: 'Cormorant Garamond', serif; font-size: 1.4rem; font-weight: 400; margin-bottom: 1rem; }
    .nap-box p { font-size: 0.9rem; line-height: 1.8; color: var(--mid); }
    .nap-box a { color: var(--gold); text-decoration: none; }
    footer { background: var(--black); border-top: 2px solid rgba(184,154,106,0.4); padding: 4rem 2rem; }
    .footer-inner { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 3rem; }
    .footer-brand-name { font-family: 'Cormorant Garamond', serif; font-size: 1.2rem; font-weight: 400; letter-spacing: 0.1em; text-transform: uppercase; color: var(--off-white); margin-bottom: 0.8rem; }
    .footer-tagline { font-size: 0.75rem; color: rgba(247,244,239,0.4); font-style: italic; font-family: 'Cormorant Garamond', serif; margin-bottom: 1.5rem; }
    .footer-contact { font-size: 0.78rem; color: rgba(247,244,239,0.5); line-height: 2; font-weight: 300; }
    .footer-contact a { color: var(--gold); text-decoration: none; }
    .footer-col-head { font-size: 0.65rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--gold); margin-bottom: 1.2rem; font-weight: 400; }
    .footer-links { list-style: none; }
    .footer-links li { margin-bottom: 0.6rem; }
    .footer-links a { font-size: 0.78rem; color: rgba(247,244,239,0.5); text-decoration: none; font-weight: 300; transition: color 0.2s; }
    .footer-links a:hover { color: var(--gold-light); }
    .footer-bottom { max-width: 1200px; margin: 3rem auto 0; padding-top: 2rem; border-top: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-between; }
    .footer-copy { font-size: 0.7rem; color: rgba(247,244,239,0.25); font-weight: 300; }
    @media (max-width: 900px) {
      .hero-page { padding: 7rem 1.5rem 3rem; }
      .content-section { padding: 3rem 1.5rem; }
      .nav-links { display: none; }
      .footer-inner { grid-template-columns: 1fr 1fr; }
      .service-grid { grid-template-columns: 1fr; }
    }
"""

NAV_HTML = """
  <nav class="nav" aria-label="Main navigation">
    <div class="nav-inner">
      <a href="/" class="nav-logo">Craft <span>Collective</span></a>
      <ul class="nav-links">
        <li><a href="/hair-services-pittsburgh">Services</a></li>
        <li><a href="/hair-salon-gallery-pittsburgh">Gallery</a></li>
        <li><a href="/derek-piekarski">Meet Derek</a></li>
        <li><a href="/meet-the-team">Team</a></li>
        <li><a href="/reviews">Reviews</a></li>
        <li><a href="/blog">Blog</a></li>
        <li><a href="/locations/north-hills-pittsburgh">Locations</a></li>
        <li><a href="/book" class="nav-book">Book Now</a></li>
      </ul>
    </div>
  </nav>
"""

FOOTER_HTML = """
  <footer>
    <div class="footer-inner">
      <div>
        <p class="footer-brand-name">Craft Collective Salon Group</p>
        <p class="footer-tagline">Pittsburgh's Premier Hair Salon</p>
        <div class="footer-contact">
          <a href="tel:+17245147231">724-514-7231</a><br>
          <a href="mailto:info@craftcollectivesalongroup.com">info@craftcollectivesalongroup.com</a><br><br>
          2014D Babcock Blvd, Pittsburgh PA 15209<br>
          115 W Pike St, Canonsburg PA 15317
        </div>
      </div>
      <div>
        <p class="footer-col-head">Services</p>
        <ul class="footer-links">
          <li><a href="/services/balayage-pittsburgh">Balayage</a></li>
          <li><a href="/services/highlights-pittsburgh">Highlights</a></li>
          <li><a href="/services/hair-color-pittsburgh">Hair Color</a></li>
          <li><a href="/services/keratin-treatment-pittsburgh">Keratin</a></li>
          <li><a href="/services/hair-extensions-pittsburgh">Extensions</a></li>
          <li><a href="/services/haircuts-pittsburgh">Haircuts</a></li>
        </ul>
      </div>
      <div>
        <p class="footer-col-head">Salon</p>
        <ul class="footer-links">
          <li><a href="/reviews">Reviews</a></li>
          <li><a href="/blog">Blog</a></li>
          <li><a href="/faq">FAQ</a></li>
          <li><a href="/hair-services-pittsburgh">All Services</a></li>
        </ul>
      </div>
      <div>
        <p class="footer-col-head">Locations</p>
        <ul class="footer-links">
          <li><a href="/book">Book Online</a></li>
          <li><a href="/locations/north-hills-pittsburgh">North Hills</a></li>
          <li><a href="/locations/canonsburg">Canonsburg</a></li>
          <li><a href="https://www.instagram.com/craftcollectivesalongroup/" target="_blank" rel="noopener">Instagram</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p class="footer-copy">&copy; 2026 Craft Collective Salon Group. All rights reserved.</p>
    </div>
  </footer>
"""

def make_page(title, description, canonical, og_type, breadcrumbs, schema_json, body_html, extra_head=""):
    bc_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": []
    }
    for i, (name, url) in enumerate(breadcrumbs):
        item = {"@type": "ListItem", "position": i+1, "name": name}
        if url:
            item["item"] = url
        bc_schema["itemListElement"].append(item)
    
    schemas = [bc_schema] + (schema_json if isinstance(schema_json, list) else [schema_json])
    schema_tags = "\n".join([f'  <script type="application/ld+json">\n  {json.dumps(s, indent=2)}\n  </script>' for s in schemas if s])
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{canonical}" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:type" content="{og_type}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:image" content="https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1200&q=85" />
  <meta property="og:locale" content="en_US" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{description}" />
  <meta name="twitter:image" content="https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1200&q=85" />
{schema_tags}
{extra_head}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Jost:wght@300;400;500;600&display=swap" rel="stylesheet" />
  <style>{SHARED_CSS}</style>
</head>
<body>
{NAV_HTML}
{body_html}
{FOOTER_HTML}
</body>
</html>"""

def write_page(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"  Created: {path}")

# ============================================================
# 1. LOCATION LANDING PAGES
# ============================================================
LOCATIONS = [
    {"slug": "shadyside", "name": "Shadyside", "dist": "15 minutes", "lat": 40.4528, "lng": -79.9331,
     "desc": "Shadyside residents looking for the best hair salon trust Craft Collective Salon Group. Just a short drive from Walnut Street, our North Hills studio offers balayage, highlights, blonding, keratin treatments, hair extensions, and precision cuts by Pittsburgh's most awarded stylists."},
    {"slug": "lawrenceville", "name": "Lawrenceville", "dist": "12 minutes", "lat": 40.4674, "lng": -79.9606,
     "desc": "From Butler Street lofts to the galleries on Penn Avenue, Lawrenceville creatives choose Craft Collective for color that matches their energy. Our team specializes in lived-in color, dimensional highlights, and bold transformations."},
    {"slug": "squirrel-hill", "name": "Squirrel Hill", "dist": "20 minutes", "lat": 40.4382, "lng": -79.9227,
     "desc": "Squirrel Hill clients love the attention to detail at Craft Collective. Whether you need a root touch-up, full balayage, or a fresh cut before a Carnegie Mellon event, our stylists deliver consistent, beautiful results."},
    {"slug": "mt-lebanon", "name": "Mt. Lebanon", "dist": "25 minutes", "lat": 40.3786, "lng": -80.0482,
     "desc": "Mt. Lebanon families and professionals trust Craft Collective for everything from kids' haircuts to full color transformations. Both our North Hills and Canonsburg locations are a convenient drive from the Lebo area."},
    {"slug": "cranberry-township", "name": "Cranberry Township", "dist": "20 minutes", "lat": 40.6863, "lng": -80.1068,
     "desc": "Cranberry Township residents enjoy easy access to Craft Collective's North Hills studio on Babcock Blvd. Skip the big-box salons and experience Pittsburgh's premier colorists and cutters just minutes from Route 19."},
    {"slug": "wexford", "name": "Wexford", "dist": "15 minutes", "lat": 40.6268, "lng": -80.0587,
     "desc": "Wexford clients are some of our most loyal guests. Just a quick drive down Route 19 to Babcock Blvd, our salon offers the premium color and cutting experience that Wexford residents expect."},
    {"slug": "mccandless", "name": "McCandless", "dist": "5 minutes", "lat": 40.5355, "lng": -80.0273,
     "desc": "As your neighborhood salon, Craft Collective is right here in McCandless on Babcock Blvd. Walk-ins welcome for cuts; color appointments recommended. We are the go-to salon for McCandless residents who want expert-level hair care."},
    {"slug": "ross-township", "name": "Ross Township", "dist": "5 minutes", "lat": 40.5250, "lng": -80.0150,
     "desc": "Ross Township residents love being minutes from Pittsburgh's top-rated hair salon. Craft Collective on Babcock Blvd is your local destination for balayage, highlights, extensions, and keratin treatments."},
    {"slug": "south-hills", "name": "South Hills", "dist": "30 minutes", "lat": 40.3700, "lng": -80.0200,
     "desc": "South Hills clients can visit either our Canonsburg studio at 115 W Pike St or make the trip to our flagship North Hills location. Both studios offer the same award-winning color, cuts, and treatments."},
    {"slug": "washington-pa", "name": "Washington, PA", "dist": "15 minutes from Canonsburg", "lat": 40.1740, "lng": -80.2462,
     "desc": "Washington, PA residents are just minutes from our Canonsburg location at 115 W Pike St. Get the same world-class balayage, highlights, and color services that made us Pittsburgh's top-rated salon."},
    {"slug": "upper-st-clair", "name": "Upper St. Clair", "dist": "25 minutes", "lat": 40.3340, "lng": -80.0830,
     "desc": "Upper St. Clair residents choose Craft Collective for occasions that matter -- wedding styling, prom updos, and the kind of everyday color that turns heads at the Galleria. Our Canonsburg studio is your closest option."},
    {"slug": "bethel-park", "name": "Bethel Park", "dist": "25 minutes", "lat": 40.3276, "lng": -80.0395,
     "desc": "Bethel Park clients drive to Craft Collective because no chain salon can match our colorists. Whether it is corrective color, extensions, or a simple blowout, our team delivers salon-quality results worth the trip."},
    {"slug": "sewickley", "name": "Sewickley", "dist": "20 minutes", "lat": 40.5366, "lng": -80.1847,
     "desc": "Sewickley's discerning clients appreciate the craft behind every appointment at Craft Collective. Our stylists bring Wella-trained precision to balayage, blonding, and dimensional color that looks natural in any light."},
    {"slug": "fox-chapel", "name": "Fox Chapel", "dist": "15 minutes", "lat": 40.5160, "lng": -79.8940,
     "desc": "Fox Chapel residents trust Craft Collective for refined, low-maintenance color and cuts. Our North Hills location on Babcock Blvd is a quick drive, and our attention to detail matches the standard Fox Chapel clients expect."},
    {"slug": "strip-district", "name": "Strip District", "dist": "15 minutes", "lat": 40.4530, "lng": -79.9780,
     "desc": "Strip District professionals and artists choose Craft Collective for bold color transformations and precision cuts. Our North Hills studio is an easy drive from Penn Avenue, and online booking is available 24/7."},
    {"slug": "oakland", "name": "Oakland", "dist": "18 minutes", "lat": 40.4417, "lng": -79.9560,
     "desc": "University of Pittsburgh and CMU students and faculty trust Craft Collective for everything from first-day-of-semester cuts to graduation balayage. Affordable student-friendly options available with select stylists."},
    {"slug": "robinson-township", "name": "Robinson Township", "dist": "25 minutes", "lat": 40.4553, "lng": -80.1620,
     "desc": "Robinson Township shoppers can skip the mall salon and drive to Craft Collective for real results. Our award-winning colorists specialize in balayage, blonding, and dimensional color that lasts."},
    {"slug": "mcmurray", "name": "McMurray", "dist": "20 minutes from Canonsburg", "lat": 40.2780, "lng": -80.0930,
     "desc": "McMurray residents are just minutes from our Canonsburg location. Craft Collective offers the same premium services at both studios -- balayage, highlights, extensions, keratin, and precision cuts."},
]

SERVICES_LIST = [
    "balayage", "highlights", "blonding", "hair color", "keratin treatments",
    "hair extensions", "precision haircuts", "lived-in color", "corrective color",
    "bridal and wedding hair", "men's haircuts", "blowouts"
]

def gen_location_pages():
    print("\n=== Generating Location Landing Pages ===")
    for loc in LOCATIONS:
        slug = loc["slug"]
        name = loc["name"]
        dist = loc["dist"]
        lat = loc["lat"]
        lng = loc["lng"]
        desc_text = loc["desc"]
        
        title = f"Best Hair Salon Near {name} PA | Craft Collective Salon Group"
        meta_desc = f"Looking for the best hair salon near {name}, PA? Craft Collective Salon Group is just {dist} away. Balayage, highlights, extensions, keratin, and cuts. Book online or call {PHONE}."
        canonical = f"{SITE_URL}/locations/{slug}"
        
        services_html = ""
        for svc in ["Balayage", "Highlights & Lowlights", "Blonding", "Hair Color", "Keratin Treatment", "Hair Extensions", "Precision Haircuts", "Bridal & Wedding Hair"]:
            svc_slug = svc.lower().replace(" & ", "-").replace(" ", "-")
            services_html += f"""
            <div class="service-card">
              <h3>{svc}</h3>
              <p>{svc} services available for {name} clients at Craft Collective Salon Group. Expert stylists with years of experience.</p>
              <a href="/hair-services-pittsburgh">Learn More &rarr;</a>
            </div>"""
        
        schema = {
            "@context": "https://schema.org",
            "@type": "HairSalon",
            "name": f"Craft Collective Salon Group - Near {name}",
            "url": canonical,
            "telephone": PHONE_TEL,
            "email": EMAIL,
            "priceRange": "$$",
            "description": f"Pittsburgh's premier hair salon serving {name}, PA. Balayage, highlights, blonding, keratin, extensions, and precision cuts.",
            "address": {"@type": "PostalAddress", "streetAddress": NH_ADDRESS, "addressLocality": NH_CITY, "addressRegion": NH_STATE, "postalCode": NH_ZIP, "addressCountry": "US"},
            "geo": {"@type": "GeoCoordinates", "latitude": NH_LAT, "longitude": NH_LNG},
            "hasMap": f"https://maps.google.com/?q={NH_ADDRESS.replace(' ','+')}+{NH_CITY}+{NH_STATE}+{NH_ZIP}",
            "openingHoursSpecification": [
                {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Tuesday","Wednesday","Thursday","Friday"], "opens": "09:00", "closes": "19:00"},
                {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "09:00", "closes": "17:00"}
            ],
            "areaServed": [name, "Pittsburgh", "North Hills"],
            "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.9", "bestRating": "5", "worstRating": "1", "ratingCount": "247", "reviewCount": "247"}
        }
        
        faq_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": f"How far is Craft Collective from {name}?",
                 "acceptedAnswer": {"@type": "Answer", "text": f"Craft Collective Salon Group's North Hills location at {NH_ADDRESS}, Pittsburgh PA {NH_ZIP} is approximately {dist} from {name}. Our Canonsburg location at {CB_ADDRESS}, Canonsburg PA {CB_ZIP} may also be convenient."}},
                {"@type": "Question", "name": f"What hair services are available for {name} residents?",
                 "acceptedAnswer": {"@type": "Answer", "text": f"We offer a full menu of services for {name} clients including balayage, highlights, blonding, full color, hair extensions, keratin smoothing treatments, precision haircuts, corrective color, and bridal styling. Book online or call {PHONE}."}},
                {"@type": "Question", "name": f"Do I need an appointment at Craft Collective?",
                 "acceptedAnswer": {"@type": "Answer", "text": f"Appointments are recommended for color services. Walk-ins are accepted for haircuts when stylists are available. Book online 24/7 at our website or call {PHONE}."}}
            ]
        }
        
        body = f"""
  <section class="hero-page">
    <p class="breadcrumb-bar"><a href="/">Home</a><span>/</span><a href="/locations/north-hills-pittsburgh">Locations</a><span>/</span>{name}</p>
    <h1>Best Hair Salon<br>Near <em>{name}</em></h1>
    <p class="subtitle">{desc_text}</p>
    <a href="/book" class="btn-primary">Book Your Appointment</a>
  </section>

  <section class="content-section alt">
    <div class="content-inner">
      <p class="section-label">Services for {name} Clients</p>
      <h2 class="section-headline">Full-service salon <em>minutes away</em></h2>
      <div class="service-grid">{services_html}
      </div>
    </div>
  </section>

  <section class="content-section">
    <div class="content-inner">
      <p class="section-label">Visit Us</p>
      <h2 class="section-headline">Just <em>{dist}</em> from {name}</h2>
      <div class="prose">
        <p>Craft Collective Salon Group has two locations serving the greater Pittsburgh area. Our flagship studio is at <strong>{NH_ADDRESS}, Pittsburgh PA {NH_ZIP}</strong> in the North Hills, and our second studio is at <strong>{CB_ADDRESS}, Canonsburg PA {CB_ZIP}</strong>.</p>
        <p>Both locations are led by owner and globally recognized stylist Derek Piekarski, a former Wella Professionals Signature Artist and Aveda/Estee Lauder Technical Capabilities Manager. Our team of 39 stylists specializes in balayage, highlights, blonding, dimensional color, keratin treatments, hair extensions, and precision cuts.</p>
      </div>
      <div class="nap-box">
        <h3>Craft Collective Salon Group</h3>
        <p>
          <strong>North Hills:</strong> {NH_ADDRESS}, Pittsburgh PA {NH_ZIP}<br>
          <strong>Canonsburg:</strong> {CB_ADDRESS}, Canonsburg PA {CB_ZIP}<br>
          <strong>Phone:</strong> <a href="tel:{PHONE_TEL}">{PHONE}</a><br>
          <strong>Email:</strong> <a href="mailto:{EMAIL}">{EMAIL}</a><br>
          <strong>Hours:</strong> Tue-Fri 9am-7pm, Sat 9am-5pm<br>
          <strong>Booking:</strong> <a href="/book">Book Online 24/7</a>
        </p>
      </div>
    </div>
  </section>

  <section class="content-section alt">
    <div class="content-inner">
      <p class="section-label">Why {name} Clients Choose Us</p>
      <h2 class="section-headline">Pittsburgh's <em>top-rated</em> salon</h2>
      <div class="prose">
        <p>With a 4.9-star rating from over 247 reviews, Craft Collective is consistently ranked as one of the best hair salons in the Pittsburgh area. {name} residents choose us for our expert colorists, welcoming atmosphere, and the kind of personalized service you will not find at a chain salon.</p>
        <p>Our team includes specialists in balayage and dimensional color, extension experts certified in hand-tied and tape-in methods, keratin smoothing treatment pros, and stylists who specialize in men's grooming, bridal styling, and corrective color work.</p>
        <p><a href="/meet-the-team">Meet our full team of stylists</a> or <a href="/reviews">read what our clients say about us</a>.</p>
      </div>
    </div>
  </section>

  <div class="book-cta">
    <h2>Ready to Book?</h2>
    <p>{name} residents can book online 24/7 or call {PHONE}.</p>
    <a href="/book" class="btn-dark">Book an Appointment</a>
  </div>
"""
        breadcrumbs = [("Home", SITE_URL), ("Locations", f"{SITE_URL}/locations/north-hills-pittsburgh"), (name, None)]
        page = make_page(title, meta_desc, canonical, "website", breadcrumbs, [schema, faq_schema], body)
        write_page(f"locations/{slug}/index.html", page)


# ============================================================
# 2. INDIVIDUAL SERVICE PAGES
# ============================================================
SERVICES = [
    {
        "slug": "balayage-pittsburgh",
        "name": "Balayage",
        "h1": "Balayage",
        "title": "Best Balayage in Pittsburgh PA | Craft Collective Salon Group",
        "meta": "Looking for the best balayage in Pittsburgh? Craft Collective Salon Group's expert colorists create natural, sun-kissed dimension with freehand painting techniques. Book online.",
        "content": """
        <p>Balayage is a freehand hair painting technique that creates soft, natural-looking dimension without harsh lines. At Craft Collective Salon Group, our colorists are trained in the latest balayage methods to deliver sun-kissed, lived-in color that grows out beautifully.</p>
        <h3>What Makes Our Balayage Different</h3>
        <p>Our team, led by globally recognized Wella Professionals artist Derek Piekarski, approaches every balayage appointment as a custom consultation. We assess your natural base, skin tone, lifestyle, and maintenance preferences before placing a single stroke. The result is color that looks like it belongs to you.</p>
        <h3>Balayage vs. Traditional Highlights</h3>
        <p>While traditional foil highlights create uniform brightness from root to tip, balayage uses a sweeping, hand-painted technique that concentrates color on the mid-lengths and ends. This creates softer grow-out, less visible regrowth lines, and a more natural finished look. Many clients find they can go 12 to 16 weeks between balayage appointments.</p>
        <h3>What to Expect</h3>
        <p>A balayage appointment at Craft Collective typically takes 2.5 to 4 hours depending on hair length, density, and the desired level of lightening. Every service includes a custom toner to perfect your shade, a deep conditioning treatment, and a blowout finish.</p>
        <p>Book your balayage consultation online or call us at <a href="tel:+17245147231">724-514-7231</a>.</p>
        """
    },
    {
        "slug": "highlights-pittsburgh",
        "name": "Highlights & Lowlights",
        "h1": "Highlights & Lowlights",
        "title": "Highlights Pittsburgh PA | Foils, Partial & Full | Craft Collective Salon",
        "meta": "Expert highlight services in Pittsburgh. Partial highlights, full highlights, lowlights, and dimensional color at Craft Collective Salon Group. Book your appointment.",
        "content": """
        <p>Highlights remain one of the most requested services at Craft Collective Salon Group. Our colorists use precision foil placement to create bright, dimensional color that enhances your natural beauty.</p>
        <h3>Types of Highlights We Offer</h3>
        <p><strong>Partial highlights</strong> focus on the face-framing sections and crown for a natural brightening effect. <strong>Full highlights</strong> cover the entire head for maximum dimension and lift. <strong>Lowlights</strong> add depth and richness, perfect for blondes who want more contrast or brunettes who want warmth without going lighter.</p>
        <h3>Our Approach</h3>
        <p>Every highlight appointment starts with a consultation. Your stylist will assess your current color, discuss your goals, and recommend the best placement strategy. We use Wella Professionals lighteners and toners exclusively, ensuring consistent, healthy results.</p>
        <p>Appointment times range from 2 to 3.5 hours. Book online or call <a href="tel:+17245147231">724-514-7231</a>.</p>
        """
    },
    {
        "slug": "hair-color-pittsburgh",
        "name": "Hair Color",
        "h1": "Hair Color Services",
        "title": "Hair Color Pittsburgh PA | Full Color, Gloss & Toner | Craft Collective",
        "meta": "Professional hair color services in Pittsburgh. Full color, root touch-ups, glossing, toning, and color corrections at Craft Collective Salon Group. Book now.",
        "content": """
        <p>From single-process color to full transformations, Craft Collective Salon Group offers the complete spectrum of professional hair color services. Our colorists work with Wella Professionals formulas to achieve rich, lasting color that protects hair integrity.</p>
        <h3>Our Color Services</h3>
        <p><strong>Full color</strong> provides all-over coverage and can take you darker, warmer, cooler, or brighter. <strong>Root touch-ups</strong> maintain your existing color with seamless blending. <strong>Glossing and toning</strong> refresh your shade between full color appointments, adding shine and neutralizing unwanted warmth or brassiness.</p>
        <h3>Corrective Color</h3>
        <p>If a previous color service did not go as planned, our corrective color specialists can help. Whether you are dealing with banding, uneven tone, over-processed ends, or a shade that simply is not right, we will create a custom correction plan to get you where you want to be.</p>
        <p>Call <a href="tel:+17245147231">724-514-7231</a> or <a href="/book">book a color consultation online</a>.</p>
        """
    },
    {
        "slug": "keratin-treatment-pittsburgh",
        "name": "Keratin Smoothing Treatment",
        "h1": "Keratin Smoothing Treatments",
        "title": "Keratin Treatment Pittsburgh PA | Frizz-Free Hair | Craft Collective Salon",
        "meta": "Keratin smoothing treatments in Pittsburgh at Craft Collective Salon Group. Eliminate frizz, reduce styling time, and enjoy smooth, shiny hair for months. Book now.",
        "content": """
        <p>Pittsburgh humidity is no match for a professional keratin smoothing treatment at Craft Collective. Our keratin services reduce frizz, improve manageability, and add lasting shine for softer, faster-drying hair that behaves in any weather.</p>
        <h3>How Keratin Works</h3>
        <p>A keratin treatment infuses the hair shaft with a protein solution that fills gaps in the cuticle, smoothing the surface and creating a protective barrier against humidity. The result is smoother texture, dramatically reduced frizz, and styling time cut by up to 50%.</p>
        <h3>How Long Does It Last?</h3>
        <p>Most clients enjoy smooth, frizz-free results for 3 to 5 months depending on hair type, washing frequency, and product use. We recommend sulfate-free shampoo and conditioner to extend the life of your treatment.</p>
        <p>Appointments typically take 2 to 3 hours. <a href="/book">Book your keratin treatment online</a> or call <a href="tel:+17245147231">724-514-7231</a>.</p>
        """
    },
    {
        "slug": "hair-extensions-pittsburgh",
        "name": "Hair Extensions",
        "h1": "Hair Extensions",
        "title": "Hair Extensions Pittsburgh PA | Hand-Tied & Tape-In | Craft Collective Salon",
        "meta": "Premium hair extensions in Pittsburgh. Hand-tied, tape-in, and keratin bond methods at Craft Collective Salon Group. Free consultation. Call 724-514-7231.",
        "content": """
        <p>Craft Collective Salon Group offers multiple extension methods customized to your goals, hair density, and maintenance preferences. Whether you want added length, volume, or both, our extension specialists will design a plan that looks and feels completely natural.</p>
        <h3>Extension Methods</h3>
        <p><strong>Hand-tied extensions</strong> use a beaded row foundation for a flat, comfortable fit that distributes weight evenly. <strong>Tape-in extensions</strong> are lightweight, quick to apply, and ideal for fine to medium hair. <strong>Keratin bond extensions</strong> offer strand-by-strand customization for the most natural movement.</p>
        <h3>Consultation Required</h3>
        <p>Every extension client starts with a free consultation where we assess your hair health, discuss your goals, and recommend the best method. We will also custom-color match your extensions so the blend is seamless.</p>
        <p>Call <a href="tel:+17245147231">724-514-7231</a> to schedule your free extension consultation.</p>
        """
    },
    {
        "slug": "haircuts-pittsburgh",
        "name": "Haircuts",
        "h1": "Haircuts for Women, Men & Kids",
        "title": "Haircuts Pittsburgh PA | Women, Men & Kids | Craft Collective Salon",
        "meta": "Expert haircuts in Pittsburgh for women, men, and children. Precision cuts tailored to your face shape and lifestyle at Craft Collective Salon Group. Book online.",
        "content": """
        <p>Every haircut at Craft Collective starts with a conversation. Your stylist will assess your face shape, hair texture, growth patterns, and daily styling routine before making a single cut. The result is a shape that works with your hair, not against it.</p>
        <h3>Women's Haircuts</h3>
        <p>From bobs and lobs to long layers and textured shags, our stylists are skilled in every modern cutting technique. Every women's cut includes a shampoo, consultation, precision cut, and blowout finish.</p>
        <h3>Men's Haircuts</h3>
        <p>Our men's cuts are tailored to the same high standard as our women's services. Fades, tapers, textured crops, and classic styles -- all finished with detail work and styling guidance.</p>
        <h3>Kids' Haircuts</h3>
        <p>We welcome kids of all ages. Our stylists make the experience comfortable and fun, whether it is a first haircut or a regular trim.</p>
        <p><a href="/book">Book your haircut online</a> or call <a href="tel:+17245147231">724-514-7231</a>.</p>
        """
    },
    {
        "slug": "bridal-hair-pittsburgh",
        "name": "Bridal & Wedding Hair",
        "h1": "Bridal & Wedding Hair Styling",
        "title": "Wedding Hair Pittsburgh PA | Bridal Styling & Updos | Craft Collective Salon",
        "meta": "Wedding and bridal hair styling in Pittsburgh. Updos, half-up styles, braids, and soft glam at Craft Collective Salon Group. Trials available. Book now.",
        "content": """
        <p>Your wedding day hair should be as effortless as it is beautiful. Craft Collective Salon Group's bridal specialists create updos, half-up looks, braids, and soft glam styles that photograph beautifully and last through every dance, toast, and hug.</p>
        <h3>Our Bridal Process</h3>
        <p>We recommend scheduling a trial appointment 4 to 6 weeks before your wedding. During the trial, your stylist will work with you to find the perfect style that complements your dress, venue, and vision. On the day of, your stylist can come to you or you can visit the salon.</p>
        <h3>Bridal Party Services</h3>
        <p>We offer group bookings for bridal parties of any size. Bridesmaids, mothers of the bride, flower girls -- everyone gets the Craft Collective treatment.</p>
        <p>Contact us at <a href="tel:+17245147231">724-514-7231</a> or <a href="mailto:info@craftcollectivesalongroup.com">info@craftcollectivesalongroup.com</a> to discuss your wedding.</p>
        """
    },
    {
        "slug": "mens-grooming-pittsburgh",
        "name": "Men's Grooming",
        "h1": "Men's Grooming & Haircuts",
        "title": "Men's Haircuts Pittsburgh PA | Fades, Tapers & Grooming | Craft Collective",
        "meta": "Premium men's haircuts and grooming in Pittsburgh. Fades, tapers, textured styles, and beard trims at Craft Collective Salon Group. Book your appointment.",
        "content": """
        <p>Craft Collective is not just for women. Our male clients enjoy the same level of precision, attention, and expertise that has made us Pittsburgh's top-rated salon. From classic cuts to modern fades, our stylists understand men's hair.</p>
        <h3>Men's Services</h3>
        <p>We offer precision haircuts, fades, tapers, textured crops, longer styles, and beard shaping. Every men's service includes a consultation, shampoo, cut, and styling finish with product recommendations tailored to your hair type.</p>
        <h3>Why Choose a Salon Over a Barbershop?</h3>
        <p>Our stylists are trained in both barbering techniques and salon-level finishing. You get the precision of a barber with the refinement and product knowledge of a full-service salon. Plus, our team can handle color services for men -- gray blending, highlights, and fashion color.</p>
        <p><a href="/book">Book your men's cut online</a> or call <a href="tel:+17245147231">724-514-7231</a>.</p>
        """
    },
    {
        "slug": "blowout-pittsburgh",
        "name": "Blowout & Styling",
        "h1": "Professional Blowouts",
        "title": "Blowout Pittsburgh PA | Professional Blowout Bar | Craft Collective Salon",
        "meta": "Professional blowouts and styling in Pittsburgh. Get salon-perfect hair for any occasion at Craft Collective Salon Group. Walk-ins welcome. Book now.",
        "content": """
        <p>Sometimes you just need your hair to look incredible. Our professional blowout service gives you smooth, voluminous, camera-ready hair in about 45 minutes. Perfect before a date, event, interview, or just because.</p>
        <h3>What is Included</h3>
        <p>Every blowout includes a shampoo with professional products, a customized blow-dry using round brushes and the right heat tools for your hair type, and a finishing spray for hold and shine. We can do sleek and straight, bouncy and voluminous, or textured waves.</p>
        <p>Walk-ins welcome when stylists are available, or <a href="/book">book your blowout online</a>.</p>
        """
    },
]

def gen_service_pages():
    print("\n=== Generating Service Pages ===")
    for svc in SERVICES:
        slug = svc["slug"]
        title = svc["title"]
        meta = svc["meta"]
        canonical = f"{SITE_URL}/services/{slug}"
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": svc["name"],
            "description": meta,
            "provider": {
                "@type": "HairSalon",
                "name": "Craft Collective Salon Group",
                "url": SITE_URL,
                "telephone": PHONE_TEL,
                "address": {"@type": "PostalAddress", "streetAddress": NH_ADDRESS, "addressLocality": NH_CITY, "addressRegion": NH_STATE, "postalCode": NH_ZIP, "addressCountry": "US"},
                "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.9", "bestRating": "5", "ratingCount": "247"}
            },
            "areaServed": {"@type": "City", "name": "Pittsburgh", "sameAs": "https://en.wikipedia.org/wiki/Pittsburgh"}
        }
        
        body = f"""
  <section class="hero-page">
    <p class="breadcrumb-bar"><a href="/">Home</a><span>/</span><a href="/hair-services-pittsburgh">Services</a><span>/</span>{svc["name"]}</p>
    <h1>{svc["h1"]} in <em>Pittsburgh</em></h1>
    <p class="subtitle">{meta}</p>
    <a href="/book" class="btn-primary">Book This Service</a>
  </section>

  <section class="content-section">
    <div class="content-inner">
      <div class="prose">
        {svc["content"]}
      </div>
    </div>
  </section>

  <section class="content-section alt">
    <div class="content-inner">
      <p class="section-label">Our Locations</p>
      <h2 class="section-headline">Two studios, <em>one standard</em></h2>
      <div class="nap-box">
        <h3>Craft Collective Salon Group</h3>
        <p>
          <strong>North Hills:</strong> {NH_ADDRESS}, Pittsburgh PA {NH_ZIP}<br>
          <strong>Canonsburg:</strong> {CB_ADDRESS}, Canonsburg PA {CB_ZIP}<br>
          <strong>Phone:</strong> <a href="tel:{PHONE_TEL}">{PHONE}</a><br>
          <strong>Hours:</strong> Tue-Fri 9am-7pm, Sat 9am-5pm<br>
          <strong>Booking:</strong> <a href="/book">Book Online 24/7</a>
        </p>
      </div>
    </div>
  </section>

  <div class="book-cta">
    <h2>Book {svc["name"]}</h2>
    <p>Online booking available 24/7. Or call {PHONE}.</p>
    <a href="/book" class="btn-dark">Book an Appointment</a>
  </div>
"""
        breadcrumbs = [("Home", SITE_URL), ("Services", f"{SITE_URL}/hair-services-pittsburgh"), (svc["name"], None)]
        page = make_page(title, meta, canonical, "website", breadcrumbs, [schema], body)
        write_page(f"services/{slug}/index.html", page)


# ============================================================
# 3. ADDITIONAL BLOG POSTS
# ============================================================
BLOG_POSTS = [
    {
        "slug": "mens-grooming-trends-2026",
        "title": "Men's Grooming Trends 2026 | What Pittsburgh Guys Are Asking For",
        "meta": "The top men's grooming and haircut trends in Pittsburgh for 2026. From textured crops to gray blending, Craft Collective stylists break down what is trending.",
        "date": "2026-04-22",
        "content": """
        <p>Men's grooming has evolved well beyond the basic fade. At Craft Collective Salon Group, our male clients are more adventurous than ever, and 2026 is shaping up to be the most interesting year yet for men's hair. Here is what our stylists are seeing.</p>

        <h2>Textured Crops Are Still King</h2>
        <p>The textured crop has dominated men's hair for the last few years, and it is showing no signs of slowing down. The appeal is simple: it works on almost every face shape, it is low maintenance, and it looks sharp whether you style it or let it air dry. Our stylists recommend a matte clay or texture paste for the best results.</p>

        <h2>The Medium-Length Revival</h2>
        <p>More Pittsburgh guys are growing their hair out in 2026. Not long, exactly, but past the ears and with enough length to push back or part. Think timeless rather than trendy. This look requires a good cut every 6 to 8 weeks to keep the shape clean.</p>

        <h2>Gray Blending, Not Covering</h2>
        <p>The days of box-dye black to cover grays are over. Men are asking for subtle blending that softens the contrast between gray and natural color without looking "done." Our colorists use demi-permanent formulas that fade naturally and never leave a harsh line of demarcation.</p>

        <h2>Beard Shaping</h2>
        <p>A great haircut deserves a great beard to match. Our stylists offer precision beard shaping that complements your cut and face shape. Even if you maintain your beard at home, a professional shape-up every month keeps things looking intentional.</p>

        <p>Ready to upgrade your grooming routine? <a href="/book">Book a men's appointment online</a> or call us at <a href="tel:+17245147231">724-514-7231</a>.</p>
        """
    },
    {
        "slug": "spring-hair-care-pittsburgh",
        "title": "Spring Hair Care Tips for Pittsburgh Weather | Craft Collective Salon",
        "meta": "How to take care of your hair during Pittsburgh's unpredictable spring weather. Tips from Craft Collective Salon Group's expert stylists on humidity, color protection, and more.",
        "date": "2026-04-18",
        "content": """
        <p>Pittsburgh spring weather is famously unpredictable. One day it is 70 and sunny, the next it is 40 and raining. Your hair care routine needs to adapt. Here are our stylists' top tips for keeping your hair healthy and looking great through spring.</p>

        <h2>Humidity Is Coming -- Prep Now</h2>
        <p>Pittsburgh summers are humid, and spring is when that humidity starts creeping in. If you are frizz-prone, now is the time to book a keratin smoothing treatment. A professional keratin service can reduce frizz for 3 to 5 months, getting you through the worst of the humidity season.</p>

        <h2>Protect Your Color</h2>
        <p>Longer days mean more UV exposure, and UV light is one of the biggest enemies of hair color. If you have balayage, highlights, or any color-treated hair, use a leave-in with UV protection. We recommend products from the Wella Professionals care line, available at both our locations.</p>

        <h2>Lighten Up Your Products</h2>
        <p>Winter calls for heavy oils and rich masks. Spring is the time to switch to lighter formulas. Swap your thick conditioner for a lightweight detangling spray, and trade your heavy oil for a serum. Your hair will feel lighter, shinier, and more manageable.</p>

        <h2>Get a Trim</h2>
        <p>Winter takes a toll on ends. Even if you are growing your hair out, a light dusting or trim removes split ends and keeps your shape looking fresh. Our stylists recommend a trim every 8 to 10 weeks during the transition from winter to spring.</p>

        <p>Need help with your spring hair routine? <a href="/book">Book a consultation</a> with any of our stylists.</p>
        """
    },
    {
        "slug": "top-hair-trends-pittsburgh-2026",
        "title": "Top Hair Trends in Pittsburgh for 2026 | Craft Collective Salon Group",
        "meta": "The biggest hair trends in Pittsburgh for 2026. From copper tones to curtain bangs, Craft Collective stylists share what clients are requesting this year.",
        "date": "2026-04-12",
        "content": """
        <p>Every year brings new trends, but not every trend works for every city. Pittsburgh has its own style -- practical, polished, and confident. Here are the hair trends our Craft Collective stylists are seeing the most demand for in 2026.</p>

        <h2>Warm Copper and Auburn Tones</h2>
        <p>Copper is the color of 2026. Pittsburgh clients are asking for warm, rich copper tones that range from soft strawberry to deep auburn. This trend works beautifully on brunettes who want to go warmer without committing to full blonde. Our colorists use custom Wella formulas to create copper shades that complement your skin tone.</p>

        <h2>Curtain Bangs Are Still Going Strong</h2>
        <p>Curtain bangs had a massive comeback in 2024 and they are not going anywhere. The reason is simple: they frame the face beautifully, work with almost any hair length, and grow out gracefully. If you have been thinking about bangs, curtain bangs are the lowest-risk option.</p>

        <h2>The Italian Bob</h2>
        <p>The Italian bob -- chin-length, slightly layered, with effortless movement -- is the haircut of the moment. It is slightly longer than a traditional bob and sits at the jawline with soft, face-framing pieces. Perfect for Pittsburgh professionals who want a low-maintenance but elevated look.</p>

        <h2>Money Pieces</h2>
        <p>The money piece -- bright, face-framing highlights placed around the hairline -- continues to be one of our most requested color services. It brightens the face, adds instant dimension, and works with any base color. Our colorists recommend pairing it with a subtle balayage for maximum impact.</p>

        <h2>Lived-In Texture</h2>
        <p>The blown-out, perfectly smooth look is giving way to more natural, lived-in texture. Clients want hair that looks effortlessly good -- tousled waves, air-dried curls, and soft bends that look like they happened naturally. This trend is as much about styling technique as it is about the cut.</p>

        <p>Want to try one of these trends? <a href="/book">Book with one of our stylists</a> and bring your inspiration photos.</p>
        """
    },
]

def gen_blog_posts():
    print("\n=== Generating Additional Blog Posts ===")
    for post in BLOG_POSTS:
        slug = post["slug"]
        title = post["title"]
        meta = post["meta"]
        canonical = f"{SITE_URL}/blog/{slug}"
        
        schema = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": title,
            "description": meta,
            "datePublished": post["date"],
            "dateModified": post["date"],
            "author": {"@type": "Organization", "name": "Craft Collective Salon Group"},
            "publisher": {"@type": "Organization", "name": "Craft Collective Salon Group", "url": SITE_URL},
            "mainEntityOfPage": canonical
        }
        
        body = f"""
  <section class="hero-page">
    <p class="breadcrumb-bar"><a href="/">Home</a><span>/</span><a href="/blog">Blog</a><span>/</span>{title.split('|')[0].strip()}</p>
    <h1>{title.split('|')[0].strip()}</h1>
    <p class="subtitle" style="font-size:0.8rem; opacity:0.5;">Published {post["date"]} by Craft Collective Salon Group</p>
  </section>

  <section class="content-section">
    <div class="content-inner">
      <div class="prose">
        {post["content"]}
      </div>
    </div>
  </section>

  <section class="content-section alt">
    <div class="content-inner">
      <p class="section-label">Related</p>
      <h2 class="section-headline">More from <em>our blog</em></h2>
      <div class="service-grid">
        <div class="service-card">
          <h3>Best Balayage in Pittsburgh</h3>
          <p>Why Craft Collective is Pittsburgh's go-to for balayage.</p>
          <a href="/blog/best-balayage-pittsburgh">Read More &rarr;</a>
        </div>
        <div class="service-card">
          <h3>How to Choose a Hair Salon</h3>
          <p>What to look for when picking a salon in Pittsburgh.</p>
          <a href="/blog/how-to-choose-hair-salon-pittsburgh">Read More &rarr;</a>
        </div>
        <div class="service-card">
          <h3>Pittsburgh Wedding Hair</h3>
          <p>Your complete guide to bridal hair styling.</p>
          <a href="/blog/pittsburgh-wedding-hair">Read More &rarr;</a>
        </div>
      </div>
    </div>
  </section>

  <div class="book-cta">
    <h2>Book Your Appointment</h2>
    <p>Online booking available 24/7. Or call {PHONE}.</p>
    <a href="/book" class="btn-dark">Book Now</a>
  </div>
"""
        breadcrumbs = [("Home", SITE_URL), ("Blog", f"{SITE_URL}/blog"), (title.split('|')[0].strip(), None)]
        page = make_page(title, meta, canonical, "article", breadcrumbs, [schema], body)
        write_page(f"blog/{slug}/index.html", page)


# ============================================================
# 4. COMPREHENSIVE SITEMAP
# ============================================================
def gen_sitemap():
    print("\n=== Generating Comprehensive Sitemap ===")
    
    pages = [
        ("/", "1.0", "weekly"),
        ("/hair-services-pittsburgh", "0.9", "monthly"),
        ("/book", "0.9", "monthly"),
        ("/reviews", "0.9", "weekly"),
        ("/blog", "0.9", "weekly"),
        ("/hair-salon-gallery-pittsburgh", "0.8", "weekly"),
        ("/derek-piekarski", "0.8", "monthly"),
        ("/meet-the-team", "0.8", "monthly"),
        ("/about-pittsburgh-hair-salon", "0.7", "monthly"),
        ("/faq", "0.8", "monthly"),
        ("/pittsburgh-hair-salon-guide-2026", "0.8", "monthly"),
        ("/hair-care-tips", "0.7", "monthly"),
    ]
    
    # Existing locations
    pages.append(("/locations/north-hills-pittsburgh", "0.8", "monthly"))
    pages.append(("/locations/canonsburg", "0.7", "monthly"))
    
    # New location pages
    for loc in LOCATIONS:
        pages.append((f"/locations/{loc['slug']}", "0.6", "monthly"))
    
    # Service pages
    for svc in SERVICES:
        pages.append((f"/services/{svc['slug']}", "0.8", "monthly"))
    
    # All team members
    team_members = [
        "derek-piekarski", "abigail-radziminski", "alexis-tara", "allison-logan",
        "alyvia-merz", "amanda-melvin", "angie-beattie", "bethany-yates", "billy-bremer",
        "carlena-bonomi", "caroline-radziminski", "cori-patterson", "delilah-keller",
        "erin-mccleary", "grace-hartle", "greg-mckenzie", "greta-healy", "ha-na-ko",
        "jess-imler", "jess-mitsch", "kayla-quinn", "kelly-buttermore", "kerrie-kipp",
        "kim-hughes", "laurel-seager", "lauren-trudeau", "liz-potts", "logan-goetz",
        "mallory-puniak", "marie-puniak", "nicolette-chieffe", "olivia-spearl",
        "rachel-batykefer", "sarah-emeigh", "sean-boyle", "selena-pace",
        "shari-geldrich", "sherry-maiolini", "susie-ober"
    ]
    for member in team_members:
        pages.append((f"/team/{member}", "0.6", "monthly"))
    
    # Existing blog posts
    existing_blogs = [
        "best-balayage-pittsburgh", "how-to-choose-hair-salon-pittsburgh",
        "balayage-vs-highlights", "hair-extensions-pittsburgh",
        "what-is-corrective-color", "best-hair-care-products-color-treated-2026",
        "pittsburgh-wedding-hair"
    ]
    for blog in existing_blogs:
        pages.append((f"/blog/{blog}", "0.7", "monthly"))
    
    # New blog posts
    for post in BLOG_POSTS:
        pages.append((f"/blog/{post['slug']}", "0.7", "monthly"))
    
    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for path, priority, freq in pages:
        url = SITE_URL + path if path != "/" else SITE_URL + "/"
        sitemap_xml += f"""  <url>
    <loc>{url}</loc>
    <lastmod>2026-04-25</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>
"""
    sitemap_xml += "</urlset>"
    
    with open("sitemap.xml", "w") as f:
        f.write(sitemap_xml)
    print(f"  Updated sitemap.xml with {len(pages)} URLs")


# ============================================================
# 5. ENHANCED ROBOTS.TXT
# ============================================================
def gen_robots():
    print("\n=== Generating robots.txt ===")
    robots = f"""User-agent: *
Allow: /
Disallow: /generate_seo.py
Disallow: /generate_pages.py

Sitemap: {SITE_URL}/sitemap.xml

# Craft Collective Salon Group
# Best Hair Salon in Pittsburgh, PA
# Locations: North Hills (2014D Babcock Blvd) & Canonsburg (115 W Pike St)
"""
    with open("robots.txt", "w") as f:
        f.write(robots)
    print("  Updated robots.txt")


# ============================================================
# RUN ALL
# ============================================================
if __name__ == "__main__":
    print("Craft Collective SEO Enhancement Generator")
    print("=" * 50)
    gen_location_pages()
    gen_service_pages()
    gen_blog_posts()
    gen_sitemap()
    gen_robots()
    print("\n=== DONE ===")
    print(f"Generated {len(LOCATIONS)} location pages")
    print(f"Generated {len(SERVICES)} service pages")
    print(f"Generated {len(BLOG_POSTS)} blog posts")
