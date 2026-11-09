+++
title = 'Promotion & Mastery Statistics'
date = 2026-11-08T00:00:00-05:00
draft = false
summary = "Roster-wide statistics on promotion and mastery costs: spreads by rarity, the most and least expensive, and how many of each material it all takes."
tags = ['Arknights', 'Guide', 'Efficiency']
excludeFromRSS = true
weight = 8
# Semi-hidden feedback release: published at its URL, but left out of search,
# the sitemap and tag pages. For the wide release, delete this [build] block
# and restore `topic` below.
[build]
  list = 'never'
[params]
  author = 'TacticalBreakfast'
  # topic = 'Other Content'   # restore for the wide release: lists the page on the homepage
showDate = false
showAuthor = false
+++

Statistics across every 4★–6★ operator, including those not yet on EN, using
today's infinite shop. Costs are counted the same way as on
[Promotion & Mastery Costs]({{< ref "/guides/promotion-costs" >}}). These are just for fun and do not reflect any real advice or value.

## Costs by rarity

How E2 and M3 costs are spread, for the whole roster and for
[recent operators]({{< ref "/guides/recent-promotion-costs" >}}). The bar shows
the full range as a line, the middle half (Q1 to Q3) as a box, and the median
as a tick.

{{< efficiency-overview >}}

## Most and least expensive

### 6★s

{{< efficiency-extremes rarity="6" >}}

### 5★s

{{< efficiency-extremes rarity="5" >}}

### 4★s

{{< efficiency-extremes rarity="4" >}}

## Materials for the whole roster

How many of each Tier 3–5 material it takes to promote every 4★–6★ operator to
E2 and master every skill.

{{< efficiency-materials >}}

## Materials for upcoming operators

The same counts for operators not yet released on EN — useful for deciding what
to stockpile. An operator drops off this list once released on EN.

{{< efficiency-upcoming >}}

{{< efficiency-materials scope="upcoming" >}}

## Where the cost goes

The average operator's E2 and M3 cost, split into its parts. These totals are
the ticket values on the cost pages.

{{< efficiency-breakdown >}}
