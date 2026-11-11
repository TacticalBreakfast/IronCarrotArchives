+++
title = "TacticalBreakfast's Sanity Value Guide"
date = 2026-11-11T00:00:00-05:00
draft = false
summary = "How to read the Arknights sanity value pages: what shop pack values and E2/M3 promotion costs measure, how they're calculated, and which packs to buy first."
tags = ['Arknights', 'Guide', 'Efficiency']
excludeFromRSS = true
# Must stay above [params]: in TOML, keys below a [table] header belong to that table.
# First of the efficiency pages (Promotion & Mastery Costs is 6). Shares 5 with the
# Tier List; ties sort newest first, so this one comes before it.
weight = 5
# Header image: featured.jpg in this folder (1200x628), also the social preview
# and the homepage card. "big" shows the whole image rather than a cropped strip.
showHero = true
heroStyle = "big"
# Semi-hidden feedback release: published at its URL, but left out of search,
# the sitemap and tag pages. For the wide release, delete this [build] block,
# restore `topic` below, and uncomment the menu entry at the bottom.
[build]
  list = 'never'
[params]
  author = 'TacticalBreakfast'
  # topic = 'Other Content'   # restore for the wide release: lists the page on the homepage
showDate = false
showAuthor = false

# Menu entry for the wide release. It lives here (not in menus.en.toml) so a
# draft page leaves no dead link. Parent and weight still to be decided.
# [menus.main]
#   name = 'Intro - README'
#   parent = '…'
#   weight = …
+++

## Introduction - What is this?

Hello, and welcome to TacticalBreakfast's Efficiency Pages, formerly Sheets. These are an evolution of my old Google Sheets version, and it contains basically the same information, but is now cleaner, more expansive, and more importantly (for me) automated. This started as a personal project for me, where I just wanted to find a good skill to use an M3 ticket on, but like everything I do, it blew up. I first thought to just share the basics, and now I'm here with a full efficiency suite. Woops. Hopefully you find them useful.

There are two major aspects to this guide. The first is paid money pack values, which attempts to determine the value of the various packs compared to simply buying the raw Originite Prime packs. The second is calculating the sanity values of E2 and Mastery promotions, for the purposes of finding the best value for the various promotion tickets. This is related to the first item, since most of these tickets are paid, although we do occasionally get some for free which should make this list valuable to non-spenders as well.

These two aspects are broken down into five pages.

Intro & README - This page. Please read this if you want to make optimal choices. It will explain how to use the various sections as well as make some recommendations. If you don't read it, and make a bad choice, don't come crying to me about it.

[Recent Promotion & Mastery Costs](/guides/recent-promotion-costs/) - This page covers the total cost of promotions from the last 10-ish patches on CN. For us global players, this will cover most things recent and upcoming. This is a more streamlined version of the full table, and is intended to help you make efficient use of paid E2 or M3 tickets. Specifically, it highlights the most expensive options. Yellow indicates it is an above average cost. Red indicates it is in the top 25%. Both are averaged over only the recent units of the same rarity, rather than the historical average. However, please be aware that this table does not make skill suggestions. Just because a skill is expensive does not mean it's good. For that, you can follow the links to their relevant Mastery or lookahead write-ups in the main guide, if available.

[Overall Promotion & Mastery Costs](/guides/promotion-costs/) - This page is similar to the Recent Promotion & Mastery Costs, but covers everyone. It's slightly expanded to include Modules, and doesn't highlight expensive versions. This one is more "informational" and should be useful to newer players who are raising units beyond just the latest and greatest. You can also adjust if you want to devalue certain infinite materials or not, in cases where you haven't reached that milestone in your career yet (although keep in mind new units use much less of infinite materials, if any).

[Promotion & Mastery Statistics](/guides/promotion-stats/) - This isn't a guide, but rather is just a collection of fun statistics related to the promotions that I found interesting. It's completely skippable if you're only here for the actual guide stuff.

[Paid Pack Values](/guides/shop-packs/) - This section is different from the promotion pages, and instead focuses on which packs are an efficient use of your money. The intention is to help you make better choices, and accounts for if you are only focused on pulls or also on sanity.

### Changes from the Sheets Version

* Promotion costs now include all costs. The Sheets version only accounted for variable costs and ignored E1. This made the calculations a lot easier. Although this was less accurate, the important point was the relative values (i.e. which skills were the most expensive). However, with this web version, I no longer have to worry as much about the complexity of the formula, so a more accurate version can be displayed. The only costs that aren't included now are SL1-7, which aren't a part of Mastery or E2, Module upgrade materials (Data Supplement Sticks and Data Supplement Instruments), which have no value, and ISW/RA/SO Modules, which have the same value across all units.

* These changes in calculations mean the displayed value is higher than it was in the Sheets. However, nothing has changed in the recommendations. It's just a more accurate value.

* What has had a material change though, is including the E1 material values. This has improved the efficiency of the E2 packs slightly compared to the old sheet.

* Modules are now included as well. This isn't relevant to any efficiency calculations, but it's something many people may find interesting and was now easy to add.

* Due to a quirk in how Sheets handles the AVERAGEIFS formula, the old value on the Sheet was actually incorrect. The values here are corrected.

* The definitions of the red and yellow values in the promotion costs have been improved to be more accurate. There shouldn't be a practical difference in advice though. The green, yellow, and red thresholds in the paid packs functionally remain the same, but are now more accurate behind the scenes (only affected one pack).

* The pack efficiencies now include all upcoming CN packs, and should update automatically. This means less waiting on me to update, as well as more accurate lookaheads. The same rules still apply though, such as excluding cosmetics, kernel rolls, furniture parts, and Module upgrade parts.

* Most content in all pages is automated, meaning you shouldn't have to wait for me to update it now. Most Operator promotion values will be available shortly after it's available in the game data. Most CN packs should update monthly.

* Because of this, I've removed the Revisions section. Most revisions now should be invisible to you.

## Feedback or Questions?

If you have any feedback or questions related to these pages, or any of my other content, the best place is to [join our community Discord](https://discord.gg/JqU3PV3uMw). It's shared among several other smaller fan sites, so swing by #ica-general. If you prefer, the [Feedback Reddit thread](https://www.reddit.com/user/TacticalBreakfast/comments/1pl4nne/a_mastery_priority_guide_feedback_comments_corner/) remains open as well.

## Paid Money Packs

* !!!READ THIS!!!: Before you buy any of the limited time packs listed on this value guide, there are some permanent / recurring packs that you should always prioritize first, especially if you're a light spender. Check the [analysis section below](#pack-buy-order). If you don't, you're wasting your money with suboptimal purchases that this page won't necessarily show directly. If you're interested in efficiency, you should be planning ahead!

How to use the page:
* There are two key columns here, "$/OP Tot Value" and "$/Pull Only".

* Use "$/OP Tot Value" ONLY if you would buy an OP pack to refresh sanity. The calculation is done assuming 1 OP = 135 sanity. If you aren't the type of person to refresh sanity, the packs are far less valuable. Further, most credible sanity calculations devalue XP since it is efficient to produce it in the base, and most players have no need to farm it. This guide treats XP with its full value, again assuming you are willing to spend OP to actually farm XP. This is not a guide for the casual player!

* Use "$/Pull Only" if you are NOT willing to spend OP to refresh sanity. This column is for people who are only interested in gacha rolls. That isn't to say the materials are valueless though. In this case, it's impossible to find a "true" value for the materials since your valuation would be highly dependent on your own preferences, so your personal valuation would be somewhere in the middle.

* In short, use "$/OP Tot Value" if you would spend OP on sanity. Use "$/Pull Only" if you are only interested in pulls. If you're the type of player who is primarily interested in rolls and doesn't refresh sanity, but still find the sanity items to be of value, then your value will be somewhere between these and you'll have to make a judgement call based on your circumstances.

* Note that the two major columns technically measure different things. "$/OP Tot Value" is the price per Originite Prime when the total value of the pack is tallied. It includes the sanity value of materials AND pulls, converted into an equivalent amount of OP. "$/Pull Only" is the price per PULL, while ignoring the sanity value of the materials. Notice the difference between $/OP and $/Pull. So even though the Monthly HH Pack (no material value) shows different values in each column, they say the same thing. This is done to make the relevant comparison in each use case easier.

* The columns have three colors associated with them. The purpose of this guide is to compare the pack values to just buying the OP packs, and that's what the color shows. Green means the pack is better than the DOUBLE OP packs (one time purchases, but refresh annually), meaning you should look at these packs before buying any OP. Yellow means the pack is better than OP packs WITHOUT the double, but are worse than WITH the double, meaning you should only look towards these if you've already used your doubles. Red means they're WORSE than any OP pack, and should generally be avoided.

* The two cheapest OP packs ($1 and $5) are excluded from the suggestions threshold. Because these packs have less OP in them, the numbers are skewed, and aren't useful anyway, which would unnecessarily throw off the thresholds. The other packs do have a slight variation in value, but not enough to affect anything. You can see these values on the Pack Values guide, under Raw Originite Prime.

* Cosmetic elements (like name cards, icons, and UIs) are not given any value in these pages. There really isn't an equivalent sanity value to use with them.

* Module upgrade parts (tier2 and tier3) are given no value since they cannot be farmed with sanity. Module Blocks are valued normally since they can be farmed. However, do be aware that there is a limited number of blocks per month. Because of this, the Module Block packs may actually be more valuable than the raw numbers indicate since it bypasses a time limiting factor.

* Kernel pulls are excluded from all calculations. You shouldn't be pulling on kernel banners, so don't add anything meaningful to overall efficiency. However, if you are desperate for someone in the kernel pool, the dedicated kernel pull packs are usually just as efficient as standard ones. Note however that the Kernel Selector is still valuable, although less valuable than the Standard Selector.

* E2 and M3 tickets are calculated using the lifetime averages, but with low outliers excluded (bottom 25%). This is to account for the fact many older skills that use a lot of items available in the infinite shop are now much cheaper overall which would drag the average down, but not be relevant to most players since new units aren't as impacted.

* If you use the tickets on high value targets (see the Promotion Values section), the efficiency of these will be even higher.

* This page now shows upcoming packs that were available on CN. Although rare, it's possible for names, prices, contents, and date availability to all change before they reach EN. Any upcoming pack should be treated as tentative.

## Promotion Value Pages

* The "Recent Promotion & Mastery Costs" page is a list of just the recent and upcoming operators, since these are the units most people are interested in. It also gives a better value baseline since older OPs tend to have lower values due to the devaluing of certain older items as they get added to the infinite event shops.

* If you are interested in other units, they are all listed in the larger "Overall Promotion & Mastery Costs" page. Use Ctrl-F to find what you're looking for.

* Values are calculated using the MSVs from the CN website yituliu. However, some values I override for more accurate calculations since the goal of these pages differs from sites like yituliu.

* Please be sure to check the footnotes under the charts before blindly throwing your tickets at the biggest number! Don't blame me if you spend it on a bad skill because you didn't do your homework. You can find my Mastery suggestions here: [https://ironcarrotarchives.com/](/)

* By default, the list devalues any material that has been added to the infinite event shops on CN. These are noted at the top of the page. However, not everyone will have an excess of these materials. In this case, there is a toggle near the top of the page which will let you change the "era" that is devalued.

## Analysis and Advice

### Pack Buy Order

* Before buying any pack in the Paid Pack Value page, you should first purchase the Monthly Card, Starter Pack, Starter Monthly Pack, and Starter Headhunting Pack. Additionally, purchase the Starter Special Training Pack if you are interested in sanity refreshes. Do not purchase the Starter Upgrade Pack or Starter Furniture Pack.

* After those, the $30 6★ paid selectors which come in during the April and October limited events (on EN) are the best value (assuming there's someone left of value you don't have yet). Those should be your next purchase targets, after the monthly card and starter packs, but before anything else in the Paid Pack Values page. You can find my [selector guide here](/guides/selector/) to help your decision.

* However, note the "random 1 of 3" packs that come on occasion are way worse. I basically never suggest buying those unless you would be happy with any of the three. They're only $4 cheaper than the selector, so almost never worth the risk. The only scenario it makes sense to get them are if you'd be happy with any of the three. If even one is a dud, either as a duplicate or as someone you don't want or need, they aren't worth it.

* Finally, the Monthly Headhunting pack is usually similarly efficient for rolls as pull-oriented event packs, and definitely more efficient than non-pull oriented event packs, so consider regularly buying that if pulls matter to you.

* After all that, it's time to start looking at other options, which is where the Paid Pack Values page comes into play.

* If it's not clear from looking at the chart, most recurring permanent material packs are bad value. You shouldn't buy them. The only value in buying them compared to buying OP to use to farm is in time savings.

* That said, the chip packs save a lot of annoyance since the drops are 50/50. Plus they're cheap. Even I buy those on occasion.

* It's a bit boring and sort of defeats the purpose of the guide, but the bottom line / conclusion from this is HG/Yostar is pretty smart about their pack values. Most material focused limited time packs are efficient. Most pull focused limited time packs come out roughly the same as the Monthly HH pack. They're remarkably consistent.

### Promotion Analysis

What follows is mostly just some random thoughts I've seen while digging through the data. You may or may not find these helpful, but I thought I'd include them anyway.

* If you're short on materials, the M3 ticket is by far the best value. It's actually sort of incredible how good it is on a cost per OP, especially if you use them smartly. If you used all 3 tickets on the most expensive skills (which isn't advisable) it drops all the way down to 20 cents per OP compared to 38.5 cents in the double $100 pack!

* For the 4★ M3 ticket, there isn't a huge amount of variance. The difference from the cheapest to most expensive is about three days of sanity, and most hover around 1000. The more expensive ones are also fairly biased towards the newer units. I personally tend to save these.

* Related, for the paid pack that includes an M3 ticket for all rarities, it is still efficient if you exclude the 4★ ticket, so don't worry too much if you wouldn't make good use of that one.

* Similarly, the pack value remains efficient if you don't use the 5★ ticket. However, if you don't use BOTH the 4★ and 5★ ticket, and only use the 6★ ticket, it becomes worse than the double OP packs. There is a big difference in value if you would only use the 6★ ticket, and you should probably avoid them in that case, although it is still better than the OP packs without the bonus.

* If you have a lot of materials and are only interested in XP/LMD (to maximize value for max leveling, which is expensive) the E2 ticket packs may still be a good purchase, but not by much. For the 6★ E2 ticket pack, it's worse than the double OP packs, but better than the single OP packs. For the 5★s, it's *slightly* better than the double OP packs. In most cases, you'll probably just want to refresh OP on CE-6/LS-6. This question is actually why I started making this in the first place!
