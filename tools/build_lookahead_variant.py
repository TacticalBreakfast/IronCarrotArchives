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
    Then a new stub event is appended for whatever operators the raw's own
    "# Lookaheads" section covers — its write-ups are imported directly,
    with rarity/pool filled in where derivable from character_table.json
    and data/operator_pools.yaml + data/pools.yaml. Only the event title
    ("### TODO") and "*Estimated Release: TODO*" are left as placeholders,
    since the raw gives no indication of real event grouping or dates.

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
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_article_variants as bav

DEFAULT_LOOKAHEAD_MD = bav.REPO_ROOT / "content" / "masteries" / "lookahead.md"
DEFAULT_OPERATOR_POOLS = bav.REPO_ROOT / "data" / "operator_pools.yaml"
DEFAULT_POOLS = bav.REPO_ROOT / "data" / "pools.yaml"

# "**Strong Pull** - Units..." style tier rows.
TIER_ROW_RE = re.compile(r"^\*\*(.+?)\*\*\s*-\s*(.+)$")
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


def build_full_appellation_map(character_table: dict) -> dict[str, str]:
    """Unlike build_article_variants.py's name_to_id (restricted to the
    frontmatter's operators list), this scans the whole character table —
    needed for '# Lookaheads' operators, which aren't in that list at all."""
    return {entry["appellation"]: op_id for op_id, entry in character_table.items()}


def resolve_info_line(operator_id: str | None, character_table: dict, operator_pools: dict, pools: dict) -> str | None:
    if operator_id is None:
        return None
    entry = character_table.get(operator_id, {})
    rarity_num = parse_rarity_number(entry.get("rarity"))
    short_id = bav.strip_char_prefix(operator_id)
    pool_key = operator_pools.get(short_id)
    pool_name = pools.get(pool_key) if pool_key else None

    if rarity_num is not None and pool_name:
        return f"**{rarity_num}★ · {pool_name}**"
    if rarity_num is not None:
        return f"**{rarity_num}★**"
    if pool_name:
        return f"**{pool_name}**"
    return None


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


def remove_covered_operators(events: list[dict], operator_names: list[str]) -> list[dict]:
    """Drops any '#### Name' entry matching (by case-insensitive substring,
    to handle old dual-naming like '#### Укусик / Ukusik') one of this raw
    article's own operators, since they're no longer upcoming. An event
    left with zero entries is dropped entirely."""
    lowered_names = [n.lower() for n in operator_names]
    filtered_events = []
    for ev in events:
        kept_entries = [
            (name, body)
            for name, body in ev["entries"]
            if not any(raw_name in name.lower() for raw_name in lowered_names)
        ]
        if kept_entries:
            filtered_events.append({**ev, "entries": kept_entries})
    return filtered_events


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


def build_new_stub_event(
    raw_lookaheads_entries: list[tuple[str, str]], character_table: dict, operator_pools: dict, pools: dict
) -> dict | None:
    if not raw_lookaheads_entries:
        return None
    full_appellation_map = build_full_appellation_map(character_table)
    entries = []
    for name, body in raw_lookaheads_entries:
        operator_id = full_appellation_map.get(name)
        info_line = resolve_info_line(operator_id, character_table, operator_pools, pools)
        entry_body = f"{info_line}\n\n{body}" if info_line else body
        entries.append((name, entry_body))
    return {"title": "TODO", "release": "*Estimated Release: TODO*", "entries": entries}


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
    lookahead_text: str, article: bav.Article, character_table: dict, operator_pools: dict, pools: dict
) -> str:
    events = parse_unit_lookaheads_events(lookahead_text)
    operator_names = [op.name for op in article.operators]
    events = remove_covered_operators(events, operator_names)

    raw_lookaheads_entries = extract_raw_lookaheads_entries(article.sections)
    new_event = build_new_stub_event(raw_lookaheads_entries, character_table, operator_pools, pools)
    if new_event:
        events.append(new_event)

    return "## Unit & Masteries Lookaheads\n\n" + render_events(events)


def build_lookahead_output(
    lookahead_text: str, article: bav.Article, character_table: dict, operator_pools: dict, pools: dict
) -> str:
    prefix = extract_prefix(lookahead_text)
    existing_notes = extract_existing_notes(lookahead_text)

    top_text, blurbs_text = extract_pull_priority_raw(article.sections)
    blurb_paragraphs, tier_rows = parse_pull_priority_top(top_text)
    blurbs = parse_pull_priority_blurbs(blurbs_text)

    overall_section = build_overall_pull_priority(blurb_paragraphs, tier_rows, existing_notes)
    blurbs_section = build_pull_priority_blurbs(blurbs)
    unit_lookaheads_section = build_unit_lookaheads_section(lookahead_text, article, character_table, operator_pools, pools)

    parts = [prefix, overall_section, blurbs_section, unit_lookaheads_section]
    return "\n\n".join(parts) + "\n"


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

    output = build_lookahead_output(lookahead_text, article, character_table, operator_pools, pools)

    stem = args.raw_file.stem
    slug = stem[:-4] if stem.endswith("-raw") else stem
    out_dir = args.output_dir or args.raw_file.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{slug}-ica-lookahead.md"
    out_path.write_text(output, encoding="utf-8")
    print(f"wrote {out_path}")

    print(
        f"\nREMINDER: review {out_path} before replacing content/masteries/lookahead.md. "
        f"The new '### TODO' event at the bottom needs a real event name and an estimated "
        f"release date filled in by hand — its write-ups are imported directly from the raw "
        f"article's own '# Lookaheads' section, so double-check them, but they shouldn't need "
        f"rewriting."
    )


if __name__ == "__main__":
    main()
