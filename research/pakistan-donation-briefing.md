# Evidence Briefing: Making "Iman Donation Trust" a Locally-Correct Pakistan Donation Prototype

**Prepared for:** the student-built SPA at `https://iman-coll.github.io/iman-donation-trust/`
**Method:** web research only. Every factual claim below is tied to a URL I actually opened, marked `[fetched]`, or is explicitly flagged as unverified / low-confidence. This is **not legal advice**.

## How to read the confidence labels

| Label | Meaning |
|---|---|
| `[fetched]` | I opened this page in this session and read the content |
| `[snippet]` | I saw this in search results (title/fragment) but did **not** open the page — treat as a lead |
| `[PDF-blocked]` | The document exists at a real URL but I could not read it (my fetch tool rejects `application/pdf`) |
| **UNVERIFIED** | I could not confirm this; do not assert it in the app |
| **CONFLICT** | Two sources disagree; the app must show the conflict, not pick a side silently |

---

## 0. Three corrections you should make before anything else

The app's current helpline set is **two-thirds right and one-third wrong**.

| App currently says | Reality | Evidence |
|---|---|---|
| Edhi 115 | ✅ **Correct** | Edhi's own site header shows "Emergency Call 115" `[fetched]`; and the Government of Sindh's Commissioner Karachi office lists "Edhi Ambulance — 115" `[fetched]` |
| Chhipa **1121** | ❌ **Wrong. Chhipa's published helpline is 1020** | Chhipa's own site: "Ambulance Helpline 1020", UAN `+92-21-111-92-1020`, phone `+92-21-111-111-134` `[fetched]`. Commissioner Karachi's official table also lists "Chhipa Ambulance — 1020" `[fetched]`. **1121 is not a Chhipa number in any source I found.** (1121 is a Government of Punjab citizen helpline; 1122 is Rescue.) |
| Saylani 111-729-526 | ✅ **Correct** | Saylani's own site footer: `+92 21 111 729 526` (UAN), plus `+92 21 38729526`, `+92 311 1729526` `[fetched]` |

**Recommended additions** (all from the Commissioner Karachi official emergency-services table `[fetched]`):
Rescue 1122 · Madadgar Police 15 · KMC Fire Brigade 16 · Aman Ambulance 1101 · Traffic Police 915.
Plus Al-Khidmat Foundation's published donation line **0800 44448** (toll-free) and cash pick-up **0304 111 4 222** `[fetched]`.

> **Design rule this implies:** never hard-code a helpline without storing the source URL and the date you checked it. Two of the three numbers the app ships were sourced from somewhere other than the organisation. Put `source_url` and `verified_on` on every helpline row.

---

## 1. The real Pakistani donation ecosystem

### 1.1 Organisations I could verify in detail

**Edhi Foundation** — `https://www.edhi.org` `[fetched]`
- Helpline 115. Fundraising categories published: Sadqa, Zakat, Fidya, Food Bank, Emergency Services, Lillah, Aqeeqa, Flood Relief, Qurbani 2026, Zakat Calculator.
- Services directory includes **Charitable Shop** — described on-page as "offers affordable and **donated items** to those in need" `[fetched]`. This is the closest thing to a formal in-kind channel at Edhi, and it is a *resale/redistribution* model, not a "we will collect your bag of clothes" model.
- Also runs Langer Service (free kitchen), Edhi Animal Hostel, Online Qurbani Service, Graveyard, Missing Person, Welfare Centers, Destitute Homes.
- ⚠️ **Its homepage carries a live scam warning** naming four fraudulent domains (`edhius.com`, `edhiusa.com`, `edhiusa.net`, `edhiusa.org`) `[fetched]`. See §6.
- **UNVERIFIED:** Edhi does not publish, anywhere I could find, an itemised list of *which* used goods it accepts, nor a doorstep-pickup telephone workflow for goods.

**Chhipa Welfare Association** — `https://www.chhipa.org` `[fetched]`
- **"You Call We Collect"**: "Call us at +92-21-111-92-1020 / +92-21-111-111-134 and we will collect your donations from your location." This is the clearest published doorstep-collection offer I found from any major Pakistani trust `[fetched]`.
- ⚠️ **Important caveat:** the page says "your donations" without specifying *goods*. Chhipa's other collection pages (courier, bank, JazzCash, Easypaisa, UPaisa, Konnect, Omni, IBFT, internet banking) are all **financial**. Whether the "You Call We Collect" vehicle actually picks up *used clothing* is **UNVERIFIED**. Do not tell users "Chhipa will collect your clothes" without confirming.
- Published service/price menu (a genuinely useful data model — see §2): Dastarkhwan meals (claims 100,000 meals/day), Chhipa Ration, Sadqa & Aqiqa goats/cows, Orphanage, Old Home, Women's Shelter, Newborn Home, Graveyard, Morgue, Kitchen, Ambulance, Education, IT, Clean Water, Solar, **Collective Qurbani Project (all over Pakistan)**, Dowry & Marriage Help, Scholarship.

**Saylani Welfare International Trust** — `https://saylaniwelfare.com` `[fetched]`
- UAN `+92 21 111 729 526`; WhatsApp `0311 1729526`; USA/UK/Canada lines published.
- **Accepts donated used medical equipment.** The Medical Equipment service page explicitly serves "individuals who donate medical supplies and **donate used medical equipment**", covering wheelchairs, walkers, hospital beds, oxygen cylinders, hearing aids, assistive devices `[fetched]`. This is a verified **in-kind** pathway — an unusually good one, because medical equipment is high-value and hard to place elsewhere.
- Donation categories: Food (from PKR 300), Sadqa (from PKR 1,000), Zakat, Sadqa/Aqiqah Animal, Education, Medical, Sadqa e Jariah.

**Al-Khidmat Foundation** — `https://alkhidmat.org` `[fetched]`
- Helpline **0800 44448** (toll-free); **0304 111 4 222**; WhatsApp `0300 0776016`; head office Lahore `+92 42 3802 0222`.
- **"Qurbani Doorstep Collection"** — but read it carefully: "you can donate through **cheques or bank drafts**, simply call at 0800 44 44 8 or 0304 111 4 222 and Alkhidmat's representative will collect it" `[fetched]`. So **doorstep pickup here means picking up a cheque, not goods.** The prototype must not conflate the two.
- Settlement rails it publishes: Visa/MasterCard, JazzCash, Easypaisa, bank transfer with named IBANs (Bank of Punjab, Meezan Bank), cash pick-up, in-person collection centres.
- Self-declared registration: `RP/4243/L/S/90/375`, NTN `C777982`, and — critically — **"tax exempted under FBR act 2(36)c"** `[fetched]`. See §5.
- Qurbani 2025 impact claims are **internally inconsistent on the same page**: an impact block says "Cows/Bulls 6,898 · Goats/Sheep 3,593 · Meat Packs 280,846 · Beneficiaries 1.4 Million", while the FAQ says "10,491 animals … over 2.2 million deserving Pakistanis" `[fetched]`. **Do not repeat either number as fact** — this is exactly the kind of thing a verification layer should catch.

**Alamgir Welfare Trust International** — `https://alamgirwelfaretrust.com.pk` `[fetched]`
The single richest **in-kind** service catalogue I found:
- **Used Medicine Department** — a dedicated department for donated medicines `[fetched]`
- **Alamgir Book Bank** — books `[fetched]`
- **Malboosat** — clothing `[fetched]`
- Blanket Distribution; Ration Distribution; Emergency Medical Equipment; Collective Sacrifice; Aqeeqa/Sadaqa Bakra; Funeral Services
- Publishes annual audit reports **and** annual FBR tax-exemption orders ("U.S 236C", T.Y. 2024–2027) `[fetched]` — an excellent model for a "show me the paperwork" trust panel.
- Helpline from site header: `+92 (21) 111-153-153` `[fetched]`

**Indus Hospital & Health Network** — `https://indushospital.org.pk`, `https://donate.indushospital.org.pk` `[snippet]`
- Accepts in-kind: newsroom items document "The C.A.S. School Extends Generous **In-Kind Donation** for Flood Relief Efforts" and "HUBCO **Donates Dialysis Machine**" `[snippet]`. So equipment and relief goods, via corporate/institutional donation.
- **UNVERIFIED:** no public consumer "drop off used clothes here" pathway; no helpline number confirmed.

**Dar-ul-Sukun** — `https://darulsukun.com` `[snippet]`
- In-kind channels indicated by page titles: "**Medicines For The Marginalized**" (`/donate-medical-supplies/`) and "**Donate a Diaper**" (`/donate-a-diaper/`); Lemmens Home for children with severe disabilities `[snippet]`.
- ⚠️ My direct fetch of `/donate-medical-supplies/` was **blocked by a redirect to `recaptcha.cloud`** — so I could not read the actual accepted-items policy. **UNVERIFIED at detail level.**

**Sundas Foundation** — `https://sundas.org` `[snippet]`
- Free blood transfusions for thalassaemia and haemophilia patients; centres incl. Karachi; dedicated blood-donation pages (`/Donation/BloodDonation`, `/donate-blood`). **Blood is its in-kind currency.** **UNVERIFIED:** helpline number, and whether they take any goods.

**Shaukat Khanum Memorial Cancer Hospital & Research Centre** — `https://shaukatkhanum.org.pk` `[snippet]`
- Runs annual Zakat campaigns; publishes a "Donations all countries" page. Predominantly **cash/Zakat**. **UNVERIFIED:** any in-kind pathway or helpline.

**The Citizens Foundation (TCF)** — `https://www.tcf.org.pk/zakat` `[snippet]` — Zakat/education, cash. **UNVERIFIED:** in-kind, helpline.
**Zindagi Trust** — `https://zindagitrust.org/donate` `[snippet]` — education, cash/cheque. **UNVERIFIED:** in-kind, helpline.
**NOWPDP** — `https://nowpdp.org.pk/donate-now` `[snippet]` — disability organisation, donation page + donor page. **UNVERIFIED:** in-kind, helpline.
**SOS Children's Villages Pakistan** — `https://www.sos.org.pk/Donations`, `/donation-for-child-pakistan` `[snippet]` — **orphan/child sponsorship**, cash. **UNVERIFIED:** in-kind.
**Pakistan Sweet Home** — `https://www.pakistansweethome.org.pk` `[snippet]` — orphan care & education, has a "Service Policy" page. **UNVERIFIED:** in-kind, helpline.
**Akhuwat Foundation** — `https://akhuwatfoundation.com.pk`, `https://akhuwat.org.pk` `[snippet]` — Qarz-e-Hasana (interest-free lending), Qurbani. Note this is a **loan** model, not a goods-collection model. **UNVERIFIED:** in-kind, helpline.
**Rizq** — `https://rizq.org` `[fetched]` — Rizq Ration, Rizq Dastarkhwan, Rizq Khana, **Rizq Bachao** (surplus-food rescue), Kissan Dost, GroRizq, Rizq Breeds, Housing Innovation Lab, plus Ramadan/Qurbani/Muharram/Arba'in seasonal campaigns. **Food-centric and cash-driven.** No consumer app or in-kind goods pathway verified.
**JDC Welfare Organization** — `https://jdcwelfare.org` `[snippet]` — has a free dialysis centre and an online checkout. **UNVERIFIED:** in-kind policy, helpline.
**Rahma** — `https://rahmapk.org` `[snippet]` — published a Ramadan food-package newsletter. **UNVERIFIED:** in-kind policy, helpline.
**Khana Ghar** — appears via a LaunchGood fundraiser page `[snippet]`. **UNVERIFIED — no official website or helpline confirmed. Do not list it with a phone number.**
**Robin Hood Army Pakistan** — Pakistan operations do exist (BBC Sounds documentary "Pakistan's Robin Hood Army"; Express Tribune topic page) `[snippet]`, volunteer surplus-food redistribution. **UNVERIFIED:** any official `.pk` site, helpline, or goods-collection address.

### 1.2 Honest summary of §1

- I could verify **published helplines** for Edhi (115), Chhipa (1020), Saylani (111-729-526), Al-Khidmat (0800 44448) and Alamgir (111-153-153) only. For every other organisation the app lists, **the helpline is unverified**.
- I could verify a genuine **goods** intake pathway for only four: **Saylani** (used medical equipment), **Alamgir** (medicines, books, clothing), **Dar-ul-Sukun** (medicines, diapers — detail unreadable), **Indus** (equipment/relief goods, institutional). Edhi's Charitable Shop clearly *uses* donated goods but doesn't publish a consumer intake spec.
- **The app's implied promise — "34 sites across Pakistan will take your clothes, books, toys and food" — is very likely overstated on current evidence.** Rebuild the directory so each site carries: what it accepts, what it refuses, pickup yes/no, and a source URL + check date.

---

## 2. How giving is actually organised in Pakistan — and the features that follow

### 2.1 The giving categories are real product SKUs

The most useful artefact I found is Chhipa's own published donation menu `[fetched]`, which reads like a schema:

| Category | Chhipa's published rate(s) `[fetched]` |
|---|---|
| Zakat | category offered |
| Sadqa | category offered |
| **Fitrana** | Wheat Rs 300 · Barley Rs 500 · Dates Rs 2,000 · Raisins Rs 3,000 · Ajwa Dates Rs 10,000 |
| **Fidya** | Rs 400 (one fast) · Rs 12,000 (thirty fasts) |
| **Roza Kaffara** | Rs 400 × 60 = Rs 24,000 |
| Sehri / Iftari | Rs 200 each · Rs 400 both · Rs 12,000 one person for one month |
| Iftar Box | Rs 200 |
| **Ramadan Ration Package** | Rs 5,000 per family (target: 100,000 families) |
| **Collective Qurbani** | "All Over Pakistan" |
| Ration items | Wheat 50kg Rs 7,500 · Rice 25kg Rs 7,250 · Sugar 50kg Rs 6,200 · Cooking oil 16L Rs 6,250 · Winter blanket Rs 1,500 |
| Also listed | Ushr, Khummas, Kaffara, Khairat, Aqiqa, Kafalat (Rs 10,000/month/family), marriage & dowry help |

> ⚠️ **These are Chhipa's own 2025/26-era rates, not a national standard.** Fitrana and Fidya amounts are set by scholars/organisations and change annually. The right app design is a **per-organisation rate table with a source link and an "as published on <date>" stamp** — never a single global number.

Other organisations' category sets confirm the same taxonomy `[fetched]`/`[snippet]`:
- **Edhi:** Sadqa, Zakat, Fidya, Lillah, Aqeeqa, Qurbani, Food Bank, Flood Relief `[fetched]`
- **Al-Khidmat:** Zakat, Sadaqah, **Sadaqah Jariyah**, Qurbani (Pakistan + Gaza), Dhul Hijjah resources, orphan sponsorship (Aghosh) `[fetched]`
- **Saylani:** Sadqa e Jariah, Sadqa/Aqiqah Animal, Food, Education, Medical `[fetched]`
- **TCF / SKMCH:** Zakat `[snippet]`
- **SOS:** child sponsorship `[snippet]`

### 2.2 Ramadan dominates the calendar

Every major organisation's donation surface is Ramadan-weighted: Chhipa's menu is dominated by Sehri/Iftari/Fidya/Kaffara/Fitrana/Ramadan ration `[fetched]`; Rizq has a dedicated Ramadan 2026 campaign page `[fetched]`; Al-Khidmat's surface is Dhul Hijjah/Qurbani-weighted `[fetched]`.
**Feature that follows:** a **Hijri-aware giving calendar** — Ramadan, the last ten nights, Laylat al-Qadr, Dhul Hijjah's first ten days, Eid al-Adha, Muharram (Rizq runs a Muharram campaign `[fetched]`), Rabi al-Awwal. Show what each organisation is doing *this* season, not a generic list.

### 2.3 Itikaf, langar, orphan sponsorship, winter drives

- **Itikaf** — a Ramadan practice, but I found **no** organisation publishing an itikaf-support product. **UNVERIFIED as a donation category.** Treat it as a user-education item, not a bucket.
- **Langar / free kitchens are extremely real**: Edhi "Langer Service (Free Kitchen)" and Chhipa "Dastarkhawan" (claims 100,000 meals daily) `[fetched]`; Rizq Dastarkhwan `[fetched]`.
- **Orphan sponsorship** is institutionally organised: SOS "Sponsor a Child in Pakistan" `[snippet]`, Al-Khidmat Aghosh, Chhipa Orphanage `[fetched]`.
- **Winter drives**: Al-Khidmat winter package/blanket distributions (blog + 2021 annual report) `[snippet]`, Alamgir Blanket Distribution `[fetched]`, Shifa Foundation "Spread the Warmth" `[snippet]`, Chhipa blanket at Rs 1,500 `[fetched]`. **Feature:** a seasonal "winter" mode from ~November to February.
- **Ration bags ("rashan")** are a first-class product, not a generic "food" bucket: Chhipa Ration Package Rs 5,000/family `[fetched]`, Rizq Ration `[fetched]`. **Feature:** model a ration bag as a **bill of materials** (flour, rice, oil, sugar, pulses, tea) with per-item quantities — donors in Pakistan think in bags, not in rupees-per-meal.

### 2.4 Emergency appeals — use verified numbers only

**2025 monsoon floods** (IFRC Operation Update #3, published Jan 2026, citing NDMA and OCHA) `[fetched]`:
- Nationwide death toll **1,037** (Punjab 304, KP 504); injuries **1,067**
- Displacement down to **~80,000** (from ~150,000 in Oct 2025); >95% of Punjab's 2.7m evacuees repatriated
- **~4.9 million** people affected overall in Punjab, >4.2m directly in Aug–Sep
- **229,760** houses destroyed or partially destroyed nationwide (92% in Punjab); 2,811 km roads disrupted; 790 bridges affected
- 1.12 million hectares inundated in Punjab (9% of arable land); >22,800 livestock deaths; agricultural losses >US$1.23bn
- Total economic damage ~**Rs 822 billion (~US$3bn)**; infrastructure losses >Rs 307bn
- Punjab Home Department / NDMA rescue figures: 7,768 rescues in Punjab, 2.9m people and 450,000 animals evacuated

⚠️ **The 2022 floods are the event the app's copy references.** In this session I could **not** fetch a primary-source figure for 2022 (the UNOCHA 2022 sitrep appeared only as a `[snippet]`/`[PDF-blocked]`). **Do not print any 2022 casualty number without fetching the source.** If you need it, the correct places are `ndma.gov.pk` situation reports and `reliefweb.int/country/pak`.

**Feature that follows:** an emergency mode that binds an appeal to a **named, dated, linked** situation report, and refuses to display an appeal with no source. That single rule kills most scam-appeal UI.

### 2.5 In-kind giving is genuinely common — the evidence

- Saylani's own text markets to people who "donate used medical equipment" `[fetched]`
- Alamgir runs three separate in-kind departments: Used Medicine, Book Bank, Malboosat `[fetched]`
- Dar-ul-Sukun runs medicines and diaper drives `[snippet]`
- Edhi's Charitable Shop redistributes donated items `[fetched]`
- Indus received an in-kind school donation for flood relief and a donated dialysis machine `[snippet]`

So an in-kind-first app is **justified**. The gap it fills is not "people don't donate goods" — it's "**nobody publishes where each good can actually go, and under what condition rules.**"

---

## 3. In-kind donation logistics the prototype should model

### 3.1 Doorstep pickup — the honest state of play

| Organisation | Published pickup | What exactly | Evidence |
|---|---|---|---|
| Chhipa | ✅ "You Call We Collect" | "your donations" — **goods unspecified** | `[fetched]` |
| Al-Khidmat | ✅ "Qurbani Doorstep Collection" | **cheques/bank drafts only** | `[fetched]` |
| Everyone else I checked | ❌ nothing published | — | `[fetched]`/`[snippet]` |

**This is the single biggest product gap and the biggest honesty risk.** I could **not** verify a single major Pakistani trust that publicly commits to collecting **used clothing, books or toys** from a donor's home. The app must therefore:
1. Separate **"documented pickup"** (with source + date) from **"ask them"** (phone/WhatsApp CTA).
2. Never generate a pickup promise the charity hasn't published.
3. Model a **drop-off** path as the default, with pickup as the exception — which is also how it works in practice: donors carry goods to the nearest Edhi/Alamgir/Saylani centre.

### 3.2 The best available in-kind logistics model in South Asia: Goonj (India)

India's Goonj is the reference implementation for exactly this problem `[fetched]`:
- **Sharing Camps** — one-time and monthly collection camps in cities
- **Dropping Centres** — permanent drop points
- **Institutional drives** — a form for corporate/school/college/association drives
- **"Send Material via Delivery Apps"** — donors book Porter / Dunzo / Uber Packages to a "Goonj Centre of Circularity". *This is the single most transferable idea:* in Pakistan the equivalents are **Bykea, Careem/Talabat courier, TCS, Leopards, M&P** — the app could generate a "send your parcel" instruction with the charity's verified address rather than promising a van.
- **Published material guidelines** (`https://goonj.org/material/` — the page rendered empty for my fetch, so `[PDF-blocked]`-grade) and an FAQ confirming accepted categories: "clothing … we also encourage people to contribute other household items like **stationery, toys, utensils**" `[fetched]`.
- Programmes that give the goods a *destination* rather than a dump: Cloth for Work, School to School, Not Just A Piece of Cloth, Rahat (disaster).

**Recommendation:** copy Goonj's structure, not its content. Pakistan has no equivalent, which is precisely the opportunity.

### 3.3 Condition grading

**UNVERIFIED.** I found **no** Pakistani charity publishing a condition rubric for used clothes or books. Do not invent one and present it as authoritative.

The defensible approach for a prototype:
- Ship a **clearly-labelled prototype rubric** (e.g. A = new/unused with tags; B = worn but clean, no holes/stains, all fasteners working; C = serviceable but visibly worn, suitable for rag/industrial use; D = not acceptable) and label it in the UI as **"our own grading guide, not a charity's published policy."**
- The critical rule is the **hard-reject list**, which protects the charity's volunteers from being used as a waste-disposal service. **UNVERIFIED for Pakistan**, but the widely-followed categories are: soiled/soiled-through, mouldy or damp clothing; underwear and socks (used); torn/unusable fabric; single shoes or heavily worn footwear; opened or expired medicines; **medical waste and sharps**; broken glass; CRT televisions and leaking batteries; hazardous chemicals; broken furniture.
- ⚠️ **One Pakistan-specific inversion:** unlike many countries, donated **medicines** are actively accepted by at least one major trust (Alamgir's Used Medicine Department `[fetched]`). So the app must not blanket-ban "medicines" — it must route them to the specific org that accepts them, and refuse them elsewhere. That nuance is a great demonstration of why a generic list is wrong.

### 3.4 Qurbani hide / skin (chamra) donation

This is a well-documented, **regulated, and shrinking** revenue stream — model it carefully.

From Arab News Pakistan, citing **Pakistan Tanners Association (PTA)** data `[fetched]`:
- Pakistan expected to generate a record **7.5 million hides worth ~Rs 8.7 billion (~US$31m)** after Eid al-Adha
- Composition: **~2.8m cow/bull hides, 4.3m goat skins, 500,000 sheepskins, ~30,000 camel hides**
- Prices recovered: average cow hide **Rs 2,000** (up from Rs 1,200); goat skin **Rs 600** (up from Rs 325) — but still far below the Rs 3,000–4,500 of 2015–2017
- **Spoilage is the core logistical failure:** Eid now falls in peak summer (and will for another 6–8 years), and Pakistan "lacks an organized, centralized slaughtering infrastructure", so hides are not salted in time and tanners bid lower
- **Al-Khidmat collected 352,000 hides nationwide, incl. 131,000 in Karachi** (up from 341,000 / 127,000) — but its spokesperson says "**hides are no longer a primary source of funding**… It has become a tradition that keeps our volunteers engaged", and that "**strict government regulations have also barred smaller organizations from collecting skins**"
- Punjab has separately **banned skin collection by banned outfits** and issues an Eid security plan `[snippet]` (APP)

**Features that follow:**
- Chamra collection should be modelled as **"route me to a large, registered collector"** — never as an open marketplace, and never for small/unregistered groups.
- The app should surface the **salting-and-speed** instruction (hides must be salted and moved fast) because that is where the value is lost. That's genuinely useful domain content no competitor has.
- Show the **live/indicative hide price** so donors understand the real value of what they're giving.

### 3.5 E-waste

**UNVERIFIED / LOW CONFIDENCE.** What I found:
- A Punjab Government **draft** SOP for e-waste management under the PRIDE programme (`piu.punjab.gov.pk`) `[snippet]` — a draft, not necessarily in force
- The LJCP *Environmental Laws Compendium* contains hazardous-waste handling provisions (including duties on owners of premises where hazardous waste is kept/treated/disposed) `[snippet]`
- ⚠️ I could **not** verify a single, in-force, named Pakistani e-waste regulation, nor a licensed e-waste recycler. I cannot confirm Pakistan's status under the Basel Convention from anything I read.

**Recommendation:** do **not** claim to know where e-waste goes in Pakistan. Feature it as a **"we're still verifying this — here's what we know"** card, or omit it. Claiming a bogus e-waste route is exactly the failure mode this briefing is trying to prevent.

---

## 4. Payments and money-movement rails

### 4.1 The rails that exist

**Raast** — `https://www.sbp.org.pk/raast` `[fetched]`
- "Pakistan's national instant payment system, enabling end-to-end digital payments among individuals, businesses, and government entities in real time."
- Operated by **Raast Payments Pakistan (Private) Limited (RPP), a wholly-owned subsidiary of the State Bank of Pakistan**.
- Designed for **low-value retail** with instant settlement and interoperability; participants include commercial banks, microfinance banks, government entities, and regulated fintechs (EMIs and PSPs).
- SBP lists **Join Raast**, **Cross Border Payments** (an MoU with the Arab Monetary Fund to integrate Raast with **Buna**), and **Bulk Payments**. A **person-to-merchant** page also exists at `sbp.org.pk/our-subsidiaries/raast/raast-person-to-merchant` `[snippet]` — I did not open it.
- **Practical read:** Raast is the right rail *conceptually* for donations, but onboarding is institutional. A student prototype cannot "use Raast"; it can only link to a registered organisation's Raast/IBAN details.

**1LINK / 1BILL** — `https://1link.net.pk` `[snippet]`
- 1LINK operates the shared ATM switch and **1BILL** bill-payment service; it onboards third parties as **aggregators on 1BILL Services** (e.g. a published PR for Kaizen Hive) and a 1BILL biller-prefix list is published by banks (Standard Chartered) `[snippet]`.
- **UNVERIFIED:** whether a charity can become a 1BILL biller directly, what the commercial terms are, or whether donation collection via 1BILL is supported.

**Easypaisa / JazzCash (mobile wallets)** — `[fetched]`/`[snippet]`
- Chhipa publishes dedicated pages for **JazzCash, Easypaisa, UPaisa, Konnect** and **Omni** `[fetched]` — so wallet donation is clearly a mainstream route for large charities.
- Al-Khidmat's Qurbani checkout accepts JazzCash and Easypaisa `[fetched]`.
- Easypaisa publishes **Merchant QR Terms & Conditions** at `easypaisa.com.pk/public-information/downloads/` `[snippet]`.
- **UNVERIFIED:** the exact merchant-onboarding requirements and whether a non-registered entity can hold a donation-collecting merchant wallet.

**Cards** — Edhi offers "Donate with Card" `[fetched]`; Al-Khidmat accepts "any Visa or MasterCard" `[fetched]`.
- **UNVERIFIED:** Stripe's availability to Pakistani merchants (I did not confirm this either way — do not assert it), and the full list of Pakistani payment gateways. `[snippet]` surfaced Pakistani gateway documentation (PayPro, WooshPay) but I did not verify their onboarding rules.

**Bank transfer / IBFT** — the workhorse. Al-Khidmat publishes full **IBANs** (Bank of Punjab `PK14BPUN…`, Meezan Bank `PK11MEZN…`) `[fetched]`; Chhipa publishes "Donate Via Bank", "Inter Bank Fund Transfer", "Internet Banking", "Money Transfer" pages `[fetched]`.

### 4.2 ⭐ Can a hobby prototype legally collect money? — the decisive source

**State Bank of Pakistan, BPRD Circular Letter No. 04 of 2012 ("Prudential Regulations M-1 to M-5")** — `https://www.sbp.org.pk/circulars/bprd-circular-letter-no-04-of-2012` `[fetched]`. This is the binding instruction to all banks/DFIs on NGO/NPO/charity accounts. Its provisions:

1. Banks must run **enhanced due diligence, including senior management approval**, before establishing a relationship with an NGO/NPO/charity, "to ensure that these accounts are used for legitimate purposes and the transactions are commensurate with the stated objectives and purposes."
2. Accounts must be opened **in the name of the relevant NGO/NPO as per the title given in its constituent documents**.
3. **"In case of advertisements through newspapers or any other medium, especially when bank account number is mentioned for donations, Banks/DFIs will ensure that the title of the account is the same as that of the entity soliciting donations."** If the titles differ → caution-mark the account and **consider filing a Suspicious Transaction Report (STR)**.
4. **"Personal accounts shall not be allowed to be used for charity purposes/collection of donations."**
5. **Documents required to open an NPO account:** certified copies of (a) registration documents/certificate and (b) by-laws/rules & regulations; (ii) governing-body resolution authorising account opening and signatories; (iii) attested CNICs of authorised persons and governing-body members; (iv) any further documents needed to assess the risk profile, including annual accounts/financial statements.
6. Non-compliance is actionable under the **Banking Companies Ordinance, 1962**.

**Direct implication for this prototype:**
- A student project **cannot** collect donations into a personal Easypaisa/JazzCash/bank account. That is expressly prohibited, and any bank doing it risks an STR.
- Therefore: **the prototype should not collect money at all.** It should be a **directory + logistics + receipt/record layer** that **deep-links out** to each verified charity's own official rails (their IBAN, their wallet merchant ID, their card page). This is both legally sane and a better product.
- If the team ever wants to collect money, it must first stand up a registered entity and an account in that entity's name, with the paperwork in item 5. That is a real, months-long process — see §4.3.

### 4.3 What a real trust actually needs — registration and licensing

| Vehicle / requirement | Status in my research |
|---|---|
| **Voluntary Social Welfare Agencies (Registration and Control) Ordinance, 1961** | ✅ Exists; text on `pakistancode.gov.pk` `[snippet]`. Provincial social-welfare departments publish NPO registration procedures (e.g. `swd.sindh.gov.pk` application procedure `[snippet]`) |
| **Societies Registration Act, 1860** | ⚠️ **I did not fetch the statute.** It is the classic vehicle for a "society" and Al-Khidmat's registration number (`RP/4243/L/S/90/375`) has the shape of a societies registration. **Verify before citing.** |
| **Trust Act, 1882** | ⚠️ **I did not fetch the statute.** Classic vehicle for a public charitable trust. **Verify before citing.** |
| **SECP licensing under section 42, Companies Act 2017** | ✅ Real: SECP publishes a **Section 42 Guidebook (English and Urdu)** at `secp.gov.pk/document/section-42-guidebook-english-and-urdu/` and a procedure guide `[snippet]`. This is the "not-for-profit company" route. |
| **Provincial Charity Commissions** | ✅ **Major finding — see table below** |
| **EAD / foreign funding** | ✅ Real portal: `ngo.ead.gov.pk` with published FAQs `[snippet]`. Foreign-funding approval is a separate regime. **UNVERIFIED at detail level (PDFs).** |
| **PCP / FBR NPO approval** | ✅ See §5 |
| **Punjab Charities Act 2018 (Act V of 2018)** | ✅ Full text on FAOLEX: `faolex.fao.org/docs/pdf/pak225112.pdf` `[PDF-blocked]`; Punjab Charity Commission runs a registration portal with a published user guide `[snippet]` |
| **Sindh Charities Act 2019 (Sindh Act No. XVI of 2019)** | ✅ `https://charitycommission.sindh.gov.pk` `[fetched]` |
| **KP Charity Commission** | ✅ `https://charities.kp.gov.pk` with an Urdu user guide `[snippet]` |
| **Balochistan** | ⚠️ A document titled "Charities Regulation Balochistan" exists `[snippet]` (`[PDF-blocked]`). **Low confidence — verify.** |

**⭐ The provincial charity commissions are the most important legal discovery for this app.** The Sindh Charity Commission's own front page states its purpose: the Sindh Charities Act 2019 exists "to register and regulate charities **and collection and utilization of charitable funds**… for the registration, administration and regulation of charities, **fund-raising and collection and utilization of charitable funds**" `[fetched]`.

That means **collecting charitable funds is itself a regulated activity in at least Sindh, Punjab and KP**, with a registration requirement and — importantly — a **public register**. Sindh's site exposes:
- **"Search for a Charity"** → `mis.charitycommission.sindh.gov.pk/Public_Search_Charity.aspx` `[fetched]`
- A published **Proscribed Organizations** list `[fetched]`

**So the answer to "may a hobby prototype collect money?" is: no, not safely, and in the provinces with charity commissions, public fund-raising without registration is exactly what the regulator exists to police.** Say this plainly in the app and in any report. **This is not legal advice — a lawyer should confirm the current position.**

---

## 5. Tax / deduction mechanics donors care about

### 5.1 The NPO approval route: section 2(36)

**Pakistan Centre for Philanthropy (PCP)** — `https://pcp.org.pk/npo-certification-2/` `[fetched]`:
- PCP is **"a designated Certification Agency by the Federal Board of Revenue (FBR), Government of Pakistan."**
- "In accordance with the **Section 2(36) of Income Tax Ordinance, 2001**, organizations working in Pakistan are required to seek approval of **Commissioner Inland Revenue** to be recognized as not for profit."
- "As part of the procedural requirement … provided in **rules 211(2)(g), 213(2)(d), 217(1)(b)(vii), 220(1)(b)(vi), 220A(3)(d) and 220A(7)(1)(b)(iv) of Income Tax Rules 2002**, PCP conducts performance evaluation of NPOs **on behalf of FBR**."
- Programme founded **2003**, authorised by the Revenue Division; **"over 5000 welfare/not for profit organizations"** have been certified.
- Evaluation domains: Legal & Regulatory Compliance · General Public Utility Compliance · Institutional Mechanisms of Oversight · Compliance with Tax Laws · Financial Management · Organizational Policies · Program Delivery.
- Published benefits are **withholding-tax related**: collection of tax at imports, withholding from dividends, interest (national savings & bank accounts), loans/borrowings, payments for goods/services/contracts, rent, prize bonds, cash withdrawals, motor vehicle purchase/tax, electricity bills.

**Corroboration that 2(36)(c) is the operative clause:**
- Al-Khidmat's own footer: "**tax exempted under FBR act 2(36)c**" `[fetched]`
- Alamgir publishes annual tax-exemption certificates labelled "U.S 236C" for T.Y. 2024–2027 `[fetched]`
- An ICMAP document is titled "**2(36)(C) (APPLICATION FOR APPROVAL AS NON-PROFIT ORGANIZATION)**" `[snippet]`

**So "section 2(36)" in the app's original brief is directionally right**: it is the NPO-recognition provision, and PCP certification is the FBR-delegated performance evaluation that sits behind it. The app can safely say: *"PCP certification means FBR has had this NPO independently evaluated. Look for it."*

### 5.2 The major recent change — clause (61) was withdrawn in 2021

Per **KPMG's brief on the Tax Laws (Second Amendment) Ordinance 2021** `[snippet]` (`[PDF-blocked]`), the amendment tabled **"Exemptions withdrawn — Clause (61): Amount paid as donation to certain in[stitutions]"**.

**CONFLICT ALERT:** that is the *old* Second Schedule clause (61). Meanwhile, **section 61 of the Ordinance is the current donation tax-credit provision** (a different thing that shares the number 61). These two are easy to confuse and the app must not.

- **Clause (66) of Part I of the Second Schedule** is the NPO *income* exemption. Per HZ & Co's comments on the Finance Act 2025: **"(66) Subject to the provisions of section 100C, any income derived by the following institution, foundations, societies, boards, …"** `[snippet]` — i.e. the NPO's own income is exempt, but **conditioned on section 100C**.
- **Section 100C** is titled "**Tax credit for charitable organizations**" per Yousuf Adil's Budget 2025-26 highlights `[snippet]`.

### 5.3 What the donor actually gets — and where sources disagree

| Point | pkrevenue.com (Nov 2025) `[fetched]` | lex-form.com (2026) `[fetched]` |
|---|---|---|
| Legal basis | Section 61 ITO 2001 | Section 100C ITO 2001 |
| Eligible donees | Educational institutions; government hospitals/relief funds; NPOs eligible under 100C; entities in the **Thirteenth Schedule** | **Thirteenth Schedule**; plus FBR notifications under **100C(2)**. Also references a "**Sixth Schedule** approved institutions list" |
| Credit formula | `Credit = (A/B) × C` — a × (tax assessed/taxable income) × (lesser of donations or cap) | Credit = donor's **average tax rate** × eligible donation |
| Cap | **30%** taxable income for individuals/associations; **20%** for companies; associates 15%/10% | **30%** for both companies and individuals |
| Carry-forward of excess | Not mentioned (implied none) | "the excess is not generally available for carry forward" |
| Cash rule | **Cash donations qualify only if paid via crossed cheque through a bank** | Cash accepted but "weaker audit defence" |
| Property | Fair market value at time of donation counts | — |

🚩 **CONFLICT.** The two secondary sources disagree on the cap (20% vs 30% for companies) and on the schedule name. **Neither is a primary source.** Both are commercial/publisher sites. **The app must not print a percentage.**

**What I can defend:**
- It is a **tax credit**, not a plain deduction — it reduces the tax liability at roughly the donor's average rate.
- It applies **only to approved institutions** (Thirteenth Schedule and/or institutions approved/notified by FBR).
- The **FBR publishes the authoritative approved list**; the correct primary sources are `fbr.gov.pk` and `download1.fbr.gov.pk`.
- **Cash with a paper trail (crossed cheque / bank transfer) is materially safer than cash.**
- **Approval can lapse or be revoked**, so the donor is responsible for checking approval status **at the time of donation** — which is exactly a feature the app should build (see §6).

### 5.4 Receipts

**UNVERIFIED as a legal requirement.** Both secondary sources say a donor should retain an **original receipt showing donor name, amount, date, and the donee's approval reference**, plus payment evidence, for at least **six years** (FBR audit window). I found **no** primary FBR rule specifying mandatory receipt *content*.

**Design recommendation (safe):** have the app's ticket/receipt generator produce a receipt that records — donor name (or anonymous), date, item or amount, the **receiving organisation's registered name and its registration/NTN/PCP status as checked**, the **source URL and check date for that status**, and a clear line: **"This is a donor record produced by this app. It is not an FBR-approved tax receipt and confers no tax benefit. The receiving organisation must issue its own receipt."** That framing is honest and still useful.

---

## 6. Verification and trust — the highest-value thing this app can do

### 6.1 The problem is real and documented

| Evidence | Source |
|---|---|
| **Edhi Foundation's homepage runs a permanent scam alert** naming four fraudulent look-alike domains: `edhius.com`, `edhiusa.com`, `edhiusa.net`, `edhiusa.org` — "Donations made here will not reach those in need and may be misused." | `[fetched]` |
| **Punjab Home Department urged citizens to donate charity only to registered organizations**; and released a list of banned organisations and unregistered charity outfits | `[snippet]` (APP, English + Urdu) |
| **Punjab banned skin collection by banned outfits** and issued an Eid security plan | `[snippet]` (APP) |
| **SECP press release: "Beware of fraudulent financial activities"** (Urdu) | `[snippet]` |
| Insider fraud: reported Rs 80M case involving a former Al-Khidmat official | `[snippet]` — **single source, treat with caution**; it shows even large, certified trusts are not immune |
| Online donation scams / arrests | `[snippet]` (Dawn: "Six arrested for online scams") |

### 6.2 Where a prototype can get **real** verification signals

This is the actionable part — these are all public, fetchable sources:

1. **PCP NPO Directory** — `https://pcp.org.pk/npo-directory/` `[fetched]`
   - A public, filterable list of evaluated NPOs, each showing **"PCP Performance Evaluation Year(s)"** (e.g. "2023,2024,2025"), category, location and address. Also an INGO directory `pcp.org.pk/ingo-directory/`.
   - **This is the single best free verification signal in Pakistan.** A partner is "PCP-evaluated" if — and only if — it appears here, with the evaluation years shown.

2. **Sindh Charity Commission public charity search** — `mis.charitycommission.sindh.gov.pk/Public_Search_Charity.aspx` `[fetched]` (link on `charitycommission.sindh.gov.pk`)
   - Plus the Commission's **Proscribed Organizations** list `[fetched]` → use as a **negative** list.

3. **Punjab Charity Commission** registration portal + user guide — `charitycommission.punjab.gov.pk` `[snippet]`
4. **KP Charity Commission** — `charities.kp.gov.pk` `[snippet]`
5. **FBR approved-institutions list** — `fbr.gov.pk` `[snippet]` (authoritative for §5)
6. **Domain + name matching** — the Edhi case proves the attack is **typo-squatting on a charity's own name**. A cheap, high-value check: does the partner's domain correspond to the organisation's official name, and does the org's own site link back? Store the evidence.

### 6.3 How the directory should label partners

```
trust: {
  tier: "verified" | "partially-verified" | "unverified" | "proscribed",
  signals: [
    { type: "pcp_evaluation", years: [2023,2024,2025], url: "…", checked_on: "…" },
    { type: "provincial_charity_register", authority: "Sindh Charity Commission", url: "…" },
    { type: "official_domain", url: "…", name_matches: true },
    { type: "published_audit", url: "…" },
    { type: "fbr_exemption_order", url: "…" },
    { type: "negative_list_hit", authority: "…", url: "…" }
  ],
  checked_on: "YYYY-MM-DD",
  notes: ""
}
```

Rules that make this honest:
- **Never** render a bare green "Verified" badge. Render the **evidence chips** and the **date checked**.
- **"Unverified" must not mean "bad."** Many genuine small local organisations are not PCP-certified. Use "not yet independently verified" and show exactly what's missing.
- **Proscribed is a hard block**, and must cite the authority.
- **Expiry matters.** PCP evaluation years are listed per record — a 2019-only record is not a 2026 assurance. Show staleness.
- **Show your own gaps.** A "we could not verify this" note on a partner is a feature, not a bug. This briefing contains many such notes; the app should too.
- Edhi's scam alert belongs **in the product**, not just on Edhi's site: "Charity names get impersonated. Check the domain."

---

## 7. Accessibility and tech realities for Pakistani users

### 7.1 The numbers (all from DataReportal "Digital 2025: Pakistan" `[fetched]`, unless noted)

| Metric | Value (Jan 2025) |
|---|---|
| Population | **253 million** |
| Cellular mobile connections | **190 million** = **75.2%** of population |
| Internet users | **116 million** = **45.7%** penetration |
| People **offline** | **137 million** = **54.3%** |
| Social media user identities | **66.9 million** = **26.4%** |
| Mobile connections that are "broadband" (3G/4G/5G) | **74.0%** |
| Median **mobile** download speed | **20.89 Mbps** (+25.3% YoY) |
| Median **fixed** download speed | **15.53 Mbps** |
| Median age | **20.6** |
| Urban / rural | **38.6% / 61.4%** |
| Social media identities female / male | **29.6% / 70.4%** |

Platform ad reach: **TikTok 66.9M** adults 18+, **YouTube 55.9M**, **Facebook 49.4M**, **Instagram 18.8M** `[fetched]`.

**PBS Census 2023** gives total population **240,458,089** `[snippet]` (PBS Key Findings Report) — i.e. **~13 million lower than DataReportal's 253M projection.** ⚠️ **Pick one source per number and label it.** Mixing them produces nonsense.

### 7.2 The three conclusions the data forces

1. **Over half the country is offline (54.3%).** An internet-only donation app cannot reach most Pakistanis. If the app is to be *genuinely* useful rather than a demo, it needs a **phone-first, WhatsApp-first, SMS/USSD-capable** fallback for every action: "call this number", "WhatsApp this number", "here is the address to walk to."
2. **Rural is the majority (61.4%).** The directory must not be a Karachi/Lahore/Islamabad app. Distance and transport cost are the real constraints on in-kind donation — which is why **drop-off proximity** matters more than anything else in the UI.
3. **Female digital participation is far lower (29.6% of social identities).** Design and content choices that assume a male smartphone user will silently exclude women. Avoid gendered assumptions; consider woman-specific safe-contact pathways and women-run collection points.

**WhatsApp** is reported as the most-used social media platform in Pakistan per an IPOR report `[snippet]` — **single secondary source; treat as directional, not precise.** Combined with the offline figures, the design conclusion is robust regardless: **WhatsApp is the default channel.**

### 7.3 Urdu, RTL, and Roman Urdu

- **Noto Nastaliq Urdu** exists on Google Fonts (`fonts.google.com/noto/specimen/Noto+Nastaliq+Urdu`) and was announced on the Google Developers Blog "I can get another if I break it: Announcing Noto Nastaliq Urdu" `[snippet]`. Nastaliq is the culturally correct style for Urdu.
- ⚠️ **Nastaliq is heavy** — a full Nastaliq webfont is a large download on a metered connection and renders slowly on low-end Android. **Recommendation:** default to the device's system Urdu font (fast, zero bytes), and treat Nastaliq as progressive enhancement for headings only, or for users who opt in. On a 45.7%-internet, data-cost-sensitive market, a 500 KB font is a real cost.
- Set `dir="rtl"` and `lang="ur"` properly; don't fake RTL with CSS flips. Keep numerals and phone numbers LTR-isolated inside RTL text (a classic bug that mangles `+92-21-111-729-526`).
- **Roman Urdu** is the everyday written register for many users. Offer **Roman Urdu microcopy** ("Ghar se pickup", "Kitabain", "Kapray") alongside Urdu and English. I found **no** statistic quantifying Roman Urdu use — **UNVERIFIED**, but it is standard practice in Pakistani digital products.
- **Literacy:** PBS Census 2023 publishes literacy tables (Table 13(a) and 13(b), national and by sex/rural-urban) and a press release dated 30 July 2024 `[snippet]`. ⚠️ **I did not read the actual literacy percentage — do not invent one.** Read the PBS table directly before printing a figure.

### 7.4 Concrete UI implications

- **Payload discipline:** this is a single-page app. Budget it. Target a small initial payload, inline critical CSS, avoid shipping a large framework + icon + font bundle for a directory. Test on a throttled 3G profile, not on your laptop.
- **Offline:** service worker + cached partner directory is the highest-leverage feature for the 54.3% offline / intermittent-connectivity reality. A donor standing in a market with no signal should still see addresses and phone numbers.
- **Tap targets ≥ 48px; large body text; high contrast.** Cheap Android screens in bright sunlight.
- **Phone and WhatsApp as primary CTAs**, not contact forms. Use `tel:` and `https://wa.me/<number>` links. **Al-Khidmat already uses a `wa.me` link for donation slips** `[fetched]` — follow the ecosystem's own pattern.
- **Low-literacy support:** icon-led category cards (already present — good), and ideally short **Urdu audio** for the top tasks.
- **Data transparency:** show the user what the page weighs. In a market where 54.3% are offline and data is a real cost, "this page is 90 KB" is a trust feature.
- **Android-first.** I could not verify a precise Android market-share figure in this session — **UNVERIFIED** — but the cheap-device, Android-dominant assumption is safe for prioritisation, and the offline/lite design is correct either way.

---

## 8. Data sources a prototype can legitimately use

| Source | What it gives | Status |
|---|---|---|
| **NDMA** — `https://www.ndma.gov.pk` | National disaster situation reports (SITREPs); publications at versioned paths (e.g. `ndma.gov.pk/storage/publications/…`) | ✅ Real; `[snippet]`/`[PDF-blocked]` — NDMA sitreps are PDFs |
| **ReliefWeb** — `https://reliefweb.int/country/pak` | Mirrors NDMA/OCHA sitreps as readable HTML summaries. **This is the practical way to consume NDMA data as a developer**, because the HTML page carries the figures inline (as demonstrated in §2.4) | ✅ `[fetched]` |
| **PDMA (provincial)** | Punjab / Sindh / KP / Balochistan disaster-management authority reports | ⚠️ Referenced but **not verified** in this session |
| **OCHA HDX** — `https://data.humdata.org` | Humanitarian datasets; listed as an OCHA service in ReliefWeb's footer | ✅ `[fetched]` (as a link) |
| **Pakistan Bureau of Statistics** — `https://www.pbs.gov.pk` | **2023 Population & Housing Census** — national/provincial reports, Key Findings Report, Table 13(a)/(b) literacy, press releases | ✅ Real; `[snippet]`/`[PDF-blocked]` (PBS is mostly PDF) |
| **opendata.com.pk** | A Pakistan open-data portal holding government datasets (e.g. PASSCO / Punjab Food Department series) | ⚠️ **Exists** `[snippet]`, but I could **not** verify its operator, licence, or freshness. **Check the licence before reuse.** |
| **data.gov.pk** | Pakistan's official open-data portal | ❓ **UNVERIFIED — I did not confirm this exists or what it holds.** Do not cite it without checking. |
| **OpenStreetMap / Overpass API** — `https://dev.overpass-api.de/overpass-doc/` | Query OSM POIs for donation points, clinics, welfare centres | ✅ Overpass docs are real `[snippet]`. OSM coverage in Pakistan is **uneven** — good in major cities, sparse rurally — so treat OSM as a **supplement to your curated list**, and verify each result against the organisation itself |
| **Google Maps deep links** — `https://developers.google.com/maps/architecture/maps-url` and `https://developers.google.com/maps/documentation/urls/get-started` | Keyless URL scheme for search/directions | ✅ Real docs `[snippet]` (I did not open them). The pragmatic choice: `https://www.google.com/maps/search/?api=1&query=<lat>,<lng>` and `https://www.google.com/maps/dir/?api=1&destination=<lat>,<lng>` require **no API key and no billing** — which matters enormously for a student prototype. Also generate `geo:` URIs so offline map apps can handle it. |

**Recommendation on mapping:** use **Google Maps deep links as the primary navigation affordance** (zero cost, zero key, works on every Android device already), store **lat/lng plus the OSM node ID** so links work offline and so the data is portable, and offer an OSM/offline fallback. Do not embed the Google Maps JS SDK — it inflates payload, needs a key, and fails on the metered connections described in §7.

---

## 9. Comparable apps and platforms to learn from

### 9.1 Pakistan

| Platform | What it is | Takeaway |
|---|---|---|
| **Rizq** — `https://rizq.org` `[fetched]` | A full welfare ecosystem: Rizq Ration, Rizq Dastarkhwan, Rizq Khana, **Rizq Bachao** (surplus-food rescue), Kissan Dost, GroRizq, Rizq Breeds, Housing Innovation Lab, Youth Republic, plus Ramadan/Qurbani/Muharram/Arba'in campaigns and published financial reports & audits | The most sophisticated Pakistani giving brand. **Food-focused, cash-driven; I found no consumer app and no in-kind goods intake.** Its "Bachao" (rescue) framing is a good vocabulary for the app's "rescue, don't discard" messaging |
| **Chhipa app** — `chhipa.org` android/iPhone links + QR code `[fetched]` | Single-charity donation app | Shows single-charity apps exist and are the norm |
| **Al-Khidmat app** — Google Play + App Store links `[fetched]` | Single-charity donation app | Same |
| **Transparent Hands** — `transparenthands.org`, `transparenthands.co.uk` `[snippet]` | Crowdfunding for free medical/surgical care; Qurbani campaigns | The **case-based giving** model — donors fund a specific patient/procedure. Strong transparency pattern to borrow |
| **OLX × Edhi Foundation — "Sellfare se Welfare"** (Ramadan campaign) `[snippet]` | Market-place/charity partnership channelling second-hand sales into welfare | Direct precedent for the **free-cycle** instinct inside a classifieds platform. Useful precedent for a "resell to donate" flow |
| **SOS / TCF / SKMCH / Akhuwat donation pages** `[snippet]` | Single-cause cash/Zakat/sponsorship | The competitive baseline the app must not duplicate |

**⭐ The gap:** I found **no** cross-charity, in-kind-first donation directory for Pakistan. Every major player is either (a) a single charity with its own app, or (b) cash/Zakat-only. The prototype's actual differentiation is the **directory + condition guidance + routing + verification-evidence** layer — not another donation form.

### 9.2 South Asia and beyond

| Platform | What it is | Takeaway |
|---|---|---|
| **Goonj (India)** — `https://goonj.org` `[fetched]` | The best in-kind logistics model in the region: Sharing Camps, Dropping Centres, institutional drive forms, material guidelines, **send-via-delivery-app**, Centre of Circularity, Cloth for Work, School to School, Not Just A Piece of Cloth, Rahat | **Copy the structure.** Especially: give goods a *destination programme*, not a warehouse |
| **ShareTheMeal (WFP)** — `wfpusa.org/get-involved/sharethemeal/`, `wfpusa.org/news/sharethemeal-app-fights-hunger-in-one-tap/` `[snippet]` | "Fight hunger in just one tap" | The benchmark for **friction-free micro-giving**. The prototype's basket → ticket flow should feel this short |
| **Give2Asia, GiveIndia, Ketto, Milaap, Daan Utsav** | Cross-border and crowdfunding giving platforms | ⚠️ I did **not** verify these in this session. **Do not cite specifics.** Treat as comparison leads only |
| **Facebook free-cycle / "Buy Nothing" groups, OLX** | Informal second-hand redistribution | ⚠️ I did **not** verify specific Pakistani groups. Acknowledged as a real behaviour, but **no evidence collected** |

### 9.3 What this means for positioning

The prototype should **not** try to be "Rizq but with more categories." It should be:

> **The trust and logistics layer for in-kind giving in Pakistan:** which organisations actually accept which goods, in what condition, where to take them or whether they'll collect, and what evidence exists that the organisation is real — with a donor record the user can keep.

That is a defensible, verifiable, locally-correct product, and every section above feeds it.

---

## 10. Prioritised recommendations

**Fix immediately (correctness bugs)**
1. Change Chhipa's helpline from **1121 → 1020**. Add Rescue 1122, Aman 1101, Police 15, Fire 16, Al-Khidmat 0800 44448.
2. Add `source_url` + `verified_on` to **every** helpline, address, and accepted-item claim.
3. Remove or clearly mark any accepted-items claim you have not verified — starting with the implication that all ~34 sites take clothes/books/toys/food.

**Build next (highest value per unit effort)**
4. **Evidence-based trust panel** per partner, sourced from the **PCP NPO Directory**, provincial charity commissions (Sindh/Punjab/KP), published audit reports, and FBR exemption orders. Show chips + check date. Never a bare "Verified" badge.
5. **Refuse to collect money.** Deep-link to each charity's own verified rails. Cite SBP BPRD Circular Letter 04/2012's ban on personal accounts for donations in your own "why we don't take your money" copy — it is a *trust* feature.
6. **Condition guidance with an explicit hard-reject list**, labelled as prototype guidance, with the medicines exception routed correctly (Alamgir/Saylani, not a blanket ban).
7. **Offline-capable directory** + `tel:` and `wa.me` CTAs as primary actions.
8. **Google Maps deep links** (keyless) + stored lat/lng for offline and OSM fallback.

**Do later (differentiators nobody has)**
9. **Hijri-aware seasonal mode**: Ramadan (Fitrana/Fidya/Kaffara/Sehri-Iftari/ration), Dhul Hijjah/Qurbani, **chamra routing to large registered collectors with salting-and-speed guidance**, Muharram, winter drives.
10. **Ration bag as a bill of materials**, not a rupee amount.
11. **Emergency appeal mode that requires a linked, dated situation report** (NDMA via ReliefWeb HTML).
12. **Honest homepage** that states its own coverage gaps and verification limitations — the opposite of the over-claiming that characterises this space.

---

## 11. What I could NOT verify (read this before shipping anything)

**People and phone numbers**
- Any helpline for JDC, Rahma, Akhuwat, Indus, SKMCH, Sundas, TCF, Zindagi Trust, Dar-ul-Sukun, Sweet Homes, SOS, NOWPDP, Rizq, Robin Hood Army, Khana Ghar.
- Whether **Chhipa's "You Call We Collect"** actually collects **goods** (not just money).
- Whether **Khana Ghar** has any official website or published number — I only saw a third-party fundraiser.

**Claims and figures**
- **PBS literacy rate** — I confirmed the census tables exist but did **not** read the percentage. Do not print one.
- **2022 flood** casualty/displacement figures — no primary source fetched.
- **Android market share** in Pakistan; **WhatsApp** as "most used" (single secondary source).
- **Stripe availability** to Pakistani merchants.
- **Roman Urdu** usage statistics.
- Whether **1BILL** can be used to collect donations, or what a charity must do to become a biller.
- **Easypaisa/JazzCash** merchant onboarding requirements for a non-profit.

**Law (⚠️ not legal advice — a Pakistani lawyer must confirm all of this)**
- The text of the **Societies Registration Act 1860** and the **Trust Act 1882** — I did not fetch either statute. Cited on reputation only.
- **Balochistan**'s charities regime — only an indirect PDF reference found.
- Whether a **federal** charity regulator exists or is proposed (e.g. a national Charity Commission) — **not verified**.
- **EAD / foreign-funding** requirements at detail level (PDFs unreadable).
- Current **2024/2025/2026 status** of the FBR exemption clauses — I read **secondary** commentary (HZ & Co, KPMG, Yousuf Adil, Crowe) via search snippets, not the Ordinance text. **Clause (61) withdrawal in 2021** comes from a KPMG PDF read only as a snippet.

**Documentation I could not read**
- Every **PDF**: PCP's Section 61 and Section 100C papers, SECP's Section 42 guidebook, the Punjab Charities Act 2018 (FAOLEX), Balochistan charities regulation, Goonj's material guidelines, PBS census tables, NDMA sitreps, the RSIL AML/CFT Toolkit. My fetch tool rejects `application/pdf` — **a follow-up pass should download and read these directly.** PCP's `Section-61-1-min.pdf` and `Sectio-100-C-1-min.pdf` in particular are likely the authoritative one-page summaries the app needs.

---

## Sources

All links below are URLs I actually opened in this session, unless marked otherwise.

**Charities — primary pages fetched**
- [Edhi Foundation](https://www.edhi.org) — homepage, scam alert, Emergency Call 115
- [Edhi Foundation — Charitable Shop](https://www.edhi.org/charitable-shop)
- [Edhi Foundation — All Pakistani Edhi Centers](https://www.edhi.org/all-pakistani-edhi-centers)
- [Chhipa Welfare Association — You Call We Collect](https://www.chhipa.org/how-to-donate/you-call-we-collect/) — helpline 1020
- [Chhipa Welfare Association — Donate Via Courier](https://www.chhipa.org/how-to-donate/donate-via-courier/) — UAN and published donation rates
- [Saylani Welfare — Medical Equipment](https://saylaniwelfare.com/services/health/medical-equipment) — accepts donated used medical equipment
- [Al-Khidmat Foundation — Qurbani](https://alkhidmat.org/donations/islamic-giving/qurbani) — 0800 44448, doorstep cheque collection, FBR 2(36)(c) claim
- [Alamgir Welfare Trust International — Used Medicine Department](https://alamgirwelfaretrust.com.pk/used-medicine-department/) — in-kind catalogue and published exemption orders
- [Alamgir Welfare Trust International — Malboosat](https://alamgirwelfaretrust.com.pk/malboosat/)
- [Rizq](https://rizq.org) — programmes and campaigns

**Government and regulator — primary pages fetched**
- [Commissioner Karachi — Emergency Services](https://commissionerkarachi.gos.pk/emergency-services) — Edhi 115, Chhipa 1020, Aman 1101, Rescue 1122, Police 15, Fire 16
- [State Bank of Pakistan — BPRD Circular Letter No. 04 of 2012](https://www.sbp.org.pk/circulars/bprd-circular-letter-no-04-of-2012) — NGO/NPO account rules; personal accounts banned for donations
- [State Bank of Pakistan — Raast](https://www.sbp.org.pk/raast)
- [State Bank of Pakistan — Payments Ecosystem and Infrastructure](https://www.sbp.org.pk/our-operations/payments-ecosystem-and-infrastructure)
- [Sindh Charity Commission](https://charitycommission.sindh.gov.pk/) — Sindh Charities Act 2019, public charity search, proscribed organisations
- [Pakistan Centre for Philanthropy — NPO Certification](https://pcp.org.pk/npo-certification-2/) — FBR-designated certification agency, section 2(36)
- [Pakistan Centre for Philanthropy — NPO Directory](https://pcp.org.pk/npo-directory/)
- [Pakistan Centre for Philanthropy](https://pcp.org.pk/)

**Data and statistics — primary pages fetched**
- [DataReportal — Digital 2025: Pakistan](https://datareportal.com/reports/digital-2025-pakistan)
- [ReliefWeb — Pakistan Monsoon Floods 2025 Operation Update #3 (MDRPK028)](https://reliefweb.int/report/pakistan/pakistan-monsoon-floods-2025-operation-update-3-mdrpk028) — NDMA/OCHA figures
- [ReliefWeb — Pakistan country page](https://reliefweb.int/country/pak)
- [Arab News Pakistan — Pakistan expected to collect record 7.5 million animal hides](https://www.arabnews.pk/pakistan/pakistan-expected-to-collect-record-75-million-animal-hides-this-year-after-eid-al-adha-data-2645616) — PTA chamra data, Al-Khidmat hide volumes, spoilage

**Tax and legal commentary — pages fetched (secondary sources; treat with caution)**
- [PkRevenue — How much tax credit does FBR allow on charitable donations in 2026?](https://pkrevenue.com/how-much-tax-credit-does-fbr-allow-on-charitable-donations-in-2026/)
- [LexForm — Pakistan Section 100C Tax Credit on Charitable Donations 2025-26](https://lex-form.com/blog/pakistan-tax-credit-charitable-donations-section-100c-2026.html)

**Comparable platforms — pages fetched**
- [Goonj — Sharing Camps](https://goonj.org/donate/sharing-camps)
- [Goonj — Material](https://goonj.org/material/) (rendered empty to my fetch)

**Sources seen only in search results / not opened (leads to verify)**
- [Punjab Home Department urges citizens to donate charity only to registered organizations (APP)](https://www.app.com.pk/domestic/punjab-home-department-urges-citizens-to-donate-charity-only-to-registered-organizations/)
- [Punjab bans skin collection by banned outfits, issues security plan for Eid (APP)](https://www.app.com.pk/domestic/punjab-bans-skin-collection-by-banned-outfits-issues-security-plan-for-eid/)
- [SECP — Section 42 Guidebook (English and Urdu)](https://www.secp.gov.pk/document/section-42-guidebook-english-and-urdu/)
- [SECP — Guide: Section 42 procedure](https://secp.gov.pk/wp-content/uploads/2016/04/Guide-Section-42.pdf)
- [Voluntary Social Welfare Agencies (Registration and Control) Ordinance, 1961 — Pakistan Code](https://www.pakistancode.gov.pk/english/UY2FqaJw2-apaUY2Fqa-cJ2b-con-6241-sg-jjjjjjjjjjjjj)
- [EAD — NGO registration FAQs](https://ngo.ead.gov.pk/faqs)
- [Punjab Charity Commission registration portal user guide](https://www.charitycommission.punjab.gov.pk/system/files?file=Charity_Registration_Portal_User_Guide_v1.0_01072020.pdf)
- [KP Charity Commission — Urdu user guide](https://charities.kp.gov.pk/system/files/User_Guide_KPK_Charity_Commission_(Urdu)_07.08.2020.pdf)
- [Punjab Charities Act 2018 (Act V of 2018) — FAOLEX](https://faolex.fao.org/docs/pdf/pak225112.pdf)
- [Pakistan Bureau of Statistics — Release of National and Provincial Census Reports, 2023](https://www.pbs.gov.pk/release-of-national-and-provincial-census-reports-of-population-and-housing-census-2023-2/)
- [Pakistan Bureau of Statistics — Census 2023 Key Findings Report](https://www.pbs.gov.pk/sites/default/files/population/2023/Key_Findings_Report.pdf)
- [Pakistan Bureau of Statistics — Table 13(b) literacy](https://www.pbs.gov.pk/sites/default/files/population/2023/tables/table_13b_national.pdf)
- [NDMA — publications](https://www.ndma.gov.pk/storage/publications/November2025/FweqUWhEX19cob8DvM4L.pdf)
- [PCP — Section 61 summary](https://pcp.org.pk/wp-content/uploads/2022/03/Section-61-1-min.pdf)
- [PCP — Section 100C summary](https://pcp.org.pk/wp-content/uploads/2022/03/Sectio-100-C-1-min.pdf)
- [KPMG — A Brief on Tax Laws (Second Amendment) Ordinance 2021](https://assets.kpmg.com/content/dam/kpmg/pk/pdf/2021/03/A-Brief-on-Tax-Laws(Second-Amendment)-Ordinance-2021.pdf) — clause (61) exemption withdrawn
- [Yousuf Adil — Budget 2025-26 Highlights & Comments](https://yousufadil.com/wp-content/uploads/2025/06/Budget-2025-26-Highlights-Comments.pdf) — section 100C tax credit
- [HZ & Co — Comments on Finance Act 2025](https://www.hzco.com.pk/publications/publications-pdf/Comments-on-Finance-Act-2025.pdf) — clause (66), section 100C
- [ICMAP — 2(36)(C) Application for Approval as Non-Profit Organization](https://www.icmap.com.pk/downloads/CorporateDocuments/ExemptionCertificate_2(36)(c)_(01-07-2019%20to%2031-12-2019).pdf)
- [Google Fonts — Noto Nastaliq Urdu](https://fonts.google.com/noto/specimen/Noto+Nastaliq+Urdu/about)
- [Google Developers Blog — Announcing Noto Nastaliq Urdu](https://developers.googleblog.com/en/i-can-get-another-if-i-break-it-announcing-noto-nastaliq-urdu/)
- [Google Maps Platform — Maps URLs reference](https://developers.google.com/maps/architecture/maps-url)
- [Google Maps Platform — Maps URLs get started](https://developers.google.com/maps/documentation/urls/get-started)
- [Overpass API documentation](https://dev.overpass-api.de/overpass-doc/)
- [opendata.com.pk — PASSCO / Punjab Food Department dataset](https://opendata.com.pk/dataset/f805d202-015a-4702-bfdd-d580514c4393)
- [Goonj — Guidelines for accepting material (PDF)](https://goonj.org/wp-content/uploads/2020/06/Guidelines-for-accpeting-material-during-Covid.pdf)
- [OLX & Edhi Foundation join hands for 'Sellfare se Welfare' Ramadan campaign](https://tradechronicle.com/olx-edhi-foundation-join-hands-for-sellfare-se-welfare-ramadan-welfare-campaign/)
- [Indus Hospital — C.A.S. School in-kind flood relief donation](https://indushospital.org.pk/impact/newsroom/the-c-a-s-school-flood-relief/)
- [Indus Hospital — HUBCO donates dialysis machine](https://indushospital.org.pk/impact/newsroom/hubco-dialysis-machine/)
- [Dar-ul-Sukun — Medicines for the Marginalized](https://darulsukun.com/donate-medical-supplies/) (fetch blocked by recaptcha redirect)
- [Dar-ul-Sukun — Donate a Diaper](https://darulsukun.com/donate-a-diaper/)
- [SOS Children's Villages Pakistan — Donations](https://www.sos.org.pk/Donations)
- [Sundas Foundation — Donate Blood](https://sundas.org/donate-blood)
- [NOWPDP — Donate Now](https://nowpdp.org.pk/donate-now)
- [Akhuwat Foundation — Donate](https://akhuwatfoundation.com.pk/donate-to-akhuwat-foundation/)
- [TCF — Zakat](https://www.tcf.org.pk/zakat/)
- [Shaukat Khanum — Donations all countries](https://shaukatkhanum.org.pk/donations-all-countries/)
- [Zindagi Trust — Donate](https://zindagitrust.org/donate)
- [Alamgir Welfare Trust — helpline/site](https://alamgirwelfaretrust.com.pk/)
- [1LINK](https://1link.net.pk)
- [Easypaisa — Merchant QR Terms and Conditions](https://easypaisa.com.pk/public-information/downloads/Terms-and-Conditions-Merchnat-QR-PR-18226.pdf)
- [ShareTheMeal — World Food Program USA](https://wfpusa.org/get-involved/sharethemeal/)
- [Transparent Hands](https://transparenthands.co.uk/)
- [IPOR report: WhatsApp becomes most used social media in Pakistan (GTV News)](https://gtvnewshd.com/tech/2025/09/01/whatsapp-becomes-most-used-social-media-in-pakistan-ipor-report/)

⚠️ **No legal, tax, or regulatory statement in this briefing should be relied upon without confirmation from a qualified Pakistani lawyer or tax practitioner, and from FBR / SBP / the relevant provincial charity commission directly.**
