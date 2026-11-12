#!/usr/bin/env python3
"""Update content/masteries/lookahead.md from a raw article, the same raw
source tools/build_article_variants.py consumes.

Normal usage runs this against the current, live content/masteries/lookahead.md
(the default for --lookahead-md) — this script's own output, once merged in,
becomes the correct starting point for the next patch's run, so no special
handling is needed run over run. The one exception: if lookahead.md was
hand-edited for a patch *before* this script existed to do that edit for
you, point --lookahead-md at the commit right before that hand-edit (`git
log -- content/masteries/lookahead.md`) for that one catch-up run only —
otherwise this raw's own operators would already be missing from it and
nothing would need removing.

Refreshes three things:
  - "Overall Pull Priority" — the dated blurb + tier table are replaced
    with the raw's "# Pull Priority" content; the trailing numbered notes
    list is left untouched.
  - "Pull Priority Blurbs" — each raw "Name - blurb" line becomes a bolded
    "**Name**" line followed by the blurb, matching lookahead.md's style.
  - "Unit & Masteries Lookaheads" — any existing "#### Operator" entry
    belonging to one of *this* raw's own operators (i.e. it has now been
    released and covered in the main guide, so it's no longer a
    "lookahead") is removed; an event emptied by this is dropped entirely.
    Names are compared in simplified form (see normalize_name), so spacing,
    punctuation and accents don't have to agree. Every removal is listed on
    stdout, and an operator of this raw that matches no lookahead entry is
    reported as a warning — check those by hand.
    Then a new stub event is appended for whatever operators the raw's own
    "# Lookaheads" section covers — its write-ups are imported directly.
    Only the event title ("### TODO") and "*Estimated Release: TODO*" are
    left as placeholders, since the raw gives no indication of real event
    grouping or dates.
    Finally every entry's bold "**6★ · Pool**" line — old entries and new
    alike — is rebuilt from character_table.json (rarity) and
    data/operator_pools.yaml + data/pools.yaml (pool), the same lookup the
    mastery-table shortcodes use, so the lookahead shows the same pool
    labels as the main guide. Add an upcoming unit to operator_pools.yaml
    before running; one that isn't there gets only "**6★**" and a WARNING.

Usage:
    python3 tools/build_lookahead_variant.py path/to/202609-zima2-raw.md

Writes "{slug}-ica-lookahead.md" next to the raw input (or into
--output-dir), where {slug} is the raw filename with its "-raw" suffix
stripped, matching build_article_variants.py's convention. This is a
review-and-merge draft — it does not modify content/masteries/lookahead.md
directly.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_article_variants as bav

DEFAULT_LOOKAHEAD_MD = bav.REPO_ROOT / "content" / "masteries" / "lookahead.md"
DEFAULT_OPERATOR_POOLS = bav.REPO_ROOT / "data" / "operator_pools.yaml"
DEFAULT_POOLS = bav.REPO_ROOT / "data" / "pools.yaml"

# "Strong Pull - Units..." tier rows, label bold or not (raws stopped bolding
# it at Ep17, which silently dropped these rows out of the table). Named
# explicitly, like LABELLED_ROW_RE below, so prose can't match.
TIER_ROW_RE = re.compile(r"^(?:\*\*)?(Strong Pull|Lean Pull|Lean Skip|Strong Skip)(?:\*\*)?\s*-\s*(.+)$")
# The two fixed non-bolded rows at the end of the tier list. Deliberately an
# explicit whitelist rather than a generic ":"-split — a generic split would
# also match ordinary prose like "September update: ..." in the lead-in blurb.
LABELLED_ROW_RE = re.compile(r"^(Meta-value 4-5★s|Niche-value 4-5★s):\s*(.+)$")
# "Name - blurb text" rows under "## Pull Priority Blurbs".
BLURB_ROW_RE = re.compile(r"^(.+?)\s*-\s*(.+)$", re.S)


def load_yaml_map(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def parse_rarity_number(rarity_str: str | None) -> int | None:
    if not rarity_str:
        return None
    m = re.search(r"TIER_(\d+)", rarity_str)
    return int(m.group(1)) if m else None


def build_name_index(character_table: dict) -> dict[str, set[str]]:
    """Normalized appellation -> operator ids, over the whole character table
    (lookahead operators aren't in the raw's frontmatter list). Only obtainable
    'char_' entries count, so e.g. the unobtainable 'char_610_acfend' can't
    shadow the playable Mechanist."""
    index: dict[str, set[str]] = {}
    for op_id, entry in character_table.items():
        if not op_id.startswith("char_") or entry.get("isNotObtainable"):
            continue
        key = normalize_name(entry.get("appellation") or "")
        if key:
            index.setdefault(key, set()).add(op_id)
    return index


def resolve_operator_id(heading: str, name_index: dict[str, set[str]]) -> str | None:
    """The one operator a '#### ' heading names (any of its '/'-separated
    spellings), or None if it matches none or several."""
    ids: set[str] = set()
    for key in heading_name_keys(heading):
        ids |= name_index.get(key, set())
    return next(iter(ids)) if len(ids) == 1 else None


def resolve_info_line(operator_id: str, character_table: dict, operator_pools: dict, pools: dict) -> tuple[str | None, bool]:
    """(bold info line, pool found). Pool lookup matches the mastery-table
    shortcodes: operator_pools.yaml gives the key, pools.yaml its label."""
    rarity_num = parse_rarity_number(character_table.get(operator_id, {}).get("rarity"))
    pool_key = operator_pools.get(bav.strip_char_prefix(operator_id))
    pool_name = pools.get(str(pool_key)) if pool_key is not None else None

    if rarity_num is not None and pool_name:
        return f"**{rarity_num}★ · {pool_name}**", True
    if rarity_num is not None:
        return f"**{rarity_num}★**", bool(pool_name)
    if pool_name:
        return f"**{pool_name}**", True
    return None, False


# A body's leading "**6★ · Collab Gacha**" / "**5★**" line.
INFO_LINE_RE = re.compile(r"^\*\*[^*\n]*★[^*\n]*\*\*[ \t]*(?:\n|$)")


def refresh_info_lines(
    events: list[dict], character_table: dict, operator_pools: dict, pools: dict
) -> tuple[list[dict], list[str], list[tuple[str, str]]]:
    """Rebuilds every entry's info line from the data (replacing the existing
    one, or adding one if the entry has none).

    Returns (events, unresolved, missing_pool):
      unresolved    headings that matched no single operator (left untouched)
      missing_pool  [(heading, id), ...] with no pool in operator_pools.yaml
    """
    name_index = build_name_index(character_table)
    unresolved: list[str] = []
    missing_pool: list[tuple[str, str]] = []
    out = []
    for ev in events:
        entries = []
        for name, body in ev["entries"]:
            op_id = resolve_operator_id(name, name_index)
            if op_id is None:
                unresolved.append(name)
                entries.append((name, body))
                continue
            info_line, has_pool = resolve_info_line(op_id, character_table, operator_pools, pools)
            if not has_pool:
                missing_pool.append((name, op_id))
            rest = INFO_LINE_RE.sub("", body, count=1).strip()
            entries.append((name, f"{info_line}\n\n{rest}" if info_line else rest))
        out.append({**ev, "entries": entries})
    return out, unresolved, missing_pool


def extract_pull_priority_raw(article_sections: list[tuple[str, str]]) -> tuple[str, str]:
    """Returns (top_text, blurbs_text) from the raw article's 'Pull Priority'
    section, split at the '## Pull Priority Blurbs' sub-heading."""
    content = dict(article_sections).get("Pull Priority")
    if content is None:
        raise ValueError("Raw article has no '# Pull Priority' section.")
    m = re.search(r"^## Pull Priority Blurbs\s*$", content, re.M)
    if not m:
        raise ValueError("Raw article's Pull Priority section has no '## Pull Priority Blurbs' heading.")
    return content[: m.start()].strip(), content[m.end():].strip()


def parse_pull_priority_top(text: str) -> tuple[list[str], list[tuple[str, str]]]:
    """Splits the lead-in text (before '## Pull Priority Blurbs') into the
    dated blurb paragraphs and the ordered (label, units) tier rows."""
    blurb_paragraphs = []
    tier_rows = []
    for para in re.split(r"\n\s*\n", text.strip()):
        line = para.strip()
        if not line:
            continue
        m = TIER_ROW_RE.match(line)
        if m:
            tier_rows.append((m.group(1).strip(), m.group(2).strip()))
            continue
        m = LABELLED_ROW_RE.match(line)
        if m:
            tier_rows.append((m.group(1).strip(), m.group(2).strip()))
            continue
        blurb_paragraphs.append(line)
    return blurb_paragraphs, tier_rows


def parse_pull_priority_blurbs(text: str) -> list[tuple[str, str]]:
    blurbs = []
    for para in re.split(r"\n\s*\n", text.strip()):
        para = para.strip()
        if not para:
            continue
        m = BLURB_ROW_RE.match(para)
        if not m:
            raise ValueError(f"Pull Priority Blurbs paragraph doesn't match 'Name - blurb': {para[:60]!r}")
        blurbs.append((m.group(1).strip(), m.group(2).strip()))
    return blurbs


def extract_prefix(lookahead_text: str) -> str:
    m = re.search(r"^## Overall Pull Priority\s*$", lookahead_text, re.M)
    if not m:
        raise ValueError("Could not find '## Overall Pull Priority' in lookahead.md.")
    return lookahead_text[: m.start()].rstrip("\n")


def extract_existing_notes(lookahead_text: str) -> str:
    """Pulls the numbered footnote list at the end of 'Overall Pull
    Priority' — left untouched by this script."""
    m = re.search(r"^A few important notes regarding this list:\n(?:^\d+\).*\n?)+", lookahead_text, re.M)
    if not m:
        raise ValueError("Could not find the numbered notes list under 'Overall Pull Priority' in lookahead.md.")
    return m.group(0).rstrip("\n")


def build_overall_pull_priority(blurb_paragraphs: list[str], tier_rows: list[tuple[str, str]], existing_notes: str) -> str:
    lines = ["## Overall Pull Priority", "", "\n\n".join(blurb_paragraphs), ""]
    lines.append("| Tier | Units |")
    lines.append("|:---|:---|")
    for label, value in tier_rows:
        lines.append(f"| **{label}** | {value} |")
    lines.append("")
    lines.append(existing_notes)
    return "\n".join(lines)


def build_pull_priority_blurbs(blurbs: list[tuple[str, str]]) -> str:
    lines = ["## Pull Priority Blurbs"]
    for name, blurb in blurbs:
        lines.append("")
        lines.append(f"**{name}**")
        lines.append("")
        lines.append(blurb)
    return "\n".join(lines)


# ── "Unit & Masteries Lookaheads" ─────────────────────────────────────────

def parse_event_block(block: str) -> tuple[str, list[tuple[str, str]]]:
    """Splits one '### Event' block's body into (release_line, [(name, body), ...])."""
    entry_matches = list(re.finditer(r"^#### (.+)$", block, re.M))
    if not entry_matches:
        return block.strip(), []
    release_line = block[: entry_matches[0].start()].strip()
    entries = []
    for i, m in enumerate(entry_matches):
        name = m.group(1).strip()
        start = m.end()
        end = entry_matches[i + 1].start() if i + 1 < len(entry_matches) else len(block)
        entries.append((name, block[start:end].strip()))
    return release_line, entries


def parse_unit_lookaheads_events(lookahead_text: str) -> list[dict]:
    m = re.search(r"^## Unit & Masteries Lookaheads\s*$", lookahead_text, re.M)
    if not m:
        raise ValueError("Could not find '## Unit & Masteries Lookaheads' in lookahead.md.")
    section_text = lookahead_text[m.end():]

    events = []
    matches = list(re.finditer(r"^### (.+)$", section_text, re.M))
    for i, event_match in enumerate(matches):
        title = event_match.group(1).strip()
        start = event_match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(section_text)
        release_line, entries = parse_event_block(section_text[start:end])
        events.append({"title": title, "release": release_line, "entries": entries})
    return events


def normalize_name(name: str) -> str:
    """Simplified form used only for comparing operator names: lowercase,
    accents stripped, and everything that isn't a letter or digit removed
    (spaces, dots, apostrophes, hyphens...). Hand-typed names drift in exactly
    these ways — "Kal'tsit· Esperanta" in lookahead.md vs "Kal'tsit·Esperanta"
    in a raw article left her un-removed for the Episode 17 update, and the
    official EN "Kal'tsit Esperanta" differs again — so none of it should
    decide whether two names are the same operator."""
    decomposed = unicodedata.normalize("NFKD", name.replace("ł", "l").replace("Ł", "L"))
    return "".join(ch for ch in decomposed if ch.isalnum()).casefold()


def heading_name_keys(heading: str) -> set[str]:
    """Every name a '#### ' heading stands for, normalized. Dual-named
    headings like '#### Vij / Viy / Вий' or '#### Укусик / Ukusik' yield one
    key per '/'-separated alternative, so any of the spellings matches —
    as a whole name, not as a substring (a substring test would also remove
    'Angelina the Mellow Wish' for an operator named 'Lin')."""
    keys = {normalize_name(part) for part in heading.split("/")}
    keys.add(normalize_name(heading))
    keys.discard("")
    return keys


def remove_covered_operators(
    events: list[dict], operator_names: list[str]
) -> tuple[list[dict], list[tuple[str, str]], list[str], list[str]]:
    """Drops any '#### Name' entry matching one of this raw article's own
    operators (see heading_name_keys for how names are compared), since
    they're no longer upcoming. An event left with zero entries is dropped
    entirely.

    Returns (events, removed, dropped_events, unmatched):
      removed         [(event title, heading as written in lookahead.md), ...]
      dropped_events  titles of events removed because they ended up empty
      unmatched       operator names from the raw that matched no entry
    """
    wanted = {normalize_name(n): n for n in operator_names}
    matched: set[str] = set()
    filtered_events = []
    removed: list[tuple[str, str]] = []
    dropped_events: list[str] = []
    for ev in events:
        kept_entries = []
        for name, body in ev["entries"]:
            hits = heading_name_keys(name) & wanted.keys()
            if hits:
                matched |= hits
                removed.append((ev["title"], name))
            else:
                kept_entries.append((name, body))
        if kept_entries:
            filtered_events.append({**ev, "entries": kept_entries})
        elif ev["entries"]:
            dropped_events.append(ev["title"])
        else:
            filtered_events.append(ev)
    unmatched = [n for key, n in wanted.items() if key not in matched]
    return filtered_events, removed, dropped_events, unmatched


def extract_raw_lookaheads_entries(article_sections: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Returns [(name, body), ...] from the raw article's own '# Lookaheads'
    section, in order. Any intro prose before the first '## ' heading (not
    tied to a specific operator) is dropped."""
    content = dict(article_sections).get("Lookaheads")
    if content is None:
        return []
    matches = list(re.finditer(r"^## (.+)$", content, re.M))
    entries = []
    for i, m in enumerate(matches):
        name = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        entries.append((name, content[start:end].strip()))
    return entries


def build_new_stub_event(raw_lookaheads_entries: list[tuple[str, str]]) -> dict | None:
    """Info lines are added afterwards, with everyone else's (refresh_info_lines)."""
    if not raw_lookaheads_entries:
        return None
    return {"title": "TODO", "release": "*Estimated Release: TODO*", "entries": list(raw_lookaheads_entries)}


def render_events(events: list[dict]) -> str:
    parts = []
    for ev in events:
        lines = [f"### {ev['title']}", "", ev["release"]]
        for name, body in ev["entries"]:
            lines.append("")
            lines.append(f"#### {name}")
            lines.append("")
            lines.append(body)
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


def build_unit_lookaheads_section(
    lookahead_text: str, article: bav.Article, character_table: dict, operator_pools: dict, pools: dict,
    report: dict | None = None,
) -> str:
    events = parse_unit_lookaheads_events(lookahead_text)
    operator_names = [op.name for op in article.operators]
    events, removed, dropped_events, unmatched = remove_covered_operators(events, operator_names)
    if report is not None:
        report.update(removed=removed, dropped_events=dropped_events, unmatched=unmatched)

    raw_lookaheads_entries = extract_raw_lookaheads_entries(article.sections)
    new_event = build_new_stub_event(raw_lookaheads_entries)
    if new_event:
        events.append(new_event)

    events, unresolved, missing_pool = refresh_info_lines(events, character_table, operator_pools, pools)
    if report is not None:
        report.update(unresolved=unresolved, missing_pool=missing_pool)

    return "## Unit & Masteries Lookaheads\n\n" + render_events(events)


def build_lookahead_output(
    lookahead_text: str, article: bav.Article, character_table: dict, operator_pools: dict, pools: dict,
    report: dict | None = None,
) -> str:
    """`report`, if given, is filled with what the removal step did —
    'removed', 'dropped_events' and 'unmatched' (see remove_covered_operators)
    — and with 'unresolved' and 'missing_pool' (see refresh_info_lines)."""
    prefix = extract_prefix(lookahead_text)
    existing_notes = extract_existing_notes(lookahead_text)

    top_text, blurbs_text = extract_pull_priority_raw(article.sections)
    blurb_paragraphs, tier_rows = parse_pull_priority_top(top_text)
    blurbs = parse_pull_priority_blurbs(blurbs_text)

    overall_section = build_overall_pull_priority(blurb_paragraphs, tier_rows, existing_notes)
    blurbs_section = build_pull_priority_blurbs(blurbs)
    unit_lookaheads_section = build_unit_lookaheads_section(lookahead_text, article, character_table, operator_pools, pools, report)

    parts = [prefix, overall_section, blurbs_section, unit_lookaheads_section]
    return "\n\n".join(parts) + "\n"


def print_removal_report(report: dict) -> None:
    """Says on stdout exactly which lookahead entries were removed (and which
    events went with them), and warns on stderr about any operator of this
    raw that wasn't found — a silent miss is how a released operator ends up
    left behind in the lookahead."""
    removed = report.get("removed", [])
    if removed:
        print(f"\nRemoved {len(removed)} operator(s) from the lookahead (covered by this article):")
        for event_title, heading in removed:
            print(f"  - {heading}   [event: {event_title}]")
    else:
        print("\nRemoved 0 operators from the lookahead.")
    for title in report.get("dropped_events", []):
        print(f"Dropped event with no operators left: {title}")
    unmatched = report.get("unmatched", [])
    if unmatched:
        print(
            f"\nWARNING: {len(unmatched)} operator(s) from this article were NOT found in the lookahead, "
            f"so nothing was removed for them: {', '.join(unmatched)}\n"
            f"         If they were never in the lookahead this is fine. Otherwise check the "
            f"'#### ' heading in lookahead.md and remove the entry by hand.",
            file=sys.stderr,
        )


def print_pool_report(report: dict) -> None:
    """Warns on stderr about entries whose pool label couldn't be filled in —
    the lookahead's counterpart of the mastery table's "Gacha pool not set"."""
    missing = report.get("missing_pool", [])
    if missing:
        print(
            f"\nWARNING: {len(missing)} lookahead operator(s) have no pool in data/operator_pools.yaml, "
            f"so their line shows only the rarity:\n"
            + "".join(f"  - {name}   (add \"{bav.strip_char_prefix(op_id)}\")\n" for name, op_id in missing)
            + "         Add them (keys in data/pools.yaml) and rerun.",
            file=sys.stderr,
        )
    unresolved = report.get("unresolved", [])
    if unresolved:
        print(
            f"\nWARNING: {len(unresolved)} lookahead heading(s) matched no single operator in "
            f"character_table.json, so their info line was left as it was: {', '.join(unresolved)}\n"
            f"         Check the '#### ' spelling (a '/'-separated alternative in the CN table's "
            f"English name works too).",
            file=sys.stderr,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("raw_file", type=Path, help="Path to the raw article markdown (e.g. 202609-zima2-raw.md)")
    parser.add_argument("--output-dir", type=Path, default=None, help="Directory to write the output (default: same directory as raw_file)")
    parser.add_argument("--lookahead-md", type=Path, default=DEFAULT_LOOKAHEAD_MD, help="Path to lookahead.md to update (default: the live file). Override only for a one-off catch-up run against a pre-hand-edit commit — see module docstring")
    parser.add_argument("--character-table", type=Path, default=bav.DEFAULT_CHARACTER_TABLE, help="Path to character_table.json")
    parser.add_argument("--operator-pools", type=Path, default=DEFAULT_OPERATOR_POOLS, help="Path to data/operator_pools.yaml")
    parser.add_argument("--pools", type=Path, default=DEFAULT_POOLS, help="Path to data/pools.yaml")
    args = parser.parse_args()

    raw_text = args.raw_file.read_text(encoding="utf-8")
    raw_text, _todos = bav.extract_todos(raw_text)
    character_table = bav.load_character_table(args.character_table)
    article = bav.parse_article(raw_text, character_table)

    lookahead_text = args.lookahead_md.read_text(encoding="utf-8")
    operator_pools = load_yaml_map(args.operator_pools)
    pools = load_yaml_map(args.pools)

    report: dict = {}
    output = build_lookahead_output(lookahead_text, article, character_table, operator_pools, pools, report)

    stem = args.raw_file.stem
    slug = stem[:-4] if stem.endswith("-raw") else stem
    out_dir = args.output_dir or args.raw_file.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{slug}-ica-lookahead.md"
    out_path.write_text(output, encoding="utf-8")
    print(f"wrote {out_path}")
    print_removal_report(report)
    print_pool_report(report)

    print(
        f"\nREMINDER: review {out_path} before replacing content/masteries/lookahead.md. "
        f"The new '### TODO' event at the bottom needs a real event name and an estimated "
        f"release date filled in by hand — its write-ups are imported directly from the raw "
        f"article's own '# Lookaheads' section, so double-check them, but they shouldn't need "
        f"rewriting."
    )


if __name__ == "__main__":
    main()
