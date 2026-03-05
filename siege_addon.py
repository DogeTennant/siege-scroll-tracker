"""
Raid: Shadow Legends — Siege Auto-Save Addon for mitmproxy
============================================================

Intercepts Alliance.Get (clan roster) and Siege.GetBuilding (battle
data) and saves them automatically. No extra packages needed.

Used by SiegeTracker GUI — do not rename or move this file.
"""

import os
import time
import hashlib
from mitmproxy import http, ctx

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(SCRIPT_DIR, "siege_data")
CAPTURE_METHODS = {"Siege.GetBuilding", "Alliance.Get"}


class SiegeAddon:
    def __init__(self):
        self.building_count = 0
        self.alliance_captured = False
        self.seen_hashes = set()
        os.makedirs(SAVE_DIR, exist_ok=True)

        # Clean old building captures
        old_files = [
            f for f in os.listdir(SAVE_DIR)
            if f.startswith("building_") and f.endswith(".bin")
        ]
        if old_files:
            for f in old_files:
                os.remove(os.path.join(SAVE_DIR, f))
            ctx.log.info(f"[Siege] Cleared {len(old_files)} old building files.")

        if os.path.exists(os.path.join(SAVE_DIR, "alliance_data.bin")):
            ctx.log.info("[Siege] Existing clan roster found.")

        ctx.log.info(f"[Siege] Addon loaded. Saving to: {SAVE_DIR}")
        ctx.log.info("[Siege] Log in to capture roster, then click buildings.")

    def response(self, flow: http.HTTPFlow):
        method = flow.request.headers.get("server-method", "")
        if method not in CAPTURE_METHODS:
            return
        if not flow.response or not flow.response.content:
            return

        if method == "Alliance.Get":
            self._save_alliance(flow)
        elif method == "Siege.GetBuilding":
            self._save_building(flow)

    def _save_alliance(self, flow):
        fpath = os.path.join(SAVE_DIR, "alliance_data.bin")
        with open(fpath, "wb") as f:
            f.write(flow.response.content)
        size_kb = len(flow.response.content) / 1024
        self.alliance_captured = True
        ctx.log.info(f"[Siege] Clan roster captured! ({size_kb:.1f} KB)")

    def _save_building(self, flow):
        content_hash = hashlib.md5(flow.response.content).hexdigest()
        if content_hash in self.seen_hashes:
            ctx.log.info("[Siege] Skipped duplicate building response")
            return
        self.seen_hashes.add(content_hash)

        self.building_count += 1
        timestamp = time.strftime("%H%M%S")
        fname = f"building_{timestamp}_{self.building_count:03d}.bin"
        fpath = os.path.join(SAVE_DIR, fname)

        with open(fpath, "wb") as f:
            f.write(flow.response.content)

        size_kb = len(flow.response.content) / 1024
        ctx.log.info(
            f"[Siege] Saved building #{self.building_count} "
            f"({size_kb:.1f} KB) -> {fname}"
        )

        if not self.alliance_captured:
            if not os.path.exists(os.path.join(SAVE_DIR, "alliance_data.bin")):
                ctx.log.warn("[Siege] No clan roster yet! Relog to capture it.")


addons = [SiegeAddon()]
