#!/usr/bin/env python3
"""
Raid: Shadow Legends - Siege Scroll Usage Tracker
===================================================
Parses Siege.GetBuilding data to count scroll uses per clan member.
Tracks both ATK victories and losses (failed attacks).

Supports three input formats:
  - .bin files (raw msgpack from siege_addon.py)
  - .json files (pre-decoded)
  - .txt  files (manually copied from mitmproxy response view)

Usage:
    python siege_tracker.py [building_files_directory]

    Defaults to current directory.

Requirements (system Python):
    pip install msgpack
"""

import re
import os
import sys
import glob
from collections import defaultdict
from datetime import datetime

try:
    import msgpack
except ImportError:
    msgpack = None

try:
    import json
except ImportError:
    json = None


# ── Clan Member Mapping ──────────────────────────────────────────────────────
CLAN_MEMBERS = {
    "8146647": "Gumbo",
    "9823966": "Sasquatchkid",
    "9866127": "_FEAR_",
    "20996119": "catmuncha",
    "29443114": "t0my11",
    "41086383": "Jambo79",
    "45460424": "Kilkler123",
    "55269853": "DynamicT",
    "60477130": "ONURFTMAGGOT",
    "61675357": "ElfOfIllusion",
    "61972801": "Wharf Rat",
    "62120951": "METALLIST",
    "68062144": "Mag Knee Toe",
    "80695919": "Deathmark13",
    "81330774": "Starfail",
    "94096810": "Wandering-Bat",
    "96350620": "Shockii",
    "97749863": "Dczmontreal",
    "99756935": "Irish74",
    "100425525": "garloud",
    "101868197": "DevilsChoir",
    "103611799": "RatedArp",
    "105215376": "ShnapiIi",
    "108868574": "SirTennant",
    "112339652": "Matter220",
    "112339662": "GoopyMess",
    "113030803": "Orjeni",
    "113355633": "Tabbz87",
    "115967153": "black rab",
    "135837792": "Raven Nevar",
}


def building_name_from_id(bid):
    if bid == 1:
        return "Stronghold"
    elif 100 <= bid < 200:
        return f"DefenseTower{bid - 99}"
    elif 1000 <= bid < 2000:
        return f"MagicTower{bid - 1000}"
    elif 2000 <= bid < 3000:
        return f"ManaShrine{bid - 2000}"
    elif 3000 <= bid < 4000:
        return f"Post{bid - 3000}"
    return f"Building{bid}"


# ── Structured Data Parser (for decoded msgpack dicts / JSON) ───────────────

def find_attacks_in_data(data, bname):
    """Recursively find attack entries in a decoded building data structure."""
    entries = []
    _find_attacks_recursive(data, entries, bname)
    return entries


def _find_attacks_recursive(obj, entries, bname):
    if isinstance(obj, dict):
        # An attack entry within a defender's l: array has:
        #   'a': dict with 'i' (attacker user ID)
        #   'w': bool (True = win, False = loss)
        if (
            "a" in obj
            and isinstance(obj["a"], dict)
            and "i" in obj["a"]
            and "w" in obj
            and isinstance(obj["w"], bool)
        ):
            uid = str(obj["a"]["i"])
            if uid in CLAN_MEMBERS:
                entries.append({
                    "uid": uid,
                    "name": CLAN_MEMBERS[uid],
                    "building": bname,
                    "won": obj["w"],
                })
            return

        for v in obj.values():
            _find_attacks_recursive(v, entries, bname)

    elif isinstance(obj, list):
        for item in obj:
            _find_attacks_recursive(item, entries, bname)


# ── Binary (raw msgpack) Parser ─────────────────────────────────────────────

def parse_building_bin(filepath):
    """Parse a raw msgpack .bin file from siege_addon.py."""
    if not msgpack:
        print("ERROR: msgpack not installed. Run: pip install msgpack")
        sys.exit(1)

    with open(filepath, "rb") as f:
        data = msgpack.unpackb(f.read(), raw=False, strict_map_key=False)

    # Get building name from the data
    bid = 0
    if isinstance(data, dict) and "b" in data:
        b = data["b"]
        if isinstance(b, dict):
            bid = b.get("i", 0)

    bname = building_name_from_id(bid)
    return find_attacks_in_data(data, bname), bname, bid


# ── JSON Parser ─────────────────────────────────────────────────────────────

def parse_building_json(filepath):
    """Parse a JSON building file."""
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    bid = data.get("b", {}).get("i", 0)
    bname = building_name_from_id(bid)
    return find_attacks_in_data(data, bname), bname, bid


# ── Text Parser (manually captured mitmproxy response files) ────────────────

def parse_building_txt(filepath):
    """Parse a TXT building file using indent-aware parsing."""
    bname = os.path.basename(filepath)
    bname = bname.replace("Siege_GetBuilding", "").replace(".txt", "")

    with open(filepath, encoding="utf-8", errors="replace") as f:
        lines = [line.rstrip("\r\n") for line in f]

    entries = []

    for i, line in enumerate(lines):
        m = re.match(r"^(\s+)- a:\s*$", line)
        if not m:
            continue

        a_indent = len(m.group(1))
        w_indent = a_indent + 2

        attacker_id = None
        for j in range(i + 1, min(i + 4, len(lines))):
            mi = re.match(r"\s+i: (\d{5,})", lines[j])
            if mi and lines[j].strip().startswith("i:"):
                attacker_id = mi.group(1)
                break

        if not attacker_id or attacker_id not in CLAN_MEMBERS:
            continue

        won = None
        for j in range(i + 1, min(i + 600, len(lines))):
            line_j = lines[j]
            line_indent = len(line_j) - len(line_j.lstrip())

            mw = re.match(r"\s+w: (true|false)\s*$", line_j)
            if mw and line_indent == w_indent:
                won = mw.group(1) == "true"
                break

            if re.match(r"\s+- a:\s*$", line_j) and line_indent == a_indent:
                break
            mq = re.match(r"\s+q: (\d{5,})", line_j)
            if mq and line_indent == w_indent:
                break

        entries.append({
            "uid": attacker_id,
            "name": CLAN_MEMBERS[attacker_id],
            "building": bname,
            "won": won,
        })

    return entries


# ── Report Generator ────────────────────────────────────────────────────────

def generate_report(search_dir="."):
    # Find all file types
    bin_files = sorted(glob.glob(os.path.join(search_dir, "*.bin")))
    # Exclude _req.bin files (request bodies saved alongside responses)
    bin_files = [f for f in bin_files if not f.endswith("_req.bin")]
    json_files = sorted(glob.glob(os.path.join(search_dir, "Siege_GetBuilding*.json")))
    txt_files = sorted(glob.glob(os.path.join(search_dir, "Siege_GetBuilding*.txt")))

    if not bin_files and not json_files and not txt_files:
        print(f"No building data files found in: {os.path.abspath(search_dir)}")
        print("Place .bin (from addon), .json, or .txt files there and re-run.")
        return

    all_entries = []
    buildings_parsed = []
    seen_building_ids = set()

    # Parse .bin files first (newest data from addon)
    for fpath in bin_files:
        try:
            entries, bname, bid = parse_building_bin(fpath)
            if bid in seen_building_ids:
                continue  # Skip duplicate buildings
            seen_building_ids.add(bid)
            all_entries.extend(entries)
            buildings_parsed.append(bname)
        except Exception as e:
            fname = os.path.basename(fpath)
            print(f"  Warning: Could not parse {fname}: {e}")

    # Then JSON files (skip if building already loaded)
    for fpath in json_files:
        try:
            entries, bname, bid = parse_building_json(fpath)
            if bid in seen_building_ids:
                continue
            seen_building_ids.add(bid)
            all_entries.extend(entries)
            buildings_parsed.append(bname)
        except Exception as e:
            fname = os.path.basename(fpath)
            print(f"  Warning: Could not parse {fname}: {e}")

    # Then TXT files (skip if building already loaded)
    seen_txt_names = set()
    for fpath in txt_files:
        bname = os.path.basename(fpath).replace("Siege_GetBuilding", "").replace(".txt", "")
        if bname in [b for b in buildings_parsed]:
            continue
        entries = parse_building_txt(fpath)
        all_entries.extend(entries)
        buildings_parsed.append(bname)

    if not buildings_parsed:
        print("No valid building data found in any files.")
        return

    # Aggregate per member
    stats = {}
    for uid, name in CLAN_MEMBERS.items():
        stats[uid] = {
            "name": name,
            "scrolls": 0,
            "wins": 0,
            "losses": 0,
            "buildings": set(),
        }

    for entry in all_entries:
        uid = entry["uid"]
        stats[uid]["scrolls"] += 1
        if entry["won"]:
            stats[uid]["wins"] += 1
        else:
            stats[uid]["losses"] += 1
        stats[uid]["buildings"].add(entry["building"])

    # ── Print Report ─────────────────────────────────────────────────────
    total_scrolls = sum(s["scrolls"] for s in stats.values())
    total_wins = sum(s["wins"] for s in stats.values())
    total_losses = total_scrolls - total_wins
    active_members = sum(1 for s in stats.values() if s["scrolls"] > 0)

    print("=" * 70)
    print("  SIEGE SCROLL USAGE REPORT")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Buildings parsed: {len(buildings_parsed)}")
    print(f"  Total scrolls used: {total_scrolls}  ({total_wins}W / {total_losses}L)")
    print(f"  Active attackers: {active_members} / {len(CLAN_MEMBERS)}")
    print("=" * 70)
    print()

    ranked = sorted(
        stats.values(),
        key=lambda s: (-s["scrolls"], -s["wins"], s["name"].lower()),
    )

    print(f"  {'#':<4} {'Name':<18} {'Scrolls':>7} {'W':>3} {'L':>3}   Buildings Hit")
    print(f"  {'-'*4} {'-'*18} {'-'*7} {'-'*3} {'-'*3}   {'-'*30}")

    for rank, s in enumerate(ranked, 1):
        bldgs = ", ".join(sorted(s["buildings"])) if s["buildings"] else "-"
        marker = "" if s["scrolls"] > 0 else "  ⚠"
        print(
            f"  {rank:<4} {s['name']:<18} {s['scrolls']:>7} "
            f"{s['wins']:>3} {s['losses']:>3}{marker}   {bldgs}"
        )

    print()
    print("  ⚠ = No attacks recorded")
    print()

    inactive = [s["name"] for s in ranked if s["scrolls"] == 0]
    if inactive:
        print("  INACTIVE MEMBERS (0 scrolls used):")
        print(f"  {', '.join(inactive)}")
        print()

    print("  BUILDING BREAKDOWN:")
    building_counts = defaultdict(lambda: [0, 0])
    for entry in all_entries:
        building_counts[entry["building"]][0] += 1
        if entry["won"]:
            building_counts[entry["building"]][1] += 1
    for bldg, (scrolls, wins) in sorted(
        building_counts.items(), key=lambda x: -x[1][0]
    ):
        losses = scrolls - wins
        loss_str = f" ({losses}L)" if losses else ""
        print(f"    {bldg:<22} {scrolls} scrolls, {wins}W{loss_str}")
    print()


if __name__ == "__main__":
    search_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_report(search_dir)
