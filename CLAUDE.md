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
```

Deployment is automatic on push to `main` via `.github/workflows/hugo.yaml`.

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

## Content model

Front matter is TOML (`+++`) except `_index.md` files, which use YAML.

- `mainSections = ["posts"]` in `params.toml` governs what reaches the RSS feed and Recent Articles.
- `excludeFromRSS = true` filters a page out of the feed regardless of section — implemented by the `rss.xml` fork, not by Hugo. Set on every `other/` page and every `masteries/` page **except `mostrecent.md`**, which is deliberately left in the feed so each patch update syndicates. Don't "fix" that omission.
- The `rss.xml` fork also sorts by `.ByDate.Reverse`. Without it, Hugo's default weight-then-date ordering puts posts in the feed in an order that ignores their dates.
- Externally-hosted articles (`content/articles/`) use `layout = 'redirect'` plus `externalUrl`, which renders `_default/redirect.html` — a meta-refresh with a JS fallback.
- `hideChildPages: true` on a section `_index.md` suppresses the theme's auto-generated child grid (used by `masteries/_index.md`, which lists its children via a `{{< list >}}` shortcode instead).

## Gotchas

**Future dates.** Hugo hides pages dated in the future, in both `hugo server` and production builds. Content dates use a `00:00:00` time component by convention to avoid a page silently vanishing until later that day. `hugo server -F` reveals them.

**`docs/` is gitignored.** `docs/site-overview.md`, `maintenance-guide.md`, and `adding-new-operators.md` are local-only working notes. They are not on GitHub and can drift from the code — verify before relying on them.

**AI-crawler blocking is two-layer:** `static/robots.txt` (user-agent blocklist) plus a `noai, noimageai` robots meta tag injected via `partials/extend-head.html`.
