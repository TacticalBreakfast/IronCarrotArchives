#!/usr/bin/env python3
"""Generate the site's efficiency data from game data plus hand-edited rules:

  data/efficiencies/item_values.json      sanity value of every item, per
                                          infinite-shop era
  data/efficiencies/operator_costs.json   what every operator costs to promote,
                                          level and master, as item counts

Inputs:
  data/efficiencies/value_rules.yaml               hand-edited rules (eras, packs)
  assets/game_img/processed/item_efficiency.json   base values (yituliu export)
  assets/game_img/excel-cn/item_table.json         item -> workshop formula
  assets/game_img/excel-cn/building_data.json      workshop recipes
  assets/game_img/excel-{cn,en}/character_table.json, char_patch_table.json,
      skill_table.json, gamedata_const.json, special_operator_table.json
                                                   operator costs and names

CN tables are used so CN-only materials and operators are included; EN tables
only supply EN names.

item_values.json (generated -- never hand-edit):
  _generated    provenance + input fingerprints (see --force)
  default_era   era id shown by default (the current shop)
  items         {item id: {name, rarity}} for display
  profiles
    standard
      base      {item id: value} with today's shop (= the default era)
      eras      list, OLDEST first (Hugo sorts map keys, so not a map):
                {id, label, values} where values holds only the items that
                differ from base. id = the last material added to the shop in
                that era, or "none" before the first. The current era's
                values is empty.
    packs       same shape: standard plus the pack-only items valued by the
                rules under `packs:` in value_rules.yaml (training items at
                the average operator cost they replace, full-value XP,
                material vouchers, Kernel permits). Computed separately for
                every era, since the averages depend on material values.
  operator_values
    eras        one per era, same order as the profiles' eras:
                  id
                  operators  {char id: {promotion, skills}} for EVERY
                             operator: total sanity cost. promotion = E0 1 ->
                             E2 1 (E1 + E2 materials, chips, LMD, E0/E1
                             levelling), null below 4-star; skills = each
                             skill's M1-M3, Skill Summaries included.
                             Materials at standard values, XP at packs
                             xp_value.
                  averages   {rarity: {promotion, mastery}} over ALL operators
                             of the rarity (alternate forms' promotions once;
                             mastery per skill). Equal to the packs profile's
                             Invitation Letter / Skill Training Pack values.
  recent_operators
    patches     [{cn_patch, operators}] for the most recent CN patches, newest
                first (release_log.csv), gameplay-promoted units left out.
    groups      [{label, rarities, rarities_present, operators}] as listed
                under recent_operators: in value_rules.yaml, operators OLDEST
                first (the order they reach EN). A group can be empty; rarities_present lists only the
                rarities actually in it (e.g. [5] when no 4-star is recent).
    eras        one per era, same order as the profiles' eras:
                  id
                  groups     [{label, promotion_average,
                             promotion_top_quartile, promotion_vs_average,
                             mastery_average, mastery_top_quartile,
                             mastery_vs_average}]. *_vs_average = how far the
                             group's operators sit above the average operator
                             of their own rarity, averaged. All null for an
                             empty group.
                  rarities   {rarity: {count, promotion_average,
                             promotion_top_quartile, mastery_average,
                             mastery_top_quartile}} over the recent operators
                             of each rarity: what the recent page colours
                             against (above average / top quartile).

Eras are rebuilt from base, not stored: each shop material not yet added goes
back to its full_value, and the change is carried up the workshop recipes
(value += count x ingredient change). Carrying only the change keeps the
workshop byproduct credit at today's amount, so an era moves only items that
actually contain a material it changes, and the current era equals base
exactly.

operator_costs.json (generated -- never hand-edit):
  _generated    as above
  rarities      {rarity: {leveling, promotion_lmd}}, identical for every
                operator of a rarity. leveling = [{xp, lmd}] for levelling
                from 1 to max at each elite (E0, E1, E2); promotion_lmd =
                [E1, E2].
  operators     {char id: {...}}:
                  name            EN name, else the CN appellation
                  name_romanized  only for Cyrillic names: "Toska" for "Тоска"
                  on_en           whether the operator is on EN yet
                  rarity, profession, class_name ("Guard", ...)
                  form_of         alternate forms (Amiya Guard/Medic) only: the
                                  base operator. Their promotions duplicate
                                  the base's -- count a promotion once per
                                  form_of group when averaging.
                  promotions      [{phase, lmd, items}] for E1 and E2. items =
                                  {item id: count}, class chips included.
                  skills          [{id, name, masteries}], masteries = M1-M3
                                  as {item id: count}, Skill Summary included.
                                  Loop over the skills listed -- the count is
                                  not fixed by rarity (base Amiya has three
                                  as a 5-star).
                                  Skill levels 1-7 are deliberately left
                                  out: no promotion ticket or pack covers
                                  them, so they never affect a valuation.
  excluded      {char id: reason}: operators left out on purpose

Costs are item counts, not sanity, so a page can value them under any era or
profile. Excluded: summons/deployables (TOKEN/TRAP), unobtainable entries, and
operators promoted through gameplay rather than materials (spTargetType other
than "NONE": Raidian, Mechanist).

Usage:
    python3 tools/build_item_values.py           regenerate if any input changed
    python3 tools/build_item_values.py --force   regenerate regardless
    python3 tools/build_item_values.py --summary FILE
        also write a plain-text summary of what changed (first line = title),
        for the CI commit message. Nothing is written if nothing changed.
"""

import argparse
import csv
import hashlib
import json
import statistics
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / "data/efficiencies/value_rules.yaml"
OUTPUT = ROOT / "data/efficiencies/item_values.json"
OPERATOR_OUTPUT = ROOT / "data/efficiencies/operator_costs.json"
ASSETS = ROOT / "assets/game_img"
EFFICIENCY = ASSETS / "processed/item_efficiency.json"
ITEM_TABLE = ASSETS / "excel-cn/item_table.json"
BUILDING_DATA = ASSETS / "excel-cn/building_data.json"
SCRIPT = Path(__file__).resolve()
OPERATOR_INPUTS = [SCRIPT] + [
    ASSETS / f"excel-{server}/{table}.json"
    for server in ("cn", "en")
    for table in ("character_table", "char_patch_table", "skill_table")
] + [ASSETS / "excel-cn/gamedata_const.json", ASSETS / "excel-cn/special_operator_table.json"]
RELEASE_LOG = ASSETS / "processed/release_log.csv"
# The packs profile and recent operators use operator costs, so item values
# depend on those too.
INPUTS = [RULES, EFFICIENCY, ITEM_TABLE, BUILDING_DATA, RELEASE_LOG] + OPERATOR_INPUTS
LMD = "4001"

# Only material promotion recipes (Tier 2 -> 3 -> 4 -> 5). Chip and Skill
# Summary recipes never contain a shop material.
FORMULA_TYPES = {"F_EVOLVE"}
DECIMALS = 4


NON_CHARACTER_PROFESSIONS = {"TRAP", "TOKEN"}
SKILL_SUMMARY_3 = "3303"

PROFESSION_NAMES = {
    "WARRIOR": "Guard", "SNIPER": "Sniper", "TANK": "Defender", "MEDIC": "Medic",
    "SUPPORT": "Supporter", "CASTER": "Caster", "SPECIAL": "Specialist", "PIONEER": "Vanguard",
}

# BGN/PCGN romanization of Russian, with the soft and hard signs dropped (EN
# writes Ольга as "Olga"). Reproduces EN's official names for every
# Cyrillic-named operator except Гум -> "Gummy", a translation, not a
# romanization. "е"/"ё" become "ye"/"yë" at the start of a word and after a
# vowel or sign; see romanize().
CYRILLIC = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "ë", "ж": "zh",
    "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
    "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "kh", "ц": "ts",
    "ч": "ch", "ш": "sh", "щ": "shch", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu",
    "я": "ya",
}
CYRILLIC_VOWELS_AND_SIGNS = set("аеёиоуыэюяйъь")


def is_cyrillic(text: str) -> bool:
    return any("\u0400" <= ch <= "\u04ff" for ch in text)


def romanize(text: str) -> str:
    out = []
    prev = ""
    for ch in text:
        low = ch.lower()
        if low in CYRILLIC:
            latin = CYRILLIC[low]
            if low in "её" and (not prev or prev in CYRILLIC_VOWELS_AND_SIGNS or not prev.isalpha()):
                latin = "y" + latin
            if ch != low and latin:
                latin = latin[0].upper() + latin[1:]
            out.append(latin)
        else:
            out.append(ch)
        prev = low
    return "".join(out)


def fingerprint(paths: list) -> dict:
    return {
        path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        for path in paths
    }


def up_to_date(output: Path, inputs: dict) -> bool:
    return output.exists() and load_json(output).get("_generated", {}).get("inputs") == inputs


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")


def assets_commit() -> str | None:
    try:
        return subprocess.run(["git", "-C", str(ASSETS), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def generated(inputs: dict, rules_hint: str) -> dict:
    return {
        "by": "tools/build_item_values.py",
        "note": f"Generated file -- {rules_hint}",
        "assets_commit": assets_commit(),
        "inputs": inputs,
    }


# Pack items worth calling out in the change summary.
SUMMARY_PACK_ITEMS = [
    "voucher_elite_II_6", "voucher_elite_II_5", "voucher_elite_II_4",
    "voucher_skill_specialLevelMax_6", "voucher_skill_specialLevelMax_5", "voucher_skill_specialLevelMax_4",
    "premium_material_issue_voucher", "precious_material_voucher_perm", "advanced_material_issue_voucher",
]


def summarize(old_values: dict | None, new_values: dict, old_ops: dict | None, new_ops: dict) -> list[str]:
    """Human-readable lines describing what changed between two generations."""
    def display(char_id: str, ops: dict) -> str:
        op = ops["operators"][char_id]
        return f"{op['name']} ({op['name_romanized']})" if "name_romanized" in op else op["name"]

    def pct(old: float, new: float) -> str:
        return f"{(new - old) / old * 100:+.1f}%" if old else "new"

    old_gen = (old_values or {}).get("_generated", {})
    new_gen = new_values["_generated"]
    changed_inputs = sorted(k for k, v in new_gen["inputs"].items() if old_gen.get("inputs", {}).get(k) != v)
    lines = []

    if old_gen.get("assets_commit") != new_gen.get("assets_commit"):
        lines.append(f"Inputs: assets/game_img {old_gen.get('assets_commit') or '?'} -> "
                     f"{new_gen.get('assets_commit') or '?'}")
    other = [k for k in changed_inputs if not k.startswith("assets/")]
    if other:
        lines.append("Changed: " + ", ".join(other))

    if old_ops:
        added = sorted(set(new_ops["operators"]) - set(old_ops["operators"]))
        removed = sorted(set(old_ops["operators"]) - set(new_ops["operators"]))
        if added:
            lines.append("New operators: " + ", ".join(display(c, new_ops) for c in added))
        if removed:
            lines.append("Removed operators: " + ", ".join(display(c, old_ops) for c in removed))
        renamed = [f"{old_ops['operators'][c]['name']} -> {new_ops['operators'][c]['name']}"
                   for c in new_ops["operators"]
                   if c in old_ops["operators"] and old_ops["operators"][c]["name"] != new_ops["operators"][c]["name"]]
        if renamed:
            lines.append("Renamed: " + ", ".join(renamed))
        costs_changed = [c for c in new_ops["operators"] if c in old_ops["operators"]
                         and {k: v for k, v in old_ops["operators"][c].items() if k != "name"}
                         != {k: v for k, v in new_ops["operators"][c].items() if k != "name"}]
        if costs_changed:
            lines.append(f"Operator data changed: {len(costs_changed)} "
                         f"({', '.join(display(c, new_ops) for c in costs_changed[:5])}"
                         f"{', ...' if len(costs_changed) > 5 else ''})")

    if old_values:
        names = new_values["items"]
        old_packs, new_packs = old_values["profiles"]["packs"]["base"], new_values["profiles"]["packs"]["base"]
        packs = [f"{names[i]['name']} {old_packs[i]:.1f} -> {new_packs[i]:.1f} ({pct(old_packs[i], new_packs[i])})"
                 for i in SUMMARY_PACK_ITEMS
                 if i in old_packs and i in new_packs and abs(new_packs[i] - old_packs[i]) >= 0.05]
        if packs:
            lines.append("Pack values (current era):")
            lines += [f"  {line}" for line in packs]

        old_std, new_std = old_values["profiles"]["standard"]["base"], new_values["profiles"]["standard"]["base"]
        moved = [i for i in new_std if i in old_std and abs(new_std[i] - old_std[i]) >= 0.005]
        if moved:
            biggest = max(moved, key=lambda i: abs(new_std[i] - old_std[i]) / (old_std[i] or 1))
            lines.append(f"Item values: {len(moved)} changed (largest: {names[biggest]['name']} "
                         f"{old_std[biggest]:.2f} -> {new_std[biggest]:.2f}, "
                         f"{pct(old_std[biggest], new_std[biggest])})")
        added_items = sorted(set(new_std) - set(old_std))
        if added_items:
            lines.append("New items: " + ", ".join(names[i]["name"] for i in added_items))

        old_recent = {g["label"]: g["operators"] for g in old_values.get("recent_operators", {}).get("groups", [])}
        for group in new_values["recent_operators"]["groups"]:
            before = old_recent.get(group["label"], [])
            joined = [c for c in group["operators"] if c not in before]
            left = [c for c in before if c not in group["operators"]]
            if joined or left:
                parts = []
                if joined:
                    parts.append("+ " + ", ".join(display(c, new_ops) for c in joined))
                if left:
                    parts.append("- " + ", ".join(display(c, old_ops or new_ops) for c in left))
                lines.append(f"Recent {group['label']}: " + "; ".join(parts))

    return lines or ["Regenerated; no value changes (provenance only)."]


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_recipes(item_table: dict) -> tuple[dict, dict]:
    """({item id: [(ingredient id, count), ...]} for workshop-craftable
    materials, {material id: tier} for every material in those recipes).

    Tiers include ingredients as well as outputs: newer Tier 3 materials
    (Grindstone, Aggregate Cyclicene, ...) are farm-only, so they have no
    recipe of their own and appear only as ingredients."""
    formulas = load_json(BUILDING_DATA)["workshopFormulas"]
    recipes, tiers = {}, {}
    for item_id, item in item_table["items"].items():
        for product in item.get("buildingProductList") or []:
            if product["roomType"] != "WORKSHOP":
                continue
            formula = formulas[product["formulaId"]]
            if formula["formulaType"] in FORMULA_TYPES:
                recipes[item_id] = [(c["id"], c["count"]) for c in formula["costs"]]
    for item_id in set(recipes) | {ing for costs in recipes.values() for ing, _ in costs}:
        tiers[item_id] = rarity_number(item_table["items"][item_id]["rarity"])
    return recipes, tiers


def era_values(base: dict, recipes: dict, changed: dict) -> dict:
    """Values that differ from base when the items in `changed` take the given
    values; the change is carried up through every recipe that uses them."""
    delta_cache = {}

    def delta(item_id: str, seen=()) -> float:
        if item_id in changed:
            return changed[item_id] - base[item_id]
        if item_id in delta_cache:
            return delta_cache[item_id]
        if item_id in seen:
            sys.exit(f"Recipe cycle through item {item_id}")
        total = sum(count * delta(ing, seen + (item_id,)) for ing, count in recipes.get(item_id, []))
        delta_cache[item_id] = total
        return total

    out = {}
    for item_id, value in base.items():
        d = delta(item_id)
        if abs(d) > 10 ** -(DECIMALS + 2):
            out[item_id] = round(value + d, DECIMALS)
    return out


def build_standard(rules: dict, efficiency: list, recipes: dict) -> dict:
    base = {item["id"]: item["apValue"] for item in efficiency}

    shop = rules["infinite_shop"]
    for entry in shop:
        if entry["id"] not in base:
            sys.exit(f"value_rules.yaml: infinite_shop item {entry['id']} ({entry['name']}) has no base value")

    eras = []
    # Era k = the first k shop materials added; k = 0 is "none".
    for k in range(len(shop) + 1):
        not_yet = {e["id"]: e["full_value"] for e in shop[k:]}
        eras.append({
            "id": shop[k - 1]["id"] if k else "none",
            "label": shop[k - 1]["name"] if k else "None",
            "values": era_values(base, recipes, not_yet),
        })

    return {
        "base": {item_id: round(v, DECIMALS) for item_id, v in sorted(base.items())},
        "eras": eras,
    }


def era_tables(profile: dict) -> list[tuple[dict, dict]]:
    """[(era, full {item id: value} for that era)] for a built profile."""
    return [(era, {**profile["base"], **era["values"]}) for era in profile["eras"]]


def pack_values(rules: dict, values: dict, operators: dict, tiers: dict, exp_items: dict,
                missing: set) -> dict:
    """Values of the pack-only items, given one era's full value table."""
    xp, lmd = rules["xp_value"], values[LMD]
    rarities, ops = operators["rarities"], operators["operators"]

    def cost(items: dict) -> float:
        total = 0.0
        for item_id, count in items.items():
            if item_id not in values:
                missing.add(item_id)
                continue
            total += values[item_id] * count
        return total

    def average(numbers: list) -> float:
        return sum(numbers) / len(numbers)

    out = {}
    for item_id in rules["battle_records"]:
        out[item_id] = exp_items[item_id]["gainExp"] * xp

    for item_id, rarity in rules["training_apparatus"].items():
        e2 = rarities[str(rarity)]["leveling"][2]
        out[item_id] = e2["xp"] * xp + e2["lmd"] * lmd

    for item_id, rarity in rules["invitation_letters"].items():
        e0, e1 = rarities[str(rarity)]["leveling"][:2]
        leveling = (e0["xp"] + e1["xp"]) * xp + (e0["lmd"] + e1["lmd"]) * lmd
        promotions = [
            sum(cost(p["items"]) + p["lmd"] * lmd for p in op["promotions"])
            for op in ops.values()
            if op["rarity"] == rarity and "form_of" not in op
        ]
        out[item_id] = average(promotions) + leveling

    for item_id, rarity in rules["skill_training_packs"].items():
        skills = [
            sum(cost(m) for m in skill["masteries"])
            for op in ops.values() if op["rarity"] == rarity
            for skill in op["skills"]
        ]
        out[item_id] = average(skills)

    for item_id, rule in rules["material_vouchers"].items():
        pool = sorted((values[m] for m, tier in tiers.items() if tier == rule["tier"] and m in values),
                      reverse=True)
        out[item_id] = average(pool[:rule["top"]])

    out.update(rules["fixed"])
    return out


def build_packs(rules: dict, standard: dict, operators: dict, tiers: dict, exp_items: dict) -> dict:
    missing = set()
    tables = [(era, {**values, **pack_values(rules, values, operators, tiers, exp_items, missing)})
              for era, values in era_tables(standard)]
    if missing:
        print(f"WARNING: no value for items {sorted(missing)} in operator costs; counted as 0",
              file=sys.stderr)

    # The current era is the base; other eras store only what differs.
    base = tables[-1][1]
    return {
        "base": {k: round(v, DECIMALS) for k, v in sorted(base.items())},
        "eras": [
            {**{k: era[k] for k in ("id", "label")},
             "values": {k: round(v, DECIMALS) for k, v in sorted(values.items())
                        if abs(v - base[k]) > 10 ** -(DECIMALS + 2)}}
            for era, values in tables
        ],
    }


def recent_patches(rules: dict, operators: dict) -> list[dict]:
    with RELEASE_LOG.open(encoding="utf-8", newline="") as f:
        log = [row for row in csv.DictReader(f) if row["cn_patch"]]
    keys = sorted({row["cn_patch"] for row in log}, reverse=True)[:rules["patches"]]
    return [
        {"cn_patch": key,
         "operators": sorted(row["char_id"] for row in log
                             if row["cn_patch"] == key and row["char_id"] in operators)}
        for key in keys
    ]


def build_operator_values(xp_value: float, standard: dict, operators: dict) -> list[dict]:
    """Per era: every operator's total costs in sanity, plus rarity averages."""
    ops, rarities = operators["operators"], operators["rarities"]
    r = lambda x: round(x, DECIMALS - 2)
    eras = []
    for era, values in era_tables(standard):
        lmd = values[LMD]

        def cost(items: dict) -> float:
            return sum(values.get(i, 0) * n for i, n in items.items())

        def leveling(rarity: int) -> float:
            # E0 and E1 levelling to max: the part of an Invitation Letter
            # that isn't a promotion.
            e0, e1 = rarities[str(rarity)]["leveling"][:2]
            return (e0["xp"] + e1["xp"]) * xp_value + (e0["lmd"] + e1["lmd"]) * lmd

        valued = {
            char_id: {
                # Only operators that reach E2 (4-star and up) have a
                # promotion an Invitation Letter could cover.
                "promotion": (sum(cost(p["items"]) + p["lmd"] * lmd for p in op["promotions"])
                              + leveling(op["rarity"])) if len(op["promotions"]) >= 2 else None,
                "skills": [sum(cost(m) for m in skill["masteries"]) for skill in op["skills"]],
            }
            for char_id, op in ops.items()
        }
        averages = {}
        for rarity in sorted({op["rarity"] for op in ops.values()}):
            promotions = [valued[c]["promotion"] for c, op in ops.items()
                          if op["rarity"] == rarity and "form_of" not in op and valued[c]["promotion"] is not None]
            masteries = [m for c, op in ops.items() if op["rarity"] == rarity for m in valued[c]["skills"]]
            if promotions and masteries:
                averages[str(rarity)] = {"promotion": statistics.mean(promotions),
                                         "mastery": statistics.mean(masteries)}
        eras.append({"id": era["id"], "valued": valued, "averages": averages})

    return eras


def build_recent(rules: dict, operator_eras: list, operators: dict) -> dict:
    ops = operators["operators"]
    patches = recent_patches(rules, ops)
    # Oldest first, as the sheet listed them -- also the order they'll reach EN.
    oldest_first = [char_id for patch in reversed(patches) for char_id in patch["operators"]]
    groups = [
        {"label": g["label"], "rarities": g["rarities"],
         "operators": [c for c in oldest_first if ops[c]["rarity"] in g["rarities"]]}
        for g in rules["groups"]
    ]
    for group in groups:
        group["rarities_present"] = sorted({ops[c]["rarity"] for c in group["operators"]})

    def top_quartile(numbers: list) -> float:
        # Inclusive method = the sheet's QUARTILE(..., 3).
        return statistics.quantiles(numbers, n=4, method="inclusive")[2] if len(numbers) > 1 else numbers[0]

    r = lambda x: round(x, DECIMALS - 2)
    eras = []
    for era in operator_eras:
        valued, averages = era["valued"], era["averages"]
        group_stats = []
        for group in groups:
            members = group["operators"]
            if not members:
                group_stats.append({"label": group["label"], **dict.fromkeys(
                    ("promotion_average", "promotion_top_quartile", "promotion_vs_average",
                     "mastery_average", "mastery_top_quartile", "mastery_vs_average"))})
                continue
            promotions = [valued[c]["promotion"] for c in members]
            masteries = [m for c in members for m in valued[c]["skills"]]
            average_of = lambda c, kind: averages[str(ops[c]["rarity"])][kind]
            group_stats.append({
                "label": group["label"],
                "promotion_average": r(statistics.mean(promotions)),
                "promotion_top_quartile": r(top_quartile(promotions)),
                "promotion_vs_average": r(statistics.mean(
                    valued[c]["promotion"] - average_of(c, "promotion") for c in members)),
                "mastery_average": r(statistics.mean(masteries)),
                "mastery_top_quartile": r(top_quartile(masteries)),
                "mastery_vs_average": r(statistics.mean(
                    m - average_of(c, "mastery") for c in members for m in valued[c]["skills"])),
            })
        # The recent page colours each value against the other RECENT operators of the
        # same rarity (tickets are per rarity), not against the whole roster.
        by_rarity = {}
        for char_id in oldest_first:
            by_rarity.setdefault(str(ops[char_id]["rarity"]), []).append(char_id)
        rarity_stats = {}
        for rarity, members in by_rarity.items():
            promotions = [valued[c]["promotion"] for c in members if valued[c]["promotion"] is not None]
            masteries = [m for c in members for m in valued[c]["skills"]]
            if promotions and masteries:
                rarity_stats[rarity] = {
                    "count": len(members),
                    "promotion_average": r(statistics.mean(promotions)),
                    "promotion_top_quartile": r(top_quartile(promotions)),
                    "mastery_average": r(statistics.mean(masteries)),
                    "mastery_top_quartile": r(top_quartile(masteries)),
                }
        eras.append({"id": era["id"], "groups": group_stats, "rarities": rarity_stats})

    return {"patches": patches, "groups": groups, "eras": eras}


def operator_values_output(operator_eras: list) -> dict:
    r = lambda x: None if x is None else round(x, DECIMALS - 2)
    return {"eras": [
        {"id": era["id"],
         "operators": {c: {"promotion": r(v["promotion"]), "skills": [r(m) for m in v["skills"]]}
                       for c, v in sorted(era["valued"].items())},
         "averages": {k: {kind: r(x) for kind, x in a.items()} for k, a in era["averages"].items()}}
        for era in operator_eras
    ]}


def rarity_number(tier: str) -> int:
    return int(tier.removeprefix("TIER_"))


def load_operator_tables(server: str) -> tuple[dict, dict, dict]:
    """({char id: data} including alternate forms, {skill id: data}, patch table)."""
    chars = load_json(ASSETS / f"excel-{server}/character_table.json")
    patch = load_json(ASSETS / f"excel-{server}/char_patch_table.json")
    skills = load_json(ASSETS / f"excel-{server}/skill_table.json")
    return {**chars, **patch["patchChars"]}, skills, patch


def item_counts(costs) -> dict:
    counts = {}
    for cost in costs or []:
        counts[cost["id"]] = counts.get(cost["id"], 0) + cost["count"]
    return counts


def build_operators() -> dict:
    cn, cn_skills, cn_patch = load_operator_tables("cn")
    en, en_skills, _ = load_operator_tables("en")
    const = load_json(ASSETS / "excel-cn/gamedata_const.json")
    special = set(load_json(ASSETS / "excel-cn/special_operator_table.json")["operatorBasicData"])

    # Alternate forms -> base operator, from char_patch_table's infos.
    form_of = {
        form: base
        for base, info in cn_patch.get("infos", {}).items()
        for form in info.get("tmplIds", [])
        if form != base
    }

    exp, upgrade, max_level, gold = (const[k] for k in
                                     ("characterExpMap", "characterUpgradeCostMap", "maxLevel", "evolveGoldCost"))
    rarities = {}
    for index, levels in enumerate(max_level):
        rarities[str(index + 1)] = {
            "leveling": [
                {"xp": sum(exp[elite][:cap - 1]), "lmd": sum(upgrade[elite][:cap - 1])}
                for elite, cap in enumerate(levels)
            ],
            "promotion_lmd": [cost for cost in gold[index] if cost > 0],
        }

    operators, excluded = {}, {}
    gameplay_promoted = set()
    for char_id, char in sorted(cn.items()):
        if (not char_id.startswith("char_") or char.get("profession") in NON_CHARACTER_PROFESSIONS
                or char.get("isNotObtainable")):
            continue
        if char.get("spTargetType", "NONE") != "NONE":
            gameplay_promoted.add(char_id)
            excluded[char_id] = f"promoted through gameplay (spTargetType {char['spTargetType']})"
            continue

        rarity = rarity_number(char["rarity"])
        on_en = char_id in en
        if on_en:
            name = en[char_id]["name"]
        else:
            name = char.get("appellation") or char["name"]
        if char_id in form_of:
            name = f"{name} ({PROFESSION_NAMES.get(char['profession'], char['profession'])})"

        entry = {"name": name}
        if is_cyrillic(name):
            entry["name_romanized"] = romanize(name)
        entry.update(on_en=on_en, rarity=rarity, profession=char["profession"],
                     class_name=PROFESSION_NAMES.get(char["profession"], char["profession"]))
        if char_id in form_of:
            entry["form_of"] = form_of[char_id]

        promotion_lmd = rarities[str(rarity)]["promotion_lmd"]
        entry["promotions"] = [
            {"phase": phase, "lmd": promotion_lmd[phase - 1], "items": item_counts(char["phases"][phase]["evolveCost"])}
            for phase in range(1, len(char["phases"]))
        ]

        entry["skills"] = []
        for skill in char["skills"]:
            skill_id = skill.get("skillId")
            masteries = [item_counts(m.get("levelUpCost")) for m in skill.get("levelUpCostCond") or []]
            if not skill_id or not any(masteries):
                continue
            source = en_skills.get(skill_id) if on_en else None
            source = source or cn_skills.get(skill_id, {})
            entry["skills"].append({
                "id": skill_id,
                "name": (source.get("levels") or [{}])[0].get("name", skill_id),
                "masteries": masteries,
            })
        operators[char_id] = entry

    # The game lists gameplay-promoted units in two places; a mismatch means
    # one of them changed meaning, so the exclusion rule needs a look.
    if gameplay_promoted != special:
        print(f"WARNING: spTargetType units {sorted(gameplay_promoted)} differ from "
              f"special_operator_table {sorted(special)}", file=sys.stderr)

    return {"rarities": rarities, "operators": operators, "excluded": excluded}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true", help="regenerate even if no input changed")
    parser.add_argument("--summary", type=Path, help="write a change summary here if anything changed")
    args = parser.parse_args()

    old_values = load_json(OUTPUT) if OUTPUT.exists() else None
    old_ops = load_json(OPERATOR_OUTPUT) if OPERATOR_OUTPUT.exists() else None
    operator_inputs, inputs = fingerprint(OPERATOR_INPUTS), fingerprint(INPUTS)
    operators_current = up_to_date(OPERATOR_OUTPUT, operator_inputs) and not args.force
    values_current = up_to_date(OUTPUT, inputs) and not args.force
    if operators_current and values_current:
        print("Everything is up to date.")
        return

    operators = build_operators()
    if operators_current:
        print(f"{OPERATOR_OUTPUT.relative_to(ROOT)} is up to date.")
    else:
        write_json(OPERATOR_OUTPUT, {
            "_generated": generated(operator_inputs, "rerun the script after the game data changes."),
            **operators,
        })
        print(f"Wrote {OPERATOR_OUTPUT.relative_to(ROOT)}: {len(operators['operators'])} operators, "
              f"{len(operators['excluded'])} excluded")
        for char_id, reason in operators["excluded"].items():
            print(f"  excluded {char_id}: {reason}")

    if values_current:
        print(f"{OUTPUT.relative_to(ROOT)} is up to date.")
        return

    with RULES.open(encoding="utf-8") as f:
        rules = yaml.safe_load(f)
    efficiency = load_json(EFFICIENCY)
    item_table = load_json(ITEM_TABLE)
    recipes, tiers = load_recipes(item_table)
    standard = build_standard(rules, efficiency, recipes)
    packs = build_packs(rules["packs"], standard, operators, tiers, item_table["expItems"])
    operator_eras = build_operator_values(rules["packs"]["xp_value"], standard, operators)
    recent = build_recent(rules["recent_operators"], operator_eras, operators)
    write_json(OUTPUT, {
        "_generated": generated(inputs, "edit data/efficiencies/value_rules.yaml and rerun the script instead."),
        "default_era": standard["eras"][-1]["id"],
        "items": {
            item["id"]: {"name": item.get("enName") or item["name"], "rarity": item["rarity"]}
            for item in sorted(efficiency, key=lambda i: i["id"])
        },
        "profiles": {"standard": standard, "packs": packs},
        "operator_values": operator_values_output(operator_eras),
        "recent_operators": recent,
    })
    print(f"Wrote {OUTPUT.relative_to(ROOT)}: {len(standard['base'])} items, {len(standard['eras'])} eras")
    for name, profile in (("standard", standard), ("packs", packs)):
        for era in profile["eras"]:
            print(f"  {name:<8} {era['id']:>6}  {era['label']:<14} {len(era['values'])} values differ from base")
    for group in recent["groups"]:
        print(f"  recent {group['label']}: {len(group['operators'])} operators "
              f"from {len(recent['patches'])} patches")

    if args.summary:
        lines = summarize(old_values, load_json(OUTPUT), old_ops, load_json(OPERATOR_OUTPUT))
        args.summary.write_text("Regenerate efficiency data\n\n" + "\n".join(lines) + "\n", encoding="utf-8")
        print("\n".join(lines))


if __name__ == "__main__":
    main()
