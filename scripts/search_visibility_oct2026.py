"""Focused GSC-led improvements. Preserve URLs, article bodies and booking links."""
from pathlib import Path
import re, json, html

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://www.craftcollectivesalongroup.com'
DATE = '2026-10-08'
BOOK = 'https://phorest.com/book/salons/craftcollectivesalongroup'

# Short snippets answer the search intent rather than truncating the first paragraph.
POSTS = {
 'why-your-hair-looks-flat-at-the-roots-but-puffy-at-the-ends': (
  'Hair Flat on Top and Puffy at the Ends? Causes and Fixes',
  'Learn why roots go flat while ends look puffy, plus practical changes to product placement, styling and haircut shape that can restore balance.',
  'Flat roots and puffy ends can need different care. Keep heavy conditioner away from the scalp, use lighter products at the roots, and ask your stylist whether the ends need moisture or a change in shape.',
  '/services/haircuts-pittsburgh', 'haircuts and shaping in Pittsburgh',
  'Bring a photo of your hair on a typical day so your stylist can discuss shape, weight and your home styling routine.'),
 'why-your-hair-feels-thinner-even-when-you-haven-t-lost-density-and-how-to-restore-fullness': (
  'Hair Feels Thinner but Is Not Falling Out? What to Check',
  'Hair can feel less full because of length, buildup, styling or breakage. Learn what to discuss with your stylist and when to seek medical advice.',
  'Less volume does not always mean fewer hairs. Length, product buildup and styling can change how full hair feels. New shedding, visible scalp changes or persistent thinning should be assessed by a healthcare professional.',
  '/services/haircuts-pittsburgh', 'Pittsburgh haircut consultations',
  'Ask about a shape that suits your existing density and daily routine. A salon consultation addresses styling and appearance, not the medical cause of hair loss.'),
 'why-your-hair-looks-healthier-right-after-a-trim-and-how-to-keep-that-freshly-cut-look-longer': (
  'Why Hair Looks Healthier After a Trim and How to Keep It',
  'Find out why a trim makes ends look smoother and fuller, and how gentle styling and a maintenance plan help preserve that freshly cut appearance.',
  'A trim removes worn ends and refines the outline of your haircut, which can make hair look smoother and fuller. Gentle detangling and a maintenance schedule suited to your hair help preserve the result.',
  '/services/haircuts-pittsburgh', 'precision haircuts in Pittsburgh',
  'Discuss how much length you want to keep and how the cut should look between salon visits.'),
 'why-your-hair-looks-different-after-you-sleep-and-how-to-fix-morning-texture': (
  'Hair Flat or Frizzy After Sleeping? Fix Morning Texture',
  'Learn why sleep changes your hair shape and how to refresh flat roots, frizz and uneven waves without starting your whole styling routine again.',
  'Pressure, friction and sleeping on damp hair can change your style overnight. Let hair dry before bed, avoid tight styles, and refresh only the areas that need attention in the morning.',
  '/services/blowout-pittsburgh', 'Pittsburgh blowouts and styling',
  'Ask your stylist to show you how to refresh your finished style at home, including the roots and your natural wave pattern.'),
 'why-your-hair-color-fades-faster-at-the-ends-and-how-to-maintain-even-tone-from-root-to-tip': (
  'Hair Color Fading at the Ends? How to Keep an Even Tone',
  'Understand why porous ends can lose color faster, and how a tailored color plan, gentle washing and heat care help maintain a more even tone.',
  'Older, more porous ends may retain color differently from the roots. Ask your colorist about your hair history, washing routine and whether a gloss or adjusted color formula fits your goal.',
  '/services/hair-color-pittsburgh', 'hair color and gloss services in Pittsburgh',
  'Bring a photo of your color just after the appointment and another showing how it fades. Your colorist can use that comparison to plan upkeep.'),
 'why-your-hair-feels-dry-even-when-you-use-hydrating-products-and-how-to-fix-moisture-imbalance': (
  'Hair Still Feels Dry After Conditioning? What to Check',
  'Explore why hair may feel dry despite conditioning, including buildup, damage and product mismatch, and what to ask your stylist before changing products.',
  'Dry-feeling hair can reflect several issues, including wear, product buildup or a routine that does not suit your texture. Adding more conditioner is not always the answer; start by reviewing your routine.',
  '/hair-services-pittsburgh', 'Pittsburgh hair services and treatments',
  'Bring the names of the products you use and explain your heat routine so the stylist can help you choose an appropriate next step.'),
 'from-gym-to-chair-how-to-protect-your-hair-from-sweat-and-daily-workouts': (
  'Sweat and Hair Care: Protect Your Style After Workouts',
  'Plan a workout hair routine with gentle ties, scalp care and sensible washing. Learn how to refresh your style without excessive heat or tension.',
  'A useful workout routine balances scalp comfort with gentle handling. Avoid overly tight ties, let damp hair dry, and adjust cleansing to your scalp and activity rather than a rigid schedule.',
  '/services/blowout-pittsburgh', 'blowouts and styling in Pittsburgh',
  'Tell your stylist how often you exercise so your finished style and home routine fit your week.'),
 'the-best-salons-in-pittsburgh-for-curly-hair-and-textured-hair': (
  'Curly Hair Salons in Pittsburgh: How to Choose a Stylist',
  'Choosing a curly hair salon in Pittsburgh? Compare texture experience, haircut consultations, maintenance and the questions to ask before booking.',
  'Choose a curly hair stylist by looking at work with a texture similar to yours and asking how the cut will behave in your daily routine. Confirm the stylist, service and preparation instructions before booking.',
  '/services/haircuts-pittsburgh', 'Pittsburgh haircuts and curl consultations',
  'Call 724-514-7231 for help choosing a stylist for your curl pattern. Bring inspiration photos and describe how you usually wear your hair.'),
 'the-best-men-s-hair-salons-and-grooming-options-in-pittsburgh': (
  "Men's Hair Salons in Pittsburgh: Find Your Next Haircut",
  "Compare men's hair salons in Pittsburgh by haircut style, consultation and upkeep. Explore Craft Collective and plan a North Hills appointment.",
  'Choose a stylist based on the shape you want, your hair texture and how much styling you prefer at home. Bring front, side and back inspiration photos, then discuss upkeep before the cut begins.',
  '/services/haircuts-pittsburgh', "men's haircuts in Pittsburgh",
  'Book a North Hills haircut online, or call to confirm the stylist and service that best fit your goal.')
}

META = {
 'index.html': ('Hair Salon Pittsburgh | Craft Collective Salon Group', 'Discover Craft Collective in North Hills Pittsburgh and Canonsburg for balayage, highlights, color and haircuts. Book North Hills online or call us.'),
 'services/balayage-pittsburgh/index.html': ('Balayage Pittsburgh | Craft Collective Salon Group', 'Explore balayage at Craft Collective in Pittsburgh. Discuss tone, brightness and upkeep with your colorist. Book North Hills online or call for Canonsburg.'),
 'services/highlights-pittsburgh/index.html': ('Highlights Pittsburgh | Craft Collective Salon Group', 'Plan highlights at Craft Collective in Pittsburgh, from face-framing brightness to dimensional color. Book North Hills online or call for appointment help.'),
 'services/haircuts-pittsburgh/index.html': ('Haircuts Pittsburgh | Craft Collective Salon Group', 'Find your next haircut at Craft Collective in North Hills Pittsburgh. Discuss shape, texture and upkeep with your stylist. Book online or call the salon.'),
 'services/hair-color-pittsburgh/index.html': ('Hair Color Pittsburgh | Craft Collective Salon Group', 'Explore hair color, root touch-ups and glossing at Craft Collective in Pittsburgh. Plan your color and upkeep with a stylist. Book online or call.'),
 'services/keratin-treatment-pittsburgh/index.html': ('Keratin Treatment Pittsburgh | Craft Collective Salon', 'Considering a keratin treatment in Pittsburgh? Discuss frizz, texture, suitability and aftercare at Craft Collective. Book North Hills online or call.'),
 'locations/north-hills-pittsburgh/index.html': ('Hair Salon North Hills Pittsburgh | Craft Collective', 'Visit Craft Collective at 2014D Babcock Blvd in North Hills Pittsburgh for haircuts, balayage and color. Check online availability or call 724-514-7231.'),
 'locations/canonsburg/index.html': ('Hair Salon Canonsburg PA | Craft Collective Salon', 'Visit Craft Collective at 115 W Pike St in Canonsburg for hair services by appointment. Call 724-514-7231 to confirm your stylist, service and appointment.')
}

FAQS = {
 'balayage-pittsburgh': [
  ('How do I choose between balayage and highlights?', 'Bring examples of the brightness and root transition you like. Your colorist can discuss hand-painted placement, foils or a combination based on your starting color and upkeep preferences.'),
  ('How much will my balayage appointment cost?', 'Ask for an estimate after discussing your hair length, density, color history and goal. Confirm which services are included, such as toning, cutting or finishing, before booking.'),
  ('How do I book balayage in North Hills or Canonsburg?', 'Book North Hills online or call 724-514-7231 for help choosing a service. Canonsburg is by appointment; call to confirm availability and your stylist.')],
 'haircuts-pittsburgh': [
  ('Can I discuss a curly or wavy haircut before booking?', 'Yes. Call 724-514-7231 to explain your texture and preferred shape and ask which stylist and service to select. Confirm how to prepare your hair before the appointment.'),
  ("How do I choose a men's haircut appointment?", 'Describe the length, shape and finish you want, and ask which appointment fits that goal. Bring inspiration photos and discuss how much time you want to spend styling at home.'),
  ('Where can I book a Pittsburgh haircut?', 'North Hills appointments can be booked online at 2014D Babcock Blvd, Pittsburgh. For Canonsburg at 115 W Pike St, call 724-514-7231 to schedule.')],
 'keratin-treatment-pittsburgh': [
  ('How is a keratin treatment different from a blowout?', 'A blowout temporarily shapes hair with washing and heat styling. A keratin smoothing service is a separate treatment with its own suitability and aftercare requirements. Ask which result fits your texture and routine.'),
  ('What should I ask before choosing a smoothing treatment?', 'Ask which product will be used, how your hair history affects suitability, what change in texture to expect, and what washing or styling instructions apply afterward. Discuss any sensitivities before the service.'),
  ('Can I get an estimate before booking?', 'Call 724-514-7231 and discuss your length, density and hair history. Confirm the treatment, finishing services, estimated appointment time and price before proceeding.')]
}

def set_meta(t, title, desc):
    t = re.sub(r'<title>.*?</title>', '<title>'+html.escape(title)+'</title>', t, count=1, flags=re.S)
    for attr, key, value in [('name','description',desc),('property','og:title',title),('property','og:description',desc),('name','twitter:title',title),('name','twitter:description',desc)]:
        t = re.sub(r'(<meta '+attr+'="'+key+r'" content=")[^"]*(")', lambda m:m[1]+html.escape(value,quote=True)+m[2],t)
    return t

def update_schema(t, desc=None, content_changed=False, faqs=None):
    def rewrite(m):
        obj=json.loads(m[1])
        def visit(n):
            if isinstance(n,list):
                for v in n:visit(v)
            elif isinstance(n,dict):
                typ=n.get('@type',[]); typ=[typ] if isinstance(typ,str) else typ
                if 'Organization' in typ and n.get('name')=='Craft Collective Salon Group':
                    n.setdefault('logo',{'@type':'ImageObject','url':SITE+'/images/logo.png'})
                if any(x in typ for x in ['BlogPosting','Article']):
                    if desc:n['description']=desc
                    if content_changed:n['dateModified']=DATE
                for v in list(n.values()):visit(v)
        visit(obj)
        indent = 2 if '\n' in m[1] else None
        payload = json.dumps(obj, ensure_ascii=False, indent=indent).replace('</','<\\/')
        if indent:payload='\n'+payload+'\n'
        return '<script type="application/ld+json">'+payload+'</script>'
    t=re.sub(r'<script type="application/ld\+json">(.*?)</script>',rewrite,t,flags=re.S)
    if faqs:
        schema={'@context':'https://schema.org','@type':'FAQPage','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in faqs]}
        t=t.replace('</head>','<script type="application/ld+json">'+json.dumps(schema)+'</script></head>',1)
    return t

def main():
    changed=[]
    for slug,(title,desc,summary,service,label,advice) in POSTS.items():
        rel='post/'+slug+'/index.html';p=ROOT/rel;t=p.read_text()
        t=re.sub(r'<!-- cc:search-answer -->.*?<!-- /cc:search-answer -->','',t,flags=re.S)
        t=re.sub(r'<!-- cc:search-booking -->.*?<!-- /cc:search-booking -->','',t,flags=re.S)
        t=set_meta(t,title,desc)
        answer='<!-- cc:search-answer --><aside class="archive-cta"><h2>Quick answer</h2><p>'+html.escape(summary)+'</p></aside><!-- /cc:search-answer -->'
        t=t.replace('<article class="archive-body">','<article class="archive-body">'+answer,1)
        cta='<aside class="archive-cta"><h2>Get help with your hair in Pittsburgh</h2><p>Explore <a href="'+service+'">'+html.escape(label)+'</a>. '+html.escape(advice)+'</p><p>Visit <a href="/locations/north-hills-pittsburgh">North Hills at 2014D Babcock Blvd</a> or <a href="/locations/canonsburg">Canonsburg at 115 W Pike St</a>.</p><p><a href="'+BOOK+'" target="_blank" rel="noopener noreferrer">Check North Hills availability</a> or call <a href="tel:+17245147231">724-514-7231</a>. Canonsburg is by appointment; call to schedule.</p></aside>'
        t=re.sub(r'<aside class="archive-cta"><h2>Plan your salon visit</h2>.*?</aside>','',t,flags=re.S)
        t=t.replace('</article>','<!-- cc:search-booking -->'+cta+'<!-- /cc:search-booking --></article>',1)
        t=update_schema(t,desc,True)
        p.write_text(t);changed.append(rel)
    for rel,(title,desc) in META.items():
        p=ROOT/rel;t=set_meta(p.read_text(),title,desc)
        slug=p.parent.name;faqs=FAQS.get(slug)
        if faqs:
            t=re.sub(r'<!-- cc:search-faq -->.*?<!-- /cc:search-faq -->','',t,flags=re.S)
            # This focused block owns its FAQ schema and can be regenerated safely.
            t=re.sub(r'<script type="application/ld\+json">[^<]*"@type": "FAQPage"[^<]*</script>','',t)
            faq='<section class="content-section"><div class="content-inner prose"><h2>Before you book</h2>'+''.join('<h3>'+html.escape(q)+'</h3><p>'+html.escape(a)+'</p>' for q,a in faqs)+'<p><a href="'+BOOK+'" target="_blank" rel="noopener noreferrer">Check North Hills availability</a>. For Canonsburg, call <a href="tel:+17245147231">724-514-7231</a>.</p></div></section>'
            t=t.replace('<footer','<!-- cc:search-faq -->'+faq+'<!-- /cc:search-faq --><footer',1)
        t=update_schema(t,faqs=faqs)
        p.write_text(t);changed.append(rel)
    print(json.dumps({'updatedPages':len(changed),'paths':changed}))

if __name__=='__main__':main()
