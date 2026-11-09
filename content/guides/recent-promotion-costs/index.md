+++
title = 'Recent Promotion & Mastery Costs'
date = 2026-11-08T00:00:00-05:00
draft = false
summary = "Promotion and mastery costs of the most recently released operators, compared with the average operator."
tags = ['Arknights', 'Guide', 'Efficiency']
excludeFromRSS = true
# Must stay above [params]: in TOML, keys below a [table] header belong to that table.
weight = 7
# Semi-hidden feedback release: published at its URL, but left out of search,
# the sitemap and tag pages (and the Mastery tables' "Costs" links switch off).
# For the wide release, delete this [build] block and restore `topic` below.
[build]
  list = 'never'
[params]
  author = 'TacticalBreakfast'
  # topic = 'Other Content'   # restore for the wide release: lists the page on the homepage
showDate = false
showAuthor = false

+++

E2 and M3 costs of operators from the last ten CN patches, the ones paid
promotion tickets are most often used on. Every operator, and Modules, are on the [full list]({{< ref "/guides/promotion-costs" >}}).

{{< efficiency-era >}}

{{% efficiency-recent %}}

## What a ticket is worth

{{< efficiency-tickets >}}

These values only show what a ticket saves, not which skills are worth
mastering. See the [Mastery Priority guide](/) for that.

## Changes From Sheets Version

- The old sheets version only included variable materials in order to simplify the calculations. This is no longer necessary, so all materials are included such as XP, LMD, Chips, and Skill Summaries. The result is the values are generally higher than the old Sheets version, especially the E2 values.
- Similarly, ticket values have also gone up slightly. This is because they now include E1 materials which were previously excluded. These values are even higher in the shop packs, which excludes the bottom 25% of Operators to show more accurate valuations.
- Due to a quirk in how Sheets handles the AVERAGESIFS formula, the old value on the Sheet was actually incorrect. The values on ICA are corrected.
- There is now an infinite shop selector so you can include the old valuations for certain items you may not have in abundance yet. This is useful for newer players or those focused primarily on older units. However, you should generally not toggle these if you don't know what you're doing.
- The colors (only on the Recents) are slightly changed. Yellow is for the average of only the recents of the same rarity. Red is now for the top quartile.