#!/usr/bin/env python3
"""Generate the four publish-ready variants (ICA, LD, SG, Reddit) of a Mastery
Priority guide from a single raw source article.

Usage:
    python3 tools/build_article_variants.py path/to/202607-wang-raw.md

Writes four files next to the input (or into --output-dir if given), named
by swapping the "-raw" suffix for "-ica-markdown", "-ld-markdown",
"-sg-markdown" (.mdx) and "-reddit-markdown".
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CHARACTER_TABLE = REPO_ROOT / "assets" / "game_img" / "excel-cn" / "character_table.json"

SKILL_LINE_RE = re.compile(r"^S(\d+)(?:M\d+)?\s*-\s*(.+)$")
BREAKPOINT_LINE_RE = re.compile(r"^S(\d+)M(\d+)\s*-\s*Breakpoint$", re.IGNORECASE)
ARKREC_RE = re.compile(r"^arkrec\s*[:\-]", re.IGNORECASE)
STAT_NUM_LINE_RE = re.compile(r"^[\d.]+(?:\s*[/\-]\s*(?:mod\s+)?[\d.]+)*$")
PAREN_COMMENT_RE = re.compile(r"^\(.*\)$")

AUTHOR = "TacticalBreakfast"


@dataclass
class Skill:
    number: int
    story: str
    advanced: str
    breakpoint_level: int | None = None

    @property
    def code(self) -> str:
        return f"S{self.number}M3"

    @property
    def breakpoint_code(self) -> str:
        return f"S{self.number}M{self.breakpoint_level}"


@dataclass
class OperatorBlock:
    name: str
    operator_id: str
    skills: list[Skill] = field(default_factory=list)
    prose: list[str] = field(default_factory=list)


@dataclass
class Article:
    title: str
    patch_name: str
    date: datetime
    banner_image: str
    operator_ids: list[str]
    sections: list[tuple[str, str]]  # (heading, verbatim body) for non-Masteries H1 sections, in order
    operators: list[OperatorBlock]  # Masteries content, in raw encounter order


def parse_frontmatter(raw_text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw_text, re.S)
    if not m:
        raise ValueError("Could not find a YAML frontmatter block delimited by '---'")
    frontmatter = yaml.safe_load(m.group(1))
    body = m.group(2)
    return frontmatter, body


def split_h1_sections(body: str) -> list[tuple[str, str]]:
    """Split body text into (heading, content) pairs on top-level '# ' headings."""
    matches = list(re.finditer(r"^# (.+)$", body, re.M))
    sections = []
    for i, m in enumerate(matches):
        heading = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections.append((heading, body[start:end].strip()))
    return sections


def classify_line(line: str) -> str:
    if BREAKPOINT_LINE_RE.match(line) or SKILL_LINE_RE.match(line):
        return "skill"
    if ARKREC_RE.match(line) or STAT_NUM_LINE_RE.match(line):
        return "stat"
    return "prose"


def parse_operator_block(name: str, content: str, name_to_id: dict[str, str]) -> OperatorBlock:
    operator_id = name_to_id.get(name)
    if operator_id is None:
        raise ValueError(
            f"Operator heading '{name}' in the Masteries section doesn't match any "
            f"appellation looked up from the frontmatter 'operators' list. "
            f"Check for a typo, or that the character_table.json entry's "
            f"'appellation' matches the heading exactly."
        )
    block = OperatorBlock(name=name, operator_id=operator_id)
    pending_breakpoints: list[tuple[int, int]] = []  # (skill_num, mastery_level)
    paragraphs = re.split(r"\n\s*\n", content.strip())
    for para in paragraphs:
        # Drop stray parenthesized comparison notes (e.g. "(Stainless S2 is C / C)")
        # before classifying anything, so they don't leak into prose or break
        # skill/stat-line detection.
        kept_lines = [l.strip() for l in para.splitlines() if l.strip() and not PAREN_COMMENT_RE.match(l.strip())]
        if not kept_lines:
            continue

        # Skill/breakpoint/stat lines are sometimes crammed together with no blank
        # line between them, so classify per line rather than requiring the whole
        # paragraph to be homogeneous. Only fall back to verbatim prose if the
        # paragraph contains a line that isn't one of the known metadata patterns.
        line_kinds = [classify_line(l) for l in kept_lines]
        if all(k in ("skill", "stat") for k in line_kinds):
            for line, kind in zip(kept_lines, line_kinds):
                if kind == "stat":
                    continue  # internal gain/arkrec numbers, not published anywhere
                bp = BREAKPOINT_LINE_RE.match(line)
                if bp:
                    pending_breakpoints.append((int(bp.group(1)), int(bp.group(2))))
                    continue
                m = SKILL_LINE_RE.match(line)
                num = int(m.group(1))
                rest = m.group(2).strip()
                if " / " in rest:
                    story, advanced = rest.split(" / ", 1)
                else:
                    story = advanced = rest
                block.skills.append(Skill(num, story.strip(), advanced.strip()))
        else:
            block.prose.append("\n".join(kept_lines))

    for skill_num, level in pending_breakpoints:
        matching = next((s for s in block.skills if s.number == skill_num), None)
        if matching is None:
            raise ValueError(
                f"'{name}' has a breakpoint line for S{skill_num}M{level} but no "
                f"matching 'S{skill_num} - Story / Advanced' skill line to attach it to."
            )
        matching.breakpoint_level = level

    return block


def parse_masteries_section(content: str, name_to_id: dict[str, str]) -> list[OperatorBlock]:
    matches = list(re.finditer(r"^## (.+)$", content, re.M))
    operators = []
    for i, m in enumerate(matches):
        name = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        operators.append(parse_operator_block(name, content[start:end], name_to_id))
    return operators


def load_character_table(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def parse_article(raw_text: str, character_table: dict) -> Article:
    frontmatter, body = parse_frontmatter(raw_text)

    title = frontmatter["title"]
    patch_name = title.split(" - ", 1)[1] if " - " in title else title
    date = datetime.strptime(str(frontmatter["date"]), "%m-%d-%Y")
    banner_image = frontmatter["bannerImage"]
    operator_ids = list(frontmatter["operators"])

    name_to_id = {}
    for op_id in operator_ids:
        entry = character_table.get(op_id)
        if entry is None:
            raise ValueError(f"'{op_id}' (from frontmatter operators list) not found in character_table.json")
        name_to_id[entry["appellation"]] = op_id

    all_sections = split_h1_sections(body)

    other_sections = []
    operators: list[OperatorBlock] = []
    for heading, content in all_sections:
        if heading == "Masteries":
            operators = parse_masteries_section(content, name_to_id)
        else:
            other_sections.append((heading, content))

    return Article(
        title=title,
        patch_name=patch_name,
        date=date,
        banner_image=banner_image,
        operator_ids=operator_ids,
        sections=other_sections,
        operators=operators,
    )


# ── shared helpers ───────────────────────────────────────────────────────

def strip_char_prefix(operator_id: str) -> str:
    return operator_id[5:] if operator_id.startswith("char_") else operator_id


def oxford_join(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def wiki_urlname(name: str) -> str:
    return urllib.parse.quote(name.replace(" ", "_"))


def skill_short_name(appellation: str) -> str:
    return appellation.split()[-1]


def grades_merge(story: str, advanced: str) -> bool:
    """Mirrors mergeGrades in layouts/shortcodes/mastery-table-enhanced.html:
    Story/Advanced collapse into a single spanned cell when equal and
    'None' or 'Breakpoint'."""
    if story.lower() != advanced.lower():
        return False
    return story.lower() in ("none", "breakpoint")


def render_sections_verbatim(sections: list[tuple[str, str]]) -> str:
    parts = []
    for heading, content in sections:
        parts.append(f"# {heading}\n\n{content}".rstrip())
    return "\n\n".join(parts)


# ── ICA (Hugo, TOML frontmatter) ─────────────────────────────────────────

def build_ica(article: Article, pool: str | None) -> str:
    date_iso = article.date.strftime("%Y-%m-%dT00:00:00-04:00")
    last_updated = article.date.strftime("%Y-%m-%d")
    operator_names = [op.name for op in article.operators]
    summary = (
        f"Arknights Mastery Priority guide for the most recent global update, "
        f"{article.patch_name} — covering {oxford_join(operator_names)} — "
        f"with skill recommendations and Priority rankings for the latest banner operators."
    )

    lines = []
    lines.append("+++")
    lines.append("draft = false")
    lines.append(f"date = {date_iso}")
    lines.append(f"title = 'Most Recent Update - {article.patch_name}'")
    lines.append(f'summary = "{summary}"')
    lines.append("weight = 9")
    lines.append("[params]")
    lines.append(f"  author = '{AUTHOR}'")
    lines.append("topic = 'Mastery Guide'")
    lines.append("showDate = false")
    lines.append("showAuthor = false")
    lines.append("featured = true")
    lines.append("tags = ['Mastery', 'Arknights', 'Guide', 'Skill Priority']")
    lines.append("+++")
    lines.append("")
    lines.append(f"## Masteries for {article.patch_name}")
    lines.append("")
    lines.append("### Full Articles")
    lines.append("")
    lines.append('{{< article-links sg="TBD" ld="TBD" reddit="TBD" >}}')

    for op in article.operators:
        row_strs = []
        for s in op.skills:
            row = f"{s.code},{s.story},{s.advanced}"
            if s.breakpoint_level:
                row += f",Breakpoint - {s.breakpoint_code}"
            row_strs.append(row)
        rows = "|".join(row_strs)
        lines.append("")
        lines.append(f"### {op.name}")
        lines.append("")
        pool_attr = f' pool="{pool}"' if pool else ""
        lines.append(f'{{{{< mastery-table-enhanced id="{strip_char_prefix(op.operator_id)}" rows="{rows}"{pool_attr} >}}}}')
        for para in op.prose:
            lines.append("")
            lines.append(para)
        lines.append("")
        lines.append(f'{{{{< last-updated "{last_updated}" >}}}}')

    return "\n".join(lines) + "\n"


# ── LD (wiki-style plain markdown) ───────────────────────────────────────

def build_ld(article: Article, banner_alt: str) -> tuple[str, list[tuple[str, str]]]:
    lines = []
    links: list[tuple[str, str]] = []  # (label, url), for the post-run reachability check
    lines.append(f"![{banner_alt}]({article.banner_image})  {{.center}}")
    lines.append("")
    lines.append("[[toc]]")
    lines.append("")
    lines.append(render_sections_verbatim([s for s in article.sections if s[0] != "Pull Priority" and s[0] != "Lookaheads"]))
    lines.append("")
    lines.append("# Masteries")

    for op in article.operators:
        appellation = op.name
        icon_name = wiki_urlname(appellation)
        wiki_link = f"https://arknights.wiki.gg/wiki/{icon_name}"
        icon_url = f"https://arknights.wiki.gg/images/thumb/{icon_name}_icon.png/120px-{icon_name}_icon.png"
        short = skill_short_name(appellation)
        links.append((f"{op.name} portrait icon", icon_url))

        lines.append("")
        lines.append(f"## {op.name}")
        lines.append("")
        lines.append(f"![{appellation}]({icon_url}) {{.center}}")
        lines.append("")
        lines.append("Skill | Mastery | Story | Advanced")
        lines.append(":---: | :---: | :---: | :---: |")
        for s in op.skills:
            skill_icon = f"https://arknights.wiki.gg/images/thumb/Skill-{short}{s.number}.png/64px-Skill-{short}{s.number}.png"
            links.append((f"{op.name} S{s.number} skill icon", skill_icon))
            if s.breakpoint_level:
                code = s.breakpoint_code
                grade_cell = "Breakpoint ||"
            else:
                code = s.code
                if grades_merge(s.story, s.advanced):
                    grade_cell = f"{s.story} ||"
                else:
                    grade_cell = f"{s.story} | {s.advanced}"
            lines.append(f"[![{short}S{s.number}]({skill_icon})]({wiki_link}) | {code} | {grade_cell}")
        for para in op.prose:
            lines.append("")
            lines.append(para)

    trailing = [s for s in article.sections if s[0] in ("Pull Priority", "Lookaheads")]
    if trailing:
        lines.append("")
        lines.append(render_sections_verbatim(trailing))

    return "\n".join(lines) + "\n", links


# ── link reachability check (LD wiki.gg image URLs) ───────────────────────

LINK_CHECK_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def check_url(url: str, timeout: float) -> tuple[str, str]:
    """Returns (status, detail). status is 'ok', '404', or 'unverified'
    (blocked, timed out, or errored some other way — not confirmed broken)."""
    req = urllib.request.Request(url, headers={"User-Agent": LINK_CHECK_USER_AGENT, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return "ok", f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "404", "HTTP 404"
        return "unverified", f"HTTP {e.code}"
    except Exception as e:
        return "unverified", f"{type(e).__name__}: {e}"


def check_links(links: list[tuple[str, str]], timeout: float) -> dict[str, tuple[str, str, list[str]]]:
    """Dedupes by URL and checks each once. Returns {url: (status, detail, [labels])}."""
    by_url: dict[str, list[str]] = {}
    for label, url in links:
        by_url.setdefault(url, []).append(label)

    results: dict[str, tuple[str, str, list[str]]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        future_to_url = {pool.submit(check_url, url, timeout): url for url in by_url}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            status, detail = future.result()
            results[url] = (status, detail, by_url[url])
    return results


# ── SG (Astro MDX) ────────────────────────────────────────────────────────

def build_sg(article: Article) -> str:
    description = (
        f"A guide to the best Masteries available in the {article.patch_name} patch, "
        f"as well as discussion of the units and other game related topics."
    )
    date_str = article.date.strftime("%m-%d-%Y")
    operators_field = "[" + ",".join(article.operator_ids) + "]"

    lines = []
    lines.append("---")
    lines.append(f"title: {article.title}")
    lines.append(f"description: {description}")
    lines.append(f"author: {AUTHOR}")
    lines.append(f"date: {date_str}")
    lines.append(f"bannerImage: {article.banner_image}")
    lines.append(f"operators: {operators_field}")
    lines.append("---")
    lines.append("")
    lines.append('import MasteryRecommendation from "~/components/guides/MasteryRecommendation.js";')
    lines.append("")
    lines.append(render_sections_verbatim([s for s in article.sections if s[0] not in ("Pull Priority", "Lookaheads")]))
    lines.append("")
    lines.append("# Masteries")

    for op in article.operators:
        lines.append("")
        lines.append(f"## {op.name}")
        lines.append("")
        lines.append(f'<MasteryRecommendation charId="{op.operator_id}" skills={{[')
        skill_lines = []
        for s in op.skills:
            extra = ", breakpoint: true" if s.breakpoint_level else ""
            skill_lines.append(
                f'    {{ index: {s.number - 1}, mastery: 9, story: "{s.story}", advanced: "{s.advanced}"{extra} }}'
            )
        lines.append(",\n".join(skill_lines))
        lines.append("]} client:load>")
        lines.append("</MasteryRecommendation>")
        for para in op.prose:
            lines.append("")
            lines.append(para)

    trailing = [s for s in article.sections if s[0] in ("Pull Priority", "Lookaheads")]
    if trailing:
        lines.append("")
        lines.append(render_sections_verbatim(trailing))

    return "\n".join(lines) + "\n"


# ── Reddit (plain markdown, no images/frontmatter) ───────────────────────

def build_reddit(article: Article) -> str:
    lines = []
    lines.append(render_sections_verbatim([s for s in article.sections if s[0] not in ("Pull Priority", "Lookaheads")]))
    lines.append("")
    lines.append("# Masteries")

    for op in article.operators:
        lines.append("")
        lines.append(f"## {op.name}")
        lines.append("")
        lines.append("Skill | Story | Advanced")
        lines.append(":---: | :---: | :---: |")
        for s in op.skills:
            if s.breakpoint_level:
                lines.append(f"{s.breakpoint_code} | Breakpoint | Breakpoint")
            else:
                lines.append(f"{s.code} | {s.story} | {s.advanced}")
        for para in op.prose:
            lines.append("")
            lines.append(para)

    trailing = [s for s in article.sections if s[0] in ("Pull Priority", "Lookaheads")]
    if trailing:
        lines.append("")
        lines.append(render_sections_verbatim(trailing))

    return "\n".join(lines) + "\n"


# ── CLI ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_file", type=Path, help="Path to the raw article markdown (e.g. 202607-wang-raw.md)")
    parser.add_argument("--output-dir", type=Path, default=None, help="Directory to write the four outputs (default: same directory as raw_file)")
    parser.add_argument("--character-table", type=Path, default=DEFAULT_CHARACTER_TABLE, help="Path to character_table.json")
    parser.add_argument("--pool", default=None, help="Explicit override for the ICA 'pool' attribute. Omitted by default so the mastery-table-enhanced shortcode resolves it from data/operator_pools.yaml at build time instead.")
    parser.add_argument("--banner-alt", default=None, help="Alt text for the LD banner image (default: first word of the patch name, lowercased)")
    parser.add_argument("--skip-link-check", action="store_true", help="Don't verify the LD output's wiki.gg image links are reachable")
    parser.add_argument("--link-check-timeout", type=float, default=8.0, help="Timeout in seconds per link check request (default: 8.0)")
    args = parser.parse_args()

    raw_text = args.raw_file.read_text(encoding="utf-8")
    character_table = load_character_table(args.character_table)
    article = parse_article(raw_text, character_table)

    banner_alt = args.banner_alt or article.patch_name.split()[0].lower()

    stem = args.raw_file.stem
    slug = stem[:-4] if stem.endswith("-raw") else stem
    out_dir = args.output_dir or args.raw_file.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    ld_content, ld_links = build_ld(article, banner_alt)
    ld_path = out_dir / f"{slug}-ld-markdown.md"
    outputs = {
        f"{slug}-ica-markdown.md": build_ica(article, args.pool),
        f"{slug}-ld-markdown.md": ld_content,
        f"{slug}-sg-markdown.mdx": build_sg(article),
        f"{slug}-reddit-markdown.md": build_reddit(article),
    }

    for filename, content in outputs.items():
        out_path = out_dir / filename
        out_path.write_text(content, encoding="utf-8")
        print(f"wrote {out_path}")

    ica_path = out_dir / f"{slug}-ica-markdown.md"
    operator_names = ", ".join(op.name for op in article.operators)
    if args.pool is None:
        print(
            f"\nREMINDER: {ica_path} has no pool= attribute, so mastery-table-enhanced "
            f"will resolve it from data/operator_pools.yaml at build time. Make sure each "
            f"operator ({operator_names}) has an entry there — otherwise the site will show "
            f'"Gacha pool not set (oops)" for them.'
        )
    print(
        f"\nREMINDER: the article-links shortcode in {ica_path} has sg/ld/reddit "
        f"all set to \"TBD\" — update it with the real URLs once those versions are published."
    )
    print(
        f"\nREMINDER: Verify the operator urls in {ica_path}."
    )

    if not args.skip_link_check:
        print(f"\nChecking {len(ld_links)} LD wiki.gg image links in {ld_path} ...")
        results = check_links(ld_links, args.link_check_timeout)
        broken = {u: v for u, v in results.items() if v[0] == "404"}
        unverified = {u: v for u, v in results.items() if v[0] == "unverified"}

        if broken:
            print(f"\nBROKEN LINKS (confirmed 404) in {ld_path} — these need fixing:")
            for url, (_, detail, labels) in sorted(broken.items()):
                print(f"  - [{', '.join(labels)}] {url} ({detail})")
        if unverified:
            print(
                f"\nCOULD NOT VERIFY ({len(unverified)} link(s) in {ld_path}) — "
                f"the request was blocked or failed, so this does NOT necessarily mean "
                f"the link is broken. Check these by hand:"
            )
            for url, (_, detail, labels) in sorted(unverified.items()):
                print(f"  - [{', '.join(labels)}] {url} ({detail})")
        if not broken and not unverified:
            print(f"All {len(results)} LD image links responded OK.")


if __name__ == "__main__":
    main()
