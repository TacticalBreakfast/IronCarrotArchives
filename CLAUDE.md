# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Hugo static site (Blowfish theme) hosting TacticalBreakfast's Arknights Mastery Priority Guide at ironcarrotarchives.com. Content-heavy, no application code — there is no test suite, linter, or package manager.

## Commands

```bash
hugo server                 # local dev at :1313
hugo server -F              # include future-dated pages (see "Future dates" below)
hugo build --gc --minify    # production-equivalent build; use to verify template changes

# Generate the four publishable variants (ICA / LD / SG / Reddit) of a guide article
python3 tools/build_article_variants.py path/to/202607-wang-raw.md

git submodule update --remote assets/game_img   # manual game-asset refresh

# Regenerate data/efficiencies/*.json (skips if no input changed; --force to override)
python3 tools/build_item_values.py
```

Deployment is automatic on push to `main` via `.github/workflows/hugo.yaml`. Its first job regenerates the efficiency data and may push a bot commit back to `main` (see "Efficiency data"), so `git pull` after a game-data merge.

## Submodules

Two, with very different update policies:

- `themes/blowfish` — pinned to a release tag. **Excluded from Dependabot**, so upgrades are manual.
- `assets/game_img` — game images plus `processed/characters.yml`, auto-synced near-daily from an upstream repo. Dependabot opens PRs for it.

`.github/dependabot.yml` sets `cooldown: default-days: 0`. This is required, not cosmetic: Dependabot's default 3-day cooldown combined with this submodule's near-daily commits means the newest commit is permanently "too fresh" and no PR is ever opened.

## `assets/` vs `static/` — the distinction that breaks things

Hugo's `resources.Get` **only reads `assets/`**. Anything resolved through the asset pipeline must live there:

- Images referenced by the mastery-table shortcodes and `home/page.html`'s `heroImage`
- `defaultSocialImage` in `params.toml` (Blowfish resolves it via `resources.Get`)

Putting such a file in `static/` produces a silent failure — no build error, just a missing image in production. `static/` is for files served verbatim (`robots.txt`, favicons).

## Theme override model

Files in `layouts/` shadow `themes/blowfish/layouts/`. They fall into two categories, and the difference matters when upgrading the theme:

**Forks of theme files** — carry local edits on top of an upstream base, so they silently go stale when the theme updates:
`_default/list.html` (adds `hideChildPages`), `_default/rss.xml` (adds `excludeFromRSS` filter, strips email from `<author>`), `partials/article-link/card.html` (full rewrite into the compact `mastery-card` layout), `partials/footer.html`, `partials/header/fixed.html`, `partials/home/page.html`, `partials/recent-articles/list.html`, `partials/toc.html`, `_default/index.json` (search index — see below).

**Purely custom** — no theme equivalent, unaffected by upgrades:
`_default/redirect.html`, `partials/extend-head.html`, and everything in `layouts/shortcodes/`.

### Upgrading the theme

Don't diff against the theme's `main`. Diff the *pinned tag* against the *target tag*, intersected with the fork list above:

```bash
git -C themes/blowfish fetch --tags
git -C themes/blowfish diff <current-tag> <target-tag> -- layouts/_default/list.html ...
```

Only forks that upstream also touched need a merge. To see what a fork actually changed, diff it against the tag it was forked from (`git -C themes/blowfish show <tag>:<path>`). Use absolute paths — `cd`-ing into the submodule makes it easy to accidentally compare the theme against itself.

## Mastery tables

The core content abstraction. Two shortcodes, differing only in that `-is` adds an Integrated Strategies grade column:

- `mastery-table-enhanced` — `{{< mastery-table-enhanced id="2027_wang" rows="S3M3,S++,S++|S2M3,A,S+" >}}`
- `mastery-table-is` — rows take a fourth grade value

**These two share nearly all their logic and must be kept in sync.** `mastery-table-enhanced.html` carries a maintainer note to this effect. A change to one almost always belongs in both.

From the `id` (e.g. `2027_wang`) they resolve, without further parameters:

| Lookup | Source | Yields |
|---|---|---|
| `char_<id>` | `assets/game_img/processed/characters.yml` | star rating, sub-profession |
| `<id>` | `data/operator_pools.yaml` → `data/pools.yaml` | banner/pool name |
| `<id>`, skill number | `assets/game_img/charavatars/`, `skills/` | portrait, skill icons |

Missing lookups degrade rather than fail: no `characters.yml` entry means no stars/sub-profession; no `operator_pools.yaml` entry renders "Gacha pool not set (oops)".

Optional parameters exist for the cases the conventions don't cover: `en_link`/`cn_link` (required for alternate forms like Amiya Guard `1001_amiya2` and Amiya Medic `1037_amiya3`, whose auto-generated links would be wrong), `icons` (pipe-separated per-row icon filename overrides, empty segment = default), and `pool`.

See `docs/adding-new-operators.md` for the full operator-addition procedure.

## Search

Search is the theme's Fuse.js over `index.json`, which the `_default/index.json` fork extends. Upstream indexes whole pages only, so a name search ranked pages by length — Guards, the longest page, came last for every Guard. The fork adds an entry per heading-level item on Masteries pages, linking to its anchor, and normalizes curly quotes (Hugo renders `'` as `’`, and `.Plain` emits it as `&rsquo;`, so typed searches like `ch'en` otherwise match nothing).

Entries are detected **by content shape**, so these formats are load-bearing — deviate and the item silently drops out of search:

- **Operator:** `### Name` whose next non-blank line is a `mastery-table-enhanced`/`-is` shortcode. Subtitle comes from `characters.yml` via the shortcode's `id`.
- **Lookahead operator:** `#### Name` whose next non-blank line is a bold `**6★ · Pool**` line; the enclosing `###` is used as the event name.
- **Glossary term:** any `###` on a page listed in `$termPages` (currently `glossary`).

The search JS (`assets/js/search.js`) is deliberately not forked. It uses `threshold: 0.0` (exact substring, no typo tolerance).

## Selector guide (`content/guides/selector/index.md`)

A standalone guide, separate from the Masteries. Built from four shortcodes whose shared logic lives in `layouts/partials/ica/`:

- `selector-tier` — grid of operator tiles, one per line (`Name | optional note`); `size="compact"` for the Gold shop / free selector / Kernel-update lists; rows are centred by default, `align="left"` left-aligns. `order-labels="Sooner | Later"` marks a list as ordered: tiles get position numbers (CSS counters, following the written line order) and a ← sooner / later → bar beneath. The numbers are deliberate — the row wraps on phones, where left/right alone would mislead. Ordered lists also wrap evenly (8 → 4+4, never 6+2) via a per-list inline `<style>` with container queries, since the break points depend on the tile count; the tile/gap sizes in `selector-tier.html` must match `custom.css`. Tiles are sized with an explicit `width`, not `flex-basis` — Firefox ignores `flex-basis` when sizing the shrink-to-fit `.sel-ordered` box, which made rows wrap early there. Test layout changes in **both Chrome and Firefox** (`/mnt/c/Program Files/Mozilla Firefox/firefox.exe --headless --remote-debugging-port`, driven over WebDriver BiDi) and at ~1024–1270px wide too — the content column narrows there while the TOC sidebar is still shown.
- `selector-tier flag="Label"` makes a list a **source**: every full-size tile elsewhere on the page for the same unit shows `Label` as an outlined amber badge linking back to that list (`ica/selector-flags.html` scans the page's raw content, like the blurb lookup). Used for the Gold shop and free selector lists so the tiers flag "you may get this one another way" with nothing maintained twice. A label ending in `?` renders dashed/unfilled for unreliable sources. Badges are deliberately outlined, normal-case and not a border — a gold border would read as "recommended". Labels must fit one line in a 6.75rem tile (~91px inner); "Free selector?" is about the limit. Compact tiles and the source lists themselves never show flags.
- `selector-blurb title="…" units="A | B"` — a blurb tiles link to. Renders a plain HTML `<h4>`, deliberately *not* a markdown heading, so blurbs stay out of the TOC.
- `selector-status` (`question | answer`, Yes/No/Unknown become badges) and `selector-timeline` (Last/Current/Next; the row whose label starts with "Current" is highlighted).

Behaviour that isn't obvious from any single file:

- **Names resolve against `characters.yml`** (`ica/resolve-operator.html`): in-game name, accents/apostrophes optional via `ica/fold.html` (shared with the search index). Only `char_` ids are considered, so summons can't shadow operators. Use a raw id (`1001_amiya2`) for names shared by several operators. Unknown or ambiguous names are **build warnings**, not errors — check `hugo` output.
- **Kernel status** comes from `data/operator_pools.yaml` (`"2"` = Kernel, `"1"` = Standard), overridden page-wide by the `poolOverrides` table in the page's front matter. That override exists for when the EN Kernel pool update lands mid-selector — the selector on sale keeps the old pools. Its comment block in the front matter explains usage.
- **Tile links:** portrait/name → the unit's blurb if one exists on the page, else their Mastery write-up; a small "Mastery" link appears on every tile that has a write-up (deliberately, even when redundant, for visual consistency). Mastery links come from `ica/mastery-anchors.html`, which scans class pages the same way the search index does and skips `mostrecent.md` (never selectable).
- **One publish switch:** `draft` in `selector/index.md`. Its menu entry is defined in that page's front matter (not `menus.en.toml`) so a draft leaves no dead link, and `content/guides/_index.md` sets `build.render: never` so no empty `/guides/` page exists.
- The page is a **bundle** (its own folder) so `featured.png`/`.jpg` beside `index.md` is picked up as the header image (`showHero = true`, `heroStyle = "big"` so the whole image shows — `custom.css` lifts the theme's 50vh cap and clears the header bar), the social preview image, and the homepage card crop. Blowfish only uses page-bundle images named `*featured*`/`*cover*`/`*thumbnail*` for social previews — a `featureimage` param alone doesn't change them; pages without one fall back to `defaultSocialImage`.
- `last-updated` takes an optional second argument `"month"` for month-precision notes.

## Efficiency data (`data/efficiencies/`)

Sanity values of items and operator costs, replacing a retired Google Sheet. Shown on `content/guides/promotion-costs/` (full roster), `content/guides/recent-promotion-costs/`, `content/guides/promotion-stats/` and `content/guides/shop-packs/` — see "Efficiency pages" below.

| File | Kind | Holds |
|---|---|---|
| `value_rules.yaml` | hand-edited | infinite-shop eras, the packs-profile rules, the recent-operator window — with the reasoning in comments |
| `item_values.json` | generated | item values per profile (`standard`, `packs`) and era; recent-operator values and stats |
| `operator_costs.json` | generated | every operator's E1/E2 and M1–M3 costs as item counts; levelling XP/LMD per rarity |
| `stats.json` | generated | stats page data, current era only: spreads, extremes, material demand (direct and with crafting), cost breakdown |
| `packs.yaml` | hand-edited | shop packs: pull maths, colour thresholds, CNY→USD price map, `event_dates`, per-pack `overrides` (by goodId), notes, and the packs not in the scrape (regular, starter, OP, common) |
| `pack_values.json` | generated | every scraped CN pack valued, with EN names/sale windows/prices; events in expected EN order; the hand-written packs; an `attention` list |

`tools/build_item_values.py` builds the JSON files from the rules plus `assets/game_img` (yituliu values in `processed/item_efficiency.json`, CN excel tables, `processed/release_log.csv`). Its docstring documents the output structure in full. **Never hand-edit the JSON** — change the rules or the script and rerun.

Non-obvious decisions, all deliberate:

- **Fingerprinted.** Each JSON records hashes of its inputs (including the script itself) and is rebuilt only when one changes, so most runs do nothing. Even a docstring edit to the script regenerates both files.
- **CI commits it back.** The `regenerate` job in `hugo.yaml` is the only job with `contents: write`. It pushes with a rebase-and-retry loop, and the build uses its output via an artifact, so a failed push never blocks a deploy (the next run retries). The bot commit's message is a human-readable summary of what changed — `git log -- data/efficiencies/` is the change log. Dependabot PRs don't show these changes; they appear in the bot commit after merging. A separate `attention` job (`tools/pack_attention_issue.py`, `issues: write`) emails new entries in the packs' `attention` list by keeping one open issue labelled `pack-attention` in step with it: new entries open it or add a comment (each @-mentions the owner), fixed ones drop from its body silently, and it closes itself when the list is empty. Closing it by hand while entries remain makes the next run open a fresh one. The build doesn't depend on that job, so its failure never blocks a deploy. `--dry-run` prints what it would do (only reads GitHub).
- **Eras are linear and rebuilt, not stored.** An era = the infinite shop as of one material. Older eras put not-yet-added materials back to their `full_value` and carry only the *change* up the workshop recipes, which holds the byproduct credit at today's amount — so the current era equals the yituliu values exactly. When CN adds a material to the infinite shop, add it to `infinite_shop` with its pre-shop value, ideally **before** merging the assets update that brings yituliu's new values. If that's missed, the site shows wrong older eras until it's added, but nothing is lost: the pre-shop value is in git history (`processed/item_efficiency.json` in the assets repo, or `data/efficiencies/item_values.json` here — the last version before the value drops).
- **CN tables throughout**, so CN-only operators and materials are included; EN only supplies names. Display name = EN name, else the CN appellation, plus a BGN/PCGN romanization for Cyrillic ones (`Тоска (Toska)`). Use character ids everywhere else — CN names change on localization.
- **Excluded operators:** summons/deployables, unobtainable entries, and units promoted through gameplay (`spTargetType` ≠ `"NONE"`: Raidian, Mechanist). The script warns if `special_operator_table` ever disagrees.
- **Amiya's alternate forms** (`form_of`) count once in promotion averages but per skill in mastery averages. Never assume skill count from rarity — base Amiya is a 5★ with three.
- **Skill levels 1–7 are never included**: no ticket or pack covers them.
- **Modules: X, Y and Δ only** (`uniequip_table` `typeName2` `X`/`Y`/`D`; ISW/RA/SO are `A`/`B` and cost only blocks). Assigned to operators via `charEquip`, not `charId` — the Amiya forms' modules all carry base Amiya's `charId`. Cost = all three phases: material + Module Data Blocks (yituliu's value; time-gated, which matters for packs) + LMD; Data Supplements are listed in `value_rules.yaml` → `modules.not_counted`. Shown on the full list and stats page only — no shop pack covers modules, so the recent page leaves them out.
- **Recipe tables are split:** most crafting is in `building_data` → `workshopFormulas`, but dualchips are made in the Factory (`manufactFormulas`). Newer Tier 3 materials (Grindstone, Aggregate Cyclicene, …) have no recipe at all — they're farm-only and appear only as ingredients.
- **Shop packs** (`tools/build_pack_values.py`, run by `build_item_values.py` after the item values, since it uses the `packs` profile; its docstring documents `pack_values.json`). Event packs come from `processed/shop_packs.json` in the assets repo (built monthly from three sources: yituliu's pack API for contents, prts.wiki as a second source — stale since Oct 2026 — and CN game data, which fills in packs neither lists by copying an earlier same-name pack's contents; each pack records `contentsSource`, and copied or disputed contents land in the `attention` list; packs are only ever added). Each pack's **goodId is shared by CN and EN**, which is how EN names, sale windows and real USD prices (cents) are found in EN `shop_client_table.json` — the scrape's `enName` is only a fallback, then its `mtlName` (a Claude API machine translation made once per pack by the scraper, needs the assets repo's `ANTHROPIC_API_KEY` Actions secret; shown with an "(MTL)" tag). A rerun pack reuses its original goodId, so its EN window = the earliest one starting no earlier than the CN start (older windows belong to earlier runs). A pack's own sale window often outlasts its event; live/ended is decided at display time, never in the generator. Price precedence: override → EN data → price map (`estimated` entries flagged) → none. Valued with the sheet's maths (in `packs.yaml`); the **colour cutoffs are derived**, not typed, from `op_packs` (skipping those marked `threshold: false`: $1, $5): green = the worst-value double pack, yellow = the best-value pack without the double; Kernel pulls count 0; selectors and α/β/γ "one of three" vouchers aren't valued (note only). **Ticket values in the packs profile drop the cheapest quarter** (`value_rules.yaml` → `tickets_exclude_bottom_quartile`). The cost pages' ticket table (`efficiency-tickets`) shows these same packs-profile values, so the pages agree; the plain averages (`operator_values → averages`) are still generated but not shown. The `attention` list (bot commit message + `pack_values.json`) is where weak spots surface: goodIds matched by price only (`goodIdMatchedBy: "price"` from the scraper), live packs without an EN price or name, missing item values, shown events with no EN name (add to `packs.yaml` → `event_names`). Copied contents are not listed for chip packs (regular and predictable).
- **Shop packs page** (`content/guides/shop-packs/`): shortcodes `efficiency-packs` (used as `{{% %}}`: one `### Event` heading per event, under the page's `## Events`, same no-blank-lines rule as `efficiency-recent`), `-packs-table section="regular|starter|common"`, `-packs-op`, `-packs-key` (colour legend), `-packs-notes` (the numbered notes, Markdown; `upcoming` is linked once per not-yet-on-EN event, from its date line); partials in `layouts/partials/ica/efficiency/packs/`. Each pack is its own `<tbody>` (numbers row + a full-width contents row — ten columns didn't fit). Live/ended is decided at build time (`now`) **and again in the browser** (`efficiency.js`, "Shop packs") from each pack's EN window: ended packs, then empty events and their TOC entries (both Blowfish TOCs; the anchor id is on a `div` inside the heading), disappear without a rebuild. Hidden (cosmetic) packs never render. Within an event, packs are ordered by group (`packs.yaml` → `pack_groups`, assigned from contents by `pack_group()` in the generator, overridable per pack), then price. Notes are numbered in `packs.yaml` order — `pack_values.json` lists them as an array because Hugo sorts map keys.
- **Reader-facing text in `packs.yaml`** (`notes:`, pack `text:`, common-pack names) is the maintainer's to write — don't edit it.
- **Recent operators** come from `release_log.csv` (assets repo), grouped by `cn_patch` (a patch's start date, so older patches can be backfilled without renumbering). A recent-operator group may be empty — 4★s are rare — and pages should then omit it.

### Efficiency pages

Shortcodes `efficiency-era`, `-roster`, `-recent`, `-recent-key`, `-tickets` (cost pages) and `-overview`, `-extremes`, `-materials`, `-upcoming`, `-breakdown` (stats page, current era only, no selector), shared partials in `layouts/partials/ica/efficiency/`, script `assets/js/efficiency.js`, styles under the `eff-` prefix in `custom.css`.

- **Templates never calculate.** Hugo renders the default era's numbers from the JSON; `efficiency-era` lets readers pick another, and the script fetches one generated file with every era (`resources.FromString` in `context.html`) and rewrites the cells marked `data-eff-*`. The choice is stored in `localStorage` and shared across pages. Only the recent page is coloured: values against the *recent* operators of the same rarity (above average / top quartile, from `recent_operators → rarities`); a rarity with a single recent operator stays uncoloured. Measured against the whole roster every recent operator looked expensive, and the full roster isn't coloured at all — its averages are still generated (`operator_values → averages`) for later use. The rule exists twice — `level.html` and the script — keep them in step.
- **Roster anchors `#op-<char id>` are load-bearing**: the search index (`efficiencyRoster = true` in the roster page's front matter adds one entry per operator, from the data) and the "Costs" link in both mastery-table shortcodes point at them. The "Costs" link appears only while `/guides/promotion-costs` is published *and listed* (`ica/efficiency/roster-url.html`).
- **Material counts** (`efficiency-materials`): "with crafting" expands Tier 5 → 4 → 3 through the workshop recipes (all make one item); sanity counts each material once at its own value. No E1 uses Tier 3+ materials, so E1 never shows in these counts. Skill levels 1–7 are excluded throughout.
- **The script loads from `partials/extend-head-uncached.html`** via `ica/efficiency/script.html`, which checks `.HasShortcode`. Not from the shortcodes themselves: they used `.Page.Store` to emit it once, but Hugo doesn't reset `.Store` on dev-server rebuilds, so after any edit `hugo server` served the pages without it. `extend-head.html` can't be used — Blowfish passes it only `.Site`, cached. A new shortcode that needs the script must be added to that `.HasShortcode` list.
- **Operator names link to their write-up** (`ica/efficiency/write-ups.html`): class page, else `mostrecent.md`, else `lookahead.md`, else no link. Lookahead entries have no id, so their `#### Name` is resolved through `ica/resolve-operator.html`; an unresolved name silently gets no link. Only this partial looks past the class pages — `ica/mastery-anchors.html` (shared with the selector guide) must keep skipping both.
- **The full list scrolls in its own box** (`.eff-table-wrap--frozen`, 75vh) so its header row can stay pinned: a sticky header only sticks inside its nearest scrolling box, and that box must scroll sideways on phones anyway. Because of that, a link to a row (`#op-…`, used by search and the Mastery tables' "Costs" links) is re-positioned by `showLinkedRow()` in the script — the browser alone puts the box under the site's fixed header.
- **`.eff-table` sets `display: table`** to undo the theme's `display: block` on tables, which stopped rows filling the width.
- **One publish switch per page**: `draft`. Menu entries live in each page's front matter (parent `Efficiency`, defined in `menus.en.toml`), as with the selector guide. `promotion-costs` and `shop-packs` carry `aliases` for the old homepage cards' URLs (`/other/ticketeff/`, `/other/paidpackslist/`), which pointed at the retired Google Sheet.
- Rarities arrive from JSON as floats — wrap in `int` before `printf "%d"`.

## Local tooling quirks

- Hugo is a **snap** with a private `/tmp`: `hugo -d /tmp/...` writes somewhere other processes can't see. Build into `public/` (gitignored) and copy out.
- `hugo server` **serves from disk by default** (writes `public/`). Two servers at once overwrite each other; use `--renderToMemory`.
- Neither Node nor a Linux browser is installed. Windows Chrome (`/mnt/c/Program Files/Google/Chrome/Application/chrome.exe`) can reach WSL servers thanks to mirrored networking; its `--screenshot` mode can't scroll to anchors and has a ~500px minimum window width, so use the DevTools protocol with `Emulation.setDeviceMetricsOverride` for true phone viewports. Force light/dark with `HUGO_PARAMS_AUTOSWITCHAPPEARANCE=false HUGO_PARAMS_DEFAULTAPPEARANCE=dark`.

## Content model

Front matter is TOML (`+++`) except `_index.md` files, which use YAML.

- The RSS feed (`_default/rss.xml` fork) includes **every regular page on the site** except those with `excludeFromRSS = true` — it is *not* limited to `mainSections`. A page appears in the feed once, when first published; updating it later does not re-announce it. To announce an update, add a page in `content/articles/` with `layout = 'redirect'` and `externalUrl` pointing at the updated page (internal paths like `/guides/selector/` work).
- `excludeFromRSS = true` filters a page out of the feed regardless of section — implemented by the `rss.xml` fork, not by Hugo. Set on every `other/` page and every `masteries/` page **except `mostrecent.md`**, which is deliberately left in the feed so each patch update syndicates. Don't "fix" that omission.
- The `rss.xml` fork also sorts by `.ByDate.Reverse`. Without it, Hugo's default weight-then-date ordering puts posts in the feed in an order that ignores their dates.
- Externally-hosted articles (`content/articles/`) use `layout = 'redirect'` plus `externalUrl`, which renders `_default/redirect.html` — a meta-refresh with a JS fallback.
- `hideChildPages: true` on a section `_index.md` suppresses the theme's auto-generated child grid (used by `masteries/_index.md`, which lists its children via a `{{< list >}}` shortcode instead).

## Gotchas

**Future dates.** Hugo hides pages dated in the future, in both `hugo server` and production builds. Content dates use a `00:00:00` time component by convention to avoid a page silently vanishing until later that day. `hugo server -F` reveals them.

**`docs/` is gitignored.** `docs/site-overview.md`, `maintenance-guide.md`, and `adding-new-operators.md` are local-only working notes. They are not on GitHub and can drift from the code — verify before relying on them.

**AI-crawler blocking is two-layer:** `static/robots.txt` (user-agent blocklist) plus a `noai, noimageai` robots meta tag injected via `partials/extend-head.html`.
