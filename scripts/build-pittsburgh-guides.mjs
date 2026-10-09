import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {profiles,competitors,slug} from './pittsburgh-guide-profiles.mjs';
import {buildSalonPlanning} from './build-salon-planning.mjs';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const OUT=path.join(ROOT,'dist');
const fingerprint=s=>createHash('sha256').update(s).digest('hex').slice(0,12);
const searchEngine=fs.readFileSync(path.join(ROOT,'scripts/hair-guide-search.mjs'),'utf8');
const searchEngineName=`hair-guide-search.${fingerprint(searchEngine)}.mjs`;
const searchClient=fs.readFileSync(path.join(ROOT,'scripts/pittsburgh-guide-search.js'),'utf8').replace('./hair-guide-search.mjs','./'+searchEngineName);
const searchClientName=`pittsburgh-guide-search.${fingerprint(searchClient)}.js`;
const SITE='https://www.craftcollectivesalongroup.com';
const DATE='2026-10-08';
const MODIFIED='2026-10-09';
const BASE='/pittsburgh-hair-guide';
const esc=t=>String(t).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const p=t=>`<p>${t}</p>`;
const ul=xs=>`<ul>${xs.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`;
const section=(title,body)=>`<section><h2>${esc(title)}</h2>${body}</section>`;
const link=(href,title)=>`<a href="${esc(href)}">${esc(title)}</a>`;
const lower=x=>x.label.toLowerCase();
const serviceFor=x=>{
 if(x.family==='styling'&&x.slug.includes('bridal'))return '/services/bridal-hair-pittsburgh';
 if(x.family==='color'&&/balayage|foilyage/.test(x.slug))return '/services/balayage-pittsburgh';
 if(x.family==='color'&&/highlight|babylight|foil|lowlights/.test(x.slug))return '/services/highlights-pittsburgh';
 return {color:'/services/hair-color-pittsburgh',extensions:'/services/hair-extensions-pittsburgh',styling:'/services/blowout-pittsburgh',treatments:'/services/keratin-treatment-pittsburgh',cuts:'/services/haircuts-pittsburgh',care:'/hair-services-pittsburgh'}[x.family];
};
const familyNames={color:'Color and blonding',extensions:'Hair extensions',styling:'Styling and events',treatments:'Smoothing consultations',cuts:'Haircuts and shapes',care:'Hair care and routines',comparisons:'Service comparisons',salons:'Pittsburgh salon comparisons'};
const records=[];
const bodyByPath=new Map();

// Each intent answers a different decision. The manually authored profile supplies
// the subject-specific definition, tradeoff, consultation question and alternative.
const intents=[
 ['overview','What to Know',x=>`${x.label} in Pittsburgh: What to Know`,x=>
  section(`What ${lower(x)} means`,p(esc(x.definition))+p(esc(x.decision)))+
  section('Turn a reference into a workable plan',p(`For ${esc(lower(x))}, begin with what you want to change about your current hair. Is the goal a different outline, more visible movement, a tonal shift or a routine that takes less effort? Identify the part of a reference photo you actually want before using its caption as an appointment name.`)+p(`Ask your stylist: “${esc(x.question)}” Bring a current photo as well as the desired result. A useful consultation compares the two and explains the steps that fit your starting point.`))+
  section('Compare an alternative',p(`It is also worth discussing ${esc(x.alternative)}. The better choice is the one that fits your preferred appearance and the amount of upkeep you can realistically manage, rather than whichever label is more popular.`))],
 ['cost','Cost and Estimates',x=>`${x.label} Cost in Pittsburgh: What Affects the Quote`,x=>
  section('What determines the estimate',p(`A useful quote for ${esc(lower(x))} names the service components instead of giving only a starting number. ${esc(x.decision)} The time and work needed to reach that plan can differ from the appointment shown in a reference photo.`)+p('Ask the salon to distinguish the main service from cutting, toning, finishing, added hair or other appointment components. The items that apply depend on the service; they should be explained before you agree to the appointment.'))+
  section('Request a quote that matches your goal',p(`Send a clear current photo and describe the result you want from ${esc(lower(x))}. Explain your length, density, relevant hair history and whether you want to retain the present outline. Ask: “${esc(x.question)}” Then confirm what the estimate includes and what could change it.`))+
  section('Compare the full appointment',p(`When comparing ${esc(lower(x))} with ${esc(x.alternative)}, compare an equivalent finished result and the upkeep afterward. A lower opening price may describe a smaller service or omit something you expect. Craft Collective quotes should be confirmed with the salon; this guide does not establish a fixed price.`))],
 ['appointment-time','Appointment Time',x=>`How Long Does ${x.label} Take in Pittsburgh?`,x=>
  section('Plan for the complete visit',p(`The time for ${esc(lower(x))} depends on the actual plan, not just the name in the booking menu. ${esc(x.definition)} Consultation, preparation, the main service and finishing can all contribute to the visit.`)+p(`Tell the salon whether you are maintaining an existing result or changing direction. ${esc(x.decision)} The second situation may need a different appointment from the one you previously booked.`))+
  section('Ask about the schedule before committing',p(`Ask your stylist: “${esc(x.question)}” Then ask which service block accommodates that goal and whether the appointment needs additional time for your length or density. Do not shorten the visit yourself to fit an unrelated calendar opening.`))+
  section('If you have a deadline that day',p(`Mention a fixed departure time before booking ${esc(lower(x))}. Ask whether a smaller first step or ${esc(x.alternative)} would be more practical. Leave room for travel and finishing rather than treating a published service duration as a guaranteed end time.`))],
 ['suitability','Suitability',x=>`Is ${x.label} Right for Your Hair? Pittsburgh Guide`,x=>
  section('Assess the starting point',p(`${esc(x.definition)} Suitability for ${esc(lower(x))} comes from comparing the intended result with your actual hair, hair history and daily routine. A reference on a different texture is an idea to discuss, not a reliable forecast.`)+p(esc(x.decision)))+
  section('Make the tradeoff explicit',p(`Ask: “${esc(x.question)}” Explain what you are willing to change at home and what you want to keep the same. If the result requires daily steps you would not normally do, ask to see a version that better fits your routine.`))+
  section('Use an alternative as a test',p(`Discuss ${esc(x.alternative)} alongside ${esc(lower(x))}. Comparing the two can make the decision clearer: which better preserves the features you like, which changes the features you dislike, and what must happen between salon visits? Confirm the particular stylist and service before booking.`))],
 ['maintenance','Maintenance',x=>`${x.label} Maintenance in Pittsburgh: Plan Your Upkeep`,x=>
  section('Define what you want to maintain',p(`The upkeep for ${esc(lower(x))} depends on which feature matters most to you. ${esc(x.decision)} Someone keeping a precise result may want a different return plan from someone comfortable with a softer transition.`)+p(`${esc(x.definition)} Before the first appointment ends, ask which visible change would be a useful reason to return and which changes are expected as the style evolves.`))+
  section('Separate salon upkeep from home styling',p(`Ask “${esc(x.question)}” and request a simple routine for the finished result. Your stylist should distinguish what you can do at home from work that needs another appointment. Avoid assuming that more products or more heat will preserve the result longer.`))+
  section('Agree on a realistic return plan',p(`Explain how often you can return to a Pittsburgh salon. Compare that schedule with ${esc(x.alternative)} if regular upkeep would be difficult. Ask how to book the next visit and what service name to select, rather than automatically repeating the original appointment.`))],
 ['consultation','Consultation Questions',x=>`${x.label} Consultation Questions for a Pittsburgh Salon`,x=>
  section('Start with the important question',p(`For ${esc(lower(x))}, a useful opening question is: “${esc(x.question)}” ${esc(x.decision)} This turns a trend label into a specific discussion about your result.`))+
  section('Bring the context a stylist needs',p(`Explain how your hair looks on a normal day, what you like about it and what is frustrating. ${esc(x.definition)} Share recent hair history and mention the products or tools you actually use. If something is uncertain, say so rather than filling in details from memory.`))+
  section('Leave with a clear agreement',ul([`What is the first achievable goal for ${lower(x)}?`,`Which appointment name and stylist should I select?`,`What is included in the estimate and finish?`,`How does ${x.alternative} change the plan?`,`What should I do before and after the visit?`])+p('Ask the salon to clarify any term you do not understand. A useful consultation ends with a shared description of the result, not only a list of technical labels.'))],
 ['inspiration-photos','Inspiration Photos',x=>`Photos to Bring for ${x.label} in Pittsburgh`,x=>
  section('Choose photographs for a purpose',p(`For ${esc(lower(x))}, bring a small set of reference photos that share the feature you want. ${esc(x.decision)} Point to the actual outline, placement or finish instead of assuming the salon will interpret the caption the same way.`)+p(esc(x.definition)))+
  section('Add a picture of your current hair',p(`Include your current hair from the front and back in ordinary light. If you usually wear it tied back or air-dried, show that too. Ask: “${esc(x.question)}” Your current photo makes that question easier to answer than a tightly cropped inspiration image alone.`))+
  section('Show an example you do not want',p(`An unwanted result can be just as useful when choosing ${esc(lower(x))}. Explain why it feels too strong, too short, too dark or too difficult to maintain. A comparison with ${esc(x.alternative)} can reveal whether your goal is a different technique or simply a different version of the finish.`))],
 ['first-visit','First Appointment',x=>`Your First ${x.label} Appointment in Pittsburgh`,x=>
  section('Before the first visit',p(`Confirm that the selected appointment fits your goal for ${esc(lower(x))}. ${esc(x.definition)} If the booking menu does not make the choice clear, call the salon before reserving a different service just because it has an opening.`)+p(`Bring a current photo and ask: “${esc(x.question)}” Explain relevant hair history and how much time you normally spend on styling.`))+
  section('At the consultation',p(`${esc(x.decision)} Agree on the first result, the included appointment components and the estimate. Ask which parts can be done in the first visit and whether any decisions need to wait until your hair is assessed in person.`))+
  section('Before you leave',p(`Ask how to maintain the result from ${esc(lower(x))}, what should prompt a follow-up and how to book the next visit. If ${esc(x.alternative)} was discussed, be clear about which plan you actually chose so the aftercare and return instructions match the finished service.`))],
 ['annual-budget','Budgeting for Upkeep',x=>`Budgeting for ${x.label} Upkeep in Pittsburgh`,x=>
  section('Budget beyond the first visit',p(`A budget for ${esc(lower(x))} should cover the first agreed appointment and the maintenance you intend to book afterward. ${esc(x.decision)} The version you choose can change the amount of ongoing work.`)+p('Ask the salon to outline the opening visit, potential refresh appointments and any replacement items or home products that actually apply. Avoid adding every suggested option into the budget before deciding which ones you need.'))+
  section('Compare two practical plans',p(`Discuss ${esc(x.alternative)} as a second plan. Ask how the opening appointment and later upkeep differ from ${esc(lower(x))}. Compare the total across the period you expect to wear the result, not just the first payment.`))+
  section('Keep the estimate specific',p(`Use “${esc(x.question)}” to clarify the result before asking about price. A useful budget is attached to a particular plan, stylist and finish. This guide does not supply a fixed annual cost because individual quotes and return schedules must be confirmed with the salon.`))],
 ['booking','Choosing the Appointment',x=>`How to Book ${x.label} in Pittsburgh`,x=>
  section('Choose the goal before the booking label',p(`${esc(x.definition)} To book ${esc(lower(x))}, explain the finished result and ask which menu item matches it. Similar labels can describe different appointment blocks, especially when a consultation, cutting or finishing is also needed.`))+
  section('Give the salon useful information',p(`Describe your current length, texture and hair history, then explain what should change. ${esc(x.decision)} Ask: “${esc(x.question)}” If you are deciding between ${esc(lower(x))} and ${esc(x.alternative)}, say so before the visit.`))+
  section('Select the actual studio',p('Craft Collective has a North Hills studio at 2014D Babcock Blvd, Pittsburgh, and a Canonsburg studio at 115 W Pike St. North Hills has online booking. Canonsburg is by appointment; call 724-514-7231 to schedule. Confirm the selected stylist, service and location rather than assuming every appointment is available at both studios.'))],
 ['expectations','Setting Expectations',x=>`${x.label} Expectations: A Pittsburgh Consultation Guide`,x=>
  section('Describe the result in ordinary language',p(`For ${esc(lower(x))}, separate what you want to see from the name of the technique. ${esc(x.definition)} Identify the feature that matters most and the part of your current hair you want to retain.`)+p(esc(x.decision)))+
  section('Agree on what happens first',p(`Ask: “${esc(x.question)}” Then ask what can reasonably change at the first appointment. A staged plan, a smaller adjustment or ${esc(x.alternative)} may meet your preferences more comfortably than insisting on every detail of a reference image immediately.`))+
  section('Judge the finish in your usual routine',p(`Ask how ${esc(lower(x))} will look when worn the way you normally wear your hair. A heavily styled photograph can hide differences in natural texture and daily effort. Before leaving, confirm which details are part of the cut or color and which came from the finishing technique.`))],
 ['realistic-goal','Choosing a Realistic Goal',x=>`Planning a Realistic ${x.label} Result in Pittsburgh`,x=>
  section('Identify the change that matters most',p(`A realistic ${esc(lower(x))} plan starts by ranking your goals. ${esc(x.decision)} Is your priority the final appearance, keeping length, reducing daily effort or maintaining a familiar overall look? A single plan may involve compromises among those goals.`))+
  section('Compare the starting point with the reference',p(`${esc(x.definition)} Bring your current photo beside the desired result and ask “${esc(x.question)}” Discuss the differences in length, texture, existing color and styling so the first appointment has a defined purpose.`))+
  section('Consider a smaller first step',p(`If the full ${esc(lower(x))} goal does not fit your starting point, ask which smaller change moves you in the right direction. Compare that option with ${esc(x.alternative)}. Agree on the point at which to reassess rather than treating a gradual plan as an automatic commitment to every future appointment.`))],
 ['choose-a-stylist','Choosing a Stylist',x=>`Choosing a Pittsburgh Stylist for ${x.label}`,x=>
  section('Look for comparable work',p(`When choosing a stylist for ${esc(lower(x))}, look for finished work with a starting point or texture comparable to yours. ${esc(x.definition)} A portfolio can show a visual direction, but it does not replace a conversation about your own hair.`))+
  section('Listen to the consultation',p(`${esc(x.decision)} Ask the stylist “${esc(x.question)}” and listen for an explanation you can follow. The right discussion connects the reference with your current hair, your preferred daily routine and a specific appointment plan.`))+
  section('Compare appointment details',p(`Before choosing between Pittsburgh salons, ask who will provide the service, where the appointment takes place and what the estimate includes. If ${esc(x.alternative)} might be a better fit, ask for that comparison without assuming that the more complex service is automatically the better choice.`))],
 ['home-routine','Your Home Routine',x=>`A Home Routine for ${x.label}: Pittsburgh Planning Guide`,x=>
  section('Build around how you actually wear your hair',p(`The home routine for ${esc(lower(x))} should fit your usual styling habits. ${esc(x.decision)} A result that depends on steps you rarely do may be less useful than a simpler finish.`)+p(esc(x.definition)))+
  section('Ask for a demonstration',p(`Ask your stylist “${esc(x.question)}” and then request the steps that matter most for your finished result. Note where products are applied and which tool movements create the effect. Ask what can be skipped on a lower-effort day rather than copying every salon finishing step.`))+
  section('Review before adding more products',p(`If ${esc(lower(x))} becomes difficult to manage at home, explain the actual problem to the salon. More product, tighter tying or repeated heat may not solve it. Ask whether a routine change, a shape adjustment or ${esc(x.alternative)} fits your daily needs better.`))],
 ['follow-up','When to Contact the Salon',x=>`When to Follow Up About ${x.label} in Pittsburgh`,x=>
  section('Describe the change clearly',p(`If you are concerned about ${esc(lower(x))}, send comparable photographs and explain when the concern became noticeable. ${esc(x.decision)} Distinguish a change in the finish from difficulty reproducing the salon styling at home.`))+
  section('Give the relevant context',p(`${esc(x.definition)} Tell the salon what you have washed with, which tools you have used and whether anything in your routine changed. Ask “${esc(x.question)}” if the original goal is still unclear. This helps the team discuss an appropriate next step without guessing from a short message.`))+
  section('Ask about the next step and policy',p(`Contact the salon before trying to correct ${esc(lower(x))} with an unrelated product or service. Ask whether a consultation, a styling demonstration or a new appointment is appropriate and confirm any adjustment policy directly. Pain, new shedding or scalp concerns should be discussed with a healthcare professional rather than treated as a styling diagnosis.`))],
 ['before-an-event','Before an Event',x=>`Planning ${x.label} Before a Pittsburgh Event`,x=>
  section('Work backward from the event',p(`For ${esc(lower(x))} before an event, explain the event date and whether the look is familiar or a new direction. ${esc(x.decision)} A first-time change may need a different plan from maintaining a result you already wear comfortably.`))+
  section('Show the finished context',p(`Bring the outfit neckline, accessories and the hairstyle you expect to wear. ${esc(x.definition)} Ask “${esc(x.question)}” and explain whether you will be indoors, outdoors or changing styles during the day.`))+
  section('Avoid an assumption about timing',p(`Ask the stylist when to schedule ${esc(lower(x))} and whether a consultation or trial makes sense. There is no single lead time for every goal. Compare ${esc(x.alternative)} if you prefer a smaller change near the event, and confirm whether the finish is included in the planned appointment.`))],
 ['photos-and-finish','Photographs and the Finish',x=>`${x.label} in Photos: Pittsburgh Styling Questions`,x=>
  section('Separate the result from the photography',p(`Photographs of ${esc(lower(x))} can look different with lighting, camera angle and styling. ${esc(x.definition)} Compare references in ordinary light and identify which feature is created by the underlying service.`))+
  section('Ask about your usual finish',p(`${esc(x.decision)} Ask “${esc(x.question)}” while showing how you normally wear your hair. If the reference is curled or heavily finished, ask what the same result looks like straight, tied back or naturally dried.`))+
  section('Use your own comparison photos',p(`Take a photograph in similar light after the appointment and again in your normal routine. This gives the stylist useful context if you want to adjust ${esc(lower(x))} later. Compare ${esc(x.alternative)} only after separating the desired color or shape from the photographic styling.`))],
 ['fine-hair','Fine Hair Considerations',x=>`${x.label} for Fine Hair: Pittsburgh Consultation Guide`,x=>
  section('Describe strands and fullness separately',p(`Fine strands and low overall density are different descriptions. When discussing ${esc(lower(x))}, explain both the feel of individual strands and the appearance of fullness. ${esc(x.decision)}`))+
  section('Preserve the feature you value',p(`${esc(x.definition)} Ask the stylist how the proposed plan affects the appearance of your ends and the way the hair sits at the roots. Use “${esc(x.question)}” to clarify the goal, and say whether keeping a full-looking outline is your priority.`))+
  section('Compare the routine and alternative',p(`Discuss ${esc(x.alternative)} if your reference appears to require much more hair or daily styling than you want. Ask how to manage the finished ${esc(lower(x))} without layering on unnecessary products. If the concern is new thinning or shedding, seek medical assessment rather than assuming a salon service identifies the cause.`))],
 ['dense-hair','Dense Hair Considerations',x=>`${x.label} for Dense Hair: Pittsburgh Planning Guide`,x=>
  section('Identify where the density matters',p(`For ${esc(lower(x))}, a dense head of hair can change the work needed in different sections. Describe where the hair feels heavy and where you want to keep fullness. ${esc(x.decision)}`))+
  section('Ask about the appointment plan',p(`${esc(x.definition)} Ask “${esc(x.question)}” and confirm whether the chosen booking block allows enough time for your length and density. A service name alone may not capture the sectioning, finishing or other work your plan needs.`))+
  section('Compare a manageable finish',p(`Show the way you normally dry and style your hair. Ask how ${esc(lower(x))} can fit that routine and what difference ${esc(x.alternative)} would make. Removing weight or changing the finish should support the desired result rather than being selected automatically because the hair is dense.`))],
 ['natural-texture','Natural Texture',x=>`${x.label} With Natural Texture: Pittsburgh Guide`,x=>
  section('Use your real texture as the starting point',p(`Discuss ${esc(lower(x))} with a current photograph showing the way you naturally wear your hair. ${esc(x.decision)} A smooth or curled inspiration photo may show finishing that changes the apparent shape.`))+
  section('Compare the finished versions',p(`${esc(x.definition)} Ask the stylist “${esc(x.question)}” and compare an air-dried version with a tool-styled version. Explain whether you want to preserve your pattern or change how it looks when finished.`))+
  section('Confirm the stylist and preparation',p(`Ask which stylist and appointment fit the ${esc(lower(x))} goal on your texture. Preparation instructions should come from the selected salon rather than a generic internet rule. Compare ${esc(x.alternative)} if the first plan depends on a finish you would rarely maintain at home.`))],
 ['hair-history','Hair History',x=>`Hair History to Share Before ${x.label} in Pittsburgh`,x=>
  section('Explain the history of the lengths',p(`A consultation for ${esc(lower(x))} is more useful when the stylist knows what has happened to the hair that is still present. ${esc(x.definition)} Include relevant salon services, at-home products and past changes even when they happened many months ago.`))+
  section('Connect history with the goal',p(`${esc(x.decision)} Ask “${esc(x.question)}” and show current pictures without filters. If you do not know the exact product name, tell the stylist that rather than describing an uncertain process as a confirmed fact.`))+
  section('Let the assessment guide the first step',p(`A reference photo cannot establish whether your current hair is ready for the proposed ${esc(lower(x))}. Ask whether an assessment, test or staged approach is appropriate before proceeding. Discuss ${esc(x.alternative)} if it achieves part of the goal with a different commitment.`))],
 ['grow-out','Grow-Out Planning',x=>`${x.label} Grow-Out Questions for a Pittsburgh Stylist`,x=>
  section('Discuss the result after the first day',p(`A grow-out plan for ${esc(lower(x))} should describe how the result changes between visits. ${esc(x.decision)} Agree on which changes you welcome and which would make the style feel less like you.`))+
  section('Keep the goal and growth separate',p(`${esc(x.definition)} Ask “${esc(x.question)}” and explain whether your main aim is retaining length, letting roots develop or moving toward a different shape. A maintenance appointment should not automatically repeat every component of the opening service.`))+
  section('Set a point for reassessment',p(`Ask when to check the ${esc(lower(x))} plan again and what signs would justify a sooner visit. Compare ${esc(x.alternative)} if the expected grow-out conflicts with your preferred routine. Use photos in similar light to show the actual transition rather than relying only on the number of weeks since the appointment.`))],
 ['active-routine','Active Schedules',x=>`${x.label} With an Active Pittsburgh Routine`,x=>
  section('Explain your week before choosing the finish',p(`If workouts, frequent tying back or outdoor activity shape your routine, discuss that before choosing ${esc(lower(x))}. ${esc(x.decision)} The salon finish should be assessed against the way you will actually wear the hair.`))+
  section('Test practical styling needs',p(`${esc(x.definition)} Ask “${esc(x.question)}” and explain whether your hair needs to stay off your face, fit under a hat or be refreshed quickly after exercise. These details help turn a visual goal into a practical appointment plan.`))+
  section('Choose the maintenance you can manage',p(`Ask how to care for the finished ${esc(lower(x))} with gentle handling and a routine suited to your activity. Discuss ${esc(x.alternative)} if it gives you a more workable everyday finish. Avoid planning repeated heat styling as the only way to make the result fit your schedule.`))],
 ['return-appointment','The Next Appointment',x=>`What to Book After ${x.label} in Pittsburgh`,x=>
  section('The next visit may be a different service',p(`After ${esc(lower(x))}, ask what needs refreshing and what can stay unchanged. ${esc(x.decision)} Maintenance can have a different purpose from the first appointment, so repeating the original menu choice may not be the best fit.`))+
  section('Explain what has changed',p(`${esc(x.definition)} Bring a photo of the fresh result and a current photo, then ask “${esc(x.question)}” again if your preferences have changed. Describe the part that still works and the part you want to adjust.`))+
  section('Confirm the goal before booking',p(`Ask which service name, stylist and time block suit the next step for ${esc(lower(x))}. If you want to move toward ${esc(x.alternative)}, mention that before the appointment is booked. Confirm the estimate and location rather than assuming the previous appointment details still apply.`))],
 ['change-the-plan','Changing Your Mind',x=>`Changing Your ${x.label} Plan: Pittsburgh Salon Guide`,x=>
  section('Identify why the plan no longer fits',p(`If you want to change direction from ${esc(lower(x))}, describe what is no longer working: the appearance, the upkeep or the amount of daily styling. ${esc(x.decision)} Keeping those concerns separate helps the stylist discuss a useful next step.`))+
  section('Revisit the starting point',p(`${esc(x.definition)} Ask “${esc(x.question)}” with a new current photo, not only the image used at the original consultation. The hair you have now may need a different plan from the one that made sense previously.`))+
  section('Compare a transition with an immediate change',p(`Discuss ${esc(x.alternative)} and ask which parts can change at the next appointment. If a gradual transition is appropriate, agree on the first decision and a reassessment point. Confirm the new booking details instead of adding a major change to the end of an existing maintenance appointment.`))]
];

const booking=()=>`<aside class="archive-cta"><h2>Plan your Craft Collective visit</h2><p>North Hills: ${link('/locations/north-hills-pittsburgh','2014D Babcock Blvd, Pittsburgh')}. Canonsburg: ${link('/locations/canonsburg','115 W Pike St, Canonsburg')}, by appointment.</p><p>${link('https://phorest.com/book/salons/craftcollectivesalongroup','Check North Hills availability')} or call ${link('tel:+17245147231','724-514-7231')}. Call for Canonsburg scheduling and help choosing the right service or stylist.</p></aside>`;

// Hair-care concerns are questions about routines, not invented bookable services.
const careIntents=[...intents.filter(x=>['overview','consultation','inspiration-photos','expectations','choose-a-stylist','home-routine','follow-up','natural-texture','active-routine'].includes(x[0])),
 ['wash-day','Wash-Day Observations',x=>`${x.label} on Wash Day: Pittsburgh Hair Guide`,x=>
  section('Notice when the concern appears',p(`For ${esc(lower(x))}, compare the way your hair looks before washing, immediately afterward and once it is fully dry. ${esc(x.definition)} These are different points in the routine, so the same description may not identify the same concern at each stage.`)+p(esc(x.decision)))+
  section('Explain the washing steps',p(`Tell the stylist which products you use, where you apply them and how often you normally cleanse. Ask “${esc(x.question)}” and describe the result you want without assuming a specific ingredient or product is the cause.`))+
  section('Change one part of the routine',p(`Ask what to try first for ${esc(lower(x))}. Keep a simple record of how the change affects the appearance or feel instead of changing every product at once. If ${esc(x.alternative)} is relevant, discuss that as a separate decision rather than adding it automatically to the wash-day routine.`))],
 ['product-placement','Product Placement',x=>`Product Placement and ${x.label}: Pittsburgh Guide`,x=>
  section('Describe where products go',p(`When discussing ${esc(lower(x))}, explain what you apply at the roots, through the middle and at the ends. ${esc(x.definition)} A useful routine review separates product choice from the amount and location of the application.`)+p(esc(x.decision)))+
  section('Review overlapping steps',p(`Bring a list of your usual products and the order you use them. Ask “${esc(x.question)}” and explain which step feels necessary and which you added while trying to solve the concern. A simplified routine can make it easier to observe what each step contributes.`))+
  section('Keep the desired result specific',p(`Ask your stylist how product placement fits the actual ${esc(lower(x))} goal. Avoid deciding that a larger quantity will automatically create a better result. If a styling change or ${esc(x.alternative)} is more relevant, clarify that before purchasing another product for the same purpose.`))],
 ['drying','Drying and Styling',x=>`Drying Your Hair With ${x.label}: Pittsburgh Guide`,x=>
  section('Compare the natural and styled results',p(`For ${esc(lower(x))}, explain how the hair looks when air-dried and how it looks after your usual styling method. ${esc(x.decision)} This helps separate the way the hair naturally falls from the effect of the finish.`)+p(esc(x.definition)))+
  section('Describe the method, not only the tool',p(`Tell your stylist how much you handle the hair while drying and which areas receive repeated attention. Ask “${esc(x.question)}” and show a photo of an ordinary day. A tool name alone does not explain the way you use it or the finish you prefer.`))+
  section('Ask for the smallest useful change',p(`Request a demonstration of the step most relevant to ${esc(lower(x))}. Ask whether you can simplify the routine or use a different finish, including ${esc(x.alternative)} when appropriate. A manageable routine should fit your real schedule rather than depend on repeatedly redoing the entire head.`))],
 ['seasonal-routine','Seasonal Routine',x=>`${x.label} in Pittsburgh Seasons: Routine Questions`,x=>
  section('Identify what changed in your routine',p(`If ${esc(lower(x))} becomes more noticeable at a different time of year, compare your actual routine before attributing the change to the weather. Hats, outdoor activity, swimming, washing and indoor styling habits can change together. ${esc(x.definition)}`))+
  section('Keep the concern specific',p(`${esc(x.decision)} Ask “${esc(x.question)}” and explain whether the difference occurs at the roots, in the lengths, at the ends or only after a certain activity. Comparable photographs help show the visible change.`))+
  section('Use a practical seasonal adjustment',p(`Ask your stylist what single adjustment is worth testing for ${esc(lower(x))}. Discuss product placement, handling and the finish before rebuilding the entire routine. Consider ${esc(x.alternative)} only if it suits your preference, and keep checking the result in the same conditions so the comparison is meaningful.`))],
 ['tracking-changes','Track the Change',x=>`How to Track ${x.label} Before a Pittsburgh Salon Visit`,x=>
  section('Create a useful comparison',p(`To discuss ${esc(lower(x))}, take a few photographs in comparable light showing the usual style and the part that concerns you. ${esc(x.definition)} Record when the change appears rather than relying only on a general impression.`))+
  section('Describe the relevant routine',p(`${esc(x.decision)} Note the most recent wash, products used, styling method and any activity that changed the finish. Ask “${esc(x.question)}” with that record available so the consultation can focus on your actual circumstances.`))+
  section('Do not turn the record into a diagnosis',p(`Tracking ${esc(lower(x))} helps explain an appearance or routine concern; it does not establish a medical cause. Ask a stylist which cosmetic or styling change is worth considering, including ${esc(x.alternative)} if appropriate. New shedding, scalp discomfort or persistent skin changes should be discussed with a healthcare professional.`))],
 ['routine-mistakes','Common Routine Mistakes',x=>`${x.label}: Routine Mistakes to Discuss in Pittsburgh`,x=>
  section('Avoid changing everything at once',p(`With ${esc(lower(x))}, changing several products, tools and styling habits at the same time makes it harder to see which step matters. ${esc(x.definition)} Begin by describing the current routine and the specific result you want.`))+
  section('Separate the concern from a guessed solution',p(`${esc(x.decision)} Ask “${esc(x.question)}” before choosing another treatment or purchasing a new product. Explain what you already tried and whether it changed the concern temporarily, made it worse or had no noticeable effect.`))+
  section('Choose a manageable next step',p(`For ${esc(lower(x))}, ask the stylist which one adjustment to test and what result to watch for. Discuss ${esc(x.alternative)} as an option rather than a guaranteed fix. A routine should fit your hair and schedule; a popular technique or a larger number of products does not automatically make it more effective.`))]
];

fs.rmSync(OUT,{recursive:true,force:true});
fs.mkdirSync(OUT,{recursive:true});
function copySource(source,destination){
 if(fs.statSync(source).isDirectory()){
  fs.mkdirSync(destination,{recursive:true});
  for(const name of fs.readdirSync(source))copySource(path.join(source,name),path.join(destination,name));
 }else fs.copyFileSync(source,destination);
}
for(const ent of fs.readdirSync(ROOT,{withFileTypes:true})){
 if(['.git','dist','node_modules','.vercel','.codex','scripts'].includes(ent.name))continue;
 copySource(path.join(ROOT,ent.name),path.join(OUT,ent.name));
}
const template=fs.readFileSync(path.join(ROOT,'guides/first-salon-visit-checklist-pittsburgh/index.html'),'utf8');
if(!template.includes('<article class="archive-body">'))throw Error('Guide template missing');

function save(route,title,description,body,{family='color',article=true,keywords=[],parent=BASE}={}){
 const url=SITE+route;
 let seoTitle=title;
 for(const [from,to] of [['Complete Planning Guide','Guide'],['Pittsburgh Consultation Guide','Pittsburgh'],['Pittsburgh Planning Guide','Pittsburgh'],['Pittsburgh Styling Questions','Pittsburgh'],['Maintenance Questions','Upkeep'],['Cost Questions','Cost'],['Hand-tied weft extensions','Hand-Tied Extensions'],['Keratin-bond extensions','Bond Extensions'],['Keratin smoothing consultation','Keratin Smoothing'],['Blonde-to-brunette transition','Blonde to Brunette'],['Dark-to-light color transition','Dark to Light'],['Coily-hair haircut consultation','Coily Haircuts'],['Changing Your ','Changing '],['Planning a Realistic ','Planning ']]){
  if(seoTitle.length>70)seoTitle=seoTitle.replace(from,to);
 }
 // A search title may be longer for a genuinely specific comparison; never cut
 // away a comparison participant merely to satisfy a character-count target.
 if(description.length>165)description=`${familyNames[family]||'Hair'} guide for a Pittsburgh salon visit: consultation questions, practical choices and appointment planning.`;
 let t=template.replace(/<title>.*?<\/title>/s,`<title>${esc(seoTitle)}</title>`);
 for(const [attr,key,value] of [['name','description',description],['property','og:title',title],['property','og:description',description],['property','og:url',url],['name','twitter:title',title],['name','twitter:description',description]]){
  t=t.replace(new RegExp(`(<meta ${attr}="${key}" content=")[^"]*(")`),(_,a,b)=>a+esc(value)+b);
 }
 t=t.replace(/(<link rel="canonical" href=")[^"]*(")/,(_,a,b)=>a+url+b);
 t=t.replace(/<header class="archive-hero">.*?<\/header>/s,`<header class="archive-hero"><nav aria-label="Breadcrumb">${link('/','Home')} / ${link(BASE,'Pittsburgh hair guide')}${parent!==BASE?' / '+link(parent,'Topic guide'):''}</nav><h1>${esc(title)}</h1><p class="archive-meta">Craft Collective Salon Group · Updated October 9, 2026</p></header>`);
 t=t.replace(/<article class="archive-body">.*?<\/article>/s,`<article class="archive-body">${body}${booking()}</article>`);
 const org={'@type':'Organization','@id':SITE+'/#organization',name:'Craft Collective Salon Group',url:SITE,logo:{'@type':'ImageObject',url:SITE+'/images/logo.png'}};
 const schema={'@context':'https://schema.org','@graph':[org,{'@type':article?'Article':'CollectionPage','@id':url,url,name:title,...(article?{headline:title,datePublished:DATE,dateModified:MODIFIED,author:{'@id':SITE+'/#organization'},publisher:{'@id':SITE+'/#organization'},mainEntityOfPage:url}:{}),description},{'@type':'BreadcrumbList',itemListElement:[{'@type':'ListItem',position:1,name:'Home',item:SITE+'/'},{'@type':'ListItem',position:2,name:'Pittsburgh hair guide',item:SITE+BASE},...(parent!==BASE?[{'@type':'ListItem',position:3,name:'Topic guide',item:SITE+parent}]:[]),...(route===BASE?[]:[{'@type':'ListItem',position:parent===BASE?3:4,name:title,item:url}])]}]};
 t=t.replace(/<script type="application\/ld\+json">.*?<\/script>/gs,'');
 t=t.replace('</head>',`<link rel="stylesheet" href="/assets/pittsburgh-guides.css"><script type="application/ld+json">${JSON.stringify(schema).replaceAll('</','<\\/')}</script></head>`);
 const file=path.join(OUT,route,'index.html');fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,t);
 bodyByPath.set(route,body);
 if(article)records.push({path:route,title,searchTitle:seoTitle,primaryKeyword:keywords[0],relatedKeywords:keywords.slice(1),family,wordCount:body.replace(/<[^>]*>/g,' ').split(/\s+/).filter(Boolean).length});
}

for(const x of profiles){
 const count=x.family==='care'?15:x.family==='cuts'?20:25;
 const selectedIntents=x.family==='care'?careIntents:intents.slice(0,count);
 const topicRoute=`${BASE}/${x.family}/${x.slug}`;
 const pages=[];
 for(const [intent,label,titleFn,bodyFn] of selectedIntents){
  const route=topicRoute+'/'+intent;const title=titleFn(x);
  const desc=`${x.label} in Pittsburgh: ${label.toLowerCase()}, practical consultation questions and appointment planning for your hair and routine.`;
  const keywords=[`${lower(x)} ${label.toLowerCase()} pittsburgh`,`${lower(x)} ${label.toLowerCase()} north hills pittsburgh`,`${lower(x)} ${label.toLowerCase()} canonsburg`,`${lower(x)} salon questions pittsburgh`];
  const intro=p(`This guide focuses on ${esc(label.toLowerCase())} for ${esc(lower(x))}. Use it to prepare a specific salon conversation, then confirm the plan with the stylist who assesses your hair.`);
  const table=`<div class="comparison-scroll"><table><thead><tr><th>Decision</th><th>What to clarify for ${esc(lower(x))}</th></tr></thead><tbody><tr><td>Goal</td><td>${esc(x.decision)}</td></tr><tr><td>Key question</td><td>${esc(x.question)}</td></tr><tr><td>Alternative</td><td>Discuss ${esc(x.alternative)} and the difference in the finish.</td></tr></tbody></table></div>`;
  const current=selectedIntents.findIndex(y=>y[0]===intent);
  const related=[-1,1,-2,2].map(offset=>selectedIntents[(current+offset+selectedIntents.length)%selectedIntents.length]).map(y=>link(topicRoute+'/'+y[0],`${x.label}: ${y[1]}`));
  save(route,title,desc,intro+bodyFn(x)+table+section('Related planning guides',p(related.join(' · '))+p(`${link(serviceFor(x),'Explore the related Craft Collective service menu')}. Confirm availability of the specific technique and stylist before booking.`)),{family:x.family,parent:topicRoute,keywords});
  pages.push([route,label]);
 }
 save(topicRoute,`${x.label} in Pittsburgh: Complete Planning Guide`,`Explore ${x.label.toLowerCase()} questions for Pittsburgh salon visits: estimates, styling goals, routine, consultation and booking.`,p(esc(x.definition))+p(esc(x.decision))+section('Choose your question',`<ul class="guide-links">${pages.map(([route,label])=>`<li>${link(route,label)}</li>`).join('')}</ul>`),{family:x.family,article:false});
}

const pairs=[['Balayage','Full foil highlights'],['Partial balayage','Full balayage'],['Babylights','Face-framing highlights'],['Money-piece color','Face-framing highlights'],['Full foil highlights','Partial foil highlights'],['Lowlights','Dimensional brunette'],['Lived-in blonde','Platinum blonde'],['Lived-in brunette','Dimensional brunette'],['Bronde color','Warm blonde color'],['Caramel balayage','Ash blonde color'],['Ash blonde color','Warm blonde color'],['Copper hair color','Auburn hair color'],['Auburn hair color','Red hair color'],['Root touch-up','Gray coverage'],['Gray coverage','Gray blending'],['Gray blending','Gray grow-out'],['Root shadow','Lived-in blonde'],['Hair gloss','Hair toner'],['Color correction','Dark-to-light color transition'],['Blonde-to-brunette transition','Bronde color'],['Tape-in extensions','Hand-tied weft extensions'],['Hand-tied weft extensions','Keratin-bond extensions'],['Extensions for volume','Extensions for length'],['Event blowout','Bridal hair trial'],['Keratin smoothing consultation','Event blowout'],['Blunt bob','Layered bob'],['Long bob','French bob'],['Pixie cut','Long pixie'],['Curtain bangs','Face-framing layers'],['Shag haircut','Long layers']];

for(const [nameA,nameB] of pairs){
 const a=profiles.find(x=>x.label===nameA),b=profiles.find(x=>x.label===nameB);if(!a||!b)throw Error('Missing comparison profile');
 const pair=slug(nameA+' vs '+nameB);
 for(const context of ['choosing','cost','maintenance']){
  const title=`${nameA} vs ${nameB}: ${context==='choosing'?'Pittsburgh Guide':context==='cost'?'Cost Questions':'Maintenance Questions'}`;
  const route=`${BASE}/comparisons/${pair}/${context}`;
  const focus=context==='cost'?'Compare the work included in each quote before comparing the opening totals. Ask which finishing, preparation and upkeep components apply to each proposed plan.':context==='maintenance'?'Compare the home routine and the return appointments needed to keep the feature you value. Two options can suit the same visual goal while requiring different ongoing attention.':'Choose by the finished result, your actual starting hair and the routine you want to maintain. A technique name alone does not determine which option fits you.';
  const comparison=`<div class="comparison-scroll"><table><thead><tr><th>Question</th><th>${esc(nameA)}</th><th>${esc(nameB)}</th></tr></thead><tbody><tr><td>Meaning</td><td>${esc(a.definition)}</td><td>${esc(b.definition)}</td></tr><tr><td>Decision</td><td>${esc(a.decision)}</td><td>${esc(b.decision)}</td></tr><tr><td>Ask your stylist</td><td>${esc(a.question)}</td><td>${esc(b.question)}</td></tr></tbody></table></div>`;
  const body=p(esc(focus))+comparison+section('Use one starting point for both options',p(`Bring the same current photo and explain the feature you want to change when comparing ${esc(lower(a))} with ${esc(lower(b))}. Ask the stylist to describe each option on your actual hair rather than only pointing to a different finished model.`)+p(context==='cost'?'If one estimate includes a cut or finish and another does not, ask for the comparable totals. Also confirm whether the plan is a maintenance appointment or a first-time change. Those are different decisions even if the menu label looks similar.':context==='maintenance'?'Explain how often you are willing to return and how much time you spend styling at home. Ask what changes would be expected between visits and which change would mean it is time for a refresh.':`Describe what you want to preserve as well as what you want to change. The consultation question for ${esc(lower(a))} is “${esc(a.question)}” For ${esc(lower(b))}, ask “${esc(b.question)}”`))+
  section('Agree on an individual recommendation',p(`Neither ${esc(lower(a))} nor ${esc(lower(b))} is automatically the better choice for every person. Ask which plan fits your texture, hair history and desired daily routine. If the two names describe overlapping elements at your salon, ask whether they can be combined or whether a simpler plan meets your goal.`)+p('Before booking, confirm the stylist, the selected service, the estimate and the intended finish. Technique availability must be checked with the salon; this comparison is a decision guide rather than a guarantee that every variation is offered.'))+
  section('Read each topic in detail',p(link(`${BASE}/${a.family}/${a.slug}`,nameA)+' · '+link(`${BASE}/${b.family}/${b.slug}`,nameB)));
  save(route,title,`Compare ${nameA.toLowerCase()} and ${nameB.toLowerCase()} for a Pittsburgh salon visit, with ${context} questions and an individual consultation checklist.`,body,{family:'comparisons',keywords:[`${lower(a)} vs ${lower(b)} ${context} pittsburgh`,`${lower(a)} or ${lower(b)} pittsburgh`,`${lower(a)} vs ${lower(b)} north hills`]});
 }
}

for(const c of competitors){
 const title=`Craft Collective vs ${c.name}: Pittsburgh Salon Guide`;
 const route=`${BASE}/salons/craft-collective-vs-${slug(c.name)}`;
 const body=p(`Compare Craft Collective with ${esc(c.name)} by the specific location, stylist and appointment you would book. This is a salon-published comparison, not an independent ranking or a record of personal visits to the other salon.`)+
 section('What the official information establishes',p(esc(c.fact))+p(`Source: ${link(c.url,c.name+' official website')}. Checked October 8, 2026. Confirm the latest menu and appointment details directly before booking.`)+p('Craft Collective operates a North Hills studio at 2014D Babcock Blvd, Pittsburgh, and a Canonsburg studio at 115 W Pike St. North Hills offers online booking; Canonsburg scheduling is by phone. The right comparison begins with the studio you will actually use.'))+
 section('The decision that matters in this comparison',p(esc(c.focus))+p(`Send the same current photograph and desired result to the salons you are considering. Tell each salon your usual styling routine, relevant hair history and whether you are maintaining a result or making a substantial change. Comparable inputs make the appointment recommendations easier to assess.`))+
 section('Compare equivalent appointments',`<div class="comparison-scroll"><table><thead><tr><th>Item</th><th>Ask both salons</th></tr></thead><tbody><tr><td>Stylist</td><td>Who would perform this service, and can I see work with a similar goal?</td></tr><tr><td>Estimate</td><td>What is included in the quote, and what could change the final total?</td></tr><tr><td>Finish</td><td>Are cutting, toning, styling or other components included when relevant?</td></tr><tr><td>Upkeep</td><td>What home routine and return appointment would you recommend?</td></tr><tr><td>Location</td><td>Which studio provides the particular appointment I am considering?</td></tr></tbody></table></div>`)+
 section('Check policies directly',p(`Ask ${esc(c.name)} and Craft Collective about the current booking, cancellation and adjustment policies before reserving an appointment. Policies, stylist rosters and menu details can change. This guide does not invent a price difference, wait time, quality score or review rating for either business.`))+
 section('Make the choice from the consultation',p('Choose the appointment that offers a clear plan for your hair and a schedule you can maintain. A familiar brand name or a starting price alone cannot tell you how a particular stylist will approach your goal. For Craft Collective, review the service menu, stylist pages and gallery, then call for help selecting a service if the online menu leaves the choice unclear.')+p(link('/hair-services-pittsburgh','Craft Collective service menu')+' · '+link('/meet-the-team','Meet the Craft Collective team')+' · '+link('/hair-salon-gallery-pittsburgh','View the gallery')));
 save(route,title,`Compare Craft Collective and ${c.name} for Pittsburgh hair appointments: official information, location, consultation, estimates and upkeep questions.`,body,{family:'salons',keywords:[`craft collective vs ${c.name.toLowerCase()} pittsburgh`,`${c.name.toLowerCase()} alternatives pittsburgh`,`${c.name.toLowerCase()} salon comparison`]});
}

if(records.length!==2000)throw Error(`Expected 2000 articles, got ${records.length}`);
if(new Set(records.map(x=>x.path)).size!==records.length)throw Error('Duplicate routes');
if(new Set(records.map(x=>x.title)).size!==records.length)throw Error('Duplicate titles');
const families=Object.keys(familyNames);
for(const family of families){
 const group=records.filter(x=>x.family===family);
 const topics=profiles.filter(x=>x.family===family);
 const body=p(`Choose a practical question about ${esc(familyNames[family].toLowerCase())} before a Pittsburgh salon visit. The guides explain what to clarify, how to compare options and how to prepare an individual consultation.`)+
 (topics.length?`<div class="guide-topic-grid">${topics.map(x=>`<section class="archive-cta"><h2>${link(`${BASE}/${x.family}/${x.slug}`,x.label)}</h2><p>${esc(x.definition)}</p></section>`).join('')}</div>`:`<ul class="guide-links">${group.map(x=>`<li>${link(x.path,x.title)}</li>`).join('')}</ul>`);
 save(`${BASE}/${family}`,`${familyNames[family]} in Pittsburgh: Questions and Guides`,`Browse Pittsburgh ${familyNames[family].toLowerCase()} guides and practical questions for choosing your next salon appointment.`,body,{family,article:false});
}
const areaLinks=['north-hills-pittsburgh','canonsburg','wexford','cranberry-township','mccandless','ross-township','shadyside','lawrenceville','squirrel-hill','south-hills','mt-lebanon','hampton-township','fox-chapel'];
const existingAreas=areaLinks.filter(a=>fs.existsSync(path.join(OUT,'locations',a,'index.html')));
const directory=p('Find a focused answer before choosing your next Pittsburgh hair appointment. Browse color, cuts, extensions, styling and home-routine questions, or compare service options and local salons. These are planning guides; confirm a specific service, technique and stylist with the salon.')+
 `<form class="guide-search" role="search" onsubmit="return false"><label for="guide-search">Search hair questions</label><input id="guide-search" type="search" placeholder="Try gray blending, bob, balayage cost…" autocomplete="off" aria-controls="guide-results"><p id="guide-status" role="status" aria-live="polite"></p><ul id="guide-results" class="guide-links"></ul></form>`+
 section('Browse by topic',`<div class="guide-topic-grid">${families.map(f=>`<section class="archive-cta"><h3>${link(BASE+'/'+f,familyNames[f])}</h3><p>${records.filter(x=>x.family===f).length} focused questions and comparisons.</p></section>`).join('')}</div>`)+
 section('Plan the location of your visit',p('Craft Collective has two studios: North Hills Pittsburgh and Canonsburg. The area guides below describe where guests are traveling from; they do not indicate additional Craft Collective storefronts.')+p(existingAreas.map(a=>link('/locations/'+a,a.split('-').map(w=>w[0].toUpperCase()+w.slice(1)).join(' '))).join(' · ')))+
 section('Use the keyword and page map',p(`${link(BASE+'/keyword-map.csv','Download the keyword and page map')}. The map includes editorial search phrases for each page. It does not claim measured search volume, current rankings or that every phrase has been observed in Search Console.`));
save(BASE,'Pittsburgh Hair Guide: Color, Cuts, Care and Comparisons','Explore Pittsburgh hair questions, service comparisons and salon planning guides. Search balayage, haircuts, extensions, styling, maintenance and costs.',directory,{article:false});
const rootPage=path.join(OUT,BASE,'index.html');fs.writeFileSync(rootPage,fs.readFileSync(rootPage,'utf8').replace('</body>',`<script type="module" src="/assets/${searchClientName}"></script></body>`));
fs.writeFileSync(path.join(OUT,'assets/pittsburgh-guides.css'),`.guide-topic-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:1rem}.guide-topic-grid .archive-cta{margin:0}.guide-topic-grid h2,.guide-topic-grid h3{font-size:1.5rem;margin:0 0 .8rem}.guide-search{background:#ede9e1;padding:1.4rem;margin:2rem 0;border-radius:8px}.guide-search label{display:block;font-weight:500;margin-bottom:.5rem}.guide-search input{width:100%;min-height:48px;font:inherit;border:1px solid #765329;background:white;padding:.65rem}.guide-links{padding-left:1.3rem;line-height:1.7}.guide-links li{margin-bottom:.65rem}.archive-body>section{margin:2rem 0}.comparison-scroll table{font-size:.95rem}#guide-results:empty{display:none}`);
fs.writeFileSync(path.join(OUT,'assets',searchEngineName),searchEngine);
fs.writeFileSync(path.join(OUT,'assets',searchClientName),searchClient);
fs.writeFileSync(path.join(OUT,BASE,'search-index.json'),JSON.stringify(records.map(({path,title,primaryKeyword,relatedKeywords})=>({path,title,primaryKeyword,relatedKeywords}))));
const csv=s=>'"'+String(s).replaceAll('"','""')+'"';
fs.writeFileSync(path.join(OUT,BASE,'keyword-map.csv'),'Category,Primary keyword,Related keywords,Page title,URL,Research status\n'+records.map(x=>[familyNames[x.family],x.primaryKeyword,x.relatedKeywords.join('; '),x.title,SITE+x.path,'Editorial topic; search volume not measured'].map(csv).join(',')).join('\n')+'\n');
fs.writeFileSync(path.join(OUT,BASE,'page-manifest.json'),JSON.stringify({created:DATE,articleCount:records.length,keywordStatus:'Editorial coverage, not search-volume estimates',sources:competitors.map(x=>({name:x.name,url:x.url,checked:DATE})),pages:records},null,2));

for(const rel of ['index.html','blog/index.html','hair-services-pittsburgh/index.html']){
 const file=path.join(OUT,rel);let t=fs.readFileSync(file,'utf8');
 if(!t.includes(`href="${BASE}"`))t=t.replace(/(<li><a href="\/pittsburgh-hair-salon-guide-2026"[^>]*>.*?<\/a><\/li>)/,`$1<li>${link(BASE,'Pittsburgh Hair Questions & Comparisons')}</li>`);
 fs.writeFileSync(file,t);
}
const urls=[...bodyByPath.keys()];
fs.writeFileSync(path.join(OUT,'pittsburgh-guides-sitemap.xml'),`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls.map(route=>`<url><loc>${esc(SITE+route)}</loc><lastmod>${MODIFIED}</lastmod></url>`).join('')}</urlset>`);
const sitemapFile=path.join(OUT,'sitemap.xml');let sitemap=fs.readFileSync(sitemapFile,'utf8');
if(!sitemap.includes('/pittsburgh-guides-sitemap.xml'))sitemap=sitemap.replace('</sitemapindex>',`<sitemap><loc>${SITE}/pittsburgh-guides-sitemap.xml</loc><lastmod>${DATE}</lastmod></sitemap></sitemapindex>`);
if(!sitemap.includes('/pittsburgh-guides-sitemap.xml'))throw Error('Root sitemap is not an index');
fs.writeFileSync(sitemapFile,sitemap);
// Validate every generated article and every root-relative link in its content.
for(const r of records){
 const t=fs.readFileSync(path.join(OUT,r.path,'index.html'),'utf8');
 if((t.match(/<h1[ >]/g)||[]).length!==1)throw Error('Invalid H1 '+r.path);
 if(!t.includes(`href="${SITE+r.path}"`))throw Error('Missing canonical '+r.path);
 if(r.wordCount<250)throw Error('Incomplete content '+r.path+' '+r.wordCount);
 for(const m of t.matchAll(/<script type="application\/ld\+json">(.*?)<\/script>/gs))JSON.parse(m[1]);
 for(const m of bodyByPath.get(r.path).matchAll(/href="(\/[^"#?]*)/g)){
  const file=path.join(OUT,m[1]);if(!fs.existsSync(file)&&!fs.existsSync(path.join(file,'index.html')))throw Error('Broken guide link '+r.path+' '+m[1]);
 }
}
console.log(JSON.stringify({articles:records.length,hubPages:urls.length-records.length,families:Object.fromEntries(families.map(f=>[f,records.filter(x=>x.family===f).length])),minimumWords:Math.min(...records.map(x=>x.wordCount)),output:OUT,validated:'unique titles and routes; one H1; canonical; schema; content links; sitemap index'},null,2));
buildSalonPlanning(ROOT,OUT);
