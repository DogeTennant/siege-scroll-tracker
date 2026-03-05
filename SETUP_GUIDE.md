# Siege Scroll Tracker — Setup Guide

A tool for Raid: Shadow Legends to track siege scroll usage per clan member. Shows who's using their scrolls, who isn't, and includes win/loss breakdowns per building.

## What This Tool Does

- Intercepts Raid's game data to read siege building battle logs
- Automatically detects your clan roster (no manual setup)
- Counts scroll usage per member with win/loss breakdown
- Shows which buildings each member attacked
- One-click report generation, copy to clipboard for Discord/chat

## Requirements

1. **Windows 10/11** (uses Windows hosts file for traffic interception)
2. **mitmproxy** (free, open-source traffic inspection tool)

## One-Time Setup (5 minutes)

### Step 1: Install mitmproxy

1. Go to https://mitmproxy.org/ and download the Windows installer
2. Run the installer with default settings
3. After installation, open a Command Prompt and type `mitmdump --version` to verify it works

### Step 2: Run SiegeTracker for the first time

1. Double-click **SiegeTracker.exe**
2. A Windows UAC prompt will ask for administrator permission — click **Yes**
   (Admin rights are needed to redirect game traffic through the tool)
3. The app will show setup status indicators at the top:
   - ✓ Admin — running with admin rights
   - ✓ mitmproxy — mitmdump found
   - ✗ Certificate — needs to be installed (first time only)
   - ✓ Addon — siege_addon.py found

### Step 3: Install the Certificate (first time only)

1. Click the **Fix Issues** button in the app
2. It will ask to install mitmproxy's CA certificate — click **Yes**
3. This allows the tool to read Raid's encrypted traffic
4. The certificate is only used locally on your machine

After this, all indicators should show green ✓ checks.

## How to Use (Every Siege)

### Capturing Data

1. **Launch SiegeTracker.exe** (UAC prompt will appear — click Yes)
2. Click **Start Capture**
3. **Launch Raid: Shadow Legends** normally
4. You'll see "Clan roster captured!" appear as the game loads
5. Go to **Siege** and **click on every building** you want to track
6. Watch the counter — it shows how many buildings have been captured
7. Click **Stop & Report** when done

### Reading the Report

The report shows:
- Each clan member ranked by scroll usage
- **Scrolls**: total scrolls used (attacks + rematches)
- **W/L**: wins and losses
- **Buildings Hit**: which buildings they attacked
- Members with 0 scrolls are highlighted in red
- Building breakdown at the bottom

### Copying for Discord

Click **Copy to Clipboard** to get a plain-text version you can paste into Discord, WhatsApp, or any chat.

## Important Notes

### Server Domain

The default server is `rdint1s09.plrm.zone`. If you're on a different game segment (different region or server), you may need to change this. You can find your server by:

1. Running mitmproxy manually: `mitmweb`
2. Setting up Proxifier or similar to route Raid through it
3. Looking at the `Host:` header in any Raid request

The server field at the top of the app is editable.

### How It Works

- When you click **Start Capture**, the tool:
  1. Adds a temporary entry to your Windows hosts file redirecting the game server to your local machine
  2. Starts a local reverse proxy (mitmproxy) that forwards traffic to the real server
  3. Intercepts and saves building data as you click through them
- When you click **Stop & Report**, it:
  1. Stops the proxy
  2. Removes the hosts entry (game works normally again)
  3. Parses the saved data and generates the report

### Safety

- The tool only reads game data — it never modifies or sends anything
- The hosts file change is temporary and automatically cleaned up
- Your game login and all other traffic passes through unchanged
- The mitmproxy certificate only allows local traffic inspection

### Troubleshooting

**"Raid won't connect after stopping capture"**
- The hosts file entry wasn't cleaned up. Open `C:\Windows\System32\drivers\etc\hosts` in Notepad (as admin) and delete any line containing `# SiegeTracker`

**"No clan roster detected"**
- Make sure capture is running BEFORE you log into Raid
- The clan roster is captured during login (Alliance.Get)
- Try restarting Raid with capture active

**"Missing buildings in report"**
- You need to click on each building in the siege screen
- Buildings you don't click won't be captured
- The counter at the top shows how many have been saved

**"Certificate issues"**
- Run the app as Administrator and click Fix Issues
- If that doesn't work, manually install the cert:
  `certutil -addstore Root "%USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.cer"`

## Building from Source

If you have Python installed and want to run from source:

```
pip install msgpack
python siege_gui.py
```

To build the standalone exe:

```
pip install pyinstaller msgpack
python build.py
```

The built exe will be in `dist/SiegeTracker/`.

## Files

- **SiegeTracker.exe** — Main application (auto-requests admin, auto-extracts addon)
- **siege_data/** — Captured data (created automatically)
- **siege_addon.py** — mitmproxy addon (auto-created by the app, don't delete)
- **config.json** — Saved settings (created automatically)
