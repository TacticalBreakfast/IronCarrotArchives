"""Shop pack valuations: data/efficiencies/pack_values.json.

Run by tools/build_item_values.py (after it has written item_values.json, whose
`packs` profile values the items); not meant to be run on its own.

Inputs:
  data/efficiencies/packs.yaml                    hand-edited rules, overrides and
                                                  the packs not in the scrape
  data/efficiencies/item_values.json              packs profile (current era)
  assets/game_img/processed/shop_packs.json       CN packs, scraped from prts.wiki
  assets/game_img/excel-en/shop_client_table.json EN names, sale windows, prices
  assets/game_img/excel-en/activity_table.json, crisis_v2_table.json,
      sandbox_perm_table.json                     EN event names and dates
  assets/game_img/excel-{en,cn}/item_table.json   item names and types

pack_values.json (generated -- never hand-edit):
  _generated   provenance + input fingerprints
  lag_days     typical days between an event's CN and EN start (median of the
               five most recent events on both servers); orders upcoming events
  events       [{id, name, name_source (en | yaml | cn), cn_name, cn_start, en_start,
               en_end, expected_en_start, order_date, packs: [pack keys]}], in
               expected EN order. name = EN game data, else packs.yaml
               event_names (announced names, before EN data has them), else CN.
               en_* = the event's own EN dates (null until EN has it);
               expected_en_start = packs.yaml event_dates; order_date = EN
               start, else expected, else CN start + lag_days.
  packs        {key: pack}, key = goodId (else "<CN name>@<CN start>"), for the
               scraped CN packs. Ended packs are kept: the page hides them.
  regular, starter, common   [pack] from packs.yaml, in file order
  op_packs     [{usd, op, double, per_op, per_pull, per_op_double, per_pull_double}]
  notes        [{key, text}], copied from packs.yaml in file order (the page
               numbers them)
  attention    [str]: what needs a look (also printed and put in the CI commit
               message). Relative to when it ran: packs whose EN sale had
               already ended are left out.

A pack:
  key, name, name_source (override | en | scrape | mtl | cn), cn_name, good_id,
  good_id_matched_by ("price" for the weak same-day/same-price match, else null),
  event, cn_start, cn_end, en_start, en_end, window_source (pack | event | null),
  price_cny, usd, usd_source (override | en | map | map_estimated | null).
            EN data only has a price when the pack's shop banner is the
            standard one (normalGiftParam); custom-art banners carry none, so a
            live pack can rightly be priced from the (confirmed) map,
  contents  [{id, name, count, kind, value}]: kind = material | op | pulls |
            kernel | zero | cosmetic | selector | random_of_3; value = sanity
            each (materials, zero) or pulls each (pulls); cosmetics have no id
  measure   {material, op, pulls, total_op, per_op, total_pulls, per_pull} or
            null when the pack isn't valued (selectors, "one of three", Kernel
            only); per_* null when there's nothing to divide by
  colours   {per_op, per_pull}: green | yellow | red | null
  notes     [note keys], automatic ones first
  group     what kind of pack it is, from its contents (pack_group) or a
            packs.yaml override; orders the packs within an event
  hidden    true when hidden from the page; hidden_reason = cosmetic (UI items
            and nothing of material value -- the default for those) or override
  text      contents description to show instead of the list (hand-written packs)

Dates are ISO 8601: CN with +08:00 as scraped, EN in UTC (Z). Live/ended is
decided where the page is shown (build time, then the reader's browser), not
here, so the file only changes when an input does.

The maths is the sheet's (packs.yaml explains it):
  pulls = permits + Orundum / 600 + banner permits by item type
  material = everything else at its packs-profile value
  total_op = material / 135 + OP + pulls x 600/180;   per_op = usd / total_op
  total_pulls = pulls + OP x 180/600;                 per_pull = usd / total_pulls
"""

import json
import re
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from build_item_values import ASSETS, ROOT, OUTPUT as VALUES_OUTPUT, fingerprint, generated, load_json, \
    up_to_date, write_json

PACK_RULES = ROOT / "data/efficiencies/packs.yaml"
VALUE_RULES = ROOT / "data/efficiencies/value_rules.yaml"
SHOP_PACKS = ASSETS / "processed/shop_packs.json"
PACK_OUTPUT = ROOT / "data/efficiencies/pack_values.json"
EN_SHOP = ASSETS / "excel-en/shop_client_table.json"
EN_ACTIVITY = ASSETS / "excel-en/activity_table.json"
EN_CRISIS = ASSETS / "excel-en/crisis_v2_table.json"
EN_SANDBOX = ASSETS / "excel-en/sandbox_perm_table.json"
EN_ITEMS = ASSETS / "excel-en/item_table.json"
CN_ITEMS = ASSETS / "excel-cn/item_table.json"
PACK_INPUTS = [PACK_RULES, VALUE_RULES, VALUES_OUTPUT, SHOP_PACKS, EN_SHOP, EN_ACTIVITY, EN_CRISIS,
               EN_SANDBOX, EN_ITEMS, CN_ITEMS]

OP, ORUNDUM, LMD = "4002", "4003", "4001"
OP_SANITY = 135
KERNEL_ITEMS = {"classic_gacha", "classic_gacha_10"}
KERNEL_TYPES = {"CLASSIC_TKT_GACHA", "CLASSIC_TKT_GACHA_10"}
RANDOM_OF_3_TYPES = {"VOUCHER_CGACHA"}
BANNER_ONLY_TYPES = {"EXCLUSIVE_TKT_GACHA", "EXCLUSIVE_TKT_GACHA_10"}
COSMETIC_CATEGORIES = {"Avatar", "Namecard", "Skin", "Scene", "UI Theme", "Furniture", "Unknown"}
DECIMALS = 4
# An EN sale window may start a day before the CN date it belongs to (time
# zones; the synced Ambience Synesthesia packs start the same calendar day).
WINDOW_SLACK = timedelta(days=1)


def iso_utc(ts) -> str | None:
    if not isinstance(ts, (int, float)) or not 1e9 < ts < 4e9:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse(iso: str | None) -> datetime | None:
    return datetime.fromisoformat(iso.replace("Z", "+00:00")) if iso else None


def rnd(x):
    return None if x is None else round(x, DECIMALS)


# ── EN game data ─────────────────────────────────────────────────────────────

def load_en_shop():
    """goodId -> EN name; goodId -> [(start, end, price in cents or None)]."""
    table = load_json(EN_SHOP)
    names = {g: d["displayName"] for g, d in table["shopGPDataDict"].items() if d.get("displayName")}
    windows = {}

    def add(good_id, start, end, price=None):
        if good_id and iso_utc(start) and iso_utc(end):
            windows.setdefault(good_id, []).append((start, end, price))

    for entry in table.get("recommendList") or []:
        gift = (entry.get("templateParam") or {}).get("normalGiftParam") or {}
        for group in entry.get("groupList") or []:
            for slot in group.get("dataList") or []:
                if slot.get("cmd") == "GIFTPACKAGE":
                    gid = slot.get("param1")
                    add(gid, entry.get("startDatetime"), entry.get("endDatetime"),
                        gift.get("price") if gift.get("goodId") == gid else None)
    for carousel in table.get("carousels") or []:
        for slot in carousel.get("items") or []:
            if slot.get("cmd") == "GIFTPACKAGE":
                add(slot.get("param1"), slot.get("startTime"), slot.get("endTime"))
    return names, windows


def en_windows_for(good_id: str, windows: dict) -> list:
    """EN windows for a goodId, including suffixed variants EN sometimes uses
    (GP_NpOne_nc_0_7 is scheduled as GP_NpOne_nc_0_7_NpOne_nc_0_7_v1)."""
    found = list(windows.get(good_id, []))
    for gid, w in windows.items():
        if gid != good_id and gid.startswith(good_id + "_"):
            found += w
    return found


def pick_window(cn_start: datetime, candidates: list):
    """The EN sale of this CN occurrence: the earliest window starting no
    earlier than the CN start. Reruns reuse their original goodId, so a goodId
    can carry windows from years before (Roka Voyager's 2023 window must not
    count for its 2026 CN rerun). recommendList and carousels list the same
    sale with starts up to a day apart, so overlapping windows are merged.
    Returns (start, end, price in cents or None) or None."""
    after = sorted((w for w in candidates
                    if datetime.fromtimestamp(w[0], tz=timezone.utc) >= cn_start - WINDOW_SLACK),
                   key=lambda w: (w[0], w[1]))
    if not after:
        return None
    start, end, price = after[0]
    for s, e, p in after[1:]:
        if s <= end:                       # overlaps the chosen sale: same one
            end = max(end, e)
            price = price if price is not None else p
    return start, end, price


def load_en_events() -> dict:
    """Event id -> {name, start, end} on EN, from the three tables events live in
    (the same three parse_shop_packs.py reads on the CN side)."""
    events = {}
    for event_id, d in load_json(EN_ACTIVITY)["basicInfo"].items():
        if d.get("startTime"):
            events[event_id] = {"name": d.get("name"), "start": d["startTime"], "end": d.get("endTime")}
    for event_id, d in load_json(EN_CRISIS).get("seasonInfoDataMap", {}).items():
        if d.get("startTs"):
            events[event_id] = {"name": d.get("name"), "start": d["startTs"], "end": d.get("endTs")}
    for event_id, d in load_json(EN_SANDBOX).get("basicInfo", {}).items():
        entries = [e for e in d.get("homeEntryDisplayData") or [] if e.get("startTs")]
        if entries:
            # A topic can rerun; its first EN run is the one a CN pack batch maps to.
            first = min(entries, key=lambda e: e["startTs"])
            events[event_id] = {"name": d.get("topicName"), "start": first["startTs"], "end": first.get("endTs")}
    return events


# ── Valuing contents ─────────────────────────────────────────────────────────

class Valuer:
    def __init__(self, rules: dict, values: dict, value_rules: dict, item_names: dict):
        self.pull_items = {str(k): v for k, v in rules["pulls"]["items"].items()}
        self.pull_types = rules["pulls"]["item_types"]
        self.orundum_per_pull = rules["pulls"]["orundum_per_pull"]
        self.orundum_per_op = rules["pulls"]["orundum_per_op"]
        self.colours = rules["colours"]
        self.values = values
        self.xp_value = value_rules["packs"]["xp_value"]
        self.voucher_items = set(value_rules["packs"]["material_vouchers"])
        self.ticket_items = set(value_rules["packs"]["invitation_letters"]) | \
            set(value_rules["packs"]["skill_training_packs"])
        self.item_names = item_names
        self.missing = set()

    def entry(self, item_id, count, item_type=None, category=None, name=None) -> dict:
        """One content line, classified."""
        item_id = None if item_id is None else str(item_id)
        label = name or (self.item_names.get(item_id) if item_id else None) or item_id
        if item_id == "xp":
            return {"id": "xp", "name": "XP", "count": count, "kind": "material", "value": self.xp_value}
        if item_id == "selector" or category == "Special":
            return {"id": item_id, "name": label if item_id != "selector" else "6★ selector",
                    "count": count, "kind": "selector", "value": None}
        if item_id in KERNEL_ITEMS or item_type in KERNEL_TYPES:
            return {"id": item_id, "name": label, "count": count, "kind": "kernel", "value": 0}
        if item_type in RANDOM_OF_3_TYPES:
            return {"id": item_id, "name": label, "count": count, "kind": "random_of_3", "value": None}
        if item_id in self.pull_items:
            return {"id": item_id, "name": label, "count": count, "kind": "pulls", "value": self.pull_items[item_id]}
        if item_type in self.pull_types:
            return {"id": item_id, "name": label, "count": count, "kind": "pulls",
                    "value": self.pull_types[item_type], "item_type": item_type}
        if item_id == ORUNDUM:
            return {"id": item_id, "name": label, "count": count, "kind": "pulls", "value": 1 / self.orundum_per_pull}
        if item_id == OP:
            return {"id": item_id, "name": label, "count": count, "kind": "op", "value": None}
        if category in COSMETIC_CATEGORIES and not item_id:
            return {"id": None, "name": label, "count": count, "kind": "cosmetic", "value": None}
        if item_id in self.values:
            v = self.values[item_id]
            return {"id": item_id, "name": label, "count": count, "kind": "material" if v else "zero", "value": v}
        if category in COSMETIC_CATEGORIES:
            return {"id": item_id, "name": label, "count": count, "kind": "cosmetic", "value": None}
        self.missing.add(item_id)
        return {"id": item_id, "name": label, "count": count, "kind": "zero", "value": 0}

    def measure(self, contents: list, usd):
        kinds = {c["kind"] for c in contents}
        material = sum(c["count"] * c["value"] for c in contents if c["kind"] in ("material", "zero"))
        op = sum(c["count"] for c in contents if c["kind"] == "op")
        pulls = sum(c["count"] * c["value"] for c in contents if c["kind"] == "pulls")
        if kinds & {"selector", "random_of_3"} or not (material or op or pulls):
            return None
        total_op = material / OP_SANITY + op + pulls * self.orundum_per_pull / self.orundum_per_op
        total_pulls = pulls + op * self.orundum_per_op / self.orundum_per_pull
        per_op = usd / total_op if usd is not None and total_op else None
        per_pull = usd / total_pulls if usd is not None and total_pulls else None
        return {"material": rnd(material), "op": op, "pulls": rnd(pulls), "total_op": rnd(total_op),
                "per_op": rnd(per_op), "total_pulls": rnd(total_pulls), "per_pull": rnd(per_pull)}

    def colour(self, value, kind):
        if value is None:
            return None
        t = self.colours[kind]
        return "green" if value <= t["green"] else "yellow" if value <= t["yellow"] else "red"

    def auto_notes(self, contents: list) -> list:
        ids = {c["id"] for c in contents}
        kinds = {c["kind"] for c in contents}
        types = {c.get("item_type") for c in contents}
        notes = []
        if ids & {"mod_update_token_1", "mod_update_token_2"}:
            notes.append("module_materials")
        if "mod_unlock_token" in ids:
            notes.append("module_blocks")
        if ids & self.voucher_items:
            notes.append("vouchers")
        if "kernel" in kinds:
            notes.append("kernel")
        if ids & self.ticket_items:
            notes.append("tickets")
        if "selector" in kinds:
            notes.append("selector")
        if "random_of_3" in kinds:
            notes.append("random_of_3")
        if types & BANNER_ONLY_TYPES:
            notes.append("banner_only")
        return notes

    def finish(self, pack: dict, own_notes: list) -> dict:
        """Add measure, colours and notes to a pack that has contents and usd."""
        m = self.measure(pack["contents"], pack["usd"])
        pack["measure"] = m
        pack["colours"] = {"per_op": self.colour(m and m["per_op"], "per_op"),
                           "per_pull": self.colour(m and m["per_pull"], "per_pull")}
        pack["notes"] = list(dict.fromkeys(self.auto_notes(pack["contents"]) + list(own_notes or [])))
        return pack


# Class chips and dualchips (32<class 1-8><1 or 3>) and Skill Summaries: a chip pack's contents.
CHIP_RE = re.compile(r"^32[1-8][13]$")
SKILL_SUMMARIES = {"3301", "3302", "3303"}
MODULE_ITEMS = {"mod_unlock_token", "mod_update_token_1", "mod_update_token_2"}
HEADHUNTING_KINDS = {"pulls", "kernel", "selector", "random_of_3"}


def pack_group(contents: list, value_rules: dict) -> str:
    """What kind of pack this is, for ordering packs within an event (packs.yaml
    pack_groups). Judged on what's left once cosmetics, Originite Prime and LMD
    are set aside -- those turn up in every kind of pack. Anything mixed is a
    bundle."""
    core = [c for c in contents if c["kind"] != "cosmetic" and c["id"] not in (OP, LMD)]
    ids = {c["id"] for c in core}
    rules = value_rules["packs"]
    training = set(rules["training_apparatus"]) | set(rules["invitation_letters"]) | \
        set(rules["skill_training_packs"])
    if not core:
        return "funding"
    if any(CHIP_RE.match(i or "") for i in ids) and \
            all(CHIP_RE.match(i or "") or i in SKILL_SUMMARIES for i in ids):
        return "chips"
    if ids <= MODULE_ITEMS:
        return "modules"
    if ids <= set(rules["material_vouchers"]):
        return "materials"
    if ids <= training:
        return "training"
    if all(c["kind"] in HEADHUNTING_KINDS for c in core):
        return "headhunting"
    return "bundles"


# ── Building ─────────────────────────────────────────────────────────────────

def hand_written(valuer: Valuer, section: list) -> list:
    out = []
    for p in section or []:
        contents = [valuer.entry(k, n) for k, n in (p.get("contents") or {}).items()]
        pack = {"name": p["name"], "usd": p.get("usd"), "contents": contents, "text": p.get("text")}
        out.append(valuer.finish(pack, p.get("notes")))
    return out


def build(force: bool = False):
    """Regenerate pack_values.json if an input changed. Returns summary lines
    for the CI commit message, or None when nothing was regenerated."""
    inputs = fingerprint(PACK_INPUTS + [Path(__file__).resolve()])
    if up_to_date(PACK_OUTPUT, inputs) and not force:
        print(f"{PACK_OUTPUT.relative_to(ROOT)} is up to date.")
        return None
    old = load_json(PACK_OUTPUT) if PACK_OUTPUT.exists() else None

    with PACK_RULES.open(encoding="utf-8") as f:
        rules = yaml.safe_load(f)
    with VALUE_RULES.open(encoding="utf-8") as f:
        value_rules = yaml.safe_load(f)
    values = load_json(VALUES_OUTPUT)["profiles"]["packs"]["base"]
    en_items = load_json(EN_ITEMS)["items"]
    cn_items = load_json(CN_ITEMS)["items"]
    item_names = {k: d["name"] for k, d in cn_items.items()}
    item_names.update({k: d["name"] for k, d in en_items.items()})
    valuer = Valuer(rules, values, value_rules, item_names)
    en_names, en_windows = load_en_shop()
    en_events = load_en_events()
    overrides = rules.get("overrides") or {}
    price_map = {int(k): v for k, v in (rules.get("price_map") or {}).items()}
    event_dates = {k: str(v) for k, v in (rules.get("event_dates") or {}).items()}
    event_names = rules.get("event_names") or {}
    type_names = rules["pulls"].get("item_type_names") or {}
    group_rank = {g: i for i, g in enumerate(rules.get("pack_groups") or [])}
    attention = []

    # Common and regular packs, for labelling event packs that match one.
    regular = hand_written(valuer, rules.get("regular_packs"))
    starter = hand_written(valuer, rules.get("starter_packs"))
    common = hand_written(valuer, rules.get("common_packs"))

    packs, events = {}, {}
    for raw in load_json(SHOP_PACKS):
        cn_start = parse(raw["startDate"])
        key = raw.get("goodId") or f"{raw['name']}@{raw['startDate']}"
        over = overrides.get(key) or {}
        event = raw.get("event") or {"id": None, "name": None}
        event_id = event["id"] or "_none"

        window = pick_window(cn_start, en_windows_for(raw["goodId"], en_windows)) if raw.get("goodId") else None
        window_source = "pack" if window else None
        ev = en_events.get(event["id"])
        if not window and ev and iso_utc(ev["start"]) and iso_utc(ev["end"]) \
                and parse(iso_utc(ev["start"])) >= cn_start - WINDOW_SLACK:
            # EN ran the event but lists no sale for this pack: assume the event's dates.
            window, window_source = (ev["start"], ev["end"], None), "event"

        name, name_source = over.get("name"), "override"
        if not name and raw.get("goodId") and en_names.get(raw["goodId"]):
            name, name_source = en_names[raw["goodId"]], "en"
        if not name and raw.get("enName"):
            name, name_source = raw["enName"], "scrape"
        if not name and raw.get("mtlName"):
            # Machine translation (the scraper's, made once per pack); the page tags it "(MTL)".
            name, name_source = raw["mtlName"], "mtl"
        if not name:
            name, name_source = raw["name"], "cn"

        usd, usd_source = over.get("usd"), "override"
        if usd is None and window and window[2] is not None:
            usd, usd_source = window[2] / 100, "en"
        if usd is None and raw.get("priceCNY") in price_map:
            mapped = price_map[raw["priceCNY"]]
            usd, usd_source = mapped["usd"], "map_estimated" if mapped.get("estimated") else "map"
        if usd is None:
            usd_source = None

        if "contents" in over:
            contents = [valuer.entry(k, n) for k, n in over["contents"].items()]
        else:
            contents = [valuer.entry(i["id"], i["count"], name=i.get("enName")) for i in raw["items"]]
            contents += [valuer.entry(o.get("id"), o.get("count", 1), item_type=o.get("itemType"),
                                      category=o.get("category"),
                                      name=o.get("enName") or type_names.get(o.get("itemType")) or o.get("name"))
                         for o in raw["otherItems"]]

        pack = {
            "key": key, "name": name, "name_source": name_source, "cn_name": raw["name"],
            "good_id": raw.get("goodId"), "good_id_matched_by": raw.get("goodIdMatchedBy"),
            "event": event_id, "cn_start": raw["startDate"], "cn_end": raw["endDate"],
            "en_start": iso_utc(window[0]) if window else None,
            "en_end": iso_utc(window[1]) if window else None,
            "window_source": window_source,
            "price_cny": raw.get("priceCNY"), "usd": usd, "usd_source": usd_source,
            "contents": contents,
        }
        # Cosmetic packs (avatars, UI themes, namecards, furniture plus some
        # Orundum/OP) have no meaningful valuation, so they're hidden -- unless
        # an override says hidden: false.
        cosmetic = any(c["kind"] == "cosmetic" for c in contents) and \
            not any(c["kind"] in ("material", "zero") for c in contents)
        pack["hidden"] = bool(over.get("hidden", cosmetic))
        pack["group"] = over.get("group") or pack_group(contents, value_rules)
        pack["hidden_reason"] = ("override" if "hidden" in over else "cosmetic") if pack["hidden"] else None
        valuer.finish(pack, over.get("notes"))
        packs[key] = pack

        en_event_name = (ev or {}).get("name")
        e = events.setdefault(event_id, {
            "id": event_id, "cn_name": event["name"],
            "name": en_event_name or event_names.get(event["id"]) or event["name"],
            "name_source": "en" if en_event_name else "yaml" if event["id"] in event_names else "cn",
            "cn_start": raw["startDate"], "en_start": iso_utc(ev["start"]) if ev else None,
            "en_end": iso_utc(ev["end"]) if ev else None,
            "expected_en_start": event_dates.get(event["id"]), "packs": [],
        })
        e["cn_start"] = min(e["cn_start"], raw["startDate"])
        e["packs"].append(key)

    # Order events by when EN gets them: real EN start, else the expected date,
    # else CN start + the usual lag (so upcoming events stay in CN order).
    lags = sorted(((parse(e["cn_start"]), parse(e["en_start"]) - parse(e["cn_start"]))
                   for e in events.values() if e["en_start"]), key=lambda x: x[0])[-5:]
    lag = statistics.median(l for _, l in lags) if lags else timedelta(days=170)
    for e in events.values():
        e["order_date"] = (e["en_start"] or (e["expected_en_start"] and e["expected_en_start"] + "T00:00:00Z")
                           or (parse(e["cn_start"]) + lag).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    ordered = sorted(events.values(), key=lambda e: (e["order_date"], e["cn_start"]))
    for e in ordered:
        # By kind of pack (packs.yaml pack_groups), then price, high to low.
        e["packs"].sort(key=lambda k: (group_rank.get(packs[k]["group"], len(group_rank)),
                                       -(packs[k]["usd"] or 0), packs[k]["cn_start"], packs[k]["name"]))

    # What needs a look. Packs whose EN sale has ended are left out.
    now = datetime.now(timezone.utc)
    estimated = []
    for p in packs.values():
        if p["hidden"] or (p["en_end"] and parse(p["en_end"]) < now):
            continue
        label = f"{p['name']} [{p['key']}]"
        if p["good_id_matched_by"] == "price":
            attention.append(f"{label}: goodId matched by price only -- check it's the right pack")
        if not p["good_id"]:
            attention.append(f"{label}: no goodId, so no EN name/window/price from game data")
        if p["usd"] is None:
            attention.append(f"{label}: no USD price (¥{p['price_cny']} not in the price map)")
        elif p["usd_source"] == "map_estimated":
            # A confirmed map entry is fine even for a live pack: EN data only
            # carries prices for packs promoted with the standard banner
            # (normalGiftParam), and the map has matched every EN price seen.
            if p["window_source"]:
                attention.append(f"{label}: on EN, priced from an estimated map entry (¥{p['price_cny']} -> "
                                 f"${p['usd']}) -- check the real price and confirm the map")
            else:
                estimated.append(p)
        if p["window_source"] == "event":
            attention.append(f"{label}: EN ran the event but lists no sale for this pack -- using the event's dates")
        if p["window_source"] and p["name_source"] in ("scrape", "mtl", "cn"):
            attention.append(f"{label}: on EN, but no EN name from game data")
    if estimated:
        # Normal for upcoming packs (mostly cosmetic ones at ¥12/¥78), so one line, not one each.
        tiers = sorted({p["price_cny"] for p in estimated})
        attention.append(f"{len(estimated)} upcoming pack(s) priced from estimated map entries "
                         f"({', '.join(f'¥{t}' for t in tiers)}) -- confirm when EN sells one")
    for item in sorted(valuer.missing):
        attention.append(f"Item {item} ({item_names.get(item, '?')}): no value in the packs profile, counted as 0")

    op_packs = []
    for p in rules.get("op_packs") or []:
        ratio = rules["pulls"]["orundum_per_op"] / rules["pulls"]["orundum_per_pull"]
        op_packs.append({**p, "per_op": rnd(p["usd"] / p["op"]), "per_pull": rnd(p["usd"] / (p["op"] * ratio)),
                         "per_op_double": rnd(p["usd"] / p["double"]),
                         "per_pull_double": rnd(p["usd"] / (p["double"] * ratio))})

    data = {
        "_generated": generated(inputs, "edit data/efficiencies/packs.yaml and rerun tools/build_item_values.py."),
        "lag_days": lag.days,
        "events": ordered,
        "packs": packs,
        "regular": regular,
        "starter": starter,
        "common": common,
        "op_packs": op_packs,
        # A list, not a map: Hugo sorts map keys, and the page numbers notes in file order.
        "notes": [{"key": k, "text": v} for k, v in (rules.get("notes") or {}).items()],
        "attention": attention,
    }
    write_json(PACK_OUTPUT, data)
    print(f"Wrote {PACK_OUTPUT.relative_to(ROOT)}: {len(packs)} packs in {len(ordered)} events")
    for line in attention:
        print(f"  attention: {line}")
    return summarize(old, data)


def summarize(old: dict | None, new: dict) -> list:
    lines = []
    old_packs = (old or {}).get("packs", {})
    added = [p["name"] for k, p in new["packs"].items() if k not in old_packs]
    if added:
        lines.append(f"New packs: {len(added)} ({', '.join(added[:6])}{', ...' if len(added) > 6 else ''})")
    to_en = [p["name"] for k, p in new["packs"].items()
             if k in old_packs and p["en_start"] and not old_packs[k].get("en_start")]
    if to_en:
        lines.append("Now on EN: " + ", ".join(to_en))
    repriced = [f"{p['name']} ${old_packs[k]['usd']} -> ${p['usd']}" for k, p in new["packs"].items()
                if k in old_packs and old_packs[k].get("usd") != p["usd"]]
    if repriced:
        lines.append("Price changes: " + "; ".join(repriced))
    if new["attention"]:
        lines.append("Shop packs needing attention:")
        lines += [f"  {line}" for line in new["attention"]]
    return lines
