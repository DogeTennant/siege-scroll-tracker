# Siege Scroll Tracker

A tool for **Raid: Shadow Legends** clan leaders to track siege scroll usage per clan member. See who's using their scrolls, who isn't, with full win/loss breakdowns per building.

## Features

- **Automatic clan detection** — roster is captured on login, no manual setup
- **Per-member scroll tracking** — total scrolls, wins, losses, buildings attacked
- **One-click capture** — just click Start, play the game, click Stop
- **No Proxifier needed** — uses local reverse proxy via hosts file redirect
- **Clipboard export** — copy the report for Discord/chat in one click
- **Works for any clan** — no hardcoded data, fully self-configuring

## Quick Start

### 1. Install mitmproxy (one-time)

Download and install from [mitmproxy.org](https://mitmproxy.org/) (free, open-source).

### 2. Download SiegeTracker

Go to [Releases](../../releases) and download the latest `SiegeTracker.zip`. Extract it anywhere.

### 3. Run

1. Double-click **SiegeTracker.exe** — UAC will ask for admin (required for traffic capture)
2. First run: click **Fix Issues** to install the mitmproxy certificate
3. Click **Start Capture**
4. Launch Raid, go to Siege, click through each building
5. Click **Stop & Report** — done!

## How It Works

When you click Start Capture, the tool:

1. Redirects Raid's server domain to your local machine (via Windows hosts file)
2. Runs a local reverse proxy (mitmproxy) that forwards traffic to the real server
3. Intercepts `Alliance.Get` (clan roster) and `Siege.GetBuilding` (battle data)
4. Parses attacker entries from building data to count scroll usage per member

When you click Stop & Report:

1. Stops the proxy and removes the hosts redirect
2. Raid works normally again immediately
3. Generates a color-coded report with full breakdown

**The tool only reads game data — it never modifies or sends anything.**

## Report Example

```
SIEGE SCROLL USAGE REPORT
Generated: 2026-03-05 01:49
Buildings: 23    Scrolls: 118 (84W / 34L)    Active: 26/30

  #    Name               Scrolls    W    L   Buildings Hit
  ──── ────────────────── ─────── ──── ────   ──────────────────────────────
  1    ONURFTMAGGOT             9    8    1   DefenseTower5, MagicTower3, ManaShrine2
  2    Orjeni                   8    3    5   Stronghold
  3    Deathmark13              7    5    2   MagicTower4, ManaShrine2
  ...
  27   Dczmontreal              0    0    0 ⚠   -
  28   Gumbo                    0    0    0 ⚠   -

INACTIVE: Dczmontreal, Gumbo, t0my11, Tabbz87
```

## Requirements

- **Windows 10/11**
- **mitmproxy** — [download here](https://mitmproxy.org/) (free)
- **Administrator privileges** — needed to modify hosts file and listen on port 443

## Building from Source

If you prefer to run from source or build the exe yourself:

```bash
# Clone the repo
git clone https://github.com/DogeTennant/siege-scroll-tracker.git
cd siege-scroll-tracker

# Install dependencies
pip install msgpack

# Run directly
python siege_gui.py

# Or build the exe
pip install pyinstaller
python build.py
# Output: dist/SiegeTracker/
```

## Server Domain

The default server is `rdint1s09.plrm.zone`. If you're on a different game segment, you can change this in the app's server field. To find your server domain, check the `Host` header in any Raid API request.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Raid won't connect after closing tracker | Open `C:\Windows\System32\drivers\etc\hosts` as admin, delete any line with `# SiegeTracker` |
| No clan roster detected | Make sure capture is running *before* you log into Raid |
| Missing buildings in report | You must click each building in the siege screen — only clicked buildings are captured |
| Certificate errors | Run as admin and click Fix Issues in the app |

## Safety & Privacy

- The tool only **reads** game data passively — it never sends, modifies, or injects anything
- The hosts file change is **temporary** and automatically cleaned up when you stop capture
- The mitmproxy CA certificate only enables local traffic inspection on your machine
- All data stays local — nothing is uploaded anywhere

## License

MIT License — see [LICENSE](LICENSE) for details.
