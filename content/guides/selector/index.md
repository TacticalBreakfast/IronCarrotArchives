+++
title = 'Paid 6★ Selector Recommendations'
date = 2026-10-10T16:25:00-04:00
draft = false
summary = "Recommendations for the paid 6★ Standard and Kernel selectors: tiered picks, blurbs on the top units, and what to check before you spend."
tags = ['Arknights', 'Guide', 'Selector']
# Position in the homepage "Other Guides and Content" list (Blog is 3, Tier List is 5).
# Must stay above [params]: in TOML, keys below a [table] header belong to that table.
weight = 4
# Header image at the top of the page. The image is featured.png (or .jpg) in this
# folder — the same file is used for social previews (Twitter/Bluesky/Discord) and,
# center-cropped, the homepage card. Recommended: 1200x630, subject centred.
showHero = true
# "big" shows the whole image at its own shape; the default "basic" crops it into a short strip.
heroStyle = "big"
[params]
  author = 'TacticalBreakfast'
  topic = 'Other Content'
showDate = false
showAuthor = false

# Menu entry lives here (not in config/_default/menus.en.toml) so it only exists
# while this page is published — a draft page gets no dead link in the menu.
[menus.main]
  name = 'Paid 6★ Selector Guide'
  parent = 'Other Content'
  weight = 22

# ============================================================================
#  POOL OVERRIDES  —  the Kernel/Standard fix for THIS PAGE ONLY
# ============================================================================
#  Every tile on this page decides "Kernel or not" from data/operator_pools.yaml,
#  the same file the Mastery tables use.
#
#  Use this when the EN Kernel pool update lands AFTER the current selector went
#  on sale: update operator_pools.yaml as normal (so the Mastery pages are right),
#  then list the moved units here with their OLD pool, because the selector
#  being sold still uses the old pools. One entry fixes every tile for that unit
#  on this page (tiers, Gold shop list, free selector list).
#
#  Values: "kernel" or "standard". Names follow the same rules as the tiles
#  (in-game name; accents and apostrophes optional). A typo or bad value shows
#  up as a warning when the site builds.
#
#  REMOVE the entries once the selector on sale matches operator_pools.yaml again.
#
#  Example, for the March 2026 CN update if it reaches EN mid-selector:
#    "Lee" = "standard"
#    "Goldenglow" = "standard"
[poolOverrides]
+++

## Introduction

Hello, and welcome to TacticalBreakfast's 6★ Selector Recommendations.

First and foremost, please READ this article in its entirety if you actually want to make a smart choice. This article is not meant to directly be used as a tier list. In fact, many choices I've made here are for maintainability, rather than exact recommendations (see the next sections for why). While I do understand if you don't want to read several thousand words just to pick an EX or S-tier unit, don't come complaining to me if you miss some important nuance and regret your choice!

That out of the way, here's some background on the article, although it's not strictly required to read the next few paragraphs if you don't care about the why. Essentially, I used to regularly do a selector guide for every limited event, but it ended up being a huge amount of work. With life being how it is, I just couldn't afford to, what was effectively, rewriting it entirely every six months. Yet it was a popular article that a lot of people found useful, and I've wanted to bring it back. So, I recently came into a little bit of time to readdress things, but rather than just repeat the same untenable mistakes, I've opted to start over with an eye towards maintainability. Some of this is behind the scenes work, and some of it is just formatting, but some of it is also changing how the information is presented here.

For you, the reader, the most obvious things though will be the tiers and blurbs. The tiers are still coded by letter, for clarity of order, but now have explicit definitions of what belongs in them. I've also reduced the total number of tiers. This makes it easier for me to group units in a way that makes sense, without fussing about the minor differences between mostly comparable units. For the blurbs, there's simply less of them. Not every Operator is worth discussion! There's no reason now to really fuss my way through blurbs for bad old units like Pallas, or even moderate middle-ground units like Penance!

So the hope is that I can regularly maintain this going forward! Fingers crossed anyway. Let's get into it.

## Selector Basics & Rules

1) The 6★ selectors are generally available twice a year, in roughly April and October on the global servers. They release along with the Celebration Limited events which occur at those times.

2) There are two selectors available, a Standard one and a Kernel one. You can buy both if you wish, but the standard is generally more valuable. This is discussed at more length below.

3) The selectors cost 30 USD each.

4) The Standard selectors go up to the banner before the previous Celebration Limited. So for example, the selector that came during SilverAsh the Reignfrost's event went up to and includes Mon3tr since Mon3tr was the unit released just before Exusiai the New Covenant's event, which was the prior Celebration Limited event before SilverAsh. That can be a bit confusing, so a summary is provided here.

{{< selector-timeline >}}
Last Selector | Released April 14th, 2026 | Mon3tr
Current Selector | Releases October 14th, 2026, along with the Kal2/Closure patch | Mantra
Next Selector | Expected April 2027, along with the (currently unannounced) patch | Zima the Raging Tide
{{< /selector-timeline >}}

{{< last-updated "2026-10-10" "month" >}}

5) Limited, Collaboration, and Welfare operators are not selectable. Only Standard and Kernel gacha units are.

6) The Kernel pool updates once a year, which affects which units are on which selector. While this is pretty consistent on CN, it is much less consistent on global. It is usually near the end of the year, but may or may not occur before the limited event. Please be aware of this fact, and double check the ACTUAL unit list in the store. I will do my best to update this article as the information becomes available, which is summarized here.

{{< selector-status >}}
Last CN Kernel pool update | March 26th, 2026
EN date | October 9th, 2026
Does the list reflect this yet? | Yes
Will it be in effect for the fall selectors? | Yes
{{< /selector-status >}}

Units moving into the Kernel pool with this update:

{{< selector-tier size="compact" >}}
Lee
Goldenglow
Fiammetta
Horn
Irene
Ebenholz
Dorothy
{{< /selector-tier >}}

This is now confirmed on official channels, but still, if the unit you want is on this list, please verify in game which selector they are on before purchasing! 

{{< last-updated "2026-10-08" "month" >}}

## How to Use this Guide

Before we begin, this guide is purely about meta power. I mention this because the general power level of the game is extremely high right now. If you're regularly rolling on new banners, you don't absolutely have to make an optimal choice (Ray bnnuy EX-tier)! Please, feel free to pick someone because you think they're neat. It's the best way to play the game! However, a list like this can't account for personal preferences, so from now on, the discussion is strictly meta focused.

As a general flow, start with the EX-tier. Units in the EX-tier are EX for a reason, and if you don't have them, it makes the choice clear.

After that, look towards the S-tier, but give an eye towards your team and playstyle preferences. For two examples, Leizi the Thunderbringer is a bad choice if you hate micromanaging skill activations. Ines is probably suboptimal if you already have Closure and SA2. Every unit in this tier has a blurb, so they can be helpful to make your choice. However, double check the “Free Selectors” and “Gold Certificate Shop” sections first.

After that, things get more nuanced and you have a lot more flexibility to consider your selection. The tier definitions below S will hopefully guide you towards the section most relevant to you. Again, double check the “Free Selectors” and “Gold Certificate Shop” sections first, but especially for these lower tiers! Although not an absolute truth, the older a unit gets, the generally lower on the list they appear, and older units are far more likely to appear on free selectors or in the gold shop.

Not every unit at these lower tiers will have a blurb, but many will (marked by a blue speech bubble thing), so check below. You can also find additional write-ups in the Mastery sections of this website, although do keep in mind some blurbs for older units may be slightly out of date. The guide has recently got a complete update, but still, it's a big guide and the game meta is moving fast right now.

### Things to Know About the Guide

- Rather than try to maintain separate lists for standard and kernel units, they are presented here in the same list. This is done to help with maintainability (see the next point). Kernel units are given a blue label to indicate their pool for the selector.

- This article is designed with maintainability first. Labels within the list such as free selectors and gold shop are automated. They *should* be accurate, but may not be updated in real time. You should absolutely read the relevant sections rather than picking blindly, and please please please double check before making your pick.

- These labels show "Gold shop" or "Free selector" and may or may not have a "?" after them. The question mark indicates an uncertainty, such as an unverified selector or an unpredictable appearance. You can click on the labels to jump to the relevant sections. For example, second gold shop appearances show as "Gold shop?" because second appearances are highly unpredictable.

- Please note that treating this list as a strict tier list is not advised. The absolute best pick will heavily depend on your team and playstyle. For example, Ines and Ulpianus are both ranked in the top tier. However, if you already have SilverAsh the Reignfrost, Ulpianus is probably the better selection. For another example, if you're just starting out, you probably shouldn't pick Mon3tr despite her high rating. 

- There is no special ordering within the tiers. Generally, I just group them by class for readability.

- Some units may appear twice when there is a notable difference in their consideration between two categories. This most commonly happens with the IS ops. For example, Typhon is a moderate IS pick and also a moderate general pick, and is worth acknowledging in both sections. However, not all IS ops will have two entries. This is mostly to avoid confusion since the general ranking is probably irrelevant (i.e. bottom tier).

- The blue speech bubble icon in the upper right corner indicates the unit has a blurb associated with them. If you click on their icon, it will jump to the blurb. Units without this will default jump to their Mastery blurbs. That will probably be helpful, but do keep in mind the Mastery guide is huge and older write-ups may be out of date. Check the "last updated" section on the Mastery blurbs if you're unsure.

- If in doubt about your choice, I suggest asking in the [Reddit Help Thread](https://www.reddit.com/r/arknights/) (pinned at the top). Be sure to include your roster when asking!

### Standard vs Kernel

There are two types of selectors, a Standard and a Kernel, each corresponding to their respective pools. You can purchase both, so technically you can select two 6★s, if you’re willing to pay. However, the Standard selector tends to be far more valuable. In most cases, if you only buy one, it should be the Standard since newer units will almost always be more powerful. In turn, that also means the Kernel is less valuable. However, there are still good units available on the Kernel selector, especially if you play lots of IS. So it's not unreasonable to buy both if you want to stretch your wallet, but I wouldn't recommend it for the average player.

There are basically three reasons to buy the Kernel selector. First, someone you really personally want is on it. Second, you play a lot of IS and are willing to make that the overriding priority at the cost of general value. Or third, the money means nothing to you. These points all come from the fundamental idea that the Kernel banner just isn't as good in the non-IS portion of the game. They're older units, and with extremely few exceptions, they've all been pretty severely powercrept now. There can be value, but unless you fall into one of the former groups, you're probably best off saving some money and sticking with just the Standard selector.

As mentioned, the major exception here is if you play a lot of IS. Many Kernel units now have a mode specific IS Module, some of which are very powerful. The top Standard units are still more valuable (they're just as good in IS but also better in the general game), but for those that heavily favor IS, or have already strong base rosters of modern units, the Kernel selector may sometimes be the better choice.

Finally, and this is discussed above, but the pools do change with time. Typically, they update once a year in the fall and this often has an impact on the fall selector, however, Yostar is not especially predictable with this. You can find the details above, and I'll do my best to update this list as soon as we know for sure. However, if the unit you're after is on the cusp of the pools, please please please double check the unit list in the actual store before buying!

### Impact of the Gold Certificate Shop

The Gold Certificate Shop is an important consideration, but is also one of the hardest things to account for in this guide. There's no reason to spend $30 of your hard earned money if a unit can be bought for free! However, the shop is also extremely difficult to predict and you may not have enough certificates either! I will try to give some rules of thumb here, but the problem is even these aren't set in stone.

The most predictable appearances are a unit's first appearance. These happen roughly in order, roughly every 2-3 rotations, and roughly two years after their initial release. This list is provided below, and if your target is early on it, you should probably wait as this will be the most “reliable” choice here. Order is not strictly guaranteed, but generally it does go in release order, so expect units later on the list to take more time to appear. If a unit is later on the list, you could potentially be waiting a while.

A unit's second appearance is also relatively predictable, although it is MUCH less reliable. For example, Lin was skipped over for several months before finally appearing. For another, Hoederer skipped ahead of two units for his second appearance. Even when it does happen, the timing is much less precise. I probably wouldn't rely on this, but it could be a deciding factor if you're on the fence between two units.

The Kernel pool is the LEAST predictable. There are some vague correlations, but these are much looser than the Standard pool. It's hard to say anything definitively, so if your target is a Kernel unit, there's probably no good reason to wait.

#### Likely First Appearances in the Next Six Months

{{< alert >}}Operators near the end of this list are likely to take much longer to appear!{{< /alert >}}
{{< alert >}}This list may not be updated in real time. If you are waiting for someone, please ensure they have not already appeared.{{< /alert >}}

{{< selector-tier size="compact" flag="Gold shop" order-labels="Likely to be sooner. | Likely to be later!" >}}
Zuo Le
Ascalon
Logos
Ulpianus
Nymph
Narantuya
{{< /selector-tier >}}

{{< last-updated "2026-10-08" >}}

#### Possible Second Appearances in the Next Six Months

{{< alert >}}Likely to be unreliable!{{< /alert >}}
{{< alert >}}This list may not be updated in real time. If you are waiting for someone, please ensure they have not already appeared.{{< /alert >}}

{{< selector-tier size="compact" flag="Gold shop?" >}}
Typhon
Swire the Elegant Wit
Jessica the Liberated
Hoederer | In shop on Oct 9
{{< /selector-tier >}}

{{< last-updated "2026-10-08" >}}

#### Kernel Locating Banners

In addition to the above, there are frequently Kernel Locating banners which allow you to select who appears in the Gold shop, from a subset of options. These are often difficult to account for, since like the base pool, they are unpredictable. However, sometimes a Locating banner runs when the selector launches.

{{< selector-status >}}
Is a Locating banner known? | Yes
Date of banner | October 20th, 2026
{{< /selector-status >}}

{{< selector-tier size="compact" flag="Gold shop" >}}
Goldenglow
Dorothy
Kal'tsit
Archetto
Blemishine
Gnosis
Surtr
Weedy
Eyjafjalla
Rosa
SilverAsh
Passenger
{{< /selector-tier >}}

{{< last-updated "2026-10-11" >}}

### Impact of Free Selectors

Hypergryph is fairly benevolent as far as gacha overlords go. There tends to be free 6★ selectors that are given out over the course of the year, usually with the very same limited events this paid selector is for sale during. Of course, the most powerful units are rarely, if ever available on them. They're mostly a smattering of older units, but still have some quality options on them, and this may have an influence on your pick.

There's a few things to know.

1) It's not guaranteed that the units on the selector will remain the same between CN and Global. They usually stay the same, and it will generally be a pretty safe assumption, but it's not guaranteed in the case a unit is a “must have” for you.

2) The selector may not come with the same event on Global. For example, HG often gives a selector with the CN Anniversary event, but Yostar often likes to delay this selector to the EN Anniversary event, which is a different event between the servers. This is not universally true though, and we won't know in advance either.

3) Related to the last two points, the paid selector has a long expiration. So you can often wait to make your decision if the free selector gets delayed.

**Upcoming selectors**

**Episode 17 - Critical Phase Transition** {{< badge >}}Confirmed{{< /badge >}}

{{< selector-tier size="compact" flag="Free selector" >}}
Saileach
Surtr
Mudrock
Pozëmka
Passenger
Reed the Flame Shadow
Suzuran
Mizuki
{{< /selector-tier >}}

This selector is confirmed. It was released October 8th and contains the same operators as CN.

**Till the Lands Become an Orange** · Expected mid-January {{< badge >}}Unconfirmed{{< /badge >}}

{{< selector-tier size="compact" flag="Free selector?" >}}
Bagpipe
Mountain
Fiammetta
Nightingale
{{< /selector-tier >}}

### Impact of "Random 1 of 3" Selectors

Occasionally, there is a different type of selector pack for sale. These packs cost $26 and grant a random one of three pre-selected units. For example, during Episode 17 there is a pack that has Nymph, Lemuen, and Jessica the Liberated on it, and you will get one of those three at random if you buy it. These are generally a bad deal and should be avoided. They are only $4 less than the regular selector, which will guarantee your option, and one of the three is usually a sub-optimal pick. You shouldn't buy them, so they have no impact on the selection.

The only scenarios where you should consider these over the selector are if you would be truly happy with any of the three, or you are simply a huge whale. Saving $4 is not worth the gamble!

## The List

PLEASE READ THE GOLD CERTIFICATE AND FREE SELECTOR SECTIONS ABOVE! Labels are automated, and mistakes are possible. Don't blame me if you don't read!

### EX

This tier is the “no questions asked” tier. If you don't own a unit in this tier, they should be your selection, regardless of your roster. The only reason not to take a unit here is personal considerations. Yes, there is currently only one OP here. That could change in the future, but as of right now, if you don't have Tragodia, select Tragodia. Simple as that.

{{< selector-tier >}}
Tragodia
{{< /selector-tier >}}

### S (meta units)

This tier is the “best” picks, but aren't so stand-out that you should ignore team considerations. There's no order provided here since the exact best will depend on you and your team. Everyone here is really powerful, so it's hard to make a bad choice. Since these are the most powerful options, all of them will have blurbs below to help you decide.

{{< selector-tier >}}
Ines
Mlynar
Ulpianus
Leizi the Thunderbringer
Ray
Narantuya
Lemuen
Logos
Mantra
Mon3tr
Haruka
Ascalon
{{< /selector-tier >}}

### S- (IS)

This tier is a “special” tier for considering the strongest IS Modules. With how the power levels have gone with the game, these units tend to *only* be great in IS. Generally, favor the regular S units first (which is why this section is labeled S-), even if IS is your favorite game mode since you'll get more value there. If you don't like IS at all, skip this category entirely.

{{< selector-tier >}}
Gnosis
Mizuki
{{< /selector-tier >}}

### A (general use)

This tier is for generally great units, but who are a step below the S-tier. The picks here are solid, but not essential, and if you fancy endgame or IS play, you may want to look at a different tier for some stronger situational value. For most in this tier, there's someone higher ranked that does the same job better, although there are some exceptions.

{{< selector-tier >}}
Hoederer
Degenbrecher
Zuo Le
Surtr
Saria
Reed the Flame Shadow
Kal'tsit
Suzuran
{{< /selector-tier >}}

### A (IS)

As with the “S- (but IS) tier”, this is for the IS modules, but the units here aren't quite as absurdly good as the S-tier. These lean more towards specific strategies, iterations, or playstyles.

{{< selector-tier >}}
Irene
Archetto
Angelina
{{< /selector-tier >}}

### A (endgame)

This tier is for units who have some specific and semi-frequent endgame use. They tend to be less generally valuable than the “A (general use)” units, but since the S-tier units will cover most general uses already, it may still make more sense to pick from this list instead, depending on your playstyle and goals. A brief note here is given for their value. Being in this tier does not mean the unit has no general value, however. Instead, it means their situational value is the overriding consideration. There aren't all that many people in this tier anymore. This is a consequence of the recent powercreep, which has tended to devalue "specific" solutions.

{{< selector-tier >}}
Hoederer | Various stall applications
Nightingale | Arts damage counter
{{< /selector-tier >}}

### B (passable general units)

These are units who are usable, if you want, and have just enough going for them to avoid the “bad” tiers. However, they tend to be underpowered compared to another unit in the same class/role above. Given how many units are already in the upper-tiers, you should probably not be picking from here, but it may have some value if you want to better justify a waifu pick.

{{< selector-tier >}}
Executor the Ex Foedere
Qiubai
Viviana
Vina Victoria
Entelechia
Horn
Jessica the Liberated
Typhon
Pozemka
Eyjafjalla
Goldenglow
Nymph | Stall
Necrass
Thorns the Lodestar
{{< /selector-tier >}}

### B (minor endgame value)

This tier is for units who do have some notable endgame value, but have become fairly fringe over the years. As in the higher tiers, the units here have less general value than the other B-tiers, but again, the general roles are easily filled by higher tiers so this fringe value may still be something to consider.

{{< selector-tier >}}
Bagpipe | SP Talent
SilverAsh | Gnosis IS comps
Qiubai | Stall comps in IS
Skadi | AH teams
Blaze the Igniting Spark | Burn damage comps, some invuln strats
Lin | Invulnerability
Ifrit | RES-shred
{{< /selector-tier >}}

### B (IS)

These are units with an IS Module that are still decently usable, but are generally inferior in almost all cases to some other choice in the same class. They're definitely better than the bottom tier units here, and can be a fun alternative for heavy IS users, but are generally a suboptimal selection.

{{< selector-tier >}}
Typhon
Phantom
Swire the Elegant Wit
{{< /selector-tier >}}

### C (fringe endgame or niche value)

These are units who are generally pretty bad, but still manage to have some fringe value in either endgame or niche play. You really shouldn't be picking from this tier unless you know what you're doing, but there is some value still.

{{< selector-tier >}}
Vulpisfoglia | IS#7 only
Saileach | CC DP generation
Eunectes | RA
Passenger | RA
Fiammetta | Base skill
Mostima | Stall
Ceobe | DEF-scaling DPS, but ST
Ho'olheyak | IS#6 only
Stainless
Magallan | Some CC stall
Weedy | Shift/stall
{{< /selector-tier >}}

### Don't Pick Tier

These units are not worth picking. They're underpowered compared to the upper-tiers and don't have the situational value to otherwise consider. The only reason to pick here is waifu-purposes. Of course, not every unit here is the same level of bad, but at this point, it's no longer worth making the distinction between them since few people will find themselves this far down.

{{< selector-tier >}}
Siege
Saga
Flametail
Ch'en
Mountain
Thorns
Blaze
Pallas
Exusiai
Hoshiguma
Blemishine
Penance
Mudrock
Schwarz
Rosa
Fartooth
Carnelian
Ebenholz
Shining
Lee
Dorothy
Aak
Hellagur
{{< /selector-tier >}}

## Blurbs

Not every operator will be discussed here. This guide is not meant to be a general guide to every 6★ in the game and it makes maintenance a huge pain! Instead, this section is for a few specific notes I have on certain ops that may factor into your decision.

### Top Unit Blurbs

Since these units are the best of the best, they'll get a little extra attention to help with your choice.

{{< selector-blurb title="Tragodia" units="Tragodia" >}}
Tragodia is easily the best unit in the standard gacha pool, and one of the best units period. It's honestly shocking he's not a limited unit. He's the easy pick if you don't have him. His control is the best in the game, while also doing a ton of damage. The only reason not to take him is personal preference because in terms of meta evaluation, he's head and shoulders above any other option. Even the fact he'll get a full rerun soon doesn't change this fact, because those pulls are better saved for all the limited banners!
{{< /selector-blurb >}}

{{< selector-blurb title="Ines" units="Ines" >}}
Even if you have both SilverAsh2 and Closure, Ines is still an extremely powerful unit. Endgame accounts will have all three. However, for newer accounts with less depth, it may be worth looking elsewhere in the top-tiers if you already have one or both of those other two Vanguards. Especially with Closure being available this patch on a strong limited banner most people will be rolling for anyway, Ines is a somewhat weaker pick for an S-tier unit this time around.
{{< /selector-blurb >}}

{{< selector-blurb title="Mlynar" units="Mlynar" >}}
Mlynar is remarkable in his durability. He's the oldest non-IS unit in the S-tier and by a pretty large margin. He does big damage against multiple targets in a wide area. Simple, but very effective. Then to top it off he has global conditionless taunt which is a valuable solution to a lot of annoying problems. Despite his age, Mlynar is still one of the top dogs- (err, top horses?) in the game. However, if IS is your focus, he can actually be one of the weaker units in the S-tier, since he really needs E2 to function. In that case, look towards Leizi2 instead, or wait for Ch'en3 next selector.
{{< /selector-blurb >}}

{{< selector-blurb title="Ulpianus" units="Ulpianus" >}}
Ulpianus brings a lot of value in one package and is my favorite among the three Guard picks in the S-tier. He has great bulk, massive range, a fast cycle, and a great AFK skill. He's everything you'd want out of a laneholder because he's a powerful DPS unit first! And that's even before you pair him with the other AHs, especially Gladiia. Of the S-tier units, he's the most all in one, but has a huge amount of ceiling too.
{{< /selector-blurb >}}

{{< selector-blurb title="Leizi the Thunderbringer" units="Leizi the Thunderbringer" >}}
Leizi2 is a fantastic unit and one of the best Guards currently available. However, among the S-tier units, she requires the most thinking and button pushing to use since S1 is her best skill. That won't appeal to some people, so it's something to be aware of. If you're looking for a simpler Guard, go with Ulpianus or Mlynar, the former of which is probably more valuable too.
{{< /selector-blurb >}}

{{< selector-blurb title="Ray, Narantuya, and Lemuen" units="Ray | Narantuya | Lemuen" >}}
The three Snipers are a bit awkward on this list, because they're somewhat interchangeable. Of course, they all do different things and have different strengths, but those differences are more muted compared to the rest in this tier. Ray excels in ST killing, Lemuen trades some of that ST ceiling for general value, and Narantuya is the most flexible of the three. If a Sniper is your target, you can't go wrong with any of them. That said, I favor Narantuya slightly.
{{< /selector-blurb >}}

{{< selector-blurb title="Logos" units="Logos" >}}
Logos is the best general purpose Caster on the ticket (at least until Pram2 joins the options). He simply does a ton of damage and shrugs off a lot of RES! However, it's worth acknowledging that if you're after a Caster and prefer ceiling to general value, Mantra might surprisingly be the better pick, especially if you already have Pram2. However, there’s two flaws with taking Logos. One, he’s somewhat low ceiling these days compared to the rest of the S-tier (crazy to say), and two, Pram2 will be available on the next selector, who is a much better general Caster pick if you can wait.
{{< /selector-blurb >}}

{{< selector-blurb title="Mantra" units="Mantra" >}}
Mantra is a bit of an odd unit. Taken on her own, she's still decent, but suffers from many of the same flaws as other Primal Casters. However, unlike the others, the NI Ritualist is one of the best units in the game. Piggy-backing off of Tragodia means that Mantra might be the highest ceiling Caster right now! However, that's a value that definitely won't be for everyone, or even necessarily a lot of people, so be a little cautious before picking her. She’s strong, even without Tragodia, but does require planning and thought to use effectively.
{{< /selector-blurb >}}

{{< selector-blurb title="Mon3tr" units="Mon3tr" >}}
This may come as a surprise, but I hesitate to recommend Mon3tr and she's probably the lowest priority in the S-tier to me. Her healing is great, as is her buffing and flexibility to S3, but this patch includes Kal2 who is the better Medic. I already wasn't especially high on Mon3tr since her S3 can be tricky to use since she isn’t a reliable blocker, but this patch especially, it doesn't make a lot of sense to pick her over the other S-tier options, in my opinion since her returning Mom (Kal2) does many of the same things, but better. However, as a general power consideration, she still deserves to be ranked here.
{{< /selector-blurb >}}

{{< selector-blurb title="Haruka" units="Haruka" >}}
Similar to Mon3tr, Haruka looks like a less appealing selection during the same patch as Kal2. However, Haruka is a much better healer than either. Her effective HPS and uptime is absurd and she surprisingly becomes one of the more effective “carry” options available on the ticket, despite doing almost no damage herself. She's just very effective at keeping people alive, with minimal effort.
{{< /selector-blurb >}}

{{< selector-blurb title="Ascalon" units="Ascalon" >}}
Ascalon is a bit more “subtle” than the other S-tier units. Her DPS isn't as absurd as the others nor is her control as good as Tragodia's. However, she combines both together very well, along with some great survivability and hit-count utility (a mechanic HG seems to be especially fond of). The fact a 4★ in the same archetype is so great, and the fact Mizuki is much better in IS, does hurt her value, but Ascalon is so effective in so many places that she's definitely worth considering.
{{< /selector-blurb >}}

{{< selector-blurb title="Mizuki (IS)" units="Mizuki" >}}
Mizuki is very weak in the general game, but has a crazy good IS Module. He has incredible bulk with it and some absurd fast-cycling control that fully locks down many stages on his own. While most IS Modules tend to favor specific iterations or team comps, Mizuki's is perhaps the most generally valuable. If you like IS, he's a great pick and will be even better than Ascalon there. Just be aware that you do give up a lot of general game value another pick would bring, like Ascalon.
{{< /selector-blurb >}}

{{< selector-blurb title="Gnosis (IS)" units="Gnosis" >}}
Gnosis' IS value is extremely strong, and he has a higher ceiling than Mizuki thanks to his strong damage and control, but he tends to be tied to other units. If you don't have Pram2 and SA2, he looks much less appealing. Those are obtainable later, but you may want to start with someone like Angelina or Mizuki instead.
{{< /selector-blurb >}}

### Other Blurbs

Please note that not all units are given blurbs. If they don’t have one, odds are there’s probably nothing too special about them in the modern meta that warrants consideration.

{{< selector-blurb title="Saria" units="Saria" >}}
If you have Shu or Hoshiguma the Breacher, Saria looks quite a bit less compelling (Shu especially). However, both of those are limited units and Saria is still fantastic. She may be worth a look if you lack those, and even still has some good value if you do have them! In addition to all the normal benefits of a Guardian, her Arts amp on her S3 has proven to be surprisingly valuable, albeit quite situational.
{{< /selector-blurb >}}

{{< selector-blurb title="Skadi" units="Skadi" >}}
Abyssal Hunter teams are a popular niche, and Skadi is one of them. So if that's something that appeals to you, definitely consider her. It's not like there's a lot of choices! However, it's worth keeping in mind that Skadi1 is one of the least valuable members of the niche as well. Most of the power is in Ulpianus and Gladiia, with the rest being situational or just warm bodies due to a lack of options. If the AH niche only sort of interests you, don't start with Skadi, and you may not even need her at all.
{{< /selector-blurb >}}

{{< selector-blurb title="Goldenglow" units="Goldenglow" >}}
Goldenglow is one of only two 6★s with true global range, and her competitor, Lappland the Decadenza, just does it better which knocks GGs value down quite a bit. However, global damage is great and Lapp2 is a limited, so if you don't have Lapp2, GG can look more appealing. Lapp2 also shares her spark with some ridiculously powerful units that you should be taking first, so obtaining her isn't straight forward either. Don't overreact if you don't have Lappland2 though! While Goldenglow does look more appealing in her absence, the general increase in power ceiling means that most of the S and A-tier units are still better picks.
{{< /selector-blurb >}}

{{< selector-blurb title="Thorns" units="Thorns" >}}
Thorns has been perpetually popular for reasons that no experienced player really understands. He's a thorn (lel) in our side we can't get rid of. If you're a newer player here and are wandering in, maybe from some older videos where he was “the” laneholder, don't be fooled. The power ceiling has exploded in recent years and left Thorns far behind.
{{< /selector-blurb >}}

{{< selector-blurb title="Other Older Laneholders (Mudrock / Penance / Mountain)" units="Mudrock | Penance | Mountain" >}}
While Thorns gets some special hate here, the situation is a little less bleak for the other laneholders, although they’re still probably not good picks. Laneholding just isn’t a key role these days with how strong the DPS is, and modern iterations, like Executor2 and Entelechia will do good DPS in addition to the laneholding. Still, these three do have some value if you *really* want a classic laneholder. Penance is an incredible reflect tank, Mudrock has her negation shields, and Mountain is super cheap with strong bulk. None of them have much ceiling, or they’d be ranked higher though.
{{< /selector-blurb >}}

{{< selector-blurb title="Nymph" units="Nymph" >}}
While she's still ranked pretty decent thanks to her S2, it's worth a quick explanation why her Necrosis damage is not brought up. Simply put, NI (Tragodia and Mantra) is better and they don't stack. Nymph's S3 has almost no value in the current meta-game, so it shouldn't really factor into your decision. It's still fine if you like her and Virtuosa personally of course, but this is a meta discussion so don't get mad at me about it!
{{< /selector-blurb >}}

{{< selector-blurb title="Saileach" units="Saileach" >}}
Saileach frequently appears in CC content, but be cautious with her if you don't know what you're doing. Agents and Strategists dominate the general meta, and Myrtle does 99% of the remaining Standard Bearer job for a quarter of the price. People tend to overvalue the CC aspect, and Saileach doesn't even appear in every CC, so approach her with extreme caution. Even if you want to attempt higher risks, you may want to consider borrowing her from supports instead since she often needs max potential to be viable in these situations!
{{< /selector-blurb >}}

{{< selector-blurb title="Hoshiguma" units="Hoshiguma" >}}
Most major roles are represented somewhere in the upper-tiers, but one notable absence is bulk defenders. The reason is that the role can be easily found elsewhere. There are a number of powerful do-it-all Defenders available, but even lacking them, Cuora and Bubble will do almost all of the job for a much lower price. Even Nian is available for a low spark cost, plus a decent Welfare option, so there isn't a lot of reason to spend your ticket on a bulk blocker of any kind.
{{< /selector-blurb >}}

{{< selector-blurb title="Eunectes and Passenger (RA)" units="Eunectes | Passenger" >}}
The RA modules don't have anywhere near the value of the IS Modules. RA just doesn't have the replayability, and the mode is perfectly beatable without them. RA3 doesn't change matters either (sadly). So for most people, these aren't worth considering since they're pretty bad units in the general game. Still, the RA effects are strong, so if you're one of the rare few RA-lovers (I'm one of them, there are dozens of us!) they could be worth a look.
{{< /selector-blurb >}}

{{< selector-blurb title="Phantom (non-IS)" units="Phantom" >}}
In some older versions of this selector guide, I suggested Phantom as a potential alternative FRD since the two other 6★ FRDs are both limited units and the welfare was pretty bad. However, this advice is now dated. Texas the Omertosa will soon have reduced spark cost and Kirin R Yato will (or has) gotten a rerun. Even Crownslayer is now viable thanks to her second mod. Further, the general power spike has meant even if you lack the limited ones, a low-powered unit like Phantom just isn't necessary. Thus, Phantom is currently an IS-only consideration.
{{< /selector-blurb >}}

{{< selector-blurb title="Ho'olheyak" units="Ho'olheyak" >}}
Just a quick note here because Ho'olheyak managed to be the only IS-Module holder to not get ranked in the IS tiers. This is not a mistake. Sadly, her IS Module is just extremely undertuned and promotes bad play that could just be avoided by picking a better caster like Logos. However, it does have some value in IS#6, so if that's your favorite iteration for some reason (god why), it may be worth a look.
{{< /selector-blurb >}}

{{< selector-blurb title="Kal'tsit" units="Kal'tsit" >}}
Kal1 is another IS-Module holder with only one rank, but unlike Ho'olheyak, it's for the opposite reason. Kal's IS Module is actually pretty good, but her general unit value is better. The IS stuff is just a bonus, so it doesn't really factor in here. In fact, the S-tier IS mods are better for IS specifically.
{{< /selector-blurb >}}

{{< selector-blurb title="Nightingale" units="Nightingale" >}}
Nightingale is an old classic, but one who has persistently stuck around. She mitigates Arts Damage so well that it's been hard to really implement any other solutions. It makes her one of the last remaining units who still has strong endgame specific value since no one else can really do it. However, she is weak as a general Medic, even being worse than several 5★s, and the general spike in power levels has also made what she does less essential too. While in the past some stages felt unbeatable without her, now they can be mostly brute forced. Still, she has enough value to be a legitimate consideration.
{{< /selector-blurb >}}

{{< selector-blurb title="Blaze the Igniting Spark" units="Blaze the Igniting Spark" >}}
In certain advanced comps, Blaze2 is one of the best DPS options due to how much raw Elemental damage she can deal out. However, there's three giant warning signs to be aware of before treading down this path. First, it's an advanced thing. In most content, more general DPS is superior. Second, Tragodia and Mantra (both on this ticket) are superior in a lot more advanced cases (just not for raw damage), and the two elemental types don't stack. Third, owning Yu, a limited, is an absolute requirement to make her work at full potential. However, she also has an immortality gimmick that has proven occasionally useful, so she has more going for her than a lot of lower tier units. Just be cautious before picking her, and make sure you know what you're getting into.  
{{< /selector-blurb >}}

{{< selector-blurb title="SilverAsh" units="SilverAsh" >}}
I may have the original SilverAsh ranked a bit too highly here, however if you like using Gnosis comps in IS, he can actually be very potent. With Gnosis and his S1, he can often perma-freeze in a large area which makes him surprisingly viable. And while his general value is a bit dated, it's still reasonable. So SA1 can be a viable pick here, albeit relatively specific compared to other units this high up.
{{< /selector-blurb >}}

{{< selector-blurb title="Qiubai" units="Qiubai" >}}
In addition to being a decent (but not amazing) DPS unit, Qiubai actually has some unique value in IS thanks to her S1. Bind immunity is relatively rare, and she only requires some modest ASPD or SP relics to permanently Bind, which makes her a unique solution to some tough bosses.
{{< /selector-blurb >}}

{{< selector-blurb title="Hoederer" units="Hoederer" >}}
Hoederer is a slightly weird unit. Crushers in general can be awkward to use in places, and while Hoederer lacks Ulpianus' raw power, his skills can be used in various places for some pretty crazy survivability. For example, in IS with ASPD, his S1 can get insane. Or his S2 can reliably interrupt certain enemies for another example. This makes him both decent as a general unit, with some endgame applications, but one who doesn't excel as much as the higher tiers either.
{{< /selector-blurb >}}

{{< selector-blurb title="Non-S-tier IS" >}}
Making recommendations here is really tricky. Their value changes wildly depending on the iteration and may even change with updates and patches. There's a lot of playstyle considerations as well. Some people love Archetto comps, some people hate them (me)! If you're considering someone from the A-tier or lower, I definitely suggest doing your homework first.
{{< /selector-blurb >}}

{{< selector-blurb title="Other IS or RA" >}}
This isn't relevant to this guide, but I know a few people will be curious where the ISW/RA Modules on non-selectable units would fall relative to these rankings. Rosmontis's IS would place her in the A-tier with Angelina. Dusk's IS module would be not recommended (it's even worse than Ho'olheyak's). Pepe's RA Module would join Eune/Passenger, but maybe higher if such a tier existed.
{{< /selector-blurb >}}
