#!/usr/bin/env python3
"""
Craft Collective Salon Group — site-wide optimisation pass.

Runs over every page in the repo and brings it up to one standard:

  SEO         Organization + FAQPage + BreadcrumbList schema on every page,
              BlogPosting on every post, canonical/OG/Twitter kept in sync
              with the page title, keyword-targeted titles and descriptions.
  Conversion  A sticky call/book bar on mobile, a trust strip carrying the
              rating and credentials, a book CTA reachable from every page.
  Content     A visible FAQ block on every page — the same questions the
              FAQPage schema declares, because Google requires the answers to
              be on the page, not only in the markup — plus a cross-link row
              so every page reaches services, locations and the team.

Everything injected sits between `<!-- cc:NAME -->` markers and is stripped
before being rewritten, so the script is idempotent: run it as many times as
you like and the output is identical.
"""

import glob
import html
import json
import os
import re
from datetime import date

SITE = "https://www.craftcollectivesalongroup.com"
PHONE = "724-514-7231"
PHONE_HREF = "+17245147231"
EMAIL = "info@craftcollectivesalongroup.com"
BOOKING = "https://phorest.com/book/salons/craftcollectivesalongroup"

NH_ADDR = "2014D Babcock Blvd, Pittsburgh, PA 15209"
CB_ADDR = "115 W Pike St, Canonsburg, PA 15317"
HOURS = "Tuesday-Friday 9am-7pm, Saturday 9am-5pm"

ROOT = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# page inventory
# ---------------------------------------------------------------------------

SERVICES = {
    "balayage-pittsburgh": "Balayage",
    "highlights-pittsburgh": "Highlights",
    "hair-color-pittsburgh": "Hair Color",
    "hair-extensions-pittsburgh": "Hair Extensions",
    "keratin-treatment-pittsburgh": "Keratin Treatment",
    "haircuts-pittsburgh": "Haircuts",
    "blowout-pittsburgh": "Blowouts",
    "bridal-hair-pittsburgh": "Bridal Hair",
    "mens-grooming-pittsburgh": "Men's Grooming",
}

# Service-area pages, and how each one gets to the salon.
AREAS = {
    "north-hills-pittsburgh": ("North Hills", None),
    "canonsburg": ("Canonsburg", None),
    "bethel-park": ("Bethel Park", "about 25 minutes north via I-79 and Route 19"),
    "cranberry-township": ("Cranberry Township", "about 20 minutes south on I-79 and McKnight Road"),
    "fox-chapel": ("Fox Chapel", "about 15 minutes west via Route 8 and Babcock Blvd"),
    "lawrenceville": ("Lawrenceville", "about 15 minutes north on Route 28 and Babcock Blvd"),
    "mccandless": ("McCandless", "under 10 minutes down McKnight Road"),
    "mcmurray": ("McMurray", "about 10 minutes from our Canonsburg studio on W Pike St"),
    "mt-lebanon": ("Mt. Lebanon", "about 25 minutes via I-79, or 15 minutes to our Canonsburg studio"),
    "oakland": ("Oakland", "about 20 minutes north via Bigelow Blvd and Route 28"),
    "robinson-township": ("Robinson Township", "about 25 minutes via I-79 north"),
    "ross-township": ("Ross Township", "under 10 minutes on Babcock Blvd"),
    "sewickley": ("Sewickley", "about 20 minutes east via I-79 and Camp Horne Road"),
    "shadyside": ("Shadyside", "about 20 minutes north via Route 28 and Babcock Blvd"),
    "south-hills": ("South Hills", "about 25 minutes via I-79, or a short drive to our Canonsburg studio"),
    "squirrel-hill": ("Squirrel Hill", "about 25 minutes north via the Parkway and Route 28"),
    "strip-district": ("Strip District", "about 15 minutes north on Route 28"),
    "upper-st-clair": ("Upper St. Clair", "about 15 minutes to our Canonsburg studio on W Pike St"),
    "washington-pa": ("Washington", "about 15 minutes north to our Canonsburg studio"),
    "wexford": ("Wexford", "about 15 minutes south down Route 19 and Babcock Blvd"),
}

BLOG_POSTS = {
    "best-balayage-pittsburgh": ("Best Balayage in Pittsburgh: What Makes Us Different", "2026-04-15", "balayage"),
    "balayage-vs-highlights": ("Balayage vs Highlights: Which Is Right for You?", "2026-03-28", "balayage"),
    "best-hair-care-products-color-treated-2026": ("Best Hair Care Products for Color-Treated Hair in 2026", "2026-02-12", "hair care"),
    "hair-extensions-pittsburgh": ("Hair Extensions in Pittsburgh: A Complete Guide", "2026-01-22", "extensions"),
    "how-to-choose-hair-salon-pittsburgh": ("How to Choose the Right Hair Salon in Pittsburgh's North Hills", "2026-03-05", "choosing a salon"),
    "mens-grooming-trends-2026": ("Men's Grooming Trends for 2026", "2026-02-26", "men's grooming"),
    "pittsburgh-wedding-hair": ("Pittsburgh Wedding Hair: Planning Your Bridal Look", "2026-05-06", "bridal hair"),
    "spring-hair-care-pittsburgh": ("Spring Hair Care in Pittsburgh", "2026-04-02", "seasonal hair care"),
    "top-hair-trends-pittsburgh-2026": ("Top Hair Trends in Pittsburgh for 2026", "2026-01-08", "hair trends"),
    "what-is-corrective-color": ("What Is Corrective Color and Do You Need It?", "2026-05-20", "corrective color"),
}


# ---------------------------------------------------------------------------
# FAQ content
# ---------------------------------------------------------------------------

BOOK_A = (
    f"Book online 24/7 at our booking page, or call {PHONE}. Online booking covers our "
    f"North Hills studio at {NH_ADDR}; our Canonsburg studio at {CB_ADDR} runs by "
    f"appointment, so call to schedule there."
)

SERVICE_FAQ = {
    "balayage-pittsburgh": [
        ("How much does balayage cost in Pittsburgh?",
         "Balayage pricing at Craft Collective depends on hair length, density and how much lift you want. "
         "Because every head of hair takes a different amount of product and time, we quote at consultation "
         f"rather than from a flat price list. Call {PHONE} or book a free consultation and we will give you "
         "an exact number before any colour is mixed."),
        ("How long does a balayage appointment take?",
         "Plan on 2.5 to 4 hours. That covers the consultation, the freehand painting itself, processing, a "
         "custom toner to perfect the shade, a deep conditioning treatment and a blowout finish. A first-time "
         "transformation from dark to bright blonde may be booked across two sessions to protect hair integrity."),
        ("How often do I need to come back for balayage?",
         "Most balayage clients go 12 to 16 weeks between appointments. Because the colour is painted rather "
         "than foiled from the root, there is no hard regrowth line, so it grows out softly. A gloss or toner "
         "refresh at around week eight keeps the tone from going brassy between full appointments."),
        ("Is balayage better than highlights for my hair?",
         "Balayage gives softer, more natural dimension and lower maintenance; traditional foil highlights give "
         "brighter, more uniform lift from the root. Fine hair and clients wanting maximum brightness often do "
         "better in foils, and many people get the best result from a combination. Read our "
         "balayage vs highlights guide, or ask at your consultation."),
        ("Do you do balayage on dark or previously coloured hair?",
         "Yes. Dark bases and box-dye history are among the most common things we work with. Depending on how "
         "much existing pigment is in the hair, we may build the result over two or three appointments so the "
         "hair stays healthy. Our colourists are trained by Derek Piekarski, who taught colour technique for "
         "Wella Professionals across North America."),
    ],
    "highlights-pittsburgh": [
        ("What is the difference between partial and full highlights?",
         "Partial highlights foil the top and sides — the areas that frame your face and show when your hair is "
         "down. Full highlights take foils through the entire head including the back and underneath. Partial is "
         "a good fit if you wear your hair down; full is better if you wear it up, or you want all-over brightness."),
        ("How much do highlights cost in Pittsburgh?",
         "Cost depends on whether you are having partial or full foils, your hair length and density, and whether "
         f"you are adding a gloss or toner. We quote at consultation so the number is accurate. Call {PHONE} or "
         "book online and we will price it before we start."),
        ("How long do highlights last?",
         "Highlights stay bright for roughly 8 to 10 weeks before regrowth becomes obvious at the part line. Many "
         "clients book a root touch-up or a toner refresh between full highlight appointments to stretch the time "
         "between visits."),
        ("Will highlights damage my hair?",
         "Lightening does open the cuticle, which is why technique matters. We use Wella Professionals lightener "
         "with bond-building additives, keep saturation off the scalp where it is not needed, and finish every "
         "service with a deep conditioning treatment. If your hair is not in a condition to lift safely, we will "
         "tell you and build a plan across several appointments instead."),
        ("Can I get highlights and balayage in the same appointment?",
         "Yes, and it is one of our most requested combinations. Foils at the root and around the face give "
         "brightness where you see it; hand-painted balayage through the mid-lengths and ends keeps the grow-out "
         "soft. Ask for a dimensional or lived-in blonde at your consultation."),
    ],
    "hair-color-pittsburgh": [
        ("What hair colour services do you offer?",
         "Single-process colour, root touch-ups, all-over grey coverage, dimensional colour, lived-in colour, "
         "glossing and toning, fashion and vivid shades, and full colour correction. We colour exclusively with "
         "Wella Professionals."),
        ("How much does hair colour cost in Pittsburgh?",
         f"A root touch-up sits at the lower end and a multi-step correction at the higher end. Because colour "
         f"work is priced by time and product, we quote at consultation. Call {PHONE} or book a consultation "
         "online and you will have an exact price before we begin."),
        ("Can you fix a box dye or a colour from another salon?",
         "Yes — corrective colour is one of our specialities. Bring photos of what you have now and what you want. "
         "Depending on how much artificial pigment is in the hair, a correction may take one long appointment or "
         "a series of sessions. We will not promise a result in one visit if getting there safely takes two."),
        ("How do I keep my colour from fading?",
         "Wash with sulphate-free colour-safe shampoo, turn the water temperature down, use heat protectant before "
         "hot tools, and book a gloss between colour appointments. We will send you home with product recommendations "
         "matched to your specific formula."),
        ("How often should I get my colour done?",
         "Root touch-ups every 4 to 6 weeks, all-over colour every 6 to 8 weeks, and dimensional or painted colour "
         "every 12 to 16 weeks. Your stylist will set a rhythm around your hair and your schedule at the first visit."),
    ],
    "hair-extensions-pittsburgh": [
        ("What types of hair extensions do you offer?",
         "We fit hand-tied wefts, tape-in extensions and individual bonds, and we will recommend a method based on "
         "your hair density, lifestyle and budget rather than defaulting to one system for everyone."),
        ("How much do hair extensions cost in Pittsburgh?",
         "Extension pricing has two parts: the hair itself and the labour to install it. Both scale with how many "
         "rows or wefts you need. A consultation is required before booking so we can colour-match, estimate the "
         f"amount of hair and give you a firm total. Call {PHONE} to arrange one."),
        ("How long do hair extensions last?",
         "The hair itself typically lasts 6 to 12 months with proper care. Move-up appointments to reposition the "
         "rows are needed every 6 to 10 weeks depending on how fast your hair grows and which method you have."),
        ("Will extensions damage my natural hair?",
         "Not when they are fitted and maintained correctly. Damage comes from wefts left in too long, rows set too "
         "tight, or too much weight for the hair's density. We size the install to what your hair can carry and "
         "hold you to a move-up schedule."),
        ("How do I care for my extensions at home?",
         "Sulphate-free shampoo, conditioner on the mid-lengths and ends only, a loop brush worked from the ends up, "
         "and hair braided or tied loosely before bed. We walk every new extension client through the routine at the "
         "install appointment."),
    ],
    "keratin-treatment-pittsburgh": [
        ("How long does a keratin treatment last?",
         "Three to five months for most clients. Coarse or very curly hair sometimes runs shorter, and how you wash "
         "matters — sulphate-free shampoo is the single biggest factor in how long the smoothing holds."),
        ("Will a keratin treatment make my hair straight?",
         "It smooths rather than straightens. Curl pattern loosens and frizz largely disappears, but you keep "
         "movement and body. If you want your hair genuinely straight, you will still blow it out — just in about "
         "half the time."),
        ("How much does a keratin treatment cost in Pittsburgh?",
         f"Pricing scales with hair length and density since both change how much solution and processing time the "
         f"service takes. We quote at consultation. Call {PHONE} or book online for an exact figure."),
        ("Can I get a keratin treatment on coloured hair?",
         "Yes. If you are colouring and smoothing in the same visit, colour first and smooth second. Many clients "
         "find keratin actually helps colour last longer because the sealed cuticle holds pigment better."),
        ("How soon can I wash my hair after a keratin treatment?",
         "Follow your stylist's instruction for the specific formula used — with most of the systems we carry you "
         "can wash the same day, while a few require waiting. Either way, switch to a sulphate-free shampoo "
         "permanently; sulphates strip the treatment out early."),
    ],
    "haircuts-pittsburgh": [
        ("How much is a haircut in Pittsburgh at Craft Collective?",
         f"Haircut pricing varies by stylist level and by whether you are booking a cut alone or a cut with a colour "
         f"service. Call {PHONE} or book online and we will confirm the price for the stylist you choose."),
        ("How long does a haircut appointment take?",
         "Around 45 minutes to an hour for a cut and style. That includes a consultation about how you actually wear "
         "your hair day to day, the cut, and a finish so you leave knowing how to recreate it."),
        ("How often should I get my hair cut?",
         "Every 6 to 8 weeks for short cuts and precision shapes, and every 10 to 12 weeks for longer hair where you "
         "are mainly maintaining ends. If you are growing your hair out, regular dusting of the ends actually helps."),
        ("Do you cut curly hair?",
         "Yes. Several of our stylists specialise in curly and textured hair and cut dry so the shape is built around "
         "how the curl actually falls. Mention curl when you book so we can match you to the right stylist."),
        ("Can I book a haircut with a specific stylist?",
         "Yes — our whole team has individual profiles with their specialities, and online booking lets you pick by "
         "name. If you are new and unsure, call us and we will match you to someone who does the kind of work you want."),
    ],
    "blowout-pittsburgh": [
        ("How much does a blowout cost in Pittsburgh?",
         f"Blowouts are priced by hair length and density. Call {PHONE} or book online for the exact price at the "
         "studio and stylist you choose."),
        ("How long does a blowout appointment take?",
         "Usually 30 to 45 minutes, depending on hair length and thickness, and how much finishing work with irons "
         "you want on top of the round-brush blow dry."),
        ("How long will a blowout last?",
         "Two to four days for most people. Dry shampoo at the roots on day two and loose pinning or a silk pillowcase "
         "overnight will get you toward the longer end."),
        ("Should I wash my hair before coming in for a blowout?",
         "No — we will shampoo you at the salon. Arriving with clean dry hair actually makes the finish harder to set, "
         "so come as you are."),
        ("Do you do blowouts for weddings and events?",
         "Yes, and we recommend booking well in advance for wedding parties. For bridal specifically we offer trials "
         "and on-the-day styling for the whole party."),
    ],
    "bridal-hair-pittsburgh": [
        ("How far in advance should I book bridal hair?",
         "Six to nine months ahead for a wedding-season date. Pittsburgh's late-spring and autumn Saturdays book out "
         "first, and booking early also leaves room for a trial at a relaxed time of year."),
        ("Do you offer bridal hair trials?",
         "Yes, and we strongly recommend one. A trial is where we test how your hair holds, how the style photographs, "
         "and how it sits with your veil and neckline. Bring your accessories and a photo of your dress."),
        ("Can you style my whole wedding party?",
         "Yes. Tell us the headcount when you enquire and we will build a timeline so everyone is finished before "
         f"photographs start. Call {PHONE} to discuss party size and scheduling."),
        ("Do you travel to the venue?",
         "On-location styling is available for wedding parties depending on date, party size and travel distance. "
         "Ask when you enquire and we will confirm availability for your date."),
        ("Should I colour my hair before the wedding?",
         "Yes — book colour for two to three weeks before the date. That gives the tone time to settle, leaves room "
         "for a small adjustment if you want one, and means your roots are fresh in the photographs."),
    ],
    "mens-grooming-pittsburgh": [
        ("What men's services do you offer?",
         "Precision cuts, scissor and clipper work, fades, beard shaping and trims, grey blending, and men's colour "
         "including highlights and lowlights."),
        ("How much is a men's haircut in Pittsburgh?",
         f"Pricing depends on the stylist and whether you are adding beard work or colour. Call {PHONE} or book "
         "online for the exact price."),
        ("How often should men get a haircut?",
         "Every 3 to 4 weeks for a fade or a tight taper to keep the line sharp, and every 6 to 8 weeks for longer "
         "or textured cuts."),
        ("Do you offer grey blending for men?",
         "Yes. Grey blending softens grey rather than covering it completely, so it grows out without an obvious line "
         "and looks like your own hair rather than a dye job. It is one of our most requested men's colour services."),
        ("Can I book a men's cut with beard work in one appointment?",
         "Yes — book the cut and mention beard work in the notes, or call us and we will schedule the extra time so "
         "you are not rushed."),
    ],
}

BLOG_FAQ = {
    "best-balayage-pittsburgh": [
        ("What makes a good balayage colourist?",
         "Freehand painting cannot be foiled into place afterwards, so the placement has to be right the first time. "
         "That means an eye for where light naturally falls on your specific head shape, plus enough chemistry "
         "knowledge to know how far a given hair can lift safely. Ask to see a colourist's own portfolio on hair "
         "similar to yours, not the salon's collective feed."),
        ("How much should balayage cost in Pittsburgh?",
         "Pittsburgh balayage pricing scales with hair length, density and how much lift is involved rather than "
         f"sitting at one flat rate. Book a consultation at Craft Collective, or call {PHONE}, and we will quote "
         "your hair specifically before any colour is mixed."),
        ("How long does balayage last?",
         "Twelve to sixteen weeks between full appointments for most clients, with a gloss around week eight to keep "
         "the tone from warming up. The painted grow-out is exactly why balayage is lower maintenance than foils."),
        ("Where can I get balayage in Pittsburgh?",
         f"Craft Collective Salon Group has two studios: {NH_ADDR} in the North Hills, and {CB_ADDR} in Canonsburg. "
         f"Book online 24/7 or call {PHONE}."),
    ],
    "balayage-vs-highlights": [
        ("Is balayage or are highlights better for fine hair?",
         "Foil highlights usually win on fine hair. Foils lift right from the root, which creates the contrast fine "
         "hair needs to read as dimensional; balayage placed on fine hair can go flat because the painted sections "
         "are less densely packed."),
        ("Which is cheaper, balayage or highlights?",
         "Per appointment they are broadly comparable and both scale with hair length. Over a year balayage usually "
         "costs less because you need roughly half as many appointments — 12 to 16 weeks between visits against 8 to "
         "10 for foils."),
        ("Can you combine balayage and highlights?",
         "Yes, and it is one of the most requested looks at our salon. Foils at the root and around the face for "
         "brightness, hand-painted balayage through the mid-lengths and ends for a soft grow-out. Ask for a "
         "dimensional or lived-in blonde."),
        ("How do I know which one to ask for?",
         "Bring photos of what you want and be honest about how often you will realistically come back. If you want "
         "to stretch appointments, ask about balayage. If you want maximum brightness and a clean root, ask about "
         "foils. A consultation settles it in ten minutes."),
    ],
    "best-hair-care-products-color-treated-2026": [
        ("What shampoo is best for colour-treated hair?",
         "A sulphate-free, colour-safe shampoo. Sulphates are the detergents that strip pigment fastest, so switching "
         "shampoo does more for colour longevity than any other single change. Your stylist will match a specific "
         "product to your formula."),
        ("Do purple shampoos actually work?",
         "Yes, on blonde and lightened hair — purple pigment counteracts the yellow tones that develop as colour "
         "oxidises. Use it once or twice a week, not daily; overuse leaves a dull violet cast and does nothing for "
         "the underlying condition."),
        ("How often should I wash colour-treated hair?",
         "Two to three times a week for most people. Every wash costs you some pigment, so stretching washes with dry "
         "shampoo genuinely extends the life of a colour service."),
        ("Are salon products worth it over drugstore?",
         "For colour-treated hair, generally yes — the difference is pigment-safe surfactants and higher-quality "
         "conditioning agents, not the label. What matters most is that the product suits your specific formula, "
         "which is why we recommend per client rather than blanket."),
    ],
    "hair-extensions-pittsburgh": [
        ("Which extension method is best for me?",
         "It depends on your natural density, how you wear your hair and how much maintenance you want. Hand-tied "
         "wefts suit most medium-to-thick hair, tape-ins sit flattest on finer hair, and individual bonds give the "
         "most placement flexibility. A consultation is where this gets decided."),
        ("How much do extensions cost in Pittsburgh?",
         "Two costs: the hair, and the labour to install it. Both scale with how much hair you need. Every extension "
         f"client at Craft Collective starts with a consultation so we can colour-match and quote exactly. Call {PHONE}."),
        ("How long do extensions take to install?",
         "Two to four hours for a first full install, depending on method and how many rows you need. Move-up "
         "appointments afterwards are shorter."),
        ("Will extensions damage my hair?",
         "Not if they are sized to your density and moved up on schedule. Damage comes from too much weight, rows set "
         "too tight, or leaving an install in past its move-up date."),
    ],
    "how-to-choose-hair-salon-pittsburgh": [
        ("What should I look for in a Pittsburgh hair salon?",
         "Three things: verifiable credentials rather than marketing language, a portfolio showing hair like yours, "
         "and a real consultation before any chemical service. A salon that will not consult before colouring is a "
         "salon guessing at your result."),
        ("How do I find a good colourist near me?",
         "Look at individual stylist portfolios, not just the salon's feed — you book a person, not a building. At "
         "Craft Collective every stylist has their own page listing their specialities so you can match before you book."),
        ("What questions should I ask at a consultation?",
         "How many appointments will this take? What will maintenance cost me per year? What happens if my hair does "
         "not lift as planned? A good stylist answers all three without hedging."),
        ("Where is Craft Collective Salon Group located?",
         f"Two studios: {NH_ADDR} in the North Hills, and {CB_ADDR} in Canonsburg. We see clients from across greater "
         f"Pittsburgh. Book online or call {PHONE}."),
    ],
    "mens-grooming-trends-2026": [
        ("How often should men get a haircut?",
         "Every 3 to 4 weeks for fades and tight tapers where the line goes soft quickly, and every 6 to 8 weeks for "
         "longer or textured cuts."),
        ("What is grey blending for men?",
         "A low-commitment colour service that softens grey rather than covering it. Because it is a blend rather than "
         "a block of pigment, it grows out with no visible line and reads as your own hair."),
        ("Do you do beard trims?",
         "Yes — beard shaping and trims, either on their own or added to a cut appointment. Mention it when booking so "
         "we schedule the extra time."),
        ("How much is a men's haircut in Pittsburgh?",
         f"Pricing depends on the stylist and whether you are adding beard work or colour. Call {PHONE} or book online "
         "for exact pricing."),
    ],
    "pittsburgh-wedding-hair": [
        ("How far in advance should I book wedding hair?",
         "Six to nine months for a wedding-season date. Pittsburgh's late-spring and autumn Saturdays go first, and "
         "early booking leaves room for an unhurried trial."),
        ("Do I really need a bridal hair trial?",
         "Yes. A trial is where you find out how your hair holds through a long day, how the style photographs under "
         "flash, and how it sits with your veil. It is much better to discover a problem at the trial than on the morning."),
        ("When should I colour my hair before my wedding?",
         "Two to three weeks before. The tone settles, the roots are fresh in photographs, and there is still time for "
         "a small adjustment if you want one."),
        ("Can you style my bridesmaids too?",
         f"Yes. Tell us your headcount when you enquire and we will build a timeline so the whole party is finished "
         f"before photographs. Call {PHONE} to discuss."),
    ],
    "spring-hair-care-pittsburgh": [
        ("How does Pittsburgh weather affect my hair?",
         "Winter's dry indoor heat leaves hair brittle and static-prone; spring's jump in humidity then swells the "
         "cuticle and brings frizz. The hair that survives both is hair with intact moisture balance, which is why "
         "spring is the natural point to reset your routine."),
        ("Should I get a keratin treatment for humidity?",
         "If frizz in humid weather is your main complaint, yes — that is precisely what smoothing treatments address, "
         "and results last three to five months, which covers a Pittsburgh summer."),
        ("How do I repair winter damage?",
         "A trim to take off split ends, a bond-building or protein treatment depending on whether the damage is "
         "structural or moisture-related, and a lighter conditioner as the humidity rises. Your stylist can tell which "
         "of the two your hair actually needs."),
        ("Should I change my hair colour for spring?",
         "Many clients go a shade or two brighter as the light changes. Balayage is the usual route because it adds "
         "brightness without committing you to a hard root line through the summer."),
    ],
    "top-hair-trends-pittsburgh-2026": [
        ("What hair colours are trending in 2026?",
         "Lived-in dimensional blondes, soft expensive brunettes with subtle warmth, and face-framing money pieces "
         "continue to dominate. The common thread is low-maintenance grow-out — clients want colour that looks "
         "deliberate at week twelve, not just at week one."),
        ("What haircuts are popular right now?",
         "Long layered shapes with movement, blunt collarbone cuts, and the modern shag with curtain fringe. Texture "
         "and movement have replaced the very sleek shapes of a few years ago."),
        ("Is balayage still in style?",
         "Yes, and it has become the default rather than a trend. What has changed is the placement — softer, more "
         "diffused and more tailored to individual face shapes than the heavy contrast of the early 2020s."),
        ("How do I know which trend suits me?",
         "Bring photos to a consultation and be honest about your maintenance appetite. A trend that needs a gloss "
         "every six weeks is the wrong trend if you can only come in twice a year — and a good stylist will say so."),
    ],
    "what-is-corrective-color": [
        ("What is corrective colour?",
         "Any service that fixes an unwanted colour result — banding, brassiness, uneven box dye, a failed at-home "
         "attempt, or colour from another salon that did not land. It is technical work: you are removing and "
         "rebalancing existing pigment, not just applying new colour on top."),
        ("How much does corrective colour cost?",
         "More than a standard colour service, because it takes more time and more product, and sometimes more than "
         f"one appointment. We quote after seeing your hair in person. Call {PHONE} to arrange a consultation."),
        ("Can you fix box dye?",
         "Usually, yes — it is one of the most common things we correct. Box dye deposits a lot of pigment unevenly, "
         "so removing it safely can take more than one session. We will tell you honestly how many."),
        ("How long does corrective colour take?",
         "A straightforward correction runs three to five hours. A significant change — very dark to blonde, for "
         "example — is often staged across two or three appointments, several weeks apart, to keep the hair healthy."),
    ],
}


def area_faq(slug):
    """FAQs for a service-area page."""
    name, drive = AREAS[slug]

    if slug == "north-hills-pittsburgh":
        return [
            ("Where is Craft Collective Salon Group in the North Hills?",
             f"Our North Hills studio is at {NH_ADDR}, on Babcock Blvd just off McKnight Road. Free parking is "
             "available on site."),
            ("What are your North Hills salon hours?",
             f"{HOURS}. We are closed Sunday and Monday. Online booking is open 24/7 even when the salon is not."),
            ("Do I need an appointment or can I walk in?",
             "Walk-ins are taken when there is availability, but colour services in particular book out well ahead, "
             f"so we recommend booking. Reserve online any time or call {PHONE}."),
            ("What services are available at the North Hills location?",
             "The full menu: balayage, highlights, blonding, dimensional and corrective colour, precision haircuts, "
             "keratin smoothing, hair extensions, blowouts and bridal styling, plus nails, skin and lash services."),
            ("Is parking available?",
             "Yes — free on-site parking at the Babcock Blvd studio, directly outside the salon."),
        ]

    if slug == "canonsburg":
        return [
            ("Where is your Canonsburg salon?",
             f"Our Canonsburg studio is at {CB_ADDR}, in the centre of town on W Pike St, serving Washington County "
             "and the South Hills."),
            ("Do I need an appointment for the Canonsburg location?",
             f"Yes — Canonsburg operates by appointment only. Call {PHONE} to schedule with one of our stylists. "
             "Online booking currently covers our North Hills studio."),
            ("What services do you offer in Canonsburg?",
             "The same services and the same standard as North Hills: balayage, highlights, blonding, colour "
             "correction, precision cutting, keratin treatments and extensions."),
            ("Which areas does the Canonsburg salon serve?",
             "Canonsburg, Peters Township, McMurray, Cecil Township, Washington PA, Upper St. Clair, Bethel Park, "
             "Mt. Lebanon and the wider South Hills."),
            ("Is it the same team as the North Hills salon?",
             "Yes. Both studios are Craft Collective Salon Group, trained to the same standard under owner Derek "
             "Piekarski, and both use Wella Professionals colour."),
        ]

    return [
        (f"Do you serve clients from {name}?",
         f"Yes — {name} clients are a regular part of our books. Our North Hills studio at {NH_ADDR} is {drive}, and "
         f"we also have a Canonsburg studio at {CB_ADDR}."),
        (f"What is the best hair salon near {name}?",
         f"Craft Collective Salon Group is rated 4.9 stars across 247 reviews and is led by Derek Piekarski, a former "
         f"Wella Professionals North America Signature Artist. {name} clients come to us for balayage, highlights, "
         f"blonding, colour correction and precision cutting."),
        (f"How do I book an appointment from {name}?",
         BOOK_A),
        (f"What services can {name} clients book?",
         "Balayage, highlights and lowlights, blonding, dimensional and corrective colour, precision haircuts, "
         "keratin smoothing treatments, hair extensions, blowouts and bridal styling."),
        ("What are your hours?",
         f"{HOURS}, closed Sunday and Monday. Online booking stays open 24 hours a day."),
    ]


def stylist_faq(name, role, specialties):
    spec = ", ".join(specialties[:-1]) + " and " + specialties[-1] if len(specialties) > 1 else (
        specialties[0] if specialties else "hair colour and cutting")
    first = name.split()[0]
    return [
        (f"How do I book an appointment with {name}?",
         f"Book {first} directly through our online booking, which is open 24 hours a day, or call {PHONE} and we "
         f"will find you a slot. New clients are welcome."),
        (f"What does {name} specialise in?",
         f"{first} works in {spec}. Every appointment starts with a consultation, so bring photos of what you want "
         "and be honest about how much maintenance you are up for."),
        (f"Where does {name} work?",
         f"{first} sees clients at Craft Collective Salon Group. Our North Hills studio is at {NH_ADDR}; our "
         f"Canonsburg studio at {CB_ADDR} runs by appointment. Call {PHONE} to confirm which location suits your booking."),
        ("What should I expect at my first appointment?",
         f"A consultation before anything else — {first} will look at your hair's history and condition, talk through "
         "what is realistic in one visit versus what needs staging, and quote you before starting. Allow extra time "
         "if you are booking colour for the first time."),
        ("What colour line does the salon use?",
         "Wella Professionals, exclusively. Owner Derek Piekarski served on the Wella North America Signature Artist "
         "Team and trained colourists for the brand across North America."),
    ]


PAGE_FAQ = {
    "about-pittsburgh-hair-salon": [
        ("What makes Craft Collective different from other Pittsburgh salons?",
         "Our owner, Derek Piekarski, spent years training other stylists — he served on the Wella Professionals "
         "North America Signature Artist Team and was North America Manager of Technical Capabilities for Aveda. "
         "Every colourist on our floor has been trained by him personally, to the same standard."),
        ("Where are your salons located?",
         f"Two studios: {NH_ADDR} in Pittsburgh's North Hills, and {CB_ADDR} in Canonsburg. We see clients from "
         "across greater Pittsburgh."),
        ("What services do you offer?",
         "Balayage, highlights, blonding, dimensional and corrective colour, precision haircuts, keratin smoothing, "
         "hair extensions, blowouts and bridal styling, plus nails, skin and lash services."),
        ("What are your hours?", f"{HOURS}. Closed Sunday and Monday. Online booking is open 24/7."),
        ("How do I book?", BOOK_A),
    ],
    "book": [
        ("How do I book an appointment at Craft Collective?", BOOK_A),
        ("Can I book online for both locations?",
         "Online booking currently covers our North Hills studio on Babcock Blvd. The Canonsburg studio on W Pike St "
         f"runs by appointment — call {PHONE} to schedule there."),
        ("How far in advance should I book?",
         "Two to three weeks for colour services, and longer for Saturdays or for bridal. Cuts can often be "
         "accommodated sooner. Weddings should be booked six to nine months ahead."),
        ("Do you take walk-ins?",
         "When there is availability, yes — but colour appointments in particular fill well ahead, so booking is "
         "always safer."),
        ("What is your cancellation policy?",
         f"We ask for at least 24 hours' notice so the slot can be offered to someone else. Call {PHONE} as soon as "
         "you know you need to change an appointment."),
    ],
    "blog": [
        ("Who writes the Craft Collective blog?",
         "Our stylists, led by owner Derek Piekarski — a former Wella Professionals North America Signature Artist "
         "and Master Trainer. Everything here comes from work done on the salon floor in Pittsburgh."),
        ("What topics do you cover?",
         "Colour technique, balayage and highlights, hair care for coloured hair, extensions, keratin smoothing, "
         "seasonal care for Pittsburgh's climate, and trend guides."),
        ("Can I book a consultation about something I read here?",
         f"Yes — that is what the articles are for. Book online 24/7 or call {PHONE} and mention what you have been "
         "reading."),
        ("Do you offer product recommendations?",
         "Yes, both in our articles and in person. Recommendations in the salon are matched to your specific colour "
         "formula and hair condition rather than given as blanket advice."),
    ],
    "derek-piekarski": [
        ("Who is Derek Piekarski?",
         "Derek Piekarski is the owner of Craft Collective Salon Group and a globally recognised hairdresser. He "
         "served on the North America Signature Artist Team for Wella Professionals and was North America Manager "
         "of Technical Capabilities for Aveda / Estée Lauder."),
        ("What awards has Derek won?",
         "He was named one of the top trainers in the world for Wella Professionals in 2016 and received the Franz "
         "Ströher Global Education Master Trainer Award. He has been featured in Vogue India and in the ELMI Cut "
         "Craft video series."),
        ("Can I book an appointment with Derek?",
         f"Yes. Derek sees clients at our North Hills studio at {NH_ADDR}. Book online or call {PHONE} — his column "
         "books out further ahead than most, so plan early."),
        ("What does Derek specialise in?",
         "Balayage, blonding, colour correction, dimensional colour, and hair education. Much of his career has been "
         "spent teaching these techniques to other professionals."),
        ("Does Derek train the rest of the team?",
         "Yes. Every colourist at Craft Collective is trained by Derek directly, using the same curriculum he taught "
         "to salon professionals across North America, Europe and Asia."),
    ],
    "hair-salon-gallery-pittsburgh": [
        ("Is the work in this gallery done at your salon?",
         "Yes — everything shown is work by Craft Collective stylists at our Pittsburgh North Hills and Canonsburg "
         "studios."),
        ("Can I bring a photo from the gallery to my appointment?",
         "Please do. Reference photos are the single most useful thing you can bring to a colour consultation, and "
         "your stylist can tell you immediately what it takes to get there on your hair."),
        ("How do I book the look I want?",
         BOOK_A),
        ("Will my hair look exactly like the photo?",
         "Your starting colour, hair history and texture all affect the outcome. A good consultation is where we tell "
         "you honestly what is achievable in one appointment and what needs staging over two or three."),
        ("What colour products do you use?",
         "Wella Professionals, exclusively. Our owner served on the Wella North America Signature Artist Team."),
    ],
    "hair-care-tips": [
        ("How often should I wash coloured hair?",
         "Two to three times a week for most people. Every wash costs pigment, so stretching washes with dry shampoo "
         "meaningfully extends the life of a colour service."),
        ("What products protect colour-treated hair?",
         "Sulphate-free colour-safe shampoo first — it makes more difference than anything else — plus a heat "
         "protectant before hot tools and a weekly deep conditioner. Your stylist will match specifics to your formula."),
        ("How do I stop frizz in Pittsburgh humidity?",
         "Reduce heat damage, keep moisture balance up with regular conditioning, and consider a keratin smoothing "
         "treatment, which controls frizz for three to five months."),
        ("How often should I trim my hair?",
         "Every 6 to 8 weeks for short shapes and every 10 to 12 weeks for long hair. If you are growing your hair "
         "out, regular dusting of the ends prevents splits travelling up the shaft."),
        ("Can I fix damaged hair at home?",
         "Bond-building and protein treatments help, but only if the damage is the type they address. Bring damaged "
         "hair in and we will tell you whether it needs protein, moisture, or simply cutting off."),
    ],
    "hair-services-pittsburgh": None,  # already has visible FAQ + schema
    "faq": None,                       # is the FAQ page
    "meet-the-team": [
        ("How do I choose a stylist?",
         "Every stylist has their own page listing specialities and their own portfolio. Match the speciality to what "
         "you actually want done — someone who lives in blondes is not automatically the right person for a curly cut."),
        ("Can I book a specific stylist online?",
         f"Yes, online booking lets you choose by name. If you are new and unsure who to pick, call {PHONE} and we "
         "will match you."),
        ("Are all your stylists trained the same way?",
         "Yes. Every colourist is trained directly by owner Derek Piekarski, formerly of the Wella Professionals "
         "North America Signature Artist Team, using the curriculum he taught to professionals internationally."),
        ("Which location does each stylist work at?",
         f"Most of the team is at our North Hills studio at {NH_ADDR}; the Canonsburg studio at {CB_ADDR} runs by "
         f"appointment. Call {PHONE} to confirm for a specific stylist."),
        ("Do you take new clients?",
         "Yes, at both studios and across the team. New colour clients should allow extra time at the first visit "
         "for a full consultation."),
    ],
    "pittsburgh-hair-salon-guide-2026": [
        ("How do I choose a hair salon in Pittsburgh?",
         "Look for verifiable credentials rather than marketing language, a stylist portfolio showing hair like yours, "
         "and a real consultation before any chemical service. A salon that will not consult before colouring is "
         "guessing at your result."),
        ("What should a colour consultation cover?",
         "Your hair's history, what is achievable in one appointment versus what needs staging, the maintenance the "
         "result will require, and a price — before anything is mixed."),
        ("How much does hair colour cost in Pittsburgh?",
         "It scales with length, density and complexity rather than sitting at a flat rate, which is why reputable "
         f"salons quote at consultation. Call {PHONE} and we will book you one."),
        ("What neighbourhoods do you serve?",
         "Clients travel to us from across greater Pittsburgh — North Hills, McCandless, Ross Township, Wexford, "
         "Cranberry, Fox Chapel, Shadyside, Lawrenceville, Squirrel Hill, the Strip District, Oakland, Mt. Lebanon, "
         "Upper St. Clair, Bethel Park, Peters Township, McMurray, Washington and Canonsburg."),
        ("Where is Craft Collective Salon Group?",
         f"{NH_ADDR} in the North Hills, and {CB_ADDR} in Canonsburg. Book online or call {PHONE}."),
    ],
    "reviews": [
        ("How is Craft Collective Salon Group rated?",
         "4.9 out of 5 stars across 247 client reviews, for balayage, highlights, colour correction and precision "
         "cutting."),
        ("Where can I read reviews?",
         "Reviews appear on this page and on Google, and our work is posted on Instagram at "
         "@craftcollectivesalongroup."),
        ("Can I leave a review?",
         "Please do — Google reviews help other Pittsburgh clients find a stylist who does the kind of work they want."),
        ("What do clients say most often?",
         "Two things come up repeatedly: that the consultation is genuinely thorough, and that colour grows out well "
         "enough to stretch the time between appointments."),
        ("How do I book after reading these?", BOOK_A),
    ],
}


# ---------------------------------------------------------------------------
# cross-link blocks
# ---------------------------------------------------------------------------

SERVICE_LINKS = [(f"/services/{s}", n) for s, n in SERVICES.items()]
AREA_LINKS = [
    ("/locations/north-hills-pittsburgh", "North Hills"),
    ("/locations/canonsburg", "Canonsburg"),
    ("/locations/wexford", "Wexford"),
    ("/locations/cranberry-township", "Cranberry Township"),
    ("/locations/mccandless", "McCandless"),
    ("/locations/ross-township", "Ross Township"),
    ("/locations/shadyside", "Shadyside"),
    ("/locations/mt-lebanon", "Mt. Lebanon"),
    ("/locations/south-hills", "South Hills"),
    ("/locations/squirrel-hill", "Squirrel Hill"),
]
CORE_LINKS = [
    ("/hair-services-pittsburgh", "All Services"),
    ("/meet-the-team", "Meet the Team"),
    ("/derek-piekarski", "Derek Piekarski"),
    ("/hair-salon-gallery-pittsburgh", "Gallery"),
    ("/reviews", "Reviews"),
    ("/blog", "Blog"),
    ("/faq", "FAQ"),
    ("/book", "Book Now"),
]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def marker(name, inner):
    return f"<!-- cc:{name} -->{inner}<!-- /cc:{name} -->"


def strip_marker(txt, name):
    return re.sub(rf"<!-- cc:{name} -->.*?<!-- /cc:{name} -->\s*", "", txt, flags=re.S)


def norm(s):
    """Fully decode a string that may have been HTML-escaped more than once.

    Descriptions are read back out of the attributes this script wrote on a
    previous run, so escaping them again would turn `&#x27;` into
    `&amp;#x27;`, then `&amp;amp;#x27;`, once per run. Decoding to a fixed
    point first makes the rewrite idempotent and repairs anything already
    over-escaped.
    """
    prev = None
    while prev != s:
        prev, s = s, html.unescape(s)
    return s


def esc(s):
    return html.escape(norm(s), quote=True)


LD_BLOCK = re.compile(
    r'[ \t]*<script type="application/ld\+json">(.*?)</script>[ \t]*\n?', re.S)


def strip_schema(txt, types, keep=None):
    """Remove every JSON-LD node of the given @types, rewriting in place.

    A regex cannot do this safely. The homepage ships its schema as a single
    JSON *array* holding the business, the Person and an FAQPage, so deleting
    the whole <script> would take the Person with it, and matching `{ ... }`
    inside the array cannot find the right closing brace. Parsing, filtering
    the node list and re-serialising is the only way that survives both the
    array form and the one-object-per-script form the other 89 pages use.
    """
    def repl(m):
        try:
            data = json.loads(m.group(1))
        except ValueError:
            return m.group(0)          # leave anything unparseable untouched

        nodes = data if isinstance(data, list) else [data]
        kept = [n for n in nodes
                if not (isinstance(n, dict) and n.get("@type") in types
                        and not (keep and keep(n)))]

        if not kept:
            return ""
        if len(kept) == len(nodes):
            return m.group(0)          # nothing removed — keep byte-identical

        payload = kept[0] if len(kept) == 1 else kept
        return ('  <script type="application/ld+json">\n'
                + json.dumps(payload, indent=2, ensure_ascii=False)
                + "\n  </script>\n")

    return LD_BLOCK.sub(repl, txt)


def jsonld(obj):
    return ('<script type="application/ld+json">\n'
            + json.dumps(obj, indent=2, ensure_ascii=False)
            + "\n  </script>")


def organization(page_url):
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": f"{SITE}/#organization",
        "name": "Craft Collective Salon Group",
        "alternateName": "Craft Collective",
        "url": SITE,
        "telephone": PHONE_HREF,
        "email": EMAIL,
        "description": (
            "Craft Collective Salon Group is a hair salon group serving the greater Pittsburgh "
            "area, specialising in balayage, highlights, blonding, dimensional and corrective "
            "colour, keratin smoothing, hair extensions and precision cutting. Led by Derek "
            "Piekarski, formerly of the Wella Professionals North America Signature Artist Team."
        ),
        "logo": {"@type": "ImageObject", "url": f"{SITE}/images/logo.png"},
        "image": "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1200&q=85",
        "priceRange": "$$",
        "founder": {"@type": "Person", "name": "Derek Piekarski"},
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "2014D Babcock Blvd",
            "addressLocality": "Pittsburgh",
            "addressRegion": "PA",
            "postalCode": "15209",
            "addressCountry": "US",
        },
        "location": [
            {
                "@type": "Place",
                "name": "Craft Collective Salon Group — North Hills",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "2014D Babcock Blvd",
                    "addressLocality": "Pittsburgh",
                    "addressRegion": "PA",
                    "postalCode": "15209",
                    "addressCountry": "US",
                },
                "telephone": PHONE_HREF,
            },
            {
                "@type": "Place",
                "name": "Craft Collective Salon Group — Canonsburg",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "115 W Pike St",
                    "addressLocality": "Canonsburg",
                    "addressRegion": "PA",
                    "postalCode": "15317",
                    "addressCountry": "US",
                },
                "telephone": PHONE_HREF,
            },
        ],
        "areaServed": [
            {"@type": "City", "name": n} for n in [
                "Pittsburgh", "Canonsburg", "Wexford", "Cranberry Township", "McCandless",
                "Ross Township", "Fox Chapel", "Sewickley", "Shadyside", "Lawrenceville",
                "Squirrel Hill", "Oakland", "Strip District", "Mt. Lebanon", "Upper St. Clair",
                "Bethel Park", "McMurray", "Washington", "Robinson Township",
            ]
        ],
        "knowsAbout": [
            "Balayage", "Highlights", "Hair Color", "Blonding", "Color Correction",
            "Keratin Treatment", "Hair Extensions", "Precision Haircuts", "Bridal Hair",
        ],
        "sameAs": [
            "https://www.instagram.com/craftcollectivesalongroup/",
            "https://www.instagram.com/derek.piekarski",
            BOOKING,
        ],
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "bestRating": "5",
            "worstRating": "1",
            "ratingCount": "247",
            "reviewCount": "247",
        },
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": PHONE_HREF,
            "contactType": "reservations",
            "areaServed": "US",
            "availableLanguage": "English",
        },
        "mainEntityOfPage": page_url,
    }



def website_schema():
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": f"{SITE}/#website",
        "url": SITE,
        "name": "Craft Collective Salon Group",
        "publisher": {"@id": f"{SITE}/#organization"},
        "inLanguage": "en-US",
    }


def service_schema(slug, url):
    name = SERVICES[slug]
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "@id": url + "#service",
        "name": f"{name} in Pittsburgh",
        "serviceType": name,
        "category": "Hair Salon",
        "url": url,
        "provider": {"@id": f"{SITE}/#organization"},
        "areaServed": [{"@type": "City", "name": n} for n in
                       ["Pittsburgh", "Canonsburg", "Wexford", "Cranberry Township",
                        "McCandless", "Mt. Lebanon", "Upper St. Clair", "Shadyside"]],
        "audience": {"@type": "Audience", "audienceType": "Hair salon clients in greater Pittsburgh"},
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": f"{name} options",
            "itemListElement": [{
                "@type": "Offer",
                "itemOffered": {"@type": "Service", "name": name},
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock",
                "url": f"{SITE}/book",
            }],
        },
        "aggregateRating": {
            "@type": "AggregateRating", "ratingValue": "4.9", "bestRating": "5",
            "ratingCount": "247", "reviewCount": "247",
        },
    }


REVIEW_RE = re.compile(
    r'<div class="review-card">\s*'
    r'(?:<div class="review-stars">.*?</div>\s*)?'
    r'<p class="review-text">(.*?)</p>\s*'
    r'.*?<p class="review-name">(.*?)</p>',
    re.S)


def reviews_schema(txt, url):
    """Lift the reviews the page already displays into Review nodes."""
    out = []
    for body, who in REVIEW_RE.findall(txt)[:12]:
        body = norm(" ".join(re.sub(r"<[^>]+>", " ", body).split())).strip('"\u201c\u201d ')
        who = norm(" ".join(re.sub(r"<[^>]+>", " ", who).split()))
        if len(body) < 40 or not who:
            continue
        out.append({
            "@type": "Review",
            "reviewBody": body,
            "author": {"@type": "Person", "name": who},
            "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"},
            "itemReviewed": {"@id": f"{SITE}/#organization"},
        })
    if not out:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "@id": url + "#reviews",
        "name": "Client reviews of Craft Collective Salon Group",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "item": r}
            for i, r in enumerate(out)
        ],
    }


TEAM_CARD = re.compile(
    r'<(?:h3|p) class="team-card-name">(.*?)</(?:h3|p)>\s*'
    r'<p class="team-card-role">(.*?)</p>'
    r'[\s\S]*?href="(/team/[^"]+)"')


def team_list_schema(txt, url):
    """Build the roster from the cards the page actually renders.

    Name, role and profile URL all come off the card, so the list can never
    drift from the page or point at a stylist who has left. An earlier version
    slugified the name to guess the URL, which would have produced 404s for
    anyone whose profile path is not a straight transliteration."""
    cards = TEAM_CARD.findall(txt)
    if not cards:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "@id": url + "#team",
        "name": "Stylists at Craft Collective Salon Group",
        "numberOfItems": len(cards),
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1,
             "item": {
                 "@type": "Person",
                 "name": norm(" ".join(re.sub(r"<[^>]+>", " ", n).split())),
                 "jobTitle": norm(" ".join(re.sub(r"<[^>]+>", " ", role).split())),
                 "worksFor": {"@id": f"{SITE}/#organization"},
                 "url": SITE + href,
             }}
            for i, (n, role, href) in enumerate(cards)
        ],
    }


def faq_schema(qas):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in qas
        ],
    }


def faq_html(qas, heading="Frequently asked <em>questions</em>"):
    items = "\n".join(
        f'''        <div class="faq-item">
          <h3 class="faq-question">{esc(q)}</h3>
          <div class="faq-answer"><p>{esc(a)}</p></div>
        </div>'''
        for q, a in qas
    )
    return f'''
  <section class="faq-block" aria-labelledby="faq-heading">
    <div class="faq-block-inner">
      <p class="section-label">Questions</p>
      <h2 id="faq-heading">{heading}</h2>
      <div class="faq-list">
{items}
      </div>
    </div>
  </section>
'''


def xlinks_html(pairs, heading="Explore more"):
    links = "\n".join(f'        <a href="{u}">{esc(t)}</a>' for u, t in pairs)
    return f'''
  <section class="xlinks" aria-labelledby="xlinks-heading">
    <div class="xlinks-inner">
      <h2 id="xlinks-heading">{esc(heading)}</h2>
      <nav class="xlinks-grid" aria-label="Related pages">
{links}
      </nav>
    </div>
  </section>
'''


CTA_BAR = '''
  <div class="cta-bar" role="region" aria-label="Call or book an appointment">
    <div class="cta-bar-inner">
      <a class="cta-bar-call" href="tel:''' + PHONE_HREF + '''">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>
        <span>Call ''' + PHONE + '''</span>
      </a>
      <a class="cta-bar-book" href="https://phorest.com/book/salons/craftcollectivesalongroup" target="_blank" rel="noreferrer noopener">
        <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4.5" width="18" height="16" rx="2"/><path d="M16 2.5v4M8 2.5v4M3 10.5h18"/></svg>
        <span>Book Now</span>
      </a>
    </div>
  </div>
'''

TRUST_BAR = '''
  <section class="trust-bar" aria-label="Why clients choose Craft Collective">
    <div class="trust-inner">
      <div class="trust-item">
        <span class="trust-value"><span class="stars" aria-hidden="true">&#9733;&#9733;&#9733;&#9733;&#9733;</span></span>
        <span class="trust-label">4.9 from 247 reviews</span>
      </div>
      <div class="trust-item">
        <span class="trust-value">Wella</span>
        <span class="trust-label">Professionals Artist Team</span>
      </div>
      <div class="trust-item">
        <span class="trust-value">2</span>
        <span class="trust-label">Pittsburgh-area studios</span>
      </div>
      <div class="trust-item">
        <span class="trust-value">39</span>
        <span class="trust-label">Stylists &amp; specialists</span>
      </div>
    </div>
  </section>
'''

SKIP_LINK = '<a class="skip-link" href="#main">Skip to content</a>'




# ---------------------------------------------------------------------------
# page imagery
# ---------------------------------------------------------------------------

# The salon's own photography (Wix) first, stock only where there is no real
# shot of that service. Nine service pages and twenty location pages shipped
# with no image at all — a balayage page with no balayage on it.

SALON = {
    "interior": "https://static.wixstatic.com/media/a97d65_a1aca9c3a1c042a0b39a24369bfac59b~mv2.png/v1/fill/w_1200,h_1200,al_c,q_85,enc_avif,quality_auto/a97d65_a1aca9c3a1c042a0b39a24369bfac59b~mv2.png",
    "balayage": "https://static.wixstatic.com/media/a97d65_3d939fce71e84345ac52dae11a44e73c~mv2.png/v1/fill/w_1200,h_1200,al_c,q_85,enc_avif,quality_auto/a97d65_3d939fce71e84345ac52dae11a44e73c~mv2.png",
    "auburn": "https://static.wixstatic.com/media/a97d65_c7c3ed8509894722a6ae538d8ec089b4~mv2.png/v1/fill/w_1200,h_1200,al_c,q_85,enc_avif,quality_auto/a97d65_c7c3ed8509894722a6ae538d8ec089b4~mv2.png",
    "bob": "https://static.wixstatic.com/media/a97d65_aa607f9b93214afaac50abb79d90ad53~mv2.png/v1/fill/w_1200,h_1200,al_c,q_85,enc_avif,quality_auto/a97d65_aa607f9b93214afaac50abb79d90ad53~mv2.png",
    "platinum": "https://static.wixstatic.com/media/a97d65_28985a7c261c42ab8cc18f735803f010~mv2.png/v1/fill/w_1200,h_1200,al_c,q_85,enc_avif,quality_auto/a97d65_28985a7c261c42ab8cc18f735803f010~mv2.png",
}

U = "https://images.unsplash.com/photo-{}?w=1200&q=85"
STOCK = {
    "balayage_paint": U.format("1605497788044-5a32c7078486"),
    "caramel": U.format("1580618672591-eb180b1a973f"),
    "honey": U.format("1519699047748-de8e457a634e"),
    "livedin": U.format("1522337360788-8b13dee7a37e"),
    "sunkissed": U.format("1527799820374-dcf8d9d4a388"),
    "red": U.format("1500917293891-ef795e70e1f6"),
    "extensions": U.format("1595476108010-b4d1f102b1b1"),
    "length": U.format("1519735777090-ec97162dc266"),
    "layers": U.format("1554519515-242161756769"),
    "mens": U.format("1562322140-8baeececf3df"),
    "bridal": U.format("1519699047748-de8e457a634e"),
    "station": U.format("1560066984-138dadb4c035"),
    "studio": U.format("1521590832167-7bcbfaa6381f"),
}

# (hero image, hero alt, [three work shots as (src, alt)])
SERVICE_ART = {
    "balayage-pittsburgh": (
        SALON["balayage"], "Hand-painted brunette balayage by Craft Collective Salon Group, Pittsburgh",
        [(STOCK["caramel"], "Caramel balayage with soft grow-out, Pittsburgh"),
         (STOCK["sunkissed"], "Sun-kissed brunette balayage, Craft Collective Pittsburgh"),
         (STOCK["honey"], "Honey blonde balayage hand-painted in Pittsburgh")]),
    "highlights-pittsburgh": (
        SALON["platinum"], "Platinum foil highlights by Craft Collective Salon Group, Pittsburgh",
        [(STOCK["livedin"], "Lived-in blonde foil highlights, Pittsburgh"),
         (STOCK["caramel"], "Partial highlights framing the face, Pittsburgh salon"),
         (STOCK["honey"], "Full head of foils finished with a custom toner, Pittsburgh")]),
    "hair-color-pittsburgh": (
        SALON["auburn"], "Rich auburn hair colour transformation at Craft Collective, Pittsburgh",
        [(STOCK["red"], "Dimensional red hair colour, Craft Collective Pittsburgh"),
         (STOCK["livedin"], "Lived-in dimensional colour, Pittsburgh salon"),
         (SALON["platinum"], "Platinum colour transformation, Pittsburgh")]),
    "hair-extensions-pittsburgh": (
        STOCK["extensions"], "Hand-tied hair extensions fitted at Craft Collective Salon Group, Pittsburgh",
        [(STOCK["length"], "Length and volume added with hand-tied wefts, Pittsburgh"),
         (STOCK["livedin"], "Extensions colour-matched to existing balayage, Pittsburgh"),
         (SALON["interior"], "Extension fitting at the Craft Collective studio, Pittsburgh")]),
    "keratin-treatment-pittsburgh": (
        SALON["bob"], "Smooth, frizz-free finish after a keratin treatment, Pittsburgh",
        [(STOCK["layers"], "Keratin-smoothed layers holding through Pittsburgh humidity"),
         (STOCK["livedin"], "Frizz-free smoothing on coloured hair, Pittsburgh salon"),
         (SALON["interior"], "Keratin smoothing service at Craft Collective, Pittsburgh")]),
    "haircuts-pittsburgh": (
        SALON["bob"], "Precision bob haircut at Craft Collective Salon Group, Pittsburgh",
        [(STOCK["layers"], "Textured long layers cut in Pittsburgh"),
         (STOCK["mens"], "Precision cutting at Craft Collective, Pittsburgh"),
         (SALON["interior"], "The cutting floor at Craft Collective Pittsburgh")]),
    "blowout-pittsburgh": (
        STOCK["station"], "Blowout and styling at the Craft Collective styling station, Pittsburgh",
        [(SALON["bob"], "Smooth blowout finish, Craft Collective Pittsburgh"),
         (STOCK["layers"], "Round-brush blowout with movement, Pittsburgh salon"),
         (STOCK["livedin"], "Blowout on lived-in blonde colour, Pittsburgh")]),
    "bridal-hair-pittsburgh": (
        STOCK["bridal"], "Bridal hair styling at Craft Collective Salon Group, Pittsburgh",
        [(STOCK["honey"], "Soft bridal waves styled in Pittsburgh"),
         (STOCK["layers"], "Wedding party styling at Craft Collective, Pittsburgh"),
         (SALON["interior"], "Bridal preparation at the Craft Collective studio, Pittsburgh")]),
    "mens-grooming-pittsburgh": (
        STOCK["mens"], "Men's precision haircut at Craft Collective Salon Group, Pittsburgh",
        [(STOCK["layers"], "Men's textured crop cut in Pittsburgh"),
         (SALON["bob"], "Clipper and scissor work, Craft Collective Pittsburgh"),
         (SALON["interior"], "Men's grooming at the Craft Collective studio, Pittsburgh")]),
}

BLOG_ART = {
    "mens-grooming-trends-2026": (STOCK["mens"], "Men's textured crop and fade, Craft Collective Salon Group Pittsburgh"),
    "spring-hair-care-pittsburgh": (STOCK["sunkissed"], "Sun-kissed spring hair colour by Craft Collective, Pittsburgh"),
    "top-hair-trends-pittsburgh-2026": (STOCK["livedin"], "Lived-in dimensional blonde, a leading 2026 Pittsburgh hair trend"),
}

PAGE_ART = {
    "hair-services-pittsburgh": (SALON["interior"], "Craft Collective Salon Group studio floor, Pittsburgh North Hills"),
    "reviews": (SALON["balayage"], "Balayage work reviewed by Craft Collective clients in Pittsburgh"),
    "book": (SALON["interior"], "The Craft Collective Salon Group studio on Babcock Blvd, Pittsburgh"),
    "faq": (STOCK["station"], "Styling station at Craft Collective Salon Group, Pittsburgh"),
    "hair-care-tips": (STOCK["sunkissed"], "Colour-treated hair cared for by Craft Collective, Pittsburgh"),
    "pittsburgh-hair-salon-guide-2026": (SALON["interior"], "Inside Craft Collective Salon Group, Pittsburgh North Hills"),
}

# Location pages alternate so neighbouring areas do not look identical.
AREA_ART = [
    (SALON["interior"], "Craft Collective Salon Group studio, Pittsburgh North Hills"),
    (SALON["balayage"], "Balayage by Craft Collective Salon Group for {} clients"),
    (STOCK["station"], "Styling station at Craft Collective Salon Group near {}"),
    (SALON["platinum"], "Blonding work by Craft Collective for {} clients"),
    (SALON["bob"], "Precision cutting at Craft Collective, serving {}"),
    (STOCK["studio"], "Craft Collective Salon Group interior, serving {}"),
]


def hero_media(src, alt, cls="loc-hero-img"):
    return f'''
  <div class="{cls}">
    <img src="{src}" alt="{esc(alt)}" />
  </div>
'''


def service_shots(shots, name):
    items = "\n".join(
        f'''      <figure class="svc-shot">
        <img src="{s}" alt="{esc(a)}" />
      </figure>''' for s, a in shots)
    return f'''
  <section class="svc-work" aria-labelledby="svc-work-heading">
    <div class="svc-work-inner">
      <p class="section-label">Recent work</p>
      <h2 id="svc-work-heading">{esc(name)} at <em>Craft Collective</em></h2>
      <div class="svc-work-grid">
{items}
      </div>
      <p class="svc-work-note"><a class="link-caps" href="/hair-salon-gallery-pittsburgh">See the full gallery &rarr;</a></p>
    </div>
  </section>
'''


# ---------------------------------------------------------------------------
# image pipeline
# ---------------------------------------------------------------------------

# Intrinsic dimensions, probed once from each CDN and baked in so the build
# stays offline. Keyed by asset id (u: Unsplash photo, w: Wix media) because
# the width parameter in the URL changes as srcsets are generated.
#
# 108 of the site's 115 <img> tags shipped with no width/height at all. With
# `img { max-width:100%; height:auto }` in the page CSS that means the browser
# reserves zero vertical space until each image arrives, then reflows the page
# under the reader — the single largest CLS source on the site.
IMG_DIMS = {
    "u:1500917293891-ef795e70e1f6": (600, 400),
    "u:1519699047748-de8e457a634e": (600, 600),
    "u:1519735777090-ec97162dc266": (600, 368),
    "u:1521590832167-7bcbfaa6381f": (800, 533),
    "u:1522337360788-8b13dee7a37e": (800, 534),
    "u:1527799820374-dcf8d9d4a388": (600, 344),
    "u:1554519515-242161756769": (600, 900),
    "u:1560066984-138dadb4c035": (1200, 900),
    "u:1562322140-8baeececf3df": (600, 401),
    "u:1580618672591-eb180b1a973f": (600, 401),
    "u:1595476108010-b4d1f102b1b1": (600, 899),
    "u:1605497788044-5a32c7078486": (600, 900),
    "w:a97d65_02539649b6434234ba619d6ae47c55f1~mv2.jpg": (900, 900),
    "w:a97d65_073f602d1d9243b08f8979fdf891f1a2~mv2.png": (900, 900),
    "w:a97d65_0cb66574125840d1bda944ab25acdadf~mv2.png": (900, 900),
    "w:a97d65_0d1e6e2b7b374aef9962bd7d0071673b~mv2.jpg": (900, 900),
    "w:a97d65_0fcf92b2a0c340179957a0a2d4459466~mv2.jpg": (900, 900),
    "w:a97d65_1304fe05d4754961b70c8c3f7a32ba16~mv2.jpeg": (900, 900),
    "w:a97d65_145200ac69134c64a570dbbc05f93b7d~mv2.jpg": (900, 900),
    "w:a97d65_162141c6073248bb872f89f4ef4a8ea2~mv2.jpeg": (900, 900),
    "w:a97d65_219410b80eb1427790d2c19b8af7b504~mv2.png": (900, 900),
    "w:a97d65_282d8b75f40141eba7b6f7b9945f2bf5~mv2.jpg": (900, 900),
    "w:a97d65_28985a7c261c42ab8cc18f735803f010~mv2.png": (600, 600),
    "w:a97d65_2b5511cec3174238ac0888ac20c7f9a6~mv2.png": (900, 900),
    "w:a97d65_38ad1a6caabd41fe87974b5ead572bf7~mv2.png": (900, 900),
    "w:a97d65_3b2c3674a90f4997980424b0f8a2c8d1~mv2.png": (900, 900),
    "w:a97d65_3d939fce71e84345ac52dae11a44e73c~mv2.png": (600, 600),
    "w:a97d65_4b886a8e39d042c88d60608593a9ac50~mv2.png": (900, 900),
    "w:a97d65_4c73d688f59a468287e5ee7345d3d845~mv2.jpeg": (900, 900),
    "w:a97d65_645aaa0952f14e2eb894dba6006ee048~mv2.png": (900, 900),
    "w:a97d65_654c6e6ca8274246bfe14f808b84d5ab~mv2.png": (900, 900),
    "w:a97d65_6f0fa7f0e41a4208bf0387ed167fe036~mv2.png": (900, 900),
    "w:a97d65_77be95ef6563489eb6da076dca9771c2~mv2.png": (900, 900),
    "w:a97d65_7925c8b83a9f42df8c603b10825f1cb7~mv2.png": (900, 900),
    "w:a97d65_8080675cee74488599d021a7f3d78536~mv2.jpeg": (900, 900),
    "w:a97d65_822bd865d59f46e68f76e0672a0d92ae~mv2.png": (900, 900),
    "w:a97d65_8e718c1d7ba04e04a2eb60bba649bbf1~mv2.png": (900, 900),
    "w:a97d65_95ce2be7b4704028bf3317dcd5c4d588~mv2.jpg": (900, 900),
    "w:a97d65_9903eef119ce46d6863563950439ef7c~mv2.png": (900, 900),
    "w:a97d65_9c6298889f67465e817d4d9ea334bed7~mv2.jpeg": (900, 900),
    "w:a97d65_9e19d097ca3a46b29398b1c327ae9a9d~mv2.png": (900, 900),
    "w:a97d65_a1aca9c3a1c042a0b39a24369bfac59b~mv2.png": (600, 600),
    "w:a97d65_a7693ca070f243ac8f078f9d494178da~mv2.png": (900, 900),
    "w:a97d65_aa607f9b93214afaac50abb79d90ad53~mv2.png": (600, 600),
    "w:a97d65_ac0e6e9c3da4477086dea2c19ec80f68~mv2.png": (900, 900),
    "w:a97d65_b34d0639d49e486d94dfeb12a7044766~mv2.png": (900, 900),
    "w:a97d65_b8660336445b47ed88eee0c985bdb68e~mv2.png": (900, 900),
    "w:a97d65_ba407c4717d7489b8575e16ac4088524~mv2.jpg": (900, 900),
    "w:a97d65_c7c3ed8509894722a6ae538d8ec089b4~mv2.png": (600, 600),
    "w:a97d65_cd91e26a02474c84805d1691e1726121~mv2.png": (900, 900),
    "w:a97d65_cfd279a1e6b64d2b93c9a58713069f4f~mv2.png": (900, 900),
    "w:a97d65_d15f83e3bd7b4bc7970946a1f631f662~mv2.png": (900, 900),
    "w:a97d65_d555ba4c5f564d3aacc1eeaf87e19018~mv2.jpeg": (900, 900),
    "w:a97d65_e11ddbf9b40641a4ab4da292d24f907a~mv2.png": (900, 900),
    "w:a97d65_f5e400b090a94544810a76a1599117f1~mv2.jpeg": (900, 900),
    "w:a97d65_fac989fda2e84df383a1b8cb48c8f14a~mv2.png": (900, 900),
}

# Only the *ratio* is taken from these numbers: the probed width is whatever
# the URL asked for, not the master asset, so it says nothing about how large
# a source is actually available.


def _asset_key(src):
    m = re.search(r"photo-([\w-]+)", src)
    if m:
        return "u:" + m.group(1)
    m = re.search(r"/media/([\w~.]+?)(?:/v1/|$)", src)
    return "w:" + m.group(1) if m else None


def img_ratio(src, fallback=1.0):
    d = IMG_DIMS.get(_asset_key(src) or "")
    return (d[0] / d[1]) if d else fallback


def _variant(src, w, h):
    """Re-point a CDN URL at a specific rendered size."""
    if "images.unsplash.com" in src:
        base = src.split("?")[0]
        return f"{base}?w={w}&q=80&auto=format&fit=crop"
    if "static.wixstatic.com" in src:
        # .../media/<id>/v1/fill/w_900,h_900,al_c,q_85,enc_avif,quality_auto/<id>
        return re.sub(r"/v1/fill/w_\d+,h_\d+,",
                      f"/v1/fill/w_{w},h_{h},", src)
    return src


# role -> (candidate widths, sizes attribute, rendered aspect ratio or None to
# use the asset's own). Widths stop at 1600: beyond that the CDN is upscaling
# a 900px master, which costs bytes and buys nothing.
IMG_ROLES = {
    "hero-split":  ([480, 768, 1024, 1440], "(min-width: 901px) 50vw, 100vw", None),
    "hero-full":   ([640, 960, 1280, 1600], "100vw", None),
    "article":     ([640, 960, 1280, 1600], "(min-width: 1240px) 1200px, 100vw", 3.0),
    "card":        ([320, 480, 640, 800], "(min-width: 901px) 380px, (min-width: 601px) 50vw, 100vw", 4 / 3),
    "portrait":    ([280, 420, 560], "(min-width: 901px) 280px, (min-width: 601px) 50vw, 100vw", 1.0),
    "gallery":     ([320, 480, 640, 800], "(min-width: 901px) 380px, 50vw", 4 / 3),
}


def classify_img(tag, before):
    """Work out an image's layout role from the container it sits in."""
    if "article-hero-img" in tag:
        return "article"
    opens = re.findall(r'<(?:div|section|a|figure|article)\b[^>]*class="([^"]+)"[^>]*>', before)
    parent = opens[-1].split()[0] if opens else ""
    return {
        "hero-image": "hero-split",
        "hero-image-panel": "hero-split",
        "about-image": "hero-split",
        "derek-image": "hero-split",
        "lead-image": "hero-split",
        "team-card-image": "portrait",
        "gallery-item": "gallery",
        "blog-card-img": "card",
        "service-card-img": "card",
        "svc-shot": "gallery",
        "loc-hero-img": "hero-full",
        "blog-hero-img": "article",
    }.get(parent, "card")


def enhance_img(tag, role, lcp=False):
    """Add srcset/sizes/width/height/decoding/loading to one <img>."""
    src_m = re.search(r'src="([^"]+)"', tag)
    if not src_m:
        return tag
    src = src_m.group(1)

    widths, sizes, forced_ratio = IMG_ROLES[role]
    ratio = forced_ratio or img_ratio(src)

    # Drop attributes this pass owns, so re-running cannot stack them up.
    for attr in ("srcset", "sizes", "width", "height", "loading",
                 "decoding", "fetchpriority"):
        tag = re.sub(rf'\s+{attr}="[^"]*"', "", tag)

    if "static.wixstatic.com" in src or "images.unsplash.com" in src:
        srcset = ", ".join(
            f"{_variant(src, w, max(1, round(w / ratio)))} {w}w" for w in widths)
        tag = tag.replace(f'src="{src}"',
                          f'src="{_variant(src, widths[-2], max(1, round(widths[-2] / ratio)))}"'
                          f' srcset="{srcset}" sizes="{sizes}"')

    w = widths[-2]
    h = max(1, round(w / ratio))
    extra = f' width="{w}" height="{h}" decoding="async"'
    # The LCP candidate must not be lazy — deferring it is a direct LCP
    # regression — and gets priority over everything else in the queue.
    extra += ' loading="eager" fetchpriority="high"' if lcp else ' loading="lazy"'

    return tag[:-1].rstrip().rstrip("/").rstrip() + extra + " />"


def process_images(txt):
    """Rewrite every <img> on the page and preload the LCP candidate."""
    body_start = txt.find("<body")
    if body_start == -1:
        return txt, None

    # Everything ahead of <body> is carried through untouched — the scan only
    # starts at the body so that an <img> inside a JSON-LD string or an OG tag
    # is never rewritten.
    out = [txt[:body_start]]
    cursor = body_start
    first = True
    preload = None

    for m in re.finditer(r"<img\b[^>]*>", txt[body_start:]):
        start, end = body_start + m.start(), body_start + m.end()
        before = txt[max(0, start - 300):start]
        role = classify_img(m.group(0), before)
        new = enhance_img(m.group(0), role, lcp=first)

        if first:
            s = re.search(r'src="([^"]+)"', new)
            ss = re.search(r'srcset="([^"]+)"', new)
            sz = re.search(r'sizes="([^"]+)"', new)
            if s:
                preload = (s.group(1), ss.group(1) if ss else "",
                           sz.group(1) if sz else "")
            first = False

        out.append(txt[cursor:start])
        out.append(new)
        cursor = end

    out.append(txt[cursor:])
    return "".join(out), preload


# ---------------------------------------------------------------------------
# per-page transformation
# ---------------------------------------------------------------------------

HERO_OPEN = re.compile(
    r'<(section|div)\b[^>]*class="[^"]*\b(?:hero|hero-page|page-hero|derek-hero)\b[^"]*"[^>]*>')


def find_hero(txt):
    """Locate the page's first hero block: (open_start, open_end, close_end).

    Regex alone cannot find the matching close tag, so this scans forward
    counting opens and closes of the same tag name. The markup here is
    well-formed and heroes are never self-closing, which is what makes the
    count reliable.
    """
    body = txt.find("<body")
    m = HERO_OPEN.search(txt, body if body != -1 else 0)
    if not m:
        return None

    tag = m.group(1)
    depth = 1
    pos = m.end()
    step = re.compile(rf"<(/?){tag}\b", re.I)

    while depth:
        nxt = step.search(txt, pos)
        if not nxt:
            return None
        depth += -1 if nxt.group(1) else 1
        pos = nxt.end()

    close = txt.find(">", pos)
    if close == -1:
        return None
    return m.start(), m.end(), close + 1


def classify(path):
    p = path.replace(os.sep, "/")
    if p == "index.html":
        return "home", ""
    parts = p.split("/")
    if parts[0] == "services":
        return "service", parts[1]
    if parts[0] == "locations":
        return "location", parts[1]
    if parts[0] == "team":
        return "stylist", parts[1]
    if parts[0] == "blog":
        return ("blog-index", "") if len(parts) == 2 else ("blog-post", parts[1])
    return "page", parts[0]


def page_url(path):
    p = path.replace(os.sep, "/")
    if p == "index.html":
        return SITE + "/"
    return SITE + "/" + p[: -len("/index.html")]


def get_faqs(kind, slug, txt):
    if kind == "service":
        return SERVICE_FAQ.get(slug)
    if kind == "location":
        return area_faq(slug) if slug in AREAS else None
    if kind == "blog-post":
        return BLOG_FAQ.get(slug)
    if kind == "stylist":
        name = re.search(r'class="name">(.*?)</h1>', txt, re.S)
        name = " ".join(re.sub(r"<[^>]+>", " ", name.group(1)).split()) if name else slug.replace("-", " ").title()
        role = re.search(r'class="page-eyebrow">(.*?)<', txt, re.S)
        role = role.group(1).strip() if role else "Stylist"
        specs = re.findall(r"<li><strong>(.*?)</strong></li>", txt)
        return stylist_faq(name, role, specs)
    if kind in ("page", "blog-index", "home"):
        key = slug or ("blog" if kind == "blog-index" else "home")
        return PAGE_FAQ.get(key)
    return None


def get_xlinks(kind, slug):
    if kind == "service":
        others = [(u, n) for u, n in SERVICE_LINKS if not u.endswith(slug)][:6]
        return ("Related services and locations",
                others + [("/hair-services-pittsburgh", "All Services"),
                          ("/meet-the-team", "Meet the Team"),
                          ("/hair-salon-gallery-pittsburgh", "See Our Work"),
                          ("/locations/north-hills-pittsburgh", "North Hills Salon"),
                          ("/locations/canonsburg", "Canonsburg Salon"),
                          ("/book", "Book Now")])
    if kind == "location":
        others = [(u, n) for u, n in AREA_LINKS if not u.endswith("/" + slug)][:6]
        return ("Services and nearby areas",
                SERVICE_LINKS[:6] + others + [("/book", "Book Now")])
    if kind == "stylist":
        return ("Book a service or browse the team",
                SERVICE_LINKS[:6] + [("/meet-the-team", "Full Team"),
                                     ("/derek-piekarski", "Derek Piekarski"),
                                     ("/hair-salon-gallery-pittsburgh", "Gallery"),
                                     ("/reviews", "Reviews"),
                                     ("/book", "Book Now")])
    if kind in ("blog-post", "blog-index"):
        return ("Services featured in this article",
                SERVICE_LINKS + [("/blog", "All Articles"), ("/book", "Book Now")])
    return ("Explore Craft Collective", CORE_LINKS + SERVICE_LINKS[:6] + AREA_LINKS[:4])


def build_breadcrumb(kind, slug, txt, url):
    crumbs = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE}]
    if kind == "service":
        crumbs.append({"@type": "ListItem", "position": 2, "name": "Services",
                       "item": f"{SITE}/hair-services-pittsburgh"})
        crumbs.append({"@type": "ListItem", "position": 3, "name": SERVICES.get(slug, slug), "item": url})
    elif kind == "location":
        crumbs.append({"@type": "ListItem", "position": 2, "name": "Locations",
                       "item": f"{SITE}/locations/north-hills-pittsburgh"})
        crumbs.append({"@type": "ListItem", "position": 3,
                       "name": AREAS.get(slug, (slug, None))[0], "item": url})
    elif kind == "stylist":
        m = re.search(r'class="name">(.*?)</h1>', txt, re.S)
        nm = " ".join(re.sub(r"<[^>]+>", " ", m.group(1)).split()) if m else slug.replace("-", " ").title()
        crumbs.append({"@type": "ListItem", "position": 2, "name": "Team", "item": f"{SITE}/meet-the-team"})
        crumbs.append({"@type": "ListItem", "position": 3, "name": nm, "item": url})
    elif kind == "blog-post":
        crumbs.append({"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog"})
        crumbs.append({"@type": "ListItem", "position": 3,
                       "name": BLOG_POSTS.get(slug, (slug, "", ""))[0], "item": url})
    elif kind == "home":
        return None
    else:
        m = re.search(r"<title>(.*?)(?:\s*\|.*)?</title>", txt, re.S)
        nm = m.group(1).strip() if m else slug.replace("-", " ").title()
        crumbs.append({"@type": "ListItem", "position": 2, "name": nm, "item": url})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": crumbs}


def blogposting(slug, txt, url):
    title, published, topic = BLOG_POSTS[slug]
    desc = re.search(r'name="description" content="([^"]*)"', txt)
    img = re.search(r'class="article-hero-img"[^>]*src="([^"]*)"', txt) or \
          re.search(r'property="og:image" content="([^"]*)"', txt)
    body = txt.split("</style>", 1)[-1]
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    return {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "@id": url + "#article",
        "headline": norm(title),
        "description": norm(desc.group(1)) if desc else norm(title),
        "image": img.group(1) if img else "",
        "datePublished": published,
        "dateModified": date.today().isoformat(),
        "wordCount": words,
        "inLanguage": "en-US",
        "keywords": f"{topic}, pittsburgh hair salon, {topic} pittsburgh",
        "author": {
            "@type": "Person",
            "name": "Derek Piekarski",
            "url": f"{SITE}/derek-piekarski",
            "jobTitle": "Owner & Master Stylist",
        },
        "publisher": {"@id": f"{SITE}/#organization"},
        "isPartOf": {"@type": "Blog", "name": "Craft Collective Salon Group Blog", "url": f"{SITE}/blog"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "about": {"@type": "Thing", "name": topic.title()},
    }


VISIBLE_FAQ = re.compile(
    r'<div class="faq-item">\s*'
    r'<(?:div|h3)[^>]*class="faq-question"[^>]*>(.*?)</(?:div|h3)>\s*'
    r'<div class="faq-answer"[^>]*>(.*?)</div>',
    re.S)


def scrape_visible_faq(txt):
    """Read the Q&A a page already displays, so its schema can be built from it.

    Three pages — the homepage, /faq and /hair-services-pittsburgh — shipped
    their own visible accordions, so the build leaves that content alone. Two
    of them also shipped a FAQPage whose questions were nothing like the ones
    on screen: the homepage declared "Where is Craft Collective located?" while
    displaying "What areas do you serve?". Google requires the answer to be
    present on the page, so that markup was ineligible for a rich result and
    read as keyword stuffing. Deriving the schema from the DOM instead makes
    the two agree by construction.
    """
    out = []
    for q, a in VISIBLE_FAQ.findall(txt):
        q = norm(" ".join(re.sub(r"<[^>]+>", " ", q).split()))
        a = norm(" ".join(re.sub(r"<[^>]+>", " ", a).split()))
        if q and len(a) > 40:
            out.append((q, a))
    return out


# --------------------------- meta title / description ----------------------

TITLE_OVERRIDES = {
    "index.html": (
        "Best Hair Salon Pittsburgh PA | Craft Collective Salon",
        "Pittsburgh's top-rated hair salon — 4.9 stars from 247 reviews. Balayage, highlights, "
        "hair color, extensions and keratin treatments across greater Pittsburgh. Led by Wella "
        f"Professionals artist Derek Piekarski. North Hills & Canonsburg. Call {PHONE}.",
    ),
    "services/balayage-pittsburgh/index.html": (
        "Balayage Pittsburgh PA | Hand-Painted Color & Blonding",
        "Balayage in Pittsburgh by expert colorists at Craft Collective Salon Group. Soft, "
        "hand-painted dimension that grows out beautifully — 12 to 16 weeks between visits. "
        f"North Hills & Canonsburg. Book online or call {PHONE}.",
    ),
    "services/highlights-pittsburgh/index.html": (
        "Highlights Pittsburgh PA | Partial & Full Foils",
        "Highlights in Pittsburgh — partial foils, full foils, lowlights and dimensional blonding "
        "at Craft Collective Salon Group. Wella Professionals color, 4.9-star rated. North Hills "
        f"& Canonsburg. Book online or call {PHONE}.",
    ),
    "services/hair-color-pittsburgh/index.html": (
        "Hair Color Pittsburgh PA | Correction & Glossing",
        "Hair color in Pittsburgh: single-process, grey coverage, dimensional color, glossing and "
        "full color correction at Craft Collective Salon Group. Wella Professionals exclusively. "
        f"Book online or call {PHONE}.",
    ),
    "services/hair-extensions-pittsburgh/index.html": (
        "Hair Extensions Pittsburgh PA | Hand-Tied & Tape-In",
        "Hair extensions in Pittsburgh — hand-tied wefts, tape-ins and individual bonds, color "
        "matched at consultation. Craft Collective Salon Group, North Hills & Canonsburg. "
        f"Call {PHONE} to book a consultation.",
    ),
    "services/keratin-treatment-pittsburgh/index.html": (
        "Keratin Treatment Pittsburgh PA | Frizz-Free Hair",
        "Keratin smoothing treatments in Pittsburgh at Craft Collective Salon Group. Cut frizz and "
        "styling time for three to five months — built for Pittsburgh humidity. North Hills & "
        f"Canonsburg. Book online or call {PHONE}.",
    ),
    "services/haircuts-pittsburgh/index.html": (
        "Haircuts Pittsburgh PA | Precision & Curly Cuts",
        "Precision haircuts in Pittsburgh at Craft Collective Salon Group — including curly and "
        "textured hair specialists. Consultation with every cut. North Hills & Canonsburg. "
        f"Book online or call {PHONE}.",
    ),
    "services/blowout-pittsburgh/index.html": (
        "Blowouts Pittsburgh PA | Salon Blow Dry & Styling",
        "Professional blowouts in Pittsburgh at Craft Collective Salon Group. Smooth, long-lasting "
        f"blow dry and styling for events, weddings or any day. North Hills & Canonsburg. Call {PHONE}.",
    ),
    "services/bridal-hair-pittsburgh/index.html": (
        "Bridal Hair Pittsburgh PA | Wedding Styling & Trials",
        "Bridal hair in Pittsburgh — trials, wedding-day styling and full wedding party scheduling "
        f"at Craft Collective Salon Group. Book six to nine months ahead. North Hills & Canonsburg. Call {PHONE}.",
    ),
    "services/mens-grooming-pittsburgh/index.html": (
        "Men's Haircuts Pittsburgh PA | Fades & Beard Trims",
        "Men's grooming in Pittsburgh: precision cuts, fades, beard shaping and grey blending at "
        f"Craft Collective Salon Group. North Hills & Canonsburg. Book online or call {PHONE}.",
    ),
    "locations/north-hills-pittsburgh/index.html": (
        "Hair Salon North Hills Pittsburgh | Babcock Blvd",
        "Craft Collective Salon Group in Pittsburgh's North Hills — 2014D Babcock Blvd, free "
        "parking, open Tue-Fri 9-7 and Sat 9-5. Balayage, highlights, color, keratin and "
        f"extensions. Book online 24/7 or call {PHONE}.",
    ),
    "locations/canonsburg/index.html": (
        "Hair Salon Canonsburg PA | 115 W Pike St",
        "Craft Collective Salon Group in Canonsburg — 115 W Pike St, by appointment. Balayage, "
        "highlights, color correction and precision cutting for Washington County and the South "
        f"Hills. Call {PHONE} to book.",
    ),
    "derek-piekarski/index.html": (
        "Derek Piekarski Hair | Pittsburgh Master Colorist",
        "Derek Piekarski — owner of Craft Collective Salon Group, former Wella Professionals North "
        "America Signature Artist and Franz Ströher Global Education Master Trainer. Book balayage, "
        f"blonding and color correction in Pittsburgh. Call {PHONE}.",
    ),
    "meet-the-team/index.html": (
        "Meet Our Stylists | Hair Salon Team Pittsburgh",
        "Meet the stylists and colorists at Craft Collective Salon Group in Pittsburgh. Every "
        "colorist trained personally by Wella Professionals artist Derek Piekarski. Browse "
        "specialties and book by name.",
    ),
    "hair-services-pittsburgh/index.html": (
        "Hair Salon Services Pittsburgh | Color, Cuts, Extensions",
        "Full service menu at Craft Collective Salon Group Pittsburgh: balayage, highlights, hair "
        "color, color correction, keratin treatments, extensions, haircuts, blowouts and bridal "
        f"hair. North Hills & Canonsburg. Call {PHONE}.",
    ),
    "hair-salon-gallery-pittsburgh/index.html": (
        "Hair Salon Gallery Pittsburgh | Balayage & Color",
        "See real balayage, highlights, blonding and color correction work by Craft Collective "
        "Salon Group stylists in Pittsburgh. Bring a photo to your consultation and we will tell "
        "you what it takes on your hair.",
    ),
    "reviews/index.html": (
        "Reviews | Best Hair Salon Pittsburgh PA | 4.9 Stars",
        "4.9 stars from 247 client reviews. Read what Pittsburgh clients say about balayage, "
        "highlights, color correction and precision cutting at Craft Collective Salon Group in "
        "the North Hills and Canonsburg.",
    ),
    "book/index.html": (
        "Book a Hair Appointment Pittsburgh | Online 24/7",
        "Book your appointment at Craft Collective Salon Group. Online booking 24/7 for our North "
        f"Hills studio at 2014D Babcock Blvd; call {PHONE} for Canonsburg at 115 W Pike St.",
    ),
    "faq/index.html": (
        "Hair Salon FAQ Pittsburgh | Pricing, Booking & Color",
        "Answers to the questions Pittsburgh clients ask most: what balayage costs, how long "
        "color takes, booking and cancellation, keratin, extensions and corrective color at "
        "Craft Collective Salon Group.",
    ),
    "blog/index.html": (
        "Hair Care Blog | Pittsburgh Salon Advice",
        "Colour technique, hair care and trend guides from the stylists at Craft Collective Salon "
        "Group in Pittsburgh — balayage, highlights, extensions, keratin and seasonal care for "
        "Pittsburgh's climate.",
    ),
    "about-pittsburgh-hair-salon/index.html": (
        "About Craft Collective | Hair Salon Pittsburgh PA",
        "Craft Collective Salon Group serves greater Pittsburgh from studios in the North Hills "
        "and Canonsburg. Every colorist trained by Wella Professionals artist Derek Piekarski. "
        "4.9 stars from 247 reviews.",
    ),
    "hair-care-tips/index.html": (
        "Hair Care Tips from Pittsburgh Salon Stylists",
        "How to keep color from fading, control frizz in Pittsburgh humidity, and when to trim — "
        "practical hair care advice from the stylists at Craft Collective Salon Group.",
    ),
    "pittsburgh-hair-salon-guide-2026/index.html": (
        "Pittsburgh Hair Salon Guide 2026 | How to Choose a Colorist",
        "How to choose a hair salon in Pittsburgh in 2026: credentials that matter, what a real "
        "colour consultation covers, what colour actually costs, and the neighbourhoods served by "
        "Craft Collective Salon Group.",
    ),
}


TITLE_MAX = 62  # Google truncates the SERP link at roughly this width


def fit_title(*candidates):
    """Pick the first candidate that fits a search result, longest-first.

    Templated titles vary in length by up to 30 characters — "Kim Hughes,
    Stylist" against "Caroline Radziminski, Esthetician / Lashes" — so a single
    format string either wastes the budget on short names or blows past it on
    long ones. Each caller passes its preferred form first and progressively
    terser fallbacks after it.
    """
    for c in candidates:
        if len(c) <= TITLE_MAX:
            return c
    return candidates[-1][:TITLE_MAX - 1].rstrip(" |,-") + "\u2026"


def area_meta(slug):
    name, _ = AREAS[slug]
    return (
        fit_title(
            f"Hair Salon Near {name} PA | Balayage & Color | Craft Collective",
            f"Hair Salon Near {name} PA | Craft Collective",
            f"Hair Salon Near {name} PA | Craft Collective Salon",
        ),
        f"Craft Collective Salon Group serves {name} clients from our Pittsburgh North Hills and "
        f"Canonsburg studios. Balayage, highlights, hair color, keratin and extensions — 4.9 stars "
        f"from 247 reviews. Book online or call {PHONE}.",
    )


def stylist_meta(slug, txt):
    m = re.search(r'class="name">(.*?)</h1>', txt, re.S)
    nm = " ".join(re.sub(r"<[^>]+>", " ", m.group(1)).split()) if m else slug.replace("-", " ").title()
    r = re.search(r'class="page-eyebrow">(.*?)<', txt, re.S)
    role = r.group(1).strip() if r else "Stylist"
    specs = re.findall(r"<li><strong>(.*?)</strong></li>", txt)
    sp = ", ".join(specs[:3]) if specs else "hair color and cutting"
    # "Stylist / Lashes" and the like eat the whole budget; the first segment
    # keeps the role recognisable at half the width.
    short_role = role.split("/")[0].strip() or "Stylist"
    return (
        fit_title(
            f"{nm} | {role} Pittsburgh | Craft Collective Salon Group",
            f"{nm} | {role} Pittsburgh | Craft Collective",
            f"{nm} | {short_role} Pittsburgh | Craft Collective",
            f"{nm} | {short_role} Pittsburgh | Craft Collective Salon",
        ),
        f"Book {nm}, {role.lower()} at Craft Collective Salon Group in Pittsburgh. Specialising in "
        f"{sp}. Trained by Wella Professionals artist Derek Piekarski. Book online or call {PHONE}.",
    )


BLOG_TITLES = {
    "best-balayage-pittsburgh": "Best Balayage in Pittsburgh | Craft Collective Salon",
    "balayage-vs-highlights": "Balayage vs Highlights: Which Suits Your Hair?",
    "best-hair-care-products-color-treated-2026": "Best Products for Color-Treated Hair in 2026",
    "hair-extensions-pittsburgh": "Hair Extensions Pittsburgh: A Complete Guide",
    "how-to-choose-hair-salon-pittsburgh": "How to Choose a Hair Salon in Pittsburgh",
    "mens-grooming-trends-2026": "Men's Grooming Trends 2026 | Pittsburgh Salon",
    "pittsburgh-wedding-hair": "Pittsburgh Wedding Hair: Planning Your Bridal Look",
    "spring-hair-care-pittsburgh": "Spring Hair Care Tips from Pittsburgh Stylists",
    "top-hair-trends-pittsburgh-2026": "Top Hair Trends in Pittsburgh for 2026",
    "what-is-corrective-color": "What Is Corrective Color? | Pittsburgh Colorists",
}


def blog_meta(slug, txt):
    d = re.search(r'name="description" content="([^"]*)"', txt)
    title = BLOG_TITLES.get(slug, BLOG_POSTS[slug][0])
    return (title, norm(d.group(1)) if d else BLOG_POSTS[slug][0])


def og_crop(src):
    """Re-point a social image at a true 1200x630 crop.

    The og:image:width/height tags below claim 1200x630. Both CDNs can crop to
    order, so the claim is made true rather than dropped — an accurate size
    lets a scraper lay the card out before the image lands, and a wrong one
    gets the card letterboxed or rejected outright."""
    if "images.unsplash.com" in src:
        return src.split("?")[0] + "?w=1200&h=630&fit=crop&crop=entropy&q=80&auto=format"
    if "static.wixstatic.com" in src:
        return re.sub(r"/v1/fill/w_\d+,h_\d+,", "/v1/fill/w_1200,h_630,", src)
    return src


def set_meta(txt, title, desc, url):
    """Rewrite title, description, canonical, OG and Twitter as one consistent set."""
    txt = re.sub(r"<title>.*?</title>", f"<title>{esc(title)}</title>", txt, count=1, flags=re.S)
    txt = re.sub(r'(<meta name="description" content=")[^"]*(")',
                 lambda m: m.group(1) + esc(desc) + m.group(2), txt, count=1)
    txt = re.sub(r'(<link rel="canonical" href=")[^"]*(")',
                 lambda m: m.group(1) + url + m.group(2), txt, count=1)
    for prop, val in (("og:title", title), ("og:description", desc), ("og:url", url)):
        txt = re.sub(rf'(<meta property="{prop}" content=")[^"]*(")',
                     lambda m, v=val: m.group(1) + esc(v) + m.group(2), txt, count=1)
    for nm, val in (("twitter:title", title), ("twitter:description", desc)):
        txt = re.sub(rf'(<meta name="{nm}" content=")[^"]*(")',
                     lambda m, v=val: m.group(1) + esc(v) + m.group(2), txt, count=1)

    for pat in (r'(<meta property="og:image" content=")([^"]*)(")',
                r'(<meta name="twitter:image" content=")([^"]*)(")'):
        txt = re.sub(pat, lambda m: m.group(1) + og_crop(m.group(2)) + m.group(3),
                     txt, count=1)
    return txt


# ---------------------------------------------------------------------------

def process(path):
    full = os.path.join(ROOT, path)
    txt = open(full, encoding="utf-8").read()
    orig = txt
    kind, slug = classify(path)
    url = page_url(path)

    # ---- 0. clear previous runs -------------------------------------------
    for m in ("head", "cta", "faq", "xlinks", "trust", "skip", "art", "work"):
        txt = strip_marker(txt, m)

    # ---- 1. meta ----------------------------------------------------------
    key = path.replace(os.sep, "/")
    if key in TITLE_OVERRIDES:
        title, desc = TITLE_OVERRIDES[key]
    elif kind == "location" and slug in AREAS:
        title, desc = area_meta(slug)
    elif kind == "stylist":
        title, desc = stylist_meta(slug, txt)
    elif kind == "blog-post" and slug in BLOG_POSTS:
        title, desc = blog_meta(slug, txt)
    else:
        tm = re.search(r"<title>(.*?)</title>", txt, re.S)
        dm = re.search(r'name="description" content="([^"]*)"', txt)
        title = norm(tm.group(1).strip()) if tm else "Craft Collective Salon Group"
        desc = norm(dm.group(1)) if dm else ""

    txt = set_meta(txt, title, desc, url)

    # ---- 2. head additions ------------------------------------------------
    head_bits = [
        '<meta name="theme-color" content="#17150f" />',
        '<meta name="format-detection" content="telephone=yes" />',
        '<meta name="author" content="Craft Collective Salon Group" />',
        '<meta name="geo.region" content="US-PA" />',
        '<meta name="geo.placename" content="Pittsburgh" />',
        '<meta property="og:site_name" content="Craft Collective Salon Group" />',
        '<meta name="twitter:site" content="@craftcollectivesalongroup" />',
        # Without this Google shows a thumbnail-sized image or none at all.
        '<meta name="robots" content="index, follow, max-image-preview:large, '
        'max-snippet:-1, max-video-preview:-1" />',
        '<meta property="og:image:width" content="1200" />',
        '<meta property="og:image:height" content="630" />',
        f'<meta property="og:image:alt" content="{esc(title)}" />',
        f'<meta name="twitter:image:alt" content="{esc(title)}" />',
        '<link rel="icon" href="/favicon.svg" type="image/svg+xml" />',
        '<link rel="icon" href="/favicon.ico" sizes="32x32" />',
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png" />',
        '<link rel="manifest" href="/site.webmanifest" />',
        '<link rel="preconnect" href="https://images.unsplash.com" crossorigin />',
        '<link rel="preconnect" href="https://static.wixstatic.com" crossorigin />',
        '<link rel="dns-prefetch" href="https://static.wixstatic.com" />',
    ]

    # The old page-level robots tag would otherwise contradict the one above.
    txt = re.sub(r'\s*<meta name="robots" content="index, follow" />', "", txt)

    # The Google Fonts stylesheet is render-blocking: nothing paints until it
    # lands. Loading it as media="print" and flipping to "all" on load takes it
    # off the critical path. The URL already carries display=swap, so text was
    # always going to paint in the fallback face first — this just stops the
    # whole page waiting on the request. The <noscript> copy keeps fonts
    # working with scripting off, where the onload flip never runs.
    #
    # Normalise first. The deferred tag no longer ends in `rel="stylesheet" />`,
    # so a naive second pass skips it and re-defers the plain copy inside the
    # <noscript> instead, nesting one wrapper per run.
    txt = re.sub(r'\s*<noscript><link href="https://fonts\.googleapis\.com[^>]*></noscript>',
                 "", txt)
    txt = txt.replace(' media="print" onload="this.media=\'all\';this.onload=null" />',
                      ' />')

    m = re.search(r'<link href="https://fonts\.googleapis\.com[^>]*rel="stylesheet" />', txt)
    if m:
        plain = m.group(0)
        deferred = plain.replace(
            ' rel="stylesheet" />',
            ' rel="stylesheet" media="print" onload="this.media=\'all\';this.onload=null" />')
        txt = txt.replace(plain, deferred + "\n  <noscript>" + plain + "</noscript>", 1)

    # Organization + WebSite — the two nodes every page anchors to by @id.
    head_bits.append(jsonld(organization(url)))
    head_bits.append(jsonld(website_schema()))

    # BreadcrumbList — replace whatever was there so positions stay correct.
    crumb = build_breadcrumb(kind, slug, txt, url)
    if crumb:
        txt = strip_schema(txt, {"BreadcrumbList"})
        head_bits.append(jsonld(crumb))

    # FAQPage — visible copy and markup always come from the same source, so
    # the two can never drift. Pages the build writes an FAQ block for use the
    # generated set; pages that already display their own accordion have their
    # schema scraped back off the page instead.
    faqs = get_faqs(kind, slug, txt)
    scraped = None if faqs else scrape_visible_faq(txt)

    if faqs or scraped:
        # Drop any pre-existing FAQPage so the page declares exactly one.
        txt = strip_schema(txt, {"FAQPage"})
        head_bits.append(jsonld(faq_schema(faqs or scraped)))

    if kind == "blog-post" and slug in BLOG_POSTS:
        txt = strip_schema(txt, {"BlogPosting", "Article", "NewsArticle"})
        head_bits.append(jsonld(blogposting(slug, txt, url)))

    if kind == "service" and slug in SERVICES:
        txt = strip_schema(txt, {"Service"})
        head_bits.append(jsonld(service_schema(slug, url)))

    # Reviews and the team roster are lifted off the rendered page, so the
    # markup can never claim testimonials the page does not actually show.
    txt = strip_schema(txt, {"ItemList"})
    if slug == "reviews":
        rv = reviews_schema(txt, url)
        if rv:
            head_bits.append(jsonld(rv))
    if slug == "meet-the-team":
        tl = team_list_schema(txt, url)
        if tl:
            head_bits.append(jsonld(tl))

    # The legacy per-page HairSalon nodes are superseded by the single
    # Organization emitted above — the group serves the greater Pittsburgh
    # area rather than trading as one storefront, which is what LocalBusiness
    # asserts. Dropping them also avoids two conflicting Organizations sharing
    # a page. The Person node for Derek is deliberately left in place.
    # Earlier revisions of this script retyped those nodes to Organization in
    # place rather than removing them, so some pages carry a second, @id-less
    # Organization. Anything that is not the canonical node goes too.
    txt = strip_schema(txt, {"HairSalon", "LocalBusiness", "BeautySalon"})
    txt = strip_schema(
        txt, {"Organization"},
        keep=lambda n: n.get("@id") == f"{SITE}/#organization")

    head_html = marker("head", "\n  " + "\n  ".join(head_bits) + "\n  ")
    txt = txt.replace("</head>", head_html + "\n</head>", 1)

    # ---- 3. body ----------------------------------------------------------

    # Inline colour overrides were written for the dark theme. An inline style
    # attribute outranks every stylesheet rule, so these have to be rewritten
    # rather than overridden — but only inside the body, never inside <style>,
    # where the same declarations are load-bearing for the nav and footer.
    head_part, sep, body_part = txt.partition("</head>")

    # Stale authoring comment: the markup it labels is an Organization graph now.
    head_part = head_part.replace(
        "<!-- Schema: LocalBusiness (both locations) -->",
        "<!-- Schema: Organization (serves the greater Pittsburgh area) -->")

    inline_fixes = [
        # Light-on-dark headings that now sit on a light band.
        (r'\s*style="color:var\(--off-white\)"', ""),
        (r'style="font-style:italic;color:var\(--off-white\);"', 'style="font-style:italic"'),
        (r'color:var\(--off-white\);', ""),
        (r'color:rgba\(247,244,239,0\.55\);', "color:var(--mid);"),
        (r'style="color:var\(--black\);opacity:0\.4"', 'style="opacity:0.55"'),
        # Two full-bleed panels that were painted near-black inline.
        (r'style="background:var\(--black\);padding:5rem 4rem;text-align:center;"',
         'style="background:var(--cream);padding:5rem 4rem;text-align:center;"'),
        # Two bare <section>s carried a gold CTA band entirely inline, so none
        # of the .cta-section theming reached them. Giving them the class does,
        # and the inline background comes off so the class can own the ground.
        (r'<section style="background:var\(--gold\);padding:5rem 4rem;text-align:center;">',
         '<section class="cta-section">'),
        # Any other inline gold ground has to name --gold-fill explicitly now
        # that --gold is the text-safe mix, or it renders dark-on-dark.
        (r'background:var\(--gold\);', "background:var(--gold-fill);"),
        # 0.6-alpha ink on a gold ground is 2.4:1. 0.82 takes it to 4.6:1.
        (r'color:rgba\(14,\s*13,\s*11,\s*0\.6\);', "color:rgba(23,21,15,0.82);"),
    ]

    for pat, rep in inline_fixes:
        body_part = re.sub(pat, rep, body_part)

    body_part = body_part.replace(
        'style="color:var(--off-white);text-decoration:none;font-size:0.75rem;letter-spacing:0.1em;'
        'text-transform:uppercase;font-weight:400;border-bottom:1px solid rgba(247,244,239,0.3);padding-bottom:2px;"',
        'class="btn-ghost"')

    # Inside the footer the ground is near-black, so the text-safe gold mix
    # inverts: an inline `color: var(--gold)` there measures 3.5:1. Scoped to
    # the footer element so the light-surface uses above are left alone.
    fm = re.search(r"<footer\b", body_part)
    if fm:
        head_of_body, foot = body_part[: fm.start()], body_part[fm.start():]
        foot = re.sub(r"(style=\"[^\"]*?)var\(--gold\)", r"\1var(--gold-light)", foot)
        body_part = head_of_body + foot

    txt = head_part + sep + body_part

    # Three footer links pointed at /hair-services-pittsburgh/<x> pages that
    # were never built — dead ends on every one of the 90 pages. Those services
    # already have full sections, with pricing, on the services page, so the
    # links are re-pointed at anchors there rather than answered with three
    # thin pages duplicating that content.
    for slug_, anchor in (("nails-pittsburgh", "nails"),
                          ("skin-care-facials-pittsburgh", "skin-care"),
                          ("lash-extensions-pittsburgh", "lash-extensions")):
        txt = txt.replace(f'href="/hair-services-pittsburgh/{slug_}"',
                          f'href="/hair-services-pittsburgh#{anchor}"')

    # ...and give those sections the ids to land on.
    for label, anchor in (("Manicures", "nails"),
                          ("Facials", "skin-care"),
                          ("Lash Extensions", "lash-extensions")):
        # Match on the leading word only: the headings carry a bare "&" rather
        # than "&amp;", and matching the full string missed two of the three.
        txt = re.sub(
            rf'<div class="services-category"(?! id=)>(\s*<p class="category-label">[^<]*</p>\s*'
            rf'<h2 class="category-title">{re.escape(label)}[^<]*</h2>)',
            rf'<div class="services-category" id="{anchor}">\1', txt, count=1)

    # Mark the nav item for the section being viewed. Without it a screen
    # reader gets eight identical links with no indication of position, and
    # sighted users get no active state either.
    nav_for = {
        "service": "/hair-services-pittsburgh",
        "location": "/locations/north-hills-pittsburgh",
        "stylist": "/meet-the-team",
        "blog-post": "/blog",
        "blog-index": "/blog",
    }.get(kind) or {
        "hair-services-pittsburgh": "/hair-services-pittsburgh",
        "hair-salon-gallery-pittsburgh": "/hair-salon-gallery-pittsburgh",
        "derek-piekarski": "/derek-piekarski",
        "meet-the-team": "/meet-the-team",
        "reviews": "/reviews",
    }.get(slug)

    txt = re.sub(r'\s+aria-current="page"', "", txt)
    if nav_for:
        txt = re.sub(
            rf'(<li><a href="{re.escape(nav_for)}")(?![^>]*aria-current)',
            r'\1 aria-current="page"', txt, count=1)
    elif kind == "home":
        txt = txt.replace('<a href="/" class="nav-logo"',
                          '<a href="/" class="nav-logo" aria-current="page"', 1)

    # Skip link — first focusable element on the page.
    txt = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + "\n  " + marker("skip", SKIP_LINK),
                 txt, count=1)

    # The hero is both the skip-link target and the anchor the trust strip
    # hangs off, so locate it once.
    hero = find_hero(txt)

    if hero and 'id="main"' not in txt:
        open_start, open_end, close_end = hero
        txt = txt[:open_end - 1] + ' id="main"' + txt[open_end - 1:]
        close_end += len(' id="main"')
        hero = (open_start, open_end, close_end)

    # ---- imagery ----------------------------------------------------------

    # Nine service pages and twenty location pages had no image at all. Each
    # gets a full-bleed shot under the masthead; service pages also get a
    # three-up of that specific service, because "balayage" is a thing people
    # want to see before they book it.
    art = None
    if kind == "service" and slug in SERVICE_ART:
        art = SERVICE_ART[slug][:2]
    elif kind == "location":
        i = sorted(AREAS).index(slug) % len(AREA_ART) if slug in AREAS else 0
        src, alt = AREA_ART[i]
        art = (src, alt.format(AREAS.get(slug, (slug, None))[0]))
    elif kind == "blog-post" and slug in BLOG_ART:
        art = BLOG_ART[slug]
    elif slug in PAGE_ART:
        art = PAGE_ART[slug]

    if art and hero:
        cls = "blog-hero-img" if kind == "blog-post" else "loc-hero-img"
        chunk = marker("art", hero_media(*art, cls=cls))
        cut = hero[2]
        txt = txt[:cut] + "\n" + chunk + txt[cut:]
        hero = (hero[0], hero[1], cut + len(chunk) + 1)

    # Trust strip: social proof immediately after the hero, where it backs up
    # the claim the hero just made. Above the hero it would only push the
    # headline and the Book button below the fold.
    if hero and (kind in ("home", "service", "location") or slug in (
            "book", "reviews", "about-pittsburgh-hair-salon", "meet-the-team",
            "hair-services-pittsburgh", "derek-piekarski")):
        cut = hero[2]
        txt = txt[:cut] + "\n" + marker("trust", TRUST_BAR) + txt[cut:]

    # FAQ block + cross-links, inserted ahead of the closing CTA / footer.
    tail = ""
    if kind == "service" and slug in SERVICE_ART:
        tail += marker("work", service_shots(SERVICE_ART[slug][2], SERVICES[slug]))
    if faqs:
        tail += marker("faq", faq_html(faqs))
    xl_heading, xl_pairs = get_xlinks(kind, slug)
    tail += marker("xlinks", xlinks_html(xl_pairs, xl_heading))

    if tail:
        for anchor_re in (r'\n\s*<div class="book-cta"', r'\n\s*<section class="book-cta"',
                          r'\n\s*<section class="cta-section"', r'\n\s*<div class="cta-section"',
                          r"\n\s*<footer"):
            m = re.search(anchor_re, txt)
            if m:
                txt = txt[:m.start()] + "\n" + tail + txt[m.start():]
                break

    # Three pages carry their own inline accordion script. On /faq/ the first
    # tap after load did nothing at all — the handler is registered per
    # question AND the same code runs again, so the first click toggled open
    # and straight back closed. Rather than work around a duplicate listener,
    # the inline handlers come out and assets/site.js owns every accordion on
    # the site, which also gives these pages the independent-toggle behaviour
    # and the max-height fix the generated blocks already have.
    txt = re.sub(
        r'[ \t]*<script>(?:(?!</script>).)*?\.faq-question(?:(?!</script>).)*?</script>[ \t]*\n?',
        "", txt, flags=re.S)

    # Sticky call/book bar.
    txt = txt.replace("</body>", marker("cta", CTA_BAR) + "\n</body>", 1)

    # Images last, so the pipeline also covers everything injected above.
    txt, preload = process_images(txt)

    if preload:
        psrc, pset, psizes = preload
        link = (f'<link rel="preload" as="image" href="{psrc}"'
                + (f' imagesrcset="{pset}"' if pset else "")
                + (f' imagesizes="{psizes}"' if psizes else "")
                + ' fetchpriority="high" />')
        # Must sit inside the marker block so a re-run replaces rather than
        # appends it.
        txt = txt.replace("<!-- /cc:head -->", "  " + link + "\n  <!-- /cc:head -->", 1)

    if txt != orig:
        open(full, "w", encoding="utf-8").write(txt)
        return True
    return False


# ---------------------------------------------------------------------------
# sitemap
# ---------------------------------------------------------------------------

def build_sitemap(paths):
    today = date.today().isoformat()

    def entry(path):
        u = page_url(path)
        kind, slug = classify(path)
        pri, freq = {
            "home": ("1.0", "weekly"),
            "service": ("0.9", "monthly"),
            "location": ("0.8", "monthly"),
            "blog-post": ("0.7", "monthly"),
            "blog-index": ("0.7", "weekly"),
            "stylist": ("0.6", "monthly"),
        }.get(kind, ("0.7", "monthly"))
        if slug in ("book", "hair-services-pittsburgh", "derek-piekarski"):
            pri, freq = "0.9", "monthly"
        if slug in ("reviews", "meet-the-team", "hair-salon-gallery-pittsburgh"):
            pri = "0.8"
        return (f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n"
                f"    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n  </url>")

    order = {"home": 0, "service": 1, "location": 2, "page": 3, "blog-index": 4,
             "blog-post": 5, "stylist": 6}
    paths = sorted(paths, key=lambda p: (order.get(classify(p)[0], 9), p))

    body = "\n".join(entry(p) for p in paths)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{body}\n</urlset>\n")


def main():
    # 404.html is hand-authored and must stay noindex and out of the sitemap;
    # the head block this script injects would overwrite both.
    paths = sorted(
        p for p in glob.glob("**/*.html", recursive=True)
        if "_audit" not in p and ".git" not in p and p != "404.html"
    )
    changed = sum(process(p) for p in paths)
    print(f"processed {len(paths)} pages, {changed} rewritten")

    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(build_sitemap(paths))
    print(f"sitemap.xml: {len(paths)} urls")


if __name__ == "__main__":
    os.chdir(ROOT)
    main()
