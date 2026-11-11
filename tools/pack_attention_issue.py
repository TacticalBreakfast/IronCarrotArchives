#!/usr/bin/env python3
"""Keep one GitHub issue in step with pack_values.json's `attention` list, so a
new problem is emailed instead of only appearing in a commit message.

Run by the `attention` job in .github/workflows/hugo.yaml, after the efficiency
data is regenerated. Needs the `gh` CLI with GH_TOKEN set (issues: write).

The open issue labelled `pack-attention` is the record of what has already
been reported -- its body lists the current entries between two markers:

  new entries        no open issue: open one (that's the email). Open issue:
                     comment with just the new lines (the email) and rewrite
                     the body with the full current list.
  entries gone       removed from the body quietly.
  list empty         close the issue, with a comment saying so.
  nothing changed    nothing.

Each email @-mentions the repository owner, because a mention always notifies.
Entries are compared with any leading count dropped ("3 upcoming pack(s) ..."
and "4 upcoming pack(s) ..." are the same entry), so a count changing alone
doesn't send an email.

Don't close the issue by hand while entries remain: the next run opens a new
one listing them all. Fix the entries (overrides, event_names, ...) instead;
the issue closes itself once the list is empty.

  python3 tools/pack_attention_issue.py            # sync the issue
  python3 tools/pack_attention_issue.py --dry-run  # print what it would do
"""
import argparse
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK_VALUES = ROOT / "data" / "efficiencies" / "pack_values.json"
LABEL = "pack-attention"
TITLE = "Shop pack data needs attention"
START, END = "<!-- attention:start -->", "<!-- attention:end -->"


def key(entry: str) -> str:
    return re.sub(r"^\d+ ", "", entry.strip())


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def listed(body: str) -> list:
    """The entries an issue body lists (between the markers)."""
    m = re.search(re.escape(START) + r"(.*?)" + re.escape(END), body or "", re.S)
    return [line[2:] for line in (m.group(1) if m else "").splitlines() if line.startswith("- ")]


def bullets(entries: list) -> str:
    return "\n".join(f"- {e}" for e in entries)


def body_for(entries: list, mention: str) -> str:
    return (f"{mention}The shop pack generator (`tools/build_pack_values.py`) lists these as needing a "
            f"look. This issue is updated by the site workflow and closes itself once the list is empty; "
            f"don't close it by hand.\n\n{START}\n{bullets(entries)}\n{END}\n")


def plan(entries: list, issue: dict | None, mention: str) -> list:
    """What to do, as (action, argument) pairs -- no side effects."""
    if not issue:
        return [("create", body_for(entries, mention))] if entries else []
    seen = {key(e) for e in listed(issue["body"])}
    new = [e for e in entries if key(e) not in seen]
    if not entries:
        return [("comment", "Nothing in the attention list any more, closing."), ("close", "")]
    actions = []
    if listed(issue["body"]) != entries:
        actions.append(("edit", body_for(entries, mention)))
    if new:
        actions.append(("comment", f"{mention}New in the attention list:\n\n{bullets(new)}"))
    return actions


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="print the actions instead of making them")
    args = ap.parse_args()

    entries = json.loads(PACK_VALUES.read_text(encoding="utf-8")).get("attention") or []
    owner = os.environ.get("GITHUB_REPOSITORY_OWNER")
    mention = f"@{owner} " if owner else ""
    found = json.loads(gh("issue", "list", "--label", LABEL, "--state", "open",
                          "--json", "number,body", "--limit", "1"))
    issue = found[0] if found else None
    actions = plan(entries, issue, mention)

    for action, arg in actions:
        if args.dry_run:
            print(f"[dry run] {action}" + (f" #{issue['number']}" if issue else "") + (f":\n{arg}" if arg else ""))
            continue
        if action == "create":
            gh("label", "create", LABEL, "--force", "--color", "d93f0b",
               "--description", "Shop pack data the generator flagged")
            print(gh("issue", "create", "--title", TITLE, "--label", LABEL, "--body", arg).strip())
        elif action == "edit":
            gh("issue", "edit", str(issue["number"]), "--body", arg)
        elif action == "comment":
            gh("issue", "comment", str(issue["number"]), "--body", arg)
        elif action == "close":
            gh("issue", "close", str(issue["number"]))
    if not actions:
        print(f"Attention list: {len(entries)} entr{'y' if len(entries) == 1 else 'ies'}, nothing new to report.")
    else:
        print(f"Attention list: {len(entries)} entries; did: {', '.join(a for a, _ in actions)}")


if __name__ == "__main__":
    main()
