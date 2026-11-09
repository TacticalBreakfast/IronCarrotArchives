+++
title = 'Promotion & Mastery Costs'
date = 2026-11-08T00:00:00-05:00
draft = false
summary = "What every 4★–6★ operator costs to promote to E2 and to master each skill, in sanity."
tags = ['Arknights', 'Guide', 'Efficiency']
excludeFromRSS = true
# Position in the homepage "Other Guides and Content" list.
# Must stay above [params]: in TOML, keys below a [table] header belong to that table.
weight = 6
# Marks this page as the full roster: the search index adds an entry per
# operator here (layouts/_default/index.json). Only one page should set it.
efficiencyRoster = true
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

The total cost of promoting every 4★–6★ operator to E2, of taking each of
their skills to M3, and of their X, Y and Δ modules, in sanity. Recently released operators have their own,
shorter page: [Recent Promotion & Mastery Costs]({{< ref "/guides/recent-promotion-costs" >}}).

{{< efficiency-era >}}

## What a ticket is worth

{{< efficiency-tickets >}}

## All operators

{{< efficiency-roster >}}

## How the numbers work

- **E2** is everything a Training Invitation Letter saves: E1 and E2
  materials, class chips and LMD, plus levelling through E0 and E1.
- **M3** is one skill from M0 to M3, Skill Summaries included.
- **ModX, ModY, ModΔ** are all three stages of that module: its materials,
  Module Data Blocks (yituliu's value) and LMD. Data Supplement Sticks and
  Instruments aren't counted — they can't be obtained with sanity. Other
  module types (ISW, RA, SO) cost only Module Data Blocks and aren't listed.
- Materials are valued at their sanity cost (yituliu's CN values), XP and
  LMD at 0.0036 sanity each.
- **Infinite shop:** materials sold in the infinite event shops are nearly free
  today. Pick an earlier shop to value them at what they used to cost.

## Changes From Sheets Version

- The old sheets version only included variable materials in order to simplify the calculations. This is no longer necessary, so all materials are included such as XP, LMD, Chips, and Skill Summaries. The result is the values are generally higher than the old Sheets version, especially the E2 values.
- Similarly, ticket values have also gone up slightly. This is because they now include E1 materials which were previously excluded.
- Due to a quirk in how Sheets handles the AVERAGESIFS formula, the old value on the Sheet was actually incorrect. The values on ICA are corrected.
- There is now an infinite shop selector so you can include the old valuations for certain items you may not have in abundance yet. This is useful for newer players or those focused primarily on older units. However, you should generally not toggle these if you don't know what you're doing.
- The colors (only on the Recents) are slightly changed. Yellow is for the average of only the recents of the same rarity. Red is now for the top quartile.