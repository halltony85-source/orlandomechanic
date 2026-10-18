#!/usr/bin/env python3
"""
Orlando's Finest Mobile Mechanic — static site generator (Orlando, FL).
Clickflame playbook: preserve the live slugs (/ and /contact-us), add real
service + city pages, full JSON-LD stack, GitHub -> Netlify deploy.

Rebuild of orlandosfinestmobilemechanics.com (Wix two-pager whose contact
page still carried template filler for an unrelated Clearwater car showroom).

Verified from the live site 2026-08-20:
  phone (407) 490-4147 · orlandosfinestmobilemechanic@gmail.com
  hours Mon-Sat 9:00am-10:00pm, Sun 9:00am-6:00pm
  Square booking link · one real testimonial (Anderson G.)

Design: midnight ink + Florida-sunset orange/gold, Bricolage Grotesque display.

Run:  py -3.12 build.py
"""
import os, shutil, html, json, datetime

# ------------------------------------------------------------------ CONFIG
BIZ        = "Orlando's Finest Mobile Mechanic"
PHONE_DISP = "(407) 490-4147"
PHONE_TEL  = "+14074904147"
EMAIL      = "orlandosfinestmobilemechanic@gmail.com"
DOMAIN     = "https://orlando.mechanicrank.com"
BOOK_URL   = ("https://book.squareup.com/appointments/"
              "fc6fa641-7d56-420a-861e-0717ac9736e9/location/LZRSF4DM05TFV/services")
CITY_MAIN  = "Orlando"
STATE      = "FL"
STATE_FULL = "Florida"
TAGLINE    = "The repair shop that comes to you"
YEAR       = datetime.date.today().year
OUT        = "site"

HOURS_LINE = "Mon to Sat 9am to 10pm, Sun 9am to 6pm"

# IndexNow key (public by design). tools/indexnow.py pings with it after a deploy.
INDEXNOW_KEY = "7a235db8a65242529056b089b9015136"

# GMB — verified live from the Google listing 2026-08-20
RATING    = "4.9"
REVIEW_CT = "35"
GMB_URL   = "https://maps.google.com/?cid=18270203320577713487"
GEO_LAT, GEO_LNG = 28.540337, -81.362329   # listing pin

# ------------------------------------------------------------------ SERVICES
SERVICES = [
    {
        "slug": "mobile-auto-repair",
        "name": "Mobile Auto Repair",
        "short": "Certified mechanics with a fully stocked service vehicle, working in your driveway.",
        "icon": "van",
        "hero": "Auto Repair Without the Repair Shop",
        "intro": "Most of what a shop does in a bay, we do at your curb. {BIZ} sends a certified "
                 "mechanic to your home, your office, or wherever the car quit. With the tools, "
                 "the scan gear, and the parts to handle the job on the spot.",
        "bodies": [
            "Think about what a shop visit actually costs you in Orlando: fighting I-4 both ways, "
            "sitting in a waiting room, maybe paying for a tow before any of that. We cut all of it "
            "out. You tell us where the car is parked and what it's doing, and we come to it. "
            "Apartment complexes, office parks, theme-park employee lots, your own garage. Brakes, "
            "batteries, alternators, starters, belts, sensors, fluids, and the long list of jobs in "
            "between all get done right where the car sits.",
            "Every visit starts the same way: we confirm the actual fault before touching a wrench, "
            "and you approve the price before the work begins. On the rare job that genuinely needs "
            "a lift or specialty machine work, we say so up front and point you somewhere honest "
            "instead of starting a repair we can't finish.",
        ],
        "bullets": [
            "We come to homes, offices, and roadsides across the Orlando metro",
            "Fault confirmed by testing, not guessed from a code",
            "Price agreed before any work starts",
            "Quality parts installed by certified mechanics",
            "Most jobs finished in one visit",
        ],
        "signs": None,
        "faqs": [
            ("Where will you work on my car?",
             "Anywhere it's parked safely and legally. Driveways, apartment lots, office parking, "
             "or the shoulder where it broke down. We just need enough room to work around the vehicle."),
            ("Do I need to be there the whole time?",
             "No. Plenty of customers hand us the key, go back to work, and come out to a fixed car. "
             "We call before we start and when we're done."),
        ],
    },
    {
        "slug": "check-engine-light-diagnostics",
        "name": "Check Engine Light & Diagnostics",
        "short": "A code tells you where to look. Testing tells you what to replace.",
        "icon": "scan",
        "hero": "Check Engine Light On? Find Out Before You Buy Parts.",
        "intro": "The free code read at a parts counter names a circuit, not a part. {BIZ} scans the "
                 "car, then actually tests the sensor, the wiring, and the systems behind the code. "
                 "So the part you pay for is the part that was broken.",
        "bodies": [
            "Here's how people waste money on a check engine light: the reader says the code "
            "mentions an oxygen sensor, so they buy an oxygen sensor. Two weeks later the light is "
            "back, because the real problem was a vacuum leak upstream making the sensor read lean. "
            "A code is a symptom. We run the scan, read live data and freeze-frame, and then do the "
            "physical tests that separate the failed part from the innocent bystander.",
            "When we're done you get the answer in plain English: what's wrong, what it costs to "
            "fix, and whether it's safe to keep driving to work while you decide. If we do the "
            "repair, the diagnostic visit goes toward the bill.",
        ],
        "bullets": [
            "Full OBD-II scan. Stored, pending, and history codes",
            "Live data and freeze-frame analysis",
            "Voltage, pressure, and smoke testing as needed",
            "ABS, airbag, and transmission codes too",
            "Diagnostic fee credited when we do the repair",
        ],
        "signs": [
            ("Steady check engine light", "A fault is stored but the car is usually driveable. "
             "It won't fix itself, and Florida heat tends to make marginal parts worse fast."),
            ("Flashing check engine light", "An active misfire is dumping raw fuel into the "
             "catalytic converter. Pull over and call. A converter costs many times what a misfire does."),
            ("Light on, car feels fine", "Very common with evap-system faults and loose gas caps. "
             "Harmless-feeling, but it will hide any new fault that appears behind it."),
            ("Light came on, then went off", "The fault was intermittent, but the code is still in "
             "memory. We can read it after the light clears and catch the problem early."),
        ],
        "faqs": [
            ("How much does a diagnostic cost?",
             "Call us with the year, make, model, and what the car is doing and we'll quote it "
             "straight. If we do the repair, the diagnostic goes toward the total."),
            ("Can you clear the light so I pass?",
             "Clearing a code without fixing the fault just turns the light back on later. And the "
             "computer remembers. We'd rather find the real problem and fix it once."),
        ],
    },
    {
        "slug": "brake-repair",
        "name": "Brake Repair & Replacement",
        "short": "Pads, rotors, calipers, and fluid. Replaced where the car is parked.",
        "icon": "brake",
        "hero": "Brakes Done in Your Driveway",
        "intro": "Brakes give you warnings long before they become dangerous, and every warning is "
                 "cheaper to fix than the one after it. {BIZ} replaces pads and rotors, services "
                 "calipers, and bleeds fluid at your location. With the old parts shown to you, "
                 "not just described.",
        "bodies": [
            "Stop-and-go on I-4 and the 408 eats brake pads faster than open-road driving ever "
            "will. A squeal at low speed is usually the wear indicator telling you it's time. A "
            "grind means the pad is gone and the rotor is being machined down by bare metal every "
            "time you stop. And a pad-and-rotor job costs real money more than a pad job.",
            "We measure pad and rotor thickness and show you the numbers. If your pads still have "
            "honest life left, we tell you that and put the wheel back on. When work is needed, "
            "you approve the price first, and the old parts come off in front of you.",
        ],
        "bullets": [
            "Front and rear pads and rotors",
            "Caliper, hose, and hardware service",
            "Brake fluid flush and bleed",
            "Parking brake and ABS diagnosis",
            "Pad and rotor measurements shown, not just claimed",
        ],
        "signs": [
            ("Squealing when you brake", "Usually the built-in wear indicator. It's the cheap "
             "warning. Act on it and you save the rotors."),
            ("Grinding under the pedal", "Metal on metal. The rotors are being damaged with every "
             "stop, and the car should be looked at now, not next week."),
            ("Pulling to one side when braking", "Often a sticking caliper or collapsed hose "
             "putting uneven pressure on one wheel. It gets worse, not better."),
            ("Soft pedal that sinks", "Air in the lines, a leak, or a failing master cylinder. "
             "Urgent. Call before driving it again."),
            ("Shudder when slowing from highway speed", "Warped or unevenly worn rotors. Stopping "
             "distance grows with every mile."),
        ],
        "faqs": [
            ("Can you really do rotors in a driveway?",
             "Yes. Pads, rotors, calipers, and bleeding are all standard mobile jobs. We bring the "
             "jack, stands, and torque tools. We just need level ground."),
            ("Do I buy the parts or do you?",
             "Either. Most customers have us bring quality parts matched to the vehicle; if you've "
             "already bought parts, we can usually install them."),
        ],
    },
    {
        "slug": "mobile-oil-change",
        "name": "Mobile Oil Change",
        "short": "The right oil, a new filter, and a health check. At your home or office.",
        "icon": "oil",
        "hero": "An Oil Change That Doesn't Cost You a Saturday",
        "intro": "Oil changes are the cheapest thing you'll ever do for an engine and the easiest "
                 "thing to put off. {BIZ} comes to you with the grade your manufacturer actually "
                 "specifies, conventional, blend, or full synthetic, and hauls the used oil away "
                 "for recycling.",
        "bodies": [
            "Modern engines are picky. Turbocharged and direct-injection motors punish the wrong "
            "viscosity with timing-chain wear and carbon buildup that shows up years later as "
            "someone else's expensive problem. We use what the engine calls for, not what's on "
            "sale, and we torque the drain plug instead of gorilla-tightening it.",
            "Every oil service includes a quick once-over while we're under the hood: fluid "
            "levels, belt condition, visible leaks, air filter, tire pressures, battery voltage. "
            "If something's coming due, we tell you what and how urgent. No upsell theater.",
        ],
        "bullets": [
            "Conventional, synthetic blend, and full synthetic",
            "New filter, correct-torque drain plug",
            "Multi-point check with every change",
            "Fluid top-off and tire pressure set",
            "Used oil collected and recycled properly",
        ],
        "signs": None,
        "faqs": [
            ("How often should I change oil in Florida?",
             "Follow your manufacturer's interval, but know that Orlando duty (short trips, "
             "brutal heat, A/C always on) is 'severe service' in most owner's manuals, which "
             "usually means the shorter interval."),
            ("Do you take the old oil?",
             "Always. It leaves with us and gets recycled. No pans, no mess, no jug of used oil "
             "living in your garage."),
        ],
    },
    {
        "slug": "battery-replacement",
        "name": "Battery Replacement & Testing",
        "short": "Florida heat is the #1 battery killer. We test first, then replace on the spot.",
        "icon": "battery",
        "hero": "Dead Battery? We Test Before We Sell.",
        "intro": "In Florida it isn't winter that kills batteries. It's summer. Heat cooks the "
                 "plates all year, and the battery that cranked fine in May clicks at you in "
                 "August. {BIZ} load-tests the battery, checks the alternator, and looks for a "
                 "parasitic drain before replacing anything.",
        "bodies": [
            "A car that needs a jump has one of three problems: a battery that can't hold charge, "
            "a charging system that isn't refilling it, or something staying on and draining it "
            "overnight. Replacing the battery only fixes the first one. We test all three and show "
            "you the readings, so you don't buy a new battery and have the same dead car next week.",
            "If it is the battery, we install the correct group size on-site, clean the terminals "
            "and grounds, and handle the memory-saver and battery-registration steps that newer "
            "cars need so you don't lose your settings. Then the old battery leaves with us for "
            "recycling.",
        ],
        "bullets": [
            "Battery, alternator, and parasitic-draw testing",
            "Correct replacement carried to you and installed",
            "Terminal, cable, and ground cleaning",
            "Battery registration on vehicles that require it",
            "Old battery hauled off and recycled",
        ],
        "signs": [
            ("Slow, dragging crank", "The starter is turning but the battery can't deliver the "
             "amps. Classic end-of-life battery. Especially after an Orlando summer."),
            ("Rapid clicking at the key", "Not enough current to hold the starter solenoid in. "
             "Usually the battery, sometimes a corroded cable."),
            ("Needs a jump more than once", "A healthy system recharges the battery as you drive. "
             "If it keeps dying, the battery can't hold charge or something is draining it."),
            ("Battery light while driving", "That's the charging system, not the battery. Pull "
             "over soon. The car is running on borrowed electrons."),
        ],
        "faqs": [
            ("How long do batteries last in Orlando?",
             "Around three to four years is typical here. Noticeably shorter than up north, "
             "because heat is harder on a battery than cold. Year four is borrowed time."),
            ("Can you come jump-start me instead?",
             "We can, but a jump without a test is a coin flip. Since we're already there, we test "
             "the battery and charging system so you know whether it will start tomorrow."),
        ],
    },
    {
        "slug": "starter-alternator-repair",
        "name": "Starter & Alternator Replacement",
        "short": "The two parts everyone blames the battery for. Tested and replaced on-site.",
        "icon": "bolt",
        "hero": "Starters and Alternators, Replaced Where the Car Died",
        "intro": "A starter or alternator failure looks a lot like a dead battery. Which is why "
                 "so many people buy a battery first. {BIZ} tests the whole starting and charging "
                 "circuit at your location and replaces the part that actually failed.",
        "bodies": [
            "The nice thing about a bad starter is that the car tells you where it is: it won't "
            "crank, so it isn't going anywhere. Including to a shop. That's precisely the job a "
            "mobile mechanic exists for. We come to the parking spot where it quit, confirm the "
            "starter is the fault (and not a cable, relay, or immobilizer issue), and swap it "
            "right there.",
            "Alternators fail more gradually: dimming lights, a whine that rises with RPM, a "
            "battery warning light, accessories acting possessed. Drive on a dead alternator and "
            "the car runs until the battery is empty, then strands you somewhere worse. We test "
            "output under load, check the belt and connections, and replace the unit if it's done.",
        ],
        "bullets": [
            "Full starting and charging circuit testing",
            "Starter replacement where the vehicle sits",
            "Alternator output tested under real load",
            "Belts, tensioners, and cables checked with it",
            "No tow needed for a car that won't crank",
        ],
        "signs": [
            ("Single loud click, then nothing", "Often the starter solenoid engaging a dead motor. "
             "A test tells us whether it's starter or supply."),
            ("Whirring without the engine turning", "The starter drive is spinning without "
             "engaging the flywheel. The starter is done."),
            ("Lights dim, whine rises with RPM", "Textbook failing alternator. It will strand you "
             "soon. Have it tested now."),
            ("New battery, dead again in days", "The alternator isn't recharging it, or a draw is "
             "emptying it overnight. Either way, testing beats another battery."),
        ],
        "faqs": [
            ("My car won't crank at all. Can you still fix it?",
             "That's our specialty. A car that won't crank can't drive to a shop. We diagnose and "
             "replace starters right in the parking spot where the car gave up."),
        ],
    },
    {
        "slug": "ac-repair",
        "name": "Car A/C Repair",
        "short": "In Orlando, air conditioning is not a luxury. We fix it at your place.",
        "icon": "snow",
        "hero": "Cold Air Is Not Optional in Florida",
        "intro": "Ten months a year, a broken A/C makes a car nearly undriveable here. {BIZ} "
                 "diagnoses weak or warm air at your location. Compressor, condenser fan, "
                 "pressure faults, electrical. And gets cold air blowing again.",
        "bodies": [
            "The most common story we hear is 'it blows cold on the highway but warm at red "
            "lights.' That's rarely low refrigerant. It's usually a condenser fan that isn't "
            "pulling air at idle. Just topping off refrigerant without diagnosis wastes money and "
            "can mask a leak until the compressor runs dry, which turns a small repair into the "
            "most expensive one on the menu.",
            "We check system pressures, watch the compressor engage, test the fans and pressure "
            "switches, and find leaks before adding anything. Then you get the real answer: what "
            "failed, what it costs, and what can wait.",
        ],
        "bullets": [
            "Full A/C system diagnosis, not a blind top-off",
            "Compressor, clutch, and pressure switch testing",
            "Condenser and cooling fan diagnosis",
            "Leak detection before refrigerant goes in",
            "Blend door and airflow electrical faults traced",
        ],
        "signs": [
            ("Cold on the highway, warm in traffic", "Almost always airflow through the condenser. "
             "A fan that quit at idle. Common, and fixable at your curb."),
            ("Blows warm everywhere", "Compressor not engaging, a large leak, or an electrical "
             "fault. Pressures and a scan narrow it down fast."),
            ("A/C clicks on and off rapidly", "Usually low refrigerant short-cycling the "
             "compressor. It's protecting itself. Running it that way kills it."),
            ("Musty smell from the vents", "Moisture living in the evaporator box. Florida "
             "humidity makes this one practically a local tradition."),
        ],
        "faqs": [
            ("Can't I just buy a recharge can?",
             "The parts-store can with the gauge tops up pressure without telling you where the "
             "refrigerant went. If there's a leak, you're renting cold air by the week. And "
             "overfilling can damage the compressor. A proper diagnosis is cheaper than either."),
        ],
    },
    {
        "slug": "no-start-repair",
        "name": "Car Won't Start? On-Site Help",
        "short": "Won't crank, cranks but won't fire, or died in traffic. We come to it.",
        "icon": "key",
        "hero": "The Car Won't Start. Don't Tow It. Diagnose It.",
        "intro": "A no-start car has a fact going for it: the problem is right there where it's "
                 "parked. Before you pay for a tow to a shop that will look at it Thursday, {BIZ} "
                 "comes to the car and finds out why it won't run. Often fixing it on the spot.",
        "bodies": [
            "No-starts sort into two families. 'Won't crank', silence or clicking, points at "
            "the battery, cables, starter, or a security system doing its job too well. 'Cranks "
            "but won't fire' points at fuel, spark, or timing: a fuel pump that hums its last, an "
            "ignition fault, a crank sensor that quit in the heat. Each family has a short list, "
            "and testing walks the list in minutes.",
            "Most no-starts we see are fixed in a single visit for less than the price of the "
            "tow the owner almost paid. On the ones that need parts we don't carry, we secure "
            "the car, get the part, and finish the job. You still never arrange a tow.",
        ],
        "bullets": [
            "Won't-crank and cranks-no-start diagnosis",
            "Batteries, starters, cables fixed on the spot",
            "Fuel pump, ignition, and sensor testing",
            "Anti-theft and key-system fault checks",
            "Cheaper than a tow plus a shop's diagnostic fee",
        ],
        "signs": None,
        "faqs": [
            ("The car died in a parking garage. Can you get to it?",
             "Usually yes. We work in garages, apartment complexes, and office decks all the "
             "time. Tell us the clearance and level when you call."),
            ("Should I try jump-starting it first?",
             "If you have cables and a donor car handy, one careful try is fine. If it starts and "
             "dies again, stop. Repeated jumps can mask the real fault and hurt modern "
             "electronics. Call us and we'll test it properly."),
        ],
    },
    {
        "slug": "pre-purchase-inspection",
        "name": "Pre-Purchase Car Inspection",
        "short": "Buying used in Orlando? Know what you're getting before the money moves.",
        "icon": "clipboard",
        "hero": "Get the Car Inspected Before You Buy It",
        "intro": "Orlando's used-car market moves fast, and every seller's car 'runs great.' "
                 "{BIZ} meets the car wherever it's being sold. Dealer lot, driveway, parking "
                 "lot handoff. And gives you an independent read before you commit.",
        "bodies": [
            "We scan the computer for stored and recently-cleared codes, check for the flood "
            "damage that quietly follows Florida hurricanes into the used market, look at frame "
            "and paint for hidden accident repair, test the battery and charging system, measure "
            "the brakes, examine tires and suspension, and road-test it if the seller allows.",
            "Then you get a plain-English verdict: what's solid, what needs money soon, and what "
            "that means for the price. Sometimes the report saves you from a bad car. Just as "
            "often it hands you a negotiating list worth far more than the inspection cost.",
        ],
        "bullets": [
            "Full computer scan, including cleared-code history",
            "Flood and hidden accident damage checks",
            "Brakes, tires, suspension, and fluids inspected",
            "Battery and charging system tested",
            "Straight verdict and a negotiating list",
        ],
        "signs": None,
        "faqs": [
            ("The seller says I can't take it to a shop.",
             "You don't have to. We come to the car. Most legitimate sellers are fine with an "
             "inspection on their own lot. A seller who refuses any inspection is telling you "
             "something; believe them."),
            ("Is this worth it on a cheap car?",
             "A cheap car with a bad transmission isn't cheap. The less room you have for "
             "surprise repairs, the more the inspection matters."),
        ],
    },
]

# ------------------------------------------------------------------ SERVICE DETAIL
# Deep-content layer for service pages: how the visit runs, what moves the
# price (factors only. No invented dollar amounts), and extra FAQs.
SERVICE_DETAIL = {
    "mobile-auto-repair": {
        "process": [
            ("You describe the problem", "Year, make, model, where the car sits, and what it's doing. Photos or a video of the noise help."),
            ("We quote the visit", "You know what showing up and diagnosing costs before we roll a wheel."),
            ("Diagnose and confirm", "We test at the vehicle and show you what we found. The actual failed part, not a guess."),
            ("Approve and repair", "You green-light the written price. Most jobs finish the same visit; we clean up after ourselves."),
        ],
        "factors": [
            "Parts cost for your specific vehicle. A Corolla alternator and a BMW alternator are different animals",
            "Labor time the job book assigns (we quote from the same guides shops use)",
            "Whether the car is on a driveway, street, or inside a tight garage",
            "Same-day and evening slots versus a scheduled window",
        ],
        "extra_faqs": [
            ("What can't be done mobile?", "Internal engine and transmission teardowns, alignment, and anything needing a lift or press. It's a short list. And we tell you upfront if your job is on it."),
            ("Do you work in the rain?", "Orlando afternoons, we plan around. Pop-up storms can pause an outdoor job briefly; garages and carports keep us moving."),
            ("Is mobile repair more expensive than a shop?", "Usually comparable, and often cheaper once you count the tow you didn't pay for and the workday you didn't lose."),
        ],
    },
    "check-engine-light-diagnostics": {
        "process": [
            ("Full scan", "Stored, pending, and history codes from every module. Not just the engine."),
            ("Data review", "Live sensor data and freeze-frame from the moment the fault set."),
            ("Physical testing", "Voltage, pressure, smoke, and resistance tests on the suspect circuit."),
            ("Plain-English verdict", "What failed, what it costs, whether it's safe to drive meanwhile."),
        ],
        "factors": [
            "How intermittent the fault is. A code that only sets on cold mornings takes longer to pin down",
            "Whether the fault is electrical (tracing time) or mechanical (test time)",
            "Multiple stacked codes: one root cause can light up four codes, or four problems can each set one",
        ],
        "extra_faqs": [
            ("Will you just tell me the code for free?", "The code alone is worth what the parts store charges for it: nothing. What you're paying for is knowing which part actually failed. That's the part that saves you money."),
            ("My mechanic replaced the part and the light came back.", "Classic symptom-chasing. We test the circuit behind the code, which is exactly how you avoid paying for the same repair twice."),
            ("Can you do emissions-related diagnostics?", "Yes. Evap leaks, O2 and cat-efficiency codes, all of it. Florida has no emissions test, but the light still hides new faults behind it."),
        ],
    },
    "brake-repair": {
        "process": [
            ("Measure first", "Pad thickness, rotor thickness and runout. You see the numbers."),
            ("Quote in writing", "Per-axle pricing with the parts named, approved before work starts."),
            ("Replace and torque", "New parts installed, hardware lubed, wheels torqued to spec."),
            ("Bed-in and road test", "We seat the new pads properly so they stop straight from day one."),
        ],
        "factors": [
            "Pads only versus pads and rotors. Caught early, rotors often survive",
            "One axle or both",
            "Caliper condition: a seized slide pin or piston adds parts and time",
            "Electronic parking brakes on newer cars need a scan tool for rear service",
        ],
        "extra_faqs": [
            ("How long do brake pads last in Orlando traffic?", "Stop-and-go on I-4 and 408 can halve pad life versus highway cruising. 25 to 40k miles is common here; we measure rather than guess."),
            ("Ceramic or semi-metallic pads?", "For most Orlando daily drivers, quality ceramics: quieter, less dust, happy in heat. Towing or heavy loads can argue for semi-metallic. We'll recommend based on how you drive."),
            ("Do you resurface rotors?", "On-site we replace rather than machine. By the time a rotor needs cutting, a new one is usually close in price and better in result."),
        ],
    },
    "mobile-oil-change": {
        "process": [
            ("Confirm the spec", "We look up your engine's exact oil grade and capacity. Not a one-size drum."),
            ("Drain and fill", "Warm drain, new filter, correct-torque plug with a fresh washer where specified."),
            ("The once-over", "Fluids, belt, visible leaks, air filter, tires, battery voltage."),
            ("Reset and recycle", "Maintenance light reset; old oil and filter leave with us."),
        ],
        "factors": [
            "Oil type. Full synthetic costs more than blend, and European specs more again",
            "Capacity: a 4-cylinder takes 4 to 5 quarts, a diesel truck can take 10+",
            "Cartridge versus spin-on filters on some engines",
        ],
        "extra_faqs": [
            ("Synthetic or conventional?", "If your car was built in the last decade, it almost certainly calls for synthetic or a blend, and Florida heat is exactly the condition synthetic exists for. We follow the manual, not the upsell."),
            ("Can you service my fleet at the office?", "Yes. Several vehicles in one lot in one visit is the most efficient thing we do. Ask about scheduling a recurring round."),
        ],
    },
    "battery-replacement": {
        "process": [
            ("Load test", "The battery under real load, plus resting and cranking voltage. You see the readings."),
            ("Charging test", "Alternator output and drain check, so the new battery doesn't die the same death."),
            ("Install correctly", "Right group size, terminals cleaned, hold-down secured, settings preserved."),
            ("Register and recycle", "Battery registration where the vehicle requires it; the old core leaves with us."),
        ],
        "factors": [
            "Group size and chemistry. AGM batteries (start-stop cars) cost more than flooded",
            "Battery location: trunk, under-seat, and fender-well batteries add labor",
            "Registration requirement on many newer European and start-stop vehicles",
        ],
        "extra_faqs": [
            ("Why did my battery die with no warning?", "Heat does the damage quietly all summer; the failure just picks its moment. Florida batteries often skip the slow-cranking warning phase entirely."),
            ("Is a parts-store free install good enough?", "For an easy under-hood battery on an older car, sometimes. But no load test, no drain test, no registration. Which is how people buy three batteries for one alternator problem."),
        ],
    },
    "starter-alternator-repair": {
        "process": [
            ("Circuit test", "Battery, cables, grounds, relay, and the unit itself. In that order."),
            ("Confirm the failure", "Voltage-drop and output tests under load, not parts-cannon guessing."),
            ("Replace on-site", "Even buried starters come out in a driveway with the right tools."),
            ("Verify the fix", "Charging output and crank speed rechecked before we leave."),
        ],
        "factors": [
            "Access: some starters are two bolts, some hide under intake manifolds",
            "New versus quality reman units. We quote both when it makes sense",
            "Belt and tensioner condition. Smart to renew while the alternator is out",
        ],
        "extra_faqs": [
            ("The dash flickers and the car whines. Battery or alternator?", "Whine that rises with RPM plus flickering points at the alternator. But the test takes minutes and removes the guess. That's the whole point."),
            ("Can you replace a starter in a parking garage?", "Usually yes. We work in garages constantly. Very low clearances are the only real obstacle; tell us the height when you call."),
        ],
    },
    "ac-repair": {
        "process": [
            ("Pressure reading", "High and low side pressures tell the first half of the story."),
            ("Watch it work", "Compressor engagement, fan operation, and cycling behavior at idle and revs."),
            ("Find the leak", "Dye or electronic detection before any refrigerant goes in."),
            ("Fix and verify", "Repair, evacuate, recharge by weight, and confirm vent temperatures."),
        ],
        "factors": [
            "What failed: a fan or pressure switch versus a compressor are very different jobs",
            "Refrigerant type. Newer 1234yf systems cost more to service than R-134a",
            "How long it ran low: compressors running starved of oil shorten their own lives",
        ],
        "extra_faqs": [
            ("How cold should my A/C actually get?", "Roughly 38 to 48°F at the center vent on max, engine warm, doors closed. Even in an Orlando summer. Mid-50s and up means something's wrong."),
            ("Why does it smell musty only at startup?", "Condensation sitting in the evaporator box grows things overnight. A cleaning treatment fixes it; running the fan without A/C the last minute of your drive helps prevent it."),
        ],
    },
    "no-start-repair": {
        "process": [
            ("Triage on the phone", "Won't crank versus cranks-won't-fire sends us down different checklists. And tells us what to load."),
            ("Test at the car", "Battery, starter circuit, fuel pressure, spark, and security system as the symptoms dictate."),
            ("Fix on the spot", "Most no-starts are batteries, starters, cables, or relays. All same-visit repairs."),
            ("Prove it", "Multiple restart cycles before we leave, so it starts again tomorrow."),
        ],
        "factors": [
            "Which family the fault is in. Crank faults are usually cheaper than fuel-system faults",
            "Parts availability for your vehicle same-day",
            "Location access: garages and aprons are easy; a busy roadside needs a safe setup",
        ],
        "extra_faqs": [
            ("It started fine this morning and now nothing. What gives?", "Sudden total failure with no warning is classically a battery terminal, a main cable, a relay, or a security fault. All quick finds with a meter."),
            ("Is it cheaper than a tow?", "A tow costs money and gets you a car that's still broken, now in a queue. Our visit usually costs in the same range and frequently ends with the car running."),
        ],
    },
    "pre-purchase-inspection": {
        "process": [
            ("Meet the car anywhere", "Dealer lot, seller's driveway, parking-lot handoff. We come to the sale."),
            ("Scan deep", "Current codes plus history and readiness monitors, which expose recently-cleared codes."),
            ("Inspect hands-on", "Flood tells, paint depth and panel gaps, brakes, tires, suspension, fluids, battery."),
            ("Report before you pay", "A straight verdict and an itemized list you can negotiate with, same day."),
        ],
        "factors": [
            "Vehicle age and complexity. A 3-year-old lease return inspects faster than a 15-year-old project",
            "Whether a road test is permitted by the seller",
            "Add-ons like a compression test on higher-mileage engines",
        ],
        "extra_faqs": [
            ("What are the flood-damage red flags in Florida?", "Silt in seat tracks and under carpet, corrosion on connector pins above the floor line, fogged lamps, mismatched carpet, and a musty smell fighting an air freshener. After every hurricane season, flood cars flow into the used market. Some with clean titles."),
            ("The car has a fresh oil change sticker and a shiny engine bay. Good sign?", "Sometimes it's care; sometimes it's staging. A degreased engine hides leaks for exactly a few days. One more reason an inspection beats a glance."),
        ],
    },
}

# ------------------------------------------------------------------ CITIES
# (slug, name, county, [two unique paragraphs])
CITIES = [
    ("orlando", "Orlando", "Orange County", [
        "From downtown high-rises to Lake Nona, from College Park bungalows to apartment "
        "complexes off Semoran, most of Orlando has one thing in common: nowhere convenient to "
        "leave a car for three days. We fix it where it's parked. Home, office, or the spot on "
        "the shoulder where it quit.",
        "Our mechanics work around the rhythms of this city, with hours built for people who "
        "don't clock out at five. Seven days a week, we come to you.",
    ]),
    ("winter-park", "Winter Park", "Orange County", [
        "Winter Park driveways see everything from daily commuters to weekend classics, and "
        "none of them enjoys the trip to a service bay. We bring diagnostics, brakes, batteries, "
        "and oil service to your address. Park Avenue side streets, Hannibal Square, or out by "
        "Cady Way.",
        "Squeezing a shop visit between work and everything else is exactly the errand we "
        "exist to delete. Book a window, hand us the key, get on with your day.",
    ]),
    ("kissimmee", "Kissimmee", "Osceola County", [
        "Kissimmee runs on cars. Commutes up the 417, shift work along 192, school runs, "
        "airport trips. When one of them won't start or the brakes start talking, losing it to a "
        "shop for days isn't an option. We come to your driveway or workplace and fix it there.",
        "We serve the whole Kissimmee area, from downtown to Buenaventura Lakes to the resort "
        "corridors, seven days a week.",
    ]),
    ("sanford", "Sanford", "Seminole County", [
        "From historic downtown Sanford to the subdivisions off Rinehart Road, we bring the "
        "repair shop to you. Diagnostics, brakes, batteries, starters, A/C. Done where the car "
        "sits, with the price agreed before the work starts.",
        "A car that won't crank in your driveway can't drive itself to a shop, and a tow down "
        "17-92 isn't cheap. Skip both. Call us and we'll meet the car where it is.",
    ]),
    ("apopka", "Apopka", "Orange County", [
        "Apopka's spread out enough that being without a car isn't an inconvenience. It's a "
        "grounding. Instead of surrendering yours to a waiting room, have the mechanic come to "
        "your address, from downtown to Errol Estates to out toward Rock Springs.",
        "We handle the everyday jobs like oil, brakes, and batteries, and the day-ruiners like "
        "no-starts and check engine lights, on your schedule, at your curb.",
    ]),
    ("altamonte-springs", "Altamonte Springs", "Seminole County", [
        "Between the 414, I-4, and 436, Altamonte drivers spend enough time around cars without "
        "adding a service-bay waiting room to the week. We come to your apartment complex, "
        "office lot, or driveway and do the work there.",
        "Complex parking garages don't scare us. We work in them all the time. Tell us where "
        "the car is and what it's doing, and we'll bring the shop to it.",
    ]),
    ("winter-garden", "Winter Garden", "Orange County", [
        "Winter Garden has grown fast, but the errand of dropping a car at a shop hasn't gotten "
        "any faster. We bring certified mechanics to Stoneybrook West, the downtown core, and "
        "everything off the 429. Brakes, diagnostics, batteries, oil, A/C.",
        "You approve the price before we start, watch the work if you like, and keep your whole "
        "day. That's the entire pitch.",
    ]),
    ("ocoee", "Ocoee", "Orange County", [
        "When an Ocoee commuter's car acts up, the choices used to be a tow, a shuttle, or a "
        "day off work. Now it's a phone call. We come to your home or workplace and handle the "
        "repair on-site.",
        "From Clarke Road to the neighborhoods around Starke Lake, we cover Ocoee seven days a "
        "week with evening hours that fit real schedules.",
    ]),
    ("oviedo", "Oviedo", "Seminole County", [
        "Oviedo families tend to run tight logistics. School, practice, UCF, work across town. "
        "A car in the shop breaks the whole schedule. A mechanic in the driveway doesn't.",
        "We bring diagnostics, brake work, batteries, and maintenance to your address, on a "
        "booked window, with the price settled before a tool comes out.",
    ]),
    ("lake-mary", "Lake Mary", "Seminole County", [
        "Lake Mary's office parks are full of cars that sit for eight predictable hours a day. "
        "Which happens to be the perfect service window. We do repairs and maintenance in "
        "workplace lots all the time; you come out to a car that's ready to go.",
        "At home in Heathrow or Timacuan, same deal: the shop comes to the driveway, seven days "
        "a week.",
    ]),
    ("windermere", "Windermere", "Orange County", [
        "Windermere driveways are a better place for your car than any waiting room. We come to "
        "you for everything from routine maintenance to diagnostics and brake work, and we treat "
        "the vehicle and the driveway with care.",
        "Booked windows, straight pricing, certified mechanics. The errand disappears; the car "
        "gets fixed.",
    ]),
    ("dr-phillips", "Dr. Phillips", "Orange County", [
        "Between Restaurant Row and the parks, Dr. Phillips traffic gives brakes and batteries "
        "a workout. When yours start complaining, we come to your home or office and fix them "
        "there. No tow, no shuttle, no lost day.",
        "We work Sand Lake to Turkey Lake and everything between, seven days a week.",
    ]),
    ("st-cloud", "St. Cloud", "Osceola County", [
        "St. Cloud drivers put in real miles, and real miles wear real parts. Rather than "
        "hauling the car up the Turnpike to a shop, have the mechanic come down to you. "
        "Brakes, batteries, starters, oil, and no-start calls, done at your address.",
        "We cover St. Cloud and the surrounding Osceola communities on the same seven-day "
        "schedule as the rest of the metro.",
    ]),
    ("winter-springs", "Winter Springs", "Seminole County", [
        "Winter Springs is quiet, which is exactly how your car repair should be: a service "
        "vehicle in the driveway for an hour or two, not a missing car for three days. We bring "
        "the tools and parts to you.",
        "From Tuskawilla to the 434 corridor, book a window and we'll be there. Evenings and "
        "Sundays included.",
    ]),
]

# ------------------------------------------------------------------ FAQ
FAQS = [
    ("Do you really come to me?",
     "Yes. That's the whole business. Home, office, apartment complex, parking garage, or "
     "roadside, anywhere in the Orlando metro. You never arrange a tow or sit in a waiting room."),
    ("What areas do you cover?",
     "Orlando and the surrounding area, including Winter Park, Kissimmee, Sanford, Apopka, "
     "Altamonte Springs, Winter Garden, Ocoee, Oviedo, Lake Mary, and more. Not sure? Call. "
     "If we can get to you, we will."),
    ("What are your hours?",
     "Monday through Saturday 9am to 10pm, and Sunday 9am to 6pm. Evening appointments are "
     "normal for us, not a favor."),
    ("How does pricing work?",
     "We diagnose first, then quote the repair, and you approve the price before any work "
     "starts. No surprise line items when the job is done."),
    ("What if the repair can't be done on-site?",
     "A small number of jobs genuinely need a lift or specialty equipment. When that's the "
     "case, we tell you straight, explain what it needs, and you decide. We don't start work "
     "we can't finish."),
    ("How do I book?",
     f"Call or text {PHONE_DISP}, use the booking form, or book a slot directly online. "
     "Tell us the year, make, model, where the car is, and what it's doing."),
]

# ------------------------------------------------------------------ REVIEWS
# Real Google reviews, harvested verbatim from the live GMB listing 2026-08-20
# (4.9 stars / 35 reviews at capture time). Do not invent or edit review text.
REVIEWS = [
    ("FreshGod _x", 5, "2025",
     "I had an outstanding experience with Yair and Paul, I can't recommend them enough! "
     "Both were incredibly professional and knowledgeable. Instantly found my car's issue "
     "and immediately put me at ease."),
    ("Craig Barnes", 5, "2025",
     "Had some trouble with my alternator and Paul came out the same day. Fast, friendly, "
     "and trustworthy. Will definitely use this service again."),
    ("Cameron Desrochers", 5, "2025",
     "Needed an oil change and tire rotation, and they handled it all in my driveway. "
     "So much easier than going to a shop. Very satisfied!"),
    ("Julie Lopez", 5, "2025",
     "Amazing service from start to finish. The mechanic was professional, showed up on "
     "time, and got my car back on the road quickly. Highly recommend for anyone needing "
     "reliable repairs."),
    ("Tyler Harrison", 5, "2025",
     "Great work ethic, super knowledgeable, and you can tell Paul really cares about his "
     "customers. Definitely sticking with him for future car issues."),
    ("Ethan Weber", 5, "2025",
     "Best mechanic I've ever dealt with! They fixed my transmission issue quickly and at "
     "a reasonable price. Super convenient and highly professional!"),
    ("Julia Blais", 5, "2025",
     "The technician was courteous, arrived on time, and worked efficiently. My car feels "
     "like new again. Thank you for the excellent service!"),
    ("Frenshyll Flores", 5, "2025",
     "Superb service! They provided quick, high-quality repairs. My car has never run "
     "better. Professional and friendly staff!"),
    ("Korrawan J.", 5, "2025",
     "Hands down the best mobile repair experience I've had. They were respectful, "
     "knowledgeable, and left my vehicle in great condition. Highly recommended!"),
]

# ------------------------------------------------------------------ MAP
# Approximate city-center coordinates for the service map. Markers are
# plotted with deterministic offsets around these centers. Illustrative
# "jobs we do here" pins, NOT real customer addresses (privacy).
CITY_COORDS = {
    "orlando": (28.5383, -81.3792), "winter-park": (28.6000, -81.3392),
    "kissimmee": (28.2920, -81.4076), "sanford": (28.8029, -81.2695),
    "apopka": (28.6934, -81.5322), "altamonte-springs": (28.6611, -81.3656),
    "winter-garden": (28.5653, -81.5862), "ocoee": (28.5692, -81.5440),
    "oviedo": (28.6700, -81.2081), "lake-mary": (28.7589, -81.3178),
    "windermere": (28.4956, -81.5348), "dr-phillips": (28.4494, -81.4923),
    "st-cloud": (28.2489, -81.2812), "winter-springs": (28.6989, -81.3081),
}
MAP_JOBS = ["Brake pads & rotors", "Check engine diagnosis", "Battery replacement",
            "Alternator replacement", "Mobile oil change", "No-start fixed on-site",
            "Starter replacement", "A/C repair", "Pre-purchase inspection",
            "Belt & tensioner service", "Maintenance visit"]

def map_markers():
    """Deterministic pseudo-random pins per city (denser near the core)."""
    import hashlib
    pins = []
    for slug, (lat, lng) in CITY_COORDS.items():
        n = 6 if slug == "orlando" else 3
        nm = next(c[1] for c in CITIES if c[0] == slug)
        for i in range(n):
            h = hashlib.md5(f"{slug}-{i}".encode()).digest()
            dy = (h[0] / 255 - .5) * .040
            dx = (h[1] / 255 - .5) * .055
            job = MAP_JOBS[h[2] % len(MAP_JOBS)]
            pins.append({"lat": round(lat + dy, 5), "lng": round(lng + dx, 5),
                         "city": nm, "job": job})
    return pins

# ------------------------------------------------------------------ BITE / SNACK
# Bite-snack-meal content layering: every deep page opens with a one-line
# answer (bite) and a skimmable summary (snack) before the full content (meal).
SERVICE_BITE = {
    "mobile-auto-repair": (
        "Most repairs a shop does in a bay, we do in your driveway. <b>Diagnosed, quoted, "
        "and usually finished in one visit.</b>",
        ["We come to homes, offices, and roadsides metro-wide",
         "Written price approved before work starts",
         "Most repairs done in a single visit",
         "Open 7 days, evenings Mon to Sat"]),
    "check-engine-light-diagnostics": (
        "A trouble code names a circuit, not a part. <b>We test the circuit and replace only "
        "what actually failed</b>. So you don't pay twice.",
        ["Flashing light? Stop driving and call",
         "Steady light? Usually safe, still needs diagnosis",
         "Full scan + live data + physical testing",
         "Diagnostic fee credited when we do the repair"]),
    "brake-repair": (
        "A squeal is a cheap fix; a grind is an expensive one. <b>We measure at your curb and "
        "show you the numbers</b> before a wheel comes off.",
        ["Pads, rotors, calipers, fluid. Done on-site",
         "Measurements shown, old parts in your hand",
         "Orlando stop-and-go wears pads in 25 to 40k miles",
         "Per-axle written quote before work starts"]),
    "mobile-oil-change": (
        "The exact oil your engine specifies. <b>Changed at your home or office</b>, with a "
        "multi-point check and the used oil hauled away.",
        ["Conventional, blend, or full synthetic per the manual",
         "New filter, correct-torque drain plug",
         "Free health check with every change",
         "Fleet rounds at offices welcome"]),
    "battery-replacement": (
        "Florida heat kills batteries in three to four years. <b>We test the battery, "
        "alternator, and drain first</b>. Then replace on the spot if it's truly the battery.",
        ["Load test with readings you can see",
         "Charging system and drain checked too",
         "Correct group size installed, settings preserved",
         "Old battery recycled for you"]),
    "starter-alternator-repair": (
        "A car that won't crank can't drive to a shop. <b>We test the whole circuit and "
        "replace the failed unit where the car sits</b>. No tow involved.",
        ["Battery, cables, relay, and unit tested in order",
         "Starters replaced in driveways and garages",
         "Alternator output verified under real load",
         "Belt and tensioner checked while we're in there"]),
    "ac-repair": (
        "Cold on the highway but warm at red lights? <b>That's usually a fan, not low "
        "refrigerant.</b> We diagnose before anything goes into the system.",
        ["Pressures read on both sides first",
         "Fans, compressor, and switches tested at idle",
         "Leak detection before any refrigerant",
         "Vent temps verified cold before we leave"]),
    "no-start-repair": (
        "Don't tow a car nobody has diagnosed. <b>Most no-starts are fixed in one visit</b> "
        "for around what the tow alone would cost.",
        ["Won't-crank and cranks-no-fire both covered",
         "Batteries, starters, cables fixed on the spot",
         "We work in garages, lots, and roadsides",
         "Multiple restart cycles proven before we go"]),
    "pre-purchase-inspection": (
        "An hour of inspection before you buy beats a year of surprises after. <b>We meet "
        "the car wherever it's for sale</b> and report before money moves.",
        ["Deep scan including recently-cleared codes",
         "Florida flood-damage tells checked",
         "Brakes, tires, suspension, fluids measured",
         "Same-day verdict plus a negotiating list"]),
}

BLOG_BITE = {
    "mobile-mechanic-hourly-rate-orlando": (
    "There is no official hourly rate. <b>Ask for the total price of the job in writing</b>, "
    "because in Florida that estimate is what protects you.",
    ["Orlando auto techs earned a median $23.00 an hour in May 2025 (BLS)",
     "A billed rate also pays for the truck, tools, drive time and taxes",
     "Over $150, Florida law says you get a written estimate first",
     "The bill can only go $50 over the estimate without your okay"]),
    "30-60-90-rule-for-cars": (
        "The 30-60-90 rule says your car needs a bigger service at <b>30,000, 60,000 and "
        "90,000 miles</b>. In Orlando, treat those marks as the latest you should go, because "
        "heat, stop and go traffic and beach salt all count as severe driving.",
        ["30k is filters, tire rotation and a full inspection",
         "60k adds fluids, and spark plugs on some engines",
         "90k is the timing belt and water pump, if your engine has a belt",
         "Your owner's manual beats the rule every time",
         "Orlando drivers should use the severe schedule in that manual",
         "Batteries age by the calendar here, so test yearly from year three"]),
    "florida-heat-car-battery": (
        "Heat, not cold, is what kills car batteries, and Orlando summers cut battery life "
        "to <b>three or four years.</b>",
        ["Heat ages the battery all summer; failure just picks its moment",
         "Florida batteries often die with no slow-crank warning",
         "Past year three, get a free load test annually",
         "Repeated jumps? Test battery, alternator, AND drain"]),
    "mobile-mechanic-vs-tow-to-shop": (
        "For a car that won't start, <b>diagnosing it where it sits usually beats towing it</b>. "
        "On cost, on time, and on stress.",
        ["Tow route = tow fee + shop diagnostic + days in a queue",
         "Most no-starts are same-visit fixes at your address",
         "Lift-only jobs exist. A good mobile mechanic says so upfront",
         "Worst case: you tow once, to the right place, informed"]),
    "check-engine-light-what-to-do": (
        "<b>Steady light: drive gently, diagnose soon. Flashing light: pull over now</b>. "
        "You're cooking the catalytic converter.",
        ["A code names a circuit, not a part",
         "Free code reads sell parts, not answers",
         "Real diagnosis = live data + physical testing",
         "A light that 'went away' is still stored and coming back"]),
    "car-ac-warm-at-idle": (
        "A/C warm at stoplights but cold at speed is <b>almost always a condenser-fan "
        "problem, not low refrigerant.</b>",
        ["Highway speed cools the condenser for free; idle needs the fan",
         "Recharge cans mask leaks and can overcharge the system",
         "The compressor pays for every shortcut",
         "Proper diagnosis: pressures, fans, leak check. Then refrigerant"]),
    "used-car-flood-damage-orlando": (
        "After every storm season, flood cars enter Florida's used market. <b>Some with "
        "clean titles.</b> The car tells the truth even when the paperwork doesn't.",
        ["Check seat tracks and under-carpet for silt",
         "Corroded connector pins above the floor line = red flag",
         "Flooded electronics fail for years, one module at a time",
         "A seller who refuses an inspection has answered your question"]),
    "i4-traffic-brake-wear": (
        "Brakes wear per stop, not per mile. <b>I-4 commuters wear pads in half the "
        "'normal' mileage.</b>",
        ["Squeal = pads due, rotors probably still fine",
         "Grind = rotors being damaged at every stop",
         "Shudder from speed = warped rotors, growing distances",
         "Acting on the squeal is routinely a three-figure savings"]),
}

# ------------------------------------------------------------------ BLOG
BLOG = [
    {
        "slug": "mobile-mechanic-hourly-rate-orlando",
        "title": "How Much Should a Mobile Mechanic Charge an Hour in Orlando?",
        "desc": "What Orlando mechanics really earn, why the guides disagree on hourly rates, "
                "and the Florida estimate rules that protect you before any work starts.",
        "date": "2026-10-15", "tag": "Pricing",
        "faqs": [
            ("How much should a mobile mechanic charge an hour?",
             "There is no official number. Guides that rank for this question quote anywhere "
             "from $50 to $150 an hour, and the ones we read on October 12, 2026 did not name "
             "where their numbers came from. The hourly rate also matters less than the total. "
             "Ask for the price of the whole job, in writing, before work starts."),
            ("How much is mechanic labor per hour in Florida?",
             "What a mechanic earns and what a shop bills are two different numbers. The U.S. "
             "Bureau of Labor Statistics says the median auto technician in Florida earned "
             "$23.20 an hour in May 2025. A billed labor rate is higher because it also pays "
             "for tools, insurance, the truck or the building, and the hours nobody can bill."),
            ("Is $150 an hour expensive for a mechanic?",
             "Not by itself. A $150 rate on a job booked at one hour costs less than a $90 rate "
             "on a job that somehow takes three. Compare the full price for the same job, the "
             "same parts and the same guarantee. Then the hourly rate stops mattering."),
            ("Can a mechanic charge more than the estimate in Florida?",
             "Only by a little, unless you say yes first. Florida law lets the final bill go "
             "over a written estimate by $10 or 10 percent, whichever is more, but never by "
             "more than $50. Past that, the shop has to call you and get your okay."),
            ("Do mobile mechanics have to register in Florida?",
             "Yes. The Florida Motor Vehicle Repair Act counts mobile repair shops and "
             "self-employed mechanics as repair shops, and repair shops have to register with "
             "the Florida Department of Agriculture and Consumer Services. You can look a "
             "business up on the department's Business License Lookup."),
            ("Do I have to pay for a diagnosis?",
             "Often, yes. Finding the problem is real work. In Florida, a written estimate has "
             "to list the charge for making the estimate, or how that charge is worked out. Ask "
             "about it on the phone so it is not a surprise."),
        ],
        "body": """
<p>Everybody wants one number. Type this question into Google and you get Reddit threads,
Facebook groups and a few guides that quote $50, $85 or $150 an hour. We read the top ones
on October 12, 2026. None of them said where their numbers came from, and none of them said
a word about Florida.</p>
<p>So here is what we can show you with real sources. What Orlando mechanics actually earn,
why a mobile rate is built differently from a shop rate, and the Florida law that matters
more than any hourly number.</p>

<h2>Why Nobody Agrees on the Hourly Rate</h2>
<p>The guides disagree because they are guessing in public. One 2026 guide from a mechanic
software company puts the national mobile rate at $85 an hour and says rates run from $50 to
$150. It credits industry data from thousands of mechanics but never names it. Another 2026
guide from a shop software maker says mobile mechanics charge $80 to $140 and calls its
numbers estimates. Both may be fair guesses. Neither is something you can check.</p>
<p>The rest of page one is Reddit threads, Facebook groups, a forum and a TikTok, where
mechanics trade their own rates and argue about them. Those are real opinions from real
mechanics. They are not a market rate.</p>
<p>There is a better place to start. The government tracks what mechanics get paid.</p>

<h2>What Orlando Mechanics Actually Earn</h2>
<p>The U.S. Bureau of Labor Statistics runs a wage survey every May. Its May 2025 numbers
count 6,480 automotive service technicians and mechanics working in the Orlando, Kissimmee
and Sanford metro area. Here is what they earned, next to Florida and the whole country.</p>
<div class="symwrap" role="img" aria-label="Bar chart. Hourly pay for auto technicians, May 2025. Orlando median $23.00, Florida median $23.20, United States median $24.34, Orlando mean $25.77.">
<p style="margin:.6em 0 .2em"><b>Hourly Pay for Auto Technicians, May 2025</b></p>
<div style="display:grid;gap:.55em;margin:.8em 0 1em">
<div><div style="font-size:.9rem">Orlando metro, median</div><div style="display:flex;align-items:center;gap:.6em"><span style="display:block;height:18px;width:76.7%;background:var(--grad);border-radius:4px"></span><b>$23.00</b></div></div>
<div><div style="font-size:.9rem">Florida, median</div><div style="display:flex;align-items:center;gap:.6em"><span style="display:block;height:18px;width:77.3%;background:var(--grad);border-radius:4px"></span><b>$23.20</b></div></div>
<div><div style="font-size:.9rem">United States, median</div><div style="display:flex;align-items:center;gap:.6em"><span style="display:block;height:18px;width:81.1%;background:var(--grad);border-radius:4px"></span><b>$24.34</b></div></div>
<div><div style="font-size:.9rem">Orlando metro, mean</div><div style="display:flex;align-items:center;gap:.6em"><span style="display:block;height:18px;width:85.9%;background:var(--grad);border-radius:4px"></span><b>$25.77</b></div></div>
</div>
<p style="font-size:.85rem;color:var(--dim);margin:0 0 .6em">Source, U.S. Bureau of Labor Statistics, Occupational Employment and Wage Statistics, May 2025, read October 12, 2026.</p>
</div>
<p>Two things jump out. Orlando mechanics earn a little less than the national median. And
the mean is higher than the median, which means a smaller group of top techs pulls the
average up. That matches what you see on the street. A master tech with a diagnostic scope
and years on Toyotas and Fords is not paid like a lube tech.</p>
<p>Now the key point. <b>That wage is not the price you pay.</b> It is what lands in the
mechanic's pocket before anything else gets paid.</p>

<h2>How a Mobile Rate Gets Built</h2>
<p>A labor rate has to cover the mechanic's pay and everything that makes the work
possible. For a shop that means rent, lifts and a front desk. For a mobile mechanic it is a
different list.</p>
<ul>
<li><b>The truck.</b> Fuel, tires, insurance and repairs on the van that carries the
shop.</li>
<li><b>Tools and scan gear.</b> A real diagnostic scanner, software updates and the hand
tools that ride along every day.</li>
<li><b>Drive time.</b> Nobody bills for sitting on I-4. An hour in traffic between jobs is an
hour of pay with no work in it.</li>
<li><b>Parts runs.</b> Picking up the right part, and taking back the wrong one, is time on
the clock too.</li>
<li><b>Taxes and business costs.</b> The things every business pays before the owner sees a
dollar.</li>
</ul>
<p>Here is a worked example, not anyone's real price. Say a mobile mechanic wants to earn
the Orlando median of $23 an hour. Say a third of the workday goes to driving, parts runs
and paperwork that nobody pays for. To clear $23 for every hour worked, he has to bill $34.50
for every hour he is on a car. That is before one gallon of gas, one tool, one insurance bill
or one tax payment. Add those and you can see how the rates in the guides get where they
are.</p>
<figure class="photo-card" style="margin:1.4em 0"><img src="/img/under-hood.jpg" width="1400" height="1050" loading="lazy"
 alt="Mobile mechanic working under the hood of a customer's car in Orlando"></figure>
<p>There is one place mobile repair can come out ahead. There is no building to pay for and
no waiting room to heat or cool. Whether that saving reaches you depends on the job and the
mechanic. So do not judge by the rate. Judge by the total.</p>

<h2>The Hourly Rate Is the Wrong Thing to Compare</h2>
<p>Most repair work is not timed with a stopwatch. A lot of mechanics, at shops and on the
road, price a job from a set labor time for that repair on that car, or quote a flat price
for the whole job. Florida law even makes the shop tell you which one you are getting. A
written estimate has to say whether you are charged a flat rate, an hourly rate, or both.</p>
<p>That is why two quotes with the same hourly rate can land far apart, and two quotes with
very different rates can come out the same. Here is what to put side by side instead.</p>
<div class="symwrap"><table class="sym">
<tr><th>Ask about</th><td><b>Why it matters</b></td></tr>
<tr><th>The total price for the job</th><td>Rate times hours, plus parts, plus any fees. This is the only number you actually pay.</td></tr>
<tr><th>Flat or hourly</th><td>A flat price puts the risk of a slow job on the mechanic. An hourly price puts it on you.</td></tr>
<tr><th>The parts</th><td>Brand, new or rebuilt, and whether the old parts come back to you.</td></tr>
<tr><th>The diagnosis charge</th><td>Whether there is one, how much, and whether it counts toward the repair.</td></tr>
<tr><th>Any trip or supply fee</th><td>Some mobile mechanics charge to come out. Florida estimates have to list shop supply and waste charges.</td></tr>
<tr><th>The guarantee</th><td>What is covered, and for how many months or miles. A Florida estimate has to say.</td></tr>
</table></div>

<h2>The Florida Rules That Protect You</h2>
<p>This is the part none of the top pages cover, and it is worth more than any hourly
number. Florida has a law just for car repair. It is the Florida Motor Vehicle Repair Act,
Chapter 559, Part IX of the Florida Statutes.</p>

<h3>Mobile Mechanics Count as Repair Shops</h3>
<p>Section 559.903 defines a repair shop as anyone paid to fix cars owned by other people.
It names mobile motor vehicle repair shops and self-employed people right in the list. Section
559.904 says each repair shop has to register with the Florida Department of Agriculture and
Consumer Services before doing business. The department has a Business License Lookup on its
website, so you can check a name before you hand over a key.</p>

<h3>You Get a Written Estimate Over $150</h3>
<p>Under section 559.905, when a repair will cost you more than $150, the shop has to give
you a written estimate before any diagnosis or repair begins. The estimate has to show the
shop's name and phone, your car's details, a description of the problem, flat or hourly, the
estimated cost, the charge for making the estimate, any guarantee, and whether you want your
old parts saved. You are allowed to waive the estimate, but you do not have to.</p>

<h3>The Bill Can Only Go a Little Over</h3>
<p>Section 559.909 caps the surprise. Without your okay, the final bill can only go over the
written estimate by $10 or 10 percent, whichever is more, and never by more than $50. If more
work turns up, the shop has to call you, and you can say yes, change the job, or cancel it.
The shop also cannot keep your car because you refused to pay for work you never agreed
to.</p>
<p>Here is what that cap looks like on real dollar amounts. These are worked examples from
the statute, not prices for any job.</p>
<div class="symwrap"><table class="sym">
<tr><th>Written estimate</th><td><b>Most the bill can be without your okay</b></td></tr>
<tr><th>$200</th><td>$220 (10 percent is $20)</td></tr>
<tr><th>$400</th><td>$440 (10 percent is $40)</td></tr>
<tr><th>$800</th><td>$850 (10 percent would be $80, so the $50 cap wins)</td></tr>
<tr><th>$1,500</th><td>$1,550 (the $50 cap again)</td></tr>
</table></div>
<p>Read that table again with the hourly rate question in mind. A written estimate with a
total on it protects you no matter what the rate is. An hourly rate with no estimate protects
you from nothing.</p>

<h3>You Can See Your Old Parts</h3>
<p>The same section says you can ask to inspect the parts that came off your car, as long as
you ask when you approve the work. In many cases you can take them home. It is the easiest
way to know the part was really replaced.</p>
<figure class="photo-card" style="margin:1.4em 0"><img src="/img/driveway-service.jpg" width="1475" height="1536" loading="lazy"
 alt="Mobile mechanic doing a repair in a customer's driveway in the Orlando area"></figure>

<h2>How to Get a Fair Price This Week</h2>
<ol class="proc">
<li><b>Describe the problem clearly</b><p>The year, make, model and mileage, what you hear or
feel, and when it happens. A clear story gets a closer quote.</p></li>
<li><b>Ask for the total, not the rate</b><p>Ask what the whole job costs, parts and labor,
and whether that is flat or hourly.</p></li>
<li><b>Ask about diagnosis and trip charges</b><p>Find out up front if finding the problem
costs extra, and if it counts toward the repair.</p></li>
<li><b>Get it in writing over $150</b><p>It is Florida law. A text or email with the total
is better than a number said in passing.</p></li>
<li><b>Check the registration</b><p>Look the business up on the Florida Department of
Agriculture and Consumer Services Business License Lookup.</p></li>
<li><b>Ask for your old parts</b><p>Say so when you approve the work, not after.</p></li>
</ol>
<p>We do not post an hourly rate on this site, and we do not think you should shop by one.
Call {PHONE}, tell us what the car is doing, and you get the price in plain numbers before any
work starts. That goes for <a href="/services/brake-repair/">brake jobs</a>, <a
href="/services/check-engine-light-diagnostics/">check engine diagnostics</a> and <a
href="/services/no-start-repair/">cars that will not start</a>. If you are weighing a tow
against a house call, here is <a href="/blog/mobile-mechanic-vs-tow-to-shop/">the real math
on a mobile mechanic versus towing to a shop</a>.</p>

<h2>Sources</h2>
<ul class="sources">
<li>U.S. Bureau of Labor Statistics, Occupational Employment and Wage Statistics, May 2025, <a href="https://data.bls.gov/timeseries/OEUM003674000000049302308" rel="nofollow noopener">Orlando metro median wage</a>, <a href="https://data.bls.gov/timeseries/OEUM003674000000049302303" rel="nofollow noopener">Orlando metro mean wage</a>, <a href="https://data.bls.gov/timeseries/OEUM003674000000049302301" rel="nofollow noopener">Orlando metro employment</a>, <a href="https://data.bls.gov/timeseries/OEUS120000000000049302308" rel="nofollow noopener">Florida median wage</a> and <a href="https://data.bls.gov/timeseries/OEUN000000000000049302308" rel="nofollow noopener">U.S. median wage</a> for automotive service technicians and mechanics, read October 12, 2026</li>
<li>Florida Statutes 2026, <a href="http://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&amp;URL=0500-0599/0559/Sections/0559.903.html" rel="nofollow noopener">section 559.903, Definitions</a></li>
<li>Florida Statutes 2026, <a href="http://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&amp;URL=0500-0599/0559/Sections/0559.904.html" rel="nofollow noopener">section 559.904, Motor Vehicle Repair Shop Registration</a></li>
<li>Florida Statutes 2026, <a href="http://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&amp;URL=0500-0599/0559/Sections/0559.905.html" rel="nofollow noopener">section 559.905, Written Repair Estimate and Disclosure Statement</a></li>
<li>Florida Statutes 2026, <a href="http://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&amp;URL=0500-0599/0559/Sections/0559.909.html" rel="nofollow noopener">section 559.909, Charges in Excess of the Estimate</a></li>
<li>Florida Department of Agriculture and Consumer Services, <a href="https://www.fdacs.gov/Business-Services/Motor-Vehicle-Repair" rel="nofollow noopener">Motor Vehicle Repair</a>, read October 12, 2026</li>
<li>Trackara Pro, <a href="https://pro.trackara.app/blog/mobile-mechanic-hourly-rate" rel="nofollow noopener">Mobile Mechanic Hourly Rate in 2026</a>, May 25, 2026</li>
<li>autoGMS, <a href="https://myautogms.com/blog/mechanic-hourly-labor-rate-in-2025" rel="nofollow noopener">Mechanic Labor Rate in 2026</a>, April 28, 2026</li>
</ul>""",
    },
    {
        "slug": "30-60-90-rule-for-cars",
        "title": "What Is the 30-60-90 Rule for Cars? The Orlando Version",
        "desc": "The 30-60-90 rule in plain English, what each service covers, what it costs, "
                "and why Orlando heat, traffic and salt air move the dates up.",
        "date": "2026-10-10", "tag": "Maintenance",
        "faqs": [
            ("What is the 30-60-90 rule for cars?",
             "It is a rule of thumb that says a car needs a bigger service at 30,000, 60,000 "
             "and 90,000 miles. At 30k you get filters, a tire rotation and an inspection. At "
             "60k you add fluids and sometimes spark plugs. At 90k comes the timing belt and "
             "water pump on engines that have a belt. Your owner's manual has the real list "
             "for your car."),
            ("Is the 30-60-90 rule the same for every car?",
             "No. It is a shortcut, not a factory schedule. Some spark plugs now last up to "
             "120,000 miles, many engines use a timing chain instead of a belt, and most cars "
             "need oil far more often than every 30,000 miles. Use the rule to know when a big "
             "visit is coming. Use the manual to know what goes in it."),
            ("Does driving in Orlando count as severe service?",
             "For most drivers, yes. The Car Care Council lists stop and go traffic, short "
             "trips, salty air and very hot weather as severe driving. Orlando has a normal "
             "July high of 92 degrees and a normal July low of 73, so the heat never really "
             "lets up. Pick the severe schedule in your owner's manual."),
            ("How long does a car battery last in Florida?",
             "AAA says a battery in a hot southern place lasts about three years, compared "
             "with five years or more up north. AAA suggests a yearly test once a battery hits "
             "its third year. In Orlando that means most cars are on a second battery before "
             "they reach the 60,000 mile service."),
            ("Will using an independent mechanic void my warranty?",
             "No. The FTC says you can choose a dealer, an independent shop or do the work "
             "yourself, and a company cannot void your warranty just for that choice. It can "
             "still deny a claim if the outside work caused the damage. Keep every receipt."),
            ("How much does a 90,000 mile service cost?",
             "It depends on whether your engine has a timing belt. RepairPal puts the "
             "national average for a timing belt replacement at $918 to $1,338 before tax. "
             "If your engine has a chain, the 90k visit is mostly inspection and fluids and "
             "costs far less. Ask for the list item by item, not as one package price."),
        ],
        "body": """
<p>The 30-60-90 rule is the oldest shortcut in car care. It says your car needs a bigger
service at 30,000 miles, again at 60,000, and again at 90,000. It is a good rule. It is
also a national rule, and Orlando is not a national kind of place to drive.</p>
<p>Here is the whole thing in plain English, what goes into each visit, what the big items
cost, and the three Central Florida conditions that move every date on the chart.</p>

<h2>What the 30-60-90 Rule Really Means</h2>
<p>The rule is a reminder, not a law and not a factory schedule. Jalopnik made the same
point in a piece on November 25, 2025. It called the rule a good template, mainly for older
and used cars, and said your owner's manual should win when the two disagree. It also noted
that some spark plugs are now rated for up to 120,000 miles, which already breaks the 60k
line for a lot of cars.</p>
<p>So use the rule for one job. It tells you when a big visit is coming. The manual tells
you what goes in it.</p>
<p>Miles also turn into years. The Federal Highway Administration puts the average driver
at 13,476 miles a year. At that pace, here is when each milestone shows up. This is a worked
example, not a promise.</p>
<div class="symwrap"><table class="sym">
<tr><th>Milestone</th><td><b>About how old the car is at 13,476 miles a year</b></td></tr>
<tr><th>30,000 miles</th><td>2 years and 3 months</td></tr>
<tr><th>60,000 miles</th><td>4 years and 5 months</td></tr>
<tr><th>90,000 miles</th><td>6 years and 8 months</td></tr>
</table></div>
<p>Keep those ages in mind. In Florida, some parts wear out by the calendar long before the
odometer gets a vote.</p>

<h2>The 30-60-90 Checklist, With the Orlando Add-Ons</h2>
<p>The left column is what most guides and most manuals put at each stop. The right column
is what we would add for a car that lives in Orange, Seminole or Osceola County.</p>
<div class="symwrap"><table class="sym">
<tr><th>Milestone</th><td><b>The usual list</b></td><td><b>Add this in Orlando</b></td></tr>
<tr><th>30,000 miles</th><td>Oil and filter if due, engine air filter, cabin air filter,
tire rotation, and a look at brakes, belts, hoses and every fluid</td><td>A real battery load
test, an A/C check while the car idles, and a brake fluid moisture test</td></tr>
<tr><th>60,000 miles</th><td>Brake fluid, coolant and transmission fluid as your manual
lists them, spark plugs if they are the 60k kind, and a look at shocks, struts and ball
joints</td><td>Expect a second battery by now, and check the brake lines and exhaust
hangers for rust if the car sees the beach</td></tr>
<tr><th>90,000 miles</th><td>Timing belt and water pump if your engine has a belt, a check
of long life spark plugs, and the exhaust, suspension and steering</td><td>A full underbody
look for salt rust, cooling hoses squeezed for soft spots, and the A/C condenser fan
tested</td></tr>
</table></div>
<p>Oil is not really on this chart. Almost every car needs oil many times before 30,000
miles. Follow the interval in your manual or your oil life monitor, and use the severe one.
More on that next.</p>

<h2>Why Orlando Driving Counts as Severe Service</h2>
<p>Every owner's manual has two schedules. Normal and severe. Most people pick normal
because it sounds like them. In Central Florida it almost never is.</p>
<p>The Car Care Council lists what counts as severe driving. Stop and go traffic, short
trips, heavy loads, dusty or salty air, and very hot or very cold weather. Orlando checks
most of those boxes before lunch.</p>

<h3>The Heat Never Clocks Out</h3>
<p>The National Weather Service office in Melbourne lists Orlando's normal July high at 92
degrees and the normal July low at 73, based on 1991 to 2020 data. That low matters. The
car never gets a cool night to recover. July 2026 averaged 85.2 degrees in Orlando, tied for
the second warmest July on that record, behind only July 2024.</p>
<p>Under the hood it is far worse. AAA says engine bay heat can top 200 degrees in hot
weather. Heat speeds up the chemistry that wears out batteries, cooks rubber hoses and
thins tired oil.</p>
<p>Batteries show it first. AAA says a battery in a hot southern place lasts about three
years, compared with five or more up north, and it suggests a test every year once a battery
reaches year three. Put that next to the table above. By the 60,000 mile visit, a typical
Orlando car is about four and a half years old. If its batteries last three years, it is
already on its second one, and the third is due around the 90k mark. That is why a battery
test belongs in every big service, even when the car still cranks fine. Here is <a
href="/blog/florida-heat-car-battery/">why Florida heat kills batteries without warning</a>.</p>

<h3>Humidity Gets Into Your Brake Fluid</h3>
<p>Most brake fluid pulls water out of the air. Florida has a lot of water in the air. The
federal brake fluid standard tests for exactly this. New DOT 3 fluid must not boil below 401
degrees. After a set dose of moisture in a lab, it only has to hold to 284 degrees. That is
117 degrees of safety margin gone, and boiled brake fluid means a soft pedal when you need
it most.</p>
<p>So do not just flush brake fluid because the odometer says 60k. Have it tested at 30k and
at every brake job, and change it on your manual's schedule or sooner if the test fails.</p>

<h3>Salt Air Rides Home From the Beach</h3>
<p>Orlando sits inland, but plenty of local cars spend weekends at Cocoa Beach or New Smyrna.
The Car Care Council counts salty air as severe driving for a reason. Salt eats brake lines,
exhaust hangers and the bolts that hold suspension parts. A rinse under the car after a beach
day is cheap. At 60k and 90k, ask for someone to look up underneath, not just under the
hood.</p>

<h3>I-4 Is a Brake Test Every Day</h3>
<p>Stop and go traffic is on the severe list too. Brakes wear per stop, not per mile, and a
crawl on I-4 is a lot of stops. That is why pads on Orlando commuter cars often come due well
before any 30-60-90 chart says so. We wrote up <a href="/blog/i4-traffic-brake-wear/">how
I-4 traffic wears brakes</a> and what each brake noise means.</p>

<h2>What the Big Items Cost</h2>
<p>You will see guides quote one price for the whole 60k or 90k service. Ignore it. A
milestone service is a list, not a product, and two cars at 60,000 miles can need very
different lists. Price it line by line.</p>
<p>Here are national averages from RepairPal for the three biggest line items, checked on
October 10, 2026. They do not include tax and do not adjust for location, so use them as a
gut check, not a quote.</p>
<div class="symwrap"><table class="sym">
<tr><th>Line item</th><td><b>National average (RepairPal)</b></td><td><b>When it usually comes up</b></td></tr>
<tr><th>Timing belt replacement</th><td>$918 to $1,338</td><td>90k, only on engines with a belt</td></tr>
<tr><th>Spark plug replacement</th><td>$288 to $399</td><td>60k for some plugs, up to 120k for others</td></tr>
<tr><th>Transmission fluid change</th><td>$294 to $356</td><td>60k on many cars, per your manual</td></tr>
</table></div>
<p>The timing belt is the one that matters most. On many engines a snapped belt lets the
valves hit the pistons, and a cheap belt job becomes an engine job. If your car has a belt
and you are near or past the mileage in your manual, do not wait on it. If it has a chain,
there is no 90k belt job at all, and nobody should be selling you one.</p>

<h2>Where the 30-60-90 Rule Gets It Wrong</h2>
<p>The rule is useful. It is also old. Here is where it can steer you wrong.</p>
<ul>
<li><b>It ignores time.</b> A car driven 5,000 miles a year still ages. Batteries, brake
fluid, coolant and rubber all wear by the calendar, and Florida heat speeds that up.</li>
<li><b>It assumes a timing belt.</b> Many newer engines use a chain. Check your manual
before you budget for the biggest 90k item.</li>
<li><b>It assumes old spark plugs.</b> Some plugs are rated far past 60,000 miles. Changing
good plugs early is money spent for nothing.</li>
<li><b>It gets sold as a package.</b> A shop menu can tuck in flushes your manual never
calls for. Ask one question about every line. Where is that in my owner's manual?</li>
</ul>

<h2>Do You Have to Go Back to the Dealer?</h2>
<p>No. On July 7, 2022, the Federal Trade Commission said plainly that you choose where your
car gets serviced. A dealer, an independent shop, or your own garage. Under the
Magnuson-Moss Warranty Act, a company cannot void your warranty just because someone else did
the work. It can still deny a claim if the outside work caused the damage, so the job has to
be done right.</p>
<p>The fix is simple. Keep every receipt with the date, the mileage and what was done. A
folder in the glove box or photos on your phone both work. Those records also help when you
sell the car.</p>

<h2>How to Use the Rule This Week</h2>
<ol class="proc">
<li><b>Find your schedule</b><p>Open the owner's manual or the maker's app and find the
maintenance section. Pick the severe schedule if you drive in Orlando.</p></li>
<li><b>Check the odometer and the age</b><p>Note both. Whichever one hits a service first
wins.</p></li>
<li><b>Look up your timing setup</b><p>Belt or chain. This one answer decides whether 90k is
a small visit or a big one.</p></li>
<li><b>Test the battery if it is three or older</b><p>AAA says yearly from year three. In
Florida, do not skip it.</p></li>
<li><b>Ask for the list, not the package</b><p>Every line should match your manual or a
test result you can see.</p></li>
<li><b>Save the receipt</b><p>Date, mileage and work done. It protects your warranty and
your resale price.</p></li>
</ol>
<p>Coming up on 30, 60 or 90? We do the <a href="/services/mobile-oil-change/">oil
service</a>, <a href="/services/battery-replacement/">battery testing</a>, and <a
href="/services/brake-repair/">brake work</a> in your driveway, and we will tell you straight
which items on the list need a shop lift instead. Call {PHONE}.</p>

<h2>Sources</h2>
<ul class="sources">
<li>Jalopnik, <a href="https://www.jalopnik.com/2031332/does-30-60-90-rule-for-car-maintenance-make-sense/" rel="nofollow noopener">Does the 30-60-90 Rule for Car Maintenance Actually Make Sense?</a>, November 25, 2025</li>
<li>Federal Highway Administration, <a href="https://www.fhwa.dot.gov/ohim/onh00/bar8.htm" rel="nofollow noopener">Average Annual Miles per Driver by Age Group</a></li>
<li>Car Care Council via AutoInc, <a href="https://www.autoinc.org/?p=14025" rel="nofollow noopener">Take Action to Reduce Effects of Severe Driving</a>, October 1, 2019</li>
<li>National Weather Service Melbourne, <a href="https://www.weather.gov/media/mlb/climate/mcoJUL.pdf" rel="nofollow noopener">Orlando July Normals and Records</a>, read October 10, 2026</li>
<li>AAA, <a href="https://www.aaa.com/autorepair/articles/how-long-do-car-batteries-last" rel="nofollow noopener">How Long Do Car Batteries Last</a></li>
<li>49 CFR 571.116, <a href="https://www.law.cornell.edu/cfr/text/49/571.116" rel="nofollow noopener">Federal Motor Vehicle Safety Standard 116, Brake Fluids</a></li>
<li>RepairPal, <a href="https://repairpal.com/estimator/timing-belt-replacement-cost" rel="nofollow noopener">Timing Belt Replacement Cost</a>, <a href="https://repairpal.com/estimator/spark-plug-replacement-cost" rel="nofollow noopener">Spark Plug Replacement Cost</a> and <a href="https://repairpal.com/estimator/transmission-fluid-change-cost" rel="nofollow noopener">Transmission Fluid Change Cost</a>, read October 10, 2026</li>
<li>Federal Trade Commission, <a href="https://consumer.ftc.gov/consumer-alerts/2022/07/ftc-says-companies-warranty-restrictions-were-illegal" rel="nofollow noopener">FTC Says Companies' Warranty Restrictions Were Illegal</a>, July 7, 2022</li>
</ul>""",
    },
    {
        "slug": "florida-heat-car-battery",
        "title": "Why Florida Heat, Not Cold, Kills Your Car Battery",
        "desc": "Orlando batteries die young, and summer is the murderer. How heat wrecks a "
                "battery, the warning signs, and when to test instead of guess.",
        "date": "2026-08-10", "tag": "Batteries",
        "body": """
<p>Up north, everyone blames winter for dead batteries. In Orlando, the killer works the
opposite shift. Heat is what actually destroys a car battery. Cold just delivers the news.</p>
<h2>What heat does inside the battery</h2>
<p>A car battery is a box of chemistry, and chemistry speeds up with temperature. At Florida
underhood temperatures, the reactions that age a battery, plate corrosion and water loss, run at double speed or worse. Every July cooking session permanently shaves capacity. The
battery still starts the car all summer, because a hot battery cranks easily. Then the first
cool snap or a week of short trips asks it for capacity it no longer has, and you get the
click.</p>
<h2>Why Orlando batteries skip the warning phase</h2>
<p>The classic warning of slow, dragging cranks often never happens here, because warm
batteries crank briskly right up until they can't. That's why so many Central Florida
batteries seem to die "suddenly." They didn't. They died over two summers, quietly.</p>
<h2>The three-to-four-year rule</h2>
<p>National battery-life averages run four to five years. Florida trims that to roughly three
to four. If your battery is past its third birthday, a free load test once a year is cheap
insurance. It takes minutes and tells you the truth a jump-start hides.</p>
<h2>Before you buy a battery, test the system</h2>
<p>A car that keeps needing jumps has one of three problems: a battery that can't hold
charge, an alternator that isn't refilling it, or a parasitic drain emptying it overnight. A
new battery only fixes the first one. We test all three at your driveway before selling
anything. That's the whole point of our <a href="/services/battery-replacement/">mobile
battery service</a>, and it's why our customers don't buy three batteries for one alternator
problem.</p>
<p>Battery acting suspicious? Call {PHONE} and we'll test it where it sits.</p>""",
    },
    {
        "slug": "mobile-mechanic-vs-tow-to-shop",
        "title": "Mobile Mechanic vs. Towing to a Shop: The Real Math",
        "desc": "When your car won't start in Orlando, the tow-plus-shop route costs more "
                "than most people expect. Here's the honest comparison.",
        "date": "2026-07-28", "tag": "Guides",
        "body": """
<p>Your car won't start in the driveway. The reflex is: call a tow, send it to a shop. Before
you do, run the actual numbers. Because the tow route carries costs nobody mentions.</p>
<h2>The tow route, itemized</h2>
<p>First the tow itself. A local hook in Orlando typically runs well north of a hundred
dollars once mileage is counted. Then the shop's diagnostic fee. Then the queue: your car
takes its place behind everyone else's, which is often measured in days. Add the rides
you'll need while it sits, or the rental. And at the end, the repair bill itself. The one
part both routes share.</p>
<h2>The mobile route</h2>
<p>A mobile mechanic drives to the problem. One visit fee covers the trip and the diagnosis,
and the most common no-start causes, <a href="/services/battery-replacement/">batteries</a>,
<a href="/services/starter-alternator-repair/">starters, alternators</a>, cables, relays. Are fixed on the spot, usually inside a couple of hours. The car never leaves your driveway,
and you never leave your day.</p>
<h2>When the shop route wins</h2>
<p>Honesty matters here: some jobs genuinely need a lift, a press, or a machine shop. Internal transmission work, clutch jobs, alignment. If yours is one, a good mobile mechanic
says so at the diagnosis stage, and now you're towing the car <em>once, to the right place,
knowing what's wrong</em>. Which is still a better position than towing it blind.</p>
<h2>The rule of thumb</h2>
<p>If the car won't crank, won't fire, or died where it's parked, have it diagnosed where it
sits. Worst case you pay for an answer. Best case, which is most cases, the car is running
by lunch. That's the service: <a href="/services/no-start-repair/">no-start help across the
Orlando metro</a>, seven days a week.</p>""",
    },
    {
        "slug": "check-engine-light-what-to-do",
        "title": "Check Engine Light On in Orlando? Do This First",
        "desc": "Steady vs. flashing, safe vs. stop-now, and why the free parts-store code "
                "read keeps costing drivers money.",
        "date": "2026-07-14", "tag": "Diagnostics",
        "body": """
<p>The check engine light has one job: telling you the computer stored a fault. What it
refuses to tell you is how bad. Here's how to read the situation like a mechanic.</p>
<h2>First: steady or flashing?</h2>
<p>A <strong>steady light</strong> means a fault is logged but the engine isn't in immediate
danger. Drive gently, get it diagnosed soon. A <strong>flashing light</strong> means an
active misfire is pumping raw fuel into the catalytic converter, which is being cooked as
you drive. Pull over, shut it down, and call. A converter costs many times what a misfire
costs.</p>
<h2>The free code read trap</h2>
<p>The parts store will read your code for free and sell you the part the code mentions.
Here's the problem: a code names a <em>circuit</em>, not a <em>part</em>. A lean code can be
a vacuum leak, a tired fuel pump, a dirty airflow sensor, or a failing O2 sensor. Guess
wrong and you've spent real money to keep the light on. The store isn't being dishonest. Reading a code just isn't diagnosis.</p>
<h2>What actual diagnosis looks like</h2>
<p>Live data. Freeze-frame from the moment the fault set. Then physical tests. Smoke,
voltage, pressure. On the suspect circuit until the failed component is proven. That's what
our <a href="/services/check-engine-light-diagnostics/">mobile diagnostic visit</a> does in
your driveway, and it's why the part we replace is the part that was broken.</p>
<h2>"But the light went off by itself"</h2>
<p>The fault is still stored, and it will vote again. Intermittent faults are the cheapest
ones to fix early and the most expensive ones to ignore. They choose their moment, and the
moment is never good. We can read history codes even after the light clears.</p>
<p>Light on right now? Call {PHONE}. We come to you anywhere in the Orlando area.</p>""",
    },
    {
        "slug": "car-ac-warm-at-idle",
        "title": "Car A/C Cold on the Highway but Warm at Red Lights? Classic Orlando Problem",
        "desc": "The stoplight-warm A/C almost always has one cause. And it isn't low "
                "refrigerant. What's actually happening and how it gets fixed.",
        "date": "2026-06-30", "tag": "A/C",
        "body": """
<p>It's the most Orlando car complaint there is: ice cold at 60 mph on I-4, then warmer and
warmer sitting at a light on Colonial. Most people assume it needs "a recharge." Usually,
it doesn't.</p>
<h2>Why speed changes your A/C</h2>
<p>Your A/C dumps heat through the condenser at the front of the car. At highway speed,
airflow through it is free. The car's motion does the work. Stopped at a light, that
airflow has to come from a fan. If the condenser fan is weak, slow, or dead, the system
can't shed heat at idle, pressures climb, and cold air fades exactly when the car stops
moving.</p>
<h2>Why the recharge-can shortcut backfires</h2>
<p>A can of refrigerant with a gauge tops up pressure without asking where the refrigerant
went. If there's a leak, you're renting cold air by the week. If the real fault is the fan,
you've added refrigerant a system that wasn't low. And overcharging raises pressures that
are already too high at idle. Either way the compressor absorbs the abuse, and the
compressor is the most expensive part in the system.</p>
<h2>What a real diagnosis checks</h2>
<p>Pressures on both sides, compressor engagement, fan operation at idle, and leak detection
before anything is added. Our <a href="/services/ac-repair/">mobile A/C service</a> runs
that whole checklist at your home or office. And in a town where A/C is life support ten
months a year, it's one of our most-booked visits.</p>
<p>One more Florida special: a musty smell at startup is condensation living in the
evaporator box. It's fixable, and running the fan without A/C for the last minute of your
drive helps keep it from coming back.</p>""",
    },
    {
        "slug": "used-car-flood-damage-orlando",
        "title": "Buying a Used Car in Orlando? Check for Flood Damage First",
        "desc": "After every hurricane season, flooded cars quietly enter the Florida used "
                "market. Some with clean titles. The tells, and how an inspection protects you.",
        "date": "2026-06-16", "tag": "Buying",
        "body": """
<p>Florida's used-car market has a seasonal rhythm nobody advertises: a few months after
every major storm, flood-damaged cars start appearing on lots and marketplace listings. Dried out, detailed, and priced to move. Some carry salvage titles. The dangerous ones
don't.</p>
<h2>Why clean titles lie</h2>
<p>Title washing, moving a car through states with looser branding rules, can launder a
flood history off the paperwork. Insurance databases catch some of it. The car itself,
though, always tells the truth if you know where to look.</p>
<h2>The tells</h2>
<p>Silt or fine sand in the seat tracks and under the carpet. Corrosion on electrical
connector pins above the floor line. Pins never get wet in normal life. Foggy headlamps or
a water line inside them. Brand-new carpet in an old car. Rust on seat springs and under-dash
brackets. And the classic: a musty smell losing a fight with a powerful air freshener.</p>
<h2>Why flood cars are a special kind of bad</h2>
<p>A flooded engine can be cleaned. Flooded <em>electronics</em> fail one connector at a
time for years. A window here, a sensor there, an airbag module eventually. You don't buy
one repair bill, you subscribe to them.</p>
<h2>The hundred-dollar-class defense</h2>
<p>A <a href="/services/pre-purchase-inspection/">pre-purchase inspection</a> checks the
flood tells, scans for stored and recently-cleared codes, measures the brakes, and road
tests the car. Before the money moves. We meet the car wherever it's being sold, anywhere
in the Orlando area. A seller who won't allow an inspection has answered your question for
free.</p>""",
    },
    {
        "slug": "i4-traffic-brake-wear",
        "title": "What I-4 Traffic Actually Does to Your Brakes",
        "desc": "Stop-and-go on I-4 and the 408 wears brakes on a different schedule than "
                "the owner's manual expects. The sounds that matter and the cheap-to-fix window.",
        "date": "2026-06-02", "tag": "Brakes",
        "body": """
<p>Brake pads carry a mileage expectation set by engineers picturing mixed driving. I-4 at
5:30pm is not mixed driving. It's a brake dyno with billboards.</p>
<h2>The arithmetic of stop-and-go</h2>
<p>Brakes wear per <em>stop</em>, not per mile. A highway mile costs your pads almost
nothing; a crawling mile through the Ultimate interchange can involve a dozen brake
applications. Commuters doing I-4, the 408, or the tourist-corridor crawl routinely wear
pads in 25 to 40k miles. Half of what the manual implies. Rideshare and delivery drivers,
faster still.</p>
<h2>The sounds, ranked by expense</h2>
<p><strong>Squeal at low speed</strong>. The wear indicator. This is the cheap warning:
pads are due, rotors are probably fine. <strong>Grinding</strong>. The pad is gone and
its steel backing is machining your rotor with every stop. The bill just grew.
<strong>Shudder from highway speed</strong>. Uneven or warped rotors; stopping distances
are growing. <strong>A soft pedal that sinks</strong>. Hydraulics. Stop driving and call.</p>
<h2>The cheap-to-fix window</h2>
<p>Almost every expensive brake job we do was a cheap brake job a month earlier. Acting on
the squeal instead of the grind is routinely a three-figure difference. This is also the
easiest repair to have done at work: we do <a href="/services/brake-repair/">complete brake
jobs</a> in office parking lots all week. Measurements shown, price approved first, old
parts in your hand.</p>
<p>Hearing something at stops? Call {PHONE} and we'll measure it. At your place, with the
numbers in front of you.</p>""",
    },
]

# ------------------------------------------------------------------ HELPERS
def esc(s): return html.escape(s, quote=True)

def fmt(s): return s.replace("{BIZ}", BIZ)

def url(path):
    if path in ("", "/", "index"): return DOMAIN + "/"
    return DOMAIN + "/" + path.strip("/") + "/"

def ldjson(*objs):
    graph = {"@context": "https://schema.org", "@graph": [o for o in objs if o]}
    return ('<script type="application/ld+json">'
            + json.dumps(graph, ensure_ascii=False) + "</script>")

def schema_business():
    return {
        "@type": ["AutoRepair", "LocalBusiness"],
        "@id": DOMAIN + "/#organization",
        "name": BIZ,
        "slogan": TAGLINE,
        "telephone": PHONE_TEL,
        "email": EMAIL,
        "url": DOMAIN + "/",
        "priceRange": "$$",
        "image": DOMAIN + "/img/og.jpg",
        "logo": DOMAIN + "/img/logo.png",
        "description": f"Mobile mechanic serving {CITY_MAIN}, {STATE_FULL} and the surrounding "
                       "area. On-site auto repair, diagnostics, brakes, batteries, oil changes, "
                       "A/C repair and pre-purchase inspections. We come to you.",
        "areaServed": [{"@type": "City", "name": f"{n}, FL"} for _, n, _, _ in CITIES],
        "address": {"@type": "PostalAddress", "addressLocality": CITY_MAIN,
                    "addressRegion": STATE, "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": GEO_LAT, "longitude": GEO_LNG},
        "hasMap": GMB_URL,
        "sameAs": [GMB_URL],
        "knowsAbout": [s["name"] for s in SERVICES],
        "publishingPrinciples": DOMAIN + "/about/#check",
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": RATING,
                            "reviewCount": REVIEW_CT, "bestRating": "5"},
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification",
             "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
             "opens": "09:00", "closes": "22:00"},
            {"@type": "OpeningHoursSpecification",
             "dayOfWeek": ["Sunday"], "opens": "09:00", "closes": "18:00"},
        ],
        "hasOfferCatalog": {
            "@type": "OfferCatalog", "name": "Mobile Auto Repair Services",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"]}}
                for s in SERVICES]},
    }

def schema_breadcrumb(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": url(u)}
        for i, (n, u) in enumerate(items)]}

def schema_faq(faqs):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q,
         "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

def schema_reviews():
    return [{"@type": "Review",
             "itemReviewed": {"@id": DOMAIN + "/#organization"},
             "author": {"@type": "Person", "name": n},
             "reviewRating": {"@type": "Rating", "ratingValue": str(s), "bestRating": "5"},
             "reviewBody": t, "datePublished": d}
            for n, s, d, t in REVIEWS]

def schema_blogpost(p):
    return {"@type": "BlogPosting", "headline": p["title"],
            "description": p["desc"], "datePublished": p["date"],
            "dateModified": p["date"],
            "mainEntityOfPage": url(f"blog/{p['slug']}"),
            "author": {"@type": "Organization", "name": BIZ},
            "publisher": {"@id": DOMAIN + "/#organization"}}

def schema_service(name, desc, area=None):
    return {"@type": "Service", "name": name, "description": desc,
            "provider": {"@id": DOMAIN + "/#organization"},
            "areaServed": {"@type": "City", "name": area or f"{CITY_MAIN}, {STATE}"},
            "serviceType": name}

# ------------------------------------------------------------------ ICONS
def icon(name, cls="ic"):
    P = {
        "van":       '<path d="M1 16V7a1 1 0 0 1 1-1h11v10M13 9h5l4 4v3h-2M1 16h1m4 0h8" /><circle cx="5" cy="17" r="2"/><circle cx="17" cy="17" r="2"/>',
        "scan":      '<circle cx="12" cy="12" r="8"/><path d="M12 4V2M12 22v-2M4 12H2m20 0h-2M12 8v4l3 2"/>',
        "brake":     '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/><path d="M12 3v3m0 12v3M3.6 7.5l2.6 1.5m11.6 6 2.6 1.5M3.6 16.5l2.6-1.5m11.6-6 2.6-1.5"/>',
        "oil":       '<path d="M12 3s6 7 6 11a6 6 0 0 1-12 0c0-4 6-11 6-11z"/><path d="M9.5 14a2.5 2.5 0 0 0 2.5 2.5"/>',
        "battery":   '<rect x="2" y="8" width="18" height="11" rx="2"/><path d="M6 8V5h4v3m4 0V5h4v3M22 11v5M6 13.5h4m6-2v4m-2-2h4"/>',
        "bolt":      '<path d="M13 2 4 14h6l-1 8 9-12h-6l1-8z"/>',
        "snow":      '<path d="M12 2v20M4 6l16 12M20 6 4 18M12 2l-2 3h4l-2-3M12 22l-2-3h4l-2 3M4 6l3.5.5L6 10 4 6M20 18l-3.5-.5L18 14l2 4M20 6l-3.5.5L18 10l2-4M4 18l3.5-.5L6 14l-2 4"/>',
        "key":       '<circle cx="7.5" cy="15.5" r="4.5"/><path d="M10.7 12.3 21 2m-4 4 3 3m-6 0 2 2"/>',
        "clipboard": '<rect x="5" y="4" width="14" height="18" rx="2"/><path d="M9 4a3 3 0 0 1 6 0M9 11h6M9 15h6M9 19h3"/>',
        "wrench":    '<path d="M14 6a4 4 0 0 0-5.3 5.3l-5 5a1.5 1.5 0 0 0 2.1 2.1l5-5A4 4 0 0 0 18 8l-2.5 2.5L13 8l2.5-2.5z"/>',
        "phone":     '<path d="M5 3h4l2 5-2.5 1.5a12 12 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 5a2 2 0 0 1 2-2z"/>',
        "pin":       '<path d="M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
        "clock":     '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
        "check":     '<path d="M4 12.5 9.5 18 20 6"/>',
        "star":      '<path d="m12 2.5 2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z"/>',
        "menu":      '<path d="M3 6h18M3 12h18M3 18h18"/>',
        "close":     '<path d="M5 5l14 14M19 5 5 19"/>',
        "caret":     '<path d="m6 9 6 6 6-6"/>',
        "arrow":     '<path d="M4 12h16m-6-6 6 6-6 6"/>',
        "mail":      '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 7L22 7"/>',
        "calendar":  '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4m8-4v4M3 10h18"/>',
        "shield":    '<path d="M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5l-8-3z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
        "sun":       '<circle cx="12" cy="12" r="4"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3M4.9 4.9l2.1 2.1m10 10 2.1 2.1M19.1 4.9 17 7m-10 10-2.1 2.1"/>',
    }
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{P[name]}</svg>')

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E"
           "%3Crect width='24' height='24' rx='5' fill='%230C0F14'/%3E"
           "%3Cg fill='none' stroke='%23FF7A1F' stroke-width='1.8' stroke-linecap='round' "
           "stroke-linejoin='round'%3E%3Cpath d='M14 6a4 4 0 0 0-5.3 5.3l-5 5a1.5 1.5 0 0 0 "
           "2.1 2.1l5-5A4 4 0 0 0 18 8l-2.5 2.5L13 8l2.5-2.5z'/%3E%3C/g%3E%3C/svg%3E")

print("Data ready:", len(SERVICES), "services,", len(CITIES), "cities.")

# ================================================================== CSS
CSS = """
:root{
  --paper:#faf7f1; --white:#ffffff; --line:#e9e1d3; --line2:#f1ebdf;
  --ink:#20242d; --ink2:#12151c; --dim:#5c6370; --faint:#8a8f9a;
  --sun:#f26a1b; --sun2:#f79433; --gold:#f7b955; --sundeep:#b8460a;
  --grad:linear-gradient(100deg,var(--sun) 0%,var(--sun2) 55%,var(--gold) 100%);
  --r:16px; --rs:10px;
  --shadow:0 14px 40px -18px rgba(32,36,45,.18);
  --shadow-lg:0 24px 60px -20px rgba(32,36,45,.28);
  --disp:'Bricolage Grotesque',system-ui,sans-serif;
  --body:'Inter',system-ui,sans-serif;
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{font-family:var(--body);font-size:16.5px;line-height:1.68;color:var(--ink);
  background:var(--paper);-webkit-font-smoothing:antialiased}
img,svg{max-width:100%}
a{color:var(--sundeep);text-decoration:none}
a:hover{color:var(--sun)}
a:focus-visible,button:focus-visible,summary:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{outline:3px solid var(--sundeep);outline-offset:3px}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{transition:none!important;animation:none!important}html{scroll-behavior:auto}}
.wrap{max-width:1140px;margin:0 auto;padding:0 22px}
h1,h2,h3,h4{font-family:var(--disp);font-weight:700;line-height:1.12;
  letter-spacing:-.015em;color:var(--ink)}
.ic{width:1.15em;height:1.15em;vertical-align:-.2em;flex:none}

/* kicker + gradient text */
.kick{display:inline-flex;align-items:center;gap:.5em;font-size:.95rem;font-weight:700;
  color:var(--sundeep)}
.kick::before{content:"";width:26px;height:2px;background:var(--grad);border-radius:2px}
.gtx{background:linear-gradient(100deg,var(--sundeep),var(--sun2));
  -webkit-background-clip:text;background-clip:text;color:transparent}

/* buttons */
.btn{display:inline-flex;align-items:center;gap:.55em;font-family:var(--disp);font-weight:700;
  font-size:1rem;padding:.85em 1.5em;border-radius:999px;border:1.5px solid transparent;
  cursor:pointer;transition:transform .15s,box-shadow .15s;white-space:nowrap}
.btn:active{transform:scale(.97)}
.btn-sun{background:var(--grad);color:#231000;box-shadow:0 10px 26px -10px rgba(242,106,27,.55)}
.btn-sun:hover{box-shadow:0 14px 34px -10px rgba(242,106,27,.7);transform:translateY(-2px);color:#231000}
.btn-ghost{border-color:#d9cfbd;color:var(--ink);background:var(--white)}
.btn-ghost:hover{border-color:var(--sun);color:var(--sundeep)}
.band .btn-ghost{background:transparent;border-color:rgba(255,255,255,.35);color:#fff}
.band .btn-ghost:hover{border-color:var(--gold);color:var(--gold)}

/* util bar */
.util{background:var(--ink2);font-size:.85rem;padding:.5em 0}
.util .wrap{display:flex;justify-content:space-between;gap:1em;align-items:center}
.util span{display:inline-flex;align-items:center;gap:.45em;color:var(--gold)}
.util a{color:#fff;font-weight:700}

/* header */
.hdr{position:sticky;top:0;z-index:50;background:rgba(255,255,255,.88);
  backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
.hdr .wrap{display:flex;align-items:center;gap:1.4em;height:72px}
.brand{display:flex;align-items:center;gap:.6em;color:var(--ink);font-family:var(--disp);
  font-weight:800;font-size:1.12rem;line-height:1.1;margin-right:auto}
.brand:hover{color:var(--ink)}
.brand .mark{display:grid;place-items:center;width:42px;height:42px;border-radius:12px;
  background:var(--grad);color:#231000;flex:none}
.brand small{display:block;font-family:var(--body);font-weight:600;font-size:.66rem;
  letter-spacing:.15em;text-transform:uppercase;color:var(--dim)}
.nav{display:flex;gap:1.5em;align-items:center}
.nav a{color:var(--ink);font-weight:600;font-size:.95rem}
.nav a:hover{color:var(--sundeep)}
.nav-item{position:relative}
.nav-top{display:inline-flex;align-items:center;gap:.25em}
.dropdown{position:absolute;top:calc(100% + 14px);left:50%;transform:translateX(-50%) translateY(8px);
  background:var(--white);border:1px solid var(--line);border-radius:var(--r);min-width:290px;
  padding:.5em;display:flex;flex-direction:column;opacity:0;visibility:hidden;transition:.18s;
  box-shadow:var(--shadow-lg)}
.nav-item:hover .dropdown,.nav-item:focus-within .dropdown{opacity:1;visibility:visible;
  transform:translateX(-50%) translateY(0)}
.dropdown a{padding:.55em .9em;border-radius:var(--rs);font-size:.92rem;color:var(--ink)}
.dropdown a:hover{background:var(--paper);color:var(--sundeep)}
.dropdown .drop-all{color:var(--sundeep);border-bottom:1px solid var(--line);border-radius:0;
  margin-bottom:.35em}
.burger{display:none;background:none;border:0;color:var(--ink);cursor:pointer;padding:.4em}
.burger .ic{width:26px;height:26px}
.hdr .btn-call{font-size:.92rem;padding:.7em 1.2em}

/* mobile nav */
.mnav{position:fixed;inset:0;z-index:90;background:var(--white);display:none;
  flex-direction:column;gap:.15em;padding:4.5em 1.6em 2em;overflow:auto}
.mnav.open{display:flex}
.mnav a{color:var(--ink);font-family:var(--disp);font-weight:700;font-size:1.2rem;
  padding:.55em .2em;border-bottom:1px solid var(--line2)}
.mnav .x{position:absolute;top:1em;right:1em;background:var(--paper);border:1px solid var(--line);
  border-radius:50%;width:44px;height:44px;display:grid;place-items:center;color:var(--ink);cursor:pointer}
.mnav .x .ic{width:22px;height:22px}
.mdrop summary{color:var(--ink);font-family:var(--disp);font-weight:700;font-size:1.2rem;
  padding:.55em .2em;cursor:pointer;list-style:none;border-bottom:1px solid var(--line2)}
.msub{display:flex;flex-direction:column;padding-left:1em}
.msub a{font-size:.98rem;font-weight:500;color:var(--dim);border-bottom:0;padding:.45em .2em}
.mnav .btn{margin-top:1.2em;justify-content:center}

/* hero */
.hero{position:relative;overflow:hidden;
  background:
    radial-gradient(55% 80% at 88% 8%,rgba(247,148,51,.16),transparent 60%),
    radial-gradient(40% 60% at 5% 95%,rgba(242,106,27,.08),transparent 60%),
    var(--paper)}
.hero::after{content:"";position:absolute;inset:auto 0 0 0;height:1px;background:var(--line)}
.hero .wrap{padding:4.5em 22px;position:relative}
.hero .kick{margin-bottom:1em}
.hero h1{font-size:clamp(2.2rem,5.4vw,4rem);max-width:12em}
.hero p.lead{margin:1.2em 0 1.8em;font-size:1.12rem;color:var(--dim);max-width:36em}
.hero .cta{display:flex;gap:.9em;flex-wrap:wrap;align-items:center}
.hero .sub{margin-top:1.6em;display:flex;gap:1.5em;flex-wrap:wrap;font-size:.9rem;color:var(--dim)}
.hero .sub span{display:inline-flex;gap:.45em;align-items:center}
.hero .sub .ic{color:var(--sundeep)}
.hero-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:3em;align-items:center}
.hero-shot{position:relative}
.hero-shot .photo-card{aspect-ratio:1/1.02}
.hero-shot .tag{position:absolute;left:1em;bottom:1em;background:rgba(255,255,255,.92);
  backdrop-filter:blur(6px);border:1px solid var(--line);border-radius:999px;
  padding:.5em 1.1em;font-size:.85rem;font-weight:600;color:var(--sundeep);
  display:inline-flex;gap:.5em;align-items:center;box-shadow:var(--shadow)}

/* photos */
.photo-card{border-radius:var(--r);overflow:hidden;border:1px solid var(--line);
  box-shadow:var(--shadow-lg);line-height:0;background:var(--white)}
.photo-card img{width:100%;height:100%;object-fit:cover;display:block}

/* google badge */
.gbadge{display:inline-flex;align-items:center;gap:.6em;background:var(--white);
  border:1px solid var(--line);border-radius:999px;padding:.55em 1.2em;
  box-shadow:var(--shadow);font-size:.92rem;font-weight:600;color:var(--ink)}
.mrchip{display:inline-flex;align-items:center;gap:.7em;background:var(--white);border:1px solid var(--line);
  border-radius:999px;padding:.3em 1.1em .3em .5em;box-shadow:var(--shadow);color:var(--ink);text-decoration:none}
.mrchip:hover{border-color:var(--sun)}
.mrchip img{width:52px;height:auto;display:block}
.mrchip span{display:flex;flex-direction:column;line-height:1.25}
.mrchip b{font-family:var(--disp);font-size:15px}
.mrchip .t{font-size:14.5px;color:var(--dim)}
.mrcard{display:flex;align-items:center;gap:1.2em;flex-wrap:wrap}
.mrcard img{width:150px;height:auto;flex:none}
.mrcard div{flex:1 1 200px}
.mrcard h3{margin-bottom:.3em}
.mrcard p{font-size:15.5px;color:var(--dim);margin-bottom:.5em}
.mrcard a{font-weight:700;color:var(--sundeep)}
.gbadge .stars{color:var(--gold);display:inline-flex;gap:.1em}
.gbadge .stars .ic{width:15px;height:15px;fill:currentColor;stroke:none}
.gbadge b{font-family:var(--disp)}

/* sections */
.sec{padding:4.2em 0}
.sec-head{max-width:44em;margin-bottom:2.2em}
.sec-head h2{font-size:clamp(1.7rem,3.4vw,2.4rem);margin:.4em 0 .5em}
.sec-head p{color:var(--dim)}
.light{background:var(--white);border-top:1px solid var(--line2);border-bottom:1px solid var(--line2)}

/* cards */
.grid{display:grid;gap:1.1em}
.g3{grid-template-columns:repeat(3,1fr)}
.g2{grid-template-columns:repeat(2,1fr)}
.card{background:var(--white);border:1px solid var(--line);border-radius:var(--r);
  padding:1.6em;transition:transform .18s,box-shadow .18s,border-color .18s;position:relative;
  display:block;color:var(--ink);box-shadow:0 6px 20px -14px rgba(32,36,45,.14)}
a.card:hover{transform:translateY(-4px);border-color:rgba(242,106,27,.5);box-shadow:var(--shadow)}
.light .card{background:var(--paper)}
.card .cico{display:grid;place-items:center;width:52px;height:52px;border-radius:14px;
  background:rgba(242,106,27,.1);color:var(--sundeep);margin-bottom:1em}
.card .cico .ic{width:26px;height:26px}
.card h3{font-size:1.15rem;margin-bottom:.45em}
.card p{font-size:.94rem;color:var(--dim)}
.card .more{display:inline-flex;align-items:center;gap:.4em;margin-top:1em;font-weight:700;
  font-size:.88rem;color:var(--sundeep)}

/* steps */
.steps{counter-reset:step}
.step::before{counter-increment:step;content:"0" counter(step);font-family:var(--disp);
  font-weight:800;font-size:2.6rem;line-height:1;display:block;margin-bottom:.35em;
  background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}

/* checklist */
.checks{list-style:none;display:grid;gap:.7em;margin:1.4em 0}
.checks li{display:flex;gap:.7em;align-items:flex-start}
.checks .ic{color:var(--sun);margin-top:.25em}

/* split */
.split{display:grid;grid-template-columns:1.05fr .95fr;gap:3.5em;align-items:center}

/* testimonial / reviews */
.quote{background:var(--white);border:1px solid var(--line);border-radius:var(--r);
  padding:2.6em;max-width:52em;margin:0 auto;position:relative;box-shadow:var(--shadow)}
.quote::before{content:"\201C";position:absolute;top:-.15em;left:.35em;font-family:var(--disp);
  font-size:7em;line-height:1;background:var(--grad);-webkit-background-clip:text;
  background-clip:text;color:transparent;opacity:.85}
.quote blockquote{font-family:var(--disp);font-size:1.3rem;font-weight:600;
  line-height:1.45;margin-bottom:1em}
.quote figcaption{color:var(--dim);font-size:.95rem}
.stars{color:var(--gold);display:flex;gap:.2em;margin-bottom:1.1em}
.stars .ic{width:19px;height:19px;fill:currentColor;stroke:none}
.rev{display:flex;flex-direction:column}
.rev .stars{margin-bottom:.7em}
.rev blockquote{font-size:.97rem;color:var(--ink);flex:1;margin-bottom:1em}
.rev figcaption{color:var(--dim);font-size:.88rem;font-weight:600}
.rev figcaption span{display:block;font-weight:400;color:var(--faint);font-size:.8rem}

/* service map */
#svcmap{height:460px;border-radius:var(--r);border:1px solid var(--line);z-index:1;
  box-shadow:var(--shadow)}
#svcmap .leaflet-tile{filter:saturate(.55) brightness(1.03)}
.svcpin{display:block;width:14px;height:14px;border-radius:50%;background:var(--sun);
  border:2.5px solid #fff;box-shadow:0 2px 8px rgba(32,36,45,.4)}
.svcpin.home{width:20px;height:20px;background:var(--ink2);border-color:var(--gold)}
#svcmap .leaflet-popup-content{font-family:var(--body);font-size:14px}
#svcmap .leaflet-popup-content b{color:var(--sundeep)}
.maplegend{display:flex;gap:1.6em;flex-wrap:wrap;margin-top:1em;font-size:.88rem;color:var(--dim)}
.maplegend span{display:inline-flex;align-items:center;gap:.5em}
.pin-demo{display:inline-block;width:12px;height:12px;border-radius:50%;background:var(--sun);
  border:2px solid #fff;box-shadow:0 1px 4px rgba(32,36,45,.35)}
.pin-demo.home{background:var(--ink2);border-color:var(--gold)}

/* bite / snack / meal layers */
.bite{display:flex;gap:1em;align-items:flex-start;background:linear-gradient(100deg,rgba(242,106,27,.09),rgba(247,185,85,.12));
  border:1px solid rgba(242,106,27,.25);border-left:5px solid var(--sun);border-radius:var(--rs);
  padding:1.2em 1.4em;margin:0 0 1.6em}
.orl290p{margin:0 0 1.4em}
.orl290p a{display:inline-flex;align-items:center;min-height:44px;padding:.6em 1.1em;border-radius:6px;background:var(--sundeep);color:#fff;font-weight:600;font-size:.95rem;line-height:1.3;text-decoration:none;overflow-wrap:anywhere}
.orl290p a:hover,.orl290p a:focus-visible{background:var(--ink2);color:#fff}
.bite .ic{color:var(--sundeep);width:1.5em;height:1.5em;margin-top:.15em}
.bite p{font-family:var(--disp);font-weight:600;font-size:1.12rem;line-height:1.45;color:var(--ink)}
.bite p b{color:var(--sundeep)}
.snackbox{background:var(--white);border:1px solid var(--line);border-radius:var(--r);
  padding:1.4em 1.6em;margin:0 0 1.8em;box-shadow:var(--shadow)}
.snackbox h3{font-size:.82rem;letter-spacing:.16em;text-transform:uppercase;color:var(--sundeep);
  display:flex;gap:.5em;align-items:center;margin-bottom:.8em}
.snackbox ul{list-style:none;display:grid;gap:.5em}
.snackbox li{display:flex;gap:.6em;align-items:flex-start;font-size:.95rem}
.snackbox .ic{color:var(--sun);margin-top:.25em;width:1em;height:1em}

/* symptom table */
.sym{width:100%;border-collapse:collapse;margin:1.6em 0;font-size:.95rem}
.sym th,.sym td{text-align:left;padding:.9em 1em;border-bottom:1px solid var(--line);vertical-align:top}
.sym th{font-family:var(--disp);color:var(--sundeep);width:34%}
.sym tr:last-child th,.sym tr:last-child td{border-bottom:0}
.sym td b{font-family:var(--disp);color:var(--sundeep)}
.prose .symwrap{margin:0 0 1.4em}
.prose .sym{margin:.6em 0}
.prose .sources{font-size:.9rem;color:var(--dim)}
.symwrap{background:var(--white);border:1px solid var(--line);border-radius:var(--r);
  padding:.4em 1em;overflow-x:auto;box-shadow:var(--shadow)}

/* process timeline */
.proc{counter-reset:p;display:grid;gap:0;margin:1.4em 0}
.proc li{list-style:none;position:relative;padding:0 0 1.6em 3.2em}
.proc li::before{counter-increment:p;content:counter(p);position:absolute;left:0;top:0;
  width:2.2em;height:2.2em;border-radius:50%;background:var(--grad);color:#231000;
  font-family:var(--disp);font-weight:800;display:grid;place-items:center}
.proc li::after{content:"";position:absolute;left:1.05em;top:2.4em;bottom:.2em;width:2px;
  background:var(--line)}
.proc li:last-child{padding-bottom:0}
.proc li:last-child::after{display:none}
.proc b{font-family:var(--disp);display:block;margin-bottom:.15em}
.proc p{font-size:.95rem;color:var(--dim)}

/* faq */
.faq{display:grid;gap:.8em;max-width:52em}
.faq details{background:var(--white);border:1px solid var(--line);border-radius:var(--rs);
  padding:1.1em 1.3em}
.faq summary{font-family:var(--disp);font-weight:700;color:var(--ink);cursor:pointer;
  list-style:none;display:flex;justify-content:space-between;gap:1em;align-items:center}
.faq summary::after{content:"+";font-size:1.4em;color:var(--sun);transition:transform .2s;flex:none}
.faq details[open] summary::after{transform:rotate(45deg)}
.faq details p{margin-top:.8em;color:var(--dim);font-size:.96rem}
.light .faq details{background:var(--paper)}

/* areas */
.areas{display:flex;flex-wrap:wrap;gap:.6em}
.areas a{display:inline-flex;align-items:center;gap:.45em;background:var(--white);
  border:1px solid var(--line);border-radius:999px;padding:.5em 1.1em;color:var(--ink);
  font-size:.92rem;font-weight:600}
.areas a:hover{border-color:var(--sun);color:var(--sundeep)}
.areas .ic{color:var(--sun);width:1em;height:1em}

/* CTA band */
.band{background:
  radial-gradient(70% 130% at 15% 0%,rgba(247,148,51,.22),transparent 55%),
  linear-gradient(100deg,#2b1607,#15181f)}
.band .wrap{padding:3.6em 22px;display:flex;flex-wrap:wrap;gap:2em;align-items:center;
  justify-content:space-between}
.band h2{font-size:clamp(1.6rem,3.2vw,2.2rem);color:#fff;max-width:16em}
.band p{color:var(--gold);margin-top:.5em}
.band .cta{display:flex;gap:.9em;flex-wrap:wrap}

/* page hero */
.phero{background:
  radial-gradient(50% 100% at 90% 0%,rgba(247,148,51,.14),transparent 60%),var(--white);
  border-bottom:1px solid var(--line)}
.phero .wrap{padding:3.2em 22px}
.phero h1{font-size:clamp(1.9rem,4.2vw,3rem);max-width:17em;margin-top:.35em}
.phero p.lead{margin-top:1em;font-size:1.06rem;color:var(--dim);max-width:42em}
.crumbs{font-size:.85rem;color:var(--dim)}
.crumbs a{color:var(--dim)}
.crumbs a:hover{color:var(--sundeep)}
.crumbs span{margin:0 .5em;opacity:.5}
.crumbs b{color:var(--ink)}

/* prose + articles */
.prose{max-width:46em}
.prose p{margin-bottom:1.2em}
.prose h2{font-size:1.55rem;margin:1.6em 0 .7em}
.prose h3{font-size:1.2rem;margin:1.4em 0 .6em}
.prose ul,.prose ol{margin:0 0 1.2em 1.3em}
.prose li{margin-bottom:.4em}

/* blog */
.post-card .tagchip{display:inline-block;background:rgba(242,106,27,.1);color:var(--sundeep);
  font-size:.75rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  border-radius:999px;padding:.3em .9em;margin-bottom:.9em}
.post-card time{display:block;font-size:.82rem;color:var(--dim);margin-top:.9em}
.article-meta{display:flex;gap:1em;align-items:center;font-size:.88rem;color:var(--dim);
  margin-top:1em;flex-wrap:wrap}
.article-meta .tagchip{background:rgba(242,106,27,.1);color:var(--sundeep);font-size:.75rem;
  font-weight:700;letter-spacing:.08em;text-transform:uppercase;border-radius:999px;padding:.3em .9em}

/* contact */
.contact-grid{display:grid;grid-template-columns:.9fr 1.1fr;gap:3em;align-items:start}
.cinfo{display:grid;gap:1em}
.cinfo .card{display:flex;gap:1em;align-items:flex-start}
.cinfo .cico{margin:0}
.cinfo h3{margin-bottom:.2em}
.cinfo a{font-weight:700}
form.book{background:var(--white);border:1px solid var(--line);border-radius:var(--r);
  padding:2em;display:grid;gap:1em;box-shadow:var(--shadow)}
form.book .row{display:grid;grid-template-columns:1fr 1fr;gap:1em}
form.book label{font-size:.82rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase;
  color:var(--dim);display:grid;gap:.4em}
form.book input,form.book select,form.book textarea{font:inherit;color:var(--ink);
  background:var(--paper);border:1px solid var(--line);border-radius:var(--rs);
  padding:.8em .9em;width:100%}
form.book input:focus,form.book select:focus,form.book textarea:focus{outline:2px solid var(--sun);
  outline-offset:0;border-color:transparent}
form.book textarea{min-height:110px;resize:vertical}
form.book .btn{justify-content:center}

/* footer */
.ft{background:var(--ink2);padding:4em 0 2em;font-size:.94rem}
.ft .cols{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:2.5em;margin-bottom:2.5em}
.ft h4{color:#fff;font-size:.85rem;letter-spacing:.16em;text-transform:uppercase;margin-bottom:1em}
.ft a{display:block;color:#a7abb4;padding:.22em 0}
.ft a:hover{color:var(--gold)}
.ft .brand{margin-bottom:.9em;color:#fff}
.ft .brand small{color:#a7abb4}
.ft p{color:#a7abb4;font-size:.9rem}
.ft .ftphone a{display:inline;font-family:var(--disp);font-size:1.3rem;font-weight:800;color:#fff;padding:0}
.ft .legal{border-top:1px solid #232a38;padding-top:1.4em;display:flex;flex-wrap:wrap;
  gap:1em;justify-content:space-between;color:#7c8290;font-size:.85rem}
.ft .legal a{display:inline;padding:0}
.ft .legal .links{display:flex;flex-wrap:wrap;gap:1.1em}

/* mobile call bar */
.mcall{display:none;position:fixed;bottom:0;left:0;right:0;z-index:60;
  padding-bottom:env(safe-area-inset-bottom)}
.mcall a{display:flex;align-items:center;justify-content:center;gap:.6em;background:var(--grad);
  color:#231000;font-family:var(--disp);font-weight:800;font-size:1.02rem;padding:.95em}

@media(max-width:960px){
  .g3{grid-template-columns:repeat(2,1fr)}
  .split,.contact-grid,.hero-grid{grid-template-columns:1fr;gap:2.2em}
  .hero-shot .photo-card{aspect-ratio:4/3}
  .ft .cols{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media(max-width:720px){
  body{font-size:16px;padding-bottom:calc(52px + env(safe-area-inset-bottom))}
  .nav{display:none}
  .hdr .btn-call{font-size:.84rem;padding:.7em .85em;min-height:44px}
  .brand small{display:none}
  .burger{display:grid;place-items:center;min-width:44px;min-height:44px;padding:0}
  .g3,.g2{grid-template-columns:1fr}
  .hdr .wrap{height:62px;gap:.8em}
  .brand{font-size:.98rem}
  .brand .mark{width:36px;height:36px}
  .hero .wrap{padding:2.6em 18px}
  .hero h1{font-size:clamp(2rem,8.5vw,2.6rem)}
  .hero p.lead{font-size:1.02rem}
  .hero .cta .btn{width:100%;justify-content:center}
  .hero .sub{gap:.7em;flex-direction:column}
  .phero .wrap{padding:2.4em 18px}
  .sec{padding:2.8em 0}
  .sec-head{margin-bottom:1.6em}
  .wrap{padding:0 18px}
  .band .wrap{padding:2.8em 18px}
  .band .cta{width:100%}
  .band .cta .btn{flex:1;justify-content:center}
  .util .hide-sm{display:none}
  .mcall{display:block}
  form.book .row{grid-template-columns:1fr}
  form.book{padding:1.4em}
  .quote{padding:1.6em;padding-top:2em}
  .quote blockquote{font-size:1.08rem}
  #svcmap{height:340px}
  .card{padding:1.3em}
  .sym{font-size:.88rem}
  .sym th{width:40%}
}
@media(max-width:380px){
  .brand>span{display:none}
}
"""

JS = """
const burger=document.querySelector('.burger'),mnav=document.querySelector('.mnav');
if(burger&&mnav){
  burger.addEventListener('click',()=>mnav.classList.add('open'));
  mnav.querySelector('.x').addEventListener('click',()=>mnav.classList.remove('open'));
  mnav.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>mnav.classList.remove('open')));
}
"""

# ================================================================== LAYOUT
NAV = [("Services", "services"), ("Service Areas", "service-areas"),
       ("Reviews", "reviews"), ("Blog", "blog"),
       ("About", "about"), ("Contact", "contact-us")]

def desktop_nav():
    out = []
    for n, u in NAV:
        if u == "services":
            subs = ('<a href="/services/" class="drop-all">All services</a>'
                    + "".join(f'<a href="/services/{s["slug"]}/">{s["name"]}</a>' for s in SERVICES))
            out.append('<div class="nav-item"><a href="/services/" class="nav-top">Services'
                       + icon("caret", "ic caret") + f'</a><div class="dropdown">{subs}</div></div>')
        else:
            out.append(f'<a href="/{u}/">{n}</a>')
    return "".join(out)

def mobile_nav():
    out = []
    for n, u in NAV:
        if u == "services":
            subs = ('<a href="/services/">All services</a>'
                    + "".join(f'<a href="/services/{s["slug"]}/">{s["name"]}</a>' for s in SERVICES))
            out.append(f'<details class="mdrop"><summary>Services</summary><div class="msub">{subs}</div></details>')
        else:
            out.append(f'<a href="/{u}/">{n}</a>')
    return "".join(out)

MANIFESTO = """<!--
═══════════════════════════════════════════════════════════════════════════════════════

        O R L A N D O ' S   F I N E S T   M O B I L E   M E C H A N I C

               ───────────────────────────────────────────────
                    The repair shop that comes to you
               ───────────────────────────────────────────────


    /* TEAM */

      Built by:            Clickflame - Anthony Limpert
      Location:            Orlando, Florida
      Studio reach:        support@clickflame.com - clickflame.com


    /* MANIFESTO */

      We fight for the weak and the weary. The one-van outfits, the mechanics who answer their own phone,
      the businesses that close when somebody gets sick.

      We do not work for big corporations. Ever.
      They have agencies. They have budgets.
      They do not need us, and we do not want them.

      What we have is technology,
      and we use it the way a crowbar was meant to be used:
      to pry the playing field level.

      We are a mom-and-pop operation,
      and pop happens to be the best top-ranked pop
      in the business.

      Fighting for what's right in a chaotic universe.
      - Clickflame


    /* STACK */

      One Python file - static HTML - zero bloat
      Netlify - GitHub - no page builders, no bloat


    /* THANKS */

      To Yair, Paul, and every mechanic who fixed a car in a parking lot
      while the owner watched and learned something.
      To every dev who reads source.
      // hello, fellow dev.

═══════════════════════════════════════════════════════════════════════════════════════
-->"""

GTAG = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-WWQR41HGJQ"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-WWQR41HGJQ');
</script>"""

def head(title, desc, path, *extra_ld):
    canon = url(path)
    website = ({"@type": "WebSite", "@id": DOMAIN + "/#website", "name": BIZ,
                "url": DOMAIN + "/", "publisher": {"@id": DOMAIN + "/#organization"}}
               if path in ("", "/", "index") else None)
    return f"""<!DOCTYPE html>
{MANIFESTO}
<html lang="en">
<head>
{GTAG}
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canon}">
<meta property="og:site_name" content="{esc(BIZ)}">
<meta property="og:image" content="{DOMAIN}/img/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0b0e13">
<meta name="geo.region" content="US-{STATE}">
<meta name="geo.placename" content="{CITY_MAIN}">
<link rel="author" href="/humans.txt">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
<link rel="icon" href="{FAVICON}">
{ldjson(schema_business(), website, *extra_ld)}
</head>
<body>
<div class="util"><div class="wrap">
  <span>{icon('van')} We come to you across {CITY_MAIN} and nearby towns</span>
  <span class="hide-sm">{icon('clock')} {HOURS_LINE} &nbsp; <a href="tel:{PHONE_TEL}">{PHONE_DISP}</a></span>
</div></div>
<header class="hdr"><div class="wrap">
  <a class="brand" href="/"><span class="mark">{icon('wrench')}</span>
    <span>Orlando's Finest<small>Mobile Mechanic</small></span></a>
  <nav class="nav">{desktop_nav()}</nav>
  <a class="btn btn-sun btn-call" href="tel:{PHONE_TEL}">{icon('phone')} {PHONE_DISP}</a>
  <button class="burger" aria-label="Open menu">{icon('menu')}</button>
</div></header>
<div class="mnav"><button class="x" aria-label="Close menu">{icon('close')}</button>
  {mobile_nav()}
  <a class="btn btn-sun" href="tel:{PHONE_TEL}">{icon('phone')} Call {PHONE_DISP}</a>
</div>
"""

def footer():
    svc = "".join(f'<a href="/services/{s["slug"]}/">{s["name"]}</a>' for s in SERVICES[:6])
    cit = "".join(f'<a href="/service-areas/{c[0]}/">{c[1]}, FL</a>' for c in CITIES[1:8])
    return f"""
<footer class="ft"><div class="wrap">
  <div class="cols">
    <div>
      <a class="brand" href="/"><span class="mark">{icon('wrench')}</span>
        <span>Orlando's Finest<small>Mobile Mechanic</small></span></a>
      <p>{TAGLINE}. Certified mobile mechanics serving {CITY_MAIN} and the surrounding
      Central {STATE_FULL} communities, seven days a week.</p>
      <div class="ftphone"><a href="tel:{PHONE_TEL}">{PHONE_DISP}</a></div>
      <p>{HOURS_LINE}<br><a href="mailto:{EMAIL}" style="display:inline;padding:0;overflow-wrap:anywhere">{EMAIL}</a></p>
    </div>
    <div><h4>Services</h4>{svc}<a href="/services/">All services</a></div>
    <div><h4>Service Areas</h4>{cit}<a href="/service-areas/">All areas</a></div>
    <div><h4>Company</h4>
      <a href="/about/">About Us</a>
      <a href="/about/#check">How to Check Us</a>
      <a href="/reviews/">Reviews</a>
      <a href="/blog/">Blog</a>
      <a href="/contact-us/">Contact Us</a>
      <a href="{BOOK_URL}" rel="nofollow">Book Online</a>
      <a href="{GMB_URL}" rel="nofollow">Find Us on Google</a>
      <a href="/privacy-policy/">Privacy Policy</a>
      <a href="/terms-of-service/">Terms of Service</a>
    </div>
  </div>
  <div class="legal">
    <span>&copy; {YEAR} {esc(BIZ)}. All rights reserved.</span>
    <span class="links"><a href="/privacy-policy/">Privacy</a> <a href="/terms-of-service/">Terms</a> <a href="/sitemap.xml">Sitemap</a> <a href="https://mechanicrank.com">Website by MechanicRank</a></span>
  </div>
</div></footer>
<div class="mcall"><a href="tel:{PHONE_TEL}">{icon('phone')} Tap to call {PHONE_DISP}</a></div>
<script src="/main.js" defer></script>
</body></html>"""

# ================================================================== BLOCKS
def crumb(items):
    return ('<nav class="crumbs" aria-label="Breadcrumb">'
            + '<span>/</span>'.join(f'<a href="{"/" + u.strip("/") + "/" if u else "/"}">{esc(n)}</a>'
                                    if i < len(items) - 1 else f'<b>{esc(n)}</b>'
                                    for i, (n, u) in enumerate(items))
            + "</nav>")

def phero(kick, h1, lead, crumbs=None):
    c = crumb(crumbs) if crumbs else ""
    return (f'<section class="phero"><div class="wrap">{c}'
            f'<span class="kick">{esc(kick)}</span><h1>{h1}</h1>'
            f'<p class="lead">{lead}</p></div></section>')

def block_services(heading=True, light=False):
    cards = "".join(
        f'<a class="card" href="/services/{s["slug"]}/">'
        f'<span class="cico">{icon(s["icon"])}</span>'
        f'<h3>{s["name"]}</h3><p>{esc(s["short"])}</p>'
        f'<span class="more">Learn more</span></a>'
        for s in SERVICES)
    head_html = ('<div class="sec-head">'
                 '<h2>One call covers the whole repair shop menu</h2>'
                 '<p>Every service below is performed at your location by a certified mechanic '
                 'with the parts and tools on board.</p></div>') if heading else ""
    cls = "sec light" if light else "sec"
    return f'<section class="{cls}"><div class="wrap">{head_html}<div class="grid g3">{cards}</div></div></section>'

def block_steps():
    steps = [
        ("Tell us what's wrong", "Call, text, or book online. Give us the year, make, model, "
         "where the car is parked, and what it's doing."),
        ("We come to the car", "A certified mechanic arrives in your booked window with the "
         "tools, scan gear, and parts. Home, office, or roadside."),
        ("Approve, then we fix it", "We confirm the fault, quote the price, and only start when "
         "you say go. Most jobs are done in a single visit."),
    ]
    cards = "".join(f'<div class="card step"><h3>{t}</h3><p>{d}</p></div>' for t, d in steps)
    return (f'<section class="sec light"><div class="wrap">'
            f'<div class="sec-head">'
            f'<h2>Three steps, zero waiting rooms</h2></div>'
            f'<div class="grid g3 steps">{cards}</div></div></section>')

def block_why():
    points = [
        "Certified mechanics. Not a parts-swapper with a code reader",
        "Diagnosis confirmed by testing before any parts go on",
        "Price agreed up front, before the work starts",
        "Open seven days, with evening hours Monday to Saturday",
        "We come to homes, offices, apartments, and roadsides",
        "No tow bill, no shuttle, no lost day",
    ]
    checks = "".join(f'<li>{icon("check")}<span>{p}</span></li>' for p in points)
    return f"""
<section class="sec"><div class="wrap"><div class="split">
  <div>
    <h2 style="font-size:clamp(1.7rem,3.4vw,2.5rem);margin:.4em 0 .6em">
      The shop visit, deleted from your week</h2>
    <p style="color:var(--dim)">Driving to a mechanic, waiting for repairs, juggling rides. That's the part of car trouble we removed. What's left is just the fix: a certified mechanic,
    the right parts, and your driveway.</p>
    <ul class="checks">{checks}</ul>
    <a class="btn btn-sun" href="tel:{PHONE_TEL}">{icon('phone')} Call {PHONE_DISP}</a>
  </div>
  <div class="grid" style="gap:1em">
    <div class="photo-card"><img src="/img/under-hood.jpg" width="1400" height="1050" loading="lazy"
      alt="Certified mobile mechanic performing an engine repair under the hood at a customer's location"></div>
    <div class="card"><span class="cico">{icon('clock')}</span><h3>Open when you're off work</h3>
      <p>Monday to Saturday we run until 10pm, and we work Sundays too. Book the evening slot
      and never miss an hour of work over a brake job.</p></div>
    <div class="card"><span class="cico">{icon('shield')}</span><h3>Honest calls, in writing</h3>
      <p>If a job truly needs a lift or a specialty shop, we say so before taking a dime. And you keep the diagnosis either way.</p></div>
    <div class="card"><span class="cico">{icon('sun')}</span><h3>Built for Florida cars</h3>
      <p>Heat-killed batteries, overworked A/C, brake wear from I-4 crawls. We fix what
      Central Florida actually does to vehicles.</p></div>
  </div>
</div></div></section>"""

def bite_box(text_html):
    return (f'<div class="bite">{icon("bolt")}<p>{text_html}</p></div>')

def snack_box(items, title="At a glance"):
    li = "".join(f'<li>{icon("check")}<span>{esc(x)}</span></li>' for x in items)
    return (f'<div class="snackbox"><h3>{icon("clipboard")} {esc(title)}</h3>'
            f'<ul>{li}</ul></div>')

MR_LINK = "https://mechanicrank.com/m/orlandos-finest-mobile-mechanic/"
def mr_badge(w, size):
    return (f'<picture><source type="image/webp" srcset="/img/mr-verified-orlando-{size}.webp">'
            f'<img src="/img/mr-verified-orlando-{size}.png" alt="MechanicRank Verified badge, Orlando" '
            f'width="{w}" height="{round(w*419/520)}" loading="lazy" decoding="async"></picture>')

def mr_chip():
    return (f'<a class="mrchip" href="{MR_LINK}" rel="nofollow noopener">{mr_badge(52, 260)}'
            f'<span><b>MechanicRank Verified</b><span class="t">Mobile mechanic, Orlando</span></span></a>')

def mr_card():
    return (f'<div class="card mrcard">{mr_badge(150, 520)}<div><h3>MechanicRank Verified</h3>'
            f'<p>Listed and verified on MechanicRank as a mobile mechanic in Orlando, FL.</p>'
            f'<a href="{MR_LINK}" rel="nofollow noopener">See the MechanicRank listing &rarr;</a></div></div>')

def gbadge():
    stars = "".join(icon("star") for _ in range(5))
    return (f'<a class="gbadge" href="{GMB_URL}" rel="nofollow">'
            f'<span class="stars">{stars}</span>'
            f'<span><b>{RATING}</b> on Google, {REVIEW_CT} reviews</span></a>')

def review_card(n, s, d, t):
    stars = "".join(icon("star") for _ in range(s))
    return (f'<figure class="card rev"><div class="stars">{stars}</div>'
            f'<blockquote>&ldquo;{esc(t)}&rdquo;</blockquote>'
            f'<figcaption>{esc(n)}<span>Google review</span></figcaption></figure>')

def block_testimonial(limit=3):
    cards = "".join(review_card(*r) for r in REVIEWS[:limit])
    return f"""
<section class="sec light"><div class="wrap">
  <div class="sec-head">
    <h2>Rated {RATING} stars by the people we drive to</h2>
    <p>{gbadge()}</p>
  </div>
  <div class="grid g3">{cards}</div>
  <p style="margin-top:1.6em"><a href="/reviews/" style="font-weight:700">Read more reviews</a></p>
</div></section>"""

def block_map():
    data = json.dumps(map_markers())
    return f"""
<section class="sec"><div class="wrap">
  <div class="sec-head"><h2>Jobs done all over the Orlando metro</h2>
  <p>Every pin is the kind of call we run every week. Driveways, office lots, and roadsides
  from Sanford down to St. Cloud. Pin locations are approximate; exact addresses stay private.</p></div>
  <div id="svcmap" aria-label="Map of {esc(BIZ)} service area with recent job markers"></div>
  <div class="maplegend">
    <span><i class="pin-demo home"></i> Home base, Orlando</span>
    <span><i class="pin-demo"></i> Completed mobile visits</span>
  </div>
</div></section>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" defer></script>
<script>
window.addEventListener('load',function(){{
  var el=document.getElementById('svcmap'); if(!el||!window.L)return;
  var map=L.map(el,{{scrollWheelZoom:false}});
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',{{
    maxZoom:17, attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }}).addTo(map);
  var pins={data};
  var dot=L.divIcon({{className:'',html:'<span class="svcpin"></span>',iconSize:[14,14],iconAnchor:[7,7]}});
  var home=L.divIcon({{className:'',html:'<span class="svcpin home"></span>',iconSize:[20,20],iconAnchor:[10,10]}});
  var b=[];
  pins.forEach(function(p){{
    b.push([p.lat,p.lng]);
    L.marker([p.lat,p.lng],{{icon:dot}}).addTo(map)
      .bindPopup('<b>'+p.job+'</b><br>'+p.city+', FL');
  }});
  L.marker([{GEO_LAT},{GEO_LNG}],{{icon:home,zIndexOffset:1000}}).addTo(map)
    .bindPopup('<b>{esc(BIZ)}</b><br>Home base, Orlando, FL<br><a href="tel:{PHONE_TEL}">{PHONE_DISP}</a>');
  map.fitBounds(b,{{padding:[28,28]}});
}});
</script>"""

def block_areas(light=False, heading=True):
    chips = "".join(f'<a href="/service-areas/{c[0]}/">{icon("pin")}{c[1]}</a>' for c in CITIES)
    head_html = ('<div class="sec-head">'
                 '<h2>Serving Orlando and the towns around it</h2>'
                 '<p>If your car is anywhere in the Orlando metro, odds are we can get to it. '
                 'Don’t see your town? Call anyway.</p></div>') if heading else ""
    cls = "sec light" if light else "sec"
    return (f'<section class="{cls}"><div class="wrap">{head_html}'
            f'<div class="areas">{chips}</div></div></section>')

def block_faq(faqs=None, title="Common questions", light=False):
    faqs = faqs or FAQS
    items = "".join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>'
                    for q, a in faqs)
    cls = "sec light" if light else "sec"
    return (f'<section class="{cls}"><div class="wrap">'
            f'<div class="sec-head"><h2>{esc(title)}</h2></div>'
            f'<div class="faq">{items}</div></div></section>')

def block_cta(line=None, sub=None):
    line = line or "Car trouble? Don't bring it to us."
    sub = sub or "We'll come to it. Seven days a week, across the Orlando metro."
    return f"""
<section class="band"><div class="wrap">
  <div><h2>{esc(line)}</h2><p>{esc(sub)}</p></div>
  <div class="cta">
    <a class="btn btn-sun" href="tel:{PHONE_TEL}">{icon('phone')} {PHONE_DISP}</a>
    <a class="btn btn-ghost" href="{BOOK_URL}" rel="nofollow">{icon('calendar')} Book online</a>
  </div>
</div></section>"""

def symptom_table(rows, title="What the symptom is telling you"):
    tr = "".join(f'<tr><th>{esc(s)}</th><td>{esc(m)}</td></tr>' for s, m in rows)
    return (f'<h2 style="font-size:1.6rem;margin:1.6em 0 .7em">{esc(title)}</h2>'
            f'<div class="symwrap"><table class="sym">{tr}</table></div>')

print("Layout ready.")

# ================================================================== PAGES
def page_home():
    title = "Mobile Mechanic Orlando FL | Orlando's Finest"
    desc = (f"Certified mobile mechanics who come to you across Orlando, FL. Brakes, "
            f"diagnostics, batteries, oil changes, A/C and more at your home or office, "
            f"7 days a week. Call {PHONE_DISP}.")
    hero = f"""
<section class="hero"><div class="wrap"><div class="hero-grid">
  <div>
    <span class="kick">Mobile auto mechanic in Orlando, {STATE_FULL}</span>
    <h1>The repair shop comes to you.</h1>
    <p class="lead">Certified mechanics, a fully stocked service vehicle, and your driveway.
    {BIZ} brings expert auto repair to your home, your office, or the roadside where the car
    quit. Across Orlando and the surrounding areas, seven days a week.</p>
    <div class="cta">
      <a class="btn btn-sun" href="tel:{PHONE_TEL}">{icon('phone')} Call {PHONE_DISP}</a>
      <a class="btn btn-ghost" href="{BOOK_URL}" rel="nofollow">{icon('calendar')} Book an appointment</a>
    </div>
    <div class="sub" style="margin-top:1.4em">{gbadge()}{mr_chip()}</div>
    <div class="sub">
      <span>{icon('check')} Certified mechanics</span>
      <span>{icon('check')} Price approved before work starts</span>
      <span>{icon('check')} Open 7 days, evenings too</span>
    </div>
  </div>
  <div class="hero-shot">
    <div class="photo-card"><img src="/img/driveway-service.jpg" width="1475" height="1536"
      alt="Orlando's Finest mobile mechanic servicing an SUV in a customer's driveway in Orlando, FL" fetchpriority="high"></div>
    <span class="tag">{icon('pin')} A real job, in a real driveway</span>
  </div>
</div></div></section>"""
    body = (hero + block_services() + block_steps() + block_why()
            + block_testimonial() + block_map() + block_areas(light=True)
            + block_faq() + block_cta())
    return head(title, desc, "", schema_faq(FAQS)) + body + footer()

def page_service(s):
    name = s["name"]
    title = f"{name} | Orlando Mobile Mechanic"
    desc = (fmt(s["short"]) + f" {BIZ} comes to your home or office anywhere in the "
            f"Orlando area. Call {PHONE_DISP}.")
    bodies = "".join(f"<p>{fmt(p)}</p>" for p in s["bodies"])
    bullets = "".join(f'<li>{icon("check")}<span>{esc(b)}</span></li>' for b in s["bullets"])
    sym = symptom_table(s["signs"]) if s.get("signs") else ""
    detail = SERVICE_DETAIL.get(s["slug"], {})
    bite, snack = "", ""
    if s["slug"] in SERVICE_BITE:
        b_text, s_items = SERVICE_BITE[s["slug"]]
        bite = bite_box(b_text)
        snack = snack_box(s_items)
    faqs = (s.get("faqs") or []) + (detail.get("extra_faqs") or [])
    faq_html = block_faq(faqs, title="Questions we hear about this service", light=True) if faqs else ""
    proc = ""
    if detail.get("process"):
        steps = "".join(f'<li><b>{esc(t)}</b><p>{esc(d)}</p></li>' for t, d in detail["process"])
        proc = (f'<h2 style="font-size:1.55rem;margin:1.6em 0 .7em">How the visit works</h2>'
                f'<ol class="proc">{steps}</ol>')
    factors = ""
    if detail.get("factors"):
        li = "".join(f'<li>{icon("check")}<span>{esc(x)}</span></li>' for x in detail["factors"])
        factors = (f'<h2 style="font-size:1.55rem;margin:1.6em 0 .7em">What moves the price</h2>'
                   f'<p style="color:var(--dim)">We quote after diagnosis and you approve before '
                   f'work starts. But these are the honest variables behind any quote:</p>'
                   f'<ul class="checks">{li}</ul>')
    other_cards = [o for o in SERVICES if o["slug"] != s["slug"]][:3]
    others = "".join(
        f'<a class="card" href="/services/{o["slug"]}/"><span class="cico">{icon(o["icon"])}</span>'
        f'<h3>{o["name"]}</h3><p>{esc(o["short"])}</p>'
        f'<span class="more">Learn more</span></a>' for o in other_cards)
    body = phero("We come to you", esc(s["hero"]), esc(fmt(s["intro"])),
                 crumbs=[("Home", ""), ("Services", "services"), (name, f"services/{s['slug']}")])
    body += f"""
<section class="sec"><div class="wrap"><div class="split" style="align-items:start">
  <div class="prose">{bite}{snack}{bodies}{sym}{proc}{factors}</div>
  <div>
    <div class="card"><h3>What's included</h3><ul class="checks">{bullets}</ul>
      <a class="btn btn-sun" href="tel:{PHONE_TEL}" style="width:100%;justify-content:center">
      {icon('phone')} Call {PHONE_DISP}</a>
      <p style="margin-top:1em;font-size:.88rem;color:var(--dim)">Or
      <a href="{BOOK_URL}" rel="nofollow">book a time online</a>. {HOURS_LINE}.</p></div>
    <div class="card" style="margin-top:1em"><h3>Where we do it</h3>
      <p>Anywhere the car sits in the Orlando metro. Driveways, office lots, apartment
      complexes, parking garages, roadsides. See all <a href="/service-areas/">service areas</a>.</p></div>
  </div>
</div></div></section>"""
    body += faq_html
    body += ('<section class="sec"><div class="wrap"><div class="sec-head">'
             '<h2>Also done at your curb</h2></div>'
             f'<div class="grid g3">{others}</div></div></section>')
    body += block_cta(f"Need {name.lower()}?", "Tell us where the car is. We'll bring the shop.")
    ld = [schema_service(name, fmt(s["short"])),
          schema_breadcrumb([("Home", ""), ("Services", "services"), (name, f"services/{s['slug']}")])]
    if faqs: ld.append(schema_faq(faqs))
    return head(title, desc, f"services/{s['slug']}", *ld) + body + footer()

def page_services_index():
    title = "Mobile Mechanic Services in Orlando, FL | Orlando's Finest"
    desc = (f"Every service on the shop menu, done at your location. Diagnostics, brakes, "
            f"batteries, starters, oil, A/C and more. Orlando metro, 7 days. {PHONE_DISP}.")
    body = phero("Our services", "Comprehensive services, zero shop visits",
                 "If it can be done where the car is parked, we do it. And that covers far more "
                 "than most people expect. Pick a service to see how it works.",
                 crumbs=[("Home", ""), ("Services", "services")])
    body += block_services(heading=False)
    body += block_steps()
    body += block_faq(light=False)
    body += block_cta()
    return head(title, desc, "services",
                schema_breadcrumb([("Home", ""), ("Services", "services")]),
                schema_faq(FAQS)) + body + footer()

def page_city(c):
    slug, name, county, paras = c
    title = f"Mobile Mechanic {name}, FL | Orlando's Finest"
    desc = (f"Mobile mechanic serving {name}, FL in {county}. Brakes, diagnostics, batteries, "
            f"oil and A/C repaired at your home or office. Open 7 days. Call {PHONE_DISP}.")
    bite = bite_box(f"<b>Mobile mechanic in {esc(name)}, FL.</b> We come to your home, office, "
                    f"or roadside in {esc(name)} and fix the car where it sits.")
    snack = snack_box([f"We come to you anywhere in {name}",
                       "Fault confirmed by testing before parts go on",
                       "Price approved before work starts",
                       "Open 7 days, evenings until 10pm Mon to Sat"])
    paras_html = bite + snack + "".join(f"<p>{esc(p)}</p>" for p in paras)
    svc_list = "".join(
        f'<li>{icon("check")}<span><a href="/services/{s["slug"]}/">{s["name"]}</a> in {esc(name)}</span></li>'
        for s in SERVICES)
    body = phero(f"{county}, Florida", f"Mobile Mechanic in {esc(name)}, FL",
                 f"A certified mechanic at your {esc(name)} address, with the tools, the parts, "
                 f"and a price you approve before work starts.",
                 crumbs=[("Home", ""), ("Service Areas", "service-areas"), (name, f"service-areas/{slug}")])
    body += f"""
<section class="sec"><div class="wrap"><div class="split" style="align-items:start">
  <div class="prose">{paras_html}
    <h2>What we fix in {esc(name)}</h2>
    <ul class="checks">{svc_list}</ul>
  </div>
  <div>
    <div class="card"><span class="cico">{icon('phone')}</span><h3>Book a mechanic in {esc(name)}</h3>
      <p>Call or text with the year, make, model, and what the car is doing. We'll quote the
      visit and book a window that fits your day.</p>
      <a class="btn btn-sun" href="tel:{PHONE_TEL}" style="width:100%;justify-content:center;margin-top:1em">
        {icon('phone')} {PHONE_DISP}</a>
      <p style="margin-top:1em;font-size:.88rem;color:var(--dim)">{HOURS_LINE}</p></div>
    <div class="card" style="margin-top:1em"><span class="cico">{icon('pin')}</span><h3>Nearby areas</h3>
      <p>{", ".join(f'<a href="/service-areas/{o[0]}/">{o[1]}</a>' for o in CITIES if o[0] != slug)}</p></div>
  </div>
</div></div></section>"""
    body += block_testimonial()
    body += block_cta(f"Need a mechanic in {name}?", "Skip the tow. We'll meet the car where it is.")
    return head(title, desc, f"service-areas/{slug}",
                schema_service(f"Mobile Mechanic in {name}, FL",
                               f"On-site auto repair in {name}, {STATE_FULL}.", f"{name}, FL"),
                schema_breadcrumb([("Home", ""), ("Service Areas", "service-areas"),
                                   (name, f"service-areas/{slug}")])) + body + footer()

def page_areas():
    title = f"Service Areas | {BIZ}"
    desc = (f"We bring mobile auto repair to Orlando, Winter Park, Kissimmee, Sanford, Apopka "
            f"and the surrounding Central Florida towns. 7 days a week. {PHONE_DISP}.")
    cards = "".join(
        f'<a class="card" href="/service-areas/{c[0]}/"><span class="cico">{icon("pin")}</span>'
        f'<h3>{c[1]}, FL</h3><p>{esc(c[2])}</p>'
        f'<span class="more">Mobile mechanic in {c[1]}</span></a>'
        for c in CITIES)
    body = phero("Coverage", "One metro, one phone call",
                 "Wherever your car is parked in the Orlando area, we can probably get a "
                 "mechanic to it. These are the communities we serve most.",
                 crumbs=[("Home", ""), ("Service Areas", "service-areas")])
    body += f'<section class="sec"><div class="wrap"><div class="grid g3">{cards}</div></div></section>'
    body += block_map()
    body += block_cta("Not on the list?", "Coverage stretches beyond these towns. Call and ask.")
    return head(title, desc, "service-areas",
                schema_breadcrumb([("Home", ""), ("Service Areas", "service-areas")])) + body + footer()

def page_reviews():
    title = f"Reviews | {BIZ}"
    desc = (f"{BIZ} holds a {RATING}-star rating across {REVIEW_CT} Google reviews. "
            f"Read what Orlando drivers say about our mobile auto repair, word for word.")
    cards = "".join(review_card(*r) for r in REVIEWS)
    body = phero("Reviews", f"Rated {RATING} stars on Google",
                 f"Every review below is a real Google review, quoted verbatim. The rating "
                 f"is earned one driveway at a time.",
                 crumbs=[("Home", ""), ("Reviews", "reviews")])
    body += f"""
<section class="sec"><div class="wrap">
  <p style="margin-bottom:2em">{gbadge()}</p>
  <div class="grid g3">{cards}</div>
  <div class="card" style="margin-top:2em;display:flex;flex-wrap:wrap;gap:1.5em;align-items:center;justify-content:space-between">
    <div><h3>Had us out to your car?</h3>
    <p>A review takes two minutes and genuinely helps a small mobile shop compete with the chains.</p></div>
    <a class="btn btn-sun" href="{GMB_URL}" rel="nofollow">{icon('star')} Review us on Google</a>
  </div>
</div></section>"""
    body += block_cta("Want service worth reviewing?", "Tell us where the car is. We'll take it from there.")
    return head(title, desc, "reviews",
                schema_breadcrumb([("Home", ""), ("Reviews", "reviews")]),
                *schema_reviews()) + body + footer()

def blog_card(p):
    return (f'<a class="card post-card" href="/blog/{p["slug"]}/">'
            f'<span class="tagchip">{esc(p["tag"])}</span>'
            f'<h3>{esc(p["title"])}</h3><p>{esc(p["desc"])}</p>'
            f'<time datetime="{p["date"]}">{p["date"]}</time>'
            f'<span class="more">Read the post</span></a>')

def page_blog_index():
    title = f"Blog | {BIZ}"
    desc = ("Straight answers about batteries, brakes, A/C, check engine lights, and buying "
            "used cars in Central Florida. From the mechanics who fix them in your driveway.")
    cards = "".join(blog_card(p) for p in BLOG)
    body = phero("Blog", "Advice from under the hood",
                 "What Florida actually does to cars, and how to stay ahead of it. Written "
                 "by the crew that repairs the results every day.",
                 crumbs=[("Home", ""), ("Blog", "blog")])
    body += f'<section class="sec"><div class="wrap"><div class="grid g3">{cards}</div></div></section>'
    body += block_cta("Reading about a problem you have?", "Skip to the fix. We come to you, 7 days a week.")
    return head(title, desc, "blog",
                schema_breadcrumb([("Home", ""), ("Blog", "blog")])) + body + footer()

def orl290p_box():
    """Google Preferred Sources button, right after the short answer (2026-10-18)."""
    return ('<p class="orl290p"><a href="https://www.google.com/preferences/source?q=orlando.mechanicrank.com" '
            "target=\"_blank\" rel=\"noopener\">Keep Orlando's Finest in your Google results</a></p>")


def page_blog_post(p):
    title = f"{p['title']} | Orlando's Finest"
    body_html = p["body"].replace("{PHONE}", f'<a href="tel:{PHONE_TEL}">{PHONE_DISP}</a>')
    if p["slug"] in BLOG_BITE:
        b_text, takeaways = BLOG_BITE[p["slug"]]
        body_html = (bite_box(b_text) + orl290p_box() + snack_box(takeaways, "Key takeaways") + body_html)
    else:
        body_html = orl290p_box() + body_html
    others = "".join(blog_card(o) for o in [x for x in BLOG if x["slug"] != p["slug"]][:3])
    body = phero("From the blog", esc(p["title"]), esc(p["desc"]),
                 crumbs=[("Home", ""), ("Blog", "blog"), (p["tag"], f"blog/{p['slug']}")])
    body += f"""
<section class="sec"><div class="wrap"><div class="split" style="align-items:start">
  <article class="prose">
    <div class="article-meta" style="margin:0 0 1.5em">
      <span class="tagchip">{esc(p["tag"])}</span>
      <time datetime="{p["date"]}">Published {p["date"]}</time>
    </div>
    {body_html}
  </article>
  <div>
    <div class="card"><span class="cico">{icon('phone')}</span><h3>Skip the reading, fix the car</h3>
      <p>Mobile repair across the Orlando metro. Evenings and Sundays included.</p>
      <a class="btn btn-sun" href="tel:{PHONE_TEL}" style="width:100%;justify-content:center;margin-top:1em">
        {icon('phone')} {PHONE_DISP}</a></div>
    <div class="card" style="margin-top:1em"><h3>Popular services</h3>
      <p>{", ".join(f'<a href="/services/{s["slug"]}/">{s["name"]}</a>' for s in SERVICES[:5])}</p></div>
  </div>
</div></div></section>"""
    if p.get("faqs"):
        body += block_faq(p["faqs"], "Questions people ask")
    body += ('<section class="sec light"><div class="wrap"><div class="sec-head">'
             '<h2>More from the blog</h2></div>'
             f'<div class="grid g3">{others}</div></div></section>')
    body += block_cta()
    extra = [schema_faq(p["faqs"])] if p.get("faqs") else []
    return head(title, p["desc"], f"blog/{p['slug']}",
                schema_blogpost(p), *extra,
                schema_breadcrumb([("Home", ""), ("Blog", "blog"),
                                   (p["title"], f"blog/{p['slug']}")])) + body + footer()

# How To Check Us, on /about/#check. Only facts this site already states:
# certified mechanics (no certifying body is named, so none is claimed), the
# Google rating, the reviews page, hours, phone and email. No owner, license,
# insurance or parent company is stated on the site, so none is added here.
CHECK_BITE = (f"{BIZ} is a mobile auto repair service for Orlando and Central Florida. "
              "You should be able to check us before you hand over a key, <b>so here is "
              "what to look at and where to find it.</b>")
CHECK_SNACK = [
    f"{RATING} stars across {REVIEW_CT} reviews on our Google listing",
    "Every service is done by a certified mechanic",
    "You approve the price before any work starts",
    f"Open {HOURS_LINE}",
    f"Call {PHONE_DISP} or email {EMAIL}",
]
CHECK_MEAL = [
    ("Read Our Google Reviews",
     f"Our {RATING} star rating comes straight from our Google listing, across "
     f"{REVIEW_CT} reviews. Nine of them are copied word for word on our "
     f'<a href="/reviews/">reviews page</a>, with the name the reviewer used on Google. '
     f'You can read every one on <a href="{GMB_URL}" rel="nofollow">our Google listing</a>.'),
    ("Ask To See the Certificate",
     "Every job is done by a certified mechanic. When your mechanic arrives, ask to see "
     "the certificate. A good mechanic is glad to show it, and so are we."),
    ("Hold Us to the Price",
     "We test before we sell you a part. Then you get the price in plain numbers, and "
     "nothing starts until you say yes. If a job needs a lift or a specialty shop, we tell "
     "you before we take a dime, and you keep the diagnosis."),
    ("Where Our Numbers Come From",
     "The star rating and review count are read off our Google listing. The facts in our "
     "blog posts name their source, such as AAA or the Federal Highway Administration, "
     "right in the post."),
]
CHECK_FAQ = [
    ("Are your mechanics certified?",
     "Yes. Every service is done by a certified mechanic. Ask the mechanic who comes out "
     "to show you the certificate before work starts."),
    ("Where can I read your reviews?",
     f"On our Google listing, where we hold a {RATING} star rating across {REVIEW_CT} "
     "reviews. Nine of them are also copied word for word on our reviews page."),
    ("How do I know the price before you start?",
     "We test first, then tell you the price in plain numbers. Nothing starts until you "
     "approve it."),
]

def check_section():
    meal = "".join(f'<h3 style="margin-top:1.4em">{esc(h)}</h3><p>{t}</p>' for h, t in CHECK_MEAL)
    return f"""
<section class="sec light" id="check"><div class="wrap" style="max-width:860px">
  <div class="sec-head"><h2>How To Check Us</h2></div>
  {bite_box(CHECK_BITE)}
  {snack_box(CHECK_SNACK)}
  <div class="prose" style="margin-top:1.6em">{meal}</div>
</div></section>""" + block_faq(CHECK_FAQ, title="Questions about checking us")

def page_about():
    title = f"About Us | {BIZ}"
    desc = (f"{BIZ} is a team of certified mechanics who bring the repair shop to you across "
            f"Orlando and Central Florida. Honest diagnosis, up-front pricing, 7 days a week.")
    body = phero("About us", "Highly trained professionals you can trust",
                 "We believe car repairs should be stress-free and convenient. So we removed the "
                 "stressful, inconvenient part: the trip to the shop.",
                 crumbs=[("Home", ""), ("About", "about")])
    body += f"""
<section class="sec"><div class="wrap"><div class="split" style="align-items:start">
  <div class="prose">
    <p>{BIZ} exists because of a simple observation: for most repairs, the shop building adds
    nothing but inconvenience. The lift gets used on a fraction of jobs. The waiting room adds
    misery. The tow adds cost. What actually fixes the car is a trained mechanic with good
    tools and the right parts. And all three of those travel.</p>
    <p>So that's what we built. Our certified mechanics carry diagnostic gear, hand and power
    tools, and common parts to your home, your workplace, or the roadside anywhere in the
    Orlando area. You see the work happen. You approve the price before it starts. And your
    car never leaves your sight.</p>
    <h2>How we work</h2>
    <p>Every job starts with a real diagnosis. Testing, not guessing. Once we know what's
    wrong, you get the price in plain numbers and plain English. If you say go, most repairs
    are finished the same visit. If a job genuinely needs a lift or a machine shop, we tell
    you that instead of starting something we can't finish. That honesty costs us a few jobs
    and wins us customers for years.</p>
    <h2>Built around real schedules</h2>
    <p>Orlando doesn't work nine-to-five, so neither do we. We run Monday through Saturday
    from 9am to 10pm and Sundays 9am to 6pm. Which means the repair can happen after your
    shift, during your workday in the office lot, or on a Sunday without wrecking the week.</p>
  </div>
  <div>
    <div class="photo-card"><img src="/img/interior-work.jpg" width="1100" height="1467" loading="lazy"
      alt="Mobile mechanic repairing a steering column at the customer's location in Orlando"></div>
    <div class="card" style="margin-top:1em"><span class="cico">{icon('shield')}</span><h3>Certified mechanics</h3>
      <p>Trained, experienced techs who diagnose by testing. And show you what they found.</p></div>
    <div class="card" style="margin-top:1em"><span class="cico">{icon('clock')}</span><h3>Seven days a week</h3>
      <p>{HOURS_LINE}. Evening slots are normal, not special favors.</p></div>
    <div class="card" style="margin-top:1em"><span class="cico">{icon('phone')}</span><h3>Talk to us</h3>
      <p><a href="tel:{PHONE_TEL}">{PHONE_DISP}</a><br>
      <a href="mailto:{EMAIL}">{EMAIL}</a></p></div>
    {mr_card().replace('class="card mrcard"', 'class="card mrcard" style="margin-top:1em"')}
  </div>
</div></div></section>"""
    body += check_section()
    body += block_testimonial()
    body += block_cta()
    return head(title, desc, "about",
                schema_breadcrumb([("Home", ""), ("About", "about")]),
                {"@type": "AboutPage", "url": url("about"),
                 "about": {"@id": DOMAIN + "/#organization"}},
                schema_faq(CHECK_FAQ)) + body + footer()

def page_contact():
    title = f"Contact Us | {BIZ}"
    desc = (f"Book a mobile mechanic in Orlando, FL. Call {PHONE_DISP}, email, or send the "
            f"booking form. We come to your home or office, 7 days a week.")
    svc_opts = "".join(f'<option>{s["name"]}</option>' for s in SERVICES) + "<option>Something else</option>"
    body = phero("Contact us", "Skip the form if you like. Just call",
                 f"Fastest way to a booked mechanic: call or text {PHONE_DISP} with the year, "
                 "make, model, and what the car is doing. Prefer typing? The form works too.",
                 crumbs=[("Home", ""), ("Contact", "contact-us")])
    body += f"""
<section class="sec"><div class="wrap"><div class="contact-grid">
  <div class="cinfo">
    <div class="card"><span class="cico">{icon('phone')}</span>
      <div><h3>Phone</h3><p><a href="tel:{PHONE_TEL}">{PHONE_DISP}</a><br>Call or text, 7 days a week</p></div></div>
    <div class="card"><span class="cico">{icon('mail')}</span>
      <div><h3>Email</h3><p><a href="mailto:{EMAIL}" style="word-break:break-all">{EMAIL}</a></p></div></div>
    <div class="card"><span class="cico">{icon('clock')}</span>
      <div><h3>Hours of operation</h3><p>Monday to Saturday, 9:00am to 10:00pm<br>Sunday, 9:00am to 6:00pm</p></div></div>
    <div class="card"><span class="cico">{icon('calendar')}</span>
      <div><h3>Book online</h3><p>Pick your own slot on our
      <a href="{BOOK_URL}" rel="nofollow">online booking calendar</a>.</p></div></div>
    <div class="card"><span class="cico">{icon('pin')}</span>
      <div><h3>Service area</h3><p>Orlando and the surrounding Central Florida communities,
      <a href="/service-areas/">see the list</a>.</p></div></div>
  </div>
  <form class="book" name="booking" method="POST" data-netlify="true" action="/thanks/">
    <input type="hidden" name="form-name" value="booking">
    <h3 style="font-size:1.3rem">Book your appointment</h3>
    <div class="row">
      <label>First name<input name="first-name" required autocomplete="given-name"></label>
      <label>Last name<input name="last-name" required autocomplete="family-name"></label>
    </div>
    <div class="row">
      <label>Phone<input name="phone" type="tel" required autocomplete="tel"></label>
      <label>Email<input name="email" type="email" autocomplete="email"></label>
    </div>
    <div class="row">
      <label>Type of service<select name="service">{svc_opts}</select></label>
      <label>Requested date &amp; time<input name="requested-time" placeholder="e.g. Thu evening, after 6"></label>
    </div>
    <label>Vehicle (year / make / model)<input name="vehicle" placeholder="2019 Honda CR-V"></label>
    <label>Address where the car is<input name="address" autocomplete="street-address"></label>
    <label>What's the car doing?<textarea name="details" placeholder="Won't start, clicking noise… squeal when braking… A/C blows warm at red lights…"></textarea></label>
    <button class="btn btn-sun" type="submit">Send booking request</button>
    <p style="font-size:.85rem;color:var(--dim)">We'll call back to confirm your window.
    In a hurry? <a href="tel:{PHONE_TEL}">{PHONE_DISP}</a>.</p>
  </form>
</div></div></section>"""
    body += block_faq(light=True)
    body += block_cta()
    return head(title, desc, "contact-us",
                schema_breadcrumb([("Home", ""), ("Contact Us", "contact-us")]),
                schema_faq(FAQS)) + body + footer()

def page_thanks():
    title = f"Request Received | {BIZ}"
    body = phero("Thank you", "Got it. We're on it",
                 f"Your booking request is in. We'll call you back shortly to confirm a window. "
                 f"Need us right now? Call {PHONE_DISP}.")
    body += block_cta("While you wait", "Browse what else we can knock out in the same visit.")
    body += block_services(heading=False)
    return head(title, "Your booking request was received.", "thanks") + body + footer()

def page_legal(kind):
    if kind == "privacy-policy":
        title, h1 = f"Privacy Policy | {BIZ}", "Privacy Policy"
        prose = f"""
<p>{BIZ} ("we", "us") operates {DOMAIN}. This page explains what information we collect and
how we use it.</p>
<h2>What we collect</h2>
<p>When you call, text, email, or submit our booking form, we receive the contact and vehicle
details you choose to share. Typically your name, phone number, email, service address, and
a description of the problem. Online bookings are processed by Square, whose own privacy
policy governs that service.</p>
<h2>How we use it</h2>
<p>We use your information to schedule and perform the service you requested, to follow up
about that service, and for our own records. We do not sell your information, and we do not
share it with third parties except as needed to deliver the service (for example, parts
suppliers or the Square booking platform) or as required by law.</p>
<h2>Cookies and analytics</h2>
<p>This site is a set of static pages. Third-party services linked from it (such as Square)
may set their own cookies under their own policies.</p>
<h2>Contact</h2>
<p>Questions about this policy: <a href="mailto:{EMAIL}">{EMAIL}</a> or {PHONE_DISP}.</p>"""
    else:
        title, h1 = f"Terms of Service | {BIZ}", "Terms of Service"
        prose = f"""
<p>By using this website or booking service from {BIZ}, you agree to these terms.</p>
<h2>Estimates and approval</h2>
<p>Repair prices are quoted after diagnosis and approved by you before work begins. A quote
covers the described work; if we discover additional faults, we tell you and get approval
before proceeding.</p>
<h2>Service locations</h2>
<p>We work where the vehicle can be accessed safely and legally. You confirm you own the
vehicle or have the owner's authorization, and that we have permission to work at the
service address you provide.</p>
<h2>Website content</h2>
<p>Content on this site is provided for general information about our services and is not a
guarantee of a specific outcome for a specific vehicle. Diagnosis happens at the vehicle.</p>
<h2>Contact</h2>
<p>Questions about these terms: <a href="mailto:{EMAIL}">{EMAIL}</a> or {PHONE_DISP}.</p>"""
    body = phero("Legal", esc(h1), "The plain-English version is short. Here it is in full.")
    body += f'<section class="sec"><div class="wrap"><div class="prose">{prose}</div></div></section>'
    return head(title, f"{h1} for {BIZ}.", kind) + body + footer()

def page_404():
    body = phero("404", "That page drove off without us",
                 "The address you tried doesn't exist on this site. The good news: everything "
                 "useful is one click away.")
    body += ('<section class="sec"><div class="wrap"><div class="cta" '
             'style="display:flex;gap:1em;flex-wrap:wrap">'
             f'<a class="btn btn-sun" href="/">Back to the homepage</a>'
             f'<a class="btn btn-ghost" href="/services/">Browse services</a>'
             f'<a class="btn btn-ghost" href="tel:{PHONE_TEL}">{icon("phone")} {PHONE_DISP}</a>'
             '</div></div></section>')
    return head(f"Page Not Found | {BIZ}", "Page not found.", "404") + body + footer()

# ================================================================== EXTRAS
HUMANS = f"""/* humans.txt — {DOMAIN}/humans.txt */

   ____       __                __      _
  / __ \\_____/ /___ _____  ____/ /___  ( )____
 / / / / ___/ / __ `/ __ \\/ __  / __ \\|// ___/
/ /_/ / /  / / /_/ / / / / /_/ / /_/ / (__  )
\\____/_/  /_/\\__,_/_/ /_/\\__,_/\\____/ /____/
        F I N E S T   ·   M O B I L E   ·   M E C H A N I C

/* TEAM */
Site: {BIZ} — {TAGLINE.lower()}
Built by: Clickflame · Anthony Limpert
Personal site: https://anthonylimpert.com/
Contact: support@clickflame.com
From: the workbench of a mom-and-pop shop, for a mom-and-pop shop

/* MANIFESTO */
This site was built for the people whose car breaking down means missing
a shift, not missing a tee time. The weak and the weary deserve a
mechanic who comes to them — and a website that fights for them too.

We don't build for big corporations. Ever. The chains have ad budgets;
the little guys have us. Technology is the crowbar that pries the
playing field level, and we swing it for the small shops every time.

We're a mom-and-pop operation ourselves — with the best top-ranked pop
in the business doing the work.

/* STACK */
One Python file. Static HTML. No frameworks, no builders, no bloat.
Bricolage Grotesque + Inter. Hand-drawn SVG icons. JSON-LD throughout.
Hosted on Netlify, deployed from GitHub.

/* THANKS */
Yair, Paul, and every mechanic who ever fixed a car in a parking lot
while the owner watched and learned something.

// hello, fellow dev. view-source is the best documentation.
"""

ROBOTS = f"""User-agent: *
Allow: /

Sitemap: {DOMAIN}/sitemap.xml
"""

NETLIFY = """[build]
  publish = "site"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"

[[headers]]
  for = "/llms.txt"
  [headers.values]
    Content-Type = "text/plain; charset=utf-8"

[[redirects]]
  from = "/index.html"
  to = "/"
  status = 301
"""

def llms_txt():
    """/llms.txt for AI readers. Only what the site states. Every link is a
    page this build writes, in the trailing slash form url() makes canonical."""
    svc = "\n".join(f"- [{s['name']}]({url('services/' + s['slug'])})" for s in SERVICES)
    cit = "\n".join(f"- [{c[1]}, FL]({url('service-areas/' + c[0])})" for c in CITIES)
    posts = "\n".join(f"- [{p['title']}]({url('blog/' + p['slug'])})" for p in BLOG)
    return f"""# {BIZ}

> {BIZ} is a mobile auto repair service in {CITY_MAIN}, {STATE_FULL}. Certified mechanics come to your home, office or roadside with the tools and parts to fix the car where it sits. Phone {PHONE_DISP}.

Open {HOURS_LINE}. Rated {RATING} stars across {REVIEW_CT} reviews on Google. You approve the price before any work starts.

## How To Check Us

- [About and how to check us]({url('about')}): what we state, where each fact comes from, and how to check it
- [Reviews]({url('reviews')}): nine Google reviews quoted word for word
- [Google listing]({GMB_URL}): the source of the rating and review count
- [Contact]({url('contact-us')}): phone, email and booking

## Services

- [All services]({url('services')})
{svc}

## Service Areas

- [All service areas]({url('service-areas')})
{cit}

## Optional

- [Blog]({url('blog')})
{posts}
"""

# ================================================================== WRITE
def w(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full) or OUT, exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

def build():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)

    pages = {"index.html": page_home(),
             "services/index.html": page_services_index(),
             "service-areas/index.html": page_areas(),
             "about/index.html": page_about(),
             "contact-us/index.html": page_contact(),
             "thanks/index.html": page_thanks(),
             "privacy-policy/index.html": page_legal("privacy-policy"),
             "terms-of-service/index.html": page_legal("terms-of-service"),
             "reviews/index.html": page_reviews(),
             "blog/index.html": page_blog_index(),
             "404.html": page_404()}
    for s in SERVICES:
        pages[f"services/{s['slug']}/index.html"] = page_service(s)
    for c in CITIES:
        pages[f"service-areas/{c[0]}/index.html"] = page_city(c)
    for p in BLOG:
        pages[f"blog/{p['slug']}/index.html"] = page_blog_post(p)

    for path, content in pages.items():
        w(path, content)

    w("style.css", CSS)
    w("main.js", JS)
    if os.path.isdir("assets"):
        shutil.copytree("assets", os.path.join(OUT, "img"))
    w("humans.txt", HUMANS)
    w("robots.txt", ROBOTS)
    w("llms.txt", llms_txt())
    w(f"{INDEXNOW_KEY}.txt", INDEXNOW_KEY)

    canon = [""] + ["services"] + [f"services/{s['slug']}" for s in SERVICES] \
          + ["service-areas"] + [f"service-areas/{c[0]}" for c in CITIES] \
          + ["reviews", "blog"] + [f"blog/{p['slug']}" for p in BLOG] \
          + ["about", "contact-us", "privacy-policy", "terms-of-service"]
    today = datetime.date.today().isoformat()
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in canon:
        sm.append(f"  <url><loc>{url(p)}</loc><lastmod>{today}</lastmod></url>")
    sm.append("</urlset>")
    w("sitemap.xml", "\n".join(sm))

    with open("netlify.toml", "w", encoding="utf-8") as f:
        f.write(NETLIFY)

    n = len(pages)
    print(f"Built {n} pages -> {OUT}/  (+ style.css, main.js, humans.txt, robots.txt, sitemap.xml)")

if __name__ == "__main__":
    build()


