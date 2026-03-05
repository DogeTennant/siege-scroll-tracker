# Siege Scroll Tracker

A tool for **Raid: Shadow Legends** clan leaders to track siege scroll usage per clan member. See who's using their scrolls, who isn't, with full win/loss breakdowns per building.

## Features

- **Automatic server detection** — click Detect, launch Raid, server found automatically
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

### 3. First Run

1. Double-click **SiegeTracker.exe** — a UAC prompt will ask for admin rights (required)
2. Click **Fix Issues** to install the mitmproxy certificate (one-time only)
3. All status indicators at the top should show green ✓

### 4. Detect Your Server (one-time)

1. Close Raid if it's running
2. Click **Detect** next to the server field
3. Launch Raid — the tool will automatically find your server domain
4. Once detected, it's saved for future use

### 5. Capture Siege Data

1. Click **Start Capture**
2. Launch Raid (or it may already be running), go to Siege
3. Click through **each building** you want to track
4. Click **Stop & Report** — hosts file is cleaned up, report appears
5. Raid works normally again immediately

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
- **Administrator privileges** — needed for hosts file and port 443

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Raid won't connect after closing tracker | Open `C:\Windows\System32\drivers\etc\hosts` as admin, delete any line with `# SiegeTracker` |
| No clan roster detected | Make sure capture is running *before* you log into Raid |
| Missing buildings in report | You must click each building in the siege screen — only clicked buildings are captured |
| Certificate errors | Run as admin and click Fix Issues in the app |
| Server detection doesn't find anything | Make sure Raid is fully closed before clicking Detect, then launch it fresh |
| Wrong server detected | Close Raid, flush DNS (`ipconfig /flushdns`), try Detect again |

## Safety & Privacy

- The tool only **reads** game data passively — it never sends, modifies, or injects anything
- The hosts file change is **temporary** and automatically cleaned up when you stop capture
- The mitmproxy CA certificate only enables local traffic inspection on your machine
- All data stays local — nothing is uploaded anywhere

## Building from Source

```bash
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

## License

MIT License — see [LICENSE](LICENSE) for details.
